# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'printer_settings_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QGridLayout,
    QLabel, QSizePolicy, QSpacerItem, QWidget)

class Ui_PrinterSettingsPage(object):
    def setupUi(self, PrinterSettingsPage):
        if not PrinterSettingsPage.objectName():
            PrinterSettingsPage.setObjectName(u"PrinterSettingsPage")
        PrinterSettingsPage.resize(348, 304)
        self.gridLayout = QGridLayout(PrinterSettingsPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontal_offset_label = QLabel(PrinterSettingsPage)
        self.horizontal_offset_label.setObjectName(u"horizontal_offset_label")

        self.gridLayout.addWidget(self.horizontal_offset_label, 2, 0, 1, 1)

        self.horizontal_offset = QDoubleSpinBox(PrinterSettingsPage)
        self.horizontal_offset.setObjectName(u"horizontal_offset")
        self.horizontal_offset.setMinimum(-100.000000000000000)
        self.horizontal_offset.setMaximum(100.000000000000000)
        self.horizontal_offset.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.horizontal_offset, 2, 1, 1, 1)

        self.landscape_workaround = QCheckBox(PrinterSettingsPage)
        self.landscape_workaround.setObjectName(u"landscape_workaround")
        self.landscape_workaround.setProperty(u"wordWrap", True)

        self.gridLayout.addWidget(self.landscape_workaround, 1, 0, 1, 2)

        self.printer_use_borderless_printing = QCheckBox(PrinterSettingsPage)
        self.printer_use_borderless_printing.setObjectName(u"printer_use_borderless_printing")

        self.gridLayout.addWidget(self.printer_use_borderless_printing, 0, 0, 1, 2)

        self.vertical_spacer = QSpacerItem(20, 261, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.vertical_spacer, 3, 0, 1, 2)


        self.retranslateUi(PrinterSettingsPage)

        QMetaObject.connectSlotsByName(PrinterSettingsPage)
    # setupUi

    def retranslateUi(self, PrinterSettingsPage):
        self.horizontal_offset_label.setText(QCoreApplication.translate("PrinterSettingsPage", u"Horizontal printing offset", None))
#if QT_CONFIG(tooltip)
        self.horizontal_offset.setToolTip(QCoreApplication.translate("PrinterSettingsPage", u"Globally shifts the printing area to correct physical offsets in the printer.\n"
"Positive values shift to the right.\n"
"Negative offsets shift to the left.", None))
#endif // QT_CONFIG(tooltip)
        self.horizontal_offset.setPrefix("")
        self.horizontal_offset.setSuffix(QCoreApplication.translate("PrinterSettingsPage", u" mm", None))
#if QT_CONFIG(tooltip)
        self.landscape_workaround.setToolTip(QCoreApplication.translate("PrinterSettingsPage", u"If enabled, print landscape documents in portrait mode with all content rotated by 90\u00b0.\n"
"Enable this, if printing landscape documents results in portrait printouts with cropped-off sides.", None))
#endif // QT_CONFIG(tooltip)
        self.landscape_workaround.setText(QCoreApplication.translate("PrinterSettingsPage", u"Enable landscape workaround: Rotate prints by 90\u00b0", None))
#if QT_CONFIG(tooltip)
        self.printer_use_borderless_printing.setToolTip(QCoreApplication.translate("PrinterSettingsPage", u"When enabled, instruct the printer to use borderless mode and let MTGProxyPrinter manage the printing margins.\n"
"Disable this, if your printer keeps scaling print-outs up or down.\n"
"\n"
"When disabled, managing the page margins is delegated to the printer driver,\n"
"which should increase compatibility, at the expense of drawing shorter cut helper lines.", None))
#endif // QT_CONFIG(tooltip)
        self.printer_use_borderless_printing.setText(QCoreApplication.translate("PrinterSettingsPage", u"Configure printer for borderless printing", None))
        pass
    # retranslateUi

