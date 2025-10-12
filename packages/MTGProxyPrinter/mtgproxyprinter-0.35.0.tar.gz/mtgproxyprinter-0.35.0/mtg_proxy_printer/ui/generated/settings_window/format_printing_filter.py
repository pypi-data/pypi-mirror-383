# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'format_printing_filter.ui'
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

class Ui_FormatPrintingFilter(object):
    def setupUi(self, FormatPrintingFilter):
        if not FormatPrintingFilter.objectName():
            FormatPrintingFilter.setObjectName(u"FormatPrintingFilter")
        FormatPrintingFilter.resize(400, 300)
        self.format_filter_layout = QGridLayout(FormatPrintingFilter)
        self.format_filter_layout.setObjectName(u"format_filter_layout")
        self.hide_banned_in_pioneer = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_pioneer.setObjectName(u"hide_banned_in_pioneer")

        self.format_filter_layout.addWidget(self.hide_banned_in_pioneer, 2, 2, 1, 1)

        self.hide_banned_in_modern = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_modern.setObjectName(u"hide_banned_in_modern")

        self.format_filter_layout.addWidget(self.hide_banned_in_modern, 4, 0, 1, 1)

        self.hide_banned_in_historic = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_historic.setObjectName(u"hide_banned_in_historic")

        self.format_filter_layout.addWidget(self.hide_banned_in_historic, 2, 0, 1, 1)

        self.hide_banned_in_vintage = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_vintage.setObjectName(u"hide_banned_in_vintage")

        self.format_filter_layout.addWidget(self.hide_banned_in_vintage, 4, 2, 1, 1)

        self.view_banned_in_brawl = QPushButton(FormatPrintingFilter)
        self.view_banned_in_brawl.setObjectName(u"view_banned_in_brawl")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.view_banned_in_brawl.sizePolicy().hasHeightForWidth())
        self.view_banned_in_brawl.setSizePolicy(sizePolicy)
        icon = QIcon(QIcon.fromTheme(u"globe"))
        self.view_banned_in_brawl.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_brawl, 0, 1, 1, 1)

        self.hide_banned_in_penny = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_penny.setObjectName(u"hide_banned_in_penny")

        self.format_filter_layout.addWidget(self.hide_banned_in_penny, 1, 2, 1, 1)

        self.hide_banned_in_standard = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_standard.setObjectName(u"hide_banned_in_standard")

        self.format_filter_layout.addWidget(self.hide_banned_in_standard, 3, 2, 1, 1)

        self.view_banned_in_pioneer = QPushButton(FormatPrintingFilter)
        self.view_banned_in_pioneer.setObjectName(u"view_banned_in_pioneer")
        sizePolicy.setHeightForWidth(self.view_banned_in_pioneer.sizePolicy().hasHeightForWidth())
        self.view_banned_in_pioneer.setSizePolicy(sizePolicy)
        self.view_banned_in_pioneer.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_pioneer, 2, 3, 1, 1)

        self.hide_banned_in_pauper = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_pauper.setObjectName(u"hide_banned_in_pauper")

        self.format_filter_layout.addWidget(self.hide_banned_in_pauper, 0, 2, 1, 1)

        self.hide_banned_in_commander = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_commander.setObjectName(u"hide_banned_in_commander")

        self.format_filter_layout.addWidget(self.hide_banned_in_commander, 1, 0, 1, 1)

        self.view_banned_in_standard = QPushButton(FormatPrintingFilter)
        self.view_banned_in_standard.setObjectName(u"view_banned_in_standard")
        sizePolicy.setHeightForWidth(self.view_banned_in_standard.sizePolicy().hasHeightForWidth())
        self.view_banned_in_standard.setSizePolicy(sizePolicy)
        self.view_banned_in_standard.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_standard, 3, 3, 1, 1)

        self.view_banned_in_legacy = QPushButton(FormatPrintingFilter)
        self.view_banned_in_legacy.setObjectName(u"view_banned_in_legacy")
        sizePolicy.setHeightForWidth(self.view_banned_in_legacy.sizePolicy().hasHeightForWidth())
        self.view_banned_in_legacy.setSizePolicy(sizePolicy)
        self.view_banned_in_legacy.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_legacy, 3, 1, 1, 1)

        self.hide_banned_in_brawl = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_brawl.setObjectName(u"hide_banned_in_brawl")

        self.format_filter_layout.addWidget(self.hide_banned_in_brawl, 0, 0, 1, 1)

        self.view_banned_in_vintage = QPushButton(FormatPrintingFilter)
        self.view_banned_in_vintage.setObjectName(u"view_banned_in_vintage")
        sizePolicy.setHeightForWidth(self.view_banned_in_vintage.sizePolicy().hasHeightForWidth())
        self.view_banned_in_vintage.setSizePolicy(sizePolicy)
        self.view_banned_in_vintage.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_vintage, 4, 3, 1, 1)

        self.view_banned_in_pauper = QPushButton(FormatPrintingFilter)
        self.view_banned_in_pauper.setObjectName(u"view_banned_in_pauper")
        sizePolicy.setHeightForWidth(self.view_banned_in_pauper.sizePolicy().hasHeightForWidth())
        self.view_banned_in_pauper.setSizePolicy(sizePolicy)
        self.view_banned_in_pauper.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_pauper, 0, 3, 1, 1)

        self.view_banned_in_modern = QPushButton(FormatPrintingFilter)
        self.view_banned_in_modern.setObjectName(u"view_banned_in_modern")
        sizePolicy.setHeightForWidth(self.view_banned_in_modern.sizePolicy().hasHeightForWidth())
        self.view_banned_in_modern.setSizePolicy(sizePolicy)
        self.view_banned_in_modern.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_modern, 4, 1, 1, 1)

        self.view_banned_in_penny = QPushButton(FormatPrintingFilter)
        self.view_banned_in_penny.setObjectName(u"view_banned_in_penny")
        sizePolicy.setHeightForWidth(self.view_banned_in_penny.sizePolicy().hasHeightForWidth())
        self.view_banned_in_penny.setSizePolicy(sizePolicy)
        self.view_banned_in_penny.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_penny, 1, 3, 1, 1)

        self.view_banned_in_historic = QPushButton(FormatPrintingFilter)
        self.view_banned_in_historic.setObjectName(u"view_banned_in_historic")
        sizePolicy.setHeightForWidth(self.view_banned_in_historic.sizePolicy().hasHeightForWidth())
        self.view_banned_in_historic.setSizePolicy(sizePolicy)
        self.view_banned_in_historic.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_historic, 2, 1, 1, 1)

        self.hide_banned_in_legacy = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_legacy.setObjectName(u"hide_banned_in_legacy")

        self.format_filter_layout.addWidget(self.hide_banned_in_legacy, 3, 0, 1, 1)

        self.view_banned_in_commander = QPushButton(FormatPrintingFilter)
        self.view_banned_in_commander.setObjectName(u"view_banned_in_commander")
        sizePolicy.setHeightForWidth(self.view_banned_in_commander.sizePolicy().hasHeightForWidth())
        self.view_banned_in_commander.setSizePolicy(sizePolicy)
        self.view_banned_in_commander.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_commander, 1, 1, 1, 1)

        self.hide_banned_in_oathbreaker = QCheckBox(FormatPrintingFilter)
        self.hide_banned_in_oathbreaker.setObjectName(u"hide_banned_in_oathbreaker")

        self.format_filter_layout.addWidget(self.hide_banned_in_oathbreaker, 5, 0, 1, 1)

        self.view_banned_in_oathbreaker = QPushButton(FormatPrintingFilter)
        self.view_banned_in_oathbreaker.setObjectName(u"view_banned_in_oathbreaker")
        self.view_banned_in_oathbreaker.setIcon(icon)

        self.format_filter_layout.addWidget(self.view_banned_in_oathbreaker, 5, 1, 1, 1)

        self.hide_banned_in_modern.raise_()
        self.hide_banned_in_historic.raise_()
        self.view_banned_in_brawl.raise_()
        self.view_banned_in_pioneer.raise_()
        self.hide_banned_in_commander.raise_()
        self.view_banned_in_standard.raise_()
        self.view_banned_in_legacy.raise_()
        self.hide_banned_in_brawl.raise_()
        self.view_banned_in_vintage.raise_()
        self.view_banned_in_pauper.raise_()
        self.view_banned_in_modern.raise_()
        self.view_banned_in_penny.raise_()
        self.view_banned_in_historic.raise_()
        self.hide_banned_in_legacy.raise_()
        self.view_banned_in_commander.raise_()
        self.view_banned_in_oathbreaker.raise_()
        self.hide_banned_in_penny.raise_()
        self.hide_banned_in_oathbreaker.raise_()
        self.hide_banned_in_pauper.raise_()
        self.hide_banned_in_standard.raise_()
        self.hide_banned_in_vintage.raise_()
        self.hide_banned_in_pioneer.raise_()

        self.retranslateUi(FormatPrintingFilter)

        QMetaObject.connectSlotsByName(FormatPrintingFilter)
    # setupUi

    def retranslateUi(self, FormatPrintingFilter):
        FormatPrintingFilter.setTitle(QCoreApplication.translate("FormatPrintingFilter", u"Hide cards banned in specific Formats", None))
        self.hide_banned_in_pioneer.setText(QCoreApplication.translate("FormatPrintingFilter", u"Pioneer", None))
        self.hide_banned_in_modern.setText(QCoreApplication.translate("FormatPrintingFilter", u"Modern", None))
        self.hide_banned_in_historic.setText(QCoreApplication.translate("FormatPrintingFilter", u"Historic", None))
        self.hide_banned_in_vintage.setText(QCoreApplication.translate("FormatPrintingFilter", u"Vintage", None))
#if QT_CONFIG(tooltip)
        self.view_banned_in_brawl.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_banned_in_penny.setText(QCoreApplication.translate("FormatPrintingFilter", u"Penny", None))
        self.hide_banned_in_standard.setText(QCoreApplication.translate("FormatPrintingFilter", u"Standard", None))
#if QT_CONFIG(tooltip)
        self.view_banned_in_pioneer.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_banned_in_pauper.setText(QCoreApplication.translate("FormatPrintingFilter", u"Pauper", None))
        self.hide_banned_in_commander.setText(QCoreApplication.translate("FormatPrintingFilter", u"Commander", None))
#if QT_CONFIG(tooltip)
        self.view_banned_in_standard.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_banned_in_legacy.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_banned_in_brawl.setText(QCoreApplication.translate("FormatPrintingFilter", u"Brawl", None))
#if QT_CONFIG(tooltip)
        self.view_banned_in_vintage.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_banned_in_pauper.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_banned_in_modern.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_banned_in_penny.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.view_banned_in_historic.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_banned_in_legacy.setText(QCoreApplication.translate("FormatPrintingFilter", u"Legacy", None))
#if QT_CONFIG(tooltip)
        self.view_banned_in_commander.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
        self.hide_banned_in_oathbreaker.setText(QCoreApplication.translate("FormatPrintingFilter", u"Oathbreaker", None))
#if QT_CONFIG(tooltip)
        self.view_banned_in_oathbreaker.setToolTip(QCoreApplication.translate("FormatPrintingFilter", u"View cards hidden by this filter on the Scryfall website.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

