from flask import Flask, request, Response
from plivo import plivoxml
import plivo
import threading
import time

AUTH_ID     = "MAYMYZMWEYNMM1YTA2MW"
AUTH_TOKEN  = "ZjMwYTI5NmEtMWY2Zi00ZGZkLWEyZGUtZjM5MzZh"
PLIVO_NUM   = "+918035736861"
YOUR_NUM    = "+919620784541"
OTP         = "0312"            
ASSOCIATE   = "+912264236412"
AUDIO_URL   = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
BASE_URL    = "https://trophy-sediment-rethink.ngrok-free.dev"

app    = Flask(__name__)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)


@app.route("/answer", methods=["GET", "POST"])
def answer():
    response = plivoxml.ResponseElement()
    get_digits = plivoxml.GetDigitsElement(
        action=f"{BASE_URL}/verify_otp",
        method="POST",
        num_digits="4",
        timeout="10",
        retries="5"
    )
    get_digits.add(plivoxml.SpeakElement(
        "Welcome to InspireWorks. Please enter your 4 digit O T P to continue."
    ))
    response.add(get_digits)
    response.add(plivoxml.SpeakElement("We did not receive any input. Goodbye."))
    response.add(plivoxml.HangupElement())
    return Response(response.to_string(), mimetype="application/xml")



@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    digits = request.values.get("Digits", "")
    print(f"[OTP] Received: '{digits}' | Expected: '{OTP}'")

    response = plivoxml.ResponseElement()

    if digits == OTP:
        response.add(plivoxml.SpeakElement("O T P verified. Welcome!"))
        get_digits = plivoxml.GetDigitsElement(
            action=f"{BASE_URL}/language_menu",
            method="POST",
            num_digits="1",
            timeout="10",
            retries="3"
        )
        get_digits.add(plivoxml.SpeakElement(
            "Please select your language. Press 1 for English. Press 2 for Spanish."
        ))
        response.add(get_digits)
        response.add(plivoxml.SpeakElement("No input received. Goodbye."))
    else:
        get_digits = plivoxml.GetDigitsElement(
            action=f"{BASE_URL}/verify_otp",
            method="POST",
            num_digits="4",
            timeout="10",
            retries="5"
        )
        get_digits.add(plivoxml.SpeakElement(
            "Incorrect O T P. Please try again. Enter your 4 digit O T P."
        ))
        response.add(get_digits)
        response.add(plivoxml.SpeakElement("No input received. Goodbye."))

    response.add(plivoxml.HangupElement())
    return Response(response.to_string(), mimetype="application/xml")



@app.route("/language_menu", methods=["GET", "POST"])
def language_menu():
    digit = request.values.get("Digits", "")
    print(f"[LANGUAGE] Pressed: '{digit}'")

    response = plivoxml.ResponseElement()

    if digit not in ("1", "2"):
        get_digits = plivoxml.GetDigitsElement(
            action=f"{BASE_URL}/language_menu",
            method="POST",
            num_digits="1",
            timeout="10",
            retries="3"
        )
        get_digits.add(plivoxml.SpeakElement(
            "Invalid input. Press 1 for English. Press 2 for Spanish."
        ))
        response.add(get_digits)
        response.add(plivoxml.HangupElement())
        return Response(response.to_string(), mimetype="application/xml")

    lang = "English" if digit == "1" else "Spanish"
    response.add(plivoxml.SpeakElement(f"You selected {lang}."))
    get_digits = plivoxml.GetDigitsElement(
        action=f"{BASE_URL}/action_menu",
        method="POST",
        num_digits="1",
        timeout="10",
        retries="3"
    )
    get_digits.add(plivoxml.SpeakElement(
        "Press 1 to hear an audio message. Press 2 to connect to a live associate."
    ))
    response.add(get_digits)
    response.add(plivoxml.SpeakElement("No input received. Goodbye."))
    response.add(plivoxml.HangupElement())
    return Response(response.to_string(), mimetype="application/xml")




@app.route("/action_menu", methods=["GET", "POST"])
def action_menu():
    digit = request.values.get("Digits", "")
    print(f"[ACTION] Pressed: '{digit}'")

    response = plivoxml.ResponseElement()

    if digit == "1":
        response.add(plivoxml.SpeakElement("Playing audio message now."))
        response.add(plivoxml.PlayElement(AUDIO_URL))
        response.add(plivoxml.SpeakElement("Thank you for listening. Goodbye."))
        response.add(plivoxml.HangupElement())
    
    elif digit == "2":
        response.add(plivoxml.SpeakElement(
            "Connecting you to a live associate. Please hold."
        ))
        dial = plivoxml.DialElement(timeout=30, caller_id=PLIVO_NUM)
        dial.add(plivoxml.NumberElement(ASSOCIATE))
        response.add(dial)
        response.add(plivoxml.SpeakElement("Associate unavailable. Goodbye."))
        response.add(plivoxml.HangupElement())

    else:
        get_digits = plivoxml.GetDigitsElement(
            action=f"{BASE_URL}/action_menu",
            method="POST",
            num_digits="1",
            timeout="10",
            retries="3"
        )
        get_digits.add(plivoxml.SpeakElement(
            "Invalid input. Press 1 for audio. Press 2 for live associate."
        ))
        response.add(get_digits)
        response.add(plivoxml.HangupElement())

    return Response(response.to_string(), mimetype="application/xml")


# ── MAKE THE OUTBOUND CALL ─────────────────────────────────────
def make_call():
    time.sleep(2)
    print(f"\n[CALL] Calling {YOUR_NUM} from {PLIVO_NUM}...")
    try:
        resp = client.calls.create(
            from_=PLIVO_NUM,
            to_=YOUR_NUM,
            answer_url=f"{BASE_URL}/answer",
            answer_method="POST",
        )
        print(f"[CALL] Initiated! UUID: {resp['request_uuid']}")
    except Exception as e:
        print(f"[CALL] Error: {e}")


if __name__ == "__main__":
    BASE_URL = "https://trophy-sediment-rethink.ngrok-free.dev"
    threading.Thread(target=make_call, daemon=True).start()
    app.run(host="0.0.0.0", port=80, debug=False)
