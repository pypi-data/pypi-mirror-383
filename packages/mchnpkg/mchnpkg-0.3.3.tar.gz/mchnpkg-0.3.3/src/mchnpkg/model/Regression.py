from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

import numpy as np
import torch
from torch import nn
import matplotlib.pyplot as plt


class LinearRegression(nn.Module):
    """
    y = w0 + w1 * x   (one feature)
    Uses SGD + MSELoss. Tracks w0, w1, and loss over epochs.
    """

    def __init__(self, learning_rate: float = 1e-2, epochs: int = 2000, seed: int = 0):
        super().__init__()
        torch.manual_seed(seed)

        # parameters
        self.w0 = nn.Parameter(torch.zeros(1))   # intercept
        self.w1 = nn.Parameter(torch.zeros(1))   # slope
        self.optimizer = torch.optim.SGD([self.w0, self.w1], lr=learning_rate)
        self.criterion = nn.MSELoss()

        # training config
        self.learning_rate = learning_rate
        self.epochs = int(epochs)

        # history
        self.w0_hist, self.w1_hist, self.loss_hist = [], [], []

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: shape (N, 1) float tensor
        return: y_pred shape (N, 1)
        """
        return self.w0 + self.w1 * x

    @torch.no_grad()
    def predict(self, x_new: Iterable[float] | np.ndarray | torch.Tensor) -> np.ndarray:
        """
        Returns predictions as numpy array with shape (N,)
        """
        if not torch.is_tensor(x_new):
            x_new = torch.as_tensor(x_new, dtype=torch.float32)
        x_new = x_new.reshape(-1, 1)
        y_hat = self.forward(x_new)
        return y_hat.reshape(-1).cpu().numpy()

    def _to_tensor(self, x, y) -> Tuple[torch.Tensor, torch.Tensor]:
        if not torch.is_tensor(x):
            x = torch.as_tensor(x, dtype=torch.float32)
        if not torch.is_tensor(y):
            y = torch.as_tensor(y, dtype=torch.float32)
        return x.reshape(-1, 1), y.reshape(-1, 1)

    def _r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        y_true = np.asarray(y_true).reshape(-1)
        y_pred = np.asarray(y_pred).reshape(-1)
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - y_true.mean()) ** 2)
        return float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")

    def fit(
        self,
        x_train,
        y_train,
        x_test: Optional[Iterable[float]] = None,
        y_test: Optional[Iterable[float]] = None,
        verbose: bool = False,
    ) -> Optional[float]:
        """
        Trains on (x_train, y_train). If test data are provided, prints and returns R^2 on test.
        """
        x_tr, y_tr = self._to_tensor(x_train, y_train)

        self.w0_hist.clear(); self.w1_hist.clear(); self.loss_hist.clear()

        for epoch in range(self.epochs):
            y_hat = self.forward(x_tr)
            loss = self.criterion(y_hat, y_tr)

            self.optimizer.zero_grad(set_to_none=True)
            loss.backward()
            self.optimizer.step()

            # record history
            self.loss_hist.append(float(loss.item()))
            self.w0_hist.append(float(self.w0.detach().item()))
            self.w1_hist.append(float(self.w1.detach().item()))

            if verbose and (epoch % max(1, self.epochs // 10) == 0 or epoch == self.epochs - 1):
                print(f"epoch {epoch:5d} | loss={loss.item():.6f} | w0={self.w0.item():.6f} w1={self.w1.item():.6f}")

        r2 = None
        if x_test is not None and y_test is not None:
            y_pred_test = self.predict(x_test)
            r2 = self._r2(np.asarray(y_test), y_pred_test)
            print(f"R^2 (test) = {r2:.6f}")
        return r2

    def analysis_plot(self, x, y, title: str = "Training Summary"):
        """
        Creates a figure with:
          (1) scatter of (x,y) + fitted line
          (2) parameter traces (w0, w1)
          (3) loss curve
        """
        x = np.asarray(x).reshape(-1)
        y = np.asarray(y).reshape(-1)

        # line for plotting
        x_line = np.linspace(x.min(), x.max(), 300, dtype=np.float32)
        y_line = self.predict(x_line)

        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

        # (1) data + regression line
        axes[0].scatter(x, y, s=12, alpha=0.7, label="train data")
        axes[0].plot(x_line, y_line, linewidth=2.5, label="fitted line")
        axes[0].set_xlabel("BCR (x)")
        axes[0].set_ylabel("AnnualProduction (y)")
        axes[0].legend()
        axes[0].grid(True, ls="--", alpha=0.3)

        # (2) parameter traces
        axes[1].plot(self.w0_hist, label="w0 (intercept)")
        axes[1].plot(self.w1_hist, label="w1 (slope)")
        axes[1].set_xlabel("epoch")
        axes[1].set_ylabel("value")
        axes[1].legend()
        axes[1].grid(True, ls="--", alpha=0.3)

        # (3) loss curve
        axes[2].plot(self.loss_hist)
        axes[2].set_xlabel("epoch")
        axes[2].set_ylabel("MSE loss")
        axes[2].grid(True, ls="--", alpha=0.3)

        fig.suptitle(title, y=1.02, fontsize=12)
        fig.tight_layout()
        plt.show()

