import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = 'AC25e320ea3dd95c4065f604ef66e461e1'
auth_token = 'b6b5d3a1af6d1d6d51f304288129f791'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                    body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                    from_='+14454466665',
                    to='+201008568308'
                )

print(message.sid)