# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'columnar.ui'
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

from mtg_proxy_printer.ui.add_card import VerticalAddCardWidget
from mtg_proxy_printer.ui.page_card_table_view import PageCardTableView
from mtg_proxy_printer.ui.page_renderer import PageRenderer

class Ui_ColumnarCentralWidget(object):
    def setupUi(self, ColumnarCentralWidget):
        if not ColumnarCentralWidget.objectName():
            ColumnarCentralWidget.setObjectName(u"ColumnarCentralWidget")
        ColumnarCentralWidget.resize(887, 257)
        self.gridLayout = QGridLayout(ColumnarCentralWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.page_move_up = QPushButton(ColumnarCentralWidget)
        self.page_move_up.setObjectName(u"page_move_up")
        self.page_move_up.setEnabled(False)
        icon = QIcon(QIcon.fromTheme(u"arrow-up"))
        self.page_move_up.setIcon(icon)

        self.gridLayout.addWidget(self.page_move_up, 7, 0, 1, 1)

        self.page_view_label = QLabel(ColumnarCentralWidget)
        self.page_view_label.setObjectName(u"page_view_label")

        self.gridLayout.addWidget(self.page_view_label, 0, 3, 1, 2)

        self.add_card_widget = VerticalAddCardWidget(ColumnarCentralWidget)
        self.add_card_widget.setObjectName(u"add_card_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.add_card_widget.sizePolicy().hasHeightForWidth())
        self.add_card_widget.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.add_card_widget, 4, 2, 4, 1)

        self.page_renderer = PageRenderer(ColumnarCentralWidget)
        self.page_renderer.setObjectName(u"page_renderer")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(9)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.page_renderer.sizePolicy().hasHeightForWidth())
        self.page_renderer.setSizePolicy(sizePolicy1)
        self.page_renderer.setAcceptDrops(False)
        self.page_renderer.setRenderHints(QPainter.RenderHint.Antialiasing)

        self.gridLayout.addWidget(self.page_renderer, 4, 4, 4, 1)

        self.delete_selected_images_button = QPushButton(ColumnarCentralWidget)
        self.delete_selected_images_button.setObjectName(u"delete_selected_images_button")
        self.delete_selected_images_button.setEnabled(False)
        icon1 = QIcon(QIcon.fromTheme(u"edit-delete"))
        self.delete_selected_images_button.setIcon(icon1)

        self.gridLayout.addWidget(self.delete_selected_images_button, 7, 3, 1, 1)

        self.add_card_widget_label = QLabel(ColumnarCentralWidget)
        self.add_card_widget_label.setObjectName(u"add_card_widget_label")

        self.gridLayout.addWidget(self.add_card_widget_label, 0, 2, 1, 1)

        self.page_card_table_view = PageCardTableView(ColumnarCentralWidget)
        self.page_card_table_view.setObjectName(u"page_card_table_view")
        sizePolicy1.setHeightForWidth(self.page_card_table_view.sizePolicy().hasHeightForWidth())
        self.page_card_table_view.setSizePolicy(sizePolicy1)
        self.page_card_table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.page_card_table_view.setLineWidth(0)
        self.page_card_table_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.page_card_table_view.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.page_card_table_view.setAlternatingRowColors(True)
        self.page_card_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.page_card_table_view.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.page_card_table_view, 4, 3, 3, 1)

        self.page_move_down = QPushButton(ColumnarCentralWidget)
        self.page_move_down.setObjectName(u"page_move_down")
        self.page_move_down.setEnabled(False)
        icon2 = QIcon(QIcon.fromTheme(u"arrow-down"))
        self.page_move_down.setIcon(icon2)

        self.gridLayout.addWidget(self.page_move_down, 7, 1, 1, 1)

        self.document_view = QListView(ColumnarCentralWidget)
        self.document_view.setObjectName(u"document_view")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(2)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.document_view.sizePolicy().hasHeightForWidth())
        self.document_view.setSizePolicy(sizePolicy2)
        self.document_view.setDragDropOverwriteMode(False)
        self.document_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.document_view.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.document_view.setAlternatingRowColors(True)
        self.document_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.document_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.gridLayout.addWidget(self.document_view, 4, 0, 3, 2)

        self.document_view_label = QLabel(ColumnarCentralWidget)
        self.document_view_label.setObjectName(u"document_view_label")

        self.gridLayout.addWidget(self.document_view_label, 0, 0, 1, 2)


        self.retranslateUi(ColumnarCentralWidget)

        QMetaObject.connectSlotsByName(ColumnarCentralWidget)
    # setupUi

    def retranslateUi(self, ColumnarCentralWidget):
        self.page_move_up.setText(QCoreApplication.translate("ColumnarCentralWidget", u"Move up", None))
        self.page_view_label.setText(QCoreApplication.translate("ColumnarCentralWidget", u"Current page:", None))
        self.delete_selected_images_button.setText(QCoreApplication.translate("ColumnarCentralWidget", u"Remove selected", None))
        self.add_card_widget_label.setText(QCoreApplication.translate("ColumnarCentralWidget", u"Add new cards:", None))
        self.page_move_down.setText(QCoreApplication.translate("ColumnarCentralWidget", u"Move down", None))
        self.document_view_label.setText(QCoreApplication.translate("ColumnarCentralWidget", u"All pages:", None))
        pass
    # retranslateUi

