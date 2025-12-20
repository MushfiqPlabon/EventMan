def email_verification_processor(request):
    """
    Context processor to check if user needs to verify their email.
    O(1) operation using existing request.user data.
    """
    if request.user.is_authenticated:
        try:
            from allauth.account.models import EmailAddress

            # Check if user has verified email (O(1) operation)
            email_addresses = EmailAddress.objects.filter(user=request.user)

            # If user has no email addresses at all (like from populate_db script),
            # they don't need verification since they have no emails to verify
            if not email_addresses.exists():
                return {"needs_email_verification": False}

            # If user has emails but none are verified, they need verification
            has_verified_email = email_addresses.filter(verified=True).exists()
            return {"needs_email_verification": not has_verified_email}
        except Exception:
            # If email verification system is unavailable, don't show message
            return {"needs_email_verification": False}
    return {"needs_email_verification": False}
