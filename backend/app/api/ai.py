from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.booking import NaturalLanguageBookingRequest
from app.agents.request_understanding import RequestUnderstandingAgent
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/understand-request")
def understand_natural_language_request(
    req: NaturalLanguageBookingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agent = RequestUnderstandingAgent()
    context = {
        "department_name": current_user.department.name if current_user.department else None,
        "user_name": current_user.name
    }
    result = agent.process(req.prompt, context)
    return result
