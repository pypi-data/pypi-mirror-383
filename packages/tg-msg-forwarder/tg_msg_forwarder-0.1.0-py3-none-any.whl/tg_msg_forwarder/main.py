import os
import re
import json
import logging
import asyncio
import argparse
from datetime import datetime, timedelta, timezone

from telethon import TelegramClient, events
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .actions import send_to_dingtalk, send_to_feishu, send_to_slack
from .db import Base, save_to_database

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path):
    """从指定的 JSON 文件加载配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"错误: 配置文件 '{config_path}' 未找到ảng")
        exit(1)
    except json.JSONDecodeError:
        logging.error(f"错误: 配置文件 '{config_path}' 格式无效ảng")
        exit(1)

# --- 查询功能 ---
async def list_my_channels(client):
    """列出用户所在的所有频道/群组。"""
    logging.info("正在获取频道与群组列表...")
    print("\n--- 您账户下的频道与群组列表 ---")
    async for dialog in client.iter_dialogs():
        if dialog.is_channel or dialog.is_group:
            print(f"名称: {dialog.title:<40} | ID: {dialog.entity.id}")
    print("------------------------------------")
    logging.info("列表获取完毕。对于私有频道/群组，请在配置文件中使用其数字 IDảng")

async def list_contacts(client):
    """列出用户的所有联系人。"""
    logging.info("正在获取联系人列表...")
    print("\n--- 您账户下的联系人列表 ---")
    contacts = await client.get_contacts()
    for contact in contacts:
        full_name = f"{contact.first_name} {contact.last_name or ''}".strip()
        username = f"@{contact.username}" if contact.username else "N/A"
        print(f"姓名: {full_name:<40} | Username: {username:<15} | ID: {contact.id}")
    print("---------------------------------")

async def get_channel_info(client, identifier):
    """获取指定频道/群组的详细信息。"""
    logging.info(f"正在查询 '{identifier}' 的详细信息...")
    try:
        entity = await client.get_entity(identifier)
        print(f"\n--- 频道/群组 '{identifier}' 的详细信息 ---")
        print(f"{'频道名称:':<15} {entity.title}")
        print(f"{'的ID:':<15} {entity.id}")
        if hasattr(entity, 'username') and entity.username: print(f"{'用户名:':<15} {entity.username}")
        entity_type = "N/A"
        if getattr(entity, 'broadcast', False): entity_type = "Channel (Broadcast)"
        elif getattr(entity, 'megagroup', False): entity_type = "Supergroup"
        elif getattr(entity, 'gigagroup', False): entity_type = "Gigagroup"
        elif hasattr(entity, 'participants_count'): entity_type = "Group"
        print(f"{'的类型:':<15} {entity_type}")
        if hasattr(entity, 'participants_count') and entity.participants_count: print(f"{'成员/订阅数:':<15} {entity.participants_count}")
        if hasattr(entity, 'date'): print(f"{'创建日期:':<15} {entity.date}")
        print("-----------------------------------------")
    except ValueError: logging.error(f"错误: 无法找到与 '{identifier}' 对应的频道、群组或用户ảng")
    except Exception as e: logging.error(f"查询时发生未知错误: {e}")

# --- 消息处理核心逻辑 ---
async def process_message(message, client, config, db_engines):
    """处理单条消息（无论是实时还是历史消息）的通用函数"""
    if not message or not message.text: return
    try:
        chat = await client.get_entity(message.peer_id)
        sender = await message.get_sender()
        channel_name = getattr(chat, 'username', chat.title)
        sender_name = getattr(sender, 'username', f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip())
        message_link = f"https://t.me/{channel_name}/{message.id}" if getattr(chat, 'username', None) else "N/A (私有频道)"
        channel_id = message.chat_id
        channel_username = getattr(chat, 'username', None)
        
        channel_config = next((c for c in config['channels'] if c['name'] == channel_id or c['name'] == channel_username), None)
        if not channel_config: return

        # --- 过滤逻辑 ---
        channel_filters = channel_config.get('filters', {})
        if channel_filters:
            text_lower = message.text.lower()
            exclude_keywords = [kw.lower() for kw in channel_filters.get('exclude_keywords', [])]
            if any(kw in text_lower for kw in exclude_keywords):
                logging.info(f"消息 (ID: {message.id}) 因包含排除关键词而被跳过ảng")
                return
            include_keywords = [kw.lower() for kw in channel_filters.get('include_keywords', [])]
            if include_keywords and not any(kw in text_lower for kw in include_keywords):
                logging.info(f"消息 (ID: {message.id}) 因不包含指定关键词而被跳过ảng")
                return

        for action in channel_config.get('actions', []):
            # --- 模板逻辑 ---
            default_formatted_message = (f"**来源频道**: {channel_name}\n\n"
                                         f"**发送者**: {sender_name}\n\n"
                                         f"**时间**: {message.date.strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n\n"
                                         f"**内容**:\n{message.text}\n\n"
                                         f"[查看原文]({message_link})")
            template = action.get('template')
            if template:
                try:
                    formatted_message = template.format(channel_name=channel_name, sender_name=sender_name, time=message.date.strftime('%Y-%m-%d %H:%M:%S'), text=message.text, link=message_link)
                except KeyError as e:
                    logging.warning(f"模板格式错误，缺少键: {e}。将使用默认格式ảng")
                    formatted_message = default_formatted_message
            else:
                formatted_message = default_formatted_message
            
            # --- 执行动作 ---
            action_type = action.get('type')
            details = action.get('details', {})
            if action_type == 'dingtalk': send_to_dingtalk(details.get('webhook_url'), details.get('secret'), formatted_message)
            elif action_type == 'feishu': send_to_feishu(details.get('webhook_url'), formatted_message)
            elif action_type == 'slack': send_to_slack(details.get('webhook_url'), formatted_message)
            elif action_type in ['sqlite', 'mysql']:
                conn_str = f"sqlite:///{details.get('db_path')}" if action_type == 'sqlite' else details.get('connection_string')
                engine = db_engines.get(conn_str)
                if engine:
                    DBSession = sessionmaker(bind=engine)
                    db_session = DBSession()
                    save_to_database(db_session, message, channel_name, sender_name, message_link)
                    db_session.close()
    except Exception as e: logging.error(f"处理消息 (ID: {message.id}) 时发生未知错误: {e}", exc_info=True)

def init_db_engines(config):
    """根据配置初始化所有需要的数据库引擎"""
    db_engines = {}
    for channel in config.get('channels', []):
        for action in channel.get('actions', []):
            if action['type'] in ['sqlite', 'mysql']:
                if action['type'] == 'sqlite':
                    db_path = action['details'].get('db_path')
                    if db_path:
                        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
                        conn_str = f'sqlite:///{db_path}'
                    else: continue
                else: conn_str = action['details'].get('connection_string')
                if conn_str and conn_str not in db_engines:
                    try:
                        engine = create_engine(conn_str)
                        db_engines[conn_str] = engine
                        Base.metadata.create_all(engine)
                        logging.info(f"数据库引擎已为 '{conn_str}' 初始化ảng")
                    except Exception as e: logging.error(f"初始化数据库引擎 '{conn_str}' 失败: {e}")
    return db_engines

# --- 主功能模块 ---
async def start_forwarder(client, config, db_engines):
    """实时转发器的主逻辑"""
    @client.on(events.NewMessage(chats=[channel['name'] for channel in config['channels']]))
    async def handler(event):
        logging.info(f"收到来自 [{getattr(event.chat, 'title', event.chat_id)}] 的新消息...")
        await process_message(event.message, client, config, db_engines)
    logging.info("客户端已启动，正在监听新消息...")
    await client.run_until_disconnected()

def parse_duration(duration_str):
    """解析时长字符串 (e.g., '7d', '24h', '30m') 为 timedelta 对象"""
    match = re.match(r"(\d+)([dhm])", duration_str.lower())
    if not match: raise ValueError("无效的时长格式。请使用例如 '7d', '24h', '30m'ảng")
    value, unit = int(match.group(1)), match.group(2)
    if unit == 'd': return timedelta(days=value)
    if unit == 'h': return timedelta(hours=value)
    if unit == 'm': return timedelta(minutes=value)

async def process_historical_messages(client, config, db_engines, duration_str):
    """一次性处理历史消息"""
    try: duration = parse_duration(duration_str)
    except ValueError as e:
        logging.error(e)
        return
    start_date = datetime.now(timezone.utc) - duration
    logging.info(f"开始处理自 {start_date.strftime('%Y-%m-%d %H:%M:%S')} 以来的历史消息...")
    for channel_config in config.get('channels', []):
        channel_identifier = channel_config['name']
        logging.info(f"正在处理频道 '{channel_identifier}' 的历史记录...")
        try:
            async for message in client.iter_messages(channel_identifier, offset_date=start_date, reverse=True):
                await process_message(message, client, config, db_engines)
        except Exception as e: logging.error(f"处理频道 '{channel_identifier}' 的历史记录时出错: {e}")
    logging.info("所有历史消息处理完毕ảng")

def cli_entry():
    """命令行工具入口函数"""
    parser = argparse.ArgumentParser(description="Telegram Message Forwarder and Management Tool.")
    parser.add_argument("-c", "--config", required=True, help="Path to the configuration JSON file.")
    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument("--list-channels", action="store_true", help="List all channels/groups and exit.")
    query_group.add_argument("--list-contacts", action="store_true", help="List all contacts (friends) and exit.")
    query_group.add_argument("--channel-info", metavar="ID_OR_USERNAME", help="Get detailed info for a specific channel/group and exit.")
    query_group.add_argument("--process-history", metavar="DURATION", help="Process historical messages for a given duration (e.g., 7d, 24h, 30m) and exit.")
    args = parser.parse_args()
    config = load_config(args.config)
    tg_config = config.get('telegram', {})
    if not all([tg_config.get('api_id'), tg_config.get('api_hash')]):
        logging.error("配置不完整。请确保 api_id 和 api_hash 已在配置文件中正确设置ảng")
        exit(1)
    session_file = os.path.join(os.path.dirname(args.config), tg_config.get('session_name', 'default_session'))
    client = TelegramClient(session_file, tg_config['api_id'], tg_config['api_hash'])
    async def run_tasks():
        async with client:
            if args.list_channels: await list_my_channels(client)
            elif args.list_contacts: await list_contacts(client)
            elif args.channel_info: await get_channel_info(client, args.channel_info)
            elif args.process_history:
                db_engines = init_db_engines(config)
                await process_historical_messages(client, config, db_engines, args.process_history)
            else:
                db_engines = init_db_engines(config)
                await start_forwarder(client, config, db_engines)
    try: asyncio.run(run_tasks())
    except (KeyboardInterrupt, SystemExit): logging.info("操作已取消或服务已停止ảng")
    except Exception as e: logging.error(f"程序启动时发生严重错误: {e}", exc_info=True)

if __name__ == '__main__':
    cli_entry()
