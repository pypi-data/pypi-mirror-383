# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'summary_page.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget, QWizardPage)

class Ui_SummaryPage(object):
    def setupUi(self, SummaryPage):
        if not SummaryPage.objectName():
            SummaryPage.setObjectName(u"SummaryPage")
        SummaryPage.resize(266, 90)
        self.verticalLayout = QVBoxLayout(SummaryPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.image_count_summary = QLabel(SummaryPage)
        self.image_count_summary.setObjectName(u"image_count_summary")

        self.verticalLayout.addWidget(self.image_count_summary)

        self.filesize_summary = QLabel(SummaryPage)
        self.filesize_summary.setObjectName(u"filesize_summary")

        self.verticalLayout.addWidget(self.filesize_summary)

        self.verticalSpacer = QSpacerItem(20, 27, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(SummaryPage)

        QMetaObject.connectSlotsByName(SummaryPage)
    # setupUi

    def retranslateUi(self, SummaryPage):
        SummaryPage.setTitle(QCoreApplication.translate("SummaryPage", u"Summary", None))
        self.image_count_summary.setText("")
        self.filesize_summary.setText("")
    # retranslateUi

