# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'decklist_import_settings_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_DecklistImportSettingsPage(object):
    def setupUi(self, DecklistImportSettingsPage):
        if not DecklistImportSettingsPage.objectName():
            DecklistImportSettingsPage.setObjectName(u"DecklistImportSettingsPage")
        DecklistImportSettingsPage.resize(439, 326)
        self.gridLayout = QGridLayout(DecklistImportSettingsPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.deck_list_search_path_browse_button = QPushButton(DecklistImportSettingsPage)
        self.deck_list_search_path_browse_button.setObjectName(u"deck_list_search_path_browse_button")
        icon = QIcon(QIcon.fromTheme(u"document-open"))
        self.deck_list_search_path_browse_button.setIcon(icon)

        self.gridLayout.addWidget(self.deck_list_search_path_browse_button, 1, 2, 1, 1)

        self.deck_list_search_path_label = QLabel(DecklistImportSettingsPage)
        self.deck_list_search_path_label.setObjectName(u"deck_list_search_path_label")

        self.gridLayout.addWidget(self.deck_list_search_path_label, 1, 0, 1, 1)

        self.basic_land_removal_group_box = QGroupBox(DecklistImportSettingsPage)
        self.basic_land_removal_group_box.setObjectName(u"basic_land_removal_group_box")
        self.verticalLayout = QVBoxLayout(self.basic_land_removal_group_box)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.automatic_basics_removal_enable = QCheckBox(self.basic_land_removal_group_box)
        self.automatic_basics_removal_enable.setObjectName(u"automatic_basics_removal_enable")

        self.verticalLayout.addWidget(self.automatic_basics_removal_enable)

        self.remove_basic_wastes_enable = QCheckBox(self.basic_land_removal_group_box)
        self.remove_basic_wastes_enable.setObjectName(u"remove_basic_wastes_enable")

        self.verticalLayout.addWidget(self.remove_basic_wastes_enable)

        self.remove_snow_basics_enable = QCheckBox(self.basic_land_removal_group_box)
        self.remove_snow_basics_enable.setObjectName(u"remove_snow_basics_enable")

        self.verticalLayout.addWidget(self.remove_snow_basics_enable)


        self.gridLayout.addWidget(self.basic_land_removal_group_box, 3, 0, 1, 3)

        self.label = QLabel(DecklistImportSettingsPage)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)

        self.print_guessing_group_box = QGroupBox(DecklistImportSettingsPage)
        self.print_guessing_group_box.setObjectName(u"print_guessing_group_box")
        self.print_guessing_group_box.setChecked(False)
        self.gridLayout_6 = QGridLayout(self.print_guessing_group_box)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.print_guessing_prefer_already_downloaded = QCheckBox(self.print_guessing_group_box)
        self.print_guessing_prefer_already_downloaded.setObjectName(u"print_guessing_prefer_already_downloaded")

        self.gridLayout_6.addWidget(self.print_guessing_prefer_already_downloaded, 2, 0, 1, 1)

        self.automatic_deck_list_translation_enable = QCheckBox(self.print_guessing_group_box)
        self.automatic_deck_list_translation_enable.setObjectName(u"automatic_deck_list_translation_enable")

        self.gridLayout_6.addWidget(self.automatic_deck_list_translation_enable, 3, 0, 1, 1)

        self.print_guessing_enable = QCheckBox(self.print_guessing_group_box)
        self.print_guessing_enable.setObjectName(u"print_guessing_enable")

        self.gridLayout_6.addWidget(self.print_guessing_enable, 1, 0, 1, 1)


        self.gridLayout.addWidget(self.print_guessing_group_box, 2, 0, 1, 3)

        self.deck_list_search_path = QLineEdit(DecklistImportSettingsPage)
        self.deck_list_search_path.setObjectName(u"deck_list_search_path")
        self.deck_list_search_path.setInputMethodHints(Qt.InputMethodHint.ImhNoAutoUppercase)
        self.deck_list_search_path.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.deck_list_search_path, 1, 1, 1, 1)

        self.spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.spacer, 4, 0, 1, 3)


        self.retranslateUi(DecklistImportSettingsPage)

        QMetaObject.connectSlotsByName(DecklistImportSettingsPage)
    # setupUi

    def retranslateUi(self, DecklistImportSettingsPage):
#if QT_CONFIG(tooltip)
        self.deck_list_search_path_browse_button.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"Browse \u2026", None))
#endif // QT_CONFIG(tooltip)
        self.deck_list_search_path_browse_button.setText("")
        self.deck_list_search_path_label.setText(QCoreApplication.translate("DecklistImportSettingsPage", u"Deck list search path", None))
#if QT_CONFIG(tooltip)
        self.basic_land_removal_group_box.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"The import wizard can remove basic lands fully- or semi-automatic.\n"
"These settings control the removal behavior.", None))
#endif // QT_CONFIG(tooltip)
        self.basic_land_removal_group_box.setTitle(QCoreApplication.translate("DecklistImportSettingsPage", u"Control the one-click or automatic basic land removal", None))
#if QT_CONFIG(tooltip)
        self.automatic_basics_removal_enable.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"If enabled, basic lands are automatically removed from deck lists.\n"
"If disabled, the deck import wizard keeps them by default,\n"
"but offers the removal via a single button click.", None))
#endif // QT_CONFIG(tooltip)
        self.automatic_basics_removal_enable.setText(QCoreApplication.translate("DecklistImportSettingsPage", u"Fully automatically remove basic lands", None))
#if QT_CONFIG(tooltip)
        self.remove_basic_wastes_enable.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"When enabled, treat Wastes like any other basic land", None))
#endif // QT_CONFIG(tooltip)
        self.remove_basic_wastes_enable.setText(QCoreApplication.translate("DecklistImportSettingsPage", u"Removal includes Wastes", None))
#if QT_CONFIG(tooltip)
        self.remove_snow_basics_enable.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"When enabled, treat Snow-Covered basic lands like any other basic land", None))
#endif // QT_CONFIG(tooltip)
        self.remove_snow_basics_enable.setText(QCoreApplication.translate("DecklistImportSettingsPage", u"Removal includes Snow-Covered Basic lands", None))
        self.label.setText(QCoreApplication.translate("DecklistImportSettingsPage", u"These options control the deck list import function.", None))
#if QT_CONFIG(tooltip)
        self.print_guessing_group_box.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"Not all deck list formats always contain complete data.\n"
"These options set the default behavior when encountering ambiguous card", None))
#endif // QT_CONFIG(tooltip)
        self.print_guessing_group_box.setTitle(QCoreApplication.translate("DecklistImportSettingsPage", u"Control print selection in ambiguous cases", None))
#if QT_CONFIG(tooltip)
        self.print_guessing_prefer_already_downloaded.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"When automatically selecting a printing, prefer printings with already downloaded images over other possible printings.", None))
#endif // QT_CONFIG(tooltip)
        self.print_guessing_prefer_already_downloaded.setText(QCoreApplication.translate("DecklistImportSettingsPage", u"Prefer printings with already downloaded images", None))
#if QT_CONFIG(tooltip)
        self.automatic_deck_list_translation_enable.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"Always enable automatic deck list translation when importing deck lists.\n"
"This avoids adding foreign language cards, if the deck list happens to contain some.", None))
#endif // QT_CONFIG(tooltip)
        self.automatic_deck_list_translation_enable.setText(QCoreApplication.translate("DecklistImportSettingsPage", u"Enable translating imported deck lists by default", None))
#if QT_CONFIG(tooltip)
        self.print_guessing_enable.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"Not all deck list formats always contain complete data to identify exact printings.\n"
"If enabled, choose an arbitrary printing, instead of failing to identify such cards.\n"
"With some deck list formats, this option is always enabled.", None))
#endif // QT_CONFIG(tooltip)
        self.print_guessing_enable.setText(QCoreApplication.translate("DecklistImportSettingsPage", u"Automatically select a printing", None))
#if QT_CONFIG(tooltip)
        self.deck_list_search_path.setToolTip(QCoreApplication.translate("DecklistImportSettingsPage", u"If set, use this as the default location for loading deck lists. Your webbrowser\u2019s download directory is a good choice.", None))
#endif // QT_CONFIG(tooltip)
        self.deck_list_search_path.setPlaceholderText(QCoreApplication.translate("DecklistImportSettingsPage", u"Path to a directory", None))
        pass
    # retranslateUi

