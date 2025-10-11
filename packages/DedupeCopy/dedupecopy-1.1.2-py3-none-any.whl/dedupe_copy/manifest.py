"""Manifest file handling for dedupe_copy.
Manifests store a mapping of hash -> list of files with that hash
They are the core data structure use to track duplicates
and what files have been read.
"""

import logging
import os
import random
import threading
from typing import Any, List, Optional, Set, Tuple, Union

from .disk_cache_dict import CacheDict, DefaultCacheDict

logger = logging.getLogger(__name__)


class Manifest:
    """Storage of manifest data. Presents the hash dict but tracks the
    read files in a separate structure"""

    cache_size = 10000

    def __init__(
        self,
        manifest_paths: Optional[Union[str, List[str]]],
        save_path: Optional[str] = None,
        temp_directory: Optional[str] = None,
        save_event: Optional[threading.Event] = None,
    ) -> None:
        self.temp_directory = temp_directory
        if save_path:
            self.path = save_path
        else:
            assert (
                temp_directory is not None
            ), "temp_directory must be provided if save_path is not"
            self.path = os.path.join(
                temp_directory, f"temporary_{random.getrandbits(16)}.dict"
            )
        self.md5_data: Any = {}
        self.read_sources: Any = {}
        self.save_event = save_event
        if manifest_paths:
            if not isinstance(manifest_paths, list):
                self.load(manifest_paths)
            else:
                self._load_manifest_list(manifest_paths)
        else:
            sources_path = f"{self.path}.read"
            # no data yet
            if os.path.exists(self.path):
                logger.info("Removing old manifest file at: %r", self.path)
                os.unlink(self.path)
            if os.path.exists(sources_path):
                logger.info("Removing old manifest sources file at: %r", sources_path)
                os.unlink(sources_path)
            logger.info("creating manifests %s / %s", self.path, sources_path)
            self.md5_data = DefaultCacheDict(
                list, db_file=self.path, max_size=self.cache_size
            )
            self.read_sources = CacheDict(
                db_file=sources_path, max_size=self.cache_size
            )

    def __contains__(self, key: str) -> bool:
        """Check if key exists in manifest."""
        return key in self.md5_data

    def __getitem__(self, key: str) -> Any:
        """Get value for key from manifest."""
        return self.md5_data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set value for key in manifest."""
        self.md5_data[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete key from manifest."""
        del self.md5_data[key]

    def __len__(self) -> int:
        """Return number of hash keys in manifest."""
        return len(self.md5_data)

    def save(
        self,
        path: Optional[str] = None,
        keys: Optional[List[str]] = None,
        no_walk: bool = False,
    ) -> None:
        """Save manifest to disk at specified path."""
        if self.save_event:
            self.save_event.set()
        path = path or self.path
        try:
            # Save the main data first, then populate and save sources.
            # This ensures that if a read happens during save, the main
            # data is consistent.
            logger.info("Writing manifest of %d hashes to %s", len(self.md5_data), path)
            self.md5_data.save(db_file=path)

            if not no_walk:
                self._populate_read_sources(keys=keys)

            logger.info(
                "Writing sources of %d files to %s.read", len(self.read_sources), path
            )
            self.read_sources.save(db_file=f"{path}.read")
        finally:
            if self.save_event:
                self.save_event.clear()

    def close(self) -> None:
        """Close the manifest and its underlying database files."""
        if hasattr(self, "md5_data") and hasattr(self.md5_data, "close"):
            self.md5_data.close()
        if hasattr(self, "read_sources") and hasattr(self.read_sources, "close"):
            self.read_sources.close()

    def load(self, path: Optional[str] = None) -> None:
        """Load manifest from disk at specified path."""
        path = path or self.path
        self.close()
        self.md5_data, self.read_sources = self._load_manifest(path=path)

    def items(self) -> Any:
        """Return items view of manifest data."""
        return self.md5_data.items()

    def iteritems(self) -> Any:
        """Deprecated: Use items() instead"""
        return self.md5_data.items()

    def _populate_read_sources(self, keys: Optional[List[str]] = None) -> None:
        """Populate the read_sources list from the md5_data."""
        if not keys:
            dict_iter = self.md5_data.items()
        else:
            dict_iter = ((k, self.md5_data[k]) for k in keys)
        for _, info in dict_iter:
            for file_data in info:
                src = file_data[0]
                if src not in self.read_sources:
                    self.read_sources[src] = None

    def hash_set(self) -> Set[str]:
        """Return set of all hash keys in manifest."""
        return set(self.md5_data.keys())

    def _load_manifest(self, path: Optional[str] = None) -> Tuple[Any, Any]:
        path = path or self.path
        logger.info("Reading manifest from %r...", path)
        # Would be nice to just get the fd, but backends require a path
        md5_data = DefaultCacheDict(list, db_file=path, max_size=self.cache_size)
        md5_data.load()
        logger.info("... read %d hashes", len(md5_data))
        read_sources = CacheDict(db_file=f"{path}.read", max_size=self.cache_size)
        read_sources.load()
        logger.info("... in %d files", len(read_sources))
        return md5_data, read_sources

    @staticmethod
    def _combine_manifests(
        manifests: List[Tuple[Any, Any]], temp_directory: Optional[str]
    ) -> Tuple[Any, Any]:
        """Combine multiple manifest data structures into one.
        Args:
            manifests: List of (md5_data, read_sources) tuples to combine
            temp_directory: The directory to use for temporary files.
        Returns:
            Tuple of (combined_md5_data, combined_read_sources)
        """
        assert temp_directory is not None
        combined_md5_path = os.path.join(
            temp_directory, f"combined_md5_{random.getrandbits(16)}.dict"
        )
        combined_read_path = f"{combined_md5_path}.read"
        combined_md5 = DefaultCacheDict(list, db_file=combined_md5_path)
        combined_read = CacheDict(db_file=combined_read_path)

        for m, r in manifests:
            for key, files in m.items():
                for info in files:
                    current_files = combined_md5[key]
                    if info not in current_files:
                        current_files.append(info)
                        combined_md5[key] = current_files
            for key in r:
                combined_read[key] = None
            m.close()
            r.close()
        return combined_md5, combined_read

    def _load_manifest_list(self, manifests: List[str]) -> None:
        if not isinstance(manifests, list):
            raise TypeError("manifests must be a list")

        # If there's only one manifest, load it directly without combining.
        if len(manifests) == 1:
            self.load(manifests[0])
            return

        loaded = []
        try:
            for src in manifests:
                loaded.append(self._load_manifest(src))

            # Close existing manifests before replacing them
            self.close()

            self.md5_data, self.read_sources = self._combine_manifests(
                loaded, self.temp_directory
            )
        finally:
            # Ensure temporary manifest dicts used for loading are closed
            for md5_data, read_sources in loaded:
                if hasattr(md5_data, "close"):
                    md5_data.close()
                if hasattr(read_sources, "close"):
                    read_sources.close()

    def convert_manifest_paths(
        self, paths_from: str, paths_to: str, temp_directory: Optional[str] = None
    ) -> None:
        """Replaces all prefixes for all paths in the manifest with a new prefix"""
        temp_directory = temp_directory or self.temp_directory
        for key, val in self.md5_data.items():
            new_values = []
            for file_data in val:
                new_values.append(
                    [file_data[0].replace(paths_from, paths_to, 1)] + file_data[1:]
                )
            self.md5_data[key] = new_values
        # build a new set of values and move into place
        # Note: Using CacheDict for read_sources (could optimize with a persistent
        # set implementation)
        db_file = self.read_sources.db_file_path()
        assert temp_directory is not None, "temp_directory must be provided"
        new_sources = CacheDict(
            db_file=os.path.join(temp_directory, "temp_convert.dict"),
            max_size=self.cache_size,
        )
        for key in self.read_sources:
            new_sources[key.replace(paths_from, paths_to, 1)] = None
        del self.read_sources
        new_sources.save(db_file=db_file)
        self.read_sources = new_sources
        self.md5_data.save()
        self.read_sources.save()
