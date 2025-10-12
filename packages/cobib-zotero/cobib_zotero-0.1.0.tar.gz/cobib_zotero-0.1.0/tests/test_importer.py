"""Tests for the ZoteroImporter."""

from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from tempfile import gettempdir
from typing import Generator

import pytest
from cobib.commands import ImportCommand
from cobib.config import config

from cobib_zotero.importer import ZoteroImporter

TMPDIR = Path(gettempdir()).resolve()


class TestZoteroImporter:
    """Tests for the ZoteroImporter."""

    TEST_DIR = TMPDIR / "cobib_zotero_test"
    """Path to a temporary test directory."""

    @pytest.fixture(autouse=True)
    def setup(self) -> Generator[None, None, None]:
        """Setup."""
        config.defaults()

        self.TEST_DIR.mkdir(parents=True, exist_ok=False)
        database_file = self.TEST_DIR / "database.yaml"
        database_file.touch(exist_ok=False)

        config.database.cache = None
        config.database.file = str(database_file)
        config.database.git = False
        config.utils.file_downloader.default_location = str(self.TEST_DIR)
        config.logging.version = None

        yield

        rmtree(self.TEST_DIR, ignore_errors=True)

        # ensure that we also clean up whatever we have set up
        config.defaults()

    @pytest.mark.asyncio
    async def test_fetch(self) -> None:
        """Test fetching entries from the Zotero API."""
        importer = ZoteroImporter("8608002", "user", skip_download=True)
        # NOTE: even though attachments are not accessible via public libraries, we explicitly skip
        # downloading them, just to be sure.
        imported_entries = await importer.fetch()

        assert len(imported_entries) == 2

    @pytest.mark.asyncio
    async def test_command(self) -> None:
        """Test integration into coBib's ImportCommand."""
        cmd = ImportCommand("--skip-download", "--zotero", "8608002", "user")
        await cmd.execute()

        assert len(cmd.new_entries) == 2
