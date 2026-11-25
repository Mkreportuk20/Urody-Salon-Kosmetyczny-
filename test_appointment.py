"""Manual smoke scenario for creating an appointment without saving it."""

from datetime import date, timedelta

from services import SERVICES
from modules.appointment_logic import (
    calculate_duration,
    calculate_total,
    create_appointment,
)


def next_workday(start_date):
    while start_date.weekday() >= 5:
        start_date += timedelta(days=1)
    return start_date


def main():
    selected_services = [SERVICES[0], SERVICES[1]]
    appointment_day = next_workday(date.today() + timedelta(days=1))
    selected_date = appointment_day.strftime("%d.%m.%Y")

    print("Total price:", calculate_total(selected_services), "PLN")
    print("Total duration:", calculate_duration(selected_services), "minutes")

    appointment = create_appointment(
        selected_services,
        selected_date,
        "14:00",
    )

    print("Appointment:", appointment)
    if appointment:
        print("Appointment scenario is valid.")
    else:
        print("Appointment scenario is invalid.")


if __name__ == "__main__":
    main()
