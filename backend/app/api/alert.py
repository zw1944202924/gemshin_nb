from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.api.user import get_current_user
from backend.app import schemas
from backend.app.services import alert as alert_service

router = APIRouter()


@router.get("/", response_model=List[schemas.alert.AlertRuleResponse])
def get_alert_rules(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取告警规则列表"""
    rules = alert_service.get_alert_rules(db, int(current_user["sub"]), skip, limit)
    return rules


@router.get("/{rule_id}", response_model=schemas.alert.AlertRuleResponse)
def get_alert_rule(
    rule_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定告警规则"""
    rule = alert_service.get_alert_rule_by_id(db, rule_id, int(current_user["sub"]))
    if not rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")
    return rule


@router.post("/", response_model=schemas.alert.AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    alert_rule: schemas.alert.AlertRuleCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建告警规则"""
    rule = alert_service.create_alert_rule(
        db, int(current_user["sub"]), alert_rule
    )
    return rule


@router.put("/{rule_id}", response_model=schemas.alert.AlertRuleResponse)
def update_alert_rule(
    rule_id: int,
    alert_rule: schemas.alert.AlertRuleUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新告警规则"""
    updated_rule = alert_service.update_alert_rule(
        db, rule_id, int(current_user["sub"]), alert_rule
    )
    if not updated_rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")
    return updated_rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(
    rule_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除告警规则"""
    success = alert_service.delete_alert_rule(db, rule_id, int(current_user["sub"]))
    if not success:
        raise HTTPException(status_code=404, detail="告警规则不存在")


@router.post("/{rule_id}/toggle", response_model=schemas.alert.AlertRuleResponse)
def toggle_alert_rule(
    rule_id: int,
    enabled: bool,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """启用/禁用告警规则"""
    rule = alert_service.toggle_alert_rule(db, rule_id, int(current_user["sub"]), enabled)
    if not rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")
    return rule