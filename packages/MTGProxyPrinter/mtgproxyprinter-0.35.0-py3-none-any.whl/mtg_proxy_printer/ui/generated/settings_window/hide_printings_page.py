# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'hide_printings_page.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QPlainTextEdit, QSizePolicy,
    QVBoxLayout, QWidget)

from mtg_proxy_printer.ui.printing_filter_widgets import (FormatPrintingFilter, GeneralPrintingFilter)

class Ui_HidePrintingsPage(object):
    def setupUi(self, HidePrintingsPage):
        if not HidePrintingsPage.objectName():
            HidePrintingsPage.setObjectName(u"HidePrintingsPage")
        HidePrintingsPage.resize(332, 462)
        self.verticalLayout = QVBoxLayout(HidePrintingsPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.card_filter_settings_header_label = QLabel(HidePrintingsPage)
        self.card_filter_settings_header_label.setObjectName(u"card_filter_settings_header_label")
        self.card_filter_settings_header_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.card_filter_settings_header_label)

        self.card_filter_general_settings = GeneralPrintingFilter(HidePrintingsPage)
        self.card_filter_general_settings.setObjectName(u"card_filter_general_settings")

        self.verticalLayout.addWidget(self.card_filter_general_settings)

        self.card_filter_format_settings = FormatPrintingFilter(HidePrintingsPage)
        self.card_filter_format_settings.setObjectName(u"card_filter_format_settings")

        self.verticalLayout.addWidget(self.card_filter_format_settings)

        self.set_filter_label = QLabel(HidePrintingsPage)
        self.set_filter_label.setObjectName(u"set_filter_label")
        self.set_filter_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.set_filter_label)

        self.set_filter_settings = QPlainTextEdit(HidePrintingsPage)
        self.set_filter_settings.setObjectName(u"set_filter_settings")
        self.set_filter_settings.setInputMethodHints(Qt.InputMethodHint.ImhLatinOnly|Qt.InputMethodHint.ImhMultiLine|Qt.InputMethodHint.ImhNoAutoUppercase|Qt.InputMethodHint.ImhNoPredictiveText)

        self.verticalLayout.addWidget(self.set_filter_settings)


        self.retranslateUi(HidePrintingsPage)

        QMetaObject.connectSlotsByName(HidePrintingsPage)
    # setupUi

    def retranslateUi(self, HidePrintingsPage):
        self.card_filter_settings_header_label.setText(QCoreApplication.translate("HidePrintingsPage", u"These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don\u2019t exist. They can\u2019t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won\u2019t be available at all.", None))
        self.set_filter_label.setText(QCoreApplication.translate("HidePrintingsPage", u"Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.", None))
#if QT_CONFIG(tooltip)
        self.set_filter_settings.setToolTip(QCoreApplication.translate("HidePrintingsPage", u"Example:\n"
"\n"
"LEA DDU TC13 J21", None))
#endif // QT_CONFIG(tooltip)
        self.set_filter_settings.setPlaceholderText(QCoreApplication.translate("HidePrintingsPage", u"No sets currently hidden.", None))
        pass
    # retranslateUi

