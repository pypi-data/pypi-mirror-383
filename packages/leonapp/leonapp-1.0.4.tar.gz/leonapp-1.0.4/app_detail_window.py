# 这破代码有人能修复吗
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QFrame, QLabel, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QFont
from qfluentwidgets import (InfoBar, InfoBarPosition, TitleLabel, SubtitleLabel,
                          PrimaryPushButton, PushButton, ScrollArea, CardWidget,
                          FluentIcon, SimpleCardWidget, BodyLabel)
from loguru import logger
import json
import os
import requests
import sys
import tempfile
import subprocess
import platform

def show_error_dialog(title, message):
    """显示错误弹窗，模拟Sweet Alert风格并记录日志"""
    # 记录错误日志
    logger.error(f"{title}: {message}")
    
    # 创建错误消息框
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
    
    # 显示弹窗
    msg_box.exec_()

class DownloadThread(QThread):
    """下载线程，用于在后台下载文件"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, download_url, save_path):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
        
    def run(self):
        """线程运行函数"""
        try:
            # 发送请求
            with requests.get(self.download_url, stream=True, timeout=30) as response:
                response.raise_for_status()
                
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                # 创建保存目录
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                
                # 下载文件
                with open(self.save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # 计算进度
                            if total_size > 0:
                                progress = int(downloaded_size / total_size * 100)
                                self.progress.emit(progress)
            
            # 下载完成
            self.finished.emit(self.save_path)
            
        except Exception as e:
            self.error.emit(f"下载失败: {str(e)}")

class AppDetailWindow(QMainWindow):
    def __init__(self, api_client, app_id, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.app_id = app_id
        self.parent_window = parent
        
        # 存储当前加载的本地缓存图片路径列表
        self.cached_image_paths = []
        
        # 设置窗口属性
        self.setWindowTitle("应用详情")
        self.resize(850, 650)
        self.setObjectName("AppDetailWindow")
        
        # 添加全局样式 - 现代扁平化设计
        self.setStyleSheet("""
            #AppDetailWindow {
                background-color: #F5F7FA;
            }
            QLabel {
                color: #333333;
            }
            #AppTitle {
                color: #1A1A1A;
                font-weight: bold;
            }
            #StatusBadge {
                border-radius: 12px;
                padding: 2px 10px;
                font-size: 12px;
            }
            #DeveloperLabel {
                color: #666666;
                font-size: 14px;
            }
        """)
        
        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 创建自定义顶部区域（非传统顶栏）
        self.create_custom_header()
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #E5E6EB;")
        self.main_layout.addWidget(separator)
        
        # 创建滚动区域 - 使用QFluentWidgets的ScrollArea
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(0)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置滚动区域样式
        self.scroll_area.setStyleSheet("""
            ScrollArea {
                background-color: #F5F7FA;
                border: none;
            }
            QScrollBar:vertical {
                width: 10px;
                background: transparent;
                margin-right: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(142, 142, 147, 0.2);
                border-radius: 5px;
                min-height: 50px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(142, 142, 147, 0.4);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                width: 0px;
            }
        """)
        
        # 创建滚动内容部件
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 30)
        self.scroll_layout.setSpacing(20)
        
        # 添加滚动区域到主布局
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)
        
        # 加载应用详情
        self.load_app_detail()
        
    def create_custom_header(self):
        """创建自定义顶部区域"""
        self.header_widget = QWidget()
        self.header_widget.setObjectName("HeaderWidget")
        self.header_widget.setStyleSheet("""
            #HeaderWidget {
                background-color: #FFFFFF;
                padding: 15px 20px;
            }
        """)
        
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(15)
        
        # 应用图标占位 - 使用QLabel替换Avatar
        self.app_icon = QLabel()
        self.app_icon.setFixedSize(60, 60)
        self.app_icon.setStyleSheet("background-color: #4CAF50; border-radius: 12px;")
        
        # 应用信息布局
        self.app_info_layout = QVBoxLayout()
        self.app_info_layout.setContentsMargins(0, 0, 0, 0)
        self.app_info_layout.setSpacing(5)
        
        # 标题和状态布局
        self.title_status_layout = QHBoxLayout()
        self.title_status_layout.setSpacing(10)
        
        # 应用标题
        self.app_title = TitleLabel("加载中...")
        self.app_title.setObjectName("AppTitle")
        self.title_status_layout.addWidget(self.app_title)
        
        # 应用状态标签
        self.status_badge = QLabel("- ")
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setStyleSheet("background-color: #E5E6EB; color: #666666;")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setFixedHeight(24)
        self.title_status_layout.addWidget(self.status_badge)
        self.title_status_layout.addStretch()
        
        # 开发者标签
        self.developer_label = QLabel("开发者: 加载中...")
        self.developer_label.setObjectName("DeveloperLabel")
        
        # 添加到应用信息布局
        self.app_info_layout.addLayout(self.title_status_layout)
        self.app_info_layout.addWidget(self.developer_label)
        
        # 右侧按钮布局
        self.button_layout = QVBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(8)
        
        # 关闭按钮
        self.close_button = PushButton("关闭")
        self.close_button.clicked.connect(self.close)
        self.close_button.setFixedSize(90, 32)
        self.button_layout.addWidget(self.close_button)
        self.button_layout.addStretch()
        
        # 添加到主头部布局
        self.header_layout.addWidget(self.app_icon)
        self.header_layout.addLayout(self.app_info_layout, 1)
        self.header_layout.addLayout(self.button_layout)
        
        # 添加到主布局
        self.main_layout.addWidget(self.header_widget)
    
    def load_app_detail(self):
        """加载应用详情"""
        try:
            # 使用API客户端调用getappinfo端点获取应用详情
            result = self.api_client.make_request('getappinfo', {'id': self.app_id})
            
            # 检查API调用是否成功
            if isinstance(result, dict) and 'data' in result and result['data'] is not None:
                # 新API格式: {"status": "success", "data": {...}}
                self.app_data = result['data']
                app_data = self.app_data
            elif isinstance(result, dict) and 'success' in result and result['success']:
                # 旧API格式兼容性支持
                self.app_data = result['data']
                app_data = self.app_data
            else:
                # API调用失败，显示错误信息
                error_msg = result.get('error', '未知错误') if isinstance(result, dict) else 'API调用失败'
                InfoBar.error(
                    title="错误",
                    content=f"加载应用详情失败: {error_msg}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                # 使用默认数据
                self.app_data = {
                    "id": self.app_id,
                    "name": "未知应用",
                    "description": "无法加载应用详情",
                    "developer_id": "0",
                    "developer_name": "未知开发者",
                    "status": "unknown",
                    "version": "0.0.0",
                    "created_at": "-",
                    "downloads": "0",
                    "rating": "0.0",
                    "category": "未知",
                    "images": []
                }
                app_data = self.app_data
            
            # 更新窗口标题
            self.setWindowTitle(f"应用详情 - {app_data.get('name', '未知应用')}")
            
            # 更新头部信息
            self.app_title.setText(app_data.get('name', '未知应用'))
            
            # 通过开发者ID查询开发者名称
            developer_id = app_data.get('developer_id', '')
            result2 = self.api_client.make_request('getdeveloperinfo', {'id': developer_id})
            developer_name = "未知开发者"
            
            if developer_id and developer_id != "0":
                # 尝试通过API获取开发者名称
                try:
                    developer_info = self.api_client.make_request('getdeveloperinfo', {'id': developer_id})
                    if isinstance(developer_info, dict) and 'success' in developer_info and developer_info['success']:
                        developer_name = result2['data'].get('username')
                    else:
                        # 如果API调用失败，尝试从本地数据获取
                        if 'developer_name' in app_data and app_data['developer_name']:
                            developer_name = app_data['developer_name']
                        elif 'developer' in app_data and app_data['developer']:
                            developer_name = app_data['developer']
                        elif 'developer_email' in app_data and app_data['developer_email']:
                            developer_name = app_data['developer_email']
                except Exception as e:
                    # 异常处理，使用本地数据
                    if 'developer_name' in app_data and app_data['developer_name']:
                        developer_name = app_data['developer_name']
                    elif 'developer' in app_data and app_data['developer']:
                        developer_name = app_data['developer']
                    elif 'developer_email' in app_data and app_data['developer_email']:
                        developer_name = app_data['developer_email']
            else:
                # 如果没有有效的开发者ID，尝试从本地数据获取
                if 'developer_name' in app_data and app_data['developer_name']:
                    developer_name = app_data['developer_name']
                elif 'developer' in app_data and app_data['developer']:
                    developer_name = app_data['developer']
                elif 'developer_email' in app_data and app_data['developer_email']:
                    developer_name = app_data['developer_email']
            
            self.developer_label.setText(f"开发者: {developer_name}")
            
            # 根据应用状态设置状态标签样式
            status = app_data.get('status', 'unknown')
            status_text = {}
            status_styles = {}
            
            status_text['approved'] = '已通过'
            status_text['pending'] = '审核中'
            status_text['rejected'] = '已拒绝'
            status_text['unknown'] = '未知状态'
            
            status_styles['approved'] = 'background-color: #E8F5E9; color: #2E7D32;'
            status_styles['pending'] = 'background-color: #FFF3E0; color: #E65100;'
            status_styles['rejected'] = 'background-color: #FFEBEE; color: #C62828;'
            status_styles['unknown'] = 'background-color: #E5E6EB; color: #666666;'
            
            self.status_badge.setText(status_text.get(status, '未知状态'))
            self.status_badge.setStyleSheet(status_styles.get(status, status_styles['unknown']))
            
            # 清空滚动区域
            for i in reversed(range(self.scroll_layout.count())):
                widget = self.scroll_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
            
            # 显示统计信息卡片
            self.display_stats_card(app_data)
            
            # 显示APP预览图片（如果有）
            images = app_data.get('images', [])
            if images and isinstance(images, list) and len(images) > 0:
                self.display_app_images(images)
            
            # 显示应用基本信息卡片
            self.display_app_info_card(app_data)
            
            # 显示应用描述卡片
            self.display_description_card(app_data)
            
            # 显示操作按钮区域
            self.display_action_buttons()
            
        except Exception as e:
            InfoBar.error(
                title="错误",
                content=f"加载应用详情失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def display_stats_card(self, app_data):
        """显示应用统计信息卡片"""
        stats_card = CardWidget()
        stats_card.setObjectName("StatsCard")
        stats_card.setStyleSheet("""
            #StatsCard {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                /* color: white; */
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
            #StatsCard QLabel {
                /* color: white; */
            }
        """)
        
        card_layout = QHBoxLayout(stats_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(25)
        
        # 下载量统计项
        downloads_item = QVBoxLayout()
        downloads_label = BodyLabel("下载量")
        downloads_label.setStyleSheet("font-size: 13px; opacity: 0.9;")
        downloads_value = TitleLabel(app_data.get("downloads", "0"))
        downloads_value.setStyleSheet("font-size: 24px; font-weight: bold;")
        downloads_item.addWidget(downloads_label)
        downloads_item.addWidget(downloads_value)
        downloads_item.setAlignment(Qt.AlignCenter)
        
        # 评分统计项
        rating_item = QVBoxLayout()
        rating_label = BodyLabel("评分")
        rating_label.setStyleSheet("font-size: 13px; opacity: 0.9;")
        rating_value = TitleLabel(app_data.get("rating", "0.0"))
        rating_value.setStyleSheet("font-size: 24px; font-weight: bold;")
        rating_item.addWidget(rating_label)
        rating_item.addWidget(rating_value)
        rating_item.setAlignment(Qt.AlignCenter)
        
        # 分类统计项
        category_item = QVBoxLayout()
        category_label = BodyLabel("分类")
        category_label.setStyleSheet("font-size: 13px; opacity: 0.9;")
        category_value = TitleLabel(app_data.get("category", "未分类"))
        category_value.setStyleSheet("font-size: 24px; font-weight: bold;")
        category_item.addWidget(category_label)
        category_item.addWidget(category_value)
        category_item.setAlignment(Qt.AlignCenter)
        
        # 添加到卡片布局
        card_layout.addLayout(downloads_item)
        card_layout.addLayout(rating_item)
        card_layout.addLayout(category_item)
        
        self.scroll_layout.addWidget(stats_card)
        
    def display_app_images(self, images):
        """显示应用预览图片，使用QFluentWidgets的HorizontalFlipView组件"""
        # 导入HorizontalFlipView组件
        from qfluentwidgets import HorizontalFlipView
        import os
        import requests
        import uuid
        from PyQt5.QtCore import Qt, QDir
        from PyQt5.QtGui import QPixmap
        from PyQt5.QtWidgets import QLabel
        
        # 打印传入的images数据
        logger.info(f"接收到的图片数据: {images}")
        logger.info(f"图片数据类型: {type(images)}")
        logger.info(f"图片数据长度: {len(images) if isinstance(images, list) else '不是列表'}")
        
        # 创建缓存文件夹
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            logger.info(f"创建缓存文件夹: {cache_dir}")
        
        # 创建图片预览卡片
        images_card = CardWidget()
        images_card.setObjectName("ImagesCard")
        images_card.setStyleSheet("""
            #ImagesCard {
                background-color: white;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }
        """)
        
        card_layout = QVBoxLayout(images_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # 卡片标题和图标
        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(FluentIcon.PHOTO.icon().pixmap(18, 18))
        title_icon.setStyleSheet("color: #9C27B0;")
        
        card_title = SubtitleLabel("应用预览")
        card_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(card_title)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)
        
        # 创建HorizontalFlipView组件
        flip_view = HorizontalFlipView(self)
        flip_view.setFixedSize(800, 450)
        flip_view.setBorderRadius(12)
        
        # 准备图片URL列表
        valid_image_urls = []
        base_domain = 'http://leonmmcoset.jjxmm.win:8010'
        logger.info(f"使用的基础域名: {base_domain}")
        
        # 验证并添加有效的图片URL
        if isinstance(images, list):
            logger.info(f"开始处理{len(images)}个图片项")
            for index, image_data in enumerate(images):
                logger.info(f"处理第{index+1}个图片项: {image_data}")
                logger.info(f"图片项类型: {type(image_data)}")
                
                try:
                    if isinstance(image_data, dict):
                        logger.info(f"图片字典键: {image_data.keys()}")
                        
                        if 'image_path' in image_data:
                            image_path = image_data['image_path']
                            logger.info(f"image_path值: {image_path}")
                            logger.info(f"image_path类型: {type(image_path)}")
                            
                            # 确保image_path是字符串类型
                            if not isinstance(image_path, str):
                                logger.warning(f"图片路径不是字符串类型: {type(image_path)}")
                                continue
                            
                            # 构建完整的图片URL
                            logger.info(f"图片路径是否以http开头: {image_path.startswith(('http://', 'https://'))}")
                            logger.info(f"图片路径是否以/开头: {image_path.startswith('/')}")
                            
                            if not image_path.startswith(('http://', 'https://')):
                                # 处理路径格式
                                if image_path.startswith('/'):
                                    image_path = image_path[1:]
                                    logger.info(f"修正后的路径: {image_path}")
                                image_url = f'{base_domain}/{image_path}'
                            else:
                                image_url = image_path
                            
                            logger.info(f"构建的完整URL: {image_url}")
                            
                            # 检查URL是否有效
                            if image_url and len(image_url) > 0:
                                valid_image_urls.append(image_url)
                                logger.info(f"添加有效图片URL: {image_url}")
                        else:
                            logger.warning(f"图片项中没有'image_path'键")
                    else:
                        logger.warning(f"图片项不是字典类型: {type(image_data)}")
                except Exception as e:
                    logger.error(f"处理图片数据时出错: {str(e)}")
        else:
            logger.error(f"images参数不是列表类型: {type(images)}")
        
        logger.info(f"最终有效图片URL列表: {valid_image_urls}")
        logger.info(f"有效图片数量: {len(valid_image_urls)}")
        
        # 添加图片，如果没有有效图片则显示默认提示
        if valid_image_urls:
            # 清空之前的缓存记录
            self.cached_image_paths = []
            
            # 下载并显示图片
            successful_images = 0
            for index, image_url in enumerate(valid_image_urls):
                try:
                    logger.info(f"准备处理第{index+1}张图片: {image_url}")
                    
                    # 生成唯一的缓存文件名
                    file_extension = os.path.splitext(image_url)[1] or '.png'
                    cache_filename = f"{uuid.uuid4()}{file_extension}"
                    cache_file_path = os.path.join(cache_dir, cache_filename)
                    
                    logger.info(f"准备下载到缓存文件: {cache_file_path}")
                    
                    # 下载图片
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"成功下载图片，状态码: 200")
                        
                        # 保存图片到本地缓存
                        with open(cache_file_path, 'wb') as f:
                            f.write(response.content)
                        logger.info(f"图片已保存到: {cache_file_path}")
                        
                        # 记录缓存文件路径
                        self.cached_image_paths.append(cache_file_path)
                        
                        # 尝试从本地文件加载图片
                        pixmap = QPixmap()
                        if pixmap.load(cache_file_path):
                            logger.info(f"成功从本地文件加载图片: {cache_file_path}")
                            
                            # 使用HorizontalFlipView的addImage方法添加本地文件路径
                            flip_view.addImage(cache_file_path)
                            successful_images += 1
                            logger.info(f"成功添加第{index+1}张图片到显示组件")
                        else:
                            logger.error(f"无法加载本地缓存图片: {cache_file_path}")
                            # 如果加载失败，删除缓存文件
                            if os.path.exists(cache_file_path):
                                os.remove(cache_file_path)
                                logger.info(f"删除无效的缓存文件: {cache_file_path}")
                    else:
                        logger.error(f"下载图片失败，状态码: {response.status_code}")
                except Exception as e:
                    logger.error(f"处理图片 {image_url} 时出错: {str(e)}")
            
            logger.info(f"成功加载图片数量: {successful_images}")
            logger.info(f"当前缓存图片路径列表: {self.cached_image_paths}")
            
            # 如果没有成功加载任何图片，显示错误信息
            if successful_images == 0:
                from qfluentwidgets import BodyLabel
                logger.warning("没有成功加载任何图片，显示错误提示")
                error_label = BodyLabel("无法加载预览图片")
                error_label.setAlignment(Qt.AlignCenter)
                error_label.setStyleSheet("color: #e74c3c; font-size: 16px;")
                error_label.setFixedSize(800, 450)
                
                flip_view_layout = QHBoxLayout()
                flip_view_layout.addStretch()
                flip_view_layout.addWidget(error_label)
                flip_view_layout.addStretch()
                
                card_layout.addLayout(flip_view_layout)
            else:
                # 监听当前页码改变信号
                flip_view.currentIndexChanged.connect(lambda index: logger.info(f"当前页面：{index}"))
                
                # 居中显示HorizontalFlipView
                flip_view_layout = QHBoxLayout()
                flip_view_layout.addStretch()
                flip_view_layout.addWidget(flip_view)
                flip_view_layout.addStretch()
                
                card_layout.addLayout(flip_view_layout)
        else:
            # 没有有效图片时显示提示信息
            from qfluentwidgets import BodyLabel
            logger.warning("没有有效图片URL，显示无图片提示")
            no_image_label = BodyLabel("暂无预览图片")
            no_image_label.setAlignment(Qt.AlignCenter)
            no_image_label.setStyleSheet("color: #999; font-size: 16px;")
            no_image_label.setFixedSize(800, 450)
            
            # 替换flip_view为提示标签
            flip_view_layout = QHBoxLayout()
            flip_view_layout.addStretch()
            flip_view_layout.addWidget(no_image_label)
            flip_view_layout.addStretch()
            
            # 添加到卡片布局
            card_layout.addLayout(flip_view_layout)
        
        # 添加到主滚动布局
        self.scroll_layout.addWidget(images_card)
        
    def cleanup_cached_images(self):
        """清理缓存的图片文件"""
        logger.info(f"开始清理缓存图片，共{len(self.cached_image_paths)}个文件")
        
        try:
            # 首先清理记录在cached_image_paths中的文件
            for image_path in self.cached_image_paths:
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logger.info(f"成功删除缓存图片: {image_path}")
                    else:
                        logger.warning(f"缓存图片不存在: {image_path}")
                except Exception as e:
                    logger.error(f"删除缓存图片失败 {image_path}: {str(e)}")
            
            # 清空缓存路径列表
            self.cached_image_paths = []
            
            # 额外清理整个cache文件夹中的所有图片文件
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
            if os.path.exists(cache_dir):
                logger.info(f"开始清理整个缓存文件夹: {cache_dir}")
                for filename in os.listdir(cache_dir):
                    file_path = os.path.join(cache_dir, filename)
                    try:
                        if os.path.isfile(file_path) and filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            os.remove(file_path)
                            logger.info(f"成功删除缓存文件夹中的文件: {filename}")
                    except Exception as e:
                        logger.error(f"删除缓存文件夹中的文件 {filename} 失败: {str(e)}")
            
            logger.info("缓存图片清理完成")
        except Exception as e:
            logger.error(f"缓存清理过程中出现错误: {str(e)}")
        
    def closeEvent(self, event):
        """窗口关闭事件，清理缓存的图片"""
        logger.info("窗口即将关闭，开始清理缓存图片")
        self.cleanup_cached_images()
        super().closeEvent(event)
        
    def __del__(self):
        """析构函数，确保在对象被销毁时也能清理缓存"""
        logger.info("对象即将销毁，执行最终缓存清理")
        # 确保在应用意外退出时也能清理缓存
        try:
            self.cleanup_cached_images()
        except:
            # 避免析构函数中抛出异常
            pass
        
    def _check_image_accessible(self, image_url):
        """检查图片URL是否可访问"""
        try:
            # 发送HEAD请求检查图片是否可访问
            logger.info(f"检查图片URL可访问性: {image_url}")
            response = requests.head(image_url, timeout=5)
            logger.info(f"图片URL状态码: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"检查图片URL可访问性失败: {str(e)}")
            return False
        

    
    def display_app_info_card(self, app_data):
        """显示应用基本信息卡片"""
        info_card = CardWidget()
        info_card.setObjectName("InfoCard")
        info_card.setStyleSheet("""
            #InfoCard {
                background-color: white;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }
        """)
        
        card_layout = QVBoxLayout(info_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # 卡片标题和图标
        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(FluentIcon.INFO.icon().pixmap(18, 18))
        title_icon.setStyleSheet("color: #4CAF50;")
        
        card_title = SubtitleLabel("基本信息")
        card_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(card_title)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)
        
        # 信息网格布局 - 使用两列布局
        info_grid_layout = QGridLayout()
        info_grid_layout.setSpacing(12)
        info_grid_layout.setColumnStretch(0, 1)
        info_grid_layout.setColumnStretch(1, 1)
        
        # 添加基本信息字段，对开发者信息进行特殊处理
        developer_id = app_data.get('developer_id')
        developer_name = "未知开发者"
        
        if developer_id and developer_id != "0":
            # 尝试通过API获取开发者名称，增加错误处理
            try:
                result2 = self.api_client.make_request('getdeveloperinfo', {'id': developer_id})
                if isinstance(result2, dict) and 'success' in result2 and result2['success'] and 'data' in result2:
                    developer_name = result2["data"].get("username", "未知开发者")
            except Exception as e:
                # API调用失败，尝试从本地数据获取
                if 'developer_name' in app_data and app_data['developer_name']:
                    developer_name = app_data['developer_name']
                elif 'developer' in app_data and app_data['developer']:
                    developer_name = app_data['developer']
                elif 'developer_email' in app_data and app_data['developer_email']:
                    developer_name = app_data['developer_email']
        
        info_items = [
            ("应用ID", app_data.get("id", "--")),
            ("开发者", developer_name),
            ("当前版本", app_data.get("version", "--")),
            ("创建时间", app_data.get("created_at", "--"))
        ]
        
        row = 0
        for label_text, value_text in info_items:
            # 创建标签和值
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("color: #666666; font-size: 14px;")
            # 确保value_text是字符串类型
            value = QLabel(str(value_text))
            value.setStyleSheet("color: #333333; font-size: 14px; font-weight: 500;")
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
            # 布局
            item_layout = QVBoxLayout()
            item_layout.addWidget(label)
            item_layout.addWidget(value)
            item_layout.setSpacing(4)
            
            # 添加到网格
            col = row % 2
            actual_row = row // 2
            info_grid_layout.addLayout(item_layout, actual_row, col)
            row += 1
        
        card_layout.addLayout(info_grid_layout)
        self.scroll_layout.addWidget(info_card)
    
    def display_description_card(self, app_data):
        """显示应用描述卡片"""
        description_card = CardWidget()
        description_card.setObjectName("DescriptionCard")
        description_card.setStyleSheet("""
            #DescriptionCard {
                background-color: white;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }
        """)
        
        card_layout = QVBoxLayout(description_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # 卡片标题和图标
        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(FluentIcon.DOCUMENT.icon().pixmap(18, 18))
        title_icon.setStyleSheet("color: #2196F3;")
        
        card_title = SubtitleLabel("应用描述")
        card_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(card_title)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)
        
        # 描述文本
        from PyQt5.QtWidgets import QTextBrowser
        description_text = QTextBrowser()
        description_text.setReadOnly(True)
        description_text.setWordWrapMode(3)  # QTextOption.WrapAtWordBoundaryOrAnywhere
        description_text.setMinimumHeight(200)
        description_text.setOpenExternalLinks(False)  # 禁用自动打开外部链接，由我们自己处理
        description_text.setStyleSheet("""
            QTextBrowser {
                background-color: #FAFAFA;
                border: 1px solid #E5E6EB;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Microsoft YaHei', 'SimHei';
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        # 设置描述内容 - 支持Markdown
        description_text.setHtml(self.convert_markdown_to_html(app_data.get("description", "无描述信息")))
        
        # 连接链接点击信号，处理外部链接打开
        # QTextBrowser组件有anchorClicked信号，可以连接到处理函数
        description_text.anchorClicked.connect(self.handle_link_clicked)
        
        card_layout.addWidget(description_text)
        self.scroll_layout.addWidget(description_card)
    
    def convert_markdown_to_html(self, markdown_text):
        """将Markdown文本转换为HTML"""
        try:
            import markdown
            return markdown.markdown(markdown_text)
        except Exception as e:
            # 如果转换失败，使用原始文本并进行HTML转义
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QTextDocument
            
            # 创建QTextDocument进行HTML转义
            doc = QTextDocument()
            doc.setPlainText(markdown_text)
            return doc.toHtml()
            
    def handle_link_clicked(self, url):
        """处理链接点击事件，使用系统默认浏览器打开外部链接"""
        from PyQt5.QtCore import QUrl
        from PyQt5.QtGui import QDesktopServices
        from qfluentwidgets import InfoBar
        
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
                # 实现打开特定应用详情的逻辑
                self.app_detail_window = AppDetailWindow(self.api_client, app_id, parent=self.parent())
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
    
    def display_action_buttons(self):
        """显示操作按钮区域"""
        button_card = CardWidget()
        button_card.setObjectName("ButtonCard")
        button_card.setStyleSheet("""
            #ButtonCard {
                background-color: white;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }
        """)
        
        button_layout = QHBoxLayout(button_card)
        button_layout.setContentsMargins(20, 20, 20, 20)
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        # 刷新按钮
        refresh_button = PushButton("刷新")
        refresh_button.setIcon(FluentIcon.SYNC)
        refresh_button.clicked.connect(self.load_app_detail)
        refresh_button.setFixedSize(100, 36)
        
        # 安装按钮
        install_button = PrimaryPushButton("安装")
        install_button.setIcon(FluentIcon.DOWNLOAD)
        install_button.setFixedSize(100, 36)
        install_button.clicked.connect(self.install_app)
        
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(install_button)
        self.scroll_layout.addWidget(button_card)
    def install_app(self):
        """安装应用"""
        from qfluentwidgets import InfoBar, MessageBox
        from PyQt5.QtWidgets import QProgressDialog
        from leonapp_gui import get_global_settings
        from loguru import logger
        
        app_name = self.app_data.get('name', '未知应用') if hasattr(self, 'app_data') else '未知应用'
        logger.info(f"用户开始安装应用，应用名称: {app_name}")
        
        # 检查是否有应用数据
        if not hasattr(self, 'app_data'):
            logger.error("应用安装失败：应用数据未加载")
            show_error_dialog("错误", "应用数据未加载，请刷新页面后重试。")
            return
        
        # 创建QFluentWidgets风格的确认对话框
        # 从全局设置获取默认的自动打开选项
        global_settings = get_global_settings()
        default_auto_open = bool(global_settings.auto_open_installer)
        
        confirm_box = MessageBox("确认安装", f"您确定要安装{self.app_data.get('name', '未知应用')}吗？", self)
        
        # 添加自动打开复选框
        from PyQt5.QtWidgets import QCheckBox
        self.auto_open_checkbox = QCheckBox("下载后自动打开安装程序", confirm_box)
        self.auto_open_checkbox.setChecked(default_auto_open)  # 使用全局设置作为默认值
        
        # 将复选框添加到对话框中
        layout = confirm_box.layout()
        layout.addWidget(self.auto_open_checkbox)
        
        # 显示对话框
        reply = confirm_box.exec()
        
        # 保存用户选择
        self.auto_open_installer = self.auto_open_checkbox.isChecked()
        
        if reply == 1:  # QFluentWidgets的MessageBox返回1表示确认
            
            # 1. 首先尝试从应用数据中获取直接下载链接
            download_url = self.app_data.get('direct_download_url')
            
            # 2. 如果没有直接下载链接，尝试使用备用的download_url字段
            if not download_url:
                download_url = self.app_data.get('download_url')
                
            # 3. 根据新API格式，从versions数组中获取最新版本的file_path
            if not download_url and 'versions' in self.app_data and isinstance(self.app_data['versions'], list) and self.app_data['versions']:
                # 假设versions数组中第一个版本是最新的
                latest_version = self.app_data['versions'][0]
                if isinstance(latest_version, dict) and 'file_path' in latest_version:
                    download_url = latest_version['file_path']
            
            # 4. 如果仍然没有下载链接，尝试通过API获取下载链接
            if not download_url:
                try:
                    # 使用app_id通过API获取下载链接
                    app_id = self.app_data.get('id')
                    if app_id:
                        download_result = self.api_client.make_request('getdownloadlink', {'id': app_id})
                        if isinstance(download_result, dict):
                            # 检查是否是新API格式的响应
                            if 'data' in download_result:
                                if isinstance(download_result['data'], dict) and 'versions' in download_result['data'] and download_result['data']['versions']:
                                    latest_version = download_result['data']['versions'][0]
                                    if isinstance(latest_version, dict) and 'file_path' in latest_version:
                                        download_url = latest_version['file_path']
                            # 兼容旧API格式
                            elif 'success' in download_result and download_result['success']:
                                download_url = download_result.get('data')
                except Exception as e:
                    print(f"获取下载链接API调用失败: {str(e)}")
            
            # 4. 如果仍然没有下载链接，显示错误信息
            if not download_url:
                logger.error(f"应用安装失败：无法获取{app_name}的下载链接")
                show_error_dialog("错误", "无法获取应用的下载链接，请稍后重试。\n可能原因：API返回数据中缺少下载链接字段。")
                return
            
            logger.info(f"成功获取{app_name}的下载链接: {download_url}")
            
            # 5. 更健壮的URL处理逻辑
            from urllib.parse import urlparse, quote
            import os
            
            # 检查是否看起来像一个文件名（包含扩展名）
            is_filename = False
            if '.' in download_url:
                # 获取最后一个点后的部分作为扩展名
                extension = download_url.split('.')[-1].lower()
                # 常见的应用安装包扩展名
                common_extensions = ['exe', 'apk', 'dmg', 'pkg', 'msi', 'appx', 'deb', 'rpm']
                if extension in common_extensions and len(extension) <= 5:
                    is_filename = True
            
            # 如果是文件名或不包含协议，处理为完整URL
            if is_filename or not download_url.startswith(('http://', 'https://')):
                # 使用基础域名 - 修正拼写错误
                base_domain = 'leonmmcoset.jjxmm.win:8010'
                
                # 对于所有情况，统一使用直链形式，不再使用download.php
                # 对文件名/路径进行URL编码，处理空格和特殊字符
                if not download_url.startswith(('http://', 'https://')):
                    # 使用http协议和基础域名，直接拼接文件名或路径
                    encoded_path = quote(download_url)
                    download_url = f'http://leonmmcoset.jjxmm.win:8010/{encoded_path.lstrip("/")}'
            
            # 额外检查：确保主机名有效（包含点）
            parsed_url = urlparse(download_url)
            if '.' not in parsed_url.netloc:
                # 如果主机名仍然无效，完全重建URL
                base_domain = 'leonmmcoset.jjxmm.win:8010'
                path = parsed_url.path or parsed_url.netloc
                # 对路径进行URL编码
                encoded_path = quote(path)
                # 使用http协议
                download_url = f'http://leonmmcoset.jjxmm.win:8010/{encoded_path.lstrip("/")}'
            
            # 创建进度对话框
            self.progress_dialog = QProgressDialog(
                f"正在下载{self.app_data.get('name', '未知应用')}...",
                "取消",
                0,
                100,
                parent=self
            )
            self.progress_dialog.setWindowTitle("正在安装")
            self.progress_dialog.setMinimumDuration(0)
            
            # 创建保存路径 - 使用代码文件夹所在的install目录
            # 从下载URL中提取文件扩展名
            import os
            _, file_extension = os.path.splitext(download_url)
            # 如果没有扩展名或者扩展名不合法，使用默认扩展名.zip
            if not file_extension or len(file_extension) < 2:
                file_extension = ".zip"
            app_name = self.app_data.get('name', '未知应用').replace(' ', '_')
            
            # 获取当前脚本所在目录
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 创建install目录路径
            install_dir = os.path.join(current_dir, 'install')
            
            # 确保install目录存在
            if not os.path.exists(install_dir):
                try:
                    os.makedirs(install_dir)
                except Exception as e:
                    # 如果创建目录失败，回退到临时目录
                    show_error_dialog("创建目录失败", f"无法创建安装目录: {str(e)}\n将使用临时目录")
                    temp_dir = tempfile.gettempdir()
                    save_path = os.path.join(temp_dir, f"{app_name}_installer{file_extension}")
                else:
                    # 使用install目录
                    save_path = os.path.join(install_dir, f"{app_name}_installer{file_extension}")
            else:
                # 目录已存在，直接使用
                save_path = os.path.join(install_dir, f"{app_name}_installer{file_extension}")
            
            # 创建下载线程
            self.download_thread = DownloadThread(download_url, save_path)
            self.download_thread.progress.connect(self.progress_dialog.setValue)
            self.download_thread.finished.connect(self.on_download_finished)
            self.download_thread.error.connect(self.on_download_error)
            
            # 开始下载
            self.download_thread.start()
            self.progress_dialog.exec_()
            
    def on_download_finished(self, file_path):
        """下载完成处理"""
        from loguru import logger
        
        app_name = self.app_data.get('name', '未知应用') if hasattr(self, 'app_data') else '未知应用'
        logger.info(f"应用{app_name}下载完成，保存位置: {file_path}")
        
        self.progress_dialog.accept()
        
        # 确保subprocess模块可用
        import subprocess
        
        # 根据操作系统执行不同的安装操作
        if platform.system() == "Windows":
            try:
                # 使用MessageBox显示下载完成提示
                from qfluentwidgets import MessageBox
                
                # 导入全局设置
                from leonapp_gui import get_global_settings
                global_settings = get_global_settings()
                app_open_method = global_settings.app_open_method
                
                # 根据用户选择决定是否自动打开安装程序
                if hasattr(self, 'auto_open_installer') and self.auto_open_installer:
                    try:
                        # 根据配置的应用打开方式执行不同的操作
                        # 0: Windows直接运行应用程序, 1: 打开文件夹方式
                        if app_open_method == 0:  # Windows直接运行应用程序
                            # 根据文件扩展名决定如何处理
                            import os
                            _, ext = os.path.splitext(file_path)
                            ext = ext.lower()
                            
                            # 对于可执行文件，直接运行
                            if ext in [".exe", ".msi", ".bat", ".cmd"]:
                                subprocess.Popen([file_path], shell=True)
                            # 对于其他文件类型，使用系统默认程序打开
                            else:
                                os.startfile(file_path)
                            
                            download_box = MessageBox("下载完成", f"安装程序已启动，请按照向导完成安装。\n文件位置：{file_path}", self)
                            download_box.exec()
                            return  # 成功打开安装程序后不需要再打开文件夹
                        else:  # 打开文件夹方式
                            # 打开下载文件夹并选中文件
                            subprocess.Popen(f'explorer /select,"{file_path}"')
                            download_box = MessageBox("下载完成", f"文件已下载完成，文件夹已打开。\n文件位置：{file_path}", self)
                            download_box.exec()
                            return
                    except Exception as e:
                        show_error_dialog("操作失败", f"无法执行操作: {str(e)}\n您可以手动运行文件: {file_path}")
                else:
                    # 不自动打开，只显示下载完成信息
                    download_box = MessageBox("下载完成", f"文件已下载完成。\n文件位置：{file_path}", self)
                    download_box.exec()
                
                # 如果没有自动打开，或者自动打开失败后，根据配置决定默认行为
                if app_open_method == 0:  # 默认直接运行应用程序
                    try:
                        import os
                        _, ext = os.path.splitext(file_path)
                        ext = ext.lower()
                        
                        if ext in [".exe", ".msi", ".bat", ".cmd"]:
                            subprocess.Popen([file_path], shell=True)
                        else:
                            os.startfile(file_path)
                    except Exception:
                        # 如果运行失败，回退到打开文件夹
                        subprocess.Popen(f'explorer /select,"{file_path}"')
                else:  # 默认打开文件夹
                    # 打开下载文件夹并选中文件
                    subprocess.Popen(f'explorer /select,"{file_path}"')
            except Exception as e:
                show_error_dialog("操作失败", f"无法执行操作: {str(e)}\n您可以手动运行文件: {file_path}")
                
                # 即使操作失败，也尝试打开下载文件夹
                try:
                    subprocess.Popen(f'explorer /select,"{file_path}"')
                except Exception as ex:
                    show_error_dialog("打开文件夹失败", f"无法打开下载文件夹: {str(ex)}")
        else:
            # 其他操作系统
            info_box = QMessageBox()
            info_box.setWindowTitle("下载完成")
            info_box.setIcon(QMessageBox.Information)
            info_box.setText(f"文件已下载完成。\n\n文件位置：{file_path}\n\n请手动运行安装程序。")
            
            # 设置字体大小
            font = QFont()
            font.setPointSize(10)
            info_box.setFont(font)
            
            # 添加按钮
            info_box.setStandardButtons(QMessageBox.Ok)
            
            # 显示对话框
            info_box.exec_()
            
            # 打开下载文件夹
            try:
                import os
                import subprocess
                # 获取文件所在目录
                folder_path = os.path.dirname(file_path)
                if platform.system() == 'Windows':
                    # Windows下使用explorer打开文件夹并选中文件
                    subprocess.Popen(f'explorer /select,"{file_path}"')
                elif platform.system() == 'Darwin':
                    # macOS下使用open命令打开文件夹
                    subprocess.Popen(['open', folder_path])
                else:
                    # Linux下使用xdg-open打开文件夹
                    subprocess.Popen(['xdg-open', folder_path])
            except Exception as e:
                show_error_dialog("打开文件夹失败", f"无法打开下载文件夹: {str(e)}")
            
    def on_download_error(self, error_msg):
        """下载错误处理"""
        from loguru import logger
        
        app_name = self.app_data.get('name', '未知应用') if hasattr(self, 'app_data') else '未知应用'
        logger.error(f"应用{app_name}下载失败: {error_msg}")
        
        self.progress_dialog.reject()
        
        # 使用Sweet Alert风格弹窗显示错误
        show_error_dialog("安装失败", error_msg)
            
    def share_app(self):
        """分享应用"""
        from qfluentwidgets import InfoBar, PushButton
        from PyQt5.QtGui import QClipboard
        from PyQt5.QtWidgets import QApplication, QMessageBox
        import webbrowser
        
        # 创建分享链接
        app_share_url = f"leonapp://app/{self.app_id}"
        web_share_url = f"http://leonmmcoset.jjxmm.win:8010/app?id={self.app_id}"
        
        # 创建自定义对话框
        dialog = QMessageBox(self)
        dialog.setWindowTitle("分享应用")
        dialog.setText(f"请选择分享方式：\n\n{self.app_data.get('name', '未知应用')}")
        dialog.setIcon(QMessageBox.Information)
        
        # 添加按钮
        copy_web_url_btn = dialog.addButton("复制网页链接", QMessageBox.AcceptRole)
        share_wechat_btn = dialog.addButton("分享到微信", QMessageBox.RejectRole)
        copy_app_url_btn = dialog.addButton("复制应用内链接", QMessageBox.ActionRole)
        
        # 显示对话框并处理结果
        dialog.exec_()
        
        clicked_button = dialog.clickedButton()
        if clicked_button == copy_web_url_btn:
            # 复制网页链接
            self.copy_to_clipboard(web_share_url)
        elif clicked_button == share_wechat_btn:
            # 分享到微信（模拟功能）
            InfoBar.info(
                title="分享到微信",
                content="请将以下链接分享给微信好友：\n" + web_share_url,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            self.copy_to_clipboard(web_share_url)
        elif clicked_button == copy_app_url_btn:
            # 复制应用内链接
            self.copy_to_clipboard(app_share_url)
            
    def copy_to_clipboard(self, text):
        # 复制文本到剪贴板
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
    
    def closeEvent(self, event):
        # 关闭窗口事件
        # 如果需要在关闭时执行清理操作，可以在这里添加
        event.accept()