"""Classes to deal with different types of measurement correctors."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from functools import cached_property
from itertools import cycle

import numpy as np
import numpy.typing as npt

from daxs.scans import Scan, Scans

logger = logging.getLogger(__name__)


class ConcentrationCorrectionError(Exception):
    def __init__(self, message: str):
        super().__init__(f"{message} The concentration correction failed.")


class Corrector(ABC):
    """Base class for measurement correctors."""

    @abstractmethod
    def apply(self, scans: Scans) -> None:
        """Apply the correction to the scans."""


class SimpleConcentrationCorrector(Corrector):
    """Class to perform simple, length-based, concentration corrections."""

    def __init__(self, scans: Scan | Scans | list[Scan]):
        """Initialize the simple concentration corrector.

        Args:
            scans: Scans used for concentration correction.
        """
        if isinstance(scans, Scans):
            self.conc_corr_scans = scans
        elif isinstance(scans, list):
            self.conc_corr_scans = Scans(scans)
        else:
            self.conc_corr_scans = Scans([scans])

    def apply(self, scans: Scans) -> None:
        logger.info("Applying simple concentration correction.")
        # When there is a single concentration correction scan and the number
        # of points in it is equal to the number of scans to be corrected, each
        # point will be used to correct a scan.
        if len(self.conc_corr_scans) == 1:
            [conc_corr_scan] = self.conc_corr_scans
            if len(scans) == conc_corr_scan.signal.size:
                for i, scan in enumerate(scans):
                    try:
                        scalars = (conc_corr_scan.signal[i], conc_corr_scan.monitor[i])
                    except IndexError:
                        scalars = (conc_corr_scan.signal[i],)
                    scan.divide_by_scalars(*scalars)
                return
        # When there is a single concentration correction scan and the previous
        # condition is not met, divide all scans by it, by cycling it.
        if len(self.conc_corr_scans) == 1:
            conc_corr_scans = cycle(self.conc_corr_scans)
        # When the number of scans to be corrected is equal to the number of
        # concentration correction scans, each scan will be corrected by a
        # corresponding concentration correction scan.
        elif len(self.conc_corr_scans) == len(scans):
            conc_corr_scans = self.conc_corr_scans
        # No other case is supported.
        else:
            raise ConcentrationCorrectionError(
                "Incompatible number of scans to correct and concentration "
                "correction scans."
            )

        for scan, conc_corr_scan in zip(scans, conc_corr_scans):
            try:
                scan.divide_by_scan(conc_corr_scan)
            except (TypeError, ValueError) as e:
                raise ConcentrationCorrectionError(
                    f"The length of the signal or monitor in the scan {scan.label} "
                    "is different than that from the correction scan "
                    f"{conc_corr_scan.label}."
                ) from e


class DataDrivenConcentrationCorrector(Corrector):
    """Class to perform concentration corrections using data from specified mappings."""

    def __init__(self, scans: Scan | Scans | list[Scan], data_mappings: dict[str, str]):
        """Initialize the data-driven concentration corrector.

        Args:
            scans: Scans used for concentration correction.
            data_mappings: Mappings between scan attributes and paths in the raw data.
        """
        if isinstance(scans, Scans):
            self.conc_corr_scans = scans
        elif isinstance(scans, list):
            self.conc_corr_scans = Scans(scans)
        else:
            self.conc_corr_scans = Scans([scans])
        self.data_mappings = data_mappings

    @cached_property
    def conc_corr_points(self) -> npt.NDArray[np.float64]:
        """Array of points used to determine the concentration correction indices.

        Returns:
            Array of points used for concentration correction.

        Raises:
            ValueError: If the concentration correction counters do not have the same
              length.
        """
        points = []
        for path in self.data_mappings.values():
            points_at_path = []
            for scan in self.conc_corr_scans:
                if scan.filename is None or scan.index is None:
                    raise ConcentrationCorrectionError(
                        "The concentration correction scans must have a filename "
                        "and index defined."
                    )
                points_at_path.extend(
                    scan.read_data_at_paths(scan.filename, scan.index, path)
                )
            points.append(points_at_path)

        try:
            return np.asarray(points, dtype=np.float64).T
        except ValueError as e:
            raise ConcentrationCorrectionError(
                "The concentration correction counters must have the same length."
            ) from e

    def find_conc_corr_indices(self, scan: Scan) -> list[int]:
        """Determine the indices of the concentration correction data for the scan.

        Args:
            scan: Scan for which the concentration correction data need to be found.

        Returns:
            Indices of the concentration correction data for the points in the scan.
        """
        # Get concentration correction points.
        conc_corr_points = self.conc_corr_points

        # Get the scan data at the same keys as the concentration correction data.
        data_points = []
        for key in self.data_mappings:
            try:
                data_points.append(scan.data[key])
            except KeyError as e:
                raise ConcentrationCorrectionError(
                    f"The data in scan {scan.label} does not have the key {key} among"
                    "the source data paths. Make sure the source data paths are"
                    "correctly set."
                ) from e
        data_points = np.asarray(data_points)

        # Add a new axis if the data points are 1D.
        if data_points.ndim == 1:
            data_points = data_points[:, None]
        # Transpose the data points to have shape (N, p) [N points, p paths].
        data_points = data_points.T

        # Calculate distances between each data point and each concentration correction
        # point.
        # data_points has shape (N, p) [N points, p paths]
        # data_points[:, None, :] has shape (N, 1, p)
        # conc_corr_points has shape (M, p) [M points, p paths]
        # conc_corr_points[None, :, :] has shape (1, M, p) [M points]
        # The subtraction uses broadcasting to yield an array of shape (N, M, p),
        # np.linalg.norm(..., axis=2) computes the Euclidean distance resulting in an
        # array of shape [N, M].

        distances = np.linalg.norm(
            data_points[:, None, :] - conc_corr_points[None, :, :],
            axis=2,
        )

        threshold = np.finfo(np.float64).eps
        # For each data point, find the index where the distance is smaller
        # than the threshold. If the number of indices is different than 1, raise an
        # error.
        mask = distances < threshold
        if np.any(mask.sum(axis=1) == 0):
            raise ConcentrationCorrectionError(
                f"No concentration correction points were found for scan {scan.label}."
            )
        if np.any(mask.sum(axis=1) > 1):
            raise ConcentrationCorrectionError(
                f"Multiple concentration correction points were found for "
                f"scan {scan.label}."
            )
        _, indices = np.where(mask)
        return indices.tolist()

    def create_conc_corr_scan(self, indices: list[int]) -> Scan:
        """Create a scan with the concentration correction data.

        Args:
            indices: Indices of the concentration correction data to be used.

        Returns:
            Scan with the concentration correction data at the specified indices.
        """
        signal = np.concatenate([scan.signal for scan in self.conc_corr_scans])
        x = np.ones_like(signal[indices])
        scan = Scan(x, signal[indices])

        try:
            monitor = np.concatenate([scan.monitor for scan in self.conc_corr_scans])
            scan.monitor = monitor[indices]
        except IndexError:
            pass
        return scan

    def apply(self, scans: Scans) -> None:
        """Apply the concentration correction using data from the specified paths.

        Args:
            scans: Scans to be corrected.
        """
        logger.info("Applying data-informed concentration correction.")
        for scan in scans:
            indices = self.find_conc_corr_indices(scan)
            conc_corr_scan = self.create_conc_corr_scan(indices)
            scan.divide_by_scan(conc_corr_scan)


class DeadTimeCorrector(Corrector):
    """Class to perform dead time corrections."""
