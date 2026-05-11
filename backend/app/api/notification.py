from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.core.database import get_db
from backend.app.api.user import get_current_user
from backend.app import schemas
from backend.app.services import notification as notification_service

router = APIRouter()


@router.get("/", response_model=List[schemas.notification.NotificationResponse])
def get_notifications(
    skip: int = 0,
    limit: int = 100,
    is_read: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取通知列表"""
    notifications = notification_service.get_notifications(
        db, int(current_user["sub"]), skip, limit, is_read
    )
    return notifications


@router.get("/{notification_id}", response_model=schemas.notification.NotificationResponse)
def get_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定通知"""
    notification = notification_service.get_notification_by_id(
        db, notification_id, int(current_user["sub"])
    )
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    return notification


@router.post("/", response_model=schemas.notification.NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification: schemas.notification.NotificationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建通知记录"""
    result = notification_service.create_notification(
        db, int(current_user["sub"]), notification
    )
    return result


@router.post("/{notification_id}/read", response_model=schemas.notification.NotificationResponse)
def mark_notification_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记通知为已读"""
    notification = notification_service.mark_as_read(
        db, notification_id, int(current_user["sub"])
    )
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除通知"""
    success = notification_service.delete_notification(
        db, notification_id, int(current_user["sub"])
    )
    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")


@router.put("/config", status_code=status.HTTP_200_OK)
def update_notify_config(
    config: schemas.notification.UserNotifyConfig,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新通知配置"""
    user = notification_service.update_user_notify_config(
        db, int(current_user["sub"]), config
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"code": 0, "message": "配置更新成功"}


@router.post("/send", status_code=status.HTTP_200_OK)
def send_notification(
    request: schemas.notification.NotifySendRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送通知"""
    result = notification_service.send_notification(
        db, int(current_user["sub"]),
        request.notify_type,
        request.title,
        request.content
    )
    if result["success"]:
        return {"code": 0, "message": "发送成功"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])