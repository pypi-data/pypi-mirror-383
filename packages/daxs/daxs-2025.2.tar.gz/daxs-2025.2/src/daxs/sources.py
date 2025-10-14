"""The module provides classes to deal with different types of data sources."""

from __future__ import annotations

import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Any

import h5py
import numpy as np
import numpy.typing as npt

from daxs.config import Config
from daxs.scans import Scan, Scans

logger = logging.getLogger(__name__)

use_blissdata_api = Config().get("use_blissdata_api", False)
if use_blissdata_api:
    from blissdata.h5api.dynamic_hdf5 import File
else:
    from silx.io.h5py_utils import File


class BlissPath:
    def __init__(  # noqa
        self,
        root: str,
        proposal: str,
        beamline: str,
        session: str,
        sample: str,
        dataset: str,
        data_type: str = "RAW_DATA",
    ) -> None:
        self.root = root
        self.proposal = proposal
        self.beamline = beamline
        self.session = session
        self.sample = sample
        self.dataset = dataset
        self.data_type = data_type

    @property
    def collection(self) -> str:
        return f"{self.sample}_{self.dataset}"

    @property
    def filename(self) -> str:
        return f"{self.collection}.h5"

    @property
    def path(self) -> str:
        return os.path.join(
            self.root,
            self.proposal,
            self.beamline,
            self.session,
            self.data_type,
            self.sample,
            self.collection,
            self.filename,
        )

    @classmethod
    def from_path(cls, path: str) -> BlissPath:
        """Create a BlissPath object from a path.

        Args:
            path: The file path to parse.

        Returns:
            A new BlissPath object.

        Raises:
            ValueError: If the path is invalid.
        """
        tokens: list[str] = os.path.normpath(path).split(os.sep)
        if not tokens:
            raise ValueError("Invalid path.")
        tokens = tokens[::-1]
        _, collection, sample, data_type, session, beamline, proposal, *root = tokens
        # Determine the dataset name.
        dataset = collection.split(sample)[1][1:]
        # Create the root.
        root = os.path.join(os.sep, *root[::-1])
        return cls(root, proposal, beamline, session, sample, dataset, data_type)


class Source(ABC):
    """Base class for sources of scans."""

    @property
    @abstractmethod
    def filename(self) -> str | None:
        """The filename of the source."""

    @property
    @abstractmethod
    def data_mappings(self) -> dict[str, Any]:
        """The mappings between scan attributes and paths in the source."""

    @property
    @abstractmethod
    def scans(self) -> Scans:
        """Return all source scans."""

    @data_mappings.setter
    @abstractmethod
    def data_mappings(self, data_mappings: dict[str, Any]) -> None:
        """Set the mappings between scan attributes and paths in the source."""

    @abstractmethod
    def read_scans(
        self, scan_ids: list[int] | npt.NDArray[np.int64] | None = None
    ) -> Scans:
        """Return all source scans."""


class Hdf5Source(Source):
    def __init__(
        self,
        filename: str,
        scan_ids: int | list[int] | npt.NDArray[np.int64] | str,
        data_mappings: dict[str, Any],
    ) -> None:
        """Class for a HDF5 source of scans.

        Args:
            filename: Name of the HDF5 file.
            scan_ids: Scan indices to read.
            data_mappings: Mappings between scan attributes (x, signal, monitor, etc.)
              and paths in the HDF5 file.
        """
        self.filename = filename
        self.scan_ids = scan_ids
        self.data_mappings = data_mappings

        self._scan_titles: dict[int, str] | None = None

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, filename: str) -> None:
        self._filename = filename
        self._scan_titles = None

    @property
    def scan_ids(self) -> list[int]:
        return self._scan_ids

    @scan_ids.setter
    def scan_ids(self, ids: int | list[int] | npt.NDArray[np.int64] | str) -> None:
        if isinstance(ids, int):
            self._scan_ids = [ids]
        elif isinstance(ids, list):
            for item in ids:
                if not isinstance(item, int):
                    raise ValueError("The scan indices must be integers.")
            self._scan_ids = ids
        elif isinstance(ids, np.ndarray):
            self._scan_ids = ids.astype(np.int64).tolist()
        elif isinstance(ids, str):
            self._scan_ids = self._parse_scan_ids(ids)
        else:
            raise ValueError("Invalid scan indices.")

    @property
    def data_mappings(self) -> dict[str, Any]:
        return self._data_mappings

    @data_mappings.setter
    def data_mappings(self, data_mappings: dict[str, Any]) -> None:
        if not isinstance(data_mappings, dict):
            raise ValueError("The data_mappings must be a dictionary")
        self._data_mappings = data_mappings

    @property
    def scans(self) -> Scans:
        """Return all source scans."""
        return self.read_scans()

    def _parse_scan_ids(self, scan_ids: str) -> list[int]:  # noqa
        """Parse a string specification into a list of scan indices."""
        scan_ids = scan_ids.strip()
        if not scan_ids:
            return []

        included_scan_ids: set[int] = set()
        excluded_scan_ids: set[int] = set()

        # Regex to match "AND" and "NOT" operators, case insensitive.
        tokens = re.compile(r"\b(and|not)\b", re.IGNORECASE)

        last_end = 0
        current_operator = "AND"
        parts: list[tuple[str, str]] = []

        # Split the input string into parts based on the operators.
        for match in tokens.finditer(scan_ids):
            fragment = scan_ids[last_end : match.start()].strip()
            if fragment:
                parts.append((current_operator, fragment))
            elif last_end > 0:
                raise ValueError(f"Missing expression after '{current_operator}'.")
            current_operator = match.group(1).upper()
            last_end = match.end()

        # Handle the tail part after the last logical operator.
        tail = scan_ids[last_end:].strip()
        if tail:
            operator = current_operator if last_end else "AND"
            parts.append((operator, tail))
        elif last_end > 0:
            raise ValueError(f"Missing expression after '{current_operator}'.")

        if not parts:
            raise ValueError("No valid scan selection found in the expression.")

        for operator, fragment in parts:
            try:
                ids = set(self._parse_scan_ids_fragment(fragment))
                if operator == "NOT":
                    excluded_scan_ids.update(ids)
                elif operator == "AND":
                    included_scan_ids.update(ids)
                else:
                    raise ValueError(f"Unrecognized operator: '{operator}'.")
            except ValueError as e:
                raise ValueError(f"Error in fragment '{fragment}': {e}.") from e

        if not included_scan_ids:
            logger.warning("No scans were included in the final selection.")

        return sorted(included_scan_ids - excluded_scan_ids)

    def _parse_scan_ids_fragment(self, fragment: str) -> list[int]:
        """Parse a single fragment of the scan ID specification."""
        fragment = fragment.strip()
        if not fragment:
            return []

        if fragment.lower() == "all":
            return list(self._read_scan_titles_from_file())

        single_match = re.fullmatch(r"\d+", fragment)
        if single_match:
            return [int(fragment)]

        range_match = re.fullmatch(r"(\d+)-(\d+)(?::(\d+))?", fragment)
        if range_match:
            try:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                step = int(range_match.group(3)) if range_match.group(3) else 1

                if step <= 0:
                    raise ValueError(
                        f"The step ({step}) range must be a positive integer."
                    )
                if start > end:
                    raise ValueError(
                        f"The start in the range of scan indices ({start}) "
                        f"must be smaller or equal to the end ({end})."
                    )
                return list(range(start, end + 1, step))
            except ValueError as e:
                # Re-raise parsing errors with more context.
                raise ValueError(f"Invalid range format: {e}") from e

        return self._get_scan_ids_by_title_regex(fragment)

    def _get_scan_ids_by_title_regex(self, regex: str) -> list[int]:
        """Get the scan indices whose titles match the given regular expression."""
        titles = self._read_scan_titles_from_file()
        try:
            pattern = re.compile(regex, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex '{regex}': {e}")
        matching_scan_ids = [
            scan_id for scan_id, title in titles.items() if pattern.search(title)
        ]
        return matching_scan_ids

    def _read_scan_titles_from_file(self) -> dict[int, str]:
        """Read all scan titles from the HDF5 file."""
        if self._scan_titles is not None:
            return self._scan_titles

        kwargs: dict[str, Any] = {}
        if use_blissdata_api:
            kwargs["retry_timeout"] = Config().get("dynamic_hdf5_retry_timeout")

        titles: dict[int, str] = {}
        with File(self.filename, **kwargs) as fh:
            indices = fh.keys()
            try:
                indices = [int(scan_id.split(".")[0]) for scan_id in indices]
            except ValueError:
                raise ValueError("Invalid scan index format in HDF5 file.")
            indices = sorted(set(indices))

            logger.info(indices)

            for scan_id in indices:
                title = fh[f"{scan_id}.1/title"]
                if isinstance(title, h5py.Dataset):
                    titles[scan_id] = str(title[()])
                else:
                    raise ValueError(f"Missing title for scan {scan_id}.")
        self._scan_titles = titles
        return self._scan_titles

    def read_scans(
        self, scan_ids: list[int] | npt.NDArray[np.int64] | None = None
    ) -> Scans:
        """Read the scans from the source."""
        if scan_ids is None:
            scan_ids = self.scan_ids
        scans = []
        for scan_id in scan_ids:
            try:
                scans.append(self.read_scan(scan_id))
            except Exception as e:
                logger.warning(
                    f"Skipping scan {scan_id} in {self.filename} due to an "
                    f"unexpected error: {e}"
                )
                pass
        return Scans(scans)

    def read_scan(self, scan_id: int) -> Scan:
        """Return a scan object at the index."""
        if "x" not in self.data_mappings:
            raise ValueError("The data_mappings attribute must contain an entry for x.")
        if "signal" not in self.data_mappings:
            raise ValueError(
                "The data_mappings attribute must contain an entry for signal."
            )
        return Scan.from_hdf5(self.filename, scan_id, self.data_mappings)


class TxtSource(Source):
    def __init__(
        self,
        filename: str,
        data_mappings: dict[str, int],
        **kwargs: Any,
    ) -> None:
        """Class for a text file source of scans.

        Args:
            filename: Name of the text file.
            data_mappings: Dictionary mapping scan attributes to column indices.
                Must contain entries for "x" and "signal". Column indices are 0-based.
            **kwargs: Additional keyword arguments passed to np.loadtxt, e.g.,
                delimiter, skiprows, etc.
        """
        self._filename = filename
        self._data_mappings = data_mappings
        self._kwargs = kwargs

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def data_mappings(self) -> dict[str, Any]:
        return self._data_mappings

    @data_mappings.setter
    def data_mappings(self, data_mappings: dict[str, Any]) -> None:
        self._data_mappings = data_mappings

    @property
    def scans(self) -> Scans:
        """Return all source scans."""
        return self.read_scans()

    def read_scans(
        self, scan_ids: list[int] | npt.NDArray[np.int64] | None = None
    ) -> Scans:
        """Read the scans from the source."""
        if scan_ids is not None and len(scan_ids) > 0:
            raise ValueError("Text file sources must contain a single scan.")
        return Scans([self.read_scan(0)])

    def read_scan(self, scan_id: int) -> Scan:
        """Return the scan object."""
        if scan_id != 0:
            raise ValueError("Text file sources must contain a single scan.")
        return Scan.from_txt(self.filename, self.data_mappings, **self._kwargs)
