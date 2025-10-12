import logging
from enum import Enum, StrEnum
from pathlib import Path

import lxml.etree as ET

logger = logging.getLogger(__name__)


QUESTION_TYPES = {
    "NF": "numerical",
    "NFM": "numerical",
    "MC": "multichoice",
    "CLOZE": "cloze",
}


class Tags(StrEnum):
    """Tags and Settings Keys are needed to always acess the correct Value.

    The Tags can be used to acess the settings or the QuestionData respectively.
    As the QSettings settings are accesed via strings, which could easily gotten wrong.
    Further, this Enum defines, which type a setting has to be.
    """

    QUESTIONVARIANT = "defaultquestionvariant", int, 1, "testgen"
    INCLUDEINCATS = "includecats", bool, False, "testgen"
    GENEXPORTREPORT = "exportreport", bool, False, "testgen"
    TOLERANCE = "tolerance", float, 0.01, "parser/nf"
    PICTUREFOLDER = "pictureFolder", Path, None, "core"
    PICTURESUBFOLDER = "imgfolder", str, "Abbildungen", "project"
    SPREADSHEETPATH = "spreadsheetFolder", Path, None, "core"
    LOGLEVEL = "loglevel", str, "INFO", "core"
    LOGFILE = "logfile", str, "excel2moodleLogFile.log", "core"
    CATEGORIESSHEET = "categoriessheet", str, "Kategorien", "core"

    IMPORTMODULE = "importmodule", str, None
    TEXT = "text", list, None
    BPOINTS = "bulletpoint", list, None
    TRUE = "true", list, None
    FALSE = "false", list, None
    TYPE = "type", str, None
    NAME = "name", str, None
    RESULT = "result", float, None
    EQUATION = "formula", str, None
    PICTURE = "picture", str, None
    NUMBER = "number", int, None
    ANSTYPE = "answertype", str, None
    QUESTIONPART = "part", list, None
    PARTTYPE = "parttype", str, None
    POINTS = "points", float, 1.0
    PICTUREWIDTH = "imgwidth", int, 500
    ANSPICWIDTH = "answerimgwidth", int, 120
    FIRSTRESULT = "firstresult", float, 0
    WRONGSIGNPERCENT = "wrongsignpercent", int, 50
    WRONGSIGNFB = "wrongsignfeedback", str, "your result has the wrong sign (+-)"
    TRUEFB = "truefeedback", str, "congratulations!!! your answer is right."
    FALSEFB = "falsefeedback", str, "Your answer is sadly wrong, try again!!!"
    PCORRECFB = "partialcorrectfeedback", str, "Your answer is partially right."
    GENERALFB = "feedback", str, "You answered this question."
    TRUEANSFB = "trueanswerfeedback", list, None
    FALSEANSFB = "falseanswerfeedback", list, None

    MEDIASCRIPTS = "mediascripts", list, None
    MEDIACALL = "parametricmedia", str, None

    def __new__(
        cls,
        key: str,
        typ: type,
        default: str | float | Path | bool | None,
        place: str = "project",
    ) -> object:
        """Define new settings class."""
        obj = str.__new__(cls, key)
        obj._value_ = key
        obj._typ_ = typ
        obj._default_ = default
        obj._place_ = place
        return obj

    def __init__(
        self,
        _,
        typ: type,
        default: str | float | Path | None,
        place: str = "project",
    ) -> None:
        self._typ_: type = typ
        self._place_: str = place
        self._default_ = default
        self._full_ = f"{self._place_}/{self._value_}"

    @property
    def default(self) -> str | int | float | Path | bool | None:
        """Get default value for the key."""
        return self._default_

    @property
    def place(self) -> str:
        return self._place_

    @property
    def full(self) -> str:
        return self._full_

    def typ(self) -> type:
        """Get type of the keys data."""
        return self._typ_


class TextElements(Enum):
    PLEFT = "p", "text-align: left;"
    SPANRED = "span", "color: rgb(239, 69, 64)"
    SPANGREEN = "span", "color: rgb(152, 202, 62)"
    SPANORANGE = "span", "color: rgb(152, 100, 100)"
    ULIST = "ul", ""
    LISTITEM = "li", "text-align: left;"
    DIV = "div", ""

    def create(self, tag: str | None = None):
        if tag is None:
            tag, style = self.value
        else:
            style = self.value[1]
        return ET.Element(tag, dir="ltr", style=style)

    @property
    def style(
        self,
    ) -> str:
        return self.value[1]


class XMLTags(StrEnum):
    NAME = "name"
    QTEXT = "questiontext"
    QUESTION = "question"
    TEXT = "text"
    PICTURE = "file"
    GENFEEDB = "generalfeedback"
    CORFEEDB = "correctfeedback"
    PCORFEEDB = "partialcorrectfeedback"
    INCORFEEDB = "incorrectfeedback"
    ANSFEEDBACK = "feedback"
    POINTS = "defaultgrade"
    PENALTY = "penalty"
    HIDE = "hidden"
    ID = "idnumber"
    TYPE = "type"
    ANSWER = "answer"
    TOLERANCE = "tolerance"


feedBElements = {
    XMLTags.CORFEEDB: TextElements.SPANGREEN.create(),
    XMLTags.PCORFEEDB: TextElements.SPANORANGE.create(),
    XMLTags.INCORFEEDB: TextElements.SPANRED.create(),
    XMLTags.ANSFEEDBACK: TextElements.SPANGREEN.create(),
    XMLTags.GENFEEDB: TextElements.SPANGREEN.create(),
}
