import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_messages():
    with open(os.path.join(BASE_DIR, "messages.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_times():
    with open(os.path.join(BASE_DIR, "times.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def make_reservations(base_hour, site, mode, tone):
    messages_data = load_messages()
    times_data = load_times()

    messages = messages_data[site][mode][tone]
    times = times_data[site][mode]

    result = []

    if mode == "normal":
        for i, time_data in enumerate(times):
            hour_offset = time_data["hour"]
            minute = time_data["minute"]

            hour = base_hour + hour_offset

            if hour < 0:
                hour += 24
            elif hour > 23:
                hour -= 24

            result.append({
                "hour": hour,
                "minute": minute,
                "message": messages[i],
            })

    elif mode in ["special", "qr"]:
        for i, time_data in enumerate(times):
            result.append({
                "after_min": time_data["after_min"],
                "message": messages[i],
            })

    return result