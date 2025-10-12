# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QTabWidget, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(800, 600)
        AboutDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tab_widget = QTabWidget(AboutDialog)
        self.tab_widget.setObjectName(u"tab_widget")
        self.tab_about = QWidget()
        self.tab_about.setObjectName(u"tab_about")
        self.tab_about_layout = QGridLayout(self.tab_about)
        self.tab_about_layout.setObjectName(u"tab_about_layout")
        self.mtg_proxy_printer_version_header_label = QLabel(self.tab_about)
        self.mtg_proxy_printer_version_header_label.setObjectName(u"mtg_proxy_printer_version_header_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mtg_proxy_printer_version_header_label.sizePolicy().hasHeightForWidth())
        self.mtg_proxy_printer_version_header_label.setSizePolicy(sizePolicy)
        self.mtg_proxy_printer_version_header_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.tab_about_layout.addWidget(self.mtg_proxy_printer_version_header_label, 2, 0, 1, 1)

        self.last_database_update_header_label = QLabel(self.tab_about)
        self.last_database_update_header_label.setObjectName(u"last_database_update_header_label")
        sizePolicy.setHeightForWidth(self.last_database_update_header_label.sizePolicy().hasHeightForWidth())
        self.last_database_update_header_label.setSizePolicy(sizePolicy)

        self.tab_about_layout.addWidget(self.last_database_update_header_label, 6, 0, 1, 1)

        self.mtg_proxy_printer_version_label = QLabel(self.tab_about)
        self.mtg_proxy_printer_version_label.setObjectName(u"mtg_proxy_printer_version_label")
        self.mtg_proxy_printer_version_label.setText(u"")
        self.mtg_proxy_printer_version_label.setTextFormat(Qt.TextFormat.PlainText)
        self.mtg_proxy_printer_version_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.mtg_proxy_printer_version_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.tab_about_layout.addWidget(self.mtg_proxy_printer_version_label, 2, 1, 1, 2)

        self.python_version_header_label = QLabel(self.tab_about)
        self.python_version_header_label.setObjectName(u"python_version_header_label")
        sizePolicy.setHeightForWidth(self.python_version_header_label.sizePolicy().hasHeightForWidth())
        self.python_version_header_label.setSizePolicy(sizePolicy)

        self.tab_about_layout.addWidget(self.python_version_header_label, 5, 0, 1, 1)

        self.last_database_update_label = QLabel(self.tab_about)
        self.last_database_update_label.setObjectName(u"last_database_update_label")
#if QT_CONFIG(tooltip)
        self.last_database_update_label.setToolTip(u"Timestamp of the last card data update.\"")
#endif // QT_CONFIG(tooltip)
        self.last_database_update_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.tab_about_layout.addWidget(self.last_database_update_label, 6, 1, 1, 2)

        self.python_version_label = QLabel(self.tab_about)
        self.python_version_label.setObjectName(u"python_version_label")
        self.python_version_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.tab_about_layout.addWidget(self.python_version_label, 5, 1, 1, 2)

        self.about_text = QTextBrowser(self.tab_about)
        self.about_text.setObjectName(u"about_text")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.about_text.sizePolicy().hasHeightForWidth())
        self.about_text.setSizePolicy(sizePolicy1)
        self.about_text.setOpenExternalLinks(True)

        self.tab_about_layout.addWidget(self.about_text, 1, 0, 1, 3)

        self.about_header_layout = QHBoxLayout()
        self.about_header_layout.setObjectName(u"about_header_layout")
        self.mtg_proxy_printer_icon = QLabel(self.tab_about)
        self.mtg_proxy_printer_icon.setObjectName(u"mtg_proxy_printer_icon")
        self.mtg_proxy_printer_icon.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.mtg_proxy_printer_icon.sizePolicy().hasHeightForWidth())
        self.mtg_proxy_printer_icon.setSizePolicy(sizePolicy2)
        self.mtg_proxy_printer_icon.setMinimumSize(QSize(64, 64))

        self.about_header_layout.addWidget(self.mtg_proxy_printer_icon)

        self.mtg_proxy_printer_name = QLabel(self.tab_about)
        self.mtg_proxy_printer_name.setObjectName(u"mtg_proxy_printer_name")
        self.mtg_proxy_printer_name.setMaximumSize(QSize(16777215, 64))
        self.mtg_proxy_printer_name.setText(u"<html><head/><body><p><span style=\" font-size:xx-large; font-weight:600;\">MTGProxyPrinter</span></p><p><br/></p></body></html>")
        self.mtg_proxy_printer_name.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.about_header_layout.addWidget(self.mtg_proxy_printer_name)

        self.about_header_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.about_header_layout.addItem(self.about_header_spacer)


        self.tab_about_layout.addLayout(self.about_header_layout, 0, 0, 1, 3)

        self.tab_widget.addTab(self.tab_about, "")
        self.changelog_text_browser = QTextBrowser()
        self.changelog_text_browser.setObjectName(u"changelog_text_browser")
        self.changelog_text_browser.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.changelog_text_browser.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextBrowserInteraction|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)
        self.changelog_text_browser.setOpenExternalLinks(True)
        self.tab_widget.addTab(self.changelog_text_browser, "")
        self.license_text_browser = QTextBrowser()
        self.license_text_browser.setObjectName(u"license_text_browser")
        self.license_text_browser.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.license_text_browser.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextBrowserInteraction|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)
        self.license_text_browser.setOpenExternalLinks(True)
        self.tab_widget.addTab(self.license_text_browser, "")
        self.third_party_license_text_browser = QTextBrowser()
        self.third_party_license_text_browser.setObjectName(u"third_party_license_text_browser")
        self.third_party_license_text_browser.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextBrowserInteraction|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)
        self.third_party_license_text_browser.setOpenExternalLinks(True)
        self.tab_widget.addTab(self.third_party_license_text_browser, "")

        self.verticalLayout.addWidget(self.tab_widget)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)
        self.buttonBox.accepted.connect(AboutDialog.accept)
        self.buttonBox.rejected.connect(AboutDialog.reject)

        self.tab_widget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About MTGProxyPrinter", None))
        self.mtg_proxy_printer_version_header_label.setText(QCoreApplication.translate("AboutDialog", u"Application Version:", None))
        self.last_database_update_header_label.setText(QCoreApplication.translate("AboutDialog", u"Last card update:", None))
#if QT_CONFIG(tooltip)
        self.mtg_proxy_printer_version_label.setToolTip(QCoreApplication.translate("AboutDialog", u"Application version", None))
#endif // QT_CONFIG(tooltip)
        self.python_version_header_label.setText(QCoreApplication.translate("AboutDialog", u"Python Version:", None))
        self.last_database_update_label.setText("")
#if QT_CONFIG(tooltip)
        self.python_version_label.setToolTip(QCoreApplication.translate("AboutDialog", u"Python runtime version", None))
#endif // QT_CONFIG(tooltip)
        self.about_text.setMarkdown(QCoreApplication.translate("AboutDialog", u"{application_name} allows printing\n"
"[Magic: The Gathering](https://magic.wizards.com/) cards for play-testing\n"
"purposes.\n"
"\n"
"{application_name} is unofficial Fan Content permitted under the\n"
"[Fan Content Policy](https://company.wizards.com/fancontentpolicy). Not\n"
"approved/endorsed by Wizards. Portions of the materials used are property of\n"
"Wizards of the Coast. \u00a9[Wizards of the Coast LLC](https://company.wizards.com/).\n"
"\n"
"Under the Fan Content Policy, you may neither sell the data downloaded using\n"
"this program, including the card database content and downloaded card images,\n"
"nor any documents created, both in digital and physical form.\n"
"\n"
"Project Website: [{application_name} home page]({application_home_page})\n"
"\n"
"Application icon by [islanders2013](https://www.reddit.com/user/islanders2013/)\n"
"\n"
"", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_about), QCoreApplication.translate("AboutDialog", u"About", None))
        self.changelog_text_browser.setDocumentTitle(QCoreApplication.translate("AboutDialog", u"Changelog", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.changelog_text_browser), QCoreApplication.translate("AboutDialog", u"Changelog", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.license_text_browser), QCoreApplication.translate("AboutDialog", u"License", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.third_party_license_text_browser), QCoreApplication.translate("AboutDialog", u"Third party licenses", None))
    # retranslateUi

