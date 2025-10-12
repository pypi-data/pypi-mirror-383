# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'parser_result_page.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QHeaderView,
    QLabel, QSizePolicy, QTextBrowser, QVBoxLayout,
    QWidget, QWizardPage)

from mtg_proxy_printer.ui.card_list_table_view import CardListTableView

class Ui_SummaryPage(object):
    def setupUi(self, SummaryPage):
        if not SummaryPage.objectName():
            SummaryPage.setObjectName(u"SummaryPage")
        self.verticalLayout = QVBoxLayout(SummaryPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.should_replace_document = QCheckBox(SummaryPage)
        self.should_replace_document.setObjectName(u"should_replace_document")
        icon = QIcon(QIcon.fromTheme(u"document-replace"))
        self.should_replace_document.setIcon(icon)

        self.verticalLayout.addWidget(self.should_replace_document)

        self.parsed_cards_label = QLabel(SummaryPage)
        self.parsed_cards_label.setObjectName(u"parsed_cards_label")
        self.parsed_cards_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.parsed_cards_label)

        self.parsed_cards_table = CardListTableView(SummaryPage)
        self.parsed_cards_table.setObjectName(u"parsed_cards_table")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(65)
        sizePolicy.setHeightForWidth(self.parsed_cards_table.sizePolicy().hasHeightForWidth())
        self.parsed_cards_table.setSizePolicy(sizePolicy)
        self.parsed_cards_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.parsed_cards_table.setAlternatingRowColors(True)
        self.parsed_cards_table.setSortingEnabled(True)
        self.parsed_cards_table.horizontalHeader().setDefaultSectionSize(110)

        self.verticalLayout.addWidget(self.parsed_cards_table)

        self.unsuccessful_lines_label = QLabel(SummaryPage)
        self.unsuccessful_lines_label.setObjectName(u"unsuccessful_lines_label")
        self.unsuccessful_lines_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.unsuccessful_lines_label)

        self.unparsed_lines_text = QTextBrowser(SummaryPage)
        self.unparsed_lines_text.setObjectName(u"unparsed_lines_text")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(35)
        sizePolicy1.setHeightForWidth(self.unparsed_lines_text.sizePolicy().hasHeightForWidth())
        self.unparsed_lines_text.setSizePolicy(sizePolicy1)
        self.unparsed_lines_text.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.unparsed_lines_text.setAcceptRichText(False)
        self.unparsed_lines_text.setOpenLinks(False)

        self.verticalLayout.addWidget(self.unparsed_lines_text)


        self.retranslateUi(SummaryPage)

        QMetaObject.connectSlotsByName(SummaryPage)
    # setupUi

    def retranslateUi(self, SummaryPage):
        SummaryPage.setTitle(QCoreApplication.translate("SummaryPage", u"Import a deck list for printing", None))
        SummaryPage.setSubTitle(QCoreApplication.translate("SummaryPage", u"The cards shown in the table will be imported. Double-click the Set, Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.", None))
#if QT_CONFIG(tooltip)
        self.should_replace_document.setToolTip(QCoreApplication.translate("SummaryPage", u"If checked, clear all cards in the current document, replacing everything with the list below.\n"
"If unchecked, append the cards found below to the document.", None))
#endif // QT_CONFIG(tooltip)
        self.should_replace_document.setText(QCoreApplication.translate("SummaryPage", u"Replace the current document content with the found cards", None))
        self.parsed_cards_label.setText(QCoreApplication.translate("SummaryPage", u"These cards were successfully identified:", None))
        self.unsuccessful_lines_label.setText(QCoreApplication.translate("SummaryPage", u"These lines from the deck list were not identified as cards:", None))
        self.unparsed_lines_text.setPlaceholderText(QCoreApplication.translate("SummaryPage", u"Nothing. All cards were successfully identified!", None))
    # retranslateUi

