"""Tkinter appointment planner window."""

from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk

from services import SERVICES
from modules.appointment_logic import (
    create_appointment,
    load_appointments,
    save_appointment,
    validate_appointment,
)


class AppointmentPlanner:
    def __init__(self, parent):
        self.window = parent
        self.frame = ttk.Frame(parent, padding=20)
        self.frame.pack(fill="both", expand=True)
        self.service_vars = []
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(
            self.frame,
            text="Planer wizyty",
            font=("Arial", 20, "bold"),
        ).pack(pady=(5, 10))

        ttk.Label(
            self.frame,
            text="Salon czynny od poniedziałku do piątku, 09:00–18:00.",
        ).pack(pady=(0, 12))

        ttk.Label(self.frame, text="Wybierz usługi:").pack(anchor="w")

        for service in SERVICES:
            var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                self.frame,
                text=(
                    f"{service['name']} — {service['price']} PLN — "
                    f"{service['duration']} min"
                ),
                variable=var,
                command=self._update_time_choices,
            ).pack(anchor="w", pady=4)
            self.service_vars.append((var, service))

        ttk.Label(
            self.frame,
            text="Data wizyty (DD.MM.RRRR):",
        ).pack(anchor="w", pady=(15, 5))
        self.date_entry = ttk.Entry(self.frame)
        self.date_entry.pack(fill="x")
        self.date_entry.bind("<KeyRelease>", self._update_time_choices)

        ttk.Label(self.frame, text="Godzina wizyty:").pack(
            anchor="w", pady=(15, 5)
        )
        self.time_box = ttk.Combobox(
            self.frame,
            values=(),
            state="readonly",
        )
        self.time_box.pack(fill="x")

        ttk.Button(
            self.frame,
            text="Podsumowanie wizyty",
            command=self.show_summary,
        ).pack(pady=(20, 5))
        ttk.Button(
            self.frame,
            text="Zapisz wizytę",
            command=self.save_current_appointment,
        ).pack(pady=5)

    def _selected_services(self):
        return [
            service
            for variable, service in self.service_vars
            if variable.get()
        ]

    def _update_time_choices(self, _event=None):
        selected_services = self._selected_services()
        selected_date = self.date_entry.get().strip()
        previous_time = self.time_box.get()

        try:
            existing_appointments = load_appointments()
        except (OSError, ValueError):
            self.time_box.configure(values=())
            self.time_box.set("")
            return

        available_times = []
        if selected_services and selected_date:
            for minute_of_day in range(9 * 60, 18 * 60, 30):
                hour, minute = divmod(minute_of_day, 60)
                candidate_time = f"{hour:02d}:{minute:02d}"
                if validate_appointment(
                    selected_services,
                    selected_date,
                    candidate_time,
                    existing_appointments,
                ) is None:
                    available_times.append(candidate_time)

        self.time_box.configure(values=available_times)
        if previous_time not in available_times:
            self.time_box.set("")

    def _get_current_appointment(self):
        selected_services = self._selected_services()
        selected_date = self.date_entry.get().strip()
        selected_time = self.time_box.get().strip()

        try:
            existing_appointments = load_appointments()
            error = validate_appointment(
                selected_services,
                selected_date,
                selected_time,
                existing_appointments,
            )
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Błąd danych wizyt",
                str(error),
                parent=self.window,
            )
            return None

        if error:
            messagebox.showerror(
                "Nie można zaplanować wizyty",
                error,
                parent=self.window,
            )
            return None

        return create_appointment(
            selected_services,
            selected_date,
            selected_time,
            existing_appointments,
        )

    def show_summary(self):
        appointment = self._get_current_appointment()
        if appointment is None:
            return

        service_names = "\n".join(
            f"{service['name']} — {service['price']} PLN "
            f"({service['duration']} min)"
            for service in appointment["services"]
        )
        end_time = (
            datetime.strptime(appointment["time"], "%H:%M")
            + timedelta(minutes=appointment["total_duration"])
        ).strftime("%H:%M")

        messagebox.showinfo(
            "Podsumowanie wizyty",
            f"Wybrane usługi:\n{service_names}\n\n"
            f"Data: {appointment['date']}\n"
            f"Godzina: {appointment['time']}–{end_time}\n"
            f"Cena: {appointment['total_price']} PLN\n"
            f"Czas: {appointment['total_duration']} min",
            parent=self.window,
        )

    def save_current_appointment(self):
        appointment = self._get_current_appointment()
        if appointment is None:
            return

        try:
            save_appointment(appointment)
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Nie udało się zapisać wizyty",
                str(error),
                parent=self.window,
            )
            return

        messagebox.showinfo(
            "Sukces",
            "Wizyta została zapisana!",
            parent=self.window,
        )


def open_appointment_planner(parent):
    """Open the planner in a separate window of the main application."""
    window = tk.Toplevel(parent)
    window.title("Planer wizyty — URODY")
    window.geometry("520x600")
    window.minsize(440, 520)
    window.transient(parent)
    AppointmentPlanner(window)
    return window
