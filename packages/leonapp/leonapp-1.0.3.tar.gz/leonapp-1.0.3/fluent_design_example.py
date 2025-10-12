#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyQt5 Fluent Design示例 - 展示基本的Fluent Design组件用法
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    PushButton, PrimaryPushButton, DefaultPushButton,
    LineEdit, Slider, CheckBox, RadioButton, SwitchButton,
    ComboBox, SpinBox, DoubleSpinBox,
    CardWidget, TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel,
    ProgressBar, Avatar, ToolTipFilter,
    FluentTranslator
)

class FluentDesignExample(QWidget):
    """Fluent Design组件示例窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Fluent Design示例")
        self.resize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 添加标题
        title = TitleLabel("PyQt5 Fluent Design组件展示")
        subtitle = SubtitleLabel("本示例展示了PyQt-Fluent-Widgets库的基本组件用法")
        
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        
        # 创建按钮示例卡片
        buttons_card = CardWidget()
        buttons_layout = QVBoxLayout(buttons_card)
        buttons_layout.setContentsMargins(20, 20, 20, 20)
        
        buttons_title = SubtitleLabel("按钮组件")
        buttons_layout.addWidget(buttons_title)
        
        # 按钮布局
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)
        
        # 标准按钮
        standard_button = PushButton("标准按钮")
        buttons_row.addWidget(standard_button)
        
        # 主要按钮
        primary_button = PrimaryPushButton("主要按钮")
        buttons_row.addWidget(primary_button)
        
        # 默认按钮
        default_button = DefaultPushButton("默认按钮")
        buttons_row.addWidget(default_button)
        
        buttons_layout.addLayout(buttons_row)
        main_layout.addWidget(buttons_card)
        
        # 创建输入控件示例卡片
        inputs_card = CardWidget()
        inputs_layout = QVBoxLayout(inputs_card)
        inputs_layout.setContentsMargins(20, 20, 20, 20)
        
        inputs_title = SubtitleLabel("输入控件")
        inputs_layout.addWidget(inputs_title)
        
        # 文本输入框
        text_input = LineEdit()
        text_input.setPlaceholderText("请输入文本...")
        inputs_layout.addWidget(text_input)
        
        # 数字输入框
        spin_boxes_layout = QHBoxLayout()
        spin_boxes_layout.setSpacing(10)
        
        spin_box = SpinBox()
        spin_box.setRange(0, 100)
        spin_box.setValue(50)
        spin_boxes_layout.addWidget(QLabel("整数："))
        spin_boxes_layout.addWidget(spin_box)
        
        double_spin_box = DoubleSpinBox()
        double_spin_box.setRange(0.0, 1.0)
        double_spin_box.setSingleStep(0.1)
        double_spin_box.setValue(0.5)
        spin_boxes_layout.addWidget(QLabel("浮点数："))
        spin_boxes_layout.addWidget(double_spin_box)
        
        inputs_layout.addLayout(spin_boxes_layout)
        
        # 下拉列表
        combo_box = ComboBox()
        combo_box.addItems(["选项 1", "选项 2", "选项 3", "选项 4", "选项 5"])
        combo_box.setCurrentIndex(0)
        inputs_layout.addWidget(combo_box)
        
        main_layout.addWidget(inputs_card)
        
        # 创建选择控件示例卡片
        selection_card = CardWidget()
        selection_layout = QVBoxLayout(selection_card)
        selection_layout.setContentsMargins(20, 20, 20, 20)
        
        selection_title = SubtitleLabel("选择控件")
        selection_layout.addWidget(selection_title)
        
        # 复选框
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(20)
        
        checkbox1 = CheckBox("选项 1")
        checkbox2 = CheckBox("选项 2")
        checkbox3 = CheckBox("选项 3")
        checkbox3.setChecked(True)
        
        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        checkbox_layout.addWidget(checkbox3)
        
        selection_layout.addLayout(checkbox_layout)
        
        # 单选按钮
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(20)
        
        radio1 = RadioButton("选项 A")
        radio2 = RadioButton("选项 B")
        radio3 = RadioButton("选项 C")
        radio1.setChecked(True)
        
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addWidget(radio3)
        
        selection_layout.addLayout(radio_layout)
        
        # 开关按钮
        switch_layout = QHBoxLayout()
        switch_layout.setSpacing(10)
        
        switch_label = QLabel("启用功能：")
        switch_button = SwitchButton()
        switch_button.setChecked(True)
        
        switch_layout.addWidget(switch_label)
        switch_layout.addWidget(switch_button)
        switch_layout.addStretch()
        
        selection_layout.addLayout(switch_layout)
        
        main_layout.addWidget(selection_card)
        
        # 创建进度条示例卡片
        progress_card = CardWidget()
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        
        progress_title = SubtitleLabel("进度条")
        progress_layout.addWidget(progress_title)
        
        # 水平进度条
        progress_bar = ProgressBar()
        progress_bar.setValue(65)
        progress_layout.addWidget(progress_bar)
        
        main_layout.addWidget(progress_card)
        
        # 创建标签和头像示例卡片
        misc_card = CardWidget()
        misc_layout = QVBoxLayout(misc_card)
        misc_layout.setContentsMargins(20, 20, 20, 20)
        
        misc_title = SubtitleLabel("文本标签和头像")
        misc_layout.addWidget(misc_title)
        
        # 文本标签
        labels_layout = QVBoxLayout()
        labels_layout.setSpacing(5)
        
        title_label = TitleLabel("标题文本")
        subtitle_label = SubtitleLabel("副标题文本")
        body_label = BodyLabel("正文文本，这是一个普通的正文文本示例")
        caption_label = CaptionLabel("说明文本，通常用于辅助信息")
        
        labels_layout.addWidget(title_label)
        labels_layout.addWidget(subtitle_label)
        labels_layout.addWidget(body_label)
        labels_layout.addWidget(caption_label)
        
        misc_layout.addLayout(labels_layout)
        
        # 头像
        avatar_layout = QHBoxLayout()
        avatar_layout.setSpacing(10)
        
        avatar1 = Avatar("用户A", size=48)
        avatar2 = Avatar("用户B", size=64)
        avatar3 = Avatar("用户C", size=32)
        
        # 添加工具提示
        avatar1.installEventFilter(ToolTipFilter(avatar1))
        avatar1.setToolTip("用户A的头像")
        
        avatar2.installEventFilter(ToolTipFilter(avatar2))
        avatar2.setToolTip("用户B的头像")
        
        avatar3.installEventFilter(ToolTipFilter(avatar3))
        avatar3.setToolTip("用户C的头像")
        
        avatar_layout.addWidget(avatar1)
        avatar_layout.addWidget(avatar2)
        avatar_layout.addWidget(avatar3)
        avatar_layout.addStretch()
        
        misc_layout.addLayout(avatar_layout)
        
        main_layout.addWidget(misc_card)
        
        # 添加底部信息
        footer = CaptionLabel("PyQt5 Fluent Design示例 v1.0.0")
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
        
        # 添加伸缩项，使内容居中
        main_layout.addStretch(1)

if __name__ == "__main__":
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 添加中文支持
    translator = FluentTranslator()
    app.installTranslator(translator)
    
    # 创建并显示主窗口
    window = FluentDesignExample()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())