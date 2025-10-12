# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'load_list_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QLineEdit, QPlainTextEdit, QPushButton,
    QSizePolicy, QWidget, QWizardPage)

class Ui_LoadListPage(object):
    def setupUi(self, LoadListPage):
        if not LoadListPage.objectName():
            LoadListPage.setObjectName(u"LoadListPage")
        LoadListPage.setEnabled(True)
        LoadListPage.resize(712, 343)
        self.gridLayout = QGridLayout(LoadListPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.translate_deck_list_target_language = QComboBox(LoadListPage)
        self.translate_deck_list_target_language.setObjectName(u"translate_deck_list_target_language")
        self.translate_deck_list_target_language.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.translate_deck_list_target_language.sizePolicy().hasHeightForWidth())
        self.translate_deck_list_target_language.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.translate_deck_list_target_language, 6, 1, 1, 3)

        self.deck_list_download_url_line_edit = QLineEdit(LoadListPage)
        self.deck_list_download_url_line_edit.setObjectName(u"deck_list_download_url_line_edit")
        self.deck_list_download_url_line_edit.setInputMethodHints(Qt.InputMethodHint.ImhUrlCharactersOnly)

        self.gridLayout.addWidget(self.deck_list_download_url_line_edit, 0, 0, 1, 2)

        self.scryfall_search = QLineEdit(LoadListPage)
        self.scryfall_search.setObjectName(u"scryfall_search")
        self.scryfall_search.setMaxLength(900)

        self.gridLayout.addWidget(self.scryfall_search, 1, 0, 1, 2)

        self.print_guessing_enable = QCheckBox(LoadListPage)
        self.print_guessing_enable.setObjectName(u"print_guessing_enable")

        self.gridLayout.addWidget(self.print_guessing_enable, 7, 0, 1, 4)

        self.scryfall_search_download_button = QPushButton(LoadListPage)
        self.scryfall_search_download_button.setObjectName(u"scryfall_search_download_button")
        self.scryfall_search_download_button.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scryfall_search_download_button.sizePolicy().hasHeightForWidth())
        self.scryfall_search_download_button.setSizePolicy(sizePolicy1)
        icon = QIcon(QIcon.fromTheme(u"edit-download"))
        self.scryfall_search_download_button.setIcon(icon)

        self.gridLayout.addWidget(self.scryfall_search_download_button, 1, 3, 1, 1)

        self.deck_list = QPlainTextEdit(LoadListPage)
        self.deck_list.setObjectName(u"deck_list")

        self.gridLayout.addWidget(self.deck_list, 4, 0, 1, 4)

        self.print_guessing_prefer_already_downloaded = QCheckBox(LoadListPage)
        self.print_guessing_prefer_already_downloaded.setObjectName(u"print_guessing_prefer_already_downloaded")
        self.print_guessing_prefer_already_downloaded.setEnabled(True)

        self.gridLayout.addWidget(self.print_guessing_prefer_already_downloaded, 8, 0, 1, 4)

        self.translate_deck_list_enable = QCheckBox(LoadListPage)
        self.translate_deck_list_enable.setObjectName(u"translate_deck_list_enable")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.translate_deck_list_enable.sizePolicy().hasHeightForWidth())
        self.translate_deck_list_enable.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.translate_deck_list_enable, 6, 0, 1, 1)

        self.line = QFrame(LoadListPage)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 5, 0, 1, 4)

        self.deck_list_browse_button = QPushButton(LoadListPage)
        self.deck_list_browse_button.setObjectName(u"deck_list_browse_button")
        icon1 = QIcon(QIcon.fromTheme(u"document-open"))
        self.deck_list_browse_button.setIcon(icon1)

        self.gridLayout.addWidget(self.deck_list_browse_button, 3, 0, 1, 4)

        self.scryfall_search_view_button = QPushButton(LoadListPage)
        self.scryfall_search_view_button.setObjectName(u"scryfall_search_view_button")
        self.scryfall_search_view_button.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.scryfall_search_view_button.sizePolicy().hasHeightForWidth())
        self.scryfall_search_view_button.setSizePolicy(sizePolicy1)
        icon2 = QIcon(QIcon.fromTheme(u"globe"))
        self.scryfall_search_view_button.setIcon(icon2)

        self.gridLayout.addWidget(self.scryfall_search_view_button, 1, 2, 1, 1)

        self.deck_list_download_button = QPushButton(LoadListPage)
        self.deck_list_download_button.setObjectName(u"deck_list_download_button")
        self.deck_list_download_button.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.deck_list_download_button.sizePolicy().hasHeightForWidth())
        self.deck_list_download_button.setSizePolicy(sizePolicy2)
        self.deck_list_download_button.setIcon(icon)

        self.gridLayout.addWidget(self.deck_list_download_button, 0, 2, 1, 2)

        QWidget.setTabOrder(self.deck_list_download_url_line_edit, self.deck_list_download_button)
        QWidget.setTabOrder(self.deck_list_download_button, self.scryfall_search)
        QWidget.setTabOrder(self.scryfall_search, self.scryfall_search_view_button)
        QWidget.setTabOrder(self.scryfall_search_view_button, self.scryfall_search_download_button)
        QWidget.setTabOrder(self.scryfall_search_download_button, self.deck_list_browse_button)
        QWidget.setTabOrder(self.deck_list_browse_button, self.deck_list)
        QWidget.setTabOrder(self.deck_list, self.translate_deck_list_enable)
        QWidget.setTabOrder(self.translate_deck_list_enable, self.translate_deck_list_target_language)
        QWidget.setTabOrder(self.translate_deck_list_target_language, self.print_guessing_enable)
        QWidget.setTabOrder(self.print_guessing_enable, self.print_guessing_prefer_already_downloaded)

        self.retranslateUi(LoadListPage)
        self.translate_deck_list_enable.toggled.connect(self.translate_deck_list_target_language.setEnabled)

        QMetaObject.connectSlotsByName(LoadListPage)
    # setupUi

    def retranslateUi(self, LoadListPage):
        LoadListPage.setTitle(QCoreApplication.translate("LoadListPage", u"Import a deck list for printing", None))
        LoadListPage.setSubTitle(QCoreApplication.translate("LoadListPage", u"Load a deck file from disk or paste deck list in the text field below", None))
        self.deck_list_download_url_line_edit.setPlaceholderText(QCoreApplication.translate("LoadListPage", u"Paste a link to a public deck list here. Hover to see supported sites.", None))
        self.scryfall_search.setPlaceholderText(QCoreApplication.translate("LoadListPage", u"Scryfall search query", None))
#if QT_CONFIG(tooltip)
        self.print_guessing_enable.setToolTip(QCoreApplication.translate("LoadListPage", u"If checked, choose an arbitrary printing, if a unique printing is not identified.\n"
"If unchecked, each ambiguous card is ignored and reported as unrecognized.", None))
#endif // QT_CONFIG(tooltip)
        self.print_guessing_enable.setText(QCoreApplication.translate("LoadListPage", u"Guess printings for ambiguous entries in the deck list", None))
        self.scryfall_search_download_button.setText(QCoreApplication.translate("LoadListPage", u"Download result", None))
        self.deck_list.setPlaceholderText(QCoreApplication.translate("LoadListPage", u"Paste your deck list here or use one of the actions above", None))
#if QT_CONFIG(tooltip)
        self.print_guessing_prefer_already_downloaded.setToolTip(QCoreApplication.translate("LoadListPage", u"When an exact printing is not determined or card translation is requested, choose a printing that is already downloaded, if possible.\n"
"Enabling this can potentially save disk space and download volume, based on the images already downloaded.", None))
#endif // QT_CONFIG(tooltip)
        self.print_guessing_prefer_already_downloaded.setText(QCoreApplication.translate("LoadListPage", u"When choosing a printing, prefer ones with already downloaded images", None))
        self.translate_deck_list_enable.setText(QCoreApplication.translate("LoadListPage", u"Translate deck list to:", None))
#if QT_CONFIG(tooltip)
        self.deck_list_browse_button.setToolTip(QCoreApplication.translate("LoadListPage", u"Opens a file picker and lets you load a deck file from disk.", None))
#endif // QT_CONFIG(tooltip)
        self.deck_list_browse_button.setText(QCoreApplication.translate("LoadListPage", u"Select deck list file", None))
        self.scryfall_search_view_button.setText(QCoreApplication.translate("LoadListPage", u"View result", None))
        self.deck_list_download_button.setText(QCoreApplication.translate("LoadListPage", u"Download deck list", None))
    # retranslateUi

