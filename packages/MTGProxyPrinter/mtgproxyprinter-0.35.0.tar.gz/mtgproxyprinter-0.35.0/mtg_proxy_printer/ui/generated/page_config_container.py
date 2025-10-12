# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'page_config_container.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QSplitter, QVBoxLayout,
    QWidget)

from mtg_proxy_printer.ui.page_config_preview_area import PageConfigPreviewArea
from mtg_proxy_printer.ui.page_config_widget import PageConfigWidget

class Ui_PageConfigContainer(object):
    def setupUi(self, PageConfigContainer):
        if not PageConfigContainer.objectName():
            PageConfigContainer.setObjectName(u"PageConfigContainer")
        self.verticalLayout = QVBoxLayout(PageConfigContainer)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(PageConfigContainer)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.page_config_widget = PageConfigWidget(self.splitter)
        self.page_config_widget.setObjectName(u"page_config_widget")
        self.splitter.addWidget(self.page_config_widget)
        self.page_config_preview_area = PageConfigPreviewArea(self.splitter)
        self.page_config_preview_area.setObjectName(u"page_config_preview_area")
        self.splitter.addWidget(self.page_config_preview_area)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(PageConfigContainer)

        QMetaObject.connectSlotsByName(PageConfigContainer)
    # setupUi

    def retranslateUi(self, PageConfigContainer):
        pass
    # retranslateUi

