# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_settings_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QWidget)

class Ui_ExportSettingsPage(object):
    def setupUi(self, ExportSettingsPage):
        if not ExportSettingsPage.objectName():
            ExportSettingsPage.setObjectName(u"ExportSettingsPage")
        ExportSettingsPage.resize(508, 186)
        self.gridLayout = QGridLayout(ExportSettingsPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pdf_page_count_limit = QSpinBox(ExportSettingsPage)
        self.pdf_page_count_limit.setObjectName(u"pdf_page_count_limit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pdf_page_count_limit.sizePolicy().hasHeightForWidth())
        self.pdf_page_count_limit.setSizePolicy(sizePolicy)
        self.pdf_page_count_limit.setMaximum(2000000000)

        self.gridLayout.addWidget(self.pdf_page_count_limit, 6, 1, 1, 2)

        self.export_path_browse_button = QPushButton(ExportSettingsPage)
        self.export_path_browse_button.setObjectName(u"export_path_browse_button")
        icon = QIcon(QIcon.fromTheme(u"document-open"))
        self.export_path_browse_button.setIcon(icon)

        self.gridLayout.addWidget(self.export_path_browse_button, 2, 2, 1, 1)

        self.landscape_workaround = QCheckBox(ExportSettingsPage)
        self.landscape_workaround.setObjectName(u"landscape_workaround")
        self.landscape_workaround.setProperty(u"wordWrap", True)

        self.gridLayout.addWidget(self.landscape_workaround, 4, 0, 1, 3)

        self.export_path = QLineEdit(ExportSettingsPage)
        self.export_path.setObjectName(u"export_path")
        self.export_path.setInputMethodHints(Qt.InputMethodHint.ImhNoAutoUppercase)
        self.export_path.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.export_path, 2, 1, 1, 1)

        self.export_path_label = QLabel(ExportSettingsPage)
        self.export_path_label.setObjectName(u"export_path_label")

        self.gridLayout.addWidget(self.export_path_label, 2, 0, 1, 1)

        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.vertical_spacer, 12, 0, 1, 3)

        self.png_background_color_label = QLabel(ExportSettingsPage)
        self.png_background_color_label.setObjectName(u"png_background_color_label")

        self.gridLayout.addWidget(self.png_background_color_label, 11, 0, 1, 1)

        self.pdf_page_count_limit_label = QLabel(ExportSettingsPage)
        self.pdf_page_count_limit_label.setObjectName(u"pdf_page_count_limit_label")

        self.gridLayout.addWidget(self.pdf_page_count_limit_label, 6, 0, 1, 1)

        self.line_2 = QFrame(ExportSettingsPage)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 8, 0, 1, 3)

        self.png_background_color_button = QPushButton(ExportSettingsPage)
        self.png_background_color_button.setObjectName(u"png_background_color_button")
        icon1 = QIcon(QIcon.fromTheme(u"color-picker"))
        self.png_background_color_button.setIcon(icon1)

        self.gridLayout.addWidget(self.png_background_color_button, 11, 2, 1, 1)

        self.line = QFrame(ExportSettingsPage)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 5, 0, 1, 3)

        self.png_background_color = QLabel(ExportSettingsPage)
        self.png_background_color.setObjectName(u"png_background_color")
        self.png_background_color.setText(u"")

        self.gridLayout.addWidget(self.png_background_color, 11, 1, 1, 1)

#if QT_CONFIG(shortcut)
        self.export_path_label.setBuddy(self.export_path)
        self.png_background_color_label.setBuddy(self.png_background_color_button)
        self.pdf_page_count_limit_label.setBuddy(self.pdf_page_count_limit)
        self.png_background_color.setBuddy(self.png_background_color_button)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.export_path, self.export_path_browse_button)
        QWidget.setTabOrder(self.export_path_browse_button, self.pdf_page_count_limit)

        self.retranslateUi(ExportSettingsPage)

        QMetaObject.connectSlotsByName(ExportSettingsPage)
    # setupUi

    def retranslateUi(self, ExportSettingsPage):
#if QT_CONFIG(tooltip)
        self.pdf_page_count_limit.setToolTip(QCoreApplication.translate("ExportSettingsPage", u"Automatically split PDF documents, if they get longer than this many pages.\n"
"Set to zero to disable splitting.\n"
"\n"
"\n"
"When printing PDFs using a USB flash drive directly connected to the printer,\n"
"the printer may refuse to print documents exceeding some arbitrary size limit.\n"
"To work around this limitation, you can enable this option,\n"
"and limit the number of pages per PDF. If the document has more pages,\n"
"it will be exported into multiple PDF documents automatically.", None))
#endif // QT_CONFIG(tooltip)
        self.pdf_page_count_limit.setSuffix(QCoreApplication.translate("ExportSettingsPage", u" pages", None))
#if QT_CONFIG(tooltip)
        self.export_path_browse_button.setToolTip(QCoreApplication.translate("ExportSettingsPage", u"Browse\u2026", None))
#endif // QT_CONFIG(tooltip)
        self.export_path_browse_button.setText("")
#if QT_CONFIG(tooltip)
        self.landscape_workaround.setToolTip(QCoreApplication.translate("ExportSettingsPage", u"If enabled, landscape documents are rotated by 90\u00b0 to portrait mode during export.\n"
"Enable this, if printing from PDFs in landscape format results in portrait printouts with cropped-off sides.\n"
"\n"
"Enabling this may cause the cut helper lines to flicker or not show in some PDF viewers.\n"
"So only enable this, if actually required.", None))
#endif // QT_CONFIG(tooltip)
        self.landscape_workaround.setText(QCoreApplication.translate("ExportSettingsPage", u"Enable landscape workaround: Rotate landscape pages by 90\u00b0", None))
#if QT_CONFIG(tooltip)
        self.export_path.setToolTip(QCoreApplication.translate("ExportSettingsPage", u"If set, use this as the default location for saving exported PDF documents.", None))
#endif // QT_CONFIG(tooltip)
        self.export_path.setPlaceholderText(QCoreApplication.translate("ExportSettingsPage", u"Path to a directory", None))
#if QT_CONFIG(tooltip)
        self.export_path_label.setToolTip(QCoreApplication.translate("ExportSettingsPage", u"If set, use this as the default location for saving exported PDF documents.", None))
#endif // QT_CONFIG(tooltip)
        self.export_path_label.setText(QCoreApplication.translate("ExportSettingsPage", u"Export path", None))
        self.png_background_color_label.setText(QCoreApplication.translate("ExportSettingsPage", u"PNG background color", None))
#if QT_CONFIG(tooltip)
        self.pdf_page_count_limit_label.setToolTip(QCoreApplication.translate("ExportSettingsPage", u"Automatically split PDF documents, if they get longer than this many pages.\n"
"Set to zero to disable splitting.\n"
"\n"
"\n"
"When printing PDFs using a USB flash drive directly connected to the printer,\n"
"the printer may refuse to print documents exceeding some arbitrary size limit.\n"
"To work around this limitation, you can enable this option,\n"
"and limit the number of pages per PDF. If the document has more pages,\n"
"it will be exported into multiple PDF documents automatically.", None))
#endif // QT_CONFIG(tooltip)
        self.pdf_page_count_limit_label.setText(QCoreApplication.translate("ExportSettingsPage", u"Split PDF documents longer than", None))
#if QT_CONFIG(tooltip)
        self.png_background_color_button.setToolTip(QCoreApplication.translate("ExportSettingsPage", u"Background color used for documents exported as PNG images.", None))
#endif // QT_CONFIG(tooltip)
        self.png_background_color_button.setText("")
        pass
    # retranslateUi

