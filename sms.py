from collections import namedtuple
from twilio.rest import TwilioRestClient
import flask
# NB:  keys.py is not committed to VC for obvious reasons :)
from keys import TWILIO_NUMBER, TWILIO_ACC_ID, TWILIO_AUTH_TOKEN, TEST_NUM1, TEST_NUM2
import weather

app = flask.Flask(__name__)

# Member info
Member = namedtuple('Member', 'name, phone_num, role')
CREW_LIST = {Member("James", TEST_NUM1, "Instructor"),
             Member("Jim", TEST_NUM2, "Student")}




def start_gliding_day():

    # Get the list of today's crew and their roles.
    # todo - currently mocked up in CREW_LIST, could grab this from the web?

    # Get today's weather information.
    message = weather.get_weather_info()

    # Send out the weather notification.
    send_mass_sms(CREW_LIST, message)


@app.route('/new_sms', methods=['POST'])
def receive_sms():
    received_message = Flask.request.form['Body']
    received_num = Flask.request.form['From']

    # Identify the sender of the message.
    sender = [person for person in CREW_LIST if person.phone_num == received_num]

    try:
        if sender.role == "Instructor":
            # If this text is from a duty instructor forward to all of today's crew.
            announcement = "Notice from " + sender.name + ":\n" + received_message
            recipients = [person for person in CREW_LIST if person != sender]
            send_mass_sms(recipients, announcement)
        else:
            # Otherwise forward it to the instructors.
            message = "Message from " + sender.name + ":\n" + received_message
            instructors = [person for person in CREW_LIST if person.role == "Instructor"]
            send_mass_sms(instructors, message)
    except:
        # todo check what error thrown
        # Most likely the sender wasn't found in the list.  Oh well...
        pass


def send_mass_sms(recipients, message):

    # Connect to Twilio and send the SMS to everyone in the list.
    client = TwilioRestClient(TWILIO_ACC_ID, TWILIO_AUTH_TOKEN)
    for person in recipients:
        message = client.messages.create(to=person.phone_num,
                                         from_=TWILIO_NUMBER,
                                         body=message)
        #todo check errors that can be thrown


@app.route("/")
def main_page():
    return flask.render_template('main_page.html')

@app.route("/about")
def about():
    return flask.render_template('about.html')

@app.route("/start_day")
def start_day():
    # Trigger business logic and go back to the main page.
    start_gliding_day()
    flask.flash("Started!")
    return flask.redirect(flask.url_for('main_page'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)