import jwt

import datetime

import requests

import time
# create a function to generate a token using the pyjwt library
def generateToken():
    token = jwt.encode(
        # Create a payload of the token containing API Key & expiration time
        {"iss": "Z8KPddIlSg-N9LTbgh5jnQ", "exp": time.time() + 5000},
        # Secret used to generate token signature
        "c18QSFhXlaHbG6gP7HI9XGhWyaM6FQTKgYfl",
        # Specify the hashing alg
        algorithm='HS256'
        # Convert token to utf-8
    )

    return token


# send a request with headers including a token
# def getUsers(): 
#     headers = {'authorization': 'Bearer %s' % generateToken(),
#                'content-type': 'application/json'}

#     r = requests.get('https://api.zoom.us/v2/users/', headers=headers)

#     print(r.text)
def create_zoom_meeting(date,start_time,duration):  

    # time_now=datetime.datetime.now()
    # expireaction_time=time_now+datetime.timedelta(seconds=20)
    # print(expireaction_time)
    # print("inside create meeting")


    # rounded_off_exp_time=round(expireaction_time.timestamp())
    # headers={"alg":"HS256","typ":"JWT"}

    # payload={"iss":"Z8KPddIlSg-N9LTbgh5jnQ","exp": rounded_off_exp_time}

    # encoded_jwt=jwt.encode(payload,"c18QSFhXlaHbG6gP7HI9XGhWyaM6FQTKgYfl", algorithm="HS256")
    # print(encoded_jwt)
    # header={"authorization":"Bearer {}".format(encoded_jwt)}
    # print(header)
    email="bookclub2022@protonmail.com"

    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}


    url ="https://api.zoom.us/v2/users/{}/meetings".format(email)
    date=str(date)+"T"+str(start_time)+":00"
    start_time=datetime.datetime.strptime(start_time, "%H:%M")

    # date=datetime.datetime(2022,7,5,13,30).strftime("%Y-%m-%dT%H:%M:%S")
    # #2019-08-24T14:15:22Z
    # print(date)
    obj={"topic":"Book Club","start_time":date,"duration":duration, "password":"1234","timezone":(time.tzname)[0]}

    create_meeting=requests.post(url, json=obj, headers=headers)
    response_data=create_meeting.json()
    global join_link, start_link
    join_link=response_data["join_url"]
    start_link=response_data["start_url"]
def get_join_link():
    # #url="https://api.zoom.us/v2/meetings/"+str(meeting_id)+"/invitation"
    # url="https://api.zoom.us/v2/meetings/82697739860/invitation"
    # obj={    "invitation": "Shrijana G is inviting you to a scheduled Zoom meeting.\r\n\r\nTopic: MyTestMeeting\r\nTime: Jul 31, 2019 04:00 PM Pacific Time (US and Canada)\r\n\r\nJoin Zoom Meeting\r\nhttps://zoom.us/j/000000\r\n\r\nOne tap mobile\r\n+000000" }
    # meeting_invitation=requests.get(url,headers=header)
    # response_data=meeting_invitation.json()
    # global invitation_text
    # invitation_text=response_data['invitation']
    return join_link
def get_start_link():
    return start_link

#screate_meeting()
# #create_meeting()
# sent_meeting_link()
# def create_message(sender, to, subject, message_text):
#   """Create a message for an email.

#   Args:
#     sender: Email address of the sender.
#     to: Email address of the receiver.
#     subject: The subject of the email message.
#     message_text: The text of the email message.

#   Returns:
#     An object containing a base64url encoded email object.
#   """
#   message = MIMEText(message_text)
#   message['to'] = to
#   message['from'] = sender
#   message['subject'] = subject
#   return {'raw': base64.urlsafe_b64encode(message.as_string())}
# create_message(email,"sofiaxia61@gmail.com",invitation_text)

# def send_message(service, user_id, message):
#   """Send an email message.

#   Args:
#     service: Authorized Gmail API service instance.
#     user_id: User's email address. The special value "me"
#     can be used to indicate the authenticated user.
#     message: Message to be sent.

#   Returns:
#     Sent Message.
#   """
#   try:
#     message = (service.users().messages().send(userId=user_id, body=message)
#                .execute())
#     print 'Message Id: %s' % message['id']
#     return message
#   except errors.HttpError, error:
#     print 'An error occurred: %s' % error
