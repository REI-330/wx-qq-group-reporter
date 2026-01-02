#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一日志系统
提供多级别日志记录，支持文件和控制台输出
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class LoggerManager:
    """日志管理器"""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def setup(cls, 
              log_dir='runtime_outputs/logs',
              console_level='INFO',
              file_level='DEBUG',
              max_bytes=10*1024*1024,  # 10MB
              backup_count=5):
        """
        初始化日志系统
        
        Args:
            log_dir: 日志文件目录
            console_level: 控制台输出级别
            file_level: 文件输出级别
            max_bytes: 单个日志文件最大大小
            backup_count: 保留的日志文件数量
        """
        if cls._initialized:
            return
        
        # 创建日志目录
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # 保存配置
        cls.log_dir = log_path
        cls.console_level = LOG_LEVELS.get(console_level.upper(), logging.INFO)
        cls.file_level = LOG_LEVELS.get(file_level.upper(), logging.DEBUG)
        cls.max_bytes = max_bytes
        cls.backup_count = backup_count
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name):
        """
        获取指定名称的logger
        
        Args:
            name: logger名称（通常使用模块名）
        
        Returns:
            logging.Logger实例
        """
        if not cls._initialized:
            cls.setup()
        
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # 设置为最低级别，由handler控制
        logger.propagate = False  # 不传播到父logger
        
        logger.handlers.clear()
        
        # 创建格式化器
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(cls.console_level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 文件handler - 使用RotatingFileHandler
        log_file = cls.log_dir / f'{name}.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=cls.max_bytes,
            backupCount=cls.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(cls.file_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def set_console_level(cls, level):
        """动态设置控制台输出级别"""
        new_level = LOG_LEVELS.get(level.upper(), logging.INFO)
        cls.console_level = new_level
        
        # 更新所有logger的控制台handler
        for logger in cls._loggers.values():
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
                    handler.setLevel(new_level)


def get_logger(name):
    """
    便捷函数：获取logger
    
    Args:
        name: logger名称
    
    Returns:
        logging.Logger实例
    """
    return LoggerManager.get_logger(name)


# 全局日志配置（可通过环境变量或config.py控制）
def init_logging(log_mode=None):
    """
    初始化日志系统
    
    Args:
        log_mode: 日志模式 ('simple', 'verbose', 'debug')
                 如果为None，从环境变量或config.py读取
    """
    # 尝试从config.py读取配置
    if log_mode is None:
        try:
            import config as cfg
            log_mode = getattr(cfg, 'LOG_MODE', 'simple')
            log_dir = getattr(cfg, 'LOG_DIR', 'runtime_outputs/logs')
            file_level = getattr(cfg, 'LOG_FILE_LEVEL', 'DEBUG')
            max_bytes = getattr(cfg, 'LOG_MAX_BYTES', 10*1024*1024)
            backup_count = getattr(cfg, 'LOG_BACKUP_COUNT', 5)
            docker_mode = getattr(cfg, 'DOCKER_MODE', False)
        except ImportError:
            log_mode = os.getenv('LOG_MODE', 'simple')
            log_dir = os.getenv('LOG_DIR', 'runtime_outputs/logs')
            file_level = os.getenv('LOG_FILE_LEVEL', 'DEBUG')
            max_bytes = int(os.getenv('LOG_MAX_BYTES', str(10*1024*1024)))
            backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
            docker_mode = os.getenv('DOCKER_MODE', 'false').lower() == 'true'
    else:
        log_dir = os.getenv('LOG_DIR', 'runtime_outputs/logs')
        file_level = os.getenv('LOG_FILE_LEVEL', 'DEBUG')
        max_bytes = int(os.getenv('LOG_MAX_BYTES', str(10*1024*1024)))
        backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        docker_mode = os.getenv('DOCKER_MODE', 'false').lower() == 'true'
    
    # 根据log_mode设置控制台级别
    console_level_map = {
        'simple': 'INFO',    # 简化模式：只显示重要信息
        'verbose': 'INFO',   # 详细模式：显示所有INFO级别
        'debug': 'DEBUG'     # 调试模式：显示所有DEBUG级别
    }
    console_level = console_level_map.get(log_mode, 'INFO')
    
    LoggerManager.setup(
        log_dir=log_dir,
        console_level=console_level,
        file_level=file_level,
        max_bytes=max_bytes,
        backup_count=backup_count
    )
    
    # Docker模式：禁用文件日志
    if docker_mode:
        for logger in LoggerManager._loggers.values():
            logger.handlers = [h for h in logger.handlers if not isinstance(h, RotatingFileHandler)]
    
    # 输出初始化信息（仅在verbose/debug模式）
    if log_mode in ['verbose', 'debug']:
        logger = get_logger('system')
        logger.info(f"📝 日志系统已初始化 (模式: {log_mode})")
        logger.debug(f"日志目录: {log_dir}")
        logger.debug(f"控制台级别: {console_level}, 文件级别: {file_level}")


# 延迟初始化，等待config.py加载
# init_logging() 将在第一次get_logger时自动调用
