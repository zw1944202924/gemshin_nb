import requests
from sqlalchemy.orm import Session
from backend.app.models import Notification, User
from backend.app.schemas.notification import NotificationCreate, UserNotifyConfig
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    is_read: Optional[bool] = None
) -> List[Notification]:
    """获取通知列表"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_notification_by_id(db: Session, notification_id: int, user_id: int):
    """获取指定通知"""
    return db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()


def create_notification(
    db: Session,
    user_id: int,
    notification: NotificationCreate
) -> Notification:
    """创建通知记录"""
    db_notification = Notification(
        user_id=user_id,
        title=notification.title,
        content=notification.content,
        notify_type=notification.notify_type
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def mark_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """标记通知为已读"""
    notification = get_notification_by_id(db, notification_id, user_id)
    if not notification:
        return None
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    """删除通知"""
    notification = get_notification_by_id(db, notification_id, user_id)
    if not notification:
        return False
    db.delete(notification)
    db.commit()
    return True


def update_user_notify_config(
    db: Session,
    user_id: int,
    config: UserNotifyConfig
) -> User:
    """更新用户通知配置"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    if config.feishu_webhook is not None:
        user.feishu_webhook = config.feishu_webhook
    if config.email is not None:
        user.email = config.email

    db.commit()
    db.refresh(user)
    return user


def send_feishu_notification(webhook: str, title: str, content: str) -> bool:
    """发送飞书通知"""
    try:
        payload = {
            "msg_type": "text",
            "content": {
                "text": f"{title}\n{content}"
            }
        }
        response = requests.post(webhook, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def send_email_notification(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    to_email: str,
    title: str,
    content: str
) -> bool:
    """发送邮件通知"""
    try:
        msg = MIMEMultipart()
        msg["From"] = username
        msg["To"] = to_email
        msg["Subject"] = title

        msg.attach(MIMEText(content, "plain", "utf-8"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)

        return True
    except Exception:
        return False


def send_notification(
    db: Session,
    user_id: int,
    notify_type: str,
    title: str,
    content: str
) -> dict:
    """发送通知"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "用户不存在"}

    if notify_type == "feishu":
        if not user.feishu_webhook:
            return {"success": False, "error": "未配置飞书webhook"}
        success = send_feishu_notification(user.feishu_webhook, title, content)
        if success:
            create_notification(db, user_id, NotificationCreate(
                title=title,
                content=content,
                notify_type="feishu"
            ))
        return {"success": success, "error": None if success else "发送失败"}

    elif notify_type == "email":
        if not user.email:
            return {"success": False, "error": "未配置邮箱"}
        return {"success": False, "error": "邮件发送暂未配置SMTP"}

    else:
        return {"success": False, "error": "不支持的通知类型"}