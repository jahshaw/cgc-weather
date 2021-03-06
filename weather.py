from datetime import date
import pyowm
# the secret key
from keys import OWM_API_KEY


def get_weather_info():
    """Make HTTP requests for the weather info and generate a text string with the output."""

    try:
        owm = pyowm.OWM(OWM_API_KEY)

        # Get current weather in Cambridge
        observation = owm.weather_at_place('Cambridge,uk')
        w = observation.get_weather()

        # Gather wind information
        wind_speed = int(w.get_wind()['speed'] * 1.94)  # conversion from m/s to kts
        wind_dir = int(w.get_wind()['deg'])
        wind_msg = "Wind: " + str(wind_speed) + "kt at " + str(wind_dir) + "deg\n"

        # Gather rain information
        rain = w.get_rain()
        if '3h' in rain:
            rain_vol = int(rain['3h'])  # returns rain volume in previous 3h
        else:
            rain_vol = 0
        rain_msg = "Rain: " + str(rain_vol) + "mm\n"

        # Check visibility
        vis = int(w.get_visibility_distance())
        vis_msg = "Visibility: " + str(vis) + "m\n"

        # Assess the weather
        if (wind_speed > 25
            or rain_vol > 3
            or vis < 5000):
            status = "Not flyable."
        elif (wind_speed > 15
              or vis < 8000):
            status = "Marginal - check with instructor."
        else:
            status = "Should be flyable."

        header = "CGC weather info for " + date.today().strftime("%A %d %b") + ":\n"
        message = header + wind_msg + rain_msg + vis_msg + status

    except Exception as e:
        print(repr(e))
        message = "Hit an error.  The weather is probably rubbish!"
    return message

if __name__ == "__main__":
    # Assume we are testing the weather function independently.
    print(get_weather_info())