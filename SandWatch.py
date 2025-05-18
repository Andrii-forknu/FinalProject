import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass


# ====== Configuration constants ======
CANVAS_W, CANVAS_H = 400, 600  # Canvas size
GLASS_MARGIN = 60  # Horizontal margin from canvas border to glass side
NECK_HEIGHT = 20  # Height of the neck opening
FALL_STREAM_WIDTH = 4  # Width of falling sand stream in pixels
TICK_MS = 30  # Animation tick in milliseconds (≈33 FPS)
PARTICLE_RADIUS = 2  # Radius of individual sand particles
MAX_PARTICLES = 120  # Upper limit to co-existing particles (performance)




@dataclass
class Particle:  # TODO: use particles somehow
    x: float
    y: float
    vy: float


class HourglassCanvas(ttk.Frame):
    def __init__(self, master: tk.Misc, *, duration_s: int = 5) -> None:
        super().__init__(master)
        self.duration_s = duration_s
        self.start_time: float | None = None
        self.elapsed = 0.0
        self.running = False
        self.top_fraction = 1.0
        self.bottom_fraction = 0.0
        self.particles: list[Particle] = []
        self.neck_width = 20  # Width of the hourglass neck

        self.canvas = tk.Canvas(self, width=CANVAS_W, height=CANVAS_H,
                                bg="#111", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3)

        self.duration_var = tk.IntVar(value=self.duration_s)
        ttk.Label(self, text="Duration (s):").grid(row=1, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.duration_var, width=5).grid(row=1, column=1)

        self.start_btn = ttk.Button(self, text="Start", command=self.start)
        self.start_btn.grid(row=1, column=2, sticky="w")
        self.stop_btn = ttk.Button(self, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.grid(row=2, column=2, sticky="w")

        self.glass_top = GLASS_MARGIN
        self.glass_bottom = CANVAS_H - GLASS_MARGIN
        self.glass_mid_y = (self.glass_top + self.glass_bottom) / 2
        self.glass_left = GLASS_MARGIN
        self.glass_right = CANVAS_W - GLASS_MARGIN

        self.glass_shape_details: dict = {}  # To store calculated glass geometry if needed
        self.after_idle(self.draw_static)
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