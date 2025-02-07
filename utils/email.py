from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from core.config import settings

def send_otp_email(email: str, otp: str):
    message = Mail(
        from_email=settings.EMAIL_FROM,
        to_emails=email,
        subject='OTP Verification',
        plain_text_content=f'Your OTP is: {otp}'
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email: {e}")