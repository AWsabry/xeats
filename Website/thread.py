import threading
from django.core.mail import EmailMessage
from X_Eats import settings

class EmailThread(threading.Thread):
    def __init__(self, subject, body, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.body = body
        threading.Thread.__init__(self)

    def run(self):
        email = EmailMessage(self.subject, self.body, settings.EMAIL_HOST_USER, self.recipient_list)
        email.send()