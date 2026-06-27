"""
Receipt PDF API endpoint.

Provides endpoint to download payment receipt PDF for an event.
"""

import logging
from datetime import date
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from weasyprint import HTML

from auth.auth import get_current_user
from data.receipt_service import get_receipt_data
from utils.number_to_words import number_to_words_es
from exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/receipts", tags=["receipts"])
templates = Jinja2Templates(directory="templates")


def build_receipt_context(receipt_data: dict) -> dict:
    """
    Build template context for receipt PDF.

    Args:
        receipt_data: Dictionary with receipt data from data layer.

    Returns:
        Dictionary with template variables.
    """
    today = date.today()
    total = receipt_data["event_price"]
    total_paid = receipt_data["total_paid"]
    balance = receipt_data["balance"]

    return {
        "number": receipt_data["event_id"],
        "date": {
            "city": "Cochabamba",
            "day": today.day,
            "month": today.month,
            "year": today.year,
        },
        "amount_bs": total,
        "amount_usd": None,
        "received_from": receipt_data["client_name"],
        "amount_in_words": number_to_words_es(total),
        "concept": receipt_data["event_name"],
        "event_place": receipt_data["event_place"],
        "event_date": receipt_data["event_date"],
        "concept_extra": None,
        "partial_payment": total_paid,
        "balance": balance,
        "total": total,
    }


@router.get("/{event_id}/pdf")
async def download_receipt_pdf(
    event_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Generate and return a receipt PDF for the given event.

    Permission: Event owner or admin only.
    """
    try:
        receipt_data = get_receipt_data(event_id)
        if not receipt_data:
            raise HTTPException(status_code=404, detail="Event not found")

        is_admin = current_user.get("role") == "admin"
        if receipt_data["event_user_id"] != current_user.get("id") and not is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")

        context = build_receipt_context(receipt_data)
        html_string = templates.get_template("receipt.html").render(**context)
        pdf_bytes = HTML(string=html_string).write_pdf()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="receipt-{event_id:07d}.pdf"'
            },
        )
    except HTTPException:
        raise
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Error generating receipt PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")