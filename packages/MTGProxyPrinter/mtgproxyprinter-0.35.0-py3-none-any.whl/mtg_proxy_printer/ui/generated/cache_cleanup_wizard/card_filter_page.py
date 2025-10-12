# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'card_filter_page.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QHeaderView,
    QLabel, QSizePolicy, QSplitter, QTableView,
    QVBoxLayout, QWidget, QWizardPage)

class Ui_CardFilterPage(object):
    def setupUi(self, CardFilterPage):
        if not CardFilterPage.objectName():
            CardFilterPage.setObjectName(u"CardFilterPage")
        CardFilterPage.resize(406, 568)
        self.verticalLayout_3 = QVBoxLayout(CardFilterPage)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.splitter = QSplitter(CardFilterPage)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.card_image_view_label = QLabel(self.verticalLayoutWidget)
        self.card_image_view_label.setObjectName(u"card_image_view_label")

        self.verticalLayout.addWidget(self.card_image_view_label)

        self.card_image_view = QTableView(self.verticalLayoutWidget)
        self.card_image_view.setObjectName(u"card_image_view")
        self.card_image_view.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.card_image_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.card_image_view.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.card_image_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.card_image_view.setSortingEnabled(True)
        self.card_image_view.horizontalHeader().setStretchLastSection(True)
        self.card_image_view.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.card_image_view)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.unknown_images_view_label = QLabel(self.verticalLayoutWidget_2)
        self.unknown_images_view_label.setObjectName(u"unknown_images_view_label")

        self.verticalLayout_2.addWidget(self.unknown_images_view_label)

        self.unknown_image_view = QTableView(self.verticalLayoutWidget_2)
        self.unknown_image_view.setObjectName(u"unknown_image_view")
        self.unknown_image_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.unknown_image_view.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.unknown_image_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.unknown_image_view.horizontalHeader().setStretchLastSection(True)
        self.unknown_image_view.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.unknown_image_view)

        self.splitter.addWidget(self.verticalLayoutWidget_2)

        self.verticalLayout_3.addWidget(self.splitter)

#if QT_CONFIG(shortcut)
        self.card_image_view_label.setBuddy(self.card_image_view)
        self.unknown_images_view_label.setBuddy(self.unknown_image_view)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(CardFilterPage)

        QMetaObject.connectSlotsByName(CardFilterPage)
    # setupUi

    def retranslateUi(self, CardFilterPage):
        CardFilterPage.setTitle(QCoreApplication.translate("CardFilterPage", u"Select images for removal", None))
        CardFilterPage.setSubTitle(QCoreApplication.translate("CardFilterPage", u"Click on entries in the tables below to mark or un-mark them for removal. All selected entries will be removed.", None))
        self.card_image_view_label.setText(QCoreApplication.translate("CardFilterPage", u"All images currently stored on disk:", None))
#if QT_CONFIG(tooltip)
        self.unknown_images_view_label.setToolTip(QCoreApplication.translate("CardFilterPage", u"Images found on disk that can not be associated with any card.", None))
#endif // QT_CONFIG(tooltip)
        self.unknown_images_view_label.setText(QCoreApplication.translate("CardFilterPage", u"Unknown images:", None))
    # retranslateUi

