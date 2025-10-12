# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'page_config_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSlider,
    QSpacerItem, QTabWidget, QWidget)

class Ui_PageConfigWidget(object):
    def setupUi(self, PageConfigWidget):
        if not PageConfigWidget.objectName():
            PageConfigWidget.setObjectName(u"PageConfigWidget")
        PageConfigWidget.resize(365, 643)
        self.gridLayout = QGridLayout(PageConfigWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.preview_button_alignment_layout = QHBoxLayout()
        self.preview_button_alignment_layout.setObjectName(u"preview_button_alignment_layout")
        self.preview_button_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.preview_button_alignment_layout.addItem(self.preview_button_spacer)

        self.show_preview_button = QPushButton(PageConfigWidget)
        self.show_preview_button.setObjectName(u"show_preview_button")
        self.show_preview_button.setCheckable(True)

        self.preview_button_alignment_layout.addWidget(self.show_preview_button)


        self.gridLayout.addLayout(self.preview_button_alignment_layout, 26, 1, 1, 3)

        self.document_name = QLineEdit(PageConfigWidget)
        self.document_name.setObjectName(u"document_name")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.document_name.sizePolicy().hasHeightForWidth())
        self.document_name.setSizePolicy(sizePolicy)
        self.document_name.setMaxLength(200)
        self.document_name.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.document_name, 0, 2, 1, 2)

        self.draw_page_numbers = QCheckBox(PageConfigWidget)
        self.draw_page_numbers.setObjectName(u"draw_page_numbers")

        self.gridLayout.addWidget(self.draw_page_numbers, 1, 1, 1, 3)

        self.document_name_label = QLabel(PageConfigWidget)
        self.document_name_label.setObjectName(u"document_name_label")

        self.gridLayout.addWidget(self.document_name_label, 0, 1, 1, 1)

        self.draw_sharp_corners = QCheckBox(PageConfigWidget)
        self.draw_sharp_corners.setObjectName(u"draw_sharp_corners")

        self.gridLayout.addWidget(self.draw_sharp_corners, 2, 1, 1, 3)

        self.spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.spacer_bottom, 28, 1, 1, 3)

        self.tab_widget = QTabWidget(PageConfigWidget)
        self.tab_widget.setObjectName(u"tab_widget")
        self.tab_paper_dimensions = QWidget()
        self.tab_paper_dimensions.setObjectName(u"tab_paper_dimensions")
        self.gridLayout_2 = QGridLayout(self.tab_paper_dimensions)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.card_bleed = QDoubleSpinBox(self.tab_paper_dimensions)
        self.card_bleed.setObjectName(u"card_bleed")
        self.card_bleed.setMaximum(1000.000000000000000)

        self.gridLayout_2.addWidget(self.card_bleed, 10, 1, 1, 2)

        self.margin_bottom_label = QLabel(self.tab_paper_dimensions)
        self.margin_bottom_label.setObjectName(u"margin_bottom_label")
        self.margin_bottom_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.margin_bottom_label, 4, 0, 1, 1)

        self.margin_right_label = QLabel(self.tab_paper_dimensions)
        self.margin_right_label.setObjectName(u"margin_right_label")
        self.margin_right_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.margin_right_label, 7, 0, 1, 1)

        self.margin_top_label = QLabel(self.tab_paper_dimensions)
        self.margin_top_label.setObjectName(u"margin_top_label")
        self.margin_top_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.margin_top_label, 3, 0, 1, 1)

        self.paper_size = QComboBox(self.tab_paper_dimensions)
        self.paper_size.setObjectName(u"paper_size")

        self.gridLayout_2.addWidget(self.paper_size, 0, 1, 1, 1)

        self.custom_page_width = QDoubleSpinBox(self.tab_paper_dimensions)
        self.custom_page_width.setObjectName(u"custom_page_width")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.custom_page_width.sizePolicy().hasHeightForWidth())
        self.custom_page_width.setSizePolicy(sizePolicy1)
        self.custom_page_width.setMinimum(88.060000000000002)
        self.custom_page_width.setMaximum(10000.000000000000000)

        self.gridLayout_2.addWidget(self.custom_page_width, 2, 1, 1, 1)

        self.margin_right = QDoubleSpinBox(self.tab_paper_dimensions)
        self.margin_right.setObjectName(u"margin_right")
        sizePolicy1.setHeightForWidth(self.margin_right.sizePolicy().hasHeightForWidth())
        self.margin_right.setSizePolicy(sizePolicy1)
        self.margin_right.setMaximum(10000.000000000000000)

        self.gridLayout_2.addWidget(self.margin_right, 7, 1, 1, 2)

        self.paper_orientation = QComboBox(self.tab_paper_dimensions)
        self.paper_orientation.setObjectName(u"paper_orientation")

        self.gridLayout_2.addWidget(self.paper_orientation, 0, 2, 1, 1)

        self.margin_left_label = QLabel(self.tab_paper_dimensions)
        self.margin_left_label.setObjectName(u"margin_left_label")
        self.margin_left_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.margin_left_label, 5, 0, 1, 1)

        self.custom_page_height_label = QLabel(self.tab_paper_dimensions)
        self.custom_page_height_label.setObjectName(u"custom_page_height_label")
        self.custom_page_height_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.custom_page_height_label, 1, 0, 1, 1)

        self.card_bleed_label = QLabel(self.tab_paper_dimensions)
        self.card_bleed_label.setObjectName(u"card_bleed_label")
        self.card_bleed_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.card_bleed_label, 10, 0, 1, 1)

        self.custom_page_height = QDoubleSpinBox(self.tab_paper_dimensions)
        self.custom_page_height.setObjectName(u"custom_page_height")
        sizePolicy1.setHeightForWidth(self.custom_page_height.sizePolicy().hasHeightForWidth())
        self.custom_page_height.setSizePolicy(sizePolicy1)
        self.custom_page_height.setMinimum(126.170000000000002)
        self.custom_page_height.setMaximum(10000.000000000000000)

        self.gridLayout_2.addWidget(self.custom_page_height, 1, 1, 1, 1)

        self.page_capacity_label = QLabel(self.tab_paper_dimensions)
        self.page_capacity_label.setObjectName(u"page_capacity_label")
        self.page_capacity_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.page_capacity_label, 12, 0, 1, 1)

        self.custom_page_width_label = QLabel(self.tab_paper_dimensions)
        self.custom_page_width_label.setObjectName(u"custom_page_width_label")
        self.custom_page_width_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.custom_page_width_label, 2, 0, 1, 1)

        self.page_capacity = QLabel(self.tab_paper_dimensions)
        self.page_capacity.setObjectName(u"page_capacity")
        self.page_capacity.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.page_capacity, 12, 1, 1, 2)

        self.flip_page_dimensions = QPushButton(self.tab_paper_dimensions)
        self.flip_page_dimensions.setObjectName(u"flip_page_dimensions")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.flip_page_dimensions.sizePolicy().hasHeightForWidth())
        self.flip_page_dimensions.setSizePolicy(sizePolicy2)
        icon = QIcon(QIcon.fromTheme(u"transform-rotate"))
        self.flip_page_dimensions.setIcon(icon)

        self.gridLayout_2.addWidget(self.flip_page_dimensions, 1, 2, 2, 1)

        self.margin_bottom = QDoubleSpinBox(self.tab_paper_dimensions)
        self.margin_bottom.setObjectName(u"margin_bottom")
        sizePolicy1.setHeightForWidth(self.margin_bottom.sizePolicy().hasHeightForWidth())
        self.margin_bottom.setSizePolicy(sizePolicy1)
        self.margin_bottom.setMaximum(10000.000000000000000)

        self.gridLayout_2.addWidget(self.margin_bottom, 4, 1, 1, 2)

        self.column_spacing_label = QLabel(self.tab_paper_dimensions)
        self.column_spacing_label.setObjectName(u"column_spacing_label")
        self.column_spacing_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.column_spacing_label, 9, 0, 1, 1)

        self.margin_left = QDoubleSpinBox(self.tab_paper_dimensions)
        self.margin_left.setObjectName(u"margin_left")
        sizePolicy1.setHeightForWidth(self.margin_left.sizePolicy().hasHeightForWidth())
        self.margin_left.setSizePolicy(sizePolicy1)
        self.margin_left.setMaximum(10000.000000000000000)

        self.gridLayout_2.addWidget(self.margin_left, 5, 1, 1, 2)

        self.row_spacing = QDoubleSpinBox(self.tab_paper_dimensions)
        self.row_spacing.setObjectName(u"row_spacing")
        sizePolicy1.setHeightForWidth(self.row_spacing.sizePolicy().hasHeightForWidth())
        self.row_spacing.setSizePolicy(sizePolicy1)
        self.row_spacing.setMaximum(10000.000000000000000)

        self.gridLayout_2.addWidget(self.row_spacing, 8, 1, 1, 2)

        self.row_spacing_label = QLabel(self.tab_paper_dimensions)
        self.row_spacing_label.setObjectName(u"row_spacing_label")
        self.row_spacing_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout_2.addWidget(self.row_spacing_label, 8, 0, 1, 1)

        self.margin_top = QDoubleSpinBox(self.tab_paper_dimensions)
        self.margin_top.setObjectName(u"margin_top")
        sizePolicy1.setHeightForWidth(self.margin_top.sizePolicy().hasHeightForWidth())
        self.margin_top.setSizePolicy(sizePolicy1)
        self.margin_top.setMaximum(10000.000000000000000)

        self.gridLayout_2.addWidget(self.margin_top, 3, 1, 1, 2)

        self.column_spacing = QDoubleSpinBox(self.tab_paper_dimensions)
        self.column_spacing.setObjectName(u"column_spacing")
        sizePolicy1.setHeightForWidth(self.column_spacing.sizePolicy().hasHeightForWidth())
        self.column_spacing.setSizePolicy(sizePolicy1)
        self.column_spacing.setMaximum(10000.000000000000000)

        self.gridLayout_2.addWidget(self.column_spacing, 9, 1, 1, 2)

        self.paper_size_label = QLabel(self.tab_paper_dimensions)
        self.paper_size_label.setObjectName(u"paper_size_label")

        self.gridLayout_2.addWidget(self.paper_size_label, 0, 0, 1, 1)

        self.tab_widget.addTab(self.tab_paper_dimensions, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_4 = QGridLayout(self.tab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.cut_marker_style = QComboBox(self.tab)
        self.cut_marker_style.setObjectName(u"cut_marker_style")

        self.gridLayout_4.addWidget(self.cut_marker_style, 1, 1, 1, 3)

        self.cut_marker_draw_above_cards = QCheckBox(self.tab)
        self.cut_marker_draw_above_cards.setObjectName(u"cut_marker_draw_above_cards")

        self.gridLayout_4.addWidget(self.cut_marker_draw_above_cards, 2, 0, 1, 4)

        self.cut_marker_width = QDoubleSpinBox(self.tab)
        self.cut_marker_width.setObjectName(u"cut_marker_width")
        self.cut_marker_width.setSuffix(u" mm ")
        self.cut_marker_width.setMaximum(10.000000000000000)
        self.cut_marker_width.setSingleStep(0.100000000000000)

        self.gridLayout_4.addWidget(self.cut_marker_width, 3, 1, 1, 3)

        self.cut_marker_style_label = QLabel(self.tab)
        self.cut_marker_style_label.setObjectName(u"cut_marker_style_label")

        self.gridLayout_4.addWidget(self.cut_marker_style_label, 1, 0, 1, 1)

        self.cut_marker_color_button = QPushButton(self.tab)
        self.cut_marker_color_button.setObjectName(u"cut_marker_color_button")
        icon1 = QIcon(QIcon.fromTheme(u"color-picker"))
        self.cut_marker_color_button.setIcon(icon1)

        self.gridLayout_4.addWidget(self.cut_marker_color_button, 4, 2, 1, 1)

        self.cut_marker_opacity = QSlider(self.tab)
        self.cut_marker_opacity.setObjectName(u"cut_marker_opacity")
        self.cut_marker_opacity.setMaximum(255)
        self.cut_marker_opacity.setOrientation(Qt.Orientation.Horizontal)
        self.cut_marker_opacity.setTickPosition(QSlider.TickPosition.NoTicks)

        self.gridLayout_4.addWidget(self.cut_marker_opacity, 4, 3, 1, 1)

        self.cut_marker_width_label = QLabel(self.tab)
        self.cut_marker_width_label.setObjectName(u"cut_marker_width_label")

        self.gridLayout_4.addWidget(self.cut_marker_width_label, 3, 0, 1, 1)

        self.tab_cut_markers_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.tab_cut_markers_spacer, 6, 0, 1, 4)

        self.cut_marker_color_label = QLabel(self.tab)
        self.cut_marker_color_label.setObjectName(u"cut_marker_color_label")

        self.gridLayout_4.addWidget(self.cut_marker_color_label, 4, 0, 1, 1)

        self.cut_marker_color = QLabel(self.tab)
        self.cut_marker_color.setObjectName(u"cut_marker_color")
        self.cut_marker_color.setMinimumSize(QSize(32, 0))

        self.gridLayout_4.addWidget(self.cut_marker_color, 4, 1, 1, 1)

        self.print_registration_marks_style = QComboBox(self.tab)
        self.print_registration_marks_style.setObjectName(u"print_registration_marks_style")

        self.gridLayout_4.addWidget(self.print_registration_marks_style, 5, 2, 1, 2)

        self.print_registration_marks_style_label = QLabel(self.tab)
        self.print_registration_marks_style_label.setObjectName(u"print_registration_marks_style_label")

        self.gridLayout_4.addWidget(self.print_registration_marks_style_label, 5, 0, 1, 2)

        self.tab_widget.addTab(self.tab, "")
        self.tab_watermark_settings = QWidget()
        self.tab_watermark_settings.setObjectName(u"tab_watermark_settings")
        self.gridLayout_3 = QGridLayout(self.tab_watermark_settings)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.watermark_pos_x_label = QLabel(self.tab_watermark_settings)
        self.watermark_pos_x_label.setObjectName(u"watermark_pos_x_label")

        self.gridLayout_3.addWidget(self.watermark_pos_x_label, 3, 0, 1, 1)

        self.watermark_pos_y_label = QLabel(self.tab_watermark_settings)
        self.watermark_pos_y_label.setObjectName(u"watermark_pos_y_label")

        self.gridLayout_3.addWidget(self.watermark_pos_y_label, 5, 0, 1, 1)

        self.watermark_text_label = QLabel(self.tab_watermark_settings)
        self.watermark_text_label.setObjectName(u"watermark_text_label")

        self.gridLayout_3.addWidget(self.watermark_text_label, 0, 0, 1, 1)

        self.watermark_pos_x = QDoubleSpinBox(self.tab_watermark_settings)
        self.watermark_pos_x.setObjectName(u"watermark_pos_x")
        self.watermark_pos_x.setSuffix(u" mm ")
        self.watermark_pos_x.setMinimum(-100.000000000000000)
        self.watermark_pos_x.setMaximum(100.000000000000000)

        self.gridLayout_3.addWidget(self.watermark_pos_x, 3, 1, 1, 4)

        self.watermark_angle_label = QLabel(self.tab_watermark_settings)
        self.watermark_angle_label.setObjectName(u"watermark_angle_label")

        self.gridLayout_3.addWidget(self.watermark_angle_label, 6, 0, 1, 1)

        self.tab_watermark_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.tab_watermark_spacer, 7, 0, 1, 4)

        self.watermark_text = QLineEdit(self.tab_watermark_settings)
        self.watermark_text.setObjectName(u"watermark_text")

        self.gridLayout_3.addWidget(self.watermark_text, 0, 1, 1, 4)

        self.watermark_font_size_label = QLabel(self.tab_watermark_settings)
        self.watermark_font_size_label.setObjectName(u"watermark_font_size_label")

        self.gridLayout_3.addWidget(self.watermark_font_size_label, 1, 0, 1, 1)

        self.watermark_color_label = QLabel(self.tab_watermark_settings)
        self.watermark_color_label.setObjectName(u"watermark_color_label")

        self.gridLayout_3.addWidget(self.watermark_color_label, 2, 0, 1, 1)

        self.watermark_font_size = QDoubleSpinBox(self.tab_watermark_settings)
        self.watermark_font_size.setObjectName(u"watermark_font_size")

        self.gridLayout_3.addWidget(self.watermark_font_size, 1, 1, 1, 4)

        self.watermark_pos_y = QDoubleSpinBox(self.tab_watermark_settings)
        self.watermark_pos_y.setObjectName(u"watermark_pos_y")
        self.watermark_pos_y.setSuffix(u" mm ")
        self.watermark_pos_y.setMinimum(-100.000000000000000)
        self.watermark_pos_y.setMaximum(100.000000000000000)

        self.gridLayout_3.addWidget(self.watermark_pos_y, 5, 1, 1, 4)

        self.watermark_color_button = QPushButton(self.tab_watermark_settings)
        self.watermark_color_button.setObjectName(u"watermark_color_button")
        self.watermark_color_button.setIcon(icon1)

        self.gridLayout_3.addWidget(self.watermark_color_button, 2, 2, 1, 1)

        self.watermark_color = QLabel(self.tab_watermark_settings)
        self.watermark_color.setObjectName(u"watermark_color")
        self.watermark_color.setMinimumSize(QSize(32, 0))

        self.gridLayout_3.addWidget(self.watermark_color, 2, 1, 1, 1)

        self.watermark_angle = QDoubleSpinBox(self.tab_watermark_settings)
        self.watermark_angle.setObjectName(u"watermark_angle")
        self.watermark_angle.setSuffix(u" \u00b0 ")
        self.watermark_angle.setMaximum(360.000000000000000)

        self.gridLayout_3.addWidget(self.watermark_angle, 6, 1, 1, 4)

        self.watermark_opacity = QSlider(self.tab_watermark_settings)
        self.watermark_opacity.setObjectName(u"watermark_opacity")
        self.watermark_opacity.setMaximum(255)
        self.watermark_opacity.setOrientation(Qt.Orientation.Horizontal)
        self.watermark_opacity.setTickPosition(QSlider.TickPosition.NoTicks)

        self.gridLayout_3.addWidget(self.watermark_opacity, 2, 3, 1, 1)

        self.tab_widget.addTab(self.tab_watermark_settings, "")

        self.gridLayout.addWidget(self.tab_widget, 14, 1, 1, 3)

#if QT_CONFIG(shortcut)
        self.document_name_label.setBuddy(self.document_name)
        self.margin_bottom_label.setBuddy(self.margin_bottom)
        self.margin_right_label.setBuddy(self.margin_right)
        self.margin_top_label.setBuddy(self.margin_top)
        self.margin_left_label.setBuddy(self.margin_left)
        self.custom_page_height_label.setBuddy(self.custom_page_height)
        self.card_bleed_label.setBuddy(self.card_bleed)
        self.custom_page_width_label.setBuddy(self.custom_page_width)
        self.column_spacing_label.setBuddy(self.column_spacing)
        self.row_spacing_label.setBuddy(self.row_spacing)
        self.paper_size_label.setBuddy(self.paper_size)
        self.cut_marker_style_label.setBuddy(self.cut_marker_style)
        self.cut_marker_width_label.setBuddy(self.cut_marker_width)
        self.cut_marker_color_label.setBuddy(self.cut_marker_color_button)
        self.cut_marker_color.setBuddy(self.cut_marker_color_button)
        self.print_registration_marks_style_label.setBuddy(self.print_registration_marks_style)
        self.watermark_pos_x_label.setBuddy(self.watermark_pos_x)
        self.watermark_pos_y_label.setBuddy(self.watermark_pos_y)
        self.watermark_text_label.setBuddy(self.watermark_text)
        self.watermark_angle_label.setBuddy(self.watermark_angle)
        self.watermark_font_size_label.setBuddy(self.watermark_font_size)
        self.watermark_color_label.setBuddy(self.watermark_color_button)
        self.watermark_color.setBuddy(self.watermark_color_button)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.document_name, self.draw_page_numbers)
        QWidget.setTabOrder(self.draw_page_numbers, self.draw_sharp_corners)
        QWidget.setTabOrder(self.draw_sharp_corners, self.tab_widget)
        QWidget.setTabOrder(self.tab_widget, self.paper_size)
        QWidget.setTabOrder(self.paper_size, self.paper_orientation)
        QWidget.setTabOrder(self.paper_orientation, self.custom_page_height)
        QWidget.setTabOrder(self.custom_page_height, self.custom_page_width)
        QWidget.setTabOrder(self.custom_page_width, self.flip_page_dimensions)
        QWidget.setTabOrder(self.flip_page_dimensions, self.margin_top)
        QWidget.setTabOrder(self.margin_top, self.margin_bottom)
        QWidget.setTabOrder(self.margin_bottom, self.margin_left)
        QWidget.setTabOrder(self.margin_left, self.margin_right)
        QWidget.setTabOrder(self.margin_right, self.row_spacing)
        QWidget.setTabOrder(self.row_spacing, self.column_spacing)
        QWidget.setTabOrder(self.column_spacing, self.card_bleed)
        QWidget.setTabOrder(self.card_bleed, self.cut_marker_style)
        QWidget.setTabOrder(self.cut_marker_style, self.cut_marker_draw_above_cards)
        QWidget.setTabOrder(self.cut_marker_draw_above_cards, self.cut_marker_width)
        QWidget.setTabOrder(self.cut_marker_width, self.cut_marker_color_button)
        QWidget.setTabOrder(self.cut_marker_color_button, self.cut_marker_opacity)
        QWidget.setTabOrder(self.cut_marker_opacity, self.print_registration_marks_style)
        QWidget.setTabOrder(self.print_registration_marks_style, self.watermark_text)
        QWidget.setTabOrder(self.watermark_text, self.watermark_font_size)
        QWidget.setTabOrder(self.watermark_font_size, self.watermark_color_button)
        QWidget.setTabOrder(self.watermark_color_button, self.watermark_opacity)
        QWidget.setTabOrder(self.watermark_opacity, self.watermark_pos_x)
        QWidget.setTabOrder(self.watermark_pos_x, self.watermark_pos_y)
        QWidget.setTabOrder(self.watermark_pos_y, self.watermark_angle)
        QWidget.setTabOrder(self.watermark_angle, self.show_preview_button)

        self.retranslateUi(PageConfigWidget)

        self.tab_widget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(PageConfigWidget)
    # setupUi

    def retranslateUi(self, PageConfigWidget):
        PageConfigWidget.setTitle(QCoreApplication.translate("PageConfigWidget", u"Default settings for new documents", None))
        self.show_preview_button.setText(QCoreApplication.translate("PageConfigWidget", u"Show Preview", None))
#if QT_CONFIG(tooltip)
        self.document_name.setToolTip(QCoreApplication.translate("PageConfigWidget", u"The document name is printed on each page and can help you keep track\n"
"of different printed sheets and to which deck they belong.\n"
"\n"
"Leave empty to disable.", None))
#endif // QT_CONFIG(tooltip)
        self.document_name.setPlaceholderText(QCoreApplication.translate("PageConfigWidget", u"Document/deck name", None))
#if QT_CONFIG(tooltip)
        self.draw_page_numbers.setToolTip(QCoreApplication.translate("PageConfigWidget", u"If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.", None))
#endif // QT_CONFIG(tooltip)
        self.draw_page_numbers.setText(QCoreApplication.translate("PageConfigWidget", u"Print page numbers", None))
        self.document_name_label.setText(QCoreApplication.translate("PageConfigWidget", u"Document name", None))
        self.draw_sharp_corners.setText(QCoreApplication.translate("PageConfigWidget", u"Draw 90\u00b0 card corners, instead of round ones", None))
#if QT_CONFIG(tooltip)
        self.card_bleed.setToolTip(QCoreApplication.translate("PageConfigWidget", u"Draw an additional border around cards to ease cutting.", None))
#endif // QT_CONFIG(tooltip)
        self.card_bleed.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
        self.margin_bottom_label.setText(QCoreApplication.translate("PageConfigWidget", u"Bottom margin", None))
        self.margin_right_label.setText(QCoreApplication.translate("PageConfigWidget", u"Right margin", None))
        self.margin_top_label.setText(QCoreApplication.translate("PageConfigWidget", u"Top margin", None))
#if QT_CONFIG(tooltip)
        self.custom_page_width.setToolTip(QCoreApplication.translate("PageConfigWidget", u"Paper width in millimeters.\n"
"Must match the size of the sheets in the printer.\n"
"Otherwise, scaling may be applied by the printer driver.", None))
#endif // QT_CONFIG(tooltip)
        self.custom_page_width.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
#if QT_CONFIG(tooltip)
        self.margin_right.setToolTip(QCoreApplication.translate("PageConfigWidget", u"<html><head/><body><p>Minimum margin between the right paper border and the page content.</p><p>Most printers have a minimum printing margin of 3 to 5 mm.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.margin_right.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
        self.margin_left_label.setText(QCoreApplication.translate("PageConfigWidget", u"Left margin", None))
        self.custom_page_height_label.setText(QCoreApplication.translate("PageConfigWidget", u"Paper height", None))
        self.card_bleed_label.setText(QCoreApplication.translate("PageConfigWidget", u"Card bleed", None))
#if QT_CONFIG(tooltip)
        self.custom_page_height.setToolTip(QCoreApplication.translate("PageConfigWidget", u"Paper height in millimeters.\n"
"Must match the size of the sheets in the printer.\n"
"Otherwise, scaling may be applied by the printer driver.", None))
#endif // QT_CONFIG(tooltip)
        self.custom_page_height.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
        self.page_capacity_label.setText(QCoreApplication.translate("PageConfigWidget", u"Resulting page capacity:", None))
        self.custom_page_width_label.setText(QCoreApplication.translate("PageConfigWidget", u"Paper width", None))
#if QT_CONFIG(tooltip)
        self.page_capacity.setToolTip(QCoreApplication.translate("PageConfigWidget", u"Number of cards fitting on each page,\n"
"based on the page size and spacings configured", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.flip_page_dimensions.setToolTip(QCoreApplication.translate("PageConfigWidget", u"Switch between portrait and landscape mode", None))
#endif // QT_CONFIG(tooltip)
        self.flip_page_dimensions.setText(QCoreApplication.translate("PageConfigWidget", u"Flip", None))
#if QT_CONFIG(tooltip)
        self.margin_bottom.setToolTip(QCoreApplication.translate("PageConfigWidget", u"<html><head/><body><p>Minimum margin between the bottom paper border and the page content.</p><p>Most printers have a minimum printing margin of 3 to 5 mm.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.margin_bottom.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
        self.column_spacing_label.setText(QCoreApplication.translate("PageConfigWidget", u"Column spacing", None))
#if QT_CONFIG(tooltip)
        self.margin_left.setToolTip(QCoreApplication.translate("PageConfigWidget", u"<html><head/><body><p>Minimum margin between the left paper border and the page content.</p><p>Most printers have a minimum printing margin of 3 to 5 mm.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.margin_left.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
#if QT_CONFIG(tooltip)
        self.row_spacing.setToolTip(QCoreApplication.translate("PageConfigWidget", u"Space between image rows in mm.\n"
"If set to zero, you only need one cut to separate two images,\n"
"otherwise you need two cuts but require less precision hitting the exact middle.", None))
#endif // QT_CONFIG(tooltip)
        self.row_spacing.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
        self.row_spacing_label.setText(QCoreApplication.translate("PageConfigWidget", u"Row spacing", None))
#if QT_CONFIG(tooltip)
        self.margin_top.setToolTip(QCoreApplication.translate("PageConfigWidget", u"<html><head/><body><p>Minimum margin between the top paper border and the page content.</p><p>Most printers have a minimum printing margin of 3 to 5 mm.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.margin_top.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
#if QT_CONFIG(tooltip)
        self.column_spacing.setToolTip(QCoreApplication.translate("PageConfigWidget", u"Space between image columns in mm.\n"
"If set to zero, you only need one cut to separate two images,\n"
"otherwise you need two cuts but require less precision hitting the exact middle.", None))
#endif // QT_CONFIG(tooltip)
        self.column_spacing.setSuffix(QCoreApplication.translate("PageConfigWidget", u" mm", None))
        self.paper_size_label.setText(QCoreApplication.translate("PageConfigWidget", u"Paper size", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_paper_dimensions), QCoreApplication.translate("PageConfigWidget", u"Paper dimensions", None))
#if QT_CONFIG(tooltip)
        self.cut_marker_draw_above_cards.setToolTip(QCoreApplication.translate("PageConfigWidget", u"Draw cut helper lines above card images, instead of below them", None))
#endif // QT_CONFIG(tooltip)
        self.cut_marker_draw_above_cards.setText(QCoreApplication.translate("PageConfigWidget", u"Draw above cards", None))
#if QT_CONFIG(tooltip)
        self.cut_marker_width.setToolTip(QCoreApplication.translate("PageConfigWidget", u"The default width of 0 draws a thin line, regardless of zoom level.", None))
#endif // QT_CONFIG(tooltip)
        self.cut_marker_style_label.setText(QCoreApplication.translate("PageConfigWidget", u"Cut helper lines", None))
        self.cut_marker_color_button.setText(QCoreApplication.translate("PageConfigWidget", u"Select a color", None))
        self.cut_marker_width_label.setText(QCoreApplication.translate("PageConfigWidget", u"Line width", None))
        self.cut_marker_color_label.setText(QCoreApplication.translate("PageConfigWidget", u"Color and opacity", None))
        self.cut_marker_color.setText("")
        self.print_registration_marks_style_label.setText(QCoreApplication.translate("PageConfigWidget", u"Print registration marks", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab), QCoreApplication.translate("PageConfigWidget", u"Cut markers", None))
        self.watermark_pos_x_label.setText(QCoreApplication.translate("PageConfigWidget", u"X position", None))
        self.watermark_pos_y_label.setText(QCoreApplication.translate("PageConfigWidget", u"Y position", None))
        self.watermark_text_label.setText(QCoreApplication.translate("PageConfigWidget", u"Watermark text", None))
        self.watermark_angle_label.setText(QCoreApplication.translate("PageConfigWidget", u"Rotation angle", None))
        self.watermark_font_size_label.setText(QCoreApplication.translate("PageConfigWidget", u"Font size", None))
        self.watermark_color_label.setText(QCoreApplication.translate("PageConfigWidget", u"Text color and opacity", None))
        self.watermark_font_size.setSuffix("")
        self.watermark_color_button.setText(QCoreApplication.translate("PageConfigWidget", u"Select a color", None))
        self.watermark_color.setText("")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_watermark_settings), QCoreApplication.translate("PageConfigWidget", u"Watermark", None))
    # retranslateUi

