import logging
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

# SQLAlchemy 数据模型基础类
Base = declarative_base()

class Message(Base):
    """数据库中消息表的 ORM 模型"""
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    telegram_message_id = Column(BigInteger, nullable=False)
    channel_name = Column(String(255), nullable=False)
    sender_name = Column(String(255))
    message_text = Column(Text, nullable=False)
    message_link = Column(String(512))
    sent_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def save_to_database(db_session, message, channel_name, sender_name, message_link):
    """将一条消息保存到数据库会话中"""
    try:
        # 检查消息是否已存在，防止重复处理
        exists = db_session.query(Message).filter_by(
            telegram_message_id=message.id,
            channel_name=channel_name
        ).first()

        if not exists:
            new_message = Message(
                telegram_message_id=message.id,
                channel_name=channel_name,
                sender_name=sender_name,
                message_text=message.text,
                message_link=message_link,
                sent_at=message.date
            )
            db_session.add(new_message)
            db_session.commit()
            logging.info(f"消息 (ID: {message.id}) 已存入数据库。")
        else:
            logging.info(f"消息 (ID: {message.id}) 已存在于数据库中，跳过。")
    except SQLAlchemyError as e:
        logging.error(f"数据库操作失败: {e}")
        db_session.rollback()
