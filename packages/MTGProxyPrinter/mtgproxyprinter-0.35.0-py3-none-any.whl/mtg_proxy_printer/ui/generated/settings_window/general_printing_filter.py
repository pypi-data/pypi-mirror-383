# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'general_printing_filter.ui'
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
    QPushButton, QSizePolicy, QWidget)

class Ui_GeneralPrintingFilter(object):
    def setupUi(self, GeneralPrintingFilter):
        if not GeneralPrintingFilter.objectName():
            GeneralPrintingFilter.setObjectName(u"GeneralPrintingFilter")
        GeneralPrintingFilter.resize(505, 302)
        self.gridLayout = QGridLayout(GeneralPrintingFilter)
        self.gridLayout.setObjectName(u"gridLayout")
        self.view_digital_cards = QPushButton(GeneralPrintingFilter)
        self.view_digital_cards.setObjectName(u"view_digital_cards")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.view_digital_cards.sizePolicy().hasHeightForWidth())
        self.view_digital_cards.setSizePolicy(sizePolicy)
        icon = QIcon(QIcon.fromTheme(u"globe"))
        self.view_digital_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_digital_cards, 5, 3, 1, 1)

        self.view_cards_without_images = QPushButton(GeneralPrintingFilter)
        self.view_cards_without_images.setObjectName(u"view_cards_without_images")
        self.view_cards_without_images.setEnabled(False)
        sizePolicy.setHeightForWidth(self.view_cards_without_images.sizePolicy().hasHeightForWidth())
        self.view_cards_without_images.setSizePolicy(sizePolicy)
        self.view_cards_without_images.setIcon(icon)

        self.gridLayout.addWidget(self.view_cards_without_images, 2, 1, 1, 1)

        self.view_reversible_cards = QPushButton(GeneralPrintingFilter)
        self.view_reversible_cards.setObjectName(u"view_reversible_cards")
        sizePolicy.setHeightForWidth(self.view_reversible_cards.sizePolicy().hasHeightForWidth())
        self.view_reversible_cards.setSizePolicy(sizePolicy)
        self.view_reversible_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_reversible_cards, 6, 3, 1, 1)

        self.hide_borderless_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_borderless_cards.setObjectName(u"hide_borderless_cards")

        self.gridLayout.addWidget(self.hide_borderless_cards, 6, 0, 1, 1)

        self.hide_token = QCheckBox(GeneralPrintingFilter)
        self.hide_token.setObjectName(u"hide_token")

        self.gridLayout.addWidget(self.hide_token, 4, 2, 1, 1)

        self.view_funny_cards = QPushButton(GeneralPrintingFilter)
        self.view_funny_cards.setObjectName(u"view_funny_cards")
        sizePolicy.setHeightForWidth(self.view_funny_cards.sizePolicy().hasHeightForWidth())
        self.view_funny_cards.setSizePolicy(sizePolicy)
        self.view_funny_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_funny_cards, 2, 3, 1, 1)

        self.hide_reversible_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_reversible_cards.setObjectName(u"hide_reversible_cards")

        self.gridLayout.addWidget(self.hide_reversible_cards, 6, 2, 1, 1)

        self.view_token = QPushButton(GeneralPrintingFilter)
        self.view_token.setObjectName(u"view_token")
        sizePolicy.setHeightForWidth(self.view_token.sizePolicy().hasHeightForWidth())
        self.view_token.setSizePolicy(sizePolicy)
        self.view_token.setIcon(icon)

        self.gridLayout.addWidget(self.view_token, 4, 3, 1, 1)

        self.view_oversized_cards = QPushButton(GeneralPrintingFilter)
        self.view_oversized_cards.setObjectName(u"view_oversized_cards")
        sizePolicy.setHeightForWidth(self.view_oversized_cards.sizePolicy().hasHeightForWidth())
        self.view_oversized_cards.setSizePolicy(sizePolicy)
        self.view_oversized_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_oversized_cards, 0, 3, 1, 1)

        self.hide_digital_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_digital_cards.setObjectName(u"hide_digital_cards")

        self.gridLayout.addWidget(self.hide_digital_cards, 5, 2, 1, 1)

        self.hide_funny_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_funny_cards.setObjectName(u"hide_funny_cards")

        self.gridLayout.addWidget(self.hide_funny_cards, 2, 2, 1, 1)

        self.hide_oversized_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_oversized_cards.setObjectName(u"hide_oversized_cards")

        self.gridLayout.addWidget(self.hide_oversized_cards, 0, 2, 1, 1)

        self.hide_gold_bordered_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_gold_bordered_cards.setObjectName(u"hide_gold_bordered_cards")

        self.gridLayout.addWidget(self.hide_gold_bordered_cards, 5, 0, 1, 1)

        self.hide_white_bordered_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_white_bordered_cards.setObjectName(u"hide_white_bordered_cards")

        self.gridLayout.addWidget(self.hide_white_bordered_cards, 4, 0, 1, 1)

        self.hide_cards_depicting_racism = QCheckBox(GeneralPrintingFilter)
        self.hide_cards_depicting_racism.setObjectName(u"hide_cards_depicting_racism")

        self.gridLayout.addWidget(self.hide_cards_depicting_racism, 0, 0, 1, 1)

        self.view_cards_depicting_racism = QPushButton(GeneralPrintingFilter)
        self.view_cards_depicting_racism.setObjectName(u"view_cards_depicting_racism")
        sizePolicy.setHeightForWidth(self.view_cards_depicting_racism.sizePolicy().hasHeightForWidth())
        self.view_cards_depicting_racism.setSizePolicy(sizePolicy)
        self.view_cards_depicting_racism.setIcon(icon)

        self.gridLayout.addWidget(self.view_cards_depicting_racism, 0, 1, 1, 1)

        self.hide_cards_without_images = QCheckBox(GeneralPrintingFilter)
        self.hide_cards_without_images.setObjectName(u"hide_cards_without_images")

        self.gridLayout.addWidget(self.hide_cards_without_images, 2, 0, 1, 1)

        self.view_gold_bordered_cards = QPushButton(GeneralPrintingFilter)
        self.view_gold_bordered_cards.setObjectName(u"view_gold_bordered_cards")
        sizePolicy.setHeightForWidth(self.view_gold_bordered_cards.sizePolicy().hasHeightForWidth())
        self.view_gold_bordered_cards.setSizePolicy(sizePolicy)
        self.view_gold_bordered_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_gold_bordered_cards, 5, 1, 1, 1)

        self.view_white_bordered_cards = QPushButton(GeneralPrintingFilter)
        self.view_white_bordered_cards.setObjectName(u"view_white_bordered_cards")
        sizePolicy.setHeightForWidth(self.view_white_bordered_cards.sizePolicy().hasHeightForWidth())
        self.view_white_bordered_cards.setSizePolicy(sizePolicy)
        self.view_white_bordered_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_white_bordered_cards, 4, 1, 1, 1)

        self.view_borderless_cards = QPushButton(GeneralPrintingFilter)
        self.view_borderless_cards.setObjectName(u"view_borderless_cards")
        sizePolicy.setHeightForWidth(self.view_borderless_cards.sizePolicy().hasHeightForWidth())
        self.view_borderless_cards.setSizePolicy(sizePolicy)
        self.view_borderless_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_borderless_cards, 6, 1, 1, 1)

        self.view_extended_art_cards = QPushButton(GeneralPrintingFilter)
        self.view_extended_art_cards.setObjectName(u"view_extended_art_cards")
        self.view_extended_art_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_extended_art_cards, 7, 1, 1, 1)

        self.hide_extended_art_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_extended_art_cards.setObjectName(u"hide_extended_art_cards")

        self.gridLayout.addWidget(self.hide_extended_art_cards, 7, 0, 1, 1)

        self.hide_art_series_cards = QCheckBox(GeneralPrintingFilter)
        self.hide_art_series_cards.setObjectName(u"hide_art_series_cards")

        self.gridLayout.addWidget(self.hide_art_series_cards, 7, 2, 1, 1)

        self.view_art_series_cards = QPushButton(GeneralPrintingFilter)
        self.view_art_series_cards.setObjectName(u"view_art_series_cards")
        sizePolicy.setHeightForWidth(self.view_art_series_cards.sizePolicy().hasHeightForWidth())
        self.view_art_series_cards.setSizePolicy(sizePolicy)
        self.view_art_series_cards.setIcon(icon)

        self.gridLayout.addWidget(self.view_art_series_cards, 7, 3, 1, 1)


        self.retranslateUi(GeneralPrintingFilter)

        QMetaObject.connectSlotsByName(GeneralPrintingFilter)
    # setupUi

    def retranslateUi(self, GeneralPrintingFilter):
        GeneralPrintingFilter.setTitle(QCoreApplication.translate("GeneralPrintingFilter", u"General printing filters", None))
#if QT_CONFIG(tooltip)
        self.view_digital_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_cards_without_images.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_reversible_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.hide_borderless_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"Hide cards without a defined, solid-color border.\n"
"Those require higher cutting precision to get right.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_borderless_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide borderless cards", None))
        self.hide_token.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide Token cards", None))
#if QT_CONFIG(tooltip)
        self.view_funny_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.hide_reversible_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.\n"
"This filter hides those.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_reversible_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide reversible cards", None))
#if QT_CONFIG(tooltip)
        self.view_token.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_oversized_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.hide_digital_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_digital_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide digital cards", None))
#if QT_CONFIG(tooltip)
        self.hide_funny_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"\u201cFunny\u201d cards, not legal in any constructed format.\n"
"This includes full-art Contraptions from Unstable,\n"
"cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),\n"
"some black-bordered promotional cards with non-standard back faces,\n"
"and all silver-bordered cards.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_funny_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide \u201cfunny\u201d cards", None))
#if QT_CONFIG(tooltip)
        self.hide_oversized_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"These cards are larger than regular Magic cards and can\u2019t be included in decks.\n"
"Includes Archenemy schemes, Planechase planes and\n"
"oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_oversized_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide oversized cards", None))
#if QT_CONFIG(tooltip)
        self.hide_gold_bordered_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"Some \u201ccollectible\u201d sets, like full reprints of tournament-winning decks were printed with golden borders.\n"
"Many also have printed signatures of the involved players in the text box.\n"
"\n"
"These are not tournament legal", None))
#endif // QT_CONFIG(tooltip)
        self.hide_gold_bordered_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide gold-bordered cards", None))
        self.hide_white_bordered_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide white-bordered cards", None))
#if QT_CONFIG(tooltip)
        self.hide_cards_depicting_racism.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"<html><head/><body><p>Hide cards banned for depicting racism.</p><p>Background:</p><p>Some cards were banned by Wizards of the Coast, because they depict references to controversial real-world events, religion or contain combinations of card effect, name and artwork that, when viewed together, depict racism. These cards are banned in all sanctioned tournament formats and several community formats like Commander, Oathbreaker and others.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.hide_cards_depicting_racism.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide cards depicting racism", None))
#if QT_CONFIG(tooltip)
        self.view_cards_depicting_racism.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.hide_cards_without_images.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"Hide non-English cards with low-resolution,\n"
"English placeholder images with an overlay text stating\n"
"\u201cThis card is not available in the selected language.\u201d", None))
#endif // QT_CONFIG(tooltip)
        self.hide_cards_without_images.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide cards with placeholder images", None))
#if QT_CONFIG(tooltip)
        self.view_gold_bordered_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_white_bordered_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_borderless_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_extended_art_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.hide_extended_art_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"Hide cards with artwork extending to the left and right card border.\n"
"Similar to borderless cards, these require higher precision during the cutting process.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_extended_art_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide extended art cards", None))
#if QT_CONFIG(tooltip)
        self.hide_art_series_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"Artwork cards that can be found in Set Boosters or Play Boosters", None))
#endif // QT_CONFIG(tooltip)
        self.hide_art_series_cards.setText(QCoreApplication.translate("GeneralPrintingFilter", u"Hide Art Series cards", None))
#if QT_CONFIG(tooltip)
        self.view_art_series_cards.setToolTip(QCoreApplication.translate("GeneralPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

