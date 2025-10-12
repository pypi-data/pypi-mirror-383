# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'custom_card_import_dialog.ui'
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
    QGridLayout, QHeaderView, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QWidget)

from mtg_proxy_printer.ui.card_list_table_view import CardListTableView

class Ui_CustomCardImportDialog(object):
    def setupUi(self, CustomCardImportDialog):
        if not CustomCardImportDialog.objectName():
            CustomCardImportDialog.setObjectName(u"CustomCardImportDialog")
        CustomCardImportDialog.resize(900, 500)
        self.gridLayout = QGridLayout(CustomCardImportDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.set_copies_to = QPushButton(CustomCardImportDialog)
        self.set_copies_to.setObjectName(u"set_copies_to")
        icon = QIcon(QIcon.fromTheme(u"document-edit"))
        self.set_copies_to.setIcon(icon)

        self.gridLayout.addWidget(self.set_copies_to, 6, 3, 1, 1)

        self.card_copies = QSpinBox(CustomCardImportDialog)
        self.card_copies.setObjectName(u"card_copies")
        self.card_copies.setMinimum(1)

        self.gridLayout.addWidget(self.card_copies, 6, 4, 1, 1)

        self.card_table = CardListTableView(CustomCardImportDialog)
        self.card_table.setObjectName(u"card_table")

        self.gridLayout.addWidget(self.card_table, 1, 2, 11, 1)

        self.remove_selected = QPushButton(CustomCardImportDialog)
        self.remove_selected.setObjectName(u"remove_selected")
        icon1 = QIcon(QIcon.fromTheme(u"edit-delete"))
        self.remove_selected.setIcon(icon1)

        self.gridLayout.addWidget(self.remove_selected, 3, 3, 1, 2)

        self.add_cards = QPushButton(CustomCardImportDialog)
        self.add_cards.setObjectName(u"add_cards")
        icon2 = QIcon(QIcon.fromTheme(u"document-import"))
        self.add_cards.setIcon(icon2)

        self.gridLayout.addWidget(self.add_cards, 2, 3, 1, 2)

        self.button_box = QDialogButtonBox(CustomCardImportDialog)
        self.button_box.setObjectName(u"button_box")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_box.sizePolicy().hasHeightForWidth())
        self.button_box.setSizePolicy(sizePolicy)
        self.button_box.setOrientation(Qt.Orientation.Vertical)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.button_box, 8, 3, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 7, 3, 1, 1)


        self.retranslateUi(CustomCardImportDialog)
        self.button_box.accepted.connect(CustomCardImportDialog.accept)
        self.button_box.rejected.connect(CustomCardImportDialog.reject)

        QMetaObject.connectSlotsByName(CustomCardImportDialog)
    # setupUi

    def retranslateUi(self, CustomCardImportDialog):
        CustomCardImportDialog.setWindowTitle(QCoreApplication.translate("CustomCardImportDialog", u"Import custom cards", None))
        self.set_copies_to.setText(QCoreApplication.translate("CustomCardImportDialog", u"Set Copies to \u2026", None))
        self.remove_selected.setText(QCoreApplication.translate("CustomCardImportDialog", u"Remove selected", None))
        self.add_cards.setText(QCoreApplication.translate("CustomCardImportDialog", u"Load images", None))
    # retranslateUi

