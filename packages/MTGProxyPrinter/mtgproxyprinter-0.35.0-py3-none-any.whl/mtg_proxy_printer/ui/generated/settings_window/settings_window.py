# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_window.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QComboBox,
    QDialog, QDialogButtonBox, QGridLayout, QListView,
    QSizePolicy, QStackedWidget, QWidget)

from mtg_proxy_printer.ui.settings_window_pages import (DebugSettingsPage, DecklistImportSettingsPage, DefaultDocumentLayoutSettingsPage, ExportSettingsPage,
    GeneralSettingsPage, HidePrintingsPage, PrinterSettingsPage)

class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow):
        if not SettingsWindow.objectName():
            SettingsWindow.setObjectName(u"SettingsWindow")
        SettingsWindow.setWindowModality(Qt.WindowModality.ApplicationModal)
        SettingsWindow.resize(1000, 700)
        self.gridLayout = QGridLayout(SettingsWindow)
        self.gridLayout.setObjectName(u"gridLayout")
        self.stacked_pages = QStackedWidget(SettingsWindow)
        self.stacked_pages.setObjectName(u"stacked_pages")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(25)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stacked_pages.sizePolicy().hasHeightForWidth())
        self.stacked_pages.setSizePolicy(sizePolicy)
        self.general_settings_page = GeneralSettingsPage()
        self.general_settings_page.setObjectName(u"general_settings_page")
        self.stacked_pages.addWidget(self.general_settings_page)
        self.decklist_import_settings_page = DecklistImportSettingsPage()
        self.decklist_import_settings_page.setObjectName(u"decklist_import_settings_page")
        self.stacked_pages.addWidget(self.decklist_import_settings_page)
        self.export_settings_page = ExportSettingsPage()
        self.export_settings_page.setObjectName(u"export_settings_page")
        self.stacked_pages.addWidget(self.export_settings_page)
        self.printer_settings_page = PrinterSettingsPage()
        self.printer_settings_page.setObjectName(u"printer_settings_page")
        self.stacked_pages.addWidget(self.printer_settings_page)
        self.default_document_layout_page = DefaultDocumentLayoutSettingsPage()
        self.default_document_layout_page.setObjectName(u"default_document_layout_page")
        self.stacked_pages.addWidget(self.default_document_layout_page)
        self.hide_printings_page = HidePrintingsPage()
        self.hide_printings_page.setObjectName(u"hide_printings_page")
        self.stacked_pages.addWidget(self.hide_printings_page)
        self.debug_settings_page = DebugSettingsPage()
        self.debug_settings_page.setObjectName(u"debug_settings_page")
        self.stacked_pages.addWidget(self.debug_settings_page)

        self.gridLayout.addWidget(self.stacked_pages, 1, 1, 1, 1)

        self.page_selection_combo_box = QComboBox(SettingsWindow)
        self.page_selection_combo_box.setObjectName(u"page_selection_combo_box")

        self.gridLayout.addWidget(self.page_selection_combo_box, 0, 1, 1, 1)

        self.page_selection_list_view = QListView(SettingsWindow)
        self.page_selection_list_view.setObjectName(u"page_selection_list_view")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(10)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.page_selection_list_view.sizePolicy().hasHeightForWidth())
        self.page_selection_list_view.setSizePolicy(sizePolicy1)
        self.page_selection_list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.page_selection_list_view.setIconSize(QSize(22, 22))
        self.page_selection_list_view.setUniformItemSizes(True)

        self.gridLayout.addWidget(self.page_selection_list_view, 0, 0, 2, 1)

        self.button_box = QDialogButtonBox(SettingsWindow)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Reset|QDialogButtonBox.StandardButton.RestoreDefaults|QDialogButtonBox.StandardButton.Save)

        self.gridLayout.addWidget(self.button_box, 2, 0, 1, 2)


        self.retranslateUi(SettingsWindow)
        self.button_box.accepted.connect(SettingsWindow.accept)
        self.button_box.rejected.connect(SettingsWindow.reject)

        self.stacked_pages.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SettingsWindow)
    # setupUi

    def retranslateUi(self, SettingsWindow):
        SettingsWindow.setWindowTitle(QCoreApplication.translate("SettingsWindow", u"Settings", None))
    # retranslateUi

