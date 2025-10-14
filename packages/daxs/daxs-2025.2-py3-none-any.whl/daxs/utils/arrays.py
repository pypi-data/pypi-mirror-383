"""Module containing array utilities."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import numpy.typing as npt

logger = logging.getLogger(__name__)


def intersect(
    a: npt.NDArray[np.float64], b: npt.NDArray[np.float64], sort: bool = False
) -> npt.NDArray[np.float64]:
    """Compute the intersection of two arrays.

    The function sorts the input arrays if required, determines the indices of
    the intersecting region, and returns the intersection. If there is no
    intersection, an empty array is returned.

    Args:
        a: The first input array.
        b: The second input array.
        sort: If True, the input arrays are sorted; default is False.

    Returns:
        The intersection of the input arrays. If there is no intersection, an
        empty array is returned.
    """
    # Sort the input arrays if required.
    if sort:
        a, b = np.sort(a, kind="stable"), np.sort(b, kind="stable")

    # Sort the input arrays by their minimum value.
    a, b = sorted([a, b], key=np.min)

    # Determine the indices of the intersecting region.
    start, stop = np.max([a[0], b[0]]), np.min([a[-1], b[-1]])
    ida = (a >= start) & (a <= stop)
    idb = (b >= start) & (b <= stop)

    if not len(a[ida]) and not len(b[idb]):
        return np.array([])
    elif len(a[ida]) == 1 and len(b[idb]) == 1:
        return a[ida]
    elif len(b[idb]) == 1:
        intersection = a[ida]
    elif len(a[ida]) == 1:
        intersection = b[idb]
    elif np.abs(np.mean(np.diff(a[ida]))) <= np.abs(np.mean(np.diff(b[idb]))):
        intersection = a[ida]
    else:
        intersection = b[idb]

    # Add start and stop points if they are not included in the intersection.
    if start not in intersection:
        intersection = np.concatenate([[start], intersection])
    if stop not in intersection:
        intersection = np.concatenate([intersection, [stop]])

    return intersection


def union(
    a: npt.NDArray[np.float64], b: npt.NDArray[np.float64], sort: bool = False
) -> npt.NDArray[np.float64]:
    # Sort the input arrays if required.
    if sort:
        a, b = np.sort(a), np.sort(b)

    # Sort the input arrays by their minimum value.
    a, b = sorted([a, b], key=np.min)

    # Determine the indices of the overlapping regions.
    start, stop = np.max([a[0], b[0]]), np.min([a[-1], b[-1]])

    intersection = intersect(a, b, sort=False)

    # The if statement is always ran because the arrays are already sorted by their
    # minimum value.
    if a[0] < b[0]:
        union = np.concatenate([a[a < start], intersection])
    else:
        union = np.concatenate([b[b < start], intersection])

    # Check the last element of the arrays to decide which array append.
    if a[-1] > b[-1]:
        union = np.concatenate([union, a[a > stop]])
    else:
        union = np.concatenate([union, b[b > stop]])

    return union


def merge(
    a: npt.NDArray[Any],
    b: npt.NDArray[Any],
    mode: str = "intersection",
    sort: bool = False,
) -> npt.NDArray[Any]:
    """Merge two array using the specified mode."""
    if mode == "intersection":
        merged = intersect(a, b, sort)
    elif mode == "union":
        merged = union(a, b, sort)
    else:
        raise ValueError("Invalid mode")
    return merged


def discretize_intervals(intervals: list[list[float]]) -> npt.NDArray[np.float64]:
    # Check if the start energy is smaller than the end energy for all regions.
    if not all(interval[0] < interval[1] for interval in intervals):
        raise ValueError(
            "The start energy must be smaller than the end energy for all regions."
        )

    # Check if the step is positive for all regions.
    if not all(interval[2] > 0 for interval in intervals):
        raise ValueError("The step must be positive for all regions.")

    # Check if the start energies of the regions are in increasing order.
    if not all(
        intervals[i][0] <= intervals[i + 1][0] for i in range(len(intervals) - 1)
    ):
        raise ValueError(
            "The start energies of the regions must be in increasing order."
        )

    points = []
    for i, (start, end, step) in enumerate(intervals):
        points.extend(np.arange(start, end, step))
        # Add the end point of the last region or if it does not intersection with
        # the next region.
        if i == len(intervals) - 1 or end < intervals[i + 1][0]:
            points.append(end)

    return np.array(points)


def trapezoid(
    y: npt.NDArray[np.float64], x: npt.NDArray[np.float64] | None = None
) -> float:
    """Integrate using the composite trapezoidal rule while ignoring NaN values.

    Args:
        y : The values of the function to integrate. NaN values are ignored.
        x : The sample points corresponding to `y` values. If None, points are
            assumed to be spaced at a unit distance.

    Returns:
        The estimated integral of `y` using the trapezoidal rule.
    """
    y = np.asarray(y)
    x = (
        np.arange(len(y), dtype=np.float64)
        if x is None
        else np.asarray(x, dtype=np.float64)
    )

    # Ensure x and y have the same shape
    if y.shape != x.shape:
        raise ValueError("Shape of x and y must be the same.")

    # Identify non-NaN regions
    mask = ~np.isnan(y)
    y = y[mask]
    x = x[mask]

    # Perform trapezoidal integration on non-NaN regions
    if y.size < 2:  # noqa: PLR2004
        return 0  # Not enough points to perform integration

    if np.version.version < "2.0.0":
        return np.trapz(y, x)  # type: ignore # noqa: NPY201
    else:
        return np.trapezoid(y, x)  # type: ignore
