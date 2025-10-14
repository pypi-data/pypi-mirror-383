# losses
import unittest as ut
import numpy as np

from pureml.machinery import Tensor
from pureml.losses import MSE, BCE, CCE

def _rng(seed=0):
    return np.random.default_rng(seed)

def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def _softmax(x, axis=-1):
    x = np.asarray(x, dtype=np.float64)
    m = np.max(x, axis=axis, keepdims=True)
    e = np.exp(x - m)
    return e / np.sum(e, axis=axis, keepdims=True)


# ----------------------------- MSE -----------------------------
class TestMSE(ut.TestCase):
    def test_value_and_grad_no_broadcast(self):
        rng = _rng(1)
        Y = Tensor(rng.standard_normal((4, 3)), requires_grad=False)
        Yh = Tensor(rng.standard_normal((4, 3)), requires_grad=True)

        L = MSE(Y, Yh)
        # expected value
        E = Y.data - Yh.data
        expected = np.mean(E * E)
        self.assertAlmostEqual(float(L.data), float(expected), places=12)

        # expected gradient wrt Y_hat
        N = Yh.data.size
        L.backward()  # upstream = 1
        grad_expected = (2.0 / N) * (Yh.data - Y.data)
        np.testing.assert_allclose(Yh.grad, grad_expected, rtol=1e-6, atol=1e-8)

    def test_value_and_grad_with_broadcast(self):
        # Y: (B,1) ; Y_hat: (B,3) (Y broadcasts across last dim)
        Y = Tensor(np.array([[1.0], [2.0]], dtype=np.float64), requires_grad=False)
        Yh = Tensor(np.array([[1.5, 0.5, 1.0],
                              [2.5, 1.0, 2.0]], dtype=np.float64), requires_grad=True)

        L = MSE(Y, Yh)
        # manual broadcast
        Yb = np.array([[1.0, 1.0, 1.0],
                       [2.0, 2.0, 2.0]])
        expected = np.mean((Yb - Yh.data) ** 2)
        self.assertAlmostEqual(float(L.data), float(expected), places=12)

        L.backward()
        N = Yh.data.size
        grad_expected = (2.0 / N) * (Yh.data - Yb)
        np.testing.assert_allclose(Yh.grad, grad_expected, rtol=1e-6, atol=1e-8)


# ----------------------------- BCE -----------------------------
class TestBCE(ut.TestCase):
    def test_logits_equals_probs(self):
        rng = _rng(2)
        z = Tensor(rng.standard_normal(10), requires_grad=False)    # logits
        y = Tensor(rng.integers(0, 2, size=10).astype(np.float64), requires_grad=False)

        L_logits = BCE(y, z, from_logits=True)
        p = _sigmoid(z.data)
        L_probs  = BCE(y, Tensor(p), from_logits=False)

        self.assertAlmostEqual(float(L_logits.data), float(L_probs.data), places=10)

    def test_grad_wrt_logits(self):
        rng = _rng(3)
        z = Tensor(rng.standard_normal((6,)), requires_grad=True)
        y = Tensor(rng.integers(0, 2, size=6).astype(np.float64), requires_grad=False)

        L = BCE(y, z, from_logits=True)
        L.backward()  # upstream = 1

        p = _sigmoid(z.data)
        N = z.data.size
        grad_expected = (p - y.data) / N
        np.testing.assert_allclose(z.grad, grad_expected, rtol=1e-6, atol=1e-8)

    def test_finite_outputs(self):
        # moderate logits to avoid overflow; BCE should be finite
        z = Tensor(np.array([-8.0, -2.0, 0.0, 2.0, 8.0], dtype=np.float64))
        y = Tensor(np.array([0, 1, 0, 1, 1], dtype=np.float64))
        L = BCE(y, z, from_logits=True)
        self.assertTrue(np.isfinite(float(L.data)))


# ----------------------------- CCE -----------------------------
class TestCCE(ut.TestCase):
    def test_logits_equals_probs_axis_last(self):
        rng = _rng(4)
        B, C = 5, 7
        Z = Tensor(rng.standard_normal((B, C)), requires_grad=False)  # logits
        # one-hot labels
        y_idx = rng.integers(0, C, size=B)
        Y = np.eye(C, dtype=np.float64)[y_idx]
        Yt = Tensor(Y, requires_grad=False)

        L_logits = CCE(Yt, Z, from_logits=True)
        P = _softmax(Z.data, axis=-1)
        L_probs  = CCE(Yt, Tensor(P), from_logits=False)

        self.assertAlmostEqual(float(L_logits.data), float(L_probs.data), places=10)

    def test_grad_wrt_logits_matches_softmax_minus_onehot_over_batch(self):
        rng = _rng(5)
        B, C = 4, 6
        Z = Tensor(rng.standard_normal((B, C)), requires_grad=True)  # logits
        y_idx = rng.integers(0, C, size=B)
        Y = Tensor(np.eye(C, dtype=np.float64)[y_idx], requires_grad=False)

        L = CCE(Y, Z, from_logits=True)
        L.backward()

        S = _softmax(Z.data, axis=-1)
        grad_expected = (S - Y.data) / B
        np.testing.assert_allclose(Z.grad, grad_expected, rtol=1e-6, atol=1e-8)

    def test_label_smoothing_effects(self):
        Y = Tensor(np.array([[1.0, 0.0, 0.0]]), requires_grad=False)

        Z_right = Tensor(np.array([[ 4.0, -1.0, -2.0]]), requires_grad=False)
        Z_wrong = Tensor(np.array([[-1.0,  4.0, -2.0]]), requires_grad=False)

        L_right_hard   = CCE(Y, Z_right, from_logits=True, label_smoothing=0.0)
        L_right_smooth = CCE(Y, Z_right, from_logits=True, label_smoothing=0.1)
        self.assertGreater(float(L_right_smooth.data), float(L_right_hard.data))

        L_wrong_hard   = CCE(Y, Z_wrong, from_logits=True, label_smoothing=0.0)
        L_wrong_smooth = CCE(Y, Z_wrong, from_logits=True, label_smoothing=0.1)
        self.assertLess(float(L_wrong_smooth.data), float(L_wrong_hard.data))


if __name__ == "__main__":
    ut.main(verbosity=2)
