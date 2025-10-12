# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'set_editor_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QWidget)

class Ui_SetEditor(object):
    def setupUi(self, SetEditor):
        if not SetEditor.objectName():
            SetEditor.setObjectName(u"SetEditor")
        SetEditor.resize(280, 38)
        self.horizontal_layout = QHBoxLayout(SetEditor)
        self.horizontal_layout.setSpacing(0)
        self.horizontal_layout.setObjectName(u"horizontal_layout")
        self.horizontal_layout.setContentsMargins(0, 0, 0, -1)
        self.name_editor = QLineEdit(SetEditor)
        self.name_editor.setObjectName(u"name_editor")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(15)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name_editor.sizePolicy().hasHeightForWidth())
        self.name_editor.setSizePolicy(sizePolicy)

        self.horizontal_layout.addWidget(self.name_editor)

        self.opening_parenthesis = QLabel(SetEditor)
        self.opening_parenthesis.setObjectName(u"opening_parenthesis")
        self.opening_parenthesis.setText(u"(")

        self.horizontal_layout.addWidget(self.opening_parenthesis)

        self.code_edit = QLineEdit(SetEditor)
        self.code_edit.setObjectName(u"code_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(7)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.code_edit.sizePolicy().hasHeightForWidth())
        self.code_edit.setSizePolicy(sizePolicy1)
        self.code_edit.setInputMethodHints(Qt.InputMethodHint.ImhUppercaseOnly)
        self.code_edit.setMaxLength(6)

        self.horizontal_layout.addWidget(self.code_edit)

        self.closing_parenthesis = QLabel(SetEditor)
        self.closing_parenthesis.setObjectName(u"closing_parenthesis")
        self.closing_parenthesis.setText(u")")

        self.horizontal_layout.addWidget(self.closing_parenthesis)

        QWidget.setTabOrder(self.name_editor, self.code_edit)

        self.retranslateUi(SetEditor)

        QMetaObject.connectSlotsByName(SetEditor)
    # setupUi

    def retranslateUi(self, SetEditor):
        self.name_editor.setPlaceholderText(QCoreApplication.translate("SetEditor", u"Set name", None))
        self.code_edit.setPlaceholderText(QCoreApplication.translate("SetEditor", u"CODE", None))
        pass
    # retranslateUi

