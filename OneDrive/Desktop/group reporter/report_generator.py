# -*- coding: utf-8 -*-

import os
from datetime import datetime

import config as cfg
from utils import generate_time_bar, sanitize_filename
from logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, analyzer, output_dir=None):
        """
        初始化报告生成器
        
        Args:
            analyzer: ChatAnalyzer实例
        """
        self.analyzer = analyzer
        self.chat_name = analyzer.chat_name
        self.output_dir = output_dir
    
    def print_console_report(self):
        """输出控制台简洁报告"""
        logger.info("\n" + "=" * cfg.CONSOLE_WIDTH)
        logger.info(f"📊 {self.chat_name} - 年度热词报告")
        logger.info("=" * cfg.CONSOLE_WIDTH)
        
        # 热词Top20
        logger.info("\n🔥 热词 Top 20:")
        logger.info("-" * 40)
        for i, (word, freq) in enumerate(self.analyzer.get_top_words(20), 1):
            logger.info(f"  {i:>2}. {word:<15} {freq:>5}次")
        
        # 趣味榜单（每个只显示Top3）
        logger.info("\n🎮 趣味榜单:")
        logger.info("-" * 40)
        rankings = self.analyzer.get_fun_rankings()
        
        emojis = {
            '话痨榜': '🏆', '字数榜': '📝', '长文王': '📖',
            '图片狂魔': '🖼️', '合并转发王': '📦', '回复狂': '💬',
            '被回复最多': '🎯', '艾特狂': '📢', '被艾特最多': '🎯',
            '表情帝': '😂', '链接分享王': '🔗', '深夜党': '🌙',
            '早起鸟': '🌅', '复读机': '🔄'
        }
        
        for title, data in rankings.items():
            if not data:
                continue
            emoji = emojis.get(title, '📌')
            top1 = data[0] if data else ('无', 0)
            logger.info(f"  {emoji} {title}: {top1[0]} ({top1[1]})")
        
        # 时段分布
        logger.info("\n⏰ 活跃时段分布:")
        logger.info("-" * 40)
        hour_data = self.analyzer.hour_distribution
        if hour_data:
            peak_hour = max(hour_data, key=hour_data.get)
            logger.info(f"  最活跃时段: {peak_hour}:00 - {peak_hour+1}:00")
        
        logger.info("\n" + "=" * cfg.CONSOLE_WIDTH)
        logger.info("💡 详细报告已保存到文件")
        logger.info("=" * cfg.CONSOLE_WIDTH)
    
    def generate_file_report(self):
        """生成详细文件报告"""
        # 构建输出路径（与输入文件同目录）
        if self.output_dir:
            input_dir = self.output_dir
        else:
            input_dir = os.path.dirname(os.path.abspath(cfg.INPUT_FILE))
        safe_name = sanitize_filename(self.chat_name)
        output_file = os.path.join(input_dir, f"{safe_name}_年度热词报告.txt")
        
        lines = []
        
        # 标题
        lines.append("=" * 60)
        lines.append(f"  📊 {self.chat_name} - 年度热词报告")
        lines.append(f"  📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  📝 消息总数: {len(self.analyzer.messages)}")
        lines.append("=" * 60)
        lines.append("")
        
        # ========== 热词排行 ==========
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + "🔥 热词排行榜".center(54) + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append("")
        
        for i, (word, freq) in enumerate(self.analyzer.get_top_words(), 1):
            detail = self.analyzer.get_word_detail(word)
            
            lines.append(f"【{i}】{word}  —— 出现 {freq} 次")
            
            # 贡献者
            if detail['contributors']:
                contributors_str = ', '.join(
                    f"{name}({count}次)" for name, count in detail['contributors'][:5]
                )
                lines.append(f"    👤 贡献者: {contributors_str}")
            
            # 样本
            if detail['samples']:
                lines.append(f"    📋 随机样本:")
                for sample in detail['samples'][:cfg.SAMPLE_COUNT]:
                    # 截断过长的样本
                    sample_short = sample[:80] + "..." if len(sample) > 80 else sample
                    sample_short = sample_short.replace('\n', ' ')
                    lines.append(f"       • {sample_short}")
            
            lines.append("")
        
        # ========== 趣味统计 ==========
        lines.append("")
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + "🎮 趣味统计榜".center(54) + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append("")
        
        rankings = self.analyzer.get_fun_rankings()
        
        rank_configs = [
            ('话痨之王', '话痨榜', '🏆', '条'),
            ('字数冠军', '字数榜', '📝', '字'),
            ('长文达人', '长文王', '📖', ''),
            ('表情狂人', '表情帝', '😂', '个'),
            ('图片轰炸', '图片狂魔', '🖼️', '张'),
            ('转发大师', '合并转发王', '📦', '次'),
            ('回复达人', '回复狂', '💬', '次'),
            ('人气之星', '被回复最多', '⭐', '次'),
            ('艾特狂魔', '艾特狂', '📢', '次'),
            ('万众瞩目', '被艾特最多', '🎯', '次'),
            ('链接分享', '链接分享王', '🔗', '条'),
            ('深夜战士', '深夜党', '🌙', '条'),
            ('黎明先锋', '早起鸟', '🌅', '条'),
            ('复读机器', '复读机', '🔄', '次'),
        ]
        
        for title, key, icon, unit in rank_configs:
            data = rankings.get(key, [])
            if not data:
                continue
            
            lines.append(f"【{title}】")
            for i, (name, count) in enumerate(data, 1):
                if isinstance(count, str):  # 长文王的特殊格式
                    lines.append(f"  {i:>2}. {name:<20} {count}")
                else:
                    lines.append(f"  {i:>2}. {name:<20} {count}{unit}")
            lines.append("")
        
        # ========== 时段分布 ==========
        lines.append("")
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + "⏰ 24小时活跃分布".center(52) + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append("")
        
        hour_data = self.analyzer.hour_distribution
        if hour_data:
            for line in generate_time_bar(hour_data):
                lines.append(line)
        
        # ========== 页脚 ==========
        lines.append("")
        lines.append("=" * 60)
        lines.append("  Generated by QQgroup Annual Report Analyzer")
        lines.append("  Author: Claude Opus 4.5 & Huixi")
        lines.append("=" * 60)
        
        # 写入文件
        with open(output_file, 'w', encoding=cfg.OUTPUT_ENCODING) as f:
            f.write('\n'.join(lines))
        
        logger.info(f"\n📄 报告已保存: {output_file}")
        return output_file
