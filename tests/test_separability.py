import unittest

import sympy as sp


class TestSeparability(unittest.TestCase):
    def test_additive_separable(self) -> None:
        from src.kan_sr.separability import detect_separability

        x, y = sp.symbols("x y")
        rep = detect_separability(x**2 + sp.sin(y))
        self.assertTrue(rep.additive_separable)
        self.assertFalse(rep.multiplicative_separable)

    def test_multiplicative_separable(self) -> None:
        from src.kan_sr.separability import detect_separability

        x, y = sp.symbols("x y")
        rep = detect_separability((x + 1) * (y - 2))
        self.assertTrue(rep.multiplicative_separable)

