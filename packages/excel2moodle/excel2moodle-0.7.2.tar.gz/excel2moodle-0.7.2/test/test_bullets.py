from pathlib import Path

import pytest

from excel2moodle.core.bullets import BulletList
from excel2moodle.core.dataStructure import QuestionDB
from excel2moodle.core.settings import Settings, Tags

settings = Settings()

katName = "NFM2"
database = QuestionDB(settings)

settings.set(Tags.QUESTIONVARIANT, 1)
database.spreadsheet = Path("test/TestQuestion.ods")
excelFile = settings.get(Tags.SPREADSHEETPATH)
database.readCategoriesMetadata(excelFile)
database.initAllCategories(excelFile)
category = database.categories[katName]


@pytest.mark.parametrize(("qnum", "bnames"), [(1, ["a", "b", "x", "F", "p"])])
def test_bulletVarnames(qnum: int, bnames: list[str]) -> None:
    question = database.setupAndParseQuestion(category, qnum)
    assert question.bulletList.varNames == bnames


@pytest.mark.parametrize(
    ("variant", "bulletName", "bulletStr"),
    [
        (1, "F", r"Kraft \(F = 25,\!0 \mathrm{ kN }\)"),
        (2, "F", r"Kraft \(F = 22,\!0 \mathrm{ kN }\)"),
        (3, "F", r"Kraft \(F = 16,\!0 \mathrm{ kN }\)"),
        (1, "p", r"Streckenlast \(p = 19,\!0 \mathrm{ kN/m }\)"),
        (2, "p", r"Streckenlast \(p = 15,\!0 \mathrm{ kN/m }\)"),
        (3, "p", r"Streckenlast \(p = 13,\!0 \mathrm{ kN/m }\)"),
        (1, "x", r"Strecke \(x = 3,\!0 \mathrm{ m }\)"),
        (2, "x", r"Strecke \(x = 2,\!0 \mathrm{ m }\)"),
        (3, "x", r"Strecke \(x = 1,\!5 \mathrm{ m }\)"),
    ],
)
def test_bulletVariants(variant, bulletName, bulletStr) -> None:
    question = database.setupAndParseQuestion(category, 1)
    question.getUpdatedElement(variant=variant)
    for bullet in question.bulletList.bullets[bulletName].element:
        assert bullet == bulletStr


@pytest.mark.parametrize(
    ("bulletString", "name", "var", "value", "unit"),
    [
        (r"Große Kraft F = 25,0 kN", "Große Kraft", "F", 25.0, "kN"),
        (r"Lange Kraft F_l = 22,0 kN", "Lange Kraft", "F_l", 22.0, "kN"),
        (r"Streckenlast p = 15,0 kN/m", "Streckenlast", "p", 15, "kN/m"),
        (r"Längste Strecke l_{max} = 15.0 km", "Längste Strecke", "l_{max}", 15, "km"),
        (r"Strng Var q_{st} = 33,339 kN/m²", "Strng Var", "q_{st}", 33.339, "kN/m²"),
        (r"Max Sp \sigma_{max} = 33 kN/m^2", "Max Sp", r"\sigma_{max}", 33, "kN/m^2"),
    ],
)
def test_paresBPointNames(bulletString, name, var, value, unit) -> None:
    bList: BulletList = BulletList([bulletString], "0000")
    assert bList.bullets.get(1).name == name
    assert bList.bullets.get(1).value == value
    assert bList.bullets.get(1).var == var
    assert bList.bullets.get(1).unit == unit
