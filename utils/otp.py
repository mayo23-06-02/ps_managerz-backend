import random
import string
import time

otp_store = {}

def generate_otp(email: str):
    otp = ''.join(random.choices(string.digits, k=6))
    otp_store[email] = {'otp': otp, 'timestamp': time.time()}
    return otp

def verify_otp(email: str, otp: str):
    if email in otp_store and otp_store[email]['otp'] == otp:
        # Check if OTP is expired (valid for 5 minutes)
        if time.time() - otp_store[email]['timestamp'] < 300:
            del otp_store[email]
            return True
    return False