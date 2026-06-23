"""
Contract PDF API endpoint.

Provides endpoint to generate service contract PDF for an event.
"""

import logging
from datetime import date
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from weasyprint import HTML
from pydantic import BaseModel

from auth.auth import get_current_user
from models.user import User
from data.contract_service import get_contract_data
from utils.number_to_words import number_to_words_es
from exceptions import DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contracts", tags=["contracts"])
templates = Jinja2Templates(directory="templates")

MONTH_NAMES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


class ContractRequest(BaseModel):
    client_name: str
    client_id: str
    client_phone: str
    company_name: str
    event_name: str
    event_location: str
    event_start_datetime: str
    event_end_datetime: str
    total_amount: float
    deposit_percent: int


def build_contract_context(contract_request: ContractRequest) -> dict:
    """
    Build template context for contract PDF.

    Args:
        contract_request: Contract request data.

    Returns:
        Dictionary with template variables.
    """
    today = date.today()
    deposit = round(contract_request.total_amount * contract_request.deposit_percent / 100, 2)
    balance = round(contract_request.total_amount - deposit, 2)

    start_dt = contract_request.event_start_datetime
    end_dt = contract_request.event_end_datetime

    return {
        "contract_id": 1,
        "client_name": contract_request.client_name,
        "client_id": contract_request.client_id,
        "client_phone": contract_request.client_phone,
        "company_name": contract_request.company_name,
        "contract_date": {
            "day": today.day,
            "month": today.month,
            "month_name": MONTH_NAMES_ES[today.month],
            "year": today.year,
        },
        "event": {
            "name": contract_request.event_name,
            "location": contract_request.event_location,
            "date": start_dt.split("T")[0] if "T" in start_dt else start_dt,
            "start_time": start_dt.split("T")[1][:5] if "T" in start_dt else start_dt,
            "end_time": end_dt.split("T")[1][:5] if "T" in end_dt else end_dt,
        },
        "payment": {
            "total": contract_request.total_amount,
            "total_in_words": number_to_words_es(contract_request.total_amount),
            "deposit_percent": contract_request.deposit_percent,
            "deposit": deposit,
            "balance": balance,
        },
    }


@router.post("/{event_id}/pdf")
async def download_contract_pdf(
    event_id: int,
    contract_request: ContractRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Generate and return a service contract PDF for the given event.

    Permission: Event owner or admin only.
    """
    try:
        contract_data = get_contract_data(event_id)
        if not contract_data:
            raise HTTPException(status_code=404, detail="Event not found")

        if contract_data["event_user_id"] != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")

        context = build_contract_context(contract_request)
        html_string = templates.get_template("contract.html").render(**context)
        pdf_bytes = HTML(string=html_string, base_url=".").write_pdf()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="contract-{event_id:06d}.pdf"'
            },
        )
    except HTTPException:
        raise
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Error generating contract PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")