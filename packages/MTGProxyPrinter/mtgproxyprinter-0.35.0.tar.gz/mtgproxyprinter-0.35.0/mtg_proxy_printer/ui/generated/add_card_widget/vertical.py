# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vertical.ui'
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

class Ui_VerticalAddCardWidget(object):
    def setupUi(self, VerticalAddCardWidget):
        if not VerticalAddCardWidget.objectName():
            VerticalAddCardWidget.setObjectName(u"VerticalAddCardWidget")
        VerticalAddCardWidget.resize(349, 715)
        self.gridLayout = QGridLayout(VerticalAddCardWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.set_name_box = QGroupBox(VerticalAddCardWidget)
        self.set_name_box.setObjectName(u"set_name_box")
        self.set_name_box.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(7)
        sizePolicy.setHeightForWidth(self.set_name_box.sizePolicy().hasHeightForWidth())
        self.set_name_box.setSizePolicy(sizePolicy)
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


        self.gridLayout.addWidget(self.set_name_box, 3, 0, 1, 3)

        self.collector_number_box = QGroupBox(VerticalAddCardWidget)
        self.collector_number_box.setObjectName(u"collector_number_box")
        self.collector_number_box.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(2)
        sizePolicy1.setHeightForWidth(self.collector_number_box.sizePolicy().hasHeightForWidth())
        self.collector_number_box.setSizePolicy(sizePolicy1)
        self.verticalLayout_3 = QVBoxLayout(self.collector_number_box)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.collector_number_list = QListView(self.collector_number_box)
        self.collector_number_list.setObjectName(u"collector_number_list")
        self.collector_number_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.collector_number_list.setAlternatingRowColors(True)

        self.verticalLayout_3.addWidget(self.collector_number_list)


        self.gridLayout.addWidget(self.collector_number_box, 10, 0, 1, 3)

        self.card_name_box = QGroupBox(VerticalAddCardWidget)
        self.card_name_box.setObjectName(u"card_name_box")
        sizePolicy.setHeightForWidth(self.card_name_box.sizePolicy().hasHeightForWidth())
        self.card_name_box.setSizePolicy(sizePolicy)
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


        self.gridLayout.addWidget(self.card_name_box, 2, 0, 1, 3)

        self.language_combo_box = QComboBox(VerticalAddCardWidget)
        self.language_combo_box.setObjectName(u"language_combo_box")

        self.gridLayout.addWidget(self.language_combo_box, 0, 1, 1, 2)

        self.language_label = QLabel(VerticalAddCardWidget)
        self.language_label.setObjectName(u"language_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.language_label.sizePolicy().hasHeightForWidth())
        self.language_label.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.language_label, 0, 0, 1, 1)

        self.copies_label = QLabel(VerticalAddCardWidget)
        self.copies_label.setObjectName(u"copies_label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.copies_label.sizePolicy().hasHeightForWidth())
        self.copies_label.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.copies_label, 11, 0, 1, 1)

        self.copies_input = QSpinBox(VerticalAddCardWidget)
        self.copies_input.setObjectName(u"copies_input")
        self.copies_input.setMinimum(1)

        self.gridLayout.addWidget(self.copies_input, 11, 1, 1, 2)

        self.button_box = QDialogButtonBox(VerticalAddCardWidget)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Reset)

        self.gridLayout.addWidget(self.button_box, 12, 0, 1, 3)

#if QT_CONFIG(shortcut)
        self.language_label.setBuddy(self.language_combo_box)
        self.copies_label.setBuddy(self.copies_input)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.language_combo_box, self.card_name_filter)
        QWidget.setTabOrder(self.card_name_filter, self.card_name_list)
        QWidget.setTabOrder(self.card_name_list, self.set_name_filter)
        QWidget.setTabOrder(self.set_name_filter, self.set_name_list)
        QWidget.setTabOrder(self.set_name_list, self.collector_number_list)
        QWidget.setTabOrder(self.collector_number_list, self.copies_input)

        self.retranslateUi(VerticalAddCardWidget)

        QMetaObject.connectSlotsByName(VerticalAddCardWidget)
    # setupUi

    def retranslateUi(self, VerticalAddCardWidget):
#if QT_CONFIG(tooltip)
        self.set_name_box.setToolTip(QCoreApplication.translate("VerticalAddCardWidget", u"The sets in which the currently selected card was printed.", None))
#endif // QT_CONFIG(tooltip)
        self.set_name_box.setTitle(QCoreApplication.translate("VerticalAddCardWidget", u"Set", None))
        self.set_name_filter.setPlaceholderText(QCoreApplication.translate("VerticalAddCardWidget", u"Filter set names", None))
        self.collector_number_box.setTitle(QCoreApplication.translate("VerticalAddCardWidget", u"Collector Number", None))
        self.card_name_box.setTitle(QCoreApplication.translate("VerticalAddCardWidget", u"Card Name", None))
#if QT_CONFIG(tooltip)
        self.card_name_filter.setToolTip(QCoreApplication.translate("VerticalAddCardWidget", u"Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.", None))
#endif // QT_CONFIG(tooltip)
        self.card_name_filter.setPlaceholderText(QCoreApplication.translate("VerticalAddCardWidget", u"Filter card names", None))
#if QT_CONFIG(tooltip)
        self.card_name_list.setToolTip(QCoreApplication.translate("VerticalAddCardWidget", u"The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.", None))
#endif // QT_CONFIG(tooltip)
        self.language_label.setText(QCoreApplication.translate("VerticalAddCardWidget", u"Language:", None))
        self.copies_label.setText(QCoreApplication.translate("VerticalAddCardWidget", u"Copies:", None))
        pass
    # retranslateUi

