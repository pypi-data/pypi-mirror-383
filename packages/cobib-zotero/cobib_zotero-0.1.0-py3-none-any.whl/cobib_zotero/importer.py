"""The `cobib-zotero` importer backend."""

from __future__ import annotations

import argparse
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, ClassVar

from cobib.config import config
from cobib.database import Author, Entry
from cobib.importers.base_importer import Importer
from cobib.utils.logging import HINT
from pyzotero.zotero import Zotero
from typing_extensions import override

LOGGER = logging.getLogger(__name__)
"""@private module logger."""


class ZoteroImporter(Importer):
    """The Zotero Importer.

    This importer can parse the following arguments:

        * `id`: the Zotero library ID from which to import.
        * `type`: the Zotero library type. This can be either `user` or `group`.
        * `--api-key`: the Zotero API key to use. This may ONLY be omitted when the library is
          publicly accessible. And even then, its attachments may not be available.
    """

    name = "zotero"

    FIELD_MAP: ClassVar[dict[str, str | None]] = {
        # mapped fields
        "publicationTitle": "journal",
        # trivial fields
        "DOI": "doi",
        "ISSN": "issn",
        "issue": "issue",
        "pages": "pages",
        "series": "series",
        "title": "title",
        "url": "url",
        "volume": "volume",
        # skipped fields
        "key": None,
        "shortTitle": None,
        "version": None,
    }
    """A mapping of Zotero's field names to coBib's field names.

    When a field name maps to `None`, this means it will skip it without warning about its presence.
    """

    @override
    def __init__(self, *args: str, skip_download: bool = False) -> None:
        super().__init__(*args, skip_download=skip_download)

        self._imported_entries: list[Entry] = []

    @property
    @override
    def imported_entries(self) -> list[Entry]:
        return self._imported_entries

    @imported_entries.setter
    @override
    def imported_entries(self, entries: list[Entry]) -> None:
        self._imported_entries = entries

    @override
    @classmethod
    def init_argparser(cls) -> None:
        parser = argparse.ArgumentParser(
            prog="zotero",
            description="Zotero migration parser.",
            epilog="Read cobib-zotero.7 for more help.",
        )

        parser.add_argument("id", type=str, help="the Zotero library ID from which to import.")
        parser.add_argument(
            "type", type=str, choices=["user", "group"], help="the Zotero library type."
        )
        parser.add_argument(
            "--api-key",
            type=str,
            default=None,
            help=(
                "the Zotero API key to use. This may ONLY be omitted when the library to be "
                "imported from is publicly accessible."
            ),
        )

        cls.argparser = parser

    @override
    async def fetch(self) -> list[Entry]:  # noqa: PLR0912
        # NOTE: we must import this here to avoid a circular import between cobib.commands.import
        # and cobib_zotero.importer
        from cobib.commands.modify import evaluate_as_f_string  # noqa: PLC0415

        LOGGER.debug("Starting Zotero fetching.")

        journal_abbrev_hint_given = False

        zotero = Zotero(self.largs.id, self.largs.type, self.largs.api_key)
        LOGGER.log(HINT, f"Detected {zotero.num_items()} entries in the Zotero database.")

        for result in zotero.everything(zotero.top()):
            key = result["key"]
            entry_data: dict[str, Any] = {}
            unprocessed_fields: set[str] = set()

            for field, value in result["data"].items():
                if not bool(value):
                    LOGGER.debug(f"Skipping empty field '{field}' of Zotero entry '{key}'.")
                    continue

                match field:
                    case "itemType":
                        match value:
                            case "journalArticle":
                                entry_data["ENTRYTYPE"] = "article"
                            case _:
                                LOGGER.error(
                                    f"Entries of type '{value}' are not supported by cobib-zotero! "
                                    "Please open an issue and provide an example Zotero entry as "
                                    "well as the expected Bib(La)TeX form of this entry."
                                )
                                break
                    case _ if field in ZoteroImporter.FIELD_MAP:
                        mapped_field = ZoteroImporter.FIELD_MAP[field]
                        if mapped_field is not None:
                            entry_data[mapped_field] = value
                    case "creators":
                        creators: dict[str, list[Author]] = defaultdict(list)
                        unprocessed_creators: set[str] = set()
                        for creator in value:
                            match creator["creatorType"]:
                                case "author" as creator_field:
                                    # TODO: handle simple names. This is blocked by
                                    # https://gitlab.com/cobib/cobib/-/issues/184
                                    creators[creator_field].append(
                                        Author(creator["firstName"], creator["lastName"])
                                    )
                                case _:
                                    LOGGER.warning(
                                        "Could not process the following creators types for Zotero "
                                        f"entry '{key}'\n{unprocessed_creators}"
                                    )
                        for creator_type, creator_value in creators.items():
                            entry_data[creator_type] = creator_value
                    case "date":
                        entry_data["date"] = value
                        # try to extract year from date
                        year = re.search(r"\d\d\d\d", value)
                        if year is not None:
                            entry_data["year"] = int(year[0])
                        # TODO: try to also extract month from date
                    case "journalAbbreviation":
                        if not journal_abbrev_hint_given:
                            journal_abbrev_hint_given = True
                            LOGGER.log(
                                HINT,
                                (
                                    "coBib does not store journal abbreviations separately. "
                                    "Instead, consider configuring "
                                    "`cobib.config.utils.journal_abbreviations`."
                                ),
                            )
                    case "tags":
                        tags = []
                        for tag in value:
                            tags.append(tag["tag"])
                        entry_data["tags"] = tags
                    case _:
                        unprocessed_fields.add(field)
            else:
                label = evaluate_as_f_string(
                    config.database.format.label_default, {"label": key, **entry_data.copy()}
                )

                LOGGER.warning(
                    f"Could not process the following fields for Zotero entry '{label}'\n"
                    f"{unprocessed_fields}"
                )

                entry = Entry(label, entry_data)

                if not self.skip_download:
                    path = Path(config.utils.file_downloader.default_location)
                    path.mkdir(parents=True, exist_ok=True)
                    for name, metadata in result["links"].items():
                        if name == "attachment":
                            item_id = metadata["href"].split("/")[-1]
                            filename = zotero.item(item_id)["data"]["filename"]
                            zotero.dump(item_id, filename=filename, path=path)
                            file = path / filename
                            entry.file += [file]
                            LOGGER.log(
                                HINT, f"Successfully downloaded {label}'s attachment: {file}"
                            )

                self.imported_entries.append(entry)
                continue

            LOGGER.error(f"The Zotero entry with key '{key}' could not be processed!")

        return self.imported_entries
