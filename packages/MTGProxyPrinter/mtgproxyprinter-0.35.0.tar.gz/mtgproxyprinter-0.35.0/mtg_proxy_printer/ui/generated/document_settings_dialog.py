# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'document_settings_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QSizePolicy, QVBoxLayout, QWidget)

from mtg_proxy_printer.ui.page_config_container import PageConfigContainer

class Ui_DocumentSettingsDialog(object):
    def setupUi(self, DocumentSettingsDialog):
        if not DocumentSettingsDialog.objectName():
            DocumentSettingsDialog.setObjectName(u"DocumentSettingsDialog")
        self.verticalLayout = QVBoxLayout(DocumentSettingsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.page_config_container = PageConfigContainer(DocumentSettingsDialog)
        self.page_config_container.setObjectName(u"page_config_container")

        self.verticalLayout.addWidget(self.page_config_container)

        self.button_box = QDialogButtonBox(DocumentSettingsDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Reset|QDialogButtonBox.StandardButton.RestoreDefaults|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(DocumentSettingsDialog)
        self.button_box.accepted.connect(DocumentSettingsDialog.accept)
        self.button_box.rejected.connect(DocumentSettingsDialog.reject)

        QMetaObject.connectSlotsByName(DocumentSettingsDialog)
    # setupUi

    def retranslateUi(self, DocumentSettingsDialog):
        DocumentSettingsDialog.setWindowTitle(QCoreApplication.translate("DocumentSettingsDialog", u"Configure the current document", None))
    # retranslateUi

