#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ群聊年度报告生成器 - 主入口

Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.html

Usage:
    python main.py [input_file]
    
    input_file: 可选，JSON文件路径，默认读取config.py中的INPUT_FILE
"""

import sys
import os
import json

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 尝试加载 backend/.env 文件中的环境变量
try:
    from dotenv import load_dotenv
    backend_env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    if os.path.exists(backend_env_path):
        load_dotenv(backend_env_path)
except ImportError:
    pass  # python-dotenv 未安装，跳过

import config as cfg
from utils import load_json, sanitize_filename
from analyzer import ChatAnalyzer
from report_generator import ReportGenerator
from image_generator import ImageGenerator
from logger import get_logger, init_logging

# 初始化日志系统
init_logging()
logger = get_logger('main')


def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = cfg.INPUT_FILE
    
    # 检查文件存在
    if not os.path.exists(input_file):
        logger.error(f"文件不存在: {input_file}")
        logger.info(f"💡 请修改 config.py 中的 INPUT_FILE 或传入文件路径")
        sys.exit(1)
    
    logger.info(f"📂 加载文件: {input_file}")
    
    # 加载数据
    try:
        data = load_json(input_file)
    except Exception as e:
        logger.error(f"文件加载失败: {e}")
        sys.exit(1)
    
    # 创建分析器
    analyzer = ChatAnalyzer(data)
    
    # 执行分析
    analyzer.analyze()
    
    # 生成报告
    reporter = ReportGenerator(analyzer)
    reporter.print_console_report()
    reporter.generate_file_report()

    json_data = analyzer.export_json()
    safe_name = sanitize_filename(analyzer.chat_name)
    json_path = os.path.join(
        os.path.dirname(os.path.abspath(cfg.INPUT_FILE)),
        f"{safe_name}_分析结果.json"
    )
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    logger.info(f"📊 JSON已保存: {json_path}")
    
    # 图片生成（如果启用）
    if cfg.ENABLE_IMAGE_EXPORT:
        logger.info("\n" + "=" * 60)
        logger.info("🖼️  可视化报告生成")
        logger.info("=" * 60)
        
        print("\n选择生成模式:")
        print("  1. 交互式选择热词 (推荐)")
        print("  2. 自动选择前10个热词")
        print("  3. AI智能选词")
        print("  4. 跳过")
        
        choice = input("\n请选择 [1/2/3/4]: ").strip()
        
        if choice == '4':
            logger.info("⏭️ 跳过可视化报告生成")
        else:
            img_gen = ImageGenerator(analyzer)
            
            # 确定是否启用AI锐评
            if cfg.AI_COMMENT_MODE == 'always':
                enable_ai = True
            elif cfg.AI_COMMENT_MODE == 'never':
                enable_ai = False
            else:  # 'ask'
                ai_choice = input("\n🤖 是否生成AI锐评? [Y/n]: ").strip().lower()
                enable_ai = ai_choice in ('', 'y', 'yes')
            
            # 确定是否生成图片
            if cfg.IMAGE_GENERATION_MODE == 'always':
                generate_image = True
            elif cfg.IMAGE_GENERATION_MODE == 'never':
                generate_image = False
            else:  # 'ask'
                img_choice = input("🖼️ 是否生成图片报告? [Y/n]: ").strip().lower()
                generate_image = img_choice in ('', 'y', 'yes')
            
            # 根据选择的模式生成报告
            if choice == '3':
                # AI 智能选词模式
                html_path, img_path = img_gen.generate(ai_select=True, enable_ai=enable_ai, generate_image=generate_image)
            elif choice == '2':
                # 自动选择前10
                html_path, img_path = img_gen.generate(auto_select=True, enable_ai=enable_ai, generate_image=generate_image)
            else:
                # 交互式选择（默认）
                html_path, img_path = img_gen.generate(auto_select=False, enable_ai=enable_ai, generate_image=generate_image)
            
            if html_path:
                logger.info(f"\n📄 HTML报告: {html_path}")
            if img_path:
                logger.info(f"🖼️ 图片报告: {img_path}")
    else:
        logger.info("\n💡 如需生成可视化报告，请设置 ENABLE_IMAGE_EXPORT = True")
    
    logger.info("\n" + "=" * 60)
    logger.info("✨ 全部完成！")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
