"""Validation and local storage for salon appointments."""

from datetime import date, datetime, time, timedelta
import json
from pathlib import Path


DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H:%M"
OPENING_TIME = time(9, 0)
CLOSING_TIME = time(18, 0)


def calculate_total(selected_services):
    """Return the total price of the selected services."""
    return sum(service["price"] for service in selected_services)


def calculate_duration(selected_services):
    """Return the combined duration of the selected services in minutes."""
    return sum(service["duration"] for service in selected_services)


def _parse_date(selected_date):
    try:
        return datetime.strptime(selected_date.strip(), DATE_FORMAT).date()
    except (AttributeError, TypeError, ValueError):
        return None


def _parse_time(selected_time):
    try:
        return datetime.strptime(selected_time.strip(), TIME_FORMAT).time()
    except (AttributeError, TypeError, ValueError):
        return None


def validate_date(selected_date, *, today=None):
    """Return whether a date is today or later and falls on a workday."""
    appointment_date = _parse_date(selected_date)
    current_date = today or date.today()

    return (
        appointment_date is not None
        and appointment_date >= current_date
        and appointment_date.weekday() < 5
    )


def validate_time(selected_time):
    """Return whether a time uses the expected HH:MM format."""
    return _parse_time(selected_time) is not None


def _appointment_interval(appointment):
    """Return an appointment's start and end, or None for an invalid record."""
    if not isinstance(appointment, dict):
        return None

    appointment_date = _parse_date(appointment.get("date"))
    start_time = _parse_time(appointment.get("time"))
    duration = appointment.get("total_duration")

    if not isinstance(duration, (int, float)) or isinstance(duration, bool):
        try:
            duration = calculate_duration(appointment.get("services", []))
        except (KeyError, TypeError):
            return None

    if appointment_date is None or start_time is None or duration <= 0:
        return None

    start = datetime.combine(appointment_date, start_time)
    return start, start + timedelta(minutes=duration)


def _appointments_overlap(first, second):
    first_interval = _appointment_interval(first)
    second_interval = _appointment_interval(second)

    if first_interval is None or second_interval is None:
        return False

    first_start, first_end = first_interval
    second_start, second_end = second_interval
    return first_start < second_end and second_start < first_end


def validate_appointment(
    selected_services,
    selected_date,
    selected_time,
    existing_appointments=None,
    *,
    now=None,
):
    """Return an explanation for invalid input, or None when it is bookable."""
    if not selected_services:
        return "Wybierz co najmniej jedną usługę."

    appointment_date = _parse_date(selected_date)
    if appointment_date is None:
        return "Podaj datę w formacie DD.MM.RRRR."

    current = now or datetime.now()
    if appointment_date < current.date():
        return "Nie można zaplanować wizyty w przeszłości."

    if appointment_date.weekday() >= 5:
        return "Salon przyjmuje wizyty od poniedziałku do piątku."

    appointment_time = _parse_time(selected_time)
    if appointment_time is None:
        return "Wybierz poprawną godzinę wizyty."

    if appointment_time < OPENING_TIME or appointment_time >= CLOSING_TIME:
        return "Godziny pracy salonu to 09:00–18:00."

    start = datetime.combine(appointment_date, appointment_time)
    if appointment_date == current.date() and start < current.replace(
        second=0, microsecond=0
    ):
        return "Nie można zaplanować wizyty na wcześniejszą godzinę dzisiaj."

    try:
        duration = calculate_duration(selected_services)
    except (KeyError, TypeError):
        return "Nie udało się odczytać wybranych usług."

    if duration <= 0:
        return "Wybrane usługi mają nieprawidłowy czas trwania."

    end = start + timedelta(minutes=duration)
    closing = datetime.combine(appointment_date, CLOSING_TIME)
    if end > closing:
        return (
            f"Wybrane usługi zakończą się o {end:%H:%M}, "
            "po zamknięciu salonu (18:00)."
        )

    candidate = {
        "date": appointment_date.strftime(DATE_FORMAT),
        "time": appointment_time.strftime(TIME_FORMAT),
        "total_duration": duration,
    }
    for appointment in existing_appointments or []:
        if _appointments_overlap(candidate, appointment):
            return "Ta godzina jest już zajęta inną wizytą. Wybierz inną."

    return None


def create_appointment(
    selected_services,
    selected_date,
    selected_time,
    existing_appointments=None,
    *,
    now=None,
):
    """Build an appointment dictionary when the date and time are available."""
    error = validate_appointment(
        selected_services,
        selected_date,
        selected_time,
        existing_appointments,
        now=now,
    )
    if error:
        return None

    return {
        "services": selected_services,
        "date": _parse_date(selected_date).strftime(DATE_FORMAT),
        "time": _parse_time(selected_time).strftime(TIME_FORMAT),
        "total_price": calculate_total(selected_services),
        "total_duration": calculate_duration(selected_services),
    }


def load_appointments(file_path=None):
    """Read saved appointments, returning an empty list when no file exists."""
    path = (
        Path(file_path)
        if file_path is not None
        else Path(__file__).resolve().parents[1] / "appointments.json"
    )

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        appointments = json.load(file)

    if not isinstance(appointments, list):
        raise ValueError("Dane wizyt muszą być zapisane jako lista.")

    return appointments


def save_appointment(appointment, file_path=None):
    """Save a valid appointment unless it overlaps an existing visit."""
    if not isinstance(appointment, dict):
        raise ValueError("Nieprawidłowe dane wizyty.")

    appointments = load_appointments(file_path)
    error = validate_appointment(
        appointment.get("services", []),
        appointment.get("date"),
        appointment.get("time"),
        appointments,
    )
    if error:
        raise ValueError(error)

    appointments.append(appointment)
    path = (
        Path(file_path)
        if file_path is not None
        else Path(__file__).resolve().parents[1] / "appointments.json"
    )
    with path.open("w", encoding="utf-8") as file:
        json.dump(appointments, file, indent=4, ensure_ascii=False)
