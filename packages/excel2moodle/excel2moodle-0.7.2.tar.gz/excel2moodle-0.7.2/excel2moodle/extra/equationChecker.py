"""Verify the equations written into the ``result`` field of ParametricQuestion.

This module

#. It calculates all the answers obtained from the series of variables.
#. It compares the calculation of the first answer to the ``firstResult`` field.

Usage
=====

From the main UI
----------------

#. Start this tool from the top bar in the main Window under the *Tools* section
#. A new window will open with the currently selected question
#. For Cloze Questions select the correct equation on the top
#. You can edit the equation in the middle field
#. Click on ``Check the equation now!`` and inspect the results.
#. If the first calculated result matches the value in the field ``firstResult`` your equation is probably right.
#. Now click on ``Save equation`` to copy all modified equations to the clipboard.
"""

import logging
import math
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox

from excel2moodle import mainLogger
from excel2moodle.core.question import ParametricQuestion, Parametrics
from excel2moodle.extra.variableGenerator import populateDataSetTable
from excel2moodle.logger import LogWindowHandler
from excel2moodle.ui.UI_equationChecker import Ui_EquationChecker

logger = logging.getLogger(__name__)

loggerSignal = LogWindowHandler()
mainLogger.addHandler(loggerSignal)


class EqCheckerWindow(QDialog):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent=parent)
        self.mainWindow = parent
        self.excelFile = Path()
        self.ui = Ui_EquationChecker()
        self.ui.setupUi(self)
        self.ui.btnRunCheck.clicked.connect(
            lambda: self.updateCalculation(),
        )
        self.ui.answerPartNum.valueChanged.connect(lambda: self.updateEquation())
        self.ui.btnCancel.clicked.connect(self.reject)
        self.ui.btnFetchQst.clicked.connect(lambda: self.updateQuestion())
        self.ui.btnSave.clicked.connect(lambda: self.copyEquation())
        self.parametrics: Parametrics

    @Slot()
    def updateQuestion(self) -> None:
        """Get the current Question from the list and set up the checker."""
        question = self.mainWindow.currentQuestion
        if not isinstance(question, ParametricQuestion):
            mainLogger.error("Can't check a question without parametrics")
            return
        self.ui.labelQuestionNum.setText(f"Question: {question.id}")
        self.parametrics = question.parametrics
        self.ui.answerPartNum.setValue(1)
        self.ui.answerPartNum.setMaximum(len(self.parametrics.equations))
        self.updateEquation()

    @Slot()
    def updateEquation(self) -> None:
        """Update only the equation number of the same question."""
        self.ui.equationText.clear()
        eqVariant = self.ui.answerPartNum.value()
        self.ui.lineFirstResult.setText(
            str(self.parametrics.resultChecker.get(eqVariant))
        )
        if len(self.parametrics.equations) == 1:
            self.ui.answerPartNum.hide()
            self.ui.labelPartNum.hide()
        else:
            self.ui.answerPartNum.show()
            self.ui.labelPartNum.show()
        self.ui.equationText.appendPlainText(
            str(self.parametrics.equations.get(eqVariant))
        )
        self.updateCalculation()

    def updateCalculation(self) -> None:
        """Calculate the current equation written in the textedit."""
        equation = self.ui.equationText.toPlainText()
        eqNum = self.ui.answerPartNum.value()
        self.parametrics.setEquation(number=eqNum, equation=equation)
        calculatedResult = self.parametrics.getResult(number=1, equation=eqNum)
        check: bool = False
        check = bool(
            math.isclose(
                calculatedResult,
                self.parametrics.resultChecker.get(eqNum, 0),
                rel_tol=0.01,
            )
        )
        self.ui.lineCalculatedRes.setText(f"{calculatedResult}")
        if check:
            self.ui.lineCheckResult.setStyleSheet("color: rgb(24,150,0)")
            self.ui.lineCheckResult.setText(
                "[OK] Value of 'first result' matches calculated set 1"
            )
            logger.info(
                "[OK] The first calculated result matches 'firstResult'",
            )
        else:
            self.ui.lineCheckResult.setStyleSheet("color: rgb(255,0,0)")
            self.ui.lineCheckResult.setText(
                "[ERROR] Value of 'first result' doesn't match set 1"
            )
            logger.warning(
                "The first calculated result does not match 'firstResult'",
            )

        populateDataSetTable(self.ui.tableVariables, self.parametrics)

    @Slot()
    def copyEquation(self) -> None:
        clipb = QApplication.clipboard()
        equationlist: list[str] = []
        if len(self.parametrics.equations) > 1:
            for i, eq in self.parametrics.equations.items():
                equationlist.append(f"result:{i} \t{eq}")
        else:
            equationlist.append(f"result\t{self.parametrics.equations.get(1)}")
        clipb.setText("\n".join(equationlist))
        mainLogger.info("Copied equations to the clipboard")
        QMessageBox.information(
            self.mainWindow,
            "Equation Copied!",
            """All equations from the current parametric question are saved to the clipboard.\n
            You can paste them with 'crtl + v' into the spreadsheet.
            Make sure to import them with 'Tab' as the seperator.""",
        )
