#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件 - 存储LeonApp GUI应用的配置信息
"""

# API相关配置
API_CONFIG = {
    # API基础URL
    'BASE_URL': 'http://localhost/PHP/APP%20Store/api.php',
    
    # 请求超时时间（秒）
    'TIMEOUT': 10,
    
    # 默认每页显示数量
    'DEFAULT_PAGE_SIZE': 20,
    
    # 重试次数
    'RETRY_COUNT': 3,
    
    # 请求头
    'HEADERS': {
        'Content-Type': 'application/json',
        'User-Agent': 'LeonApp-GUI-Client/1.0.0'
    }
}

# 界面相关配置
UI_CONFIG = {
    # 窗口标题
    'WINDOW_TITLE': 'LeonApp 应用商店客户端',
    
    # 默认窗口大小
    'DEFAULT_WIDTH': 1000,
    'DEFAULT_HEIGHT': 700,
    
    # 最小窗口大小
    'MIN_WIDTH': 800,
    'MIN_HEIGHT': 600,
    
    # 主题设置
    'THEME': {
        # 支持 'light' 和 'dark'
        'DEFAULT_THEME': 'light',
        
        # 是否跟随系统主题
        'FOLLOW_SYSTEM_THEME': True
    },
    
    # 显示设置
    'DISPLAY': {
        # 是否显示状态栏
        'SHOW_STATUS_BAR': True,
        
        # 是否显示工具栏
        'SHOW_TOOL_BAR': True,
        
        # 详情窗口宽度占比
        'DETAIL_WIDTH_RATIO': 0.4
    }
}

# 缓存相关配置
CACHE_CONFIG = {
    # 是否启用缓存
    'ENABLE_CACHE': True,
    
    # 缓存目录
    'CACHE_DIR': './cache',
    
    # 缓存过期时间（秒）
    'CACHE_EXPIRY': {
        'APPS': 3600,       # 应用列表缓存1小时
        'TAGS': 86400,      # 标签缓存24小时
        'DEVELOPERS': 86400, # 开发者缓存24小时
        'ANNOUNCEMENTS': 3600, # 公告缓存1小时
        'STATS': 3600       # 统计信息缓存1小时
    }
}

# 日志相关配置
LOG_CONFIG = {
    # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
    'LOG_LEVEL': 'INFO',
    
    # 是否保存日志到文件
    'LOG_TO_FILE': True,
    
    # 日志文件路径
    'LOG_FILE': './logs/leonapp_gui.log',
    
    # 日志文件大小上限（字节）
    'LOG_FILE_MAX_SIZE': 10 * 1024 * 1024,  # 10MB
    
    # 日志文件备份数量
    'LOG_BACKUP_COUNT': 5
}

# 网络连接测试配置
NETWORK_CONFIG = {
    # 连接测试间隔（秒）
    'TEST_INTERVAL': 60,
    
    # 测试URL
    'TEST_URL': 'http://localhost/PHP/APP%20Store/api.php?t=stats'
}

# 搜索相关配置
SEARCH_CONFIG = {
    # 搜索延迟（毫秒） - 用于实时搜索
    'SEARCH_DELAY': 500,
    
    # 搜索结果最小字符数
    'MIN_SEARCH_CHARS': 2
}

# 下载相关配置
DOWNLOAD_CONFIG = {
    # 默认下载目录
    'DEFAULT_DOWNLOAD_DIR': './downloads',
    
    # 下载线程数
    'DOWNLOAD_THREADS': 3
}

# 通知相关配置
NOTIFICATION_CONFIG = {
    # 是否启用桌面通知
    'ENABLE_DESKTOP_NOTIFICATIONS': True,
    
    # 通知显示时间（秒）
    'NOTIFICATION_DISPLAY_TIME': 5
}

# 语言配置
LANGUAGE_CONFIG = {
    # 支持的语言
    'SUPPORTED_LANGUAGES': ['zh_CN', 'en_US'],
    
    # 默认语言
    'DEFAULT_LANGUAGE': 'zh_CN',
    
    # 是否跟随系统语言
    'FOLLOW_SYSTEM_LANGUAGE': True
}

# 安全相关配置
SECURITY_CONFIG = {
    # 是否验证SSL证书
    'VERIFY_SSL': False,
    
    # 启用数据加密
    'ENABLE_ENCRYPTION': False,
    
    # 加密密钥（仅当ENABLE_ENCRYPTION为True时有效）
    'ENCRYPTION_KEY': 'your-encryption-key-here'
}