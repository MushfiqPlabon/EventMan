"""
Secure payment utilities for EventMan.
Centralized payment logic with proper security measures.
"""

import logging
from typing import Dict

from decouple import config
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from sslcommerz_lib import SSLCOMMERZ

from .models import Event, Payment

User = get_user_model()
logger = logging.getLogger(__name__)


class PaymentHandler:
    """Centralized payment handling with security measures."""

    def __init__(self):
        self.store_id = config("SSLCOMMERZ_STORE_ID")
        self.store_pass = config("SSLCOMMERZ_STORE_PASS")
        self.is_sandbox = config("SSLCOMMERZ_IS_SANDBOX", default=True, cast=bool)

        self.sslcz = SSLCOMMERZ(
            {
                "store_id": self.store_id,
                "store_pass": self.store_pass,
                "issandbox": self.is_sandbox,
            }
        )

    def create_payment_session(
        self, request: HttpRequest, event: Event, user: User
    ) -> Dict:
        """Create a secure payment session."""
        # Create payment record
        payment = Payment.objects.create(
            user=user,
            event=event,
            amount=event.ticket_price,
            status="pending",
            transaction_id=f"txn_{event.id}_{user.id}_{int(timezone.now().timestamp())}",
        )

        # Build payment data
        post_body = {
            "total_amount": str(event.ticket_price),
            "currency": "BDT",
            "tran_id": payment.transaction_id,
            "success_url": request.build_absolute_uri(reverse("payment_success")),
            "fail_url": request.build_absolute_uri(reverse("payment_fail")),
            "cancel_url": request.build_absolute_uri(reverse("payment_fail")),
            "emi_option": 0,
            "cus_name": user.get_full_name() or user.username,
            "cus_email": user.email,
            "cus_phone": (
                getattr(user.profile, "phone_number", "")
                if hasattr(user, "profile")
                else ""
            ),
            "cus_add1": "",
            "cus_city": "",
            "cus_country": "Bangladesh",
            "shipping_method": "NO",
            "multi_card_name": "",
            "num_of_item": 1,
            "product_name": event.name,
            "product_category": event.category.name if event.category else "Event",
            "product_profile": "general",
        }

        try:
            response = self.sslcz.createSession(post_body)
            if response.get("status") == "SUCCESS":
                logger.info(
                    f"Payment session created for user {user.id}, event {event.id}"
                )
                return {
                    "success": True,
                    "gateway_url": response.get("GatewayPageURL"),
                    "payment": payment,
                }
            else:
                logger.error(
                    f"Payment session failed for user {user.id}, event {event.id}: {response}"
                )
                payment.status = "failed"
                payment.save()
                return {"success": False, "error": "Failed to create payment session"}
        except Exception as e:
            logger.error(
                f"Payment session exception for user {user.id}, event {event.id}: {e}"
            )
            payment.status = "failed"
            payment.save()
            return {"success": False, "error": str(e)}

    def validate_payment(self, payment_data: Dict) -> Dict:
        """Validate payment response from SSLCommerz."""
        tran_id = payment_data.get("tran_id")
        if not tran_id:
            return {"success": False, "error": "Missing transaction ID"}

        try:
            payment = get_object_or_404(Payment, transaction_id=tran_id)

            # Validate with SSLCommerz
            if self.sslcz.validationResponse(payment_data):
                # Update payment status
                payment.status = "valid"
                payment.save()

                # Update event and add participant
                event = payment.event
                event.tickets_sold += 1
                event.participants.add(payment.user)
                event.save()

                logger.info(f"Payment validated successfully: {tran_id}")
                return {
                    "success": True,
                    "payment": payment,
                    "event": event,
                    "user": payment.user,
                }
            else:
                logger.warning(f"Payment validation failed: {tran_id}")
                payment.status = "failed"
                payment.save()
                return {"success": False, "error": "Payment validation failed"}

        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {tran_id}")
            return {"success": False, "error": "Payment record not found"}
        except Exception as e:
            logger.error(f"Payment validation exception for {tran_id}: {e}")
            return {"success": False, "error": str(e)}

    def handle_failed_payment(self, payment_data: Dict) -> Dict:
        """Handle failed payment."""
        tran_id = payment_data.get("tran_id")
        if tran_id:
            try:
                payment = get_object_or_404(Payment, transaction_id=tran_id)
                payment.status = "failed"
                payment.save()
                logger.info(f"Payment marked as failed: {tran_id}")
                return {"success": True, "payment": payment}
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for failure: {tran_id}")

        return {"success": False, "error": "Could not process failed payment"}


# Global payment handler instance
payment_handler = PaymentHandler()
