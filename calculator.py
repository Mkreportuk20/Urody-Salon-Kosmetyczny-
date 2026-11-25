"""Inline price calculator page for the single-window application."""

import tkinter as tk

from services import SERVICES


BG = "#FFF5F7"
PINK = "#D98CA5"
PINK_ACTIVE = "#C47791"
PLUM = "#713B50"
MUTED = "#65545B"
WHITE = "#FFFFFF"
BORDER = "#EBD5DD"


class PriceCalculator:
    def __init__(self, parent):
        self.parent = parent
        self.selected_services = []
        self.view = tk.Frame(parent, bg=BG)
        self.view.pack(fill="both", expand=True)
        self.create_content()

    def create_content(self):
        tk.Label(
            self.view,
            text="Kalkulator cen",
            font=("Arial", 22, "bold"),
            bg=BG,
            fg=PLUM,
        ).pack(anchor="w", pady=(0, 4))
        tk.Label(
            self.view,
            text="Zaznacz usługi, aby obliczyć łączny koszt.",
            font=("Arial", 10),
            bg=BG,
            fg=MUTED,
        ).pack(anchor="w", pady=(0, 16))

        card = tk.Frame(
            self.view,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=18,
            pady=14,
        )
        card.pack(fill="x", pady=(0, 14))

        for service in SERVICES:
            variable = tk.BooleanVar(value=False)
            self.selected_services.append((service, variable))
            row = tk.Frame(card, bg=WHITE)
            row.pack(fill="x", pady=5)
            tk.Checkbutton(
                row,
                text=f"{service['name']}  ·  {service['duration']} min",
                variable=variable,
                command=self.update_total,
                font=("Arial", 11, "bold"),
                bg=WHITE,
                fg=PLUM,
                activebackground=WHITE,
                selectcolor=BG,
                bd=0,
                cursor="hand2",
            ).pack(side="left")
            tk.Label(
                row,
                text=f"{service['price']} PLN",
                font=("Arial", 11),
                bg=WHITE,
                fg=MUTED,
            ).pack(side="right")

        self.total_label = tk.Label(
            self.view,
            text="Łączna cena: 0 PLN",
            font=("Arial", 18, "bold"),
            bg=BG,
            fg=PLUM,
        )
        self.total_label.pack(anchor="w", pady=(5, 12))

        tk.Button(
            self.view,
            text="Wyczyść wybór",
            command=self.clear_selection,
            font=("Arial", 10, "bold"),
            bg=PINK,
            fg=WHITE,
            activebackground=PINK_ACTIVE,
            activeforeground=WHITE,
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
        ).pack(anchor="w")

    def update_total(self):
        total = sum(
            service["price"]
            for service, variable in self.selected_services
            if variable.get()
        )
        self.total_label.configure(text=f"Łączna cena: {total} PLN")

    def clear_selection(self):
        for _service, variable in self.selected_services:
            variable.set(False)
        self.update_total()


def open_calculator(parent):
    """Render the calculator inside the supplied page container."""
    return PriceCalculator(parent)
