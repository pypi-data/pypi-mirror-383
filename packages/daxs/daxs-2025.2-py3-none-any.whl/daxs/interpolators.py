"""The module provides interpolators."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.interpolate import (
    CloughTocher2DInterpolator,
    LinearNDInterpolator,
    NearestNDInterpolator,
)

logger = logging.getLogger(__name__)


class Interpolator2D:
    """Two-dimensional interpolator."""

    def __init__(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        z: npt.NDArray[np.float64],
        kind: str = "linear",
        fill_value: float = np.nan,
    ):
        """Initialize the 2D interpolator.

        Args:
            x: X-axis values (1-D array)
            y: Y-axis values (1-D array)
            z: Data values (1-D array)
            kind: The kind of interpolation to use. Options are "nearest" or "linear".
            fill_value: Value used to fill in for requested points outside of the convex
              hull of the input points.
        """
        if not (x.ndim == y.ndim == z.ndim == 1):
            raise ValueError("x, y, z must be 1D arrays.")
        if not (len(x) == len(y) == len(z)):
            raise ValueError("x, y, z must have the same length.")
        self.x = x
        self.y = y
        self.z = z

        self.kind = kind
        self.fill_value = fill_value

        self._interpolator = None

    @property
    def interpolator(self):
        """The actual interpolator."""
        if self._interpolator is None:
            if self.kind == "nearest":
                interp = NearestNDInterpolator((self.x, self.y), self.z)
            elif self.kind == "linear":
                interp = LinearNDInterpolator((self.x, self.y), self.z, self.fill_value)
            elif self.kind == "cubic":
                interp = CloughTocher2DInterpolator(
                    (self.x, self.y), self.z, fill_value=self.fill_value
                )
            else:
                raise ValueError(f"Unknown interpolation method: {self.kind}")
            self._interpolator = interp
        return self._interpolator

    def update(self, parameters: dict[str, Any]):
        """Update the interpolator parameters."""
        for key, value in parameters.items():
            setattr(self, key, value)
        logger.info("The interpolator parameters have been updated.")
        self._interpolator = None

    def __call__(self, points: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Evaluate interpolator."""
        return self.interpolator.__call__(points)
