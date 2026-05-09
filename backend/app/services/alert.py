from sqlalchemy.orm import Session
from backend.app.models import AlertRule
from backend.app.schemas.alert import AlertRuleCreate, AlertRuleUpdate
from typing import List, Optional


def get_alert_rules(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """获取用户的告警规则列表"""
    return db.query(AlertRule).filter(
        AlertRule.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_alert_rule_by_id(db: Session, rule_id: int, user_id: int):
    """获取指定告警规则"""
    return db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == user_id
    ).first()


def create_alert_rule(db: Session, user_id: int, alert_rule: AlertRuleCreate):
    """创建告警规则"""
    db_rule = AlertRule(
        user_id=user_id,
        name=alert_rule.name,
        rule_type=alert_rule.rule_type,
        condition=alert_rule.condition,
        notify_type=alert_rule.notify_type,
        is_enabled=alert_rule.is_enabled
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


def update_alert_rule(
    db: Session,
    rule_id: int,
    user_id: int,
    alert_rule: AlertRuleUpdate
):
    """更新告警规则"""
    db_rule = get_alert_rule_by_id(db, rule_id, user_id)
    if not db_rule:
        return None

    update_data = alert_rule.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rule, field, value)

    db.commit()
    db.refresh(db_rule)
    return db_rule


def delete_alert_rule(db: Session, rule_id: int, user_id: int) -> bool:
    """删除告警规则"""
    db_rule = get_alert_rule_by_id(db, rule_id, user_id)
    if not db_rule:
        return False

    db.delete(db_rule)
    db.commit()
    return True


def toggle_alert_rule(db: Session, rule_id: int, user_id: int, enabled: bool):
    """启用/禁用告警规则"""
    db_rule = get_alert_rule_by_id(db, rule_id, user_id)
    if not db_rule:
        return None

    db_rule.is_enabled = enabled
    db.commit()
    db.refresh(db_rule)
    return db_rule