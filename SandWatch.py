import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass


CANVAS_W, CANVAS_H = 400, 600
TICK_MS = 30
PARTICLE_RADIUS = 2
MAX_PARTICLES = 120


@dataclass
class Particle:  # TODO: use particles somehow
    x: float
    y: float
    vy: float


class HourglassCanvas(ttk.Frame):
    def __init__(self, master: tk.Misc, *, duration_s: int = 5) -> None:
        super().__init__(master)
        self.duration_s = duration_s
        ...

    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...

class HourglassApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Animated Hourglass")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.theme_use("clam") 

        HourglassCanvas(self).pack(padx=10, pady=10)


if __name__ == "__main__":
    HourglassApp().mainloop()   