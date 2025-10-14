"""The module provides functions for filtering data."""

from __future__ import annotations

import logging

import numpy as np
import numpy.typing as npt

logger = logging.getLogger(__name__)


def hampel(
    data: npt.NDArray[np.float64],
    window_size: int | None = None,
    threshold: float = 3.5,
    axis: int = 0,
    k: float = 1.4826,
) -> tuple[npt.NDArray[np.bool_], npt.NDArray[np.float64]]:
    """Outliers detection using the Hampel filter.

    More details about the filter can be found here:

    - https://fr.mathworks.com/help/dsp/ref/hampelfilter.html
    - https://dsp.stackexchange.com/questions/26552
    - https://stackoverflow.com/questions/22354094

    Args:
        data: Input data.
        window_size: Size of the sliding window.
        threshold: Threshold for outlier detection expressed in number of standard
          deviations. Iglewicz and Hoaglin [1]_ suggest using a value of 3.5, but
          larger values are often needed to avoid removing data points from a
          noisy signal.
        axis: Axis along which the detection is performed.
        k: Scale factor for the median absolute deviation. The default value is
          1.4826, which is the scale factor for normally distributed data.

    Returns:
        Mask identifying the outliers, and the rolling window median.

    References:
        .. [1] Boris Iglewicz and David Hoaglin (1993) "Volume 16: How to Detect
           and Handle Outliers", The ASQC Basic References in Quality Control:
           Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.
    """
    if window_size is None:
        SECTIONS: int = 10
        window_size = data.shape[axis] // SECTIONS

    # Don't allow the window size to be too small or larger than the data.
    MIN_WINDOW_SIZE = 3
    window_size = max(window_size, MIN_WINDOW_SIZE)
    window_size = min(window_size, data.shape[axis])

    # Make the size of the window an odd number.
    if window_size % 2 == 0:
        window_size -= 1

    logger.debug("Hampel filter window size = %d.", window_size)

    # Pad the data along the direction used for the outlier detection.
    pad_size = np.zeros((len(data.shape), 2), dtype=int)
    pad_size[axis] = np.array((window_size // 2, window_size // 2))
    padded_data = np.pad(data, pad_size)

    # Create a sliding window view of the padded data.
    padded_data_views = np.lib.stride_tricks.sliding_window_view(
        padded_data, window_size, axis, subok=True
    )

    # Compute the median of each view. As the views increase the number of dimensions,
    # the axis argument always identifies the axis along which the median is computed.
    medians = np.median(padded_data_views, axis=-1)
    abs_diff = np.abs(data - medians)

    outliers = np.full(data.shape, False, dtype=bool)

    # Put the median in a suitable shape.
    medians_views = np.repeat(medians, window_size).reshape(padded_data_views.shape)

    # Calculate the median absolute deviation for each view.
    mad = np.median(np.abs(padded_data_views - medians_views), axis=-1)

    # Calculate the standard deviation. We assume that the data is normally distributed.
    # https://en.wikipedia.org/wiki/Median_absolute_deviation
    sigma = k * mad

    score = threshold * sigma
    outliers[(abs_diff > score)] = True

    # If the score is zero, the data is not necessarily an outlier because all
    # absolute differences with the exception of zero will be greater than it.
    # For this case we add a condition that excludes from the outliers the points
    # that are smaller than the median.
    outliers[(score == 0) & (np.abs(data) < np.abs(np.median(data)))] = False

    return outliers, medians
