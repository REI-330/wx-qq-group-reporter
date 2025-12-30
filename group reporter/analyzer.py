# -*- coding: utf-8 -*-
import os
import re
import random
import string
import math
# 尝试导入 jieba_fast（更快），如果失败则回退到 jieba（标准版本）
try:
    import jieba_fast as jieba
except ImportError:
    import jieba
from collections import Counter, defaultdict
import config as cfg
from utils import (
    is_emoji,
    parse_timestamp,
    parse_datetime,
    clean_text,
    calculate_entropy,
    analyze_single_chars,
)
from logger import get_logger, init_logging

init_logging()

# 设置 jieba 日志级别（jieba_fast 和 jieba 都支持，但标准 jieba 可能没有此方法）
try:
    if hasattr(jieba, 'setLogLevel') and hasattr(jieba, 'logging'):
        jieba.setLogLevel(jieba.logging.INFO)
except (AttributeError, Exception):
    # 某些版本的 jieba 可能没有 setLogLevel，忽略错误
    pass

logger = get_logger('analyzer')

_STOPWORDS_CACHE = None

_DIGIT_SYMBOL_PATTERN = re.compile(r'^[\d\W]+$')
_URL_PATTERN = re.compile(r'https?://')
_SENTENCE_SPLIT_PATTERN = re.compile(r'[，。！？、；：""''（）\s\n\r,\.!?\(\)]')

def load_stopwords(force_enable=None):
    """
    加载停用词
    
    Args:
        force_enable: 如果为True，强制加载停用词；如果为False，强制不加载；如果为None，使用配置文件的值
    """
    global _STOPWORDS_CACHE
    
    # 如果强制禁用，直接返回空集合
    if force_enable is False:
        return set()
    
    # 如果缓存已存在且不是强制启用，直接返回缓存
    if _STOPWORDS_CACHE is not None and force_enable is not True:
        return _STOPWORDS_CACHE
    
    # 决定是否启用停用词
    if force_enable is True:
        use_stopwords = True
    else:
        # 安全获取USE_STOPWORDS，如果不存在则默认为False
        use_stopwords = getattr(cfg, 'USE_STOPWORDS', False)
    
    if not use_stopwords:
        logger.info("📚 停用词功能已禁用")
        _STOPWORDS_CACHE = set()
        return _STOPWORDS_CACHE
    
    stopwords = set()
    
    base_dir = os.path.dirname(__file__)
    # 安全获取STOPWORDS_PATHS，如果不存在则使用默认路径
    stopwords_paths = getattr(cfg, 'STOPWORDS_PATHS', [
        'resources/baidu_stopwords.txt',
        'backend/resources/baidu_stopwords.txt'
    ])
    candidate_paths = [os.path.join(base_dir, path) for path in stopwords_paths]
    
    stopwords_path = None
    for p in candidate_paths:
        if os.path.exists(p):
            stopwords_path = p
            break
    
    file_count = 0
    if stopwords_path:
        try:
            encoding = getattr(cfg, 'STOPWORDS_ENCODING', 'utf-8')
            with open(stopwords_path, 'r', encoding=encoding) as f:
                file_words = {line.strip() for line in f if line.strip() and not line.startswith('#')}
            stopwords.update(file_words)
            file_count = len(file_words)
            logger.info(f"📚 从文件加载停用词 {file_count} 个 (来源: {os.path.basename(stopwords_path)})")
        except Exception as e:
            logger.error(f"❌ 加载停用词文件失败: {e}")
    else:
        warn_if_missing = getattr(cfg, 'STOPWORDS_WARN_IF_MISSING', True)
        if warn_if_missing:
            logger.warning(f"⚠️  停用词文件不存在，尝试路径: {candidate_paths}")
    
    manual_words = set(cfg.STOPWORDS_MANUAL) if hasattr(cfg, 'STOPWORDS_MANUAL') else set()
        
    stopwords.update(manual_words)
    manual_count = len(manual_words)
    
    total_count = len(stopwords)
    if manual_count > 0:
        logger.info(f"📝 手动添加停用词 {manual_count} 个")
    logger.info(f"✅ 停用词总数: {total_count} 个 (文件: {file_count}, 手动: {manual_count})")
    
    _STOPWORDS_CACHE = stopwords
    return _STOPWORDS_CACHE


def detect_file_type(data):
    """
    检测文件类型
    
    Args:
        data: JSON数据
        
    Returns:
        'wechat' 或 'qq'
    """
    if not isinstance(data, list) and isinstance(data, dict):
        # 检查是否是QQ格式（有chatInfo等字段）
        if 'chatInfo' in data or 'messages' in data:
            return 'qq'
        # 检查是否是微信格式（通常是消息列表）
        elif 'messages' not in data and isinstance(data.get('messages', []), list):
            # 微信格式通常是消息数组，每个消息有content, sender等字段
            messages = data if isinstance(data, list) else data.get('messages', data)
            if isinstance(messages, list) and len(messages) > 0:
                first_msg = messages[0]
                # 微信消息通常有content, sender, time字段
                if 'content' in first_msg and 'sender' in first_msg and 'time' in first_msg:
                    return 'wechat'

    elif isinstance(data, list):
        # 如果是数组，检查第一个元素
        if len(data) > 0:
            first_item = data[0]
            # 微信格式特征
            if 'content' in first_item and 'sender' in first_item and 'time' in first_item:
                return 'wechat'
            # QQ格式特征
            elif 'messageId' in first_item and 'sender' in first_item and 'content' in first_item:
                return 'qq'

    # 默认返回qq（如果无法确定）
    return 'qq'


def convert_wechat_to_qq(wechat_data, start_date=None, end_date=None, use_stopwords=False):
    """
    将微信数据转换为QQ格式
    
    Args:
        wechat_data: 微信JSON数据
        start_date: 开始日期过滤
        end_date: 结束日期过滤
        use_stopwords: 是否使用停用词
    
    Returns:
        转换后的QQ格式数据
    """
    # 导入转换函数
    from wechat2qq_cli import convert_in_memory
    
    # 如果是列表格式，直接转换
    if isinstance(wechat_data, list):
        qq_data = convert_in_memory(
            wechat_data,
            start_date=start_date,
            end_date=end_date,
            use_stopwords=use_stopwords
        )
    else:
        # 如果是字典格式，提取消息列表
        messages = wechat_data.get('messages', wechat_data)
        if isinstance(messages, list):
            qq_data = convert_in_memory(
                messages,
                start_date=start_date,
                end_date=end_date,
                use_stopwords=use_stopwords
            )
        else:
            raise ValueError("微信数据格式不正确，应为消息列表")
    
    return qq_data


class ChatAnalyzer:
    def __init__(self, data, use_stopwords=None, start_date=None, end_date=None):
        """
        初始化分析器
        
        Args:
            data: JSON数据（微信或QQ格式）
            use_stopwords: 是否使用停用词
            start_date: 开始日期过滤
            end_date: 结束日期过滤
        """
        # 检测文件类型
        self.file_type = detect_file_type(data)
        
        # 如果是微信格式，先转换
        if self.file_type == 'wechat':
            self.converted_data = convert_wechat_to_qq(
                data,
                start_date=start_date,
                end_date=end_date,
                use_stopwords=use_stopwords or False
            )
            # 使用转换后的数据
            self.data = self.converted_data
        else:  # QQ格式
            self.data = data
        
        self.messages = self.data.get('messages', [])
        self.chat_name = self.data.get('chatName', self.data.get('chatInfo', {}).get('name', '未知群聊'))

        # 如果传入了use_stopwords参数，使用传入的值；否则使用配置文件的值
        if use_stopwords is not None:
            self.use_stopwords = use_stopwords
        else:
            # 安全获取USE_STOPWORDS，如果不存在则默认为False
            self.use_stopwords = getattr(cfg, 'USE_STOPWORDS', False)
        
        # 根据use_stopwords参数决定是否加载停用词
        if self.use_stopwords:
            self.stopwords = load_stopwords(force_enable=True)
        else:
            self.stopwords = set()
        
        self._filter_messages_and_build_mappings()
        self.word_freq = Counter()
        self.word_samples = defaultdict(list)
        self.word_contributors = defaultdict(Counter)
        self.user_msg_count = Counter()
        self.user_char_count = Counter()
        self.user_char_per_msg = {}
        self.user_image_count = Counter()
        self.user_forward_count = Counter()
        self.user_reply_count = Counter()
        self.user_replied_count = Counter()
        self.user_at_count = Counter()
        self.user_ated_count = Counter()
        self.user_emoji_count = Counter()
        self.user_link_count = Counter()
        self.user_night_count = Counter()
        self.user_morning_count = Counter()
        self.user_repeat_count = Counter()
        self.hour_distribution = Counter()
        self.discovered_words = set()
        self.merged_words = {}
        self.single_char_stats = {}  
        self.cleaned_texts_with_sender = []  # 改为存储 (文本, 发送者uin) 元组

    
    def _filter_messages_and_build_mappings(self):
        """
        合并时间过滤和构建 uin 到 name 及 msgid_to_sender 的映射，
        减少两次遍历带来的性能开销
        """
        # 安全获取时间过滤配置
        message_start_date = getattr(cfg, 'MESSAGE_START_DATE', None)
        message_end_date = getattr(cfg, 'MESSAGE_END_DATE', None)
        
        if message_start_date is None and message_end_date is None:
            filtered_messages = self.messages
        else:
            from datetime import datetime
            start_dt = None
            end_dt = None
            
            if message_start_date:
                try:
                    start_dt = datetime.strptime(message_start_date, '%Y-%m-%d')
                    start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                    from datetime import timezone, timedelta
                    start_dt = start_dt.replace(tzinfo=timezone(timedelta(hours=8)))
                except Exception as e:
                    logger.warning(f"起始日期格式错误: {message_start_date}, 错误: {e}")
            
            if message_end_date:
                try:
                    end_dt = datetime.strptime(message_end_date, '%Y-%m-%d')
                    end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                    from datetime import timezone, timedelta
                    end_dt = end_dt.replace(tzinfo=timezone(timedelta(hours=8)))
                except Exception as e:
                    logger.warning(f"结束日期格式错误: {message_end_date}, 错误: {e}")
            
            filtered_messages = []
            for msg in self.messages:
                timestamp = msg.get('timestamp', '')
                msg_dt = parse_datetime(timestamp)
                if msg_dt is None:
                    continue
                if start_dt and msg_dt < start_dt:
                    continue
                if end_dt and msg_dt > end_dt:
                    continue
                filtered_messages.append(msg)
            
            filtered_count = len(filtered_messages)
            original_count = len(self.messages)
            if start_dt or end_dt:
                time_range = []
                if start_dt:
                    time_range.append(f"从 {message_start_date}")
                if end_dt:
                    time_range.append(f"到 {message_end_date}")
                logger.info(f"⏰ 时间范围过滤: {' '.join(time_range)}")
                logger.info(f"   原始消息: {original_count} 条, 过滤后: {filtered_count} 条")

        self.messages = filtered_messages
        
        uin_names = defaultdict(list)
        uin_member_names = {}
        msgid_to_sender = {}
        all_uins = set()

        for msg in self.messages:
            if self._is_bot_message(msg):
                continue
            sender = msg.get('sender', {})
            uin = sender.get('uin')
            name = (sender.get('name') or '').strip()
            msg_id = msg.get('messageId')
            if uin:
                all_uins.add(uin)
            if uin and name:
                if not uin_names[uin] or uin_names[uin][-1] != name:
                    uin_names[uin].append(name)
            if uin:
                raw_msg = msg.get('rawMessage', {})
                send_member_name = raw_msg.get('sendMemberName', '').strip()
                if send_member_name:
                    uin_member_names[uin] = send_member_name
            if msg_id and uin:
                msgid_to_sender[msg_id] = uin

        self.uin_to_name = {}
        for uin in all_uins:
            chosen_name = None
            
            # 优先使用有效的name
            if uin in uin_names:
                names = uin_names[uin]
                for name in reversed(names):
                    if name != str(uin):
                        chosen_name = name
                        break
                if chosen_name is None and names:
                    chosen_name = names[-1]
            
            # 其次使用sendMemberName
            if chosen_name is None and uin in uin_member_names:
                chosen_name = uin_member_names[uin]
            
            # 兜底：使用uin本身
            if chosen_name is None or chosen_name == str(uin):
                chosen_name = f"用户{uin}" 
            
            self.uin_to_name[uin] = chosen_name
        
        self.msgid_to_sender = msgid_to_sender

    def _is_bot_message(self, msg):
        """判断是否为机器人消息（基于 subMsgType 或 配置的机器人UIN）"""
        # 安全获取FILTER_BOT_MESSAGES，如果不存在则默认为True
        filter_bot = getattr(cfg, 'FILTER_BOT_MESSAGES', True)
        if not filter_bot:
            return False
        
        raw_msg = msg.get('rawMessage', {})
        sub_msg_type = raw_msg.get('subMsgType', 0)
        if sub_msg_type in [577, 65]:
            return True
        
        # 安全获取BOT_UINS，如果不存在则默认为空列表
        bot_uins = getattr(cfg, 'BOT_UINS', [])
        if bot_uins:
            sender_uin = msg.get('sender', {}).get('uin')
            if sender_uin and str(sender_uin) in [str(uin) for uin in bot_uins]:
                return True
        
        return False

    def get_name(self, uin):
        return self.uin_to_name.get(uin, f"未知用户({uin})")

    def analyze(self):
        logger.info(f"📊 开始分析: {self.chat_name}")
        logger.info(f"🔍 检测到文件类型: {self.file_type}")
        logger.info(f"📝 消息总数: {len(self.messages)}")

        logger.info("🧹 第一轮：处理消息，预处理文本、统计词频和趣味数据...")
        self._process_messages_once()

        logger.info("🔤 分析单字独立性...")
        self.single_char_stats = analyze_single_chars(
            [text for text, _ in self.cleaned_texts_with_sender]
        )

        logger.info("🔍 新词发现...")
        discovered_count = self._discover_new_words()  

        logger.info("🔗 词组合并...")
        merged_count = self._merge_word_pairs()  

        if discovered_count > 0 or merged_count > 0:
            logger.info(f"🔄 发现 {discovered_count} 个新词，合并 {merged_count} 个词组")
            logger.info("🔄 重新分词以应用新词...")
            self._reprocess_word_frequency()
        
        logger.info("🧹 释放临时内存...")
        if self.cleaned_texts_with_sender:
            memory_mb = len(self.cleaned_texts_with_sender) * 100 / 1024 / 1024
            self.cleaned_texts_with_sender.clear()
            logger.debug(f"已释放约 {memory_mb:.1f} MB 内存")

        logger.info("🧹 过滤整理...")
        self._filter_results()

        logger.info("✅ 分析完成!")

    def _process_messages_once(self):
        """一次遍历实现预处理文本、词频统计、趣味统计"""

        skipped = 0
        bot_filtered = 0
        prev_clean = None
        prev_sender = None

        for msg in self.messages:

            if self._is_bot_message(msg):
                continue
            
            sender_uin = msg.get('sender', {}).get('uin')
            if not sender_uin:
                continue

            if self._is_bot_message(msg):
                bot_filtered += 1
                continue
            
            sender_uin = msg.get('sender', {}).get('uin')
            if not sender_uin:
                continue
            
            content = msg.get('content', {})
            text = content.get('text', '') if isinstance(content, dict) else ''

            at_contents = []
            if '@' in text:
                elements = msg.get('rawMessage', {}).get('elements', [])
                for element in elements:
                    text_element = element.get('textElement')
                    if not text_element:
                        continue
                        
                    at_type = text_element.get('atType', 0)
                    content_text = text_element.get('content', '')
                    
                    if at_type == 2 and content_text:
                        at_contents.append(content_text)
                        
            cleaned = clean_text(text, at_contents)
            
            if cleaned and len(cleaned) >= 1:
                self.cleaned_texts_with_sender.append((cleaned, sender_uin))

                words = list(jieba.cut(cleaned))

                for word in words:
                    word = word.strip()
                    if not word:
                        continue
                    if self.use_stopwords and word in self.stopwords:
                        continue
                    
                    self.word_freq[word] += 1
                    if sender_uin:
                        self.word_contributors[word][sender_uin] += 1
                    sample_count = getattr(cfg, 'SAMPLE_COUNT', 10)
                    if len(self.word_samples[word]) < sample_count * 3:
                        self.word_samples[word].append(cleaned)

                self.user_msg_count[sender_uin] += 1
                self.user_char_count[sender_uin] += len(cleaned)
            else:
                if text:
                    skipped += 1

            raw = msg.get('rawMessage', {})
            elements = raw.get('elements', [])

            image_count = 0 
            emoji_count_from_elements = 0 
            has_forward = False
            has_link = False
            has_reply = False

            

            for elem in elements:
                elem_type = elem.get('elementType')
                
                if elem_type == 2:  # 图片元素
                    pic_elem = elem.get('picElement', {})
                    summary = pic_elem.get('summary', '')
                    # 判断是否为表情包（summary格式为 [表情名称]）
                    if summary and summary.startswith('[') and summary.endswith(']'):
                        emoji_count_from_elements += 1
                    else:
                        image_count += 1
                
                elif elem_type == 1:  # 文本元素
                    text_elem = elem.get('textElement', {})
                    at_type = text_elem.get('atType', 0)
                    at_uid = text_elem.get('atUid', '')
                    at_uid_str = str(at_uid) if at_uid else ''
                    if at_type > 0 and at_uid_str and at_uid_str != '0' and at_uid_str != '':
                        self.user_at_count[sender_uin] += 1
                        self.user_ated_count[at_uid_str] += 1
                    
                    # 链接统计
                    text_content = text_elem.get('content', '')
                    if re.search(_URL_PATTERN, text_content):
                        has_link = True
                
                elif elem_type == 10:  # 链接元素
                    has_link = True
                
                elif elem_type == 16 and 'multiForwardMsgElement' in elem:  # 合并转发元素
                    has_forward = True
                
                elif elem_type == 7:  # 回复元素
                    has_reply = True
                    reply_elem = elem.get('replyElement', {})
                    
                    # 优先用 senderUid（如果有的话）
                    target_uin = reply_elem.get('senderUid')
                    
                    # 如果没有，回退到用 msgId 查找
                    if not target_uin or target_uin == '0':
                        ref_msg_id = reply_elem.get('sourceMsgIdInRecords')
                        if not ref_msg_id or ref_msg_id == '0':
                            ref_msg_id = reply_elem.get('replayMsgId')
                        
                        if ref_msg_id and ref_msg_id != '0':
                            target_uin = self.msgid_to_sender.get(ref_msg_id)
                    
                    if target_uin and str(target_uin) != '0':
                        self.user_replied_count[str(target_uin)] += 1
            
            # 统计各项数据
            if image_count > 0:
                self.user_image_count[sender_uin] += image_count  
            
            if has_reply:
                self.user_reply_count[sender_uin] += 1
            
            if has_link:
                self.user_link_count[sender_uin] += 1
            
            if has_forward:
                self.user_forward_count[sender_uin] += 1    

            emojis = content.get('emojis', []) if isinstance(content, dict) else []
            emoji_count = len(emojis) + emoji_count_from_elements
            if emoji_count > 0:
                self.user_emoji_count[sender_uin] += emoji_count
            
            hour = parse_timestamp(msg.get('timestamp', ''))
            if hour is not None:
                self.hour_distribution[hour] += 1
                # 安全获取时间范围配置
                night_owl_hours = getattr(cfg, 'NIGHT_OWL_HOURS', range(0, 6))
                early_bird_hours = getattr(cfg, 'EARLY_BIRD_HOURS', range(6, 9))
                if hour in night_owl_hours:
                    self.user_night_count[sender_uin] += 1
                if hour in early_bird_hours:
                    self.user_morning_count[sender_uin] += 1
            
            if cleaned and len(cleaned) >= 2:
                if cleaned == prev_clean and sender_uin != prev_sender:
                    self.user_repeat_count[sender_uin] += 1

            prev_clean = cleaned
            prev_sender = sender_uin
        
        # 处理跳过及机器人消息计数日志
        if cfg.FILTER_BOT_MESSAGES and bot_filtered > 0:
            logger.debug(f"有效文本: {len(self.cleaned_texts_with_sender)} 条, 跳过: {skipped} 条, 过滤机器人: {bot_filtered} 条")
        else:
            logger.debug(f"有效文本: {len(self.cleaned_texts_with_sender)} 条, 跳过: {skipped} 条")

        # 计算人均字数（保留1位小数）
        for uin in self.user_msg_count:
            msg_count = self.user_msg_count[uin]
            char_count = self.user_char_count[uin]
            if msg_count >= 10:
                self.user_char_per_msg[uin] = round(char_count / msg_count, 1)

    def _discover_new_words(self):
        """新词发现"""
        ngram_freq = Counter()
        left_neighbors = defaultdict(Counter)
        right_neighbors = defaultdict(Counter)
        total_chars = 0
        
        for text, _ in self.cleaned_texts_with_sender:
            sentences = re.split(_SENTENCE_SPLIT_PATTERN, text)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 2:
                    continue
                total_chars += len(sentence)
                
                for n in range(2, min(6, len(sentence) + 1)):
                    for i in range(len(sentence) - n + 1):
                        ngram = sentence[i:i+n]
                        # 只跳过纯空格
                        if not ngram.strip():
                            continue
                        ngram_freq[ngram] += 1
                        if i > 0:
                            left_neighbors[ngram][sentence[i-1]] += 1
                        else:
                            left_neighbors[ngram]['<BOS>'] += 1
                        if i + n < len(sentence):
                            right_neighbors[ngram][sentence[i+n]] += 1
                        else:
                            right_neighbors[ngram]['<EOS>'] += 1
        
        for word, freq in ngram_freq.items():
            if freq < cfg.NEW_WORD_MIN_FREQ:
                continue
            
            # 邻接熵
            left_ent = calculate_entropy(left_neighbors[word])
            right_ent = calculate_entropy(right_neighbors[word])
            min_ent = min(left_ent, right_ent)
            if min_ent < cfg.ENTROPY_THRESHOLD:
                continue
            
            # PMI
            min_pmi = float('inf')
            for i in range(1, len(word)):
                left_freq = ngram_freq.get(word[:i], 0)
                right_freq = ngram_freq.get(word[i:], 0)
                if left_freq > 0 and right_freq > 0:
                    pmi = math.log2((freq * total_chars) / (left_freq * right_freq + 1e-10))
                    min_pmi = min(min_pmi, pmi)
            
            if min_pmi == float('inf'):
                min_pmi = 0
            
            if min_pmi < cfg.PMI_THRESHOLD:
                continue
            
            self.discovered_words.add(word)
        
        for word in self.discovered_words:
            jieba.add_word(word, freq=1000)
        
        discovered_count = len(self.discovered_words)

        logger.debug(f"发现 {len(self.discovered_words)} 个新词")

        return discovered_count

    def _merge_word_pairs(self):
        bigram_counter = Counter()
        word_right_counter = Counter()
        
        for text, _ in self.cleaned_texts_with_sender:
            words = [w for w in jieba.cut(text) if w.strip()]
            for i in range(len(words) - 1):
                w1, w2 = words[i].strip(), words[i+1].strip()
                if not w1 or not w2:
                    continue
                if re.match(_DIGIT_SYMBOL_PATTERN, w1) or re.match(_DIGIT_SYMBOL_PATTERN, w2):
                    continue
                bigram_counter[(w1, w2)] += 1
                word_right_counter[w1] += 1
        
        for (w1, w2), count in bigram_counter.items():
            merged = w1 + w2
            if len(merged) > cfg.MERGE_MAX_LEN:
                continue
            if count < cfg.MERGE_MIN_FREQ:
                continue
            
            # 条件概率 P(w2|w1)
            if word_right_counter[w1] > 0:
                prob = count / word_right_counter[w1]
                if prob >= cfg.MERGE_MIN_PROB:
                    self.merged_words[merged] = (w1, w2, count, prob)
                    jieba.add_word(merged, freq=count * 1000)

        merged_count = len(self.merged_words)
        
        logger.debug(f"合并 {len(self.merged_words)} 个词组")
        
        if self.merged_words:
            sorted_merges = sorted(self.merged_words.items(), key=lambda x: -x[1][2])[:10]
            for merged, (w1, w2, cnt, prob) in sorted_merges:
                logger.debug(f"  {merged}: {w1}+{w2} ({cnt}次, {prob:.0%})")
        
        return merged_count
    
    def _reprocess_word_frequency(self):
        # 清空旧的词频统计
        self.word_freq = Counter()
        self.word_samples = defaultdict(list)
        self.word_contributors = defaultdict(Counter)
        
        # 重新处理每条消息
        for cleaned, sender_uin in self.cleaned_texts_with_sender:
            # 重新分词
            words = list(jieba.cut(cleaned))
            
            for word in words:
                word = word.strip()
                if not word:
                    continue
                if self.use_stopwords and word in self.stopwords:
                    continue
                
                # 重新统计
                self.word_freq[word] += 1
                if sender_uin:
                    self.word_contributors[word][sender_uin] += 1
                if len(self.word_samples[word]) < cfg.SAMPLE_COUNT * 3:
                    self.word_samples[word].append(cleaned)
        
        logger.debug(f"重新分词完成，当前词汇总数: {len(self.word_freq)}")

    def _filter_results(self):
        """过滤结果"""
        filtered_freq = Counter()
        
        for word, freq in self.word_freq.items():
            if len(word) < cfg.MIN_WORD_LEN or len(word) > cfg.MAX_WORD_LEN:
                continue
            if freq < cfg.MIN_FREQ:
                continue
            if is_emoji(word):
                filtered_freq[word] = freq
                continue

            if word in cfg.WHITELIST:
                filtered_freq[word] = freq
                continue
            
            # 单字特殊处理
            if len(word) == 1:
                # 单个符号跳过（但数字/字母走单字统计）
                if word in string.punctuation or word in '，。！？；：、""''（）【】':
                    continue
                # 其他单字（数字/字母/汉字）走独立性检查
                stats = self.single_char_stats.get(word)
                if stats:
                    total, indep, ratio = stats
                    if ratio < cfg.SINGLE_MIN_SOLO_RATIO or indep < cfg.SINGLE_MIN_SOLO_COUNT:
                        continue
                else:
                    continue
                        
            filtered_freq[word] = freq
        
        self.word_freq = filtered_freq
        
        # 采样
        for word in self.word_samples:
            samples = self.word_samples[word]
            sample_count = getattr(cfg, 'SAMPLE_COUNT', 10)
            if len(samples) > sample_count:
                self.word_samples[word] = random.sample(samples, sample_count)
        
        logger.debug(f"过滤后 {len(self.word_freq)} 个词")

    def get_top_words(self, n=None):
        n = n or cfg.TOP_N
        return self.word_freq.most_common(n)

    def get_word_detail(self, word):
        return {
            'word': word,
            'freq': self.word_freq.get(word, 0),
            'samples': self.word_samples.get(word, []),
            'contributors': [(self.get_name(uin), count) 
                           for uin, count in self.word_contributors[word].most_common(cfg.CONTRIBUTOR_TOP_N)]
        }

    def get_fun_rankings(self):
        rankings = {}
        
        def fmt(counter, top_n=cfg.RANK_TOP_N):
            return [(self.get_name(uin), count) for uin, count in counter.most_common(top_n)]
        
        rankings['话痨榜'] = fmt(self.user_msg_count)
        rankings['字数榜'] = fmt(self.user_char_count)
        
        sorted_avg = sorted(self.user_char_per_msg.items(), key=lambda x: x[1], reverse=True)[:cfg.RANK_TOP_N]
        rankings['长文王'] = [(self.get_name(uin), f"{avg:.1f}字/条") for uin, avg in sorted_avg]
        
        rankings['图片狂魔'] = fmt(self.user_image_count)
        rankings['合并转发王'] = fmt(self.user_forward_count)
        rankings['回复狂'] = fmt(self.user_reply_count)
        rankings['被回复最多'] = fmt(self.user_replied_count)
        rankings['艾特狂'] = fmt(self.user_at_count)
        rankings['被艾特最多'] = fmt(self.user_ated_count)
        rankings['表情帝'] = fmt(self.user_emoji_count)
        rankings['链接分享王'] = fmt(self.user_link_count)
        rankings['深夜党'] = fmt(self.user_night_count)
        rankings['早起鸟'] = fmt(self.user_morning_count)
        rankings['复读机'] = fmt(self.user_repeat_count)
        
        return rankings
    
    def export_json(self):
        """导出JSON格式结果（包含uin信息）"""
        top_words = []
        for word, freq in self.get_top_words():
            # 再次在导出阶段过滤停用词，保证报告中不包含停用词
            if self.use_stopwords and word in self.stopwords:
                continue
            top_words.append({
                'word': word,
                'freq': freq,
                'contributors': [
                    {
                        'name': self.get_name(uin),
                        'uin': uin,
                        'count': count
                    }
                    for uin, count in self.word_contributors[word].most_common(cfg.CONTRIBUTOR_TOP_N)
                ],
                'samples': self.word_samples.get(word, [])[:getattr(cfg, 'SAMPLE_COUNT', 10)]
            })

        result = {
            'chatName': self.chat_name,
            'messageCount': len(self.messages),
            'topWords': top_words,
            'rankings': {},
            'hourDistribution': {str(h): self.hour_distribution.get(h, 0) for h in range(24)},
            'fileType': self.file_type  # 添加文件类型信息
        }
        
        # 趣味榜单（包含uin）
        def fmt_with_uin(counter, top_n=cfg.RANK_TOP_N):
            return [
                {'name': self.get_name(uin), 'uin': uin, 'value': count}
                for uin, count in counter.most_common(top_n)
            ]
        
        result['rankings']['话痨榜'] = fmt_with_uin(self.user_msg_count)
        result['rankings']['字数榜'] = fmt_with_uin(self.user_char_count)
        
        # 长文王特殊处理
        sorted_avg = sorted(self.user_char_per_msg.items(), key=lambda x: x[1], reverse=True)[:cfg.RANK_TOP_N]
        result['rankings']['长文王'] = [
            {'name': self.get_name(uin), 'uin': uin, 'value': f"{avg:.1f}字/条"}
            for uin, avg in sorted_avg
        ]
        
        result['rankings']['图片狂魔'] = fmt_with_uin(self.user_image_count)
        result['rankings']['合并转发王'] = fmt_with_uin(self.user_forward_count)
        result['rankings']['回复狂'] = fmt_with_uin(self.user_reply_count)
        result['rankings']['被回复最多'] = fmt_with_uin(self.user_replied_count)
        result['rankings']['艾特狂'] = fmt_with_uin(self.user_at_count)
        result['rankings']['被艾特最多'] = fmt_with_uin(self.user_ated_count)
        result['rankings']['表情帝'] = fmt_with_uin(self.user_emoji_count)
        result['rankings']['链接分享王'] = fmt_with_uin(self.user_link_count)
        result['rankings']['深夜党'] = fmt_with_uin(self.user_night_count)
        result['rankings']['早起鸟'] = fmt_with_uin(self.user_morning_count)
        result['rankings']['复读机'] = fmt_with_uin(self.user_repeat_count)
        
        return result