const puppeteer = require('puppeteer-core');
const path = require('path');

(async () => {
    const config = JSON.parse(process.argv[2]);
    const scale = config.scale || 1;
    const browser = await puppeteer.launch({
        headless: 'new',
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu',
               '--font-render-hinting=none']
    });

    for (const item of config.files) {
        const page = await browser.newPage();
        await page.setViewport({
            width: 1280,
            height: 720,
            deviceScaleFactor: scale
        });

        await page.goto('file://' + item.html, {
            waitUntil: 'networkidle0',
            timeout: 30000
        });
        await page.evaluate(async () => {
            await document.fonts.ready;
            const images = Array.from(document.querySelectorAll('img'));
            await Promise.all(images.map(img => {
                if (img.complete) return Promise.resolve();
                return new Promise(r => { img.onload = r; img.onerror = r; });
            }));
        });

        await page.screenshot({
            path: item.png,
            type: 'png',
            fullPage: false,
            clip: { x: 0, y: 0, width: 1280, height: 720 }
        });
        console.log('PNG: ' + path.basename(item.html) + ' -> ' + path.basename(item.png));
        await page.close();
    }

    await browser.close();
    console.log('Done: ' + config.files.length + ' PNGs');
})();
