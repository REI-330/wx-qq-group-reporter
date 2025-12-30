#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

import sys
import pymysql
from db_service import DatabaseService
from logger import get_logger

logger = get_logger(__name__)


def check_database_exists(cursor, database):
    cursor.execute(f"SHOW DATABASES LIKE '{database}'")
    return cursor.fetchone() is not None


def check_table_exists(cursor, table):
    cursor.execute(f"SHOW TABLES LIKE '{table}'")
    return cursor.fetchone() is not None


def main():
    force = '--force' in sys.argv
    db_service = DatabaseService()
    database = db_service.config['database']
    
    config_without_db = db_service.config.copy()
    config_without_db.pop('database')
    
    logger.info(f"连接到 MySQL 服务器 {db_service.config['host']}:{db_service.config['port']}...")
    
    conn = pymysql.connect(**config_without_db)
    try:
        with conn.cursor() as cursor:
            db_exists = check_database_exists(cursor, database)
            logger.info(f"数据库 {database} 存在状态: {db_exists}")
            
            if not force and db_exists:
                cursor.execute(f"USE {database}")
                table_exists = check_table_exists(cursor, 'reports')
                logger.info(f"表 reports 存在状态: {table_exists}")
                
                if table_exists:
                    logger.info(f"✓ 数据库 {database} 和表 reports 已存在")
                    logger.info("✓ 跳过初始化，使用现有数据库")
                    logger.info("\n💡 提示：如需重新初始化数据库，请运行：")
                    logger.info("   python backend/init_db.py --force")
                    return
                else:
                    logger.info(f"⚠️  数据库 {database} 存在，但表 reports 不存在")
                    logger.info("开始创建表...")
            
            # 执行初始化
            if force:
                logger.info("⚠️  强制初始化模式：将删除现有数据库表并重新初始化")
                if db_exists:
                    cursor.execute(f"USE {database}")
                    cursor.execute("DROP TABLE IF EXISTS reports")
                    conn.commit()
                    logger.info("✓ 旧表已删除")
            else:
                if not db_exists:
                    logger.info(f"数据库 {database} 不存在，开始创建数据库和表...")
                else:
                    logger.info("开始创建表...")
    finally:
        conn.close()
    
    # 调用统一的初始化方法
    logger.info("执行数据库初始化...")
    db_service.init_database()
    logger.info("✅ 数据库初始化完成！")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"\n❌ 初始化失败: {e}")
        exit(1)
