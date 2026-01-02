import json
import os
import re
import zlib
from datetime import datetime as dt

class Wechat2QQ:
    """
    微信 JSON → QQ 格式（文件输出版）
    """
    def __init__(self):
        pass


    def is_wechat_file(self, file_path: str, sample_size: int = 8192) -> bool:
        """
        通过探测文件头部的特征关键字来判断格式。
        返回 True  代表是微信导出的 JSON (通常是一个 [ {...} ] 数组)
        返回 False 代表是 QQ 导出的 JSON (通常是一个 { "metadata":... } 对象) 或其他
        """
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 只读取前几 KB，足以包含元数据或前几条消息
                head = f.read(sample_size).strip()
            
            if not head:
                return False

            # --- 核心判断逻辑 ---
            
            # 1. 微信特征判断：
            # 微信导出的通常是消息列表数组，包含 'talker', 'isSelf', 'type' 等
            wechat_signals = ['"talker"', '"talkerName"', '"isSelf"', '"content"']
            # 统计命中特征的数量
            wechat_score = sum(1 for signal in wechat_signals if signal in head)

            # 2. QQ 特征判断：
            # QQ 导出的通常是包含 metadata 的对象
            qq_signals = ['"metadata"', '"chatInfo"', '"messages"', '"QQChatExporter"']
            qq_score = sum(1 for signal in qq_signals if signal in head)

            # 3. 优先级决策
            if head.startswith('[') and wechat_score > 0:
                return True
            if head.startswith('{') and qq_score > wechat_score:
                return False
            
            # 兜底：如果特征不明显，看谁的得分高
            return wechat_score > qq_score

        except (UnicodeDecodeError, IOError):
            # 如果 utf-8 读取失败，尝试用二进制读取寻找关键字
            try:
                with open(file_path, 'rb') as f:
                    head_bin = f.read(sample_size)
                return b'"talker"' in head_bin or b'"isSelf"' in head_bin
            except:
                return False
    def convert_to_file(self, input_path: str, output_path: str):
        """
        读取 input_path，处理后直接写入 output_path，避免返回巨型字符串
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"找不到输入文件: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)

        messages, sender_stats, type_counts, res_stats, timestamps = [], {}, {}, {"total": 0, "byType": {}}, []
        chat_name = "未命名群聊"
        if raw and len(raw) > 0:
            chat_name = raw[0].get('talkerName') or raw[0].get('talker') or "未命名群聊"

        for i, msg in enumerate(raw):
            raw_content = msg.get('content', '')
            sender_id = msg.get('sender', 'unknown')
            sender_name = msg.get('senderName')
            is_self = msg.get('isSelf', False)
            ts_str = msg.get('time')

            # 逻辑处理：群聊 ID 剥离
            final_content_text = raw_content
            if not is_self:
                m = re.match(r'^([a-zA-Z0-9_\-]+):\n([\s\S]*)', raw_content)
                if m and len(m.group(1)) > 5:
                    sender_id, final_content_text = m.group(1), m.group(2)
            
            if not sender_name:
                sender_name = "我" if is_self else sender_id

            sender_uin = self._generate_uin(sender_id)

            # 统计逻辑
            if sender_id not in sender_stats:
                sender_stats[sender_id] = {"name": sender_name, "count": 0, "uin": sender_uin}
            sender_stats[sender_id]["count"] += 1

            # 时间处理
            try:
                dt_obj = dt.fromisoformat(ts_str)
                ts_millis = dt_obj.timestamp() * 1000
                timestamps.append(ts_millis)
                unix_time_str = str(int(dt_obj.timestamp()))
            except:
                ts_millis, unix_time_str = 0, "0"

            # 消息类型映射
            wx_type = msg.get('type')
            msg_type_int, content_obj = 2, {"text": "", "resources": [], "mentions": [], "raw": ""}

            if wx_type == 1:
                content_obj['text'] = final_content_text
                type_counts['text'] = type_counts.get('text', 0) + 1
            elif wx_type == 3:
                path = msg.get('contents', {}).get('path', '') if isinstance(msg.get('contents'), dict) else ''
                content_obj.update(text="[图片]", resources=[{"type": "image", "fileName": path}])
                type_counts['image'] = type_counts.get('image', 0) + 1
                res_stats['total'] += 1
            elif wx_type == 47:
                content_obj['text'] = "[表情]"
                type_counts['emoji'] = type_counts.get('emoji', 0) + 1
            elif wx_type == 49:
                content_obj['text'] = "[文件/链接]"
                type_counts['file'] = type_counts.get('file', 0) + 1
            elif wx_type == 10000:
                msg_type_int, content_obj['text'] = 5, final_content_text
                type_counts['system'] = type_counts.get('system', 0) + 1
            else:
                content_obj['text'] = "[其他消息]"
                type_counts['system'] = type_counts.get('system', 0) + 1

            # 构建消息对象
            messages.append({
                "messageId": str(msg.get('id', i)),
                "messageSeq": str(msg.get('seq', i)),
                "timestamp": ts_str,
                "sender": {"uid": sender_id, "uin": sender_uin, "name": sender_name},
                "receiver": {"uid": "group", "type": "group"},
                "messageType": msg_type_int,
                "content": content_obj,
                "rawMessage": {
                    "msgTime": unix_time_str,
                    "senderUin": sender_uin,
                    "sendNickName": sender_name,
                    "elements": [{"textElement": {"content": content_obj['text']}}]
                }
            })

        # 时间范围计算
        tr = {"start": "", "end": "", "durationDays": 0}
        if timestamps:
            t_min, t_max = min(timestamps), max(timestamps)
            tr = {
                "start": dt.fromtimestamp(t_min / 1000).isoformat(),
                "end": dt.fromtimestamp(t_max / 1000).isoformat(),
                "durationDays": int((t_max - t_min) / 86400000) or 1
            }

        # 组装最终结果
        final_data = {
            "metadata": {"name": "QQChatExporter V5", "version": "5.0.0"},
            "chatInfo": {"name": chat_name, "type": "group"},
            "statistics": {
                "totalMessages": len(messages),
                "timeRange": tr,
                "messageTypes": type_counts,
                "senders": sorted([{"uid": k, "name": v['name'], "messageCount": v['count']} for k,v in sender_stats.items()], key=lambda x: x['messageCount'], reverse=True),
                "resources": res_stats
            },
            "messages": messages
        }

        # --- 关键步骤：流式写入文件 ---
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(final_data, f_out, ensure_ascii=False, indent=2)

    @staticmethod
    def _generate_uin(wxid: str) -> str:
        return "0" if not wxid else str(zlib.crc32(wxid.encode('utf-8')))