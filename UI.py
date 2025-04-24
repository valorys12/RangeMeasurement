import tkinter as tk
from tkinter import ttk
import subprocess
import os
import random

DARK_TOSKA = "#008080"
WHITE = "#ffffff"
BLACK = "#000000"

CIRCLE_COLORS = ["#80c4b3", "#003940", "#5ca194"]

window = tk.Tk()
window.title("Distance Recognition")
window.geometry("1080x600")
window.configure(bg=WHITE)

main_frame = tk.Frame(window, bg=WHITE)
main_frame.pack(expand=True, fill="both")

canvas = tk.Canvas(main_frame, bg=WHITE, highlightthickness=0)
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

circle_data = []

# Fungsi RGB to hex dengan alpha simulasi (fade effect)
def fade_color(hex_color, alpha):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * (1 - alpha))
    g = int(g + (255 - g) * (1 - alpha))
    b = int(b + (255 - b) * (1 - alpha))
    return f'#{r:02x}{g:02x}{b:02x}'

def draw_circles(canvas, count=15):
    for _ in range(count):
        x = random.randint(0, 1080)
        y = random.randint(0, 600)
        r = random.randint(20, 80)
        dx = random.choice([-1, 1]) * random.uniform(0.2, 1.0)
        dy = random.choice([-1, 1]) * random.uniform(0.2, 1.0)
        color = random.choice(CIRCLE_COLORS)
        alpha = random.uniform(0.0, 1.0)
        fade_dir = random.choice([-1, 1])  # -1: fade out, 1: fade in
        circle = canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=fade_color(color, alpha),
            outline=fade_color(color, 0.3)
        )
        circle_data.append({
            "id": circle, "x": x, "y": y, "r": r,
            "dx": dx, "dy": dy, "color": color,
            "alpha": alpha, "fade_dir": fade_dir
        })

def animate_circles():
    for data in circle_data:
        data["x"] += data["dx"]
        data["y"] += data["dy"]
        r = data["r"]

        if data["x"] - r < 0 or data["x"] + r > 1080:
            data["dx"] *= -1
        if data["y"] - r < 0 or data["y"] + r > 600:
            data["dy"] *= -1

        # Alpha fade in/out
        data["alpha"] += 0.01 * data["fade_dir"]
        if data["alpha"] >= 1:
            data["alpha"] = 1
            data["fade_dir"] = -1
        elif data["alpha"] <= 0.1:
            data["alpha"] = 0.1
            data["fade_dir"] = 1

        color = fade_color(data["color"], data["alpha"])
        outline = fade_color(data["color"], 0.3)

        canvas.coords(data["id"], data["x"] - r, data["y"] - r, data["x"] + r, data["y"] + r)
        canvas.itemconfig(data["id"], fill=color, outline=outline)

    window.after(50, animate_circles)

draw_circles(canvas)
animate_circles()

title_label = tk.Label(
    main_frame,
    text="Distance Recognition",
    font=("Helvetica", 24, "bold"),
    fg=DARK_TOSKA,
    bg=WHITE
)
title_label.place(relx=0.5, rely=0.25, anchor="center")

def on_start():
    for widget in main_frame.winfo_children():
        if widget != canvas:
            widget.destroy()

    loading_label = tk.Label(main_frame, text="Loading...", font=("Helvetica", 16, "bold"), fg=DARK_TOSKA, bg=WHITE)
    loading_label.pack(pady=20)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("Toska.Horizontal.TProgressbar", troughcolor=WHITE, background=DARK_TOSKA, thickness=20)

    progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="indeterminate", style="Toska.Horizontal.TProgressbar")
    progress.pack(pady=10)
    progress.start()

    window.update_idletasks()

    try:
        script_path = os.path.join(os.path.dirname(__file__), "run_me.py")
        if os.name == 'nt':
            subprocess.Popen(['python', script_path], shell=True)
        window.after(15000, lambda: finish_loading(progress, loading_label))
    except Exception as e:
        progress.stop()
        loading_label.config(text=f"Error: {str(e)}\nPlease check if run_me.py exists", fg="red")
        retry_button = tk.Button(main_frame, text="Retry", command=on_start, font=("Helvetica", 12), bg="#f0f0f0", fg=BLACK)
        retry_button.pack(pady=20)

def finish_loading(progress, loading_label):
    progress.stop()
    loading_label.config(text="Process Completed!", fg=DARK_TOSKA)

    button_frame = tk.Frame(main_frame, bg=WHITE)
    button_frame.pack(pady=20)

    restart_label = tk.Label(button_frame, text="PRESS TO RERUN", font=("Helvetica", 10, "bold"), fg=DARK_TOSKA, bg=WHITE)
    restart_label.grid(row=0, column=0, padx=10)

    exit_label = tk.Label(button_frame, text="PRESS TO EXIT", font=("Helvetica", 10, "bold"), fg=DARK_TOSKA, bg=WHITE)
    exit_label.grid(row=0, column=1, padx=10)

    restart_button = tk.Button(button_frame, text="Restart", command=on_start, font=("Helvetica", 12, "bold"),
                               bg=DARK_TOSKA, fg=WHITE, width=15,
                               activebackground="#006666", activeforeground=WHITE)
    restart_button.grid(row=1, column=0, padx=10, pady=5)

    exit_button = tk.Button(button_frame, text="Exit", command=window.destroy, font=("Helvetica", 12, "bold"),
                            bg="#aa0000", fg=WHITE, width=15,
                            activebackground="#880000", activeforeground=WHITE)
    exit_button.grid(row=1, column=1, padx=10, pady=5)

start_button = tk.Button(main_frame, text="Start", command=on_start, font=("Helvetica", 16, "bold"),
                         bg=DARK_TOSKA, fg=WHITE, width=12, height=2,
                         activebackground="#006666", activeforeground=WHITE)
start_button.place(relx=0.5, rely=0.5, anchor="center")

window.mainloop()
restart_label = tk.Label(
    # button_frame,
    text="PRESS TO RERUN",
    font=("Helvetica", 10, "bold"),
    fg=DARK_TOSKA,
    bg=WHITE,              # Tetap putih
    borderwidth=0,
    highlightthickness=0
)
