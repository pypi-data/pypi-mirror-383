#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LeonApp GUI - 基于PyQt5和Fluent Design的App Store API图形界面工具
"""

#
# 　　　┏┓　　　┏┓
# 　　┏┛┻━━━┛┻┓
# 　　┃　　　　　　　 ┃
# 　　┃　　　━　　　 ┃
# 　　┃　┳┛　┗┳　┃
# 　　┃　　　　　　　 ┃
# 　　┃　　　┻　　　 ┃
# 　　┃　　　　　　　 ┃
# 　　┗━┓　　　┏━┛Codes are far away from bugs with the animal protecting
# 　　　　┃　　　┃    神兽保佑,代码无bug
# 　　　　┃　　　┃
# 　　　　┃　　　┗━━━┓
# 　　　　┃　　　　　 ┣┓
# 　　　　┃　　　　 ┏┛
# 　　　　┗┓┓┏━┳┓┏┛
# 　　　　　┃┫┫　┃┫┫
# 　　　　　┗┻┛　┗┻┛
#

# APP版本号
APP_VERSION = "Prerelease 2"

import sys
import json
import requests
import traceback
import os
import datetime
import markdown
from enum import Enum
from loguru import logger
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QTableWidget, QTextEdit, QFrame, QHeaderView, QLabel, QSplashScreen
)
from PyQt5.QtGui import QTextOption, QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSize
from qfluentwidgets import (
    CardWidget, TitleLabel, SubtitleLabel, CaptionLabel, BodyLabel, PushButton,
    PrimaryPushButton, LineEdit, ComboBox, ProgressBar, TableWidget,
    ScrollArea, InfoBar, InfoBarPosition, NavigationInterface, NavigationItemPosition,
    FluentWindow, MSFluentWindow, FluentIcon, SimpleCardWidget, PrimaryPushSettingCard,
    OptionsSettingCard, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, OptionsValidator, qconfig, SplashScreen, NavigationAvatarWidget
)
from qfluentwidgets import FluentTranslator
from app_detail_window import AppDetailWindow

# 配置管理 - 使用QConfig管理配置
class AppConfig(QConfig):
    """应用配置类"""
    # 常规设置
    auto_open_installer = OptionsConfigItem(
        "General", "AutoOpenInstaller", True, 
        OptionsValidator([True, False])
    )
    
    # 应用打开方式
    # 0: Windows直接运行应用程序, 1: 打开文件夹方式
    app_open_method = OptionsConfigItem(
        "General", "AppOpenMethod", 0, 
        OptionsValidator([0, 1])
    )
    
    # 配置项已删除云母效果

# 创建配置文件目录
config_dir = os.path.join(os.path.dirname(__file__), "config")
os.makedirs(config_dir, exist_ok=True)

# 创建配置实例并使用配置文件来初始化它
app_config = AppConfig()
config_path = os.path.join(config_dir, "config.json")
qconfig.load(config_path, app_config)

def get_global_settings():
    """获取全局配置"""
    return app_config

class APIClient:
    """API客户端类，处理与API的通信"""
    def __init__(self, api_base_url="https://leon.miaostars.com/api.php"):
        self.api_base_url = api_base_url
        
    def make_request(self, endpoint_type, params=None):
        """基础API请求函数"""
        if params is None:
            params = {}
            
        # 添加API类型参数
        params['t'] = endpoint_type
        
        # 记录API请求开始
        logger.info(f"API请求开始: {endpoint_type}，参数: {params}")
        
        try:
            response = requests.get(self.api_base_url, params=params, timeout=30)
            response.raise_for_status()  # 抛出HTTP错误
            
            logger.info(f"API请求成功: {endpoint_type}，状态码: {response.status_code}")
            
            data = response.json()
            
            # 添加返回数据日志，限制数据量大小
            import json
            data_str = json.dumps(data, ensure_ascii=False)
            if len(data_str) > 500:
                # 如果数据太大，只记录部分内容
                logger.info(f"API返回数据: {endpoint_type}，数据长度: {len(data_str)} 字符，前500字符: {data_str[:500]}...")
            else:
                logger.info(f"API返回数据: {endpoint_type}，完整数据: {data_str}")
            
            if data.get('status') == 'error':
                error_msg = data.get('message', '未知错误')
                logger.error(f"API返回错误: {endpoint_type} - {error_msg}")
                return {'error': error_msg}
            
            logger.info(f"API响应成功: {endpoint_type}，数据获取完成")
            return {'success': True, 'data': data.get('data')}
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {endpoint_type} - {str(e)}")
            return {'error': f"请求异常: {str(e)}"}
        except json.JSONDecodeError:
            logger.error(f"API响应解析失败: {endpoint_type}")
            return {'error': "无法解析响应"}

class WorkerThread(QThread):
    """工作线程，用于在后台执行API请求"""
    # 使用object类型以接受任何数据类型（dict、list等）
    finished = pyqtSignal(object)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, api_client, endpoint_type, params=None):
        super().__init__()
        self.api_client = api_client
        self.endpoint_type = endpoint_type
        self.params = params or {}
        
    def run(self):
        """线程运行函数"""
        try:
            self.progress.emit(10)
            result = self.api_client.make_request(self.endpoint_type, self.params)
            self.progress.emit(100)
            if 'error' in result:
                self.error.emit(result['error'])
            else:
                # 确保数据是可序列化的对象
                if isinstance(result['data'], (dict, list, str, int, float, bool, type(None))):
                    self.finished.emit(result['data'])
                else:
                    self.error.emit(f"API返回的数据类型不支持: {type(result['data'])}")
        except Exception as e:
            self.error.emit(f"执行错误: {str(e)}")

class HomepageTab(QWidget):
    """主页标签页 - 显示最新增加的APP和最新的公告"""
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel("欢迎使用 LeonApp")
        layout.addWidget(title)
        
        # 添加副标题
        subtitle = SubtitleLabel("这是应用商店的管理工具，用于查看和管理应用、标签和开发者信息。")
        layout.addWidget(subtitle)
        
        # 添加分隔符
        layout.addSpacing(20)
        
        # 创建最新应用部分
        latest_apps_title = SubtitleLabel("最新添加的应用")
        layout.addWidget(latest_apps_title)
        
        # 创建最新应用卡片
        self.latest_apps_card = CardWidget()
        apps_layout = QVBoxLayout(self.latest_apps_card)
        apps_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建水平滚动区域来放置应用卡片 - 设置为隐形样式
        self.apps_scroll_area = ScrollArea()
        self.apps_scroll_area.setWidgetResizable(True)
        self.apps_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.apps_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置隐形样式
        self.apps_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:horizontal {
                height: 0px;
                background: transparent;
            }
            QScrollBar::handle:horizontal {
                background: transparent;
                min-width: 0px;
            }
        """)
        
        # 创建水平布局来放置卡片
        self.apps_container = QWidget()
        self.apps_layout = QHBoxLayout(self.apps_container)
        self.apps_layout.setContentsMargins(0, 0, 0, 0)
        self.apps_layout.setSpacing(15)
        
        # 设置滚动区域的内容
        self.apps_scroll_area.setWidget(self.apps_container)
        self.apps_scroll_area.setMaximumHeight(1000)
        self.apps_scroll_area.setMaximumWidth(1000)
        self.apps_scroll_area.setMinimumWidth(1000)
        apps_layout.addWidget(self.apps_scroll_area)
        

        
        layout.addWidget(self.latest_apps_card)
        
        # 添加分隔符
        layout.addSpacing(20)
        
        # 创建最新公告部分
        latest_announcements_title = SubtitleLabel("最新公告")
        layout.addWidget(latest_announcements_title)
        
        # 创建最新公告卡片
        self.latest_announcements_card = CardWidget()
        announcements_layout = QVBoxLayout(self.latest_announcements_card)
        announcements_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建最新公告列表
        self.latest_announcements_list = QWidget()
        self.latest_announcements_list_layout = QVBoxLayout(self.latest_announcements_list)
        self.latest_announcements_list_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域放置公告列表 - 设置为隐形样式
        scroll_area = ScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 设置隐形样式
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 0px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: transparent;
                min-height: 0px;
            }
        """)
        scroll_area.setWidget(self.latest_announcements_list)
        scroll_area.setMaximumHeight(300)
        announcements_layout.addWidget(scroll_area)
        

        
        layout.addWidget(self.latest_announcements_card)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 添加填充，使内容上移
        layout.addStretch()
        
    def load_data(self):
        """加载最新应用和公告数据"""
        self.show_progress()
        
        # 加载最新应用
        self.apps_worker = WorkerThread(
            self.api_client,
            'getallapps',
            {'page': 1, 'limit': 5, 'sort': 'latest'}  # 获取最新的5个应用
        )
        self.apps_worker.finished.connect(self.on_latest_apps_loaded)
        self.apps_worker.progress.connect(self.update_progress)
        self.apps_worker.error.connect(self.show_error)
        self.apps_worker.start()
        
        # 加载最新公告
        self.announcements_worker = WorkerThread(
            self.api_client,
            'getacc',
            {'page': 1, 'limit': 3}  # 获取最新的3个公告
        )
        self.announcements_worker.finished.connect(self.on_latest_announcements_loaded)
        self.announcements_worker.progress.connect(self.update_progress)
        self.announcements_worker.error.connect(self.show_error)
        self.announcements_worker.start()
        
    def on_latest_apps_loaded(self, data):
        """最新应用加载完成处理"""
        # 清空现有卡片
        while self.apps_layout.count() > 0:
            item = self.apps_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if data and isinstance(data, dict) and 'apps' in data and isinstance(data['apps'], list):
            # 为每个应用创建卡片
            index = 0
            for app in data['apps']:
                if not isinstance(app, dict):
                    continue
                     
                # 只显示前三个应用
                if index >= 3:
                    break
                index += 1
                    
                # 创建卡片 - 微软商店风格
                app_card = CardWidget()
                app_card.setFixedWidth(160)  # 固定卡片宽度
                app_card.setFixedHeight(220) # 固定卡片高度
                # 使用样式表设置圆角并移除边框
                app_card.setStyleSheet("""
                    QWidget {
                        border-radius: 12px;
                        border: none;
                    }
                """)
                
                # 创建卡片内容布局
                card_layout = QVBoxLayout(app_card)
                card_layout.setContentsMargins(12, 12, 12, 12)
                card_layout.setSpacing(8)  # 调整间距
                
                # 添加应用ID（隐藏）
                app_id_label = QLabel(str(app.get('id', '')))
                app_id_label.setVisible(False)
                card_layout.addWidget(app_id_label)
                
                # 添加应用图标占位区 - 微软商店风格的图标位置
                icon_widget = QWidget()
                icon_widget.setFixedSize(100, 100)
                icon_layout = QVBoxLayout(icon_widget)
                icon_layout.setAlignment(Qt.AlignCenter)
                
                # 创建图标占位符（实际应用中可以替换为真实图标）
                placeholder_label = QLabel()
                placeholder_label.setFixedSize(80, 80)
                placeholder_label.setStyleSheet("""
                    background-color: #f0f0f0;
                    border-radius: 12px;
                    font-size: 32px;
                    color: #666;
                """)
                placeholder_label.setAlignment(Qt.AlignCenter)
                # 使用应用名称的第一个字符作为图标占位符
                first_char = app.get('name', 'A')[0].upper() if app.get('name') else 'A'
                placeholder_label.setText(first_char)
                
                icon_layout.addWidget(placeholder_label)
                card_layout.addWidget(icon_widget, alignment=Qt.AlignCenter)
                
                # 添加应用名称 - 限制为2行
                name_label = SubtitleLabel(app.get('name', '无名称'))
                name_label.setWordWrap(True)
                name_label.setMaximumHeight(40)  # 限制高度，最多显示2行
                name_label.setStyleSheet("""
                    QLabel {
                        font-weight: 500;
                        font-size: 14px;
                    }
                """)
                card_layout.addWidget(name_label)
                
                # 添加应用版本和添加时间（合并显示）
                version = app.get('version', '未知')
                created_at = app.get('created_at', '未知')
                # 简化时间显示
                if created_at != '未知':
                    try:
                        # 假设时间格式为ISO格式，提取日期部分
                        if 'T' in created_at:
                            created_at = created_at.split('T')[0]
                    except:
                        pass
                
                info_label = CaptionLabel(f"版本 {version} · {created_at}")
                info_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-size: 12px;
                    }
                """)
                card_layout.addWidget(info_label)
                
                # 添加获取按钮（模拟微软商店的获取按钮）- 使用PrimaryPushButton获得标准的蓝色按钮
                get_button = PrimaryPushButton("查看详情")
                get_button.setFixedHeight(32)
                
                get_button.clicked.connect(lambda checked, app_id=app.get('id', ''): self.show_app_detail(app_id))
                card_layout.addWidget(get_button)
                
                # 添加点击事件到整个卡片
                app_card.mousePressEvent = lambda event, app_id=app.get('id', ''): self.show_app_detail(app_id)
                
                # 将卡片添加到水平布局
                self.apps_layout.addWidget(app_card)
        
        # 添加一个占位符，确保卡片不会被拉伸
        self.apps_layout.addStretch()
        
        # 检查是否还有其他数据正在加载
        if not self.apps_worker.isRunning() and not self.announcements_worker.isRunning():
            self.hide_progress()
            
    def on_latest_announcements_loaded(self, data):
        """最新公告加载完成处理"""
        # 清空公告列表
        while self.latest_announcements_list_layout.count() > 0:
            item = self.latest_announcements_list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        announcements = []
        if data and isinstance(data, dict) and 'announcements' in data and isinstance(data['announcements'], list):
            announcements = data['announcements']
        elif data and isinstance(data, list):
            announcements = data
        
        if not announcements:
            # 如果没有公告，显示提示信息
            no_announcement_label = CaptionLabel("暂无公告")
            no_announcement_label.setAlignment(Qt.AlignCenter)
            self.latest_announcements_list_layout.addWidget(no_announcement_label)
        else:
            # 只显示最新的公告
            announcement = announcements[0]  # 只取最新的一个公告
            if not isinstance(announcement, dict):
                return
                
            # 创建公告卡片
            announcement_item = QWidget()
            announcement_layout = QVBoxLayout(announcement_item)
            announcement_layout.setContentsMargins(0, 0, 0, 10)
            
            # 添加标题
            title_label = SubtitleLabel(announcement.get('title', '无标题'))
            announcement_layout.addWidget(title_label)
            
            # 添加发布时间
            time_label = CaptionLabel(f"发布时间: {announcement.get('created_at', '未知时间')}")
            announcement_layout.addWidget(time_label)
            
            # 添加内容 - 支持Markdown格式
            content_text_edit = QTextEdit()
            content_text_edit.setReadOnly(True)  # 设置为只读
            content_text_edit.setFrameShape(QFrame.NoFrame)  # 无边框
            content_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 必要时显示滚动条
            content_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 不显示水平滚动条
            
            # 将Markdown内容转换为HTML并显示
            content = announcement.get('content', '无内容')
            try:
                html_content = markdown.markdown(content)
                content_text_edit.setHtml(html_content)
            except Exception as e:
                # 如果Markdown解析失败，显示原始文本
                content_text_edit.setPlainText(content)
                print(f"Markdown解析错误: {str(e)}")
            
            # 设置最大高度，避免内容过长占用过多空间
            content_text_edit.setMaximumHeight(200)
            announcement_layout.addWidget(content_text_edit)
            
            # 添加到布局
            self.latest_announcements_list_layout.addWidget(announcement_item)
        
        # 检查是否还有其他数据正在加载
        if not self.apps_worker.isRunning() and not self.announcements_worker.isRunning():
            self.hide_progress()
            
    def show_app_detail(self, app_id):
        """显示应用详情"""
        # 直接创建并显示应用详情窗口
        detail_window = AppDetailWindow(self.api_client, app_id, self)
        detail_window.show()
            
    def show_announcement_detail(self, announcement_id):
        """显示公告详情方法已被移除，现在主页直接显示最新公告内容"""
        pass
            


            
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class AppTab(QWidget):
    """应用列表标签页"""
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        # 先初始化分页相关变量，因为init_ui()内部会调用load_apps()
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel("应用列表")
        layout.addWidget(title)
        
        # 创建搜索和过滤器区域
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 10, 0, 10)
        
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("搜索应用...")
        filter_layout.addWidget(self.search_input, 3)
        
        filter_layout.addSpacing(10)
        
        self.page_size_combo = ComboBox()
        self.page_size_combo.addItems(["10", "20", "50", "100"])
        self.page_size_combo.setCurrentText("20")
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        filter_layout.addWidget(CaptionLabel("每页显示:"))
        filter_layout.addWidget(self.page_size_combo)
        
        filter_layout.addSpacing(10)
        
        search_button = PrimaryPushButton("搜索")
        search_button.clicked.connect(self.search_apps)
        filter_layout.addWidget(search_button)
        
        layout.addLayout(filter_layout)
        
        # 创建表格
        self.table = TableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "应用名称", "版本", "评分", "下载量"])
        self.table.horizontalHeader().setSectionResizeMode(1, 3)
        self.table.cellDoubleClicked.connect(self.show_app_detail)
        layout.addWidget(self.table)
        
        # 创建分页控制
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 10, 0, 0)
        
        self.prev_button = PushButton("上一页")
        self.prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_button)
        
        self.page_label = CaptionLabel("第 1 页，共 1 页")
        pagination_layout.addWidget(self.page_label, alignment=Qt.AlignCenter)
        
        self.next_button = PushButton("下一页")
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)
        
        layout.addLayout(pagination_layout)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 加载初始数据
        self.load_apps()
        
    def load_apps(self):
        """加载应用列表"""
        self.show_progress()
        self.worker = WorkerThread(
            self.api_client, 
            'getallapps', 
            {'page': self.current_page, 'limit': self.items_per_page}
        )
        self.worker.finished.connect(self.on_apps_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_apps_loaded(self, data):
        """应用列表加载完成处理"""
        self.hide_progress()
        
        if not data or 'apps' not in data or 'pagination' not in data:
            self.show_error("数据格式错误")
            return
        
        # 清空表格
        self.table.setRowCount(0)
        
        # 填充表格
        for app in data['apps']:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            
            self.table.setItem(row_pos, 0, QTableWidgetItem(str(app.get('id', ''))))
            self.table.setItem(row_pos, 1, QTableWidgetItem(app.get('name', '')))
            self.table.setItem(row_pos, 2, QTableWidgetItem(app.get('version', '')))
            self.table.setItem(row_pos, 3, QTableWidgetItem(str(app.get('avg_rating', '暂无'))))
            self.table.setItem(row_pos, 4, QTableWidgetItem(str(app.get('total_downloads', 0))))
        
        # 更新分页信息
        self.total_pages = data['pagination']['totalPages']
        self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        
        # 更新按钮状态
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        
    def search_apps(self):
        """搜索应用"""
        search_text = self.search_input.text().strip()
        if search_text:
            self.current_page = 1
            self.show_progress()
            self.worker = WorkerThread(
                self.api_client, 
                'getallapps', 
                {'page': 1, 'limit': self.items_per_page, 'search': search_text}
            )
            self.worker.finished.connect(self.on_apps_loaded)
            self.worker.progress.connect(self.update_progress)
            self.worker.error.connect(self.show_error)
            self.worker.start()
        else:
            self.load_apps()
            
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_apps()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_apps()
            
    def on_page_size_changed(self, value):
        """每页显示数量变化"""
        self.items_per_page = int(value)
        self.current_page = 1
        self.load_apps()
        
    def show_app_detail(self, row, column):
        """显示应用详情"""
        app_id = self.table.item(row, 0).text()
        # 直接创建应用详情窗口，使用文件顶部已导入的AppDetailWindow类
        self.app_detail_window = AppDetailWindow(self.api_client, app_id, self)
        self.app_detail_window.show()
        
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        # 使用Sweet Alert风格的弹窗
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class TagTab(QWidget):
    """标签管理标签页"""
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.parent = parent
        # 初始化分页相关变量
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.init_ui()
        # 加载所有标签
        self.load_tags()
        
    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel("标签管理")
        layout.addWidget(title)
        
        # 创建标签ID输入框和按钮
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 10, 0, 10)
        
        self.tag_id_input = LineEdit()
        self.tag_id_input.setPlaceholderText("输入标签ID...")
        input_layout.addWidget(self.tag_id_input, 3)
        
        input_layout.addSpacing(10)
        
        app_list_button = PrimaryPushButton("查看应用列表")
        app_list_button.clicked.connect(self.show_tag_apps_by_id_input)
        input_layout.addWidget(app_list_button)
        
        input_layout.addSpacing(10)
        
        # 添加刷新按钮
        refresh_button = PushButton("刷新标签列表")
        refresh_button.clicked.connect(self.load_tags)
        input_layout.addWidget(refresh_button)
        
        layout.addLayout(input_layout)
        
        # 创建标签列表
        self.tag_list = TableWidget()
        self.tag_list.setColumnCount(2)
        self.tag_list.setHorizontalHeaderLabels(["ID", "标签名称"])
        self.tag_list.horizontalHeader().setSectionResizeMode(1, 3)
        self.tag_list.cellDoubleClicked.connect(self.show_tag_apps)
        layout.addWidget(self.tag_list)
        
        # 创建分页控制
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 10, 0, 10)
        
        self.prev_button = PushButton("上一页")
        self.prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_button)
        
        self.page_label = CaptionLabel("第 1 页，共 1 页")
        pagination_layout.addWidget(self.page_label, alignment=Qt.AlignCenter)
        
        self.next_button = PushButton("下一页")
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)
        
        layout.addLayout(pagination_layout)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def load_tags(self):
        """加载标签数据"""
        self.show_progress()
        self.worker = WorkerThread(
            self.api_client, 
            'getalltags', 
            {'page': self.current_page, 'limit': self.items_per_page}
        )
        self.worker.finished.connect(self.on_tags_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_tags_loaded(self, data):
        """标签数据加载完成处理"""
        self.hide_progress()
        
        # 增强的数据格式验证，提供更具体的错误信息
        if data is None:
            self.show_error("API返回数据为空")
            return
        
        # 处理数据 - 如果是列表类型，转换为预期的字典格式
        processed_data = {}
        if isinstance(data, list):
            # API返回了列表，我们将其转换为预期的字典结构
            processed_data['tags'] = data
            # 构建简单的分页信息
            total_items = len(data)
            total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
            processed_data['pagination'] = {'totalPages': total_pages}
        elif isinstance(data, dict):
            # 保留原有的字典处理逻辑，但添加更灵活的验证
            processed_data = data.copy()
            
            # 验证必要字段是否存在，如果不存在则使用默认值
            if 'tags' not in processed_data:
                processed_data['tags'] = []
            elif not isinstance(processed_data['tags'], list):
                # 如果tags不是列表，尝试转换或使用空列表
                try:
                    processed_data['tags'] = [processed_data['tags']]
                except:
                    processed_data['tags'] = []
            
            if 'pagination' not in processed_data:
                # 如果没有分页信息，计算简单的分页
                total_items = len(processed_data['tags'])
                total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
                processed_data['pagination'] = {'totalPages': total_pages}
            elif not isinstance(processed_data['pagination'], dict):
                # 如果pagination不是字典，创建默认分页信息
                processed_data['pagination'] = {'totalPages': 1}
            
            # 确保分页信息中有totalPages
            if 'totalPages' not in processed_data['pagination']:
                processed_data['pagination']['totalPages'] = 1
        else:
            self.show_error(f"数据格式错误: 期望字典或列表类型，实际为{type(data).__name__}")
            return
        
        # 清空表格
        self.tag_list.setRowCount(0)
        
        # 填充表格，添加更健壮的数据处理
        tags_to_display = processed_data['tags'] if isinstance(processed_data['tags'], list) else []
        for tag in tags_to_display:
            # 确保tag是字典类型
            if not isinstance(tag, dict):
                continue
                
            row_pos = self.tag_list.rowCount()
            self.tag_list.insertRow(row_pos)
            
            # 安全获取字段值，避免KeyError
            tag_id = str(tag.get('id', '未知ID'))
            tag_name = tag.get('name', '无名称')
            
            self.tag_list.setItem(row_pos, 0, QTableWidgetItem(tag_id))
            self.tag_list.setItem(row_pos, 1, QTableWidgetItem(tag_name))
        
        # 更新分页信息，增加异常处理
        try:
            self.total_pages = int(processed_data['pagination']['totalPages'])
            self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        except (ValueError, TypeError):
            self.total_pages = 1
            self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
            
        # 更新按钮状态
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_tags()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_tags()
            
    def show_tag_apps(self, row, column):
        """显示标签下的应用"""
        tag_id = self.tag_list.item(row, 0).text()
        tag_name = self.tag_list.item(row, 1).text()
        # 直接创建并显示标签应用窗口
        tag_apps_window = TagAppsWindow(self.api_client, tag_id, tag_name, self)
        tag_apps_window.show()
        
    def show_tag_apps_by_id_input(self):
        """通过输入框中的ID查看标签下的应用列表"""
        tag_id = self.tag_id_input.text().strip()
        if tag_id:
            # 先获取标签名称
            self.show_progress()
            self.worker = WorkerThread(
                self.api_client, 
                'gettagapps', 
                {'id': tag_id, 'page': 1, 'limit': 1}
            )
            self.worker.finished.connect(lambda data, tid=tag_id: self.on_tag_info_loaded(data, tid))
            self.worker.progress.connect(self.update_progress)
            self.worker.error.connect(self.show_error)
            self.worker.start()
        else:
            InfoBar.warning(
                title="警告",
                content="请输入标签ID",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )
            
    def on_tag_info_loaded(self, data, tag_id):
        """标签信息加载完成处理"""
        self.hide_progress()
        
        if data and 'apps' in data and data['apps']:
            # 从第一个应用中获取标签名称
            tag_name = "标签名称未知"
            if data['apps'] and isinstance(data['apps'], list):
                first_app = data['apps'][0]
                if 'tags' in first_app and isinstance(first_app['tags'], list) and first_app['tags']:
                    tag_name = first_app['tags'][0].get('name', f"标签{tag_id}")
            
            # 打开标签应用列表窗口
            tag_apps_window = TagAppsWindow(self.api_client, tag_id, tag_name, self)
            tag_apps_window.show()
        else:
            self.show_error("未找到该标签的信息")
        
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class DeveloperTab(QWidget):
    """开发者管理标签页"""
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.parent = parent
        # 初始化分页相关变量
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.init_ui()
        # 加载所有开发者
        self.load_developers()
        
    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel("开发者管理")
        layout.addWidget(title)
        
        # 创建开发者ID输入框和按钮
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 10, 0, 10)
        
        self.developer_id_input = LineEdit()
        self.developer_id_input.setPlaceholderText("输入开发者ID...")
        input_layout.addWidget(self.developer_id_input, 3)
        
        input_layout.addSpacing(10)
        
        app_list_button = PrimaryPushButton("查看应用列表")
        app_list_button.clicked.connect(self.show_developer_apps)
        input_layout.addWidget(app_list_button)
        
        input_layout.addSpacing(10)
        
        info_button = PushButton("查看开发者信息")
        info_button.clicked.connect(self.show_developer_info)
        input_layout.addWidget(info_button)
        
        input_layout.addSpacing(10)
        
        # 添加刷新按钮
        refresh_button = PushButton("刷新开发者列表")
        refresh_button.clicked.connect(self.load_developers)
        input_layout.addWidget(refresh_button)
        
        layout.addLayout(input_layout)
        
        # 创建开发者列表
        self.developers_table = TableWidget()
        self.developers_table.setColumnCount(4)
        self.developers_table.setHorizontalHeaderLabels(["ID", "开发者名称", "应用数量", "注册时间"])
        self.developers_table.horizontalHeader().setSectionResizeMode(1, 3)
        self.developers_table.cellDoubleClicked.connect(self.on_developer_double_clicked)
        layout.addWidget(self.developers_table)
        
        # 创建分页控制
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 10, 0, 10)
        
        self.prev_button = PushButton("上一页")
        self.prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_button)
        
        self.page_label = CaptionLabel("第 1 页，共 1 页")
        pagination_layout.addWidget(self.page_label, alignment=Qt.AlignCenter)
        
        self.next_button = PushButton("下一页")
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)
        
        layout.addLayout(pagination_layout)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def load_developers(self):
        """加载所有开发者"""
        self.show_progress()
        self.worker = WorkerThread(
            self.api_client, 
            'getalldevelopers', 
            {'page': self.current_page, 'limit': self.items_per_page}
        )
        self.worker.finished.connect(self.on_developers_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_developers_loaded(self, data):
        """开发者列表加载完成处理"""
        self.hide_progress()
        
        # 增强的数据格式验证
        if data is None:
            self.show_error("API返回数据为空")
            return
        
        # 处理数据 - 如果是列表类型，转换为预期的字典格式
        processed_data = {}  
        if isinstance(data, list):
            # API返回了列表，我们将其转换为预期的字典结构
            processed_data['developers'] = data
            # 构建简单的分页信息
            total_items = len(data)
            total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
            processed_data['pagination'] = {'totalPages': total_pages}
        elif isinstance(data, dict):
            # 保留原有的字典处理逻辑，但添加更灵活的验证
            processed_data = data.copy()
            
            # 验证必要字段是否存在，如果不存在则使用默认值
            if 'developers' not in processed_data:
                processed_data['developers'] = []
            elif not isinstance(processed_data['developers'], list):
                # 如果developers不是列表，尝试转换或使用空列表
                try:
                    processed_data['developers'] = [processed_data['developers']]
                except:
                    processed_data['developers'] = []
            
            if 'pagination' not in processed_data:
                # 如果没有分页信息，计算简单的分页
                total_items = len(processed_data['developers'])
                total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
                processed_data['pagination'] = {'totalPages': total_pages}
            elif not isinstance(processed_data['pagination'], dict):
                # 如果pagination不是字典，创建默认分页信息
                processed_data['pagination'] = {'totalPages': 1}
            
            # 确保分页信息中有totalPages
            if 'totalPages' not in processed_data['pagination']:
                processed_data['pagination']['totalPages'] = 1
        else:
            self.show_error(f"数据格式错误: 期望字典或列表类型，实际为{type(data).__name__}")
            return
        
        # 清空表格
        self.developers_table.setRowCount(0)
        
        # 填充表格，添加更健壮的数据处理
        developers_to_display = processed_data['developers'] if isinstance(processed_data['developers'], list) else []
        for developer in developers_to_display:
            # 确保developer是字典类型
            if not isinstance(developer, dict):
                continue
                
            row_pos = self.developers_table.rowCount()
            self.developers_table.insertRow(row_pos)
            
            # 安全获取字段值，避免KeyError
            dev_id = str(developer.get('id', '未知ID'))
            dev_name = developer.get('username', '无名称')
            app_count = str(developer.get('app_count', 0))
            created_at = developer.get('created_at', '未知时间')
            
            self.developers_table.setItem(row_pos, 0, QTableWidgetItem(dev_id))
            self.developers_table.setItem(row_pos, 1, QTableWidgetItem(dev_name))
            self.developers_table.setItem(row_pos, 2, QTableWidgetItem(app_count))
            self.developers_table.setItem(row_pos, 3, QTableWidgetItem(created_at))
        
        # 更新分页信息，增加异常处理
        try:
            self.total_pages = int(processed_data['pagination']['totalPages'])
            self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        except (ValueError, TypeError):
            self.total_pages = 1
            self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
            
        # 更新按钮状态
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_developers()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_developers()
            
    def on_developer_double_clicked(self, row, column):
        """双击开发者行查看详情"""
        developer_id = self.developers_table.item(row, 0).text()
        # 显示开发者信息
        self.show_developer_info_by_id(developer_id)
        
    def show_developer_apps(self):
        """查看开发者的应用列表"""
        developer_id = self.developer_id_input.text().strip()
        if developer_id:
            # 直接创建并显示开发者应用窗口
            developer_apps_window = DeveloperAppsWindow(self.api_client, developer_id, self)
            developer_apps_window.show()
        else:
            InfoBar.warning(
                title="警告",
                content="请输入开发者ID",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )
            
    def show_developer_info(self):
        """查看开发者信息"""
        developer_id = self.developer_id_input.text().strip()
        if developer_id:
            self.show_developer_info_by_id(developer_id)
        else:
            InfoBar.warning(
                title="警告",
                content="请输入开发者ID",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
            duration=3000,
            parent=self
        )
            
    def show_developer_info_by_id(self, developer_id):
        """根据ID显示开发者信息"""
        # 直接创建并显示开发者信息窗口
        developer_info_window = DeveloperInfoWindow(self.api_client, developer_id, self)
        developer_info_window.show()
        
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )
        if developer_id:
            # 直接创建并显示开发者信息窗口，而不是调用parent方法
            developer_info_window = DeveloperInfoWindow(self.api_client, developer_id, self)
            developer_info_window.show()
        else:
            InfoBar.warning(
                title="警告",
                content="请输入开发者ID",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )
            
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class AnnouncementTab(QWidget):
    """公告管理标签页"""
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        # 先初始化分页相关变量，因为init_ui()内部会调用load_announcements()
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel("公告管理")
        layout.addWidget(title)
        
        # 创建分页控制
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 10, 0, 10)
        
        self.prev_button = PushButton("上一页")
        self.prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_button)
        
        self.page_label = CaptionLabel("第 1 页，共 1 页")
        pagination_layout.addWidget(self.page_label, alignment=Qt.AlignCenter)
        
        self.next_button = PushButton("下一页")
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)
        
        layout.addLayout(pagination_layout)
        
        # 创建公告列表
        self.announcement_list = TableWidget()
        self.announcement_list.setColumnCount(3)
        self.announcement_list.setHorizontalHeaderLabels(["ID", "标题", "发布时间"])
        self.announcement_list.horizontalHeader().setSectionResizeMode(1, 3)
        self.announcement_list.cellDoubleClicked.connect(self.show_announcement_detail)
        
        # 设置表格为只读
        self.announcement_list.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.announcement_list)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 加载初始数据
        self.load_announcements()
        
    def load_announcements(self):
        """加载公告列表"""
        self.show_progress()
        self.worker = WorkerThread(
            self.api_client, 
            'getacc', 
            {'page': self.current_page, 'limit': self.items_per_page}
        )
        self.worker.finished.connect(self.on_announcements_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_announcements_loaded(self, data):
        """公告列表加载完成处理"""
        self.hide_progress()
        
        # 增强的数据格式验证，提供更具体的错误信息
        if data is None:
            self.show_error("API返回数据为空")
            return
        
        # 处理数据 - 如果是列表类型，转换为预期的字典格式
        processed_data = {}
        if isinstance(data, list):
            # API返回了列表，我们将其转换为预期的字典结构
            processed_data['announcements'] = data
            # 构建简单的分页信息
            total_items = len(data)
            total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
            processed_data['pagination'] = {'totalPages': total_pages}
        elif isinstance(data, dict):
            # 保留原有的字典处理逻辑，但添加更灵活的验证
            processed_data = data.copy()
            
            # 验证必要字段是否存在，如果不存在则使用默认值
            if 'announcements' not in processed_data:
                processed_data['announcements'] = []
            elif not isinstance(processed_data['announcements'], list):
                # 如果announcements不是列表，尝试转换或使用空列表
                try:
                    processed_data['announcements'] = [processed_data['announcements']]
                except:
                    processed_data['announcements'] = []
            
            if 'pagination' not in processed_data:
                # 如果没有分页信息，计算简单的分页
                total_items = len(processed_data['announcements'])
                total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
                processed_data['pagination'] = {'totalPages': total_pages}
            elif not isinstance(processed_data['pagination'], dict):
                # 如果pagination不是字典，创建默认分页信息
                processed_data['pagination'] = {'totalPages': 1}
            
            # 确保分页信息中有totalPages
            if 'totalPages' not in processed_data['pagination']:
                processed_data['pagination']['totalPages'] = 1
        else:
            self.show_error(f"数据格式错误: 期望字典或列表类型，实际为{type(data).__name__}")
            return
        
        # 清空表格
        self.announcement_list.setRowCount(0)
        
        # 填充表格，添加更健壮的数据处理
        for announcement in processed_data['announcements']:
            # 确保announcement是字典类型
            if not isinstance(announcement, dict):
                continue
                
            row_pos = self.announcement_list.rowCount()
            self.announcement_list.insertRow(row_pos)
            
            # 安全获取字段值，避免KeyError
            self.announcement_list.setItem(row_pos, 0, QTableWidgetItem(str(announcement.get('id', '未知ID'))))
            self.announcement_list.setItem(row_pos, 1, QTableWidgetItem(announcement.get('title', '无标题')))
            self.announcement_list.setItem(row_pos, 2, QTableWidgetItem(announcement.get('created_at', '未知时间')))
        
        # 更新分页信息，增加异常处理
        try:
            self.total_pages = int(processed_data['pagination']['totalPages'])
            self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        except (ValueError, TypeError):
            self.total_pages = 1
            self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
            
        # 更新按钮状态
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_announcements()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_announcements()
            
    def show_announcement_detail(self, row, column):
        """显示公告详情"""
        announcement_id = self.announcement_list.item(row, 0).text()
        title = self.announcement_list.item(row, 1).text()
        created_at = self.announcement_list.item(row, 2).text()
        
        # 查找完整的公告数据
        for i in range(self.announcement_list.rowCount()):
            if self.announcement_list.item(i, 0).text() == announcement_id:
                # 获取完整的公告内容
                # 由于表格中没有直接存储content，我们需要重新获取
                self.show_progress()
                self.detail_worker = WorkerThread(
                    self.api_client,
                    'getacc',
                    {'page': 1, 'limit': 100}  # 获取足够多的公告以确保找到目标公告
                )
                self.detail_worker.finished.connect(lambda data, aid=announcement_id, t=title, ca=created_at: 
                                                   self.on_announcement_detail_loaded(data, aid, t, ca))
                self.detail_worker.progress.connect(self.update_progress)
                self.detail_worker.error.connect(self.show_error)
                self.detail_worker.start()
                break
    
    def on_announcement_detail_loaded(self, data, announcement_id, title, created_at):
        """公告详情加载完成处理"""
        self.hide_progress()
        
        # 增强的数据格式验证
        if data is None:
            self.show_error("获取公告详情失败: API返回数据为空")
            return
        
        # 处理数据 - 支持字典或列表类型
        processed_data = {}
        if isinstance(data, list):
            # API返回了列表，转换为预期的字典结构
            processed_data['announcements'] = data
        elif isinstance(data, dict):
            # 保留字典处理逻辑，但添加更灵活的验证
            processed_data = data.copy()
            
            # 验证必要字段是否存在
            if 'announcements' not in processed_data:
                processed_data['announcements'] = []
            elif not isinstance(processed_data['announcements'], list):
                # 尝试转换announcements为列表类型
                try:
                    processed_data['announcements'] = [processed_data['announcements']]
                except:
                    processed_data['announcements'] = []
        else:
            self.show_error(f"获取公告详情失败: 数据格式错误，期望字典或列表类型，实际为{type(data).__name__}")
            return
        
        # 查找特定的公告，增加异常处理
        content = "无内容"
        try:
            for announcement in processed_data['announcements']:
                if not isinstance(announcement, dict):
                    continue
                    
                if str(announcement.get('id', '')) == announcement_id:
                    content = announcement.get('content', '无内容')
                    break
        except Exception as e:
            self.show_error(f"查找公告详情时发生错误: {str(e)}")
            return
        
        # 创建并显示公告详情窗口
        detail_window = AnnouncementDetailWindow(self.api_client, announcement_id, title, created_at, content, self)
        detail_window.show()
        
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class StatsTab(QWidget):
    """统计信息标签页"""
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel("应用商店统计信息")
        layout.addWidget(title)
        
        # 创建统计卡片容器
        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(20)
        
        # 创建统计卡片
        self.app_count_card = CardWidget()
        self.app_count_card.setMinimumHeight(100)
        self.app_count_layout = QVBoxLayout(self.app_count_card)
        self.app_count_title = SubtitleLabel("应用总数")
        self.app_count_value = TitleLabel("--")
        self.app_count_layout.addWidget(self.app_count_title)
        self.app_count_layout.addWidget(self.app_count_value, alignment=Qt.AlignCenter)
        cards_layout.addWidget(self.app_count_card)
        
        self.developer_count_card = CardWidget()
        self.developer_count_card.setMinimumHeight(100)
        self.developer_count_layout = QVBoxLayout(self.developer_count_card)
        self.developer_count_title = SubtitleLabel("开发者总数")
        self.developer_count_value = TitleLabel("--")
        self.developer_count_layout.addWidget(self.developer_count_title)
        self.developer_count_layout.addWidget(self.developer_count_value, alignment=Qt.AlignCenter)
        cards_layout.addWidget(self.developer_count_card)
        
        self.tag_count_card = CardWidget()
        self.tag_count_card.setMinimumHeight(100)
        self.tag_count_layout = QVBoxLayout(self.tag_count_card)
        self.tag_count_title = SubtitleLabel("标签总数")
        self.tag_count_value = TitleLabel("--")
        self.tag_count_layout.addWidget(self.tag_count_title)
        self.tag_count_layout.addWidget(self.tag_count_value, alignment=Qt.AlignCenter)
        cards_layout.addWidget(self.tag_count_card)
        
        self.announcement_count_card = CardWidget()
        self.announcement_count_card.setMinimumHeight(100)
        self.announcement_count_layout = QVBoxLayout(self.announcement_count_card)
        self.announcement_count_title = SubtitleLabel("公告总数")
        self.announcement_count_value = TitleLabel("--")
        self.announcement_count_layout.addWidget(self.announcement_count_title)
        self.announcement_count_layout.addWidget(self.announcement_count_value, alignment=Qt.AlignCenter)
        cards_layout.addWidget(self.announcement_count_card)
        
        self.download_count_card = CardWidget()
        self.download_count_card.setMinimumHeight(100)
        self.download_count_layout = QVBoxLayout(self.download_count_card)
        self.download_count_title = SubtitleLabel("总下载量")
        self.download_count_value = TitleLabel("--")
        self.download_count_layout.addWidget(self.download_count_title)
        self.download_count_layout.addWidget(self.download_count_value, alignment=Qt.AlignCenter)
        cards_layout.addWidget(self.download_count_card)
        
        layout.addLayout(cards_layout)
        
        # 创建刷新按钮
        refresh_button = PrimaryPushButton("刷新统计数据")
        refresh_button.clicked.connect(self.load_stats)
        layout.addWidget(refresh_button, alignment=Qt.AlignCenter)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 加载初始数据
        self.load_stats()
        
    def load_stats(self):
        """加载统计数据"""
        self.show_progress()
        self.worker = WorkerThread(self.api_client, 'getcount')
        self.worker.finished.connect(self.on_stats_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_stats_loaded(self, data):
        """统计数据加载完成处理"""
        self.hide_progress()
        
        if not data:
            self.show_error("数据加载失败")
            return
        
        # 更新统计数据
        self.app_count_value.setText(str(data.get('total_apps', '--')))
        self.developer_count_value.setText(str(data.get('total_developers', '--')))
        self.tag_count_value.setText(str(data.get('total_tags', '--')))
        self.announcement_count_value.setText(str(data.get('total_announcements', '--')))
        self.download_count_value.setText(str(data.get('total_downloads', '--')))
        
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )



class TagAppsWindow(QMainWindow):
    """标签下的应用列表窗口"""
    def __init__(self, api_client, tag_id, tag_name, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.setWindowTitle(f"标签 '{tag_name}' 下的应用")
        self.resize(800, 600)
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.init_ui()
        self.load_tag_apps()
        
    def init_ui(self):
        """初始化界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel(f"标签 '{self.tag_name}' 下的应用")
        main_layout.addWidget(title)
        
        # 创建应用列表
        self.app_table = TableWidget()
        self.app_table.setColumnCount(5)
        self.app_table.setHorizontalHeaderLabels(["ID", "应用名称", "版本", "评分", "下载量"])
        self.app_table.horizontalHeader().setSectionResizeMode(1, 3)
        self.app_table.cellDoubleClicked.connect(self.show_app_detail)
        main_layout.addWidget(self.app_table)
        
        # 创建分页控件
        pagination_layout = QHBoxLayout()
        self.prev_button = PushButton("上一页")
        self.prev_button.clicked.connect(self.prev_page)
        self.page_label = CaptionLabel("第 1 页，共 1 页")
        self.next_button = PushButton("下一页")
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_button)
        main_layout.addLayout(pagination_layout)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
    def load_tag_apps(self):
        """加载标签下的应用"""
        self.show_progress()
        params = {
            'id': self.tag_id,
            'page': self.current_page,
            'limit': self.items_per_page
        }
        self.worker = WorkerThread(self.api_client, 'gettagapp', params)
        self.worker.finished.connect(self.on_tag_apps_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_tag_apps_loaded(self, data):
        """标签应用加载完成处理"""
        self.hide_progress()
        
        if not data or 'apps' not in data:
            self.show_error("应用列表加载失败")
            return
        
        # 清空表格
        self.app_table.setRowCount(0)
        
        # 添加数据
        for app in data['apps']:
            row_position = self.app_table.rowCount()
            self.app_table.insertRow(row_position)
            
            # 添加应用数据到表格
            self.app_table.setItem(row_position, 0, QTableWidgetItem(str(app.get('id', '--'))))
            self.app_table.setItem(row_position, 1, QTableWidgetItem(app.get('name', '未知应用')))
            self.app_table.setItem(row_position, 2, QTableWidgetItem(app.get('version', '未知')))
            self.app_table.setItem(row_position, 3, QTableWidgetItem(str(app.get('avg_rating', '暂无'))))
            self.app_table.setItem(row_position, 4, QTableWidgetItem(str(app.get('total_downloads', 0))))
        
        # 更新分页信息
        self.total_pages = data.get('total_pages', 1)
        self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        
        # 更新按钮状态
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_tag_apps()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_tag_apps()
            
    def show_app_detail(self, row, column):
        """显示应用详情"""
        # 获取应用ID
        app_id_item = self.app_table.item(row, 0)
        if app_id_item:
            app_id = int(app_id_item.text())
            # 打开应用详情窗口
            self.app_detail_window = AppDetailWindow(self.api_client, app_id, self)
            self.app_detail_window.show()
            
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class DeveloperAppsWindow(QMainWindow):
    """开发者的应用列表窗口"""
    def __init__(self, api_client, developer_id, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.developer_id = developer_id
        self.setWindowTitle(f"开发者ID {developer_id} 的应用")
        self.resize(800, 600)
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.init_ui()
        self.load_developer_apps()
        
    def init_ui(self):
        """初始化界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel(f"开发者ID {self.developer_id} 的应用")
        main_layout.addWidget(title)
        
        # 创建应用列表
        self.app_table = TableWidget()
        self.app_table.setColumnCount(5)
        self.app_table.setHorizontalHeaderLabels(["ID", "应用名称", "版本", "评分", "下载量"])
        self.app_table.horizontalHeader().setSectionResizeMode(1, 3)
        self.app_table.cellDoubleClicked.connect(self.show_app_detail)
        main_layout.addWidget(self.app_table)
        
        # 创建分页控件
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 10, 0, 0)
        
        self.prev_button = PushButton("上一页")
        self.prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_button)
        
        self.page_label = CaptionLabel("第 1 页，共 1 页")
        pagination_layout.addWidget(self.page_label, alignment=Qt.AlignCenter)
        
        self.next_button = PushButton("下一页")
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)
        
        main_layout.addLayout(pagination_layout)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
    def load_developer_apps(self):
        """加载开发者的应用"""
        self.show_progress()
        self.worker = WorkerThread(
            self.api_client, 
            'getdeveloperapp', 
            {'id': self.developer_id, 'page': self.current_page, 'limit': self.items_per_page}
        )
        self.worker.finished.connect(self.on_developer_apps_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_developer_apps_loaded(self, data):
        """开发者应用加载完成处理"""
        self.hide_progress()
        
        if not data or 'apps' not in data or 'pagination' not in data:
            self.show_error("数据格式错误")
            return
        
        # 清空表格
        self.app_table.setRowCount(0)
        
        # 填充表格
        for app in data['apps']:
            row_pos = self.app_table.rowCount()
            self.app_table.insertRow(row_pos)
            
            self.app_table.setItem(row_pos, 0, QTableWidgetItem(str(app.get('id', ''))))
            self.app_table.setItem(row_pos, 1, QTableWidgetItem(app.get('name', '')))
            self.app_table.setItem(row_pos, 2, QTableWidgetItem(app.get('version', '')))
            self.app_table.setItem(row_pos, 3, QTableWidgetItem(str(app.get('avg_rating', '暂无'))))
            self.app_table.setItem(row_pos, 4, QTableWidgetItem(str(app.get('total_downloads', 0))))
        
        # 更新分页信息
        self.total_pages = data['pagination']['totalPages']
        self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        
        # 更新按钮状态
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_developer_apps()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_developer_apps()
            
    def show_app_detail(self, row, column):
        """显示应用详情"""
        app_id = self.app_table.item(row, 0).text()
        detail_window = AppDetailWindow(self.api_client, app_id, self)
        detail_window.show()
        
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class AnnouncementDetailWindow(QMainWindow):
    """公告详情窗口"""
    def __init__(self, api_client, announcement_id, title, created_at, content, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.announcement_id = announcement_id
        self.title = title
        self.created_at = created_at
        
        # 设置窗口属性
        self.setWindowTitle(f"公告详情 - {title}")
        self.resize(700, 550)
        self.setObjectName("AnnouncementDetailWindow")
        
        # 添加全局样式
        self.setStyleSheet("""
            #AnnouncementDetailWindow {
                background-color: #F2F3F5;
            }
        """)
        
        # 将Markdown内容转换为HTML
        try:
            import markdown
            self.content_html = markdown.markdown(content)
        except Exception as e:
            # 如果转换失败，使用原始内容
            self.content_html = content
            print(f"Markdown转换失败: {str(e)}")
        
        self.content = content
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)
        
        # 创建标题
        self.title_label = TitleLabel(f"{self.title}")
        self.title_label.setObjectName("AnnouncementTitle")
        main_layout.addWidget(self.title_label)
        
        # 创建滚动区域 - 使用QFluentWidgets的ScrollArea
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(0)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置滚动区域样式
        self.scroll_area.setStyleSheet("""
            ScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: rgba(142, 142, 147, 0.3);
                border-radius: 4px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(142, 142, 147, 0.5);
            }
        """)
        
        # 创建滚动内容部件
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 20)
        self.scroll_layout.setSpacing(16)
        
        # 添加滚动区域到主布局
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        # 创建信息卡片
        self.create_info_card()
        
        # 创建内容卡片
        self.create_content_card()
        
        # 添加关闭按钮
        self.create_close_button(main_layout)
        
    def create_info_card(self):
        """创建公告信息卡片"""
        info_card = SimpleCardWidget()
        info_card.setObjectName("InfoCard")
        
        card_layout = QHBoxLayout(info_card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(20)
        
        # 添加公告信息
        info_items = [
            ("ID", self.announcement_id),
            ("发布时间", self.created_at)
        ]
        
        for label_text, value_text in info_items:
            info_layout = QVBoxLayout()
            label = CaptionLabel(label_text)
            value = BodyLabel(value_text)
            
            info_layout.addWidget(label)
            info_layout.addWidget(value)
            card_layout.addLayout(info_layout)
        
        card_layout.addStretch()
        self.scroll_layout.addWidget(info_card)
        
    def create_content_card(self):
        """创建公告内容卡片"""
        content_card = CardWidget()
        content_card.setObjectName("ContentCard")
        
        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)
        
        # 添加内容标题
        content_title = SubtitleLabel("公告内容")
        card_layout.addWidget(content_title)
        
        # 添加内容文本框，支持Markdown渲染和链接点击
        from PyQt5.QtWidgets import QTextBrowser
        self.content_text = QTextBrowser()
        self.content_text.setHtml(self.content_html)
        self.content_text.setReadOnly(True)
        self.content_text.setMinimumHeight(250)
        self.content_text.setLineWrapMode(QTextEdit.WidgetWidth)
        self.content_text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.content_text.setOpenExternalLinks(False)  # 禁用自动打开外部链接，由我们自己处理
        
        # QTextBrowser组件有anchorClicked信号，可以连接到处理函数
        self.content_text.anchorClicked.connect(self.handle_link_clicked)
        
        # 设置Fluent风格样式
        self.content_text.setStyleSheet("""
            TextEdit {
                background-color: transparent;
                border: 1px solid rgba(0, 0, 0, 0.05);
                border-radius: 6px;
                padding: 12px;
            }
        """)
        
        card_layout.addWidget(self.content_text)
        self.scroll_layout.addWidget(content_card)
        
    def handle_link_clicked(self, url):
        """处理链接点击事件，使用系统默认浏览器打开外部链接"""
        from PyQt5.QtCore import QUrl
        from PyQt5.QtGui import QDesktopServices
        
        # 检查URL是否为http或https协议
        if url.scheme() in ['http', 'https']:
            # 使用系统默认浏览器打开链接
            QDesktopServices.openUrl(url)
            return
        
        # 处理特殊的leonapp链接
        elif url.toString().startswith('leonapp://'):
            # 提取应用ID或其他参数
            # 示例: leonapp://app/123
            path = url.toString()[10:]  # 移除 'leonapp://'
            if path.startswith('app/'):
                app_id = path[4:]  # 提取应用ID
                # 这里可以实现打开特定应用详情的逻辑
                from app_detail_window import AppDetailWindow
                self.app_detail_window = AppDetailWindow(self.api_client, app_id, parent=self)
                self.app_detail_window.show()
            return
        
        # 显示不支持的链接类型提示
        InfoBar.warning(
            title="不支持的链接类型",
            content=f"无法打开链接: {url.toString()}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=3000,
            parent=self
        )
    
    def create_close_button(self, parent_layout):
        """创建关闭按钮"""
        button_card = SimpleCardWidget()
        button_card.setObjectName("ButtonCard")
        button_card.setMinimumHeight(80)
        
        button_layout = QHBoxLayout(button_card)
        button_layout.setContentsMargins(16, 16, 16, 16)
        button_layout.addStretch()
        
        # 关闭按钮
        close_button = PushButton("关闭")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        parent_layout.addWidget(button_card)
            
    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        from qfluentwidgets import InfoBar
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        InfoBar.success(
            title="复制成功",
            content="链接已复制到剪贴板！",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

class DeveloperInfoWindow(QMainWindow):
    """开发者信息窗口"""
    def __init__(self, api_client, developer_id, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.developer_id = developer_id
        self.setWindowTitle(f"开发者信息")
        self.resize(600, 400)
        self.init_ui()
        self.load_developer_info()
        
    def init_ui(self):
        """初始化界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel("开发者信息")
        main_layout.addWidget(title)
        
        # 创建信息卡片
        self.info_card = CardWidget()
        self.info_layout = QVBoxLayout(self.info_card)
        main_layout.addWidget(self.info_card)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
    def load_developer_info(self):
        """加载开发者信息"""
        self.show_progress()
        self.worker = WorkerThread(self.api_client, 'getdeveloperinfo', {'id': self.developer_id})
        self.worker.finished.connect(self.on_developer_info_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_developer_info_loaded(self, data):
        """开发者信息加载完成处理"""
        self.hide_progress()
        
        if not data:
            self.show_error("开发者信息加载失败")
            return
        
        # 清空之前的信息
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 添加开发者信息
        info_items = [
            ("ID", data.get('id', '--')),
            ("用户名", data.get('username', '--')),
            ("注册时间", data.get('created_at', '--')),
            ("是否验证", "是" if data.get('is_verified', False) else "否"),
            ("应用数量", data.get('app_count', 0))
        ]
        
        for label_text, value_text in info_items:
            label = CaptionLabel(f"{label_text}: {value_text}")
            self.info_layout.addWidget(label)
            
        # 添加验证时间（如果已验证）
        if data.get('is_verified', False) and data.get('verified_at'):
            verified_at_label = CaptionLabel(f"验证时间: {data.get('verified_at')}")
            self.info_layout.addWidget(verified_at_label)

    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class AppVersionsWindow(QMainWindow):
    """应用版本列表窗口"""
    def __init__(self, api_client, app_id, app_name, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.app_id = app_id
        self.app_name = app_name
        self.setWindowTitle(f"{app_name} - 版本历史")
        self.resize(800, 600)
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.init_ui()
        self.load_versions()
        
    def init_ui(self):
        """初始化界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel(f"{self.app_name} - 版本历史")
        main_layout.addWidget(title)
        
        # 创建版本列表
        self.versions_table = TableWidget()
        self.versions_table.setColumnCount(6)
        self.versions_table.setHorizontalHeaderLabels(["版本号", "发布日期", "操作系统", "文件大小", "下载量", "操作"])
        main_layout.addWidget(self.versions_table)
        
        # 创建分页控件
        pagination_layout = QHBoxLayout()
        self.prev_button = PushButton("上一页")
        self.prev_button.clicked.connect(self.prev_page)
        self.page_label = CaptionLabel("第 1 页，共 1 页")
        self.next_button = PushButton("下一页")
        self.next_button.clicked.connect(self.next_page)
        
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_button)
        main_layout.addLayout(pagination_layout)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
    def load_versions(self):
        """加载版本列表"""
        self.show_progress()
        self.worker = WorkerThread(self.api_client, 'getappversions', 
                                  {'id': self.app_id, 
                                   'page': self.current_page, 
                                   'limit': self.items_per_page})
        self.worker.finished.connect(self.on_versions_loaded)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()
        
    def on_versions_loaded(self, data):
        """版本列表加载完成处理"""
        self.hide_progress()
        
        if not data:
            self.show_error("版本列表加载失败")
            return
        
        # 清空表格
        self.versions_table.setRowCount(0)
        
        # 更新分页信息
        pagination = data.get('pagination', {})
        self.total_pages = pagination.get('totalPages', 1)
        self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        
        # 更新按钮状态
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        
        # 填充表格
        versions = data.get('versions', [])
        for version in versions:
            row_position = self.versions_table.rowCount()
            self.versions_table.insertRow(row_position)
            
            # 添加版本数据并存储版本ID和文件路径
            version_item = QTableWidgetItem(version.get('version', '未知'))
            # 存储版本ID和文件路径信息
            version_item.version_id = version.get('id', '')
            version_item.file_path = version.get('file_path', '')
            self.versions_table.setItem(row_position, 0, version_item)
            
            self.versions_table.setItem(row_position, 1, QTableWidgetItem(version.get('created_at', '未知')))
            self.versions_table.setItem(row_position, 2, QTableWidgetItem(version.get('platform', '未知')))
            self.versions_table.setItem(row_position, 3, QTableWidgetItem(version.get('file_size', '未知')))
            self.versions_table.setItem(row_position, 4, QTableWidgetItem(str(version.get('download_count', 0))))
            
            # 添加下载按钮
            download_button = PushButton("下载")
            download_button.setIcon(FluentIcon.DOWNLOAD)
            # 将版本ID绑定到按钮上
            version_id = version.get('id', '')
            download_button.clicked.connect(lambda checked, vid=version_id: self.download_version(vid))
            
            # 创建按钮容器并添加按钮
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(5, 5, 5, 5)
            button_layout.addWidget(download_button)
            button_container.setLayout(button_layout)
            
            self.versions_table.setCellWidget(row_position, 5, button_container)
        
        # 自动调整列宽
        self.versions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_versions()
            
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_versions()
        
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """显示错误消息"""
        self.hide_progress()
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class AppInfoTab(QWidget):
    """APP信息标签页"""
    def __init__(self, api_client=None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title = TitleLabel("应用信息")
        layout.addWidget(title)
        
        # 创建信息卡片
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加版本号信息 - 使用PrimaryPushSettingCard
        self.version_card = PrimaryPushSettingCard(
            title="版本号",
            text="检查更新",
            content="目前APP版本号：" + APP_VERSION,
            icon=FluentIcon.INFO,
            parent=self
        )
        self.version_card.clicked.connect(self.check_update)
        card_layout.addWidget(self.version_card)
        
        # 添加描述信息
        description_label = CaptionLabel("这是LeonApp应用商店的PC端管理工具，用于查看和管理应用、标签和开发者信息。")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setMinimumHeight(60)
        card_layout.addWidget(description_label)
        
        # 添加分隔符
        card_layout.addSpacing(10)
        
        # 添加QFluentDesign版权信息
        qfluentdesign_label = CaptionLabel("界面设计基于QFluentWidgets - PyQt5的Fluent Design风格组件库")
        qfluentdesign_label.setWordWrap(True)
        qfluentdesign_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(qfluentdesign_label)
        
        # 添加GPLv3许可证信息
        license_label = CaptionLabel("本应用采用GNU General Public License v3.0 (GPLv3) 许可协议发布")
        license_label.setWordWrap(True)
        license_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(license_label)
        
        # 添加信息卡片到主布局
        layout.addWidget(card, alignment=Qt.AlignCenter)
        
        # 填充空白，使内容居中
        layout.addStretch()
    
    def check_update(self):
        """检查更新功能"""
        # 显示加载中的提示
        self.show_info("正在检查更新...")
        
        # 创建工作线程来异步获取版本信息
        self.worker = WorkerThread(
            self.api_client,
            'getappversions',
            {'id': 15}  # LeonAPP的ID为15
        )
        self.worker.finished.connect(self.on_update_checked)
        self.worker.error.connect(self.on_update_error)
        self.worker.start()
    
    def on_update_checked(self, data):
        """更新检查完成后的处理"""
        try:
            # 检查API返回的数据格式
            if not isinstance(data, dict) or 'versions' not in data:
                self.show_error("获取版本信息失败：数据格式不正确")
                return
            
            versions = data.get('versions', [])
            if not versions:
                self.show_error("未找到任何版本信息")
                return
            
            # 最新版本通常在列表的第一个
            latest_version = versions[0].get('version', '未知')
            current_version = APP_VERSION
            
            # 比较版本号
            if latest_version != current_version:
                # 版本不一致，显示更新提示
                self.show_info(
                    f"发现新版本：{latest_version}",
                    f"当前版本：{current_version}\n建议前往应用商店下载最新版本。"
                )
            else:
                # 已是最新版本
                self.show_info("已是最新版本", f"当前版本 {current_version} 是最新版本")
        except Exception as e:
            self.show_error(f"处理版本信息时发生错误：{str(e)}")
    
    def on_update_error(self, error_message):
        """处理更新检查时的错误"""
        self.show_error(f"检查更新失败：{error_message}")
    
    def show_info(self, title, content=None):
        """显示信息消息"""
        if content is None:
            content = ""
        InfoBar.info(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )
    
    def show_error(self, message):
        """显示错误消息"""
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

class SettingsTab(QWidget):
    """设置标签页"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        
        # 创建滚动区域并设置无样式
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        # 设置无样式但保留内容显示
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")
        self.scroll_area.verticalScrollBar().setStyleSheet("QScrollBar:vertical { width: 0px; }")
        self.scroll_area.horizontalScrollBar().setStyleSheet("QScrollBar:horizontal { height: 0px; }")
        
        # 创建滚动内容控件
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建常规设置卡片
        general_card = CardWidget(self.scroll_content)
        general_layout = QVBoxLayout(general_card)
        general_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加卡片标题
        title = TitleLabel("常规设置", general_card)
        general_layout.addWidget(title)
        general_layout.addSpacing(16)
        
        # 添加自动打开安装程序选项
        from qfluentwidgets import FluentIcon, OptionsValidator
        
        # 创建OptionsSettingCard，直接使用configItem
        self.auto_open_option = OptionsSettingCard(
            icon=FluentIcon.SETTING,
            title="下载后自动打开安装程序",
            content="设置是否在下载完成后自动打开安装程序",
            texts=["是", "否"],
            configItem=app_config.auto_open_installer,
            parent=general_card
        )
        
        # 连接信号
        self.auto_open_option.optionChanged.connect(self.on_auto_open_changed)
        
        general_layout.addWidget(self.auto_open_option)
        
        # 添加应用打开方式选项
        self.app_open_method_option = OptionsSettingCard(
            icon=FluentIcon.SHARE, 
            title="应用打开方式",
            content="选择下载完成后如何打开应用程序",
            texts=["Windows直接运行应用程序", "打开文件夹方式"],
            configItem=app_config.app_open_method,
            parent=general_card
        )
        
        # 连接信号
        self.app_open_method_option.optionChanged.connect(self.on_app_open_method_changed)
        
        general_layout.addWidget(self.app_open_method_option)
        
        # 已删除云母效果选项
        
        # 已经删除了云母效果选项
        
        # 添加查看日志按钮
        general_layout.addSpacing(20)
        
        view_logs_button = PrimaryPushButton("查看应用日志", general_card)
        view_logs_button.clicked.connect(self.show_logs)
        general_layout.addWidget(view_logs_button)
        
        # 将常规设置卡片添加到布局
        self.scroll_layout.addWidget(general_card)
        
        # 添加底部间距
        self.scroll_layout.addSpacing(20)
        
        # 设置滚动区域的内容
        self.scroll_area.setWidget(self.scroll_content)
        
        # 将滚动区域添加到主布局
        self.main_layout.addWidget(self.scroll_area)
    
    def on_auto_open_changed(self, index):
        """自动打开设置变更处理"""
        app_config.auto_open_installer = (index == 0)
        
    def on_app_open_method_changed(self, index):
        """应用打开方式设置变更处理"""
        app_config.app_open_method = index
    
    # 已删除云母效果处理方法
    
    def show_logs(self):
        """显示应用日志"""
        from qfluentwidgets import InfoBar, InfoBarPosition
        from qfluentwidgets import ScrollArea, PushButton, PrimaryPushButton
        from qfluentwidgets import FluentIcon, CardWidget, TitleLabel, SubtitleLabel
        from PyQt5.QtGui import QIcon
        import os
        import threading
        import time
        from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout
        from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
        
        # 尝试找到日志文件
        log_file_path = None
        # 常见的日志文件位置
        possible_log_paths = [
            './logs/leonapp_gui.log',  # 主要日志文件路径（从config.py中配置）
            './leonapp.log',
            './logs/leonapp.log',
            os.path.expanduser('~') + '/leonapp.log'
        ]
        
        for path in possible_log_paths:
            if os.path.exists(path):
                log_file_path = path
                break
        
        # 如果找不到日志文件，显示提示
        if not log_file_path:
            InfoBar.warning(
                title="提示",
                content="未找到日志文件",
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
            return
        
        # 定义日志更新信号类
        class LogUpdateSignal(QObject):
            log_updated = pyqtSignal(str)
        
        log_signal = LogUpdateSignal()
        
        # 创建Sweet Alert风格的弹窗
        class LogDialog(QDialog):
            def __init__(self, title, parent=None):
                super().__init__(parent)
                self.setWindowTitle(title)
                self.setFixedSize(800, 600)
                # 设置为非模态对话框，允许主窗口和日志窗口同时交互
                self.setWindowModality(Qt.NonModal)
                # 设置窗口样式
                self.setStyleSheet("""
                    QDialog {
                        background-color: #f8f9fa;
                        border-radius: 12px;
                        border: 1px solid #e0e0e0;
                    }
                """)
                self.init_ui()
            
            def init_ui(self):
                # 创建主布局
                main_layout = QVBoxLayout(self)
                main_layout.setContentsMargins(20, 20, 20, 20)
                
                # 创建标题
                title_label = TitleLabel("应用日志", self)
                main_layout.addWidget(title_label)
                
                # 创建日志显示区域
                self.log_text_edit = QTextEdit()
                self.log_text_edit.setReadOnly(True)
                self.log_text_edit.setStyleSheet("""
                    QTextEdit {
                        background-color: #2d2d2d;
                        color: #f8f8f2;
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-size: 12px;
                        border-radius: 8px;
                        padding: 15px;
                        border: none;
                    }
                    QScrollBar:vertical {
                        background-color: #3d3d3d;
                        width: 10px;
                        border-radius: 5px;
                    }
                    QScrollBar::handle:vertical {
                        background-color: #666666;
                        border-radius: 5px;
                    }
                    QScrollBar::add-line:vertical,
                    QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                """)
                main_layout.addWidget(self.log_text_edit, 1)
                
                # 创建按钮区域
                button_layout = QHBoxLayout()
                button_layout.setContentsMargins(0, 15, 0, 0)
                button_layout.setAlignment(Qt.AlignRight)
                
                # 创建按钮
                self.close_button = PrimaryPushButton("关闭", self)
                self.close_button.setFixedWidth(100)
                self.close_button.clicked.connect(self.accept)
                
                button_layout.addWidget(self.close_button)
                main_layout.addLayout(button_layout)
        
        # 创建日志对话框
        log_dialog = LogDialog("应用日志", self)
        log_text_edit = log_dialog.log_text_edit
        
        # 定义日志文件监听函数
        def monitor_log_file():
            # 初始时直接移动到文件末尾，只监控新的日志
            try:
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    f.seek(0, os.SEEK_END)  # 移动到文件末尾
                    last_position = f.tell()
            except Exception:
                last_position = 0
            
            while log_dialog.isVisible():
                try:
                    with open(log_file_path, 'r', encoding='utf-8') as f:
                        # 检查文件大小是否有变化
                        f.seek(0, os.SEEK_END)
                        current_size = f.tell()
                        
                        if current_size > last_position:
                            # 文件有新增内容，读取并发送信号
                            f.seek(last_position)
                            new_logs = f.read()
                            if new_logs:
                                log_signal.log_updated.emit(new_logs)
                                last_position = current_size
                        elif current_size < last_position:
                            # 文件被截断（如日志轮转），从头开始读取
                            last_position = 0
                except Exception as e:
                    # 如果文件被锁定或其他错误，忽略
                    pass
                time.sleep(0.3)  # 降低检查间隔，提高实时性
        
        # 日志更新槽函数
        def update_log_text(new_logs):
            current_text = log_text_edit.toPlainText()
            # 限制日志显示的行数，避免内存占用过大
            lines = (current_text + new_logs).splitlines()
            if len(lines) > 1000:
                lines = lines[-1000:]
            
            # 使用QTimer延迟设置文本，确保UI响应
            from PyQt5.QtCore import QTimer
            def set_log_text():
                log_text_edit.setPlainText('\n'.join(lines))
                # 强制滚动到底部，确保显示最新日志
                log_text_edit.verticalScrollBar().setValue(log_text_edit.verticalScrollBar().maximum())
                # 使用QTimer的单次触发确保滚动生效
                QTimer.singleShot(0, lambda: log_text_edit.verticalScrollBar().setValue(log_text_edit.verticalScrollBar().maximum()))
            
            QTimer.singleShot(0, set_log_text)
        
        # 连接信号和槽
        log_signal.log_updated.connect(update_log_text)
        
        # 初始加载日志，优先显示最新日志
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                # 直接获取文件大小
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                
                # 只读取文件末尾的内容（约100KB），确保优先显示最新日志
                # 如果文件较小，则读取全部内容
                chunk_size = min(100 * 1024, file_size)
                f.seek(max(0, file_size - chunk_size))
                logs = f.read()
                
                lines = logs.splitlines()
                if len(lines) > 1000:
                    lines = lines[-1000:]  # 确保只显示最新的1000行
                
                log_text_edit.setPlainText('\n'.join(lines))
                
                # 确保滚动到底部，显示最新日志
                # 使用QTimer确保UI渲染完成后再滚动
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, lambda: log_text_edit.verticalScrollBar().setValue(log_text_edit.verticalScrollBar().maximum()))
                # 再次触发滚动，确保生效
                QTimer.singleShot(100, lambda: log_text_edit.verticalScrollBar().setValue(log_text_edit.verticalScrollBar().maximum()))
        except Exception as e:
            log_text_edit.setPlainText(f"无法读取日志文件: {str(e)}")
        
        # 启动日志监听线程
        log_thread = threading.Thread(target=monitor_log_file, daemon=True)
        log_thread.start()
        
        # 显示弹窗（非模态）
        log_dialog.show()

class LeonAppGUI(MSFluentWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        # 初始化API客户端
        self.api_client = APIClient()
        # 设置窗口标题和大小
        self.setWindowTitle("LeonApp For PC")
        self.resize(1000, 700)
        
        # 设置窗口图标
        from PyQt5.QtGui import QIcon
        import os
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.jpeg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 已删除云母效果相关代码
        # 保持窗口默认不透明状态
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 创建各个标签页
        self.homepage_tab = HomepageTab(self.api_client, self)
        self.homepage_tab.setObjectName("homepage")
        self.app_tab = AppTab(self.api_client, self)
        self.app_tab.setObjectName("app")
        self.tag_tab = TagTab(self.api_client, self)
        self.tag_tab.setObjectName("tag")
        self.developer_tab = DeveloperTab(self.api_client, self)
        self.developer_tab.setObjectName("developer")
        self.announcement_tab = AnnouncementTab(self.api_client, self)
        self.announcement_tab.setObjectName("announcement")
        self.stats_tab = StatsTab(self.api_client, self)
        self.stats_tab.setObjectName("stats")
        
        # 添加子界面到主窗口
        self.addSubInterface(self.homepage_tab, FluentIcon.HOME, "首页")
        self.addSubInterface(self.app_tab, FluentIcon.APPLICATION, "应用管理")
        self.addSubInterface(self.tag_tab, FluentIcon.TAG, "标签管理")
        self.addSubInterface(self.developer_tab, FluentIcon.DEVELOPER_TOOLS, "开发者管理")
        self.addSubInterface(self.announcement_tab, FluentIcon.MEGAPHONE, "公告管理")
        self.addSubInterface(self.stats_tab, FluentIcon.PIE_SINGLE, "统计信息")
        
        # 添加APP信息标签页
        self.info_tab = AppInfoTab(self.api_client, self)
        self.info_tab.setObjectName("info")
        self.addSubInterface(self.info_tab, FluentIcon.INFO, "应用信息")
        
        # 添加设置标签页
        self.settings_tab = SettingsTab(self)
        self.settings_tab.setObjectName("settings")
        self.addSubInterface(self.settings_tab, FluentIcon.SETTING, "设置")
        
        # 设置默认选中的标签页
        self.navigationInterface.setCurrentItem("homepage")
        
        # 构建状态栏
        # self.init_status_bar()

    def show_app_detail(self, app_id):
        """显示应用详情"""
        logger.info(f"用户查看应用详情，应用ID: {app_id}")
        detail_window = AppDetailWindow(self.api_client, app_id, self)
        detail_window.show()
        
    def show_tag_apps(self, tag_id, tag_name):
        """显示标签下的应用"""
        tag_apps_window = TagAppsWindow(self.api_client, tag_id, tag_name, self)
        tag_apps_window.show()
        
    def show_developer_apps(self, developer_id):
        """显示开发者的应用"""
        developer_apps_window = DeveloperAppsWindow(self.api_client, developer_id, self)
        developer_apps_window.show()
        
    def show_developer_info(self, developer_id):
        """显示开发者信息"""
        developer_info_window = DeveloperInfoWindow(self.api_client, developer_id, self)
        developer_info_window.show()
        
    def show_app_versions(self, app_id, app_name):
        """显示应用的版本列表"""
        versions_window = AppVersionsWindow(self.api_client, app_id, app_name, self)
        versions_window.show()

def show_error_dialog(title, message):
    """显示错误弹窗"""
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtGui import QFont
    
    # 创建错误消息框，模拟Sweet Alert风格
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    
    # 设置字体大小
    font = QFont()
    font.setPointSize(10)
    msg_box.setFont(font)
    
    # 设置消息内容
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    
    # 记录到日志
    logger.error(f"{title}: {message}")
    
    # 显示弹窗
    msg_box.exec_()

def log_error(error_message):
    """记录错误日志到文件"""
    logger.error(error_message)

def main():
    """主函数"""
    try:
        # 配置loguru日志系统
        from config import LOG_CONFIG
        import logging
        import os
        import sys
        
        # 设置日志文件路径
        log_dir = os.path.dirname(os.path.abspath(LOG_CONFIG['LOG_FILE']))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 移除默认的控制台输出
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sys.stdout,
            level=LOG_CONFIG['LOG_LEVEL'],
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # 添加文件输出（如果配置了）
        if LOG_CONFIG['LOG_TO_FILE']:
            logger.add(
                LOG_CONFIG['LOG_FILE'],
                level=LOG_CONFIG['LOG_LEVEL'],
                rotation="10 MB",  # 当日志文件达到10MB时旋转
                retention=LOG_CONFIG['LOG_BACKUP_COUNT'],  # 保留的备份文件数量
                compression="zip",  # 压缩旧日志
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                encoding="utf-8"
            )
        
        # 配置PyQt5的日志转发到loguru
        class LoguruHandler(logging.Handler):
            def emit(self, record):
                # 获取日志级别对应的loguru方法
                level = getattr(logger, record.levelname.lower(), logger.info)
                level(self.format(record))
        
        # 获取PyQt5的根日志记录器
        qt_logger = logging.getLogger("PyQt5")
        # 设置级别
        qt_logger.setLevel(getattr(logging, LOG_CONFIG['LOG_LEVEL']))
        # 添加自定义处理器
        handler = LoguruHandler()
        handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
        qt_logger.addHandler(handler)
        # 确保所有子记录器也使用这个处理器
        qt_logger.propagate = False
        
        # 也处理PyQt的其他可能的日志记录器
        for logger_name in ["PyQt", "Qt", "QApplication", "QMainWindow", "QWidget", "QtCore", "QtGui", "QtWidgets"]:
            qt_logger = logging.getLogger(logger_name)
            qt_logger.setLevel(getattr(logging, LOG_CONFIG['LOG_LEVEL']))
            qt_logger.addHandler(handler)
            qt_logger.propagate = False
        
        # 设置Python标准库logging的根记录器也使用我们的处理器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, LOG_CONFIG['LOG_LEVEL']))
        root_logger.addHandler(handler)
        
        logger.info("日志系统配置完成，PyQt5相关日志已集成到loguru")
        
        logger.info(f"LeonApp {APP_VERSION} 启动")
        
        # 创建应用实例
        app = QApplication(sys.argv)
        
        # 添加中文支持
        translator = FluentTranslator()
        app.installTranslator(translator)
        
        # 加载并应用QFluentWidgets主题色配置
        import json
        import os
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                theme_color = config.get('QFluentWidgets', {}).get('ThemeColor', '#4169E1')
                from qfluentwidgets import setThemeColor
                setThemeColor(theme_color)
                logger.info(f"已设置QFluentWidgets主题色: {theme_color}")
        except Exception as e:
            logger.warning(f"加载主题色配置失败: {e}")
            # 使用默认主题色
            from qfluentwidgets import setThemeColor
            setThemeColor('#4169E1')
        
        # 创建主窗口实例
        window = LeonAppGUI()
        
        # 设置窗口图标
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets/logo.jpeg")
        if os.path.exists(logo_path):
            window.setWindowIcon(QIcon(logo_path))
        
        # 创建QFluentWidgets的启动页面
        splash = SplashScreen(window.windowIcon(), window)
        splash.setIconSize(QSize(102, 102))
        
        # 在创建其他子页面前先显示主界面
        window.show()
        
        # 确保启动画面显示
        app.processEvents()
        
        # 隐藏启动页面
        splash.finish()
        
        # 运行应用
        sys.exit(app.exec_())
    except Exception as e:
        # 获取完整的错误堆栈
        error_traceback = traceback.format_exc()
        
        # 记录错误日志
        log_error(error_traceback)
        
        # 显示错误弹窗
        error_msg = f"程序崩溃了！错误信息：\n{e}\n\n详细日志已保存到logs目录。"
        show_error_dialog("程序崩溃", error_msg)
        
        # 退出程序
        sys.exit(1)

if __name__ == "__main__":
    main()