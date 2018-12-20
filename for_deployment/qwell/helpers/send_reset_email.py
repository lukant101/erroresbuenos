"""Exports send_reset_email function."""

from flask import url_for
from flask_mail import Message
from qwell import mail
from qwell.constants import EMAIL_SENDER


def send_reset_email(student):
    token = student.get_reset_token()
    msg = Message("Password Reset",
                  sender=EMAIL_SENDER,
                  recipients=[student.email])
    msg.body = f"""To reset the password, go to:
{url_for("reset_password", token=token, _external=True)}

If you did not request a password reset, you can simply ignore this email and no changes will be made to your account.
"""
    mail.send(msg)
