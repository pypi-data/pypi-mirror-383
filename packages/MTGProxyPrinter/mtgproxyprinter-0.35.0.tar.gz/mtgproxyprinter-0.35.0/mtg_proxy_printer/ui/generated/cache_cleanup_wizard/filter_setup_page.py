# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filter_setup_page.ui'
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
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget, QWizardPage)

class Ui_FilterSetupPage(object):
    def setupUi(self, FilterSetupPage):
        if not FilterSetupPage.objectName():
            FilterSetupPage.setObjectName(u"FilterSetupPage")
        FilterSetupPage.resize(417, 186)
        self.verticalLayout = QVBoxLayout(FilterSetupPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.delete_everything_checkbox = QCheckBox(FilterSetupPage)
        self.delete_everything_checkbox.setObjectName(u"delete_everything_checkbox")
        icon = QIcon(QIcon.fromTheme(u"edit-delete"))
        self.delete_everything_checkbox.setIcon(icon)

        self.verticalLayout.addWidget(self.delete_everything_checkbox)

        self.individual_filter_group = QGroupBox(FilterSetupPage)
        self.individual_filter_group.setObjectName(u"individual_filter_group")
        self.gridLayout_2 = QGridLayout(self.individual_filter_group)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.count_filter_enabled_checkbox = QCheckBox(self.individual_filter_group)
        self.count_filter_enabled_checkbox.setObjectName(u"count_filter_enabled_checkbox")

        self.gridLayout_2.addWidget(self.count_filter_enabled_checkbox, 1, 0, 1, 1)

        self.time_filter_enabled_checkbox = QCheckBox(self.individual_filter_group)
        self.time_filter_enabled_checkbox.setObjectName(u"time_filter_enabled_checkbox")

        self.gridLayout_2.addWidget(self.time_filter_enabled_checkbox, 0, 0, 1, 1)

        self.time_filter_value_spinbox = QSpinBox(self.individual_filter_group)
        self.time_filter_value_spinbox.setObjectName(u"time_filter_value_spinbox")
        self.time_filter_value_spinbox.setEnabled(False)
        self.time_filter_value_spinbox.setMaximum(10000)
        self.time_filter_value_spinbox.setValue(90)

        self.gridLayout_2.addWidget(self.time_filter_value_spinbox, 0, 1, 1, 1)

        self.count_filter_value_spinbox = QSpinBox(self.individual_filter_group)
        self.count_filter_value_spinbox.setObjectName(u"count_filter_value_spinbox")
        self.count_filter_value_spinbox.setEnabled(False)
        self.count_filter_value_spinbox.setMinimum(1)
        self.count_filter_value_spinbox.setMaximum(10000)

        self.gridLayout_2.addWidget(self.count_filter_value_spinbox, 1, 1, 1, 1)

        self.remove_unknown_cards_checkbox = QCheckBox(self.individual_filter_group)
        self.remove_unknown_cards_checkbox.setObjectName(u"remove_unknown_cards_checkbox")

        self.gridLayout_2.addWidget(self.remove_unknown_cards_checkbox, 2, 0, 1, 2)


        self.verticalLayout.addWidget(self.individual_filter_group)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        QWidget.setTabOrder(self.delete_everything_checkbox, self.time_filter_enabled_checkbox)
        QWidget.setTabOrder(self.time_filter_enabled_checkbox, self.time_filter_value_spinbox)
        QWidget.setTabOrder(self.time_filter_value_spinbox, self.count_filter_enabled_checkbox)
        QWidget.setTabOrder(self.count_filter_enabled_checkbox, self.count_filter_value_spinbox)
        QWidget.setTabOrder(self.count_filter_value_spinbox, self.remove_unknown_cards_checkbox)

        self.retranslateUi(FilterSetupPage)
        self.time_filter_enabled_checkbox.toggled.connect(self.time_filter_value_spinbox.setEnabled)
        self.count_filter_enabled_checkbox.toggled.connect(self.count_filter_value_spinbox.setEnabled)
        self.delete_everything_checkbox.toggled.connect(self.individual_filter_group.setDisabled)

        QMetaObject.connectSlotsByName(FilterSetupPage)
    # setupUi

    def retranslateUi(self, FilterSetupPage):
        FilterSetupPage.setTitle(QCoreApplication.translate("FilterSetupPage", u"Cleanup locally stored card images", None))
        FilterSetupPage.setSubTitle(QCoreApplication.translate("FilterSetupPage", u"This wizard can be used to remove unwanted card images currently stored on your computer. You can enable automatic cleanup conditions below, to preselect images for removal.", None))
        self.delete_everything_checkbox.setText(QCoreApplication.translate("FilterSetupPage", u"Delete everything", None))
#if QT_CONFIG(tooltip)
        self.individual_filter_group.setToolTip(QCoreApplication.translate("FilterSetupPage", u"Select images for removal based on any matching criterion.", None))
#endif // QT_CONFIG(tooltip)
        self.individual_filter_group.setTitle(QCoreApplication.translate("FilterSetupPage", u"Select images for deletion, that are \u2026", None))
        self.count_filter_enabled_checkbox.setText(QCoreApplication.translate("FilterSetupPage", u"Used in prints and PDFs less often than:", None))
        self.time_filter_enabled_checkbox.setText(QCoreApplication.translate("FilterSetupPage", u"Not used in prints for:", None))
        self.time_filter_value_spinbox.setSuffix(QCoreApplication.translate("FilterSetupPage", u" days", None))
        self.count_filter_value_spinbox.setSuffix(QCoreApplication.translate("FilterSetupPage", u" times", None))
#if QT_CONFIG(tooltip)
        self.remove_unknown_cards_checkbox.setToolTip(QCoreApplication.translate("FilterSetupPage", u"Card images may become unknown, if printings are removed by Scryfall.\n"
"This filter also applies to cards and printings hidden by a card filter in the settings.\n"
"For example, if you downloaded images of silver-bordered cards and then configured the program to hide those,\n"
"all these images become hidden and will be removed.", None))
#endif // QT_CONFIG(tooltip)
        self.remove_unknown_cards_checkbox.setText(QCoreApplication.translate("FilterSetupPage", u"Unknown or belong to hidden printings", None))
    # retranslateUi

