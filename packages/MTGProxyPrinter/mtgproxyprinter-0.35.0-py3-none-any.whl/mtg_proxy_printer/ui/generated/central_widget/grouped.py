# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'grouped.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHeaderView,
    QLabel, QListView, QPushButton, QSizePolicy,
    QWidget)

from mtg_proxy_printer.ui.add_card import HorizontalAddCardWidget
from mtg_proxy_printer.ui.page_card_table_view import PageCardTableView
from mtg_proxy_printer.ui.page_renderer import PageRenderer

class Ui_GroupedCentralWidget(object):
    def setupUi(self, GroupedCentralWidget):
        if not GroupedCentralWidget.objectName():
            GroupedCentralWidget.setObjectName(u"GroupedCentralWidget")
        GroupedCentralWidget.resize(792, 273)
        self.gridLayout = QGridLayout(GroupedCentralWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.add_card_widget_label = QLabel(GroupedCentralWidget)
        self.add_card_widget_label.setObjectName(u"add_card_widget_label")

        self.gridLayout.addWidget(self.add_card_widget_label, 0, 2, 1, 2)

        self.add_card_widget = HorizontalAddCardWidget(GroupedCentralWidget)
        self.add_card_widget.setObjectName(u"add_card_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(7)
        sizePolicy.setVerticalStretch(6)
        sizePolicy.setHeightForWidth(self.add_card_widget.sizePolicy().hasHeightForWidth())
        self.add_card_widget.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.add_card_widget, 1, 2, 2, 2)

        self.document_view = QListView(GroupedCentralWidget)
        self.document_view.setObjectName(u"document_view")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(3)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.document_view.sizePolicy().hasHeightForWidth())
        self.document_view.setSizePolicy(sizePolicy1)
        self.document_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.document_view.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.document_view.setAlternatingRowColors(True)
        self.document_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.document_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.gridLayout.addWidget(self.document_view, 1, 0, 7, 2)

        self.document_view_label = QLabel(GroupedCentralWidget)
        self.document_view_label.setObjectName(u"document_view_label")

        self.gridLayout.addWidget(self.document_view_label, 0, 0, 1, 2)

        self.page_move_down = QPushButton(GroupedCentralWidget)
        self.page_move_down.setObjectName(u"page_move_down")
        self.page_move_down.setEnabled(False)
        icon = QIcon(QIcon.fromTheme(u"arrow-down"))
        self.page_move_down.setIcon(icon)

        self.gridLayout.addWidget(self.page_move_down, 8, 1, 1, 1)

        self.page_move_up = QPushButton(GroupedCentralWidget)
        self.page_move_up.setObjectName(u"page_move_up")
        self.page_move_up.setEnabled(False)
        icon1 = QIcon(QIcon.fromTheme(u"arrow-up"))
        self.page_move_up.setIcon(icon1)

        self.gridLayout.addWidget(self.page_move_up, 8, 0, 1, 1)

        self.delete_selected_images_button = QPushButton(GroupedCentralWidget)
        self.delete_selected_images_button.setObjectName(u"delete_selected_images_button")
        self.delete_selected_images_button.setEnabled(False)
        icon2 = QIcon(QIcon.fromTheme(u"edit-delete"))
        self.delete_selected_images_button.setIcon(icon2)

        self.gridLayout.addWidget(self.delete_selected_images_button, 8, 2, 1, 1)

        self.page_renderer = PageRenderer(GroupedCentralWidget)
        self.page_renderer.setObjectName(u"page_renderer")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(7)
        sizePolicy2.setVerticalStretch(10)
        sizePolicy2.setHeightForWidth(self.page_renderer.sizePolicy().hasHeightForWidth())
        self.page_renderer.setSizePolicy(sizePolicy2)
        self.page_renderer.setAcceptDrops(False)
        self.page_renderer.setRenderHints(QPainter.RenderHint.Antialiasing)

        self.gridLayout.addWidget(self.page_renderer, 5, 3, 4, 1)

        self.page_card_table_view = PageCardTableView(GroupedCentralWidget)
        self.page_card_table_view.setObjectName(u"page_card_table_view")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(8)
        sizePolicy3.setVerticalStretch(10)
        sizePolicy3.setHeightForWidth(self.page_card_table_view.sizePolicy().hasHeightForWidth())
        self.page_card_table_view.setSizePolicy(sizePolicy3)
        self.page_card_table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.page_card_table_view.setLineWidth(0)
        self.page_card_table_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.page_card_table_view.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.page_card_table_view.setAlternatingRowColors(True)
        self.page_card_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.page_card_table_view.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.page_card_table_view, 5, 2, 3, 1)


        self.retranslateUi(GroupedCentralWidget)

        QMetaObject.connectSlotsByName(GroupedCentralWidget)
    # setupUi

    def retranslateUi(self, GroupedCentralWidget):
        self.add_card_widget_label.setText(QCoreApplication.translate("GroupedCentralWidget", u"Add new cards:", None))
        self.document_view_label.setText(QCoreApplication.translate("GroupedCentralWidget", u"All pages:", None))
        self.page_move_down.setText(QCoreApplication.translate("GroupedCentralWidget", u"Move down", None))
        self.page_move_up.setText(QCoreApplication.translate("GroupedCentralWidget", u"Move up", None))
        self.delete_selected_images_button.setText(QCoreApplication.translate("GroupedCentralWidget", u"Remove selected", None))
        pass
    # retranslateUi

