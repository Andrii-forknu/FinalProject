import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from time import perf_counter


# ====== Configuration constants ======
CANVAS_W, CANVAS_H = 400, 600  # Canvas size
GLASS_MARGIN = 60              # Horizontal margin from canvas border to glass side
NECK_HEIGHT = 20               # Height of the neck opening
FALL_STREAM_WIDTH = 4          # Width of falling sand stream in pixels
TICK_MS = 30                   # Animation tick in milliseconds (≈33 FPS)
PARTICLE_RADIUS = 2            # Radius of individual sand particles
MAX_PARTICLES = 120            # Upper limit to co-existing particles (performance)


# ====== Helper dataclass ======
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
        
        self.glass_shape_details: dict = {} # To store calculated glass geometry if needed
        self.after_idle(self.draw_static)

    def start(self) -> None:
        if self.running:
            return

        self.duration_s = max(1, self.duration_var.get())

        self.start_time = perf_counter() - self.elapsed

        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.animate()

    def stop(self) -> None:
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def animate(self) -> None:
        if not self.running:
            return
        now = perf_counter()
        
        if self.start_time is None: # Should be set by start(), but as a fallback
            self.start_time = now 
        self.elapsed = now - self.start_time
        progress = min(1.0, self.elapsed / self.duration_s)
        
        self.top_fraction = 1.0 - progress
        self.bottom_fraction = progress

        if progress >= 1.0:
            self.running = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
        else:
            self.after(TICK_MS, self.animate)

        self.redraw()

    def draw_static(self) -> None:
        c = self.canvas
        c.delete("static")

        c.create_rectangle(self.glass_left - 20, self.glass_bottom,
                           self.glass_left + 20, self.glass_bottom + 40,
                           fill="#444", tags="static")
        c.create_rectangle(self.glass_right - 20, self.glass_bottom,
                           self.glass_right + 20, self.glass_bottom + 40,
                           fill="#444", tags="static")
        c.create_rectangle(self.glass_left - 20, self.glass_top - 40,
                           self.glass_right + 20, self.glass_top - 20,
                           fill="#666", tags="static")

        neck_top_y = self.glass_mid_y - NECK_HEIGHT / 2
        neck_bottom_y = self.glass_mid_y + NECK_HEIGHT / 2

        left_path = [
            (self.glass_left, self.glass_top),
            (CANVAS_W / 2 - self.neck_width / 2, neck_top_y),
            (CANVAS_W / 2 - self.neck_width / 2, neck_bottom_y),
            (self.glass_left, self.glass_bottom)
        ]
        right_path = [
            (self.glass_right, self.glass_bottom),
            (CANVAS_W / 2 + self.neck_width / 2, neck_bottom_y),
            (CANVAS_W / 2 + self.neck_width / 2, neck_top_y),
            (self.glass_right, self.glass_top)
        ]
        glass_path = left_path + right_path
        c.create_polygon(*glass_path,
                         outline="#AAA", width=2, fill="", tags="static")
        
        # Store key geometry points for _get_glass_width_at_y
        self.glass_shape_details = {
            'neck_top_y': neck_top_y,
            'neck_bottom_y': neck_bottom_y,
            # Points for interpolation: (x, y)
            'top_chamber_left_p1': (self.glass_left, self.glass_top),
            'top_chamber_left_p2': (CANVAS_W / 2 - self.neck_width / 2, neck_top_y),
            'bottom_chamber_left_p1': (CANVAS_W / 2 - self.neck_width / 2, neck_bottom_y),
            'bottom_chamber_left_p2': (self.glass_left, self.glass_bottom),
        }

    def _get_glass_width_at_y(self, y_coord: float) -> float:
        details = self.glass_shape_details
        if not details:
            if self.glass_top <= y_coord <= self.glass_bottom:
                 return self.glass_right - self.glass_left # Max width as a rough estimate
            return 0.0

        neck_top_y = details['neck_top_y']
        neck_bottom_y = details['neck_bottom_y']

        if not (self.glass_top <= y_coord <= self.glass_bottom):
            return 0.0

        current_x_left = 0.0
        if y_coord < neck_top_y:  # Top chamber
            p1_x, p1_y = details['top_chamber_left_p1']
            p2_x, p2_y = details['top_chamber_left_p2']
            if abs(p2_y - p1_y) < 1e-6: # Horizontal segment (e.g. flat top of glass)
                current_x_left = p1_x
            else:
                t = (y_coord - p1_y) / (p2_y - p1_y)
                current_x_left = p1_x + t * (p2_x - p1_x)
        elif y_coord <= neck_bottom_y:  # Neck region
            return self.neck_width
        else:  # Bottom chamber
            p1_x, p1_y = details['bottom_chamber_left_p1']
            p2_x, p2_y = details['bottom_chamber_left_p2']
            if abs(p2_y - p1_y) < 1e-6: # Horizontal segment
                current_x_left = p1_x
            else:
                t = (y_coord - p1_y) / (p2_y - p1_y)
                current_x_left = p1_x + t * (p2_x - p1_x)
        
        current_x_right = CANVAS_W - current_x_left # Assumes symmetry
        return max(0.0, current_x_right - current_x_left)

    def redraw(self) -> None:
        c = self.canvas
        c.delete("dynamic")
        self.draw_sand_top()
        self.draw_sand_bottom()
        self.draw_falling()

    def top_fraction_height(self) -> float:
        max_h = (self.glass_mid_y - NECK_HEIGHT) - self.glass_top
        # Ensure max_h is not negative if geometry is unusual
        return max(0.0, max_h * self.top_fraction)

    def bottom_fraction_height(self) -> float:
        max_h = self.glass_bottom - (self.glass_mid_y + NECK_HEIGHT)
        return max(0.0, max_h * self.bottom_fraction)

    def draw_sand_top(self) -> None:
        h = self.top_fraction_height() # Current height of sand mass
        if h <= 1e-3: # Effectively no sand, or height is negligible
            return
        c = self.canvas

        y_sand_cone_tip = self.glass_mid_y - NECK_HEIGHT 
        
        y_sand_surface = y_sand_cone_tip - h

        sand_width_at_surface = self._get_glass_width_at_y(y_sand_surface)
        if sand_width_at_surface <= 1e-3: # Effectively no width (e.g. surface is outside glass or at a point)
            return

        # Polygon points: (tip_x, tip_y), (surface_left_x, surface_y), (surface_right_x, surface_y)
        c.create_polygon(
            CANVAS_W / 2, y_sand_cone_tip,  # Lower vertex (tip)
            CANVAS_W / 2 - sand_width_at_surface / 2, y_sand_surface, # Upper-left of base
            CANVAS_W / 2 + sand_width_at_surface / 2, y_sand_surface, # Upper-right of base
            fill="#F5DEB3", outline="", tags="dynamic"
        )

    def draw_sand_bottom(self) -> None:
        h = self.bottom_fraction_height()
        if h <= 1e-3: # Effectively no sand pile
            return
        c = self.canvas
        
        y_pile_base = self.glass_bottom
        y_pile_tip = y_pile_base - h
        
        # Clamp tip to be within defined bottom chamber and not below (mid_y + NECK_HEIGHT)
        y_pile_tip = max(self.glass_mid_y + NECK_HEIGHT, min(y_pile_base, y_pile_tip)) 

        if y_pile_tip >= y_pile_base - 1e-3: # Effectively no pile height
            return

        max_glass_width_at_bottom = self.glass_right - self.glass_left
        
        # Denominator for grow_factor: effective max height of the pile
        pile_max_h_denominator = self.glass_bottom - (self.glass_mid_y + NECK_HEIGHT)
        if pile_max_h_denominator <= 1e-6: 
            grow_factor = 1.0 # Max width if no effective height for pile
        else: 
            grow_factor = h / pile_max_h_denominator
        grow_factor = min(1.0, max(0.0, grow_factor)) # Clamp grow_factor
        
        current_pile_base_width = max_glass_width_at_bottom * (0.4 + grow_factor * 0.6)
        # Ensure the calculated width does not exceed the actual glass width at the base
        current_pile_base_width = min(current_pile_base_width, self._get_glass_width_at_y(y_pile_base))

        if current_pile_base_width <= 1e-3:
            return

        c.create_polygon(
            CANVAS_W / 2, y_pile_tip,
            CANVAS_W / 2 - current_pile_base_width / 2, y_pile_base,
            CANVAS_W / 2 + current_pile_base_width / 2, y_pile_base,
            fill="#F5DEB3", outline="", tags="dynamic"
        )

    def draw_falling(self) -> None:
        c = self.canvas
        if self.running:
            # Stream of sand in the neck
            c.create_line(CANVAS_W / 2, self.glass_mid_y - NECK_HEIGHT / 2,
                          CANVAS_W / 2, self.glass_mid_y + NECK_HEIGHT / 2,
                          fill="#F5DEB3", width=FALL_STREAM_WIDTH, tags="dynamic")

class HourglassApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Animated Hourglass")
        self.resizable(False, False)

        style = ttk.Style(self)
        try:
            # Attempt to use a modern theme if available (e.g., azure.tcl)
            self.tk.call("source", "azure.tcl") 
            style.theme_use("azure")
        except tk.TclError:
            style.theme_use("clam") 

        HourglassCanvas(self).pack(padx=10, pady=10)


if __name__ == "__main__":
    HourglassApp().mainloop()   