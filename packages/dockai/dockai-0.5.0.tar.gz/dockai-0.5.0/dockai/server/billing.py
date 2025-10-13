import stripe, os
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(email):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer_email=email,
        line_items=[{
            "price": os.getenv("STRIPE_PRICE_ID"),
            "quantity": 1,
        }],
        mode="subscription",
        success_url=os.getenv("SUCCESS_URL"),
        cancel_url=os.getenv("CANCEL_URL"),
    )
    return session.url
