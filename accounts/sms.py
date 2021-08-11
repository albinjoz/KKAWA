# Download the helper library from https://www.twilio.com/docs/python/install

from kkawa import settings


def send_sms(account_sid, auth_token, body_, from_, to_):
    import twilio
    from twilio.rest import Client

    account_sid = ''
    auth_token = ''

    client = Client(settings.account_sid, settings.auth_token)

    message = client.messages \
        .create(
            body=body_,
            from_=from_,
            status_callback='http://postb.in/1234abcd',
            to=to_
        )


def generate_otp():
    import math
    import random
    digits = '0123456789'
    otp = ''
    for i in range(6):
        otp += digits[math.floor(random.random()*10)]

    return otp
