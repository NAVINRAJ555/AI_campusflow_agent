import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.enums import UserRole
from app.api.deps import require_roles

router = APIRouter()

@router.get("")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.RESOURCE_MANAGER]))
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    res = []
    for l in logs:
        try:
            meta = json.loads(l.metadata_json) if l.metadata_json else {}
        except Exception:
            meta = {"raw": l.metadata_json}

        res.append({
            "id": l.id,
            "user_id": l.user_id,
            "user_name": l.user.name if l.user else "System Agent",
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "metadata": meta,
            "created_at": l.created_at
        })
    return res
