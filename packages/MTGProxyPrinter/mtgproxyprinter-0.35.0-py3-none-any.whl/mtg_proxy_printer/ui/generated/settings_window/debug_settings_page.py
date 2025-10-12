# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'debug_settings_page.ui'
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
    QGridLayout, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_DebugSettingsPage(object):
    def setupUi(self, DebugSettingsPage):
        if not DebugSettingsPage.objectName():
            DebugSettingsPage.setObjectName(u"DebugSettingsPage")
        DebugSettingsPage.resize(446, 291)
        self.gridLayout = QGridLayout(DebugSettingsPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.open_debug_log_location = QPushButton(DebugSettingsPage)
        self.open_debug_log_location.setObjectName(u"open_debug_log_location")
        icon = QIcon(QIcon.fromTheme(u"document-open"))
        self.open_debug_log_location.setIcon(icon)

        self.gridLayout.addWidget(self.open_debug_log_location, 8, 1, 1, 2)

        self.enable_write_log_file = QCheckBox(DebugSettingsPage)
        self.enable_write_log_file.setObjectName(u"enable_write_log_file")

        self.gridLayout.addWidget(self.enable_write_log_file, 5, 0, 1, 3)

        self.enable_cutelog_integration = QCheckBox(DebugSettingsPage)
        self.enable_cutelog_integration.setObjectName(u"enable_cutelog_integration")

        self.gridLayout.addWidget(self.enable_cutelog_integration, 4, 0, 1, 1)

        self.debug_download_card_data_as_file = QPushButton(DebugSettingsPage)
        self.debug_download_card_data_as_file.setObjectName(u"debug_download_card_data_as_file")
        icon1 = QIcon(QIcon.fromTheme(u"edit-download"))
        self.debug_download_card_data_as_file.setIcon(icon1)

        self.gridLayout.addWidget(self.debug_download_card_data_as_file, 9, 1, 1, 2)

        self.debug_settings_header_line = QFrame(DebugSettingsPage)
        self.debug_settings_header_line.setObjectName(u"debug_settings_header_line")
        self.debug_settings_header_line.setFrameShape(QFrame.Shape.HLine)
        self.debug_settings_header_line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.debug_settings_header_line, 1, 0, 1, 2)

        self.log_level_label = QLabel(DebugSettingsPage)
        self.log_level_label.setObjectName(u"log_level_label")

        self.gridLayout.addWidget(self.log_level_label, 7, 0, 1, 1)

        self.log_level_combo_box = QComboBox(DebugSettingsPage)
        self.log_level_combo_box.setObjectName(u"log_level_combo_box")

        self.gridLayout.addWidget(self.log_level_combo_box, 7, 1, 1, 2)

        self.debug_settings_headerlabel = QLabel(DebugSettingsPage)
        self.debug_settings_headerlabel.setObjectName(u"debug_settings_headerlabel")

        self.gridLayout.addWidget(self.debug_settings_headerlabel, 0, 0, 1, 2)

        self.spacer = QSpacerItem(20, 32, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.spacer, 11, 0, 1, 2)

        self.debug_import_card_data_from_file = QPushButton(DebugSettingsPage)
        self.debug_import_card_data_from_file.setObjectName(u"debug_import_card_data_from_file")
        icon2 = QIcon(QIcon.fromTheme(u"document-import"))
        self.debug_import_card_data_from_file.setIcon(icon2)

        self.gridLayout.addWidget(self.debug_import_card_data_from_file, 10, 1, 1, 2)

        self.open_cutelog_website_button = QPushButton(DebugSettingsPage)
        self.open_cutelog_website_button.setObjectName(u"open_cutelog_website_button")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.open_cutelog_website_button.sizePolicy().hasHeightForWidth())
        self.open_cutelog_website_button.setSizePolicy(sizePolicy)
        self.open_cutelog_website_button.setText(u"")
        icon3 = QIcon(QIcon.fromTheme(u"globe"))
        self.open_cutelog_website_button.setIcon(icon3)

        self.gridLayout.addWidget(self.open_cutelog_website_button, 4, 2, 1, 1)

#if QT_CONFIG(shortcut)
        self.log_level_label.setBuddy(self.log_level_combo_box)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.enable_cutelog_integration, self.open_cutelog_website_button)
        QWidget.setTabOrder(self.open_cutelog_website_button, self.enable_write_log_file)
        QWidget.setTabOrder(self.enable_write_log_file, self.log_level_combo_box)
        QWidget.setTabOrder(self.log_level_combo_box, self.open_debug_log_location)
        QWidget.setTabOrder(self.open_debug_log_location, self.debug_download_card_data_as_file)
        QWidget.setTabOrder(self.debug_download_card_data_as_file, self.debug_import_card_data_from_file)

        self.retranslateUi(DebugSettingsPage)

        QMetaObject.connectSlotsByName(DebugSettingsPage)
    # setupUi

    def retranslateUi(self, DebugSettingsPage):
        self.open_debug_log_location.setText(QCoreApplication.translate("DebugSettingsPage", u"Open debug log directory", None))
        self.enable_write_log_file.setText(QCoreApplication.translate("DebugSettingsPage", u"Enable writing a log file to disk", None))
#if QT_CONFIG(tooltip)
        self.enable_cutelog_integration.setToolTip(QCoreApplication.translate("DebugSettingsPage", u"Cutelog is a live log event viewer that can be used to monitor events in real-time.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.enable_cutelog_integration.setWhatsThis(QCoreApplication.translate("DebugSettingsPage", u"<html><head/><body><p>See <a href=\"https://github.com/busimus/cutelog\"><span style=\" text-decoration: underline; color:#2980b9;\">https://github.com/busimus/cutelog</span></a> for details about Cutelog.</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.enable_cutelog_integration.setText(QCoreApplication.translate("DebugSettingsPage", u"Enable Cutelog integration", None))
        self.debug_download_card_data_as_file.setText(QCoreApplication.translate("DebugSettingsPage", u"Download card data as file", None))
        self.log_level_label.setText(QCoreApplication.translate("DebugSettingsPage", u"Event severity that gets logged to file:", None))
#if QT_CONFIG(tooltip)
        self.log_level_combo_box.setToolTip(QCoreApplication.translate("DebugSettingsPage", u"Only write events with the given severity level and higher to the log file.", None))
#endif // QT_CONFIG(tooltip)
        self.debug_settings_headerlabel.setText(QCoreApplication.translate("DebugSettingsPage", u"Debug settings (Changing these require an application restart)", None))
        self.debug_import_card_data_from_file.setText(QCoreApplication.translate("DebugSettingsPage", u"Import card data from file", None))
#if QT_CONFIG(tooltip)
        self.open_cutelog_website_button.setToolTip(QCoreApplication.translate("DebugSettingsPage", u"Open the Cutelog homepage", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

