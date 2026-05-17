import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import modal

APP_NAME = "kan-sr-smoke-test"
DEFAULT_VOLUME_NAME = os.environ.get("KAN_SR_VOLUME", "kan-sr")

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(DEFAULT_VOLUME_NAME, create_if_missing=True)

image = modal.Image.debian_slim(python_version="3.11")


def _utc_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


@app.function(image=image)
def ping() -> dict:
    return {
        "ok": True,
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "time": time.time(),
    }


@app.function(image=image, volumes={"/vol": volume})
def volume_roundtrip(run_id: str, payload: dict) -> dict:
    base = f"/vol/runs/{run_id}"
    os.makedirs(base, exist_ok=True)

    path = f"{base}/payload.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    volume.commit()

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.function(image=image, volumes={"/vol": volume}, retries=2)
def retry_once(run_id: str) -> dict:
    """
    Intentionally fails the first time to verify Modal retries work.
    Uses the shared Volume as a durable marker so retries can succeed.
    """
    base = f"/vol/runs/{run_id}"
    os.makedirs(base, exist_ok=True)

    marker = f"{base}/retry_marker"
    if not os.path.exists(marker):
        with open(marker, "w", encoding="utf-8") as f:
            f.write("first_attempt\n")
        volume.commit()
        raise RuntimeError("intentional failure (should be retried)")

    return {"retry_ok": True}


@app.function(image=image)
def square(i: int) -> int:
    return i * i


@app.function(image=image, gpu="L4")
def gpu_probe() -> dict:
    import glob
    import subprocess

    devices = sorted(glob.glob("/dev/nvidia*"))
    env = {
        "NVIDIA_VISIBLE_DEVICES": os.environ.get("NVIDIA_VISIBLE_DEVICES"),
        "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }

    smi = None
    try:
        smi = subprocess.check_output(["nvidia-smi", "-L"], text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:  # noqa: BLE001
        smi = f"nvidia-smi unavailable: {type(e).__name__}: {e}"

    return {"devices": devices, "env": env, "nvidia_smi": smi}


@app.local_entrypoint()
def main(with_gpu: bool = False, fanout: int = 32) -> None:
    """
    Run:
      modal run modal_jobs/smoke_test.py

    Optional:
      modal run modal_jobs/smoke_test.py --with-gpu
      modal run modal_jobs/smoke_test.py --fanout 64

    Notes:
      - Uses Volume name from env KAN_SR_VOLUME (default: kan-sr).
      - Writes artifacts to /runs/<run_id>/ under that Volume.
    """
    run_id = _utc_run_id()
    print(f"[smoke] volume={DEFAULT_VOLUME_NAME} run_id={run_id}")

    p = ping.remote()
    assert p.get("ok") is True
    print(f"[ping] ok python={p['python']} platform={p['platform']}")

    payload = {"run_id": run_id, "ts": time.time(), "fanout": fanout}
    back = volume_roundtrip.remote(run_id, payload)
    assert back == payload
    print("[volume] roundtrip ok")

    r = retry_once.remote(run_id)
    assert r.get("retry_ok") is True
    print("[retry] ok")

    values = list(square.map(range(fanout)))
    expected = [i * i for i in range(fanout)]
    assert values == expected
    print(f"[fanout] ok count={fanout}")

    if with_gpu:
        try:
            g = gpu_probe.remote()
            print(f"[gpu] devices={g.get('devices')}")
            print(f"[gpu] env={g.get('env')}")
            print(f"[gpu] nvidia_smi={g.get('nvidia_smi')}")
        except Exception as e:  # noqa: BLE001
            print(f"[gpu] failed: {type(e).__name__}: {e}")
            print("[gpu] (This can be normal if your Modal account has no GPU access.)")

    print("[smoke] PASS")

