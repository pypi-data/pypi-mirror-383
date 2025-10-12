# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'general_settings_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_GeneralSettingsPage(object):
    def setupUi(self, GeneralSettingsPage):
        if not GeneralSettingsPage.objectName():
            GeneralSettingsPage.setObjectName(u"GeneralSettingsPage")
        GeneralSettingsPage.resize(449, 604)
        self.gridLayout = QGridLayout(GeneralSettingsPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.look_and_feel_settings_group_box = QGroupBox(GeneralSettingsPage)
        self.look_and_feel_settings_group_box.setObjectName(u"look_and_feel_settings_group_box")
        self.gridLayout_2 = QGridLayout(self.look_and_feel_settings_group_box)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.application_language_label = QLabel(self.look_and_feel_settings_group_box)
        self.application_language_label.setObjectName(u"application_language_label")

        self.gridLayout_2.addWidget(self.application_language_label, 0, 0, 1, 1)

        self.add_card_widget_style_label = QLabel(self.look_and_feel_settings_group_box)
        self.add_card_widget_style_label.setObjectName(u"add_card_widget_style_label")

        self.gridLayout_2.addWidget(self.add_card_widget_style_label, 1, 0, 1, 1)

        self.gui_open_maximized = QCheckBox(self.look_and_feel_settings_group_box)
        self.gui_open_maximized.setObjectName(u"gui_open_maximized")

        self.gridLayout_2.addWidget(self.gui_open_maximized, 2, 0, 1, 2)

        self.add_card_widget_style_combo_box = QComboBox(self.look_and_feel_settings_group_box)
        self.add_card_widget_style_combo_box.setObjectName(u"add_card_widget_style_combo_box")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_card_widget_style_combo_box.sizePolicy().hasHeightForWidth())
        self.add_card_widget_style_combo_box.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.add_card_widget_style_combo_box, 1, 1, 1, 1)

        self.application_language_combo_box = QComboBox(self.look_and_feel_settings_group_box)
        self.application_language_combo_box.setObjectName(u"application_language_combo_box")

        self.gridLayout_2.addWidget(self.application_language_combo_box, 0, 1, 1, 1)

        self.wizards_open_maximized = QCheckBox(self.look_and_feel_settings_group_box)
        self.wizards_open_maximized.setObjectName(u"wizards_open_maximized")

        self.gridLayout_2.addWidget(self.wizards_open_maximized, 3, 0, 1, 2)


        self.gridLayout.addWidget(self.look_and_feel_settings_group_box, 1, 0, 1, 2)

        self.double_faced_cards_group_box = QGroupBox(GeneralSettingsPage)
        self.double_faced_cards_group_box.setObjectName(u"double_faced_cards_group_box")
        self.verticalLayout_5 = QVBoxLayout(self.double_faced_cards_group_box)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.automatically_add_opposing_faces = QCheckBox(self.double_faced_cards_group_box)
        self.automatically_add_opposing_faces.setObjectName(u"automatically_add_opposing_faces")

        self.verticalLayout_5.addWidget(self.automatically_add_opposing_faces)


        self.gridLayout.addWidget(self.double_faced_cards_group_box, 3, 0, 1, 2)

        self.default_paths_group_box = QGroupBox(GeneralSettingsPage)
        self.default_paths_group_box.setObjectName(u"default_paths_group_box")
        self.gridLayout_4 = QGridLayout(self.default_paths_group_box)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.document_save_path_browse_button = QPushButton(self.default_paths_group_box)
        self.document_save_path_browse_button.setObjectName(u"document_save_path_browse_button")
        icon = QIcon(QIcon.fromTheme(u"document-open"))
        self.document_save_path_browse_button.setIcon(icon)

        self.gridLayout_4.addWidget(self.document_save_path_browse_button, 0, 2, 1, 1)

        self.document_save_path_label = QLabel(self.default_paths_group_box)
        self.document_save_path_label.setObjectName(u"document_save_path_label")

        self.gridLayout_4.addWidget(self.document_save_path_label, 0, 0, 1, 1)

        self.document_save_path = QLineEdit(self.default_paths_group_box)
        self.document_save_path.setObjectName(u"document_save_path")
        self.document_save_path.setInputMethodHints(Qt.InputMethodHint.ImhNoAutoUppercase)
        self.document_save_path.setClearButtonEnabled(True)

        self.gridLayout_4.addWidget(self.document_save_path, 0, 1, 1, 1)


        self.gridLayout.addWidget(self.default_paths_group_box, 4, 0, 1, 2)

        self.update_check_group_box = QGroupBox(GeneralSettingsPage)
        self.update_check_group_box.setObjectName(u"update_check_group_box")
        self.verticalLayout_9 = QVBoxLayout(self.update_check_group_box)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.update_check_label = QLabel(self.update_check_group_box)
        self.update_check_label.setObjectName(u"update_check_label")

        self.verticalLayout_9.addWidget(self.update_check_label)

        self.check_application_updates_enabled = QCheckBox(self.update_check_group_box)
        self.check_application_updates_enabled.setObjectName(u"check_application_updates_enabled")
        self.check_application_updates_enabled.setTristate(True)

        self.verticalLayout_9.addWidget(self.check_application_updates_enabled)

        self.check_card_data_updates_enabled = QCheckBox(self.update_check_group_box)
        self.check_card_data_updates_enabled.setObjectName(u"check_card_data_updates_enabled")
        self.check_card_data_updates_enabled.setTristate(True)

        self.verticalLayout_9.addWidget(self.check_card_data_updates_enabled)


        self.gridLayout.addWidget(self.update_check_group_box, 5, 0, 1, 2)

        self.preferred_language_combo_box = QComboBox(GeneralSettingsPage)
        self.preferred_language_combo_box.setObjectName(u"preferred_language_combo_box")
        sizePolicy.setHeightForWidth(self.preferred_language_combo_box.sizePolicy().hasHeightForWidth())
        self.preferred_language_combo_box.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.preferred_language_combo_box, 0, 1, 1, 1)

        self.bottom_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.bottom_spacer, 6, 0, 1, 2)

        self.preferred_language_label = QLabel(GeneralSettingsPage)
        self.preferred_language_label.setObjectName(u"preferred_language_label")

        self.gridLayout.addWidget(self.preferred_language_label, 0, 0, 1, 1)

        self.custom_cards_group_box = QGroupBox(GeneralSettingsPage)
        self.custom_cards_group_box.setObjectName(u"custom_cards_group_box")
        self.gridLayout_3 = QGridLayout(self.custom_cards_group_box)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.custom_cards_search_path_label = QLabel(self.custom_cards_group_box)
        self.custom_cards_search_path_label.setObjectName(u"custom_cards_search_path_label")

        self.gridLayout_3.addWidget(self.custom_cards_search_path_label, 0, 0, 1, 1)

        self.custom_cards_search_path = QLineEdit(self.custom_cards_group_box)
        self.custom_cards_search_path.setObjectName(u"custom_cards_search_path")
        self.custom_cards_search_path.setInputMethodHints(Qt.InputMethodHint.ImhNoAutoUppercase)
        self.custom_cards_search_path.setClearButtonEnabled(True)

        self.gridLayout_3.addWidget(self.custom_cards_search_path, 0, 3, 1, 1)

        self.custom_cards_search_path_browse_button = QPushButton(self.custom_cards_group_box)
        self.custom_cards_search_path_browse_button.setObjectName(u"custom_cards_search_path_browse_button")
        self.custom_cards_search_path_browse_button.setIcon(icon)

        self.gridLayout_3.addWidget(self.custom_cards_search_path_browse_button, 0, 4, 1, 1)

        self.custom_cards_force_round_corners = QCheckBox(self.custom_cards_group_box)
        self.custom_cards_force_round_corners.setObjectName(u"custom_cards_force_round_corners")

        self.gridLayout_3.addWidget(self.custom_cards_force_round_corners, 1, 0, 1, 5)


        self.gridLayout.addWidget(self.custom_cards_group_box, 2, 0, 1, 2)

#if QT_CONFIG(shortcut)
        self.add_card_widget_style_label.setBuddy(self.add_card_widget_style_combo_box)
        self.document_save_path_label.setBuddy(self.document_save_path)
        self.preferred_language_label.setBuddy(self.preferred_language_combo_box)
        self.custom_cards_search_path_label.setBuddy(self.custom_cards_search_path)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.preferred_language_combo_box, self.application_language_combo_box)
        QWidget.setTabOrder(self.application_language_combo_box, self.add_card_widget_style_combo_box)
        QWidget.setTabOrder(self.add_card_widget_style_combo_box, self.gui_open_maximized)
        QWidget.setTabOrder(self.gui_open_maximized, self.wizards_open_maximized)
        QWidget.setTabOrder(self.wizards_open_maximized, self.custom_cards_search_path)
        QWidget.setTabOrder(self.custom_cards_search_path, self.custom_cards_search_path_browse_button)
        QWidget.setTabOrder(self.custom_cards_search_path_browse_button, self.custom_cards_force_round_corners)
        QWidget.setTabOrder(self.custom_cards_force_round_corners, self.automatically_add_opposing_faces)
        QWidget.setTabOrder(self.automatically_add_opposing_faces, self.document_save_path)
        QWidget.setTabOrder(self.document_save_path, self.document_save_path_browse_button)
        QWidget.setTabOrder(self.document_save_path_browse_button, self.check_application_updates_enabled)
        QWidget.setTabOrder(self.check_application_updates_enabled, self.check_card_data_updates_enabled)

        self.retranslateUi(GeneralSettingsPage)

        QMetaObject.connectSlotsByName(GeneralSettingsPage)
    # setupUi

    def retranslateUi(self, GeneralSettingsPage):
        self.look_and_feel_settings_group_box.setTitle(QCoreApplication.translate("GeneralSettingsPage", u"Look && Feel (Changing most of these require an application restart)", None))
        self.application_language_label.setText(QCoreApplication.translate("GeneralSettingsPage", u"Application language", None))
        self.add_card_widget_style_label.setText(QCoreApplication.translate("GeneralSettingsPage", u"Main window layout", None))
        self.gui_open_maximized.setText(QCoreApplication.translate("GeneralSettingsPage", u"Open the main window maximized", None))
#if QT_CONFIG(tooltip)
        self.add_card_widget_style_combo_box.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.\n"
"Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.\n"
"Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.application_language_combo_box.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.wizards_open_maximized.setText(QCoreApplication.translate("GeneralSettingsPage", u"Open all wizards and dialogs maximized", None))
        self.double_faced_cards_group_box.setTitle(QCoreApplication.translate("GeneralSettingsPage", u"Double-faced cards", None))
#if QT_CONFIG(tooltip)
        self.automatically_add_opposing_faces.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"When adding double-faced cards, automatically add the same number of copies of the other side.\n"
"Uses the appropriate, matching other card side.\n"
"Uncheck to disable this automatism.", None))
#endif // QT_CONFIG(tooltip)
        self.automatically_add_opposing_faces.setText(QCoreApplication.translate("GeneralSettingsPage", u"Automatically add the other side of double-faced cards", None))
#if QT_CONFIG(tooltip)
        self.default_paths_group_box.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"These paths are selected by default when browsing the file system for files", None))
#endif // QT_CONFIG(tooltip)
        self.default_paths_group_box.setTitle(QCoreApplication.translate("GeneralSettingsPage", u"Default save paths", None))
#if QT_CONFIG(tooltip)
        self.document_save_path_browse_button.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"Browse\u2026", None))
#endif // QT_CONFIG(tooltip)
        self.document_save_path_browse_button.setText("")
        self.document_save_path_label.setText(QCoreApplication.translate("GeneralSettingsPage", u"Document save path", None))
#if QT_CONFIG(tooltip)
        self.document_save_path.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"If set, use this as the default location for saving documents.", None))
#endif // QT_CONFIG(tooltip)
        self.document_save_path.setPlaceholderText(QCoreApplication.translate("GeneralSettingsPage", u"Path to a directory", None))
#if QT_CONFIG(tooltip)
        self.update_check_group_box.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.update_check_group_box.setTitle(QCoreApplication.translate("GeneralSettingsPage", u"Automatic update checks", None))
        self.update_check_label.setText(QCoreApplication.translate("GeneralSettingsPage", u"Update checks are performed at application start, if enabled.", None))
#if QT_CONFIG(tooltip)
        self.check_application_updates_enabled.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"If enabled, check for application updates, and notify if new updates are available for installation.", None))
#endif // QT_CONFIG(tooltip)
        self.check_application_updates_enabled.setText(QCoreApplication.translate("GeneralSettingsPage", u"Check for application updates", None))
#if QT_CONFIG(tooltip)
        self.check_card_data_updates_enabled.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.", None))
#endif // QT_CONFIG(tooltip)
        self.check_card_data_updates_enabled.setText(QCoreApplication.translate("GeneralSettingsPage", u"Check for new card data", None))
#if QT_CONFIG(tooltip)
        self.preferred_language_combo_box.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"Language choices will default to the chosen language here.\n"
"Entries use the language codes as listed on Scryfall.\n"
"\n"
"Note: Cards in deck lists use the language as given by the deck list. To overwrite, use the deck list translation option.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.preferred_language_label.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"Card language selected at application start and default language when enabling deck list translations", None))
#endif // QT_CONFIG(tooltip)
        self.preferred_language_label.setText(QCoreApplication.translate("GeneralSettingsPage", u"Preferred card language:", None))
        self.custom_cards_group_box.setTitle(QCoreApplication.translate("GeneralSettingsPage", u"Custom cards", None))
        self.custom_cards_search_path_label.setText(QCoreApplication.translate("GeneralSettingsPage", u"Default search path", None))
#if QT_CONFIG(tooltip)
        self.custom_cards_search_path.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"If set, search here for custom card images", None))
#endif // QT_CONFIG(tooltip)
        self.custom_cards_search_path.setPlaceholderText(QCoreApplication.translate("GeneralSettingsPage", u"Path to a directory", None))
#if QT_CONFIG(tooltip)
        self.custom_cards_search_path_browse_button.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"Browse\u2026", None))
#endif // QT_CONFIG(tooltip)
        self.custom_cards_search_path_browse_button.setText("")
#if QT_CONFIG(tooltip)
        self.custom_cards_force_round_corners.setToolTip(QCoreApplication.translate("GeneralSettingsPage", u"Enforce rounded corners for all imported custom cards", None))
#endif // QT_CONFIG(tooltip)
        self.custom_cards_force_round_corners.setText(QCoreApplication.translate("GeneralSettingsPage", u"Force round corners", None))
        pass
    # retranslateUi

