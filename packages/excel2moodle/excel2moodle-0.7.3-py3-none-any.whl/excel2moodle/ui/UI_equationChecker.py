# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UI_equationChecker.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_EquationChecker(object):
    def setupUi(self, EquationChecker):
        if not EquationChecker.objectName():
            EquationChecker.setObjectName(u"EquationChecker")
        EquationChecker.setWindowModality(Qt.WindowModality.WindowModal)
        EquationChecker.resize(650, 722)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListRemove))
        EquationChecker.setWindowIcon(icon)
        EquationChecker.setAutoFillBackground(False)
        self.verticalLayout = QVBoxLayout(EquationChecker)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_4 = QLabel(EquationChecker)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 2, 1, 1)

        self.answerPartNum = QSpinBox(EquationChecker)
        self.answerPartNum.setObjectName(u"answerPartNum")
        self.answerPartNum.setMinimum(1)

        self.gridLayout.addWidget(self.answerPartNum, 1, 3, 1, 1)

        self.labelPartNum = QLabel(EquationChecker)
        self.labelPartNum.setObjectName(u"labelPartNum")

        self.gridLayout.addWidget(self.labelPartNum, 1, 2, 1, 1)

        self.lineCalculatedRes = QLineEdit(EquationChecker)
        self.lineCalculatedRes.setObjectName(u"lineCalculatedRes")
        font = QFont()
        font.setBold(True)
        self.lineCalculatedRes.setFont(font)
        self.lineCalculatedRes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineCalculatedRes.setReadOnly(True)
        self.lineCalculatedRes.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.lineCalculatedRes, 3, 3, 1, 1)

        self.lineFirstResult = QLineEdit(EquationChecker)
        self.lineFirstResult.setObjectName(u"lineFirstResult")
        self.lineFirstResult.setEnabled(True)
        self.lineFirstResult.setFont(font)
        self.lineFirstResult.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineFirstResult.setReadOnly(True)

        self.gridLayout.addWidget(self.lineFirstResult, 2, 3, 1, 1)

        self.label_3 = QLabel(EquationChecker)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 2, 1, 1)

        self.btnFetchQst = QPushButton(EquationChecker)
        self.btnFetchQst.setObjectName(u"btnFetchQst")

        self.gridLayout.addWidget(self.btnFetchQst, 0, 3, 1, 1)

        self.labelQuestionNum = QLabel(EquationChecker)
        self.labelQuestionNum.setObjectName(u"labelQuestionNum")
        self.labelQuestionNum.setFont(font)

        self.gridLayout.addWidget(self.labelQuestionNum, 0, 2, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.label_2 = QLabel(EquationChecker)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.equationText = QPlainTextEdit(EquationChecker)
        self.equationText.setObjectName(u"equationText")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.equationText.sizePolicy().hasHeightForWidth())
        self.equationText.setSizePolicy(sizePolicy)
        self.equationText.setMinimumSize(QSize(0, 20))
        self.equationText.setBaseSize(QSize(0, 20))

        self.verticalLayout.addWidget(self.equationText)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 5, -1, -1)
        self.btnRunCheck = QPushButton(EquationChecker)
        self.btnRunCheck.setObjectName(u"btnRunCheck")
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.btnRunCheck.setFont(font1)

        self.horizontalLayout.addWidget(self.btnRunCheck)

        self.lineCheckResult = QLineEdit(EquationChecker)
        self.lineCheckResult.setObjectName(u"lineCheckResult")
        font2 = QFont()
        font2.setBold(True)
        font2.setItalic(True)
        self.lineCheckResult.setFont(font2)
        self.lineCheckResult.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.lineCheckResult.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineCheckResult.setReadOnly(True)

        self.horizontalLayout.addWidget(self.lineCheckResult)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.line = QFrame(EquationChecker)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.tableVariables = QTableWidget(EquationChecker)
        self.tableVariables.setObjectName(u"tableVariables")
        sizePolicy.setHeightForWidth(self.tableVariables.sizePolicy().hasHeightForWidth())
        self.tableVariables.setSizePolicy(sizePolicy)
        self.tableVariables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout.addWidget(self.tableVariables)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.btnSave = QPushButton(EquationChecker)
        self.btnSave.setObjectName(u"btnSave")

        self.horizontalLayout_2.addWidget(self.btnSave)

        self.btnCancel = QPushButton(EquationChecker)
        self.btnCancel.setObjectName(u"btnCancel")

        self.horizontalLayout_2.addWidget(self.btnCancel)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.retranslateUi(EquationChecker)

        QMetaObject.connectSlotsByName(EquationChecker)
    # setupUi

    def retranslateUi(self, EquationChecker):
        EquationChecker.setWindowTitle(QCoreApplication.translate("EquationChecker", u"Equation Checker", None))
        self.label_4.setText(QCoreApplication.translate("EquationChecker", u"calculated first Result", None))
        self.labelPartNum.setText(QCoreApplication.translate("EquationChecker", u"Answer Part (Cloze)", None))
        self.lineCalculatedRes.setText(QCoreApplication.translate("EquationChecker", u"0.00", None))
        self.lineFirstResult.setText(QCoreApplication.translate("EquationChecker", u"0.00", None))
        self.lineFirstResult.setPlaceholderText(QCoreApplication.translate("EquationChecker", u"waiting", None))
        self.label_3.setText(QCoreApplication.translate("EquationChecker", u"firstResult from spreadsheet", None))
#if QT_CONFIG(tooltip)
        self.btnFetchQst.setToolTip(QCoreApplication.translate("EquationChecker", u"Get the last selected question from the main windows list.", None))
#endif // QT_CONFIG(tooltip)
        self.btnFetchQst.setText(QCoreApplication.translate("EquationChecker", u"Fetch current question", None))
        self.labelQuestionNum.setText(QCoreApplication.translate("EquationChecker", u"Question: ", None))
        self.label_2.setText(QCoreApplication.translate("EquationChecker", u"Edit the equation below", None))
        self.btnRunCheck.setText(QCoreApplication.translate("EquationChecker", u"Check the equation now !", None))
        self.lineCheckResult.setText("")
        self.lineCheckResult.setPlaceholderText(QCoreApplication.translate("EquationChecker", u"waiting for check", None))
        self.btnSave.setText(QCoreApplication.translate("EquationChecker", u"Save equation", None))
        self.btnCancel.setText(QCoreApplication.translate("EquationChecker", u"Close", None))
    # retranslateUi

