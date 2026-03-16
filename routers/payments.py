import stripe, os
def _get_stripe_key():
    return os.getenv("STRIPE_SECRET_KEY")
def _get_pub_key():
    return os.getenv("STRIPE_PUBLISHABLE_KEY")
from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel
from typing import Optional
router=APIRouter(prefix="/payments",tags=["payments"])
PRICES={"athlete_annual":2500,"judge_annual":3000,"organizer_annual":9900,"team_annual":19900,"competition_local":4900,"competition_national":14900,"competition_continental":29900,"competition_world":49900,"asl_match":7900}
LABELS={"athlete_annual":"WSM Athlete Annual Membership","judge_annual":"WSM Judge Annual Membership","organizer_annual":"WSM Organizer Annual Membership","team_annual":"WSM Team Annual Membership","competition_local":"WSM Local Competition Fee","competition_national":"WSM National Competition Fee","competition_continental":"WSM Continental Competition Fee","competition_world":"WSM World/Grand Prix Competition Fee","asl_match":"WSM ASL Match Fee"}
class CheckoutRequest(BaseModel):
    product_type:str; success_url:str; cancel_url:str; metadata:Optional[dict]=None; coupon_code:Optional[str]=None
@router.get("/config")
async def get_config(): return {"publishable_key":_get_pub_key()}
@router.post("/create-checkout")
async def create_checkout(data:CheckoutRequest):
    stripe.api_key=_get_stripe_key()
    if data.product_type not in PRICES: raise HTTPException(400,"Invalid product type")
    discounts=[]
    if data.coupon_code:
        try:
            promo=stripe.PromotionCode.list(code=data.coupon_code,active=True)
            if promo.data: discounts=[{"promotion_code":promo.data[0].id}]
            else: raise HTTPException(400,"Invalid coupon")
        except stripe.StripeError as e: raise HTTPException(400,str(e))
    session=stripe.checkout.Session.create(payment_method_types=["card"],line_items=[{"price_data":{"currency":"eur","product_data":{"name":LABELS[data.product_type],"description":"World Strongman International Union"},"unit_amount":PRICES[data.product_type]},"quantity":1}],mode="payment",success_url=data.success_url,cancel_url=data.cancel_url,metadata=data.metadata or {},discounts=discounts if discounts else [],allow_promotion_codes=True)
    return {"checkout_url":session.url,"session_id":session.id}
@router.get("/verify/{session_id}")
async def verify_payment(session_id:str):
    stripe.api_key=_get_stripe_key()
    try:
        session=stripe.checkout.Session.retrieve(session_id)
        return {"paid":session.payment_status=="paid","status":session.payment_status,"metadata":session.metadata,"amount":session.amount_total}
    except stripe.StripeError as e: raise HTTPException(400,str(e))
@router.post("/webhook")
async def stripe_webhook(request:Request):
    import json
    from models.membership import Membership
    import datetime, uuid
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    if webhook_secret and sig_header:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except Exception as e:
            raise HTTPException(400, f"Webhook error: {e}")
    else:
        event = json.loads(payload)
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        email = metadata.get("email", "")
        role = metadata.get("role", "")
        
        if email and role:
            try:
                from db.database import SessionLocal
                async with SessionLocal() as db:
                    membership = Membership(
                        id=uuid.uuid4(),
                        user_id=email,
                        role=role,
                        stripe_session_id=session["id"],
                        stripe_payment_intent=session.get("payment_intent", ""),
                        amount_eur=str(session.get("amount_total", 0) / 100),
                        status="active",
                        paid_at=datetime.datetime.utcnow(),
                        expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=365),
                    )
                    db.add(membership)
                    await db.commit()
                    print(f"Membership created: {email} / {role}")
            except Exception as e:
                print(f"Membership error: {e}")
    
    return {"ok": True}
