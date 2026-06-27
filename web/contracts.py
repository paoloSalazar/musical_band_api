"""
Contract PDF API endpoint.

Provides endpoint to generate service contract PDF for an event.
"""

import logging
import os
from datetime import date
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from weasyprint import HTML
from dotenv import load_dotenv

from auth.auth import get_current_user
from data.contract_service import get_contract_data
from utils.number_to_words import number_to_words_es
from exceptions import DatabaseError

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contracts", tags=["contracts"])
templates = Jinja2Templates(directory="templates")

MONTH_NAMES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


def build_contract_context(contract_data: dict) -> dict:
    """
    Build template context for contract PDF.

    Args:
        contract_data: Contract data from data layer.

    Returns:
        Dictionary with template variables.
    """
    today = date.today()
    deposit_percent = 30
    deposit = round(contract_data["event_price"] * deposit_percent / 100, 2)
    balance = round(contract_data["event_price"] - deposit, 2)

    return {
        "contract_id": 1,
        "client_name": contract_data["client_name"],
        "client_id": contract_data["client_ci"],
        "client_phone": contract_data["client_phone"],
        "company_name": os.getenv("GROUP_NAME", "Musical Band"),
        "contract_date": {
            "day": today.day,
            "month": today.month,
            "month_name": MONTH_NAMES_ES[today.month],
            "year": today.year,
        },
        "event": {
            "name": contract_data["event_name"],
            "location": contract_data["event_location"],
            "duration": contract_data.get("event_duration", "6 Horas"),
        },
        "event_date": {
            "day": contract_data["event_start_datetime"].day,
            "month": contract_data["event_start_datetime"].month,
            "month_name": MONTH_NAMES_ES[contract_data["event_start_datetime"].month],
            "year": contract_data["event_start_datetime"].year,
        },
        "payment": {
            "total": contract_data["event_price"],
            "total_in_words": number_to_words_es(contract_data["event_price"]),
            "deposit_percent": deposit_percent,
            "deposit": deposit,
            "balance": balance,
        },
    }


@router.get("/{event_id}/pdf")
async def download_contract_pdf(
    event_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Generate and return a service contract PDF for the given event.

    Permission: Event owner or admin only.
    """
    try:
        contract_data = get_contract_data(event_id)
        if not contract_data:
            raise HTTPException(status_code=404, detail="Event not found")

        is_admin = current_user.get("role") == "admin"
        if contract_data["event_user_id"] != current_user.get("id") and not is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")

        context = build_contract_context(contract_data)
        html_string = templates.get_template("contract.html").render(**context)
        pdf_bytes = HTML(string=html_string).write_pdf()

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