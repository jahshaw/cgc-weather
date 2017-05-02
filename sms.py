from collections import namedtuple
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import flask
# NB:  keys.py is not committed to VC for obvious reasons :)
from keys import TWILIO_NUMBER, TWILIO_ACC_ID, TWILIO_AUTH_TOKEN, TEST_NUM1, TEST_NUM2
import weather

app = flask.Flask(__name__)
app.secret_key = TWILIO_AUTH_TOKEN

# Member info
Member = namedtuple('Member', 'name, phone_num, role')
#CREW_LIST = {Member("James", TEST_NUM1, "Instructor"),
#             Member("Jim", TEST_NUM2, "Student")}
CREW_LIST = {}


def start_gliding_day(form_data):

    # Get the list of today's crew and their roles.
    # todo - currently mocked up in CREW_LIST, could grab this from the web?
    for member in form_data.split('\n'):
        name, number, role = member.split(',', 2)
        CREW_LIST.add(Member(name, number, role))

    # Get today's weather information.
    message = weather.get_weather_info()

    # Send out the weather notification.
    send_mass_sms(CREW_LIST, message)


@app.route('/new_sms', methods=['POST'])
def receive_sms():
    received_message = flask.request.form['Body']
    received_num = flask.request.form['From']

    try:
        # Identify the sender of the message (we assume no duplicates...)
        sender = [person for person in CREW_LIST if person.phone_num == received_num][0]

        if sender.role == "Instructor":
            # If this text is from a duty instructor forward to all of today's crew.
            announcement = "Announcement from " + sender.name + ":\n" + received_message
            recipients = [person for person in CREW_LIST if person != sender]
            send_mass_sms(recipients, announcement)
            response = "Announcement delivered!"
        else:
            # Otherwise forward it to the instructors.
            message = "Message from " + sender.name + ":\n" + received_message
            instructors = [person for person in CREW_LIST if person.role == "Instructor"]
            send_mass_sms(instructors, message)
            response = "Message delivered!"
    except Exception as e:
        # Most likely the sender wasn't found in the list.  Oh well...
        print(repr(e))
        response = "Couldn't deliver message.  Are you on today's roster?"

    # Build and return the response to the message.
    rsp = MessagingResponse()
    rsp.message(to=received_num,
                from_=TWILIO_NUMBER,
                body=response)
    return str(rsp)


def send_mass_sms(recipients, message):
    # Connect to Twilio and send the SMS to everyone in the list.
    client = Client(TWILIO_ACC_ID, TWILIO_AUTH_TOKEN)
    for person in recipients:
        client.messages.create(to=person.phone_num,
                               from_=TWILIO_NUMBER,
                               body=message)
        #todo check errors that can be thrown


@app.route("/")
def main_page():
    return flask.render_template('main_page.html')


@app.route("/about")
def about():
    return flask.render_template('about.html')


@app.route("/bugs")
def bugs():
    return flask.render_template('bugs.html')


@app.route("/start_day", methods=['POST'])
def start_day():
    form_data = flask.request.form['user_data']
    # Trigger business logic and go back to the main page.
    start_gliding_day(form_data)
    flask.flash("Started!")
    return flask.redirect(flask.url_for('main_page'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)