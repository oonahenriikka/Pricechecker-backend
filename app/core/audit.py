from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import Any

def log_admin_action(
    db: Session,
    admin_id: int,
    action: str,
    target_user_id: int | None = None,
    details: dict | None = None
):
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        target_user_id=target_user_id,
        details=details or {}
    )
    db.add(log)
    db.commit()