# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_deck_parser_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QWidget, QWizardPage)

class Ui_SelectDeckParserPage(object):
    def setupUi(self, SelectDeckParserPage):
        if not SelectDeckParserPage.objectName():
            SelectDeckParserPage.setObjectName(u"SelectDeckParserPage")
        SelectDeckParserPage.resize(371, 398)
        self.gridLayout = QGridLayout(SelectDeckParserPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tappedout_include_acquire_board = QCheckBox(SelectDeckParserPage)
        self.tappedout_include_acquire_board.setObjectName(u"tappedout_include_acquire_board")
        self.tappedout_include_acquire_board.setEnabled(False)

        self.gridLayout.addWidget(self.tappedout_include_acquire_board, 7, 3, 1, 1)

        self.sample_buttons_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.sample_buttons_spacer, 11, 1, 1, 1)

        self.select_parser_card_name_list = QRadioButton(SelectDeckParserPage)
        self.select_parser_card_name_list.setObjectName(u"select_parser_card_name_list")

        self.gridLayout.addWidget(self.select_parser_card_name_list, 0, 1, 1, 4)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 7, 4, 1, 1)

        self.tapped_out_board_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.tapped_out_board_spacer, 7, 1, 1, 1)

        self.select_parser_scryfall_csv = QRadioButton(SelectDeckParserPage)
        self.select_parser_scryfall_csv.setObjectName(u"select_parser_scryfall_csv")

        self.gridLayout.addWidget(self.select_parser_scryfall_csv, 5, 1, 1, 4)

        self.select_parser_xmage = QRadioButton(SelectDeckParserPage)
        self.select_parser_xmage.setObjectName(u"select_parser_xmage")

        self.gridLayout.addWidget(self.select_parser_xmage, 4, 1, 1, 4)

        self.select_parser_custom_re = QRadioButton(SelectDeckParserPage)
        self.select_parser_custom_re.setObjectName(u"select_parser_custom_re")

        self.gridLayout.addWidget(self.select_parser_custom_re, 9, 1, 1, 4)

        self.select_parser_tappedout_csv = QRadioButton(SelectDeckParserPage)
        self.select_parser_tappedout_csv.setObjectName(u"select_parser_tappedout_csv")

        self.gridLayout.addWidget(self.select_parser_tappedout_csv, 6, 1, 1, 4)

        self.select_parser_mtg_online = QRadioButton(SelectDeckParserPage)
        self.select_parser_mtg_online.setObjectName(u"select_parser_mtg_online")

        self.gridLayout.addWidget(self.select_parser_mtg_online, 2, 1, 1, 4)

        self.select_parser_magic_workstation = QRadioButton(SelectDeckParserPage)
        self.select_parser_magic_workstation.setObjectName(u"select_parser_magic_workstation")

        self.gridLayout.addWidget(self.select_parser_magic_workstation, 3, 1, 1, 4)

        self.select_parser_mtg_arena = QRadioButton(SelectDeckParserPage)
        self.select_parser_mtg_arena.setObjectName(u"select_parser_mtg_arena")

        self.gridLayout.addWidget(self.select_parser_mtg_arena, 1, 1, 1, 4)

        self.tappedout_include_maybe_board = QCheckBox(SelectDeckParserPage)
        self.tappedout_include_maybe_board.setObjectName(u"tappedout_include_maybe_board")
        self.tappedout_include_maybe_board.setEnabled(False)

        self.gridLayout.addWidget(self.tappedout_include_maybe_board, 7, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 14, 1, 1, 4)

        self.sample_buttons_layout = QGridLayout()
        self.sample_buttons_layout.setObjectName(u"sample_buttons_layout")
        self.insert_name_matcher_sample_button = QPushButton(SelectDeckParserPage)
        self.insert_name_matcher_sample_button.setObjectName(u"insert_name_matcher_sample_button")
        self.insert_name_matcher_sample_button.setEnabled(False)

        self.sample_buttons_layout.addWidget(self.insert_name_matcher_sample_button, 1, 0, 1, 1)

        self.insert_collector_number_matcher_sample_button = QPushButton(SelectDeckParserPage)
        self.insert_collector_number_matcher_sample_button.setObjectName(u"insert_collector_number_matcher_sample_button")
        self.insert_collector_number_matcher_sample_button.setEnabled(False)

        self.sample_buttons_layout.addWidget(self.insert_collector_number_matcher_sample_button, 2, 0, 1, 1)

        self.insert_language_matcher_sample_button = QPushButton(SelectDeckParserPage)
        self.insert_language_matcher_sample_button.setObjectName(u"insert_language_matcher_sample_button")
        self.insert_language_matcher_sample_button.setEnabled(False)

        self.sample_buttons_layout.addWidget(self.insert_language_matcher_sample_button, 3, 0, 1, 1)

        self.insert_set_code_matcher_sample_button = QPushButton(SelectDeckParserPage)
        self.insert_set_code_matcher_sample_button.setObjectName(u"insert_set_code_matcher_sample_button")
        self.insert_set_code_matcher_sample_button.setEnabled(False)

        self.sample_buttons_layout.addWidget(self.insert_set_code_matcher_sample_button, 1, 1, 1, 1)

        self.insert_copies_matcher_sample_button = QPushButton(SelectDeckParserPage)
        self.insert_copies_matcher_sample_button.setObjectName(u"insert_copies_matcher_sample_button")
        self.insert_copies_matcher_sample_button.setEnabled(False)

        self.sample_buttons_layout.addWidget(self.insert_copies_matcher_sample_button, 2, 1, 1, 1)

        self.insert_scryfall_id_matcher_sample_button = QPushButton(SelectDeckParserPage)
        self.insert_scryfall_id_matcher_sample_button.setObjectName(u"insert_scryfall_id_matcher_sample_button")
        self.insert_scryfall_id_matcher_sample_button.setEnabled(False)

        self.sample_buttons_layout.addWidget(self.insert_scryfall_id_matcher_sample_button, 3, 1, 1, 1)

        self.custom_re_input = QLineEdit(SelectDeckParserPage)
        self.custom_re_input.setObjectName(u"custom_re_input")
        self.custom_re_input.setEnabled(False)
        self.custom_re_input.setInputMethodHints(Qt.InputMethodHint.ImhPreferLatin)
        self.custom_re_input.setPlaceholderText(u"(?P<copies>\\w+) (?P<name>.+) \\((?P<set_code>\\w+)\\) (?P<collector_number>\\d+)")
        self.custom_re_input.setClearButtonEnabled(True)

        self.sample_buttons_layout.addWidget(self.custom_re_input, 0, 0, 1, 2)


        self.gridLayout.addLayout(self.sample_buttons_layout, 11, 2, 1, 3)


        self.retranslateUi(SelectDeckParserPage)
        self.select_parser_custom_re.toggled.connect(self.custom_re_input.setEnabled)
        self.select_parser_card_name_list.clicked.connect(SelectDeckParserPage.isComplete)
        self.select_parser_mtg_arena.clicked.connect(SelectDeckParserPage.isComplete)
        self.select_parser_mtg_online.clicked.connect(SelectDeckParserPage.isComplete)
        self.select_parser_scryfall_csv.clicked.connect(SelectDeckParserPage.isComplete)
        self.select_parser_custom_re.clicked.connect(SelectDeckParserPage.isComplete)
        self.select_parser_xmage.clicked.connect(SelectDeckParserPage.isComplete)
        self.custom_re_input.textChanged.connect(SelectDeckParserPage.isComplete)
        self.select_parser_tappedout_csv.clicked.connect(SelectDeckParserPage.isComplete)
        self.select_parser_tappedout_csv.toggled.connect(self.tappedout_include_maybe_board.setEnabled)
        self.select_parser_tappedout_csv.toggled.connect(self.tappedout_include_acquire_board.setEnabled)
        self.select_parser_custom_re.toggled.connect(self.insert_name_matcher_sample_button.setEnabled)
        self.select_parser_custom_re.toggled.connect(self.insert_collector_number_matcher_sample_button.setEnabled)
        self.select_parser_custom_re.toggled.connect(self.insert_scryfall_id_matcher_sample_button.setEnabled)
        self.select_parser_custom_re.toggled.connect(self.insert_set_code_matcher_sample_button.setEnabled)
        self.select_parser_custom_re.toggled.connect(self.insert_copies_matcher_sample_button.setEnabled)
        self.select_parser_custom_re.toggled.connect(self.insert_language_matcher_sample_button.setEnabled)
        self.select_parser_magic_workstation.clicked.connect(SelectDeckParserPage.isComplete)

        QMetaObject.connectSlotsByName(SelectDeckParserPage)
    # setupUi

    def retranslateUi(self, SelectDeckParserPage):
        SelectDeckParserPage.setTitle(QCoreApplication.translate("SelectDeckParserPage", u"Import a deck list for printing", None))
        SelectDeckParserPage.setSubTitle(QCoreApplication.translate("SelectDeckParserPage", u"Select which kind of deck list you want to import.", None))
#if QT_CONFIG(tooltip)
        self.tappedout_include_acquire_board.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"This is a Tappedout-specific section of the deck.\n"
"It may contain the deck list author\u2019s buy-list or anything else.", None))
#endif // QT_CONFIG(tooltip)
        self.tappedout_include_acquire_board.setText(QCoreApplication.translate("SelectDeckParserPage", u"Include \u201cAcquire-Board\u201d", None))
#if QT_CONFIG(tooltip)
        self.select_parser_card_name_list.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"A simple list, containing one card name per line", None))
#endif // QT_CONFIG(tooltip)
        self.select_parser_card_name_list.setText(QCoreApplication.translate("SelectDeckParserPage", u"List with card names", None))
#if QT_CONFIG(tooltip)
        self.select_parser_scryfall_csv.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"CSV exports from Scryfall\u2019s own deck builder.\n"
"Gives very accurate results, unless the imported deck list contains ignored items\n"
"matching an enabled card filter.", None))
#endif // QT_CONFIG(tooltip)
        self.select_parser_scryfall_csv.setText(QCoreApplication.translate("SelectDeckParserPage", u"Scryfall.com deck lists (CSV export)", None))
#if QT_CONFIG(tooltip)
        self.select_parser_xmage.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Deck list files, stored in XMage\u2019s native format.\n"
"Because XMage closely follows Scryfall regarding Magic sets,\n"
"this should give very accurate results.", None))
#endif // QT_CONFIG(tooltip)
        self.select_parser_xmage.setText(QCoreApplication.translate("SelectDeckParserPage", u"XMage", None))
#if QT_CONFIG(tooltip)
        self.select_parser_custom_re.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Specify a custom regular expression in the input field below. It will be used to parse each deck list line.\n"
"You can use the buttons below to insert basic building blocks.\n"
"You have to separate them with the \u201ccontrol structures\u201d, like spaces, as used in your deck list.", None))
#endif // QT_CONFIG(tooltip)
        self.select_parser_custom_re.setText(QCoreApplication.translate("SelectDeckParserPage", u"Custom regular expression based parser:", None))
#if QT_CONFIG(tooltip)
        self.select_parser_tappedout_csv.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.", None))
#endif // QT_CONFIG(tooltip)
        self.select_parser_tappedout_csv.setText(QCoreApplication.translate("SelectDeckParserPage", u"tappedout.net deck list (CSV export)", None))
#if QT_CONFIG(tooltip)
        self.select_parser_mtg_online.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.", None))
#endif // QT_CONFIG(tooltip)
        self.select_parser_mtg_online.setText(QCoreApplication.translate("SelectDeckParserPage", u"Magic Online", None))
        self.select_parser_magic_workstation.setText(QCoreApplication.translate("SelectDeckParserPage", u"Magic Workstation Deck Data (mwDeck)", None))
#if QT_CONFIG(tooltip)
        self.select_parser_mtg_arena.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Magic Arena and exports from compatible websites, like moxfield.com\n"
"Note that this option is not limited to cards in Standard/Historic,\n"
"as the format works for any card.", None))
#endif // QT_CONFIG(tooltip)
        self.select_parser_mtg_arena.setText(QCoreApplication.translate("SelectDeckParserPage", u"MTG Arena", None))
#if QT_CONFIG(tooltip)
        self.tappedout_include_maybe_board.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"This is a Tappedout-specific section of the deck.\n"
"It may contain cards that the deck list creator considers for inclusion, based on the meta\n"
"or any other preference, like card price.", None))
#endif // QT_CONFIG(tooltip)
        self.tappedout_include_maybe_board.setText(QCoreApplication.translate("SelectDeckParserPage", u"Include \u201cMaybe-Board\u201d", None))
#if QT_CONFIG(tooltip)
        self.insert_name_matcher_sample_button.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Appends a matcher for a card name to the input field above.", None))
#endif // QT_CONFIG(tooltip)
        self.insert_name_matcher_sample_button.setText(QCoreApplication.translate("SelectDeckParserPage", u"Card name matcher", None))
#if QT_CONFIG(tooltip)
        self.insert_collector_number_matcher_sample_button.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Appends a sample matcher for a collector number to the input field above", None))
#endif // QT_CONFIG(tooltip)
        self.insert_collector_number_matcher_sample_button.setText(QCoreApplication.translate("SelectDeckParserPage", u"Collector number matcher", None))
#if QT_CONFIG(tooltip)
        self.insert_language_matcher_sample_button.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Appends a matcher for the  card language to the input field above.\n"
"If a language field is not present in the deck list, the card language is guessed.", None))
#endif // QT_CONFIG(tooltip)
        self.insert_language_matcher_sample_button.setText(QCoreApplication.translate("SelectDeckParserPage", u"Language matcher", None))
#if QT_CONFIG(tooltip)
        self.insert_set_code_matcher_sample_button.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Appends a sample matcher for a set code to the input field above.", None))
#endif // QT_CONFIG(tooltip)
        self.insert_set_code_matcher_sample_button.setText(QCoreApplication.translate("SelectDeckParserPage", u"Set code matcher", None))
#if QT_CONFIG(tooltip)
        self.insert_copies_matcher_sample_button.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Appends a matcher for the number of card copies to the input field above.\n"
"If a card count field is not present in the deck list, 1 card copy per line is assumed", None))
#endif // QT_CONFIG(tooltip)
        self.insert_copies_matcher_sample_button.setText(QCoreApplication.translate("SelectDeckParserPage", u"Copies matcher", None))
#if QT_CONFIG(tooltip)
        self.insert_scryfall_id_matcher_sample_button.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Appends a matcher for the Scryfall ID to the input field above.\n"
"This may be used by deck lists that closely integrate with the Scryfall website.\n"
"Most deck lists won\u2019t use this.", None))
#endif // QT_CONFIG(tooltip)
        self.insert_scryfall_id_matcher_sample_button.setText(QCoreApplication.translate("SelectDeckParserPage", u"Scryfall ID matcher", None))
#if QT_CONFIG(tooltip)
        self.custom_re_input.setToolTip(QCoreApplication.translate("SelectDeckParserPage", u"Enter a Regular Expression containing at least one supported, named group.\n"
"\n"
"Supported named groups are: {group_names}\n"
"\n"
"See the 'What\u2019s this?' (?-Button) help for details.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.custom_re_input.setWhatsThis(QCoreApplication.translate("SelectDeckParserPage", u"You can enter a custom Regular Expression (in Python syntax) to parse the lines of your deck list. Use *named groups* to extract the individual card properties from the individual lines of the deck list.\n"
"A named group looks like this:\n"
"**(?P\\<GroupName>RE)**, where RE is a Regular Expression matching the part you want to extract, and GroupName is one of the following:\n"
"\n"
"- `copies`: The number of card copies. Defaults to 1, if not present\n"
"- `name`: The card name\n"
"- `set_code`: The 3 (or more) letter code identifying the set\n"
"- `collector_number`: The collector number of the card\n"
"- `language`: The card language, using a two-letter language code. If not given, the importer tries to determine the language from the card name. Defaults to \"en\" for English, if not possible.\n"
"\n"
"Not all groups are required for a successful match. For example, `set_code` and `collector_number` is sufficient for exact identification most of the time.\n"
"Hint: You may want to use an online Regular Exp"
                        "ression editor, like [](https://regex101.com/), for example.", None))
#endif // QT_CONFIG(whatsthis)
    # retranslateUi

