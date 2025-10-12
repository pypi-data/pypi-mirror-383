# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'page_config_preview_area.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QRadioButton, QSizePolicy,
    QSpinBox, QWidget)

from mtg_proxy_printer.ui.page_renderer import PageRenderer

class Ui_PageConfigPreviewArea(object):
    def setupUi(self, PageConfigPreviewArea):
        if not PageConfigPreviewArea.objectName():
            PageConfigPreviewArea.setObjectName(u"PageConfigPreviewArea")
        PageConfigPreviewArea.resize(377, 241)
        self.grid_layout = QGridLayout(PageConfigPreviewArea)
        self.grid_layout.setObjectName(u"grid_layout")
        self.grid_layout.setContentsMargins(6, 0, 0, 0)
        self.oversized_card_count = QSpinBox(PageConfigPreviewArea)
        self.oversized_card_count.setObjectName(u"oversized_card_count")

        self.grid_layout.addWidget(self.oversized_card_count, 0, 3, 1, 1)

        self.regular_card_count = QSpinBox(PageConfigPreviewArea)
        self.regular_card_count.setObjectName(u"regular_card_count")

        self.grid_layout.addWidget(self.regular_card_count, 0, 1, 1, 1)

        self.regular_size_selected = QRadioButton(PageConfigPreviewArea)
        self.regular_size_selected.setObjectName(u"regular_size_selected")
        self.regular_size_selected.setChecked(True)

        self.grid_layout.addWidget(self.regular_size_selected, 0, 0, 1, 1)

        self.oversized_selected = QRadioButton(PageConfigPreviewArea)
        self.oversized_selected.setObjectName(u"oversized_selected")

        self.grid_layout.addWidget(self.oversized_selected, 0, 2, 1, 1)

        self.preview_area = PageRenderer(PageConfigPreviewArea)
        self.preview_area.setObjectName(u"preview_area")

        self.grid_layout.addWidget(self.preview_area, 1, 0, 1, 4)


        self.retranslateUi(PageConfigPreviewArea)

        QMetaObject.connectSlotsByName(PageConfigPreviewArea)
    # setupUi

    def retranslateUi(self, PageConfigPreviewArea):
        self.oversized_card_count.setSuffix(QCoreApplication.translate("PageConfigPreviewArea", u" cards", None))
        self.regular_card_count.setSuffix(QCoreApplication.translate("PageConfigPreviewArea", u" cards", None))
        self.regular_size_selected.setText(QCoreApplication.translate("PageConfigPreviewArea", u"Regular", None))
        self.oversized_selected.setText(QCoreApplication.translate("PageConfigPreviewArea", u"Oversized", None))
        pass
    # retranslateUi

