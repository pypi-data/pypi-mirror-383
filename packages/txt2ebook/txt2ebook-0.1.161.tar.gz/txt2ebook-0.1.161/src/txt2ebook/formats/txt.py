# Copyright (c) 2021,2022,2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Convert and backup source text file into text as well."""

import logging
import shutil
from datetime import datetime as dt
from pathlib import Path

from txt2ebook.formats.base import BaseWriter
from txt2ebook.helpers import lower_underscore
from txt2ebook.models import Chapter, Volume

logger = logging.getLogger(__name__)


class TxtWriter(BaseWriter):
    """Module for writing ebook in txt format."""

    def write(self) -> None:
        """Optionally backup and overwrite the txt file.

        If the input content came from stdin, we'll skip backup and overwrite
        source text file.
        """
        if self.config.input_file.name == "<stdin>":
            logger.info("Skip backup source text file as content from stdin")
        elif self.config.split_volume_and_chapter:
            self._export_multiple_files()
        else:
            output_filename = self._output_filename(".txt")
            output_filename.parent.mkdir(parents=True, exist_ok=True)

            if self.config.overwrite and output_filename == Path(
                self.config.input_file.name
            ):
                ymd_hms = dt.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = Path(
                    Path(self.config.input_file.name)
                    .resolve()
                    .parent.joinpath(
                        lower_underscore(
                            Path(self.config.input_file.name).stem
                            + "_"
                            + ymd_hms
                            + ".txt"
                        )
                    )
                )
                logger.info(
                    "Backup source text file: %s", backup_filename.resolve()
                )
                shutil.copyfile(output_filename, backup_filename)

            with open(output_filename, "w", encoding="utf8") as file:
                logger.info("Generate TXT file: %s", output_filename.resolve())
                file.write(self._to_txt())

            if self.config.open:
                self._open_file(output_filename)

    def _get_metadata_filename_for_split(
        self, txt_filename: Path, extension: str
    ) -> Path:
        return Path(
            txt_filename.resolve().parent.joinpath(
                self.config.output_folder,
                f"00_{txt_filename.stem}_" + self._("metadata") + extension,
            )
        )

    def _get_toc_filename_for_split(
        self, txt_filename: Path, extension: str
    ) -> Path:
        return Path(
            txt_filename.resolve().parent.joinpath(
                self.config.output_folder,
                f"01_{txt_filename.stem}_" + self._("toc") + extension,
            )
        )

    def _get_volume_chapter_filename_for_split(
        self,
        txt_filename: Path,
        section_seq: str,
        chapter_seq: str,
        volume: Volume,
        chapter: Chapter,
        extension: str,
    ) -> Path:
        return Path(
            txt_filename.resolve().parent.joinpath(
                self.config.output_folder,
                (
                    f"{section_seq}"
                    f"_{chapter_seq}"
                    f"_{txt_filename.stem}"
                    f"_{volume.title}"
                    f"_{chapter.title}"
                    f"{extension}"
                ),
            )
        )

    def _get_chapter_filename_for_split(
        self,
        txt_filename: Path,
        section_seq: str,
        chapter: Chapter,
        extension: str,
    ) -> Path:
        return Path(
            txt_filename.resolve().parent.joinpath(
                self.config.output_folder,
                (
                    f"{section_seq}_{txt_filename.stem}_{chapter.title}{extension}"
                ),
            )
        )

    def _export_multiple_files(self) -> None:
        """Export multiple files based on volume and chapter."""
        txt_filename = Path(self.config.input_file.name)
        txt_filename.parent.joinpath(self.config.output_folder).mkdir(
            parents=True, exist_ok=True
        )

        # 1. Write metadata file
        metadata_filename = self._get_metadata_filename_for_split(
            txt_filename, ".txt"
        )
        with open(metadata_filename, "w", encoding="utf8") as file:
            logger.info("Creating %s", metadata_filename.resolve())
            file.write(self._to_metadata_txt())

        # 2. Write volume/chapter files
        section_seq = 0
        chapter_seq = 0
        for section in self.book.toc:
            if isinstance(section, Volume):
                section_seq += 1
                chapter_seq = 0
                for chapter in section.chapters:
                    chapter_seq += 1
                    output_filename = (
                        self._get_volume_chapter_filename_for_split(
                            txt_filename,
                            str(section_seq).rjust(2, "0"),
                            str(chapter_seq).rjust(2, "0"),
                            section,
                            chapter,
                            ".txt",
                        )
                    )
                    with open(output_filename, "w", encoding="utf8") as file:
                        logger.info("Creating %s", output_filename.resolve())
                        file.write(
                            self._to_volume_chapter_txt(section, chapter)
                        )
            elif isinstance(section, Chapter):
                section_seq += 1
                output_filename = self._get_chapter_filename_for_split(
                    txt_filename,
                    str(section_seq).rjust(2, "0"),
                    section,
                    ".txt",
                )
                with open(output_filename, "w", encoding="utf8") as file:
                    logger.info("Creating %s", output_filename.resolve())
                    file.write(self._to_chapter_txt(section))

        if self.config.open:
            self._open_file(metadata_filename)

    def _to_txt(self) -> str:
        toc = self._to_toc("-") if self.config.with_toc else ""
        return self._to_metadata_txt() + toc + self._to_body_txt()
        content = []
        for section in self.book.toc:
            if isinstance(section, Volume):
                content.append(self._to_volume_txt(section))
            if isinstance(section, Chapter):
                content.append(self._to_chapter_txt(section))

        return f"{self.config.paragraph_separator}".join(content)

    def _to_volume_txt(self, volume) -> str:
        return (
            volume.title
            + self.config.paragraph_separator
            + self.config.paragraph_separator.join(
                [self._to_chapter_txt(chapter) for chapter in volume.chapters]
            )
        )

    def _to_chapter_txt(self, chapter) -> str:
        return (
            chapter.title
            + self.config.paragraph_separator
            + self.config.paragraph_separator.join(chapter.paragraphs)
        )

    def _to_volume_chapter_txt(self, volume, chapter) -> str:
        return (
            volume.title
            + " "
            + chapter.title
            + self.config.paragraph_separator
            + self.config.paragraph_separator.join(chapter.paragraphs)
        )
