from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services import payment_service, pdf_service

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.get("", response_model=Dict[str, Any])
def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return payment_service.get_invoices(
        db=db,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        status_filter=status_filter
    )

@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf_buffer = pdf_service.generate_invoice_pdf(db, invoice_id)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Invoice_{invoice_id}.pdf"}
    )
