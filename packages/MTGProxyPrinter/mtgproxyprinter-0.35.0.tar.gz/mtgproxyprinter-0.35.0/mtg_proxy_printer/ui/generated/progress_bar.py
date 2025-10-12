# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'progress_bar.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QSizePolicy, QWidget)

class Ui_ProgressBar(object):
    def setupUi(self, ProgressBar):
        if not ProgressBar.objectName():
            ProgressBar.setObjectName(u"ProgressBar")
        ProgressBar.resize(682, 182)
        self.horizontal_layout = QHBoxLayout(ProgressBar)
        self.horizontal_layout.setObjectName(u"horizontal_layout")
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.task_label = QLabel(ProgressBar)
        self.task_label.setObjectName(u"task_label")

        self.horizontal_layout.addWidget(self.task_label)

        self.cancel_button = QPushButton(ProgressBar)
        self.cancel_button.setObjectName(u"cancel_button")
        icon = QIcon(QIcon.fromTheme(u"dialog-cancel"))
        self.cancel_button.setIcon(icon)

        self.horizontal_layout.addWidget(self.cancel_button)

        self.progress_bar = QProgressBar(ProgressBar)
        self.progress_bar.setObjectName(u"progress_bar")

        self.horizontal_layout.addWidget(self.progress_bar)


        self.retranslateUi(ProgressBar)
        self.cancel_button.clicked["bool"].connect(self.cancel_button.setEnabled)

        QMetaObject.connectSlotsByName(ProgressBar)
    # setupUi

    def retranslateUi(self, ProgressBar):
        self.task_label.setText("")
#if QT_CONFIG(tooltip)
        self.cancel_button.setToolTip(QCoreApplication.translate("ProgressBar", u"Cancel", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

