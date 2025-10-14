"""Settings module provides the adjusted subclass of ``PySide6.QtCore.QSettings``."""

import logging
from pathlib import Path
from typing import ClassVar, Literal, overload

from excel2moodle.core.globals import Tags

logger = logging.getLogger(__name__)


class Settings:
    values: ClassVar[dict[str, str | float | Path | list]] = {}

    def __contains__(self, tag: Tags) -> bool:
        return bool(tag in type(self).values)

    @classmethod
    def clear(cls) -> None:
        cls.values.clear()

    @classmethod
    def pop(cls, key: str):
        return cls.values.pop(key)

    @overload
    @classmethod
    def get(
        cls,
        key: Literal[Tags.POINTS],
    ) -> float: ...
    @overload
    @classmethod
    def get(
        cls,
        key: Literal[
            Tags.QUESTIONVARIANT,
            Tags.TOLERANCE,
            Tags.PICTUREWIDTH,
            Tags.ANSPICWIDTH,
            Tags.WRONGSIGNPERCENT,
        ],
    ) -> int: ...
    @overload
    @classmethod
    def get(cls, key: Literal[Tags.INCLUDEINCATS, Tags.GENEXPORTREPORT]) -> bool: ...
    @overload
    @classmethod
    def get(
        cls,
        key: Literal[
            Tags.PICTURESUBFOLDER,
            Tags.LOGLEVEL,
            Tags.LOGFILE,
            Tags.CATEGORIESSHEET,
            Tags.IMPORTMODULE,
            Tags.WRONGSIGNFB,
        ],
    ) -> str: ...
    @overload
    @classmethod
    def get(
        cls,
        key: Literal[Tags.PICTUREFOLDER, Tags.SPREADSHEETPATH],
    ) -> Path: ...

    @classmethod
    def get(cls, key: Tags):
        """Get the typesafe settings value.

        If no setting is made, the default value is returned.
        """
        try:
            raw = cls.values[key]
        except KeyError:
            default = key.default
            if default is None:
                return None
            logger.debug("Returning the default value for %s", key)
            return default
        if key.typ() is Path:
            path: Path = Path(raw)
            try:
                path.resolve(strict=True)
            except ValueError:
                logger.warning(
                    f"The settingsvalue {key} couldn't be fetched with correct typ",
                )
                return key.default
            logger.debug("Returning path setting: %s = %s", key, path)
            return path
        try:
            return key.typ()(raw)
        except (ValueError, TypeError):
            logger.warning(
                f"The settingsvalue {key} couldn't be fetched with correct typ",
            )
            return key.default

    @classmethod
    def set(
        cls,
        key: Tags | str,
        value: float | bool | Path | str,
    ) -> None:
        """Set the setting to value."""
        if key in Tags:
            tag = Tags(key) if not isinstance(key, Tags) else key
            try:
                cls.values[tag] = tag.typ()(value)
            except TypeError:
                logger.exception(
                    "trying to save %s = %s %s with wrong type not possible.",
                    tag,
                    value,
                    type(value),
                )
                return
            logger.info("Saved  %s = %s: %s", key, value, tag.typ().__name__)
        else:
            logger.warning("got invalid local Setting %s = %s", key, value)
