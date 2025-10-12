# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tabbed_vertical.ui'
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
    QListView, QPushButton, QSizePolicy, QTabWidget,
    QVBoxLayout, QWidget)

from mtg_proxy_printer.ui.add_card import VerticalAddCardWidget
from mtg_proxy_printer.ui.page_card_table_view import PageCardTableView
from mtg_proxy_printer.ui.page_renderer import PageRenderer

class Ui_TabbedCentralWidget(object):
    def setupUi(self, TabbedCentralWidget):
        if not TabbedCentralWidget.objectName():
            TabbedCentralWidget.setObjectName(u"TabbedCentralWidget")
        TabbedCentralWidget.resize(262, 266)
        self.gridLayout = QGridLayout(TabbedCentralWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget(TabbedCentralWidget)
        self.tab_widget.setObjectName(u"tab_widget")
        self.tab_document_page = QWidget()
        self.tab_document_page.setObjectName(u"tab_document_page")
        self.tab_document_page_layout = QGridLayout(self.tab_document_page)
        self.tab_document_page_layout.setObjectName(u"tab_document_page_layout")
        self.tab_document_page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_move_up = QPushButton(self.tab_document_page)
        self.page_move_up.setObjectName(u"page_move_up")
        self.page_move_up.setEnabled(False)
        icon = QIcon(QIcon.fromTheme(u"arrow-up"))
        self.page_move_up.setIcon(icon)

        self.tab_document_page_layout.addWidget(self.page_move_up, 1, 0, 1, 1)

        self.page_move_down = QPushButton(self.tab_document_page)
        self.page_move_down.setObjectName(u"page_move_down")
        self.page_move_down.setEnabled(False)
        icon1 = QIcon(QIcon.fromTheme(u"arrow-down"))
        self.page_move_down.setIcon(icon1)

        self.tab_document_page_layout.addWidget(self.page_move_down, 1, 1, 1, 1)

        self.document_view = QListView(self.tab_document_page)
        self.document_view.setObjectName(u"document_view")
        self.document_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.document_view.setDefaultDropAction(Qt.DropAction.MoveAction)

        self.tab_document_page_layout.addWidget(self.document_view, 0, 0, 1, 2)

        self.tab_widget.addTab(self.tab_document_page, "")
        self.add_card_widget = VerticalAddCardWidget()
        self.add_card_widget.setObjectName(u"add_card_widget")
        self.tab_widget.addTab(self.add_card_widget, "")
        self.tab_current_page = QWidget()
        self.tab_current_page.setObjectName(u"tab_current_page")
        self.verticalLayout = QVBoxLayout(self.tab_current_page)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.page_card_table_view = PageCardTableView(self.tab_current_page)
        self.page_card_table_view.setObjectName(u"page_card_table_view")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.page_card_table_view.sizePolicy().hasHeightForWidth())
        self.page_card_table_view.setSizePolicy(sizePolicy)
        self.page_card_table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.page_card_table_view.setLineWidth(0)
        self.page_card_table_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.page_card_table_view.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.page_card_table_view.setAlternatingRowColors(True)
        self.page_card_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.page_card_table_view.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.page_card_table_view)

        self.delete_selected_images_button = QPushButton(self.tab_current_page)
        self.delete_selected_images_button.setObjectName(u"delete_selected_images_button")
        self.delete_selected_images_button.setEnabled(False)
        icon2 = QIcon(QIcon.fromTheme(u"edit-delete"))
        self.delete_selected_images_button.setIcon(icon2)

        self.verticalLayout.addWidget(self.delete_selected_images_button)

        self.tab_widget.addTab(self.tab_current_page, "")
        self.page_renderer = PageRenderer()
        self.page_renderer.setObjectName(u"page_renderer")
        self.tab_widget.addTab(self.page_renderer, "")

        self.gridLayout.addWidget(self.tab_widget, 4, 0, 2, 2)


        self.retranslateUi(TabbedCentralWidget)

        self.tab_widget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(TabbedCentralWidget)
    # setupUi

    def retranslateUi(self, TabbedCentralWidget):
        self.page_move_up.setText(QCoreApplication.translate("TabbedCentralWidget", u"Move up", None))
        self.page_move_down.setText(QCoreApplication.translate("TabbedCentralWidget", u"Move down", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_document_page), QCoreApplication.translate("TabbedCentralWidget", u"All pages", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.add_card_widget), QCoreApplication.translate("TabbedCentralWidget", u"Add new cards", None))
        self.delete_selected_images_button.setText(QCoreApplication.translate("TabbedCentralWidget", u"Remove selected", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_current_page), QCoreApplication.translate("TabbedCentralWidget", u"Current page", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.page_renderer), QCoreApplication.translate("TabbedCentralWidget", u"Preview", None))
        pass
    # retranslateUi

