import datetime
import time

import jwt
import requests

from faker import Faker
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


def create_zoom_meeting(date, time_start, duration):
    email = "bookclub2022@protonmail.com"

    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}
    url = "https://api.zoom.us/v2/users/{}/meetings".format(email)
    date = str(date) + "T" + str(time_start) + ":00"
    obj = {"topic": "Book Club", "start_time": date, "duration": duration, "password": "1234",
           "timezone": (time.tzname)[0]}

    create_meeting = requests.post(url, json=obj, headers=headers)
    response_data = create_meeting.json()
    global join_link, start_link
    join_link = response_data["join_url"]
    start_link = response_data["start_url"]


def get_join_link():
    return join_link


def get_start_link():
    return start_link


def delete_zoom_meeting():
    email = "bookclub2022@protonmail.com"

    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}

    url = "https://api.zoom.us/v2/users/{}/meetings".format(email)

    delete_meeting = requests.get(url, headers=headers)
    response_data = delete_meeting.json()

    while (len(response_data['meetings'])):
        email = "bookclub2022@protonmail.com"

        headers = {'authorization': 'Bearer %s' % generateToken(),
                   'content-type': 'application/json'}

        url = "https://api.zoom.us/v2/users/{}/meetings".format(email)

        delete_meeting = requests.get(url, headers=headers)
        response_data = delete_meeting.json()
        for meeting in response_data['meetings']:
            meetingId = meeting['id']
            url = "https://api.zoom.us/v2/meetings/" + str(meetingId)
            requests.delete(url, headers=headers)
