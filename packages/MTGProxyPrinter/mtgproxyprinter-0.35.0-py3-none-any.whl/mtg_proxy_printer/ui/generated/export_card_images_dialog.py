# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_card_images_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QWidget)

class Ui_ExportCardImagesDialog(object):
    def setupUi(self, ExportCardImagesDialog):
        if not ExportCardImagesDialog.objectName():
            ExportCardImagesDialog.setObjectName(u"ExportCardImagesDialog")
        ExportCardImagesDialog.setWindowModality(Qt.WindowModality.WindowModal)
        ExportCardImagesDialog.resize(600, 200)
        self.grid_layout = QGridLayout(ExportCardImagesDialog)
        self.grid_layout.setObjectName(u"grid_layout")
        self.output_path_browse_button = QPushButton(ExportCardImagesDialog)
        self.output_path_browse_button.setObjectName(u"output_path_browse_button")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.output_path_browse_button.sizePolicy().hasHeightForWidth())
        self.output_path_browse_button.setSizePolicy(sizePolicy)
        self.output_path_browse_button.setText(u"")
        icon = QIcon(QIcon.fromTheme(u"document-open"))
        self.output_path_browse_button.setIcon(icon)

        self.grid_layout.addWidget(self.output_path_browse_button, 1, 2, 1, 1)

        self.button_box = QDialogButtonBox(ExportCardImagesDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.grid_layout.addWidget(self.button_box, 10, 0, 1, 3)

        self.export_custom_cards = QCheckBox(ExportCardImagesDialog)
        self.export_custom_cards.setObjectName(u"export_custom_cards")

        self.grid_layout.addWidget(self.export_custom_cards, 6, 0, 1, 3)

        self.line = QFrame(ExportCardImagesDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.grid_layout.addWidget(self.line, 3, 0, 1, 3)

        self.output_path_label = QLabel(ExportCardImagesDialog)
        self.output_path_label.setObjectName(u"output_path_label")

        self.grid_layout.addWidget(self.output_path_label, 1, 0, 1, 1)

        self.export_official_cards = QCheckBox(ExportCardImagesDialog)
        self.export_official_cards.setObjectName(u"export_official_cards")
        self.export_official_cards.setChecked(True)

        self.grid_layout.addWidget(self.export_official_cards, 5, 0, 1, 3)

        self.header_label = QLabel(ExportCardImagesDialog)
        self.header_label.setObjectName(u"header_label")
        self.header_label.setWordWrap(True)

        self.grid_layout.addWidget(self.header_label, 4, 0, 1, 3)

        self.output_path = QLineEdit(ExportCardImagesDialog)
        self.output_path.setObjectName(u"output_path")
        self.output_path.setClearButtonEnabled(True)

        self.grid_layout.addWidget(self.output_path, 1, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.grid_layout.addItem(self.verticalSpacer, 7, 0, 1, 3)


        self.retranslateUi(ExportCardImagesDialog)
        self.button_box.accepted.connect(ExportCardImagesDialog.accept)
        self.button_box.rejected.connect(ExportCardImagesDialog.reject)
        self.export_custom_cards.clicked.connect(ExportCardImagesDialog.update_ok_button_enabled_state)
        self.export_official_cards.clicked.connect(ExportCardImagesDialog.update_ok_button_enabled_state)

        QMetaObject.connectSlotsByName(ExportCardImagesDialog)
    # setupUi

    def retranslateUi(self, ExportCardImagesDialog):
        ExportCardImagesDialog.setWindowTitle(QCoreApplication.translate("ExportCardImagesDialog", u"Export card images", None))
#if QT_CONFIG(tooltip)
        self.output_path_browse_button.setToolTip(QCoreApplication.translate("ExportCardImagesDialog", u"Browse \u2026", None))
#endif // QT_CONFIG(tooltip)
        self.export_custom_cards.setText(QCoreApplication.translate("ExportCardImagesDialog", u"Custom cards", None))
        self.output_path_label.setText(QCoreApplication.translate("ExportCardImagesDialog", u"Output directory:", None))
        self.export_official_cards.setText(QCoreApplication.translate("ExportCardImagesDialog", u"Official cards", None))
        self.header_label.setText(QCoreApplication.translate("ExportCardImagesDialog", u"Which card images should be exported?", None))
        self.output_path.setPlaceholderText(QCoreApplication.translate("ExportCardImagesDialog", u"Path to a directory", None))
    # retranslateUi

