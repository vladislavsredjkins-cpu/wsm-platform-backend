import stripe
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from pydantic import BaseModel
from typing import Optional

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

router = APIRouter(prefix="/payments", tags=["payments"])

# Тарифы
PRICES = {
    "athlete_annual": 2500,      # €25.00
    "judge_annual": 3000,        # €30.00
    "organizer_annual": 9900,    # €99.00
    "team_annual": 19900,        # €199.00
    "competition_local": 4900,   # €49.00
    "competition_national": 14900, # €149.00
    "competition_continental": 29900, # €299.00
    "competition_world": 49900,  # €499.00
    "asl_match": 7900,           # €79.00
}

LABELS = {
    "athlete_annual": "WSM Athlete Annual Membership",
    "judge_annual": "WSM Judge Annual Membership",
    "organizer_annual": "WSM Organizer Annual Membership",
    "team_annual": "WSM Team Annual Membership",
    "competition_local": "WSM Local Competition Fee",
    "competition_national": "WSM National Competition Fee",
    "competition_continental": "WSM Continental Competition Fee",
    "competition_world": "WSM World/Grand Prix Competition Fee",
    "asl_match": "WSM ASL Match Fee",
}

class CheckoutRequest(BaseModel):
    product_type: str
    success_url: str
    cancel_url: str
    metadata: Optional[dict] = None
    coupon_code: Optional[str] = None

@router.get("/config")
async def get_config():
    return {"publishable_key": PUBLISHABLE_KEY}

@router.post("/create-checkout")
async def create_checkout(data: CheckoutRequest):
    if data.product_type not in PRICES:
        raise HTTPException(400, "Invalid product type")
    
    # Проверяем купон если есть
    discounts = []
    if data.coupon_code:
        try:
            promo = stripe.PromotionCode.list(code=data.coupon_code, active=True)
            if promo.data:
                discounts = [{"promotion_code": promo.data[0].id}]
            else:
                raise HTTPException(400, "Invalid or expired coupon code")
        except stripe.error.StripeError as e:
            raise HTTPException(400, str(e))
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": LABELS[data.product_type],
                    "description": "World Strongman International Union",
                },
                "unit_amount": PRICES[data.product_type],
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=data.success_url,
        cancel_url=data.cancel_url,
        metadata=data.metadata or {},
        discounts=discounts if discounts else [],
    )
    
    return {"checkout_url": session.url, "session_id": session.id}

@router.get("/verify/{session_id}")
async def verify_payment(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "paid": session.payment_status == "paid",
            "status": session.payment_status,
            "metadata": session.metadata,
            "amount": session.amount_total,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(400, str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    if webhook_secret:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except Exception:
            raise HTTPException(400, "Invalid webhook")
    else:
        import json
        event = json.loads(payload)
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        # TODO: активировать membership после оплаты
        print(f"Payment completed: {session['id']} metadata={metadata}")
    
    return {"ok": True}
