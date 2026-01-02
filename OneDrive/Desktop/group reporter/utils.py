# -*- coding: utf-8 -*-
import re
import json
import math
from datetime import datetime, timezone, timedelta
from collections import Counter
from logger import get_logger

logger = get_logger(__name__)

def load_json(filepath):
    """
    使用流式解析加载 JSON 文件，减少内存占用
    对于大文件，只保留必要的字段
    """
    try:
        import ijson
        logger.info("📖 使用流式解析加载 JSON 文件...")
        
        with open(filepath, 'rb') as f:
            parser = ijson.parse(f)
            result = {
                'messages': [],
                'chatInfo': {}
            }
            
            current_message = None
            current_element = None
            in_messages = False
            in_elements = False
            message_count = 0
            
            for prefix, event, value in parser:
                if prefix == 'chatInfo.name' and event == 'string':
                    result['chatInfo']['name'] = value
                
                elif prefix == 'messages' and event == 'start_array':
                    in_messages = True
                elif prefix == 'messages' and event == 'end_array':
                    in_messages = False
                
                elif in_messages:
                    if prefix == 'messages.item' and event == 'start_map':
                        current_message = {}
                        message_count += 1
                        if message_count % 10000 == 0:
                            logger.debug(f"   已处理 {message_count} 条消息...")
                    
                    elif prefix == 'messages.item' and event == 'end_map':
                        if current_message:
                            result['messages'].append(current_message)
                            current_message = None
                    
                    # 保留必要字段
                    elif current_message is not None:
                        # 消息 ID
                        if prefix == 'messages.item.messageId' and event == 'string':
                            current_message['messageId'] = value
                        
                        # 时间戳
                        elif prefix == 'messages.item.timestamp' and event in ('string', 'number'):
                            current_message['timestamp'] = str(value)
                        
                        # 发送者信息
                        elif prefix == 'messages.item.sender.uin' and event == 'string':
                            if 'sender' not in current_message:
                                current_message['sender'] = {}
                            current_message['sender']['uin'] = value
                        elif prefix == 'messages.item.sender.name' and event == 'string':
                            if 'sender' not in current_message:
                                current_message['sender'] = {}
                            current_message['sender']['name'] = value
                        
                        # 内容
                        elif prefix == 'messages.item.content.text' and event == 'string':
                            if 'content' not in current_message:
                                current_message['content'] = {}
                            current_message['content']['text'] = value
                        
                        # resources（图片等资源）
                        elif prefix.startswith('messages.item.content.resources'):
                            if 'content' not in current_message:
                                current_message['content'] = {}
                            if 'resources' not in current_message['content']:
                                current_message['content']['resources'] = []
                            
                            if prefix == 'messages.item.content.resources.item' and event == 'start_map':
                                current_message['content']['resources'].append({})
                            elif prefix.endswith('.type') and event == 'string':
                                if current_message['content']['resources']:
                                    current_message['content']['resources'][-1]['type'] = value
                        
                        # emojis
                        elif prefix == 'messages.item.content.emojis' and event == 'start_array':
                            if 'content' not in current_message:
                                current_message['content'] = {}
                            current_message['content']['emojis'] = []
                        elif prefix == 'messages.item.content.emojis.item' and event in ('string', 'start_map'):
                            if 'content' in current_message and 'emojis' in current_message['content']:
                                current_message['content']['emojis'].append({} if event == 'start_map' else value)
                        
                        # mentions
                        elif prefix.startswith('messages.item.content.mentions'):
                            if 'content' not in current_message:
                                current_message['content'] = {}
                            if 'mentions' not in current_message['content']:
                                current_message['content']['mentions'] = []
                            
                            if prefix == 'messages.item.content.mentions.item' and event == 'start_map':
                                current_message['content']['mentions'].append({})
                            elif prefix.endswith('.uid') and event == 'string':
                                if current_message['content']['mentions']:
                                    current_message['content']['mentions'][-1]['uid'] = value
                        
                        # multiForward
                        elif prefix == 'messages.item.content.multiForward' and event == 'start_map':
                            if 'content' not in current_message:
                                current_message['content'] = {}
                            current_message['content']['multiForward'] = {}
                        
                        # 回复信息
                        elif prefix == 'messages.item.content.reply.referencedMessageId' and event == 'string':
                            if 'content' not in current_message:
                                current_message['content'] = {}
                            if 'reply' not in current_message['content']:
                                current_message['content']['reply'] = {}
                            current_message['content']['reply']['referencedMessageId'] = value
                        
                        # rawMessage 中的关键字段
                        elif prefix == 'messages.item.rawMessage.subMsgType' and event == 'number':
                            if 'rawMessage' not in current_message:
                                current_message['rawMessage'] = {}
                            current_message['rawMessage']['subMsgType'] = value
                        elif prefix == 'messages.item.rawMessage.sendMemberName' and event == 'string':
                            if 'rawMessage' not in current_message:
                                current_message['rawMessage'] = {}
                            current_message['rawMessage']['sendMemberName'] = value
                        
                        # 完整保留 elements
                        elif prefix == 'messages.item.rawMessage.elements' and event == 'start_array':
                            if 'rawMessage' not in current_message:
                                current_message['rawMessage'] = {}
                            current_message['rawMessage']['elements'] = []
                            in_elements = True
                        
                        elif prefix == 'messages.item.rawMessage.elements' and event == 'end_array':
                            in_elements = False
                        
                        elif in_elements:
                            if prefix == 'messages.item.rawMessage.elements.item' and event == 'start_map':
                                current_element = {}
                            
                            elif prefix == 'messages.item.rawMessage.elements.item' and event == 'end_map':
                                if current_element:
                                    current_message['rawMessage']['elements'].append(current_element)
                                    current_element = None
                            
                            # 元素类型
                            elif prefix == 'messages.item.rawMessage.elements.item.elementType' and event == 'number':
                                if current_element is not None:
                                    current_element['elementType'] = value
                            
                            # textElement（文本/艾特）
                            elif prefix.startswith('messages.item.rawMessage.elements.item.textElement'):
                                if current_element is not None:
                                    if 'textElement' not in current_element:
                                        current_element['textElement'] = {}
                                    
                                    if prefix.endswith('.atType') and event == 'number':
                                        current_element['textElement']['atType'] = value
                                    elif prefix.endswith('.atUid') and event == 'string':
                                        current_element['textElement']['atUid'] = value
                                    elif prefix.endswith('.content') and event == 'string':
                                        current_element['textElement']['content'] = value
                            
                            # picElement（图片）
                            elif prefix.startswith('messages.item.rawMessage.elements.item.picElement'):
                                if current_element is not None:
                                    if 'picElement' not in current_element:
                                        current_element['picElement'] = {}
                                    
                                    if prefix.endswith('.summary') and event == 'string':
                                        current_element['picElement']['summary'] = value
                            
                            # replyElement（回复）
                            elif prefix.startswith('messages.item.rawMessage.elements.item.replyElement'):
                                if current_element is not None:
                                    if 'replyElement' not in current_element:
                                        current_element['replyElement'] = {}
                                    
                                    if prefix.endswith('.sourceMsgIdInRecords') and event == 'string':
                                        current_element['replyElement']['sourceMsgIdInRecords'] = value
                                    elif prefix.endswith('.replayMsgId') and event == 'string':
                                        current_element['replyElement']['replayMsgId'] = value
                                    elif prefix.endswith('.senderUid') and event in ('string', 'number'):
                                        current_element['replyElement']['senderUid'] = str(value)                            

                            # arkElement（链接/小程序）
                            elif prefix == 'messages.item.rawMessage.elements.item.arkElement' and event == 'start_map':
                                if current_element is not None:
                                    current_element['arkElement'] = {}
                            
                            # multiForwardMsgElement（合并转发）
                            elif prefix == 'messages.item.rawMessage.elements.item.multiForwardMsgElement' and event == 'start_map':
                                if current_element is not None:
                                    current_element['multiForwardMsgElement'] = {}
        
        # 确保群名有值
        chat_name = result['chatInfo'].get('name', '未知群聊')
        if not chat_name:
            chat_name = '未知群聊'
            result['chatInfo']['name'] = chat_name
            
        logger.info(f"✅ 成功加载 {len(result['messages'])} 条消息, 群聊: {chat_name}")
        return result
        
    except ImportError:
        logger.warning("⚠️ ijson 未安装，使用标准加载（大文件可能导致内存不足）")
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"⚠️ 流式解析失败，尝试标准加载: {e}")
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except MemoryError:
            logger.error("❌ 文件过大，无法加载到内存")
            raise MemoryError("JSON 文件过大，请减小文件大小或增加系统内存")
        
def extract_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002600-\U000026FF"
        "\U00002300-\U000023FF"
        "]",
        flags=re.UNICODE
    )
    return emoji_pattern.findall(text)

def is_emoji(char):
    if len(char) != 1:
        return False
    code = ord(char)
    emoji_ranges = [
        (0x1F600, 0x1F64F), (0x1F300, 0x1F5FF), (0x1F680, 0x1F6FF),
        (0x1F1E0, 0x1F1FF), (0x2702, 0x27B0), (0x1F900, 0x1F9FF),
        (0x1FA00, 0x1FA6F), (0x1FA70, 0x1FAFF), (0x2600, 0x26FF), (0x2300, 0x23FF),
    ]
    return any(start <= code <= end for start, end in emoji_ranges)

def parse_timestamp(ts):
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        local_dt = dt.astimezone(timezone(timedelta(hours=8)))
        return local_dt.hour
    except:
        return None

def parse_datetime(ts):
    """
    解析 ISO 8601 时间字符串，返回东八区 datetime 对象
    """
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        local_dt = dt.astimezone(timezone(timedelta(hours=8)))
        return local_dt
    except Exception as e:
        logger.warning(f"解析时间失败: {ts} | 错误: {e}")
        return None

def clean_text(text, at_contents=None):
    """清理文本，去除表情、@、回复等干扰内容"""
    if not text:
        return ""
    
    # 1. 去除@内容
    if at_contents:
        for at_content in at_contents:
            if at_content:
                text = text.replace(at_content, '')
    
    # 2. 去除方括号内容（仅当存在时）
    if '[' in text or ']' in text:
        result = []
        bracket_depth = 0
        for char in text:
            if char == '[':
                bracket_depth += 1
            elif char == ']':
                if bracket_depth > 0:
                    bracket_depth -= 1
            elif bracket_depth == 0:
                result.append(char)
        text = ''.join(result)
    
    # 3. 去除链接（仅当存在时）
    if 'http' in text or 'www.' in text:
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
    
    # 4. 去除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def calculate_entropy(neighbor_freq):
    total = sum(neighbor_freq.values())
    if total == 0:
        return 0
    entropy = 0
    for freq in neighbor_freq.values():
        p = freq / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def generate_time_bar(hour_counts, width=20):
    max_count = max(hour_counts.values()) if hour_counts else 1
    lines = []
    for hour in range(24):
        count = hour_counts.get(hour, 0)
        bar_len = int(count / max_count * width) if max_count > 0 else 0
        bar = '█' * bar_len + '░' * (width - bar_len)
        percentage = count * 100 / sum(hour_counts.values()) if sum(hour_counts.values()) > 0 else 0
        lines.append(f"  {hour:02d}:00 {bar} {count:>5} ({percentage:>4.1f}%)")
    return lines

def sanitize_filename(filename):
    """
    清理文件名中的非法字符
    Windows文件名不允许的字符: < > : " / \\ | ? *
    保留原始字符用于显示，仅在文件名中替换
    """
    if not filename:
        return "未命名"
    
    # 替换Windows非法字符为下划线
    illegal_chars = '<>:"/\\|?*'
    sanitized = filename
    for char in illegal_chars:
        sanitized = sanitized.replace(char, '_')
    
    # 去除首尾空格和点号（Windows不允许）
    sanitized = sanitized.strip('. ')
    
    # 如果清理后为空，返回默认名称
    if not sanitized:
        return "未命名"
    
    return sanitized


def analyze_single_chars(texts):
    total_count = Counter()
    solo_count = Counter()
    boundary_count = Counter()
    punctuation = set('，。！？、；：""''（）,.!?;:\'"()[]【】《》<>…—～·')
    
    for text in texts:
        for char in text:
            if re.match(r'^[\u4e00-\u9fffa-zA-Z]$', char):
                total_count[char] += 1
        
        clean_chars = [c for c in text if re.match(r'^[\u4e00-\u9fffa-zA-Z]$', c)]
        if len(clean_chars) == 1:
            solo_count[clean_chars[0]] += 1
        
        for i, char in enumerate(text):
            if not re.match(r'^[\u4e00-\u9fffa-zA-Z]$', char):
                continue
            left_ok = (i == 0) or (text[i-1] in punctuation) or (text[i-1].isspace())
            right_ok = (i == len(text)-1) or (text[i+1] in punctuation) or (text[i+1].isspace())
            if left_ok and right_ok:
                boundary_count[char] += 1
    
    result = {}
    for char in total_count:
        total = total_count[char]
        solo = solo_count[char]
        boundary = boundary_count[char]
        independent = solo + boundary * 0.5
        ratio = independent / total if total > 0 else 0
        result[char] = (total, independent, ratio)
    
    return result
