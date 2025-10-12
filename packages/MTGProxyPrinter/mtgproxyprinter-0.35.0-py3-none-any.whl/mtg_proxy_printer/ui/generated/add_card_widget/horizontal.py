# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'horizontal.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QComboBox,
    QDialogButtonBox, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QListView, QSizePolicy, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_HorizontalAddCardWidget(object):
    def setupUi(self, HorizontalAddCardWidget):
        if not HorizontalAddCardWidget.objectName():
            HorizontalAddCardWidget.setObjectName(u"HorizontalAddCardWidget")
        HorizontalAddCardWidget.resize(1242, 292)
        self.gridLayout = QGridLayout(HorizontalAddCardWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.language_label = QLabel(HorizontalAddCardWidget)
        self.language_label.setObjectName(u"language_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.language_label.sizePolicy().hasHeightForWidth())
        self.language_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.language_label, 7, 5, 1, 1)

        self.card_name_box = QGroupBox(HorizontalAddCardWidget)
        self.card_name_box.setObjectName(u"card_name_box")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(7)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.card_name_box.sizePolicy().hasHeightForWidth())
        self.card_name_box.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.card_name_box)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.card_name_filter = QLineEdit(self.card_name_box)
        self.card_name_filter.setObjectName(u"card_name_filter")
        self.card_name_filter.setClearButtonEnabled(True)

        self.verticalLayout.addWidget(self.card_name_filter)

        self.card_name_list = QListView(self.card_name_box)
        self.card_name_list.setObjectName(u"card_name_list")
        self.card_name_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.card_name_list.setAlternatingRowColors(True)

        self.verticalLayout.addWidget(self.card_name_list)


        self.gridLayout.addWidget(self.card_name_box, 7, 1, 9, 1)

        self.set_name_box = QGroupBox(HorizontalAddCardWidget)
        self.set_name_box.setObjectName(u"set_name_box")
        self.set_name_box.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.set_name_box.sizePolicy().hasHeightForWidth())
        self.set_name_box.setSizePolicy(sizePolicy1)
        self.verticalLayout_2 = QVBoxLayout(self.set_name_box)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.set_name_filter = QLineEdit(self.set_name_box)
        self.set_name_filter.setObjectName(u"set_name_filter")
        self.set_name_filter.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.set_name_filter)

        self.set_name_list = QListView(self.set_name_box)
        self.set_name_list.setObjectName(u"set_name_list")
        self.set_name_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.set_name_list.setAlternatingRowColors(True)

        self.verticalLayout_2.addWidget(self.set_name_list)


        self.gridLayout.addWidget(self.set_name_box, 7, 2, 9, 1)

        self.collector_number_box = QGroupBox(HorizontalAddCardWidget)
        self.collector_number_box.setObjectName(u"collector_number_box")
        self.collector_number_box.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(5)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.collector_number_box.sizePolicy().hasHeightForWidth())
        self.collector_number_box.setSizePolicy(sizePolicy2)
        self.verticalLayout_3 = QVBoxLayout(self.collector_number_box)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.collector_number_list = QListView(self.collector_number_box)
        self.collector_number_list.setObjectName(u"collector_number_list")
        self.collector_number_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.collector_number_list.setAlternatingRowColors(True)

        self.verticalLayout_3.addWidget(self.collector_number_list)


        self.gridLayout.addWidget(self.collector_number_box, 7, 3, 9, 1)

        self.language_combo_box = QComboBox(HorizontalAddCardWidget)
        self.language_combo_box.setObjectName(u"language_combo_box")

        self.gridLayout.addWidget(self.language_combo_box, 8, 5, 1, 1)

        self.copies_label = QLabel(HorizontalAddCardWidget)
        self.copies_label.setObjectName(u"copies_label")
        sizePolicy.setHeightForWidth(self.copies_label.sizePolicy().hasHeightForWidth())
        self.copies_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.copies_label, 9, 5, 1, 1)

        self.copies_input = QSpinBox(HorizontalAddCardWidget)
        self.copies_input.setObjectName(u"copies_input")
        self.copies_input.setMinimum(1)

        self.gridLayout.addWidget(self.copies_input, 10, 5, 1, 1)

        self.button_box = QDialogButtonBox(HorizontalAddCardWidget)
        self.button_box.setObjectName(u"button_box")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy3)
        self.button_box.setOrientation(Qt.Orientation.Vertical)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Reset)

        self.gridLayout.addWidget(self.button_box, 11, 5, 5, 1)

#if QT_CONFIG(shortcut)
        self.language_label.setBuddy(self.language_combo_box)
        self.copies_label.setBuddy(self.copies_input)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.card_name_filter, self.card_name_list)
        QWidget.setTabOrder(self.card_name_list, self.set_name_filter)
        QWidget.setTabOrder(self.set_name_filter, self.set_name_list)
        QWidget.setTabOrder(self.set_name_list, self.collector_number_list)
        QWidget.setTabOrder(self.collector_number_list, self.language_combo_box)
        QWidget.setTabOrder(self.language_combo_box, self.copies_input)

        self.retranslateUi(HorizontalAddCardWidget)

        QMetaObject.connectSlotsByName(HorizontalAddCardWidget)
    # setupUi

    def retranslateUi(self, HorizontalAddCardWidget):
        self.language_label.setText(QCoreApplication.translate("HorizontalAddCardWidget", u"Language:", None))
        self.card_name_box.setTitle(QCoreApplication.translate("HorizontalAddCardWidget", u"Card Name", None))
#if QT_CONFIG(tooltip)
        self.card_name_filter.setToolTip(QCoreApplication.translate("HorizontalAddCardWidget", u"Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.", None))
#endif // QT_CONFIG(tooltip)
        self.card_name_filter.setPlaceholderText(QCoreApplication.translate("HorizontalAddCardWidget", u"Filter card names", None))
#if QT_CONFIG(tooltip)
        self.card_name_list.setToolTip(QCoreApplication.translate("HorizontalAddCardWidget", u"The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.set_name_box.setToolTip(QCoreApplication.translate("HorizontalAddCardWidget", u"The sets in which the currently selected card was printed.", None))
#endif // QT_CONFIG(tooltip)
        self.set_name_box.setTitle(QCoreApplication.translate("HorizontalAddCardWidget", u"Set", None))
        self.set_name_filter.setPlaceholderText(QCoreApplication.translate("HorizontalAddCardWidget", u"Filter set names", None))
        self.collector_number_box.setTitle(QCoreApplication.translate("HorizontalAddCardWidget", u"Collector Number", None))
        self.copies_label.setText(QCoreApplication.translate("HorizontalAddCardWidget", u"Copies:", None))
        pass
    # retranslateUi

