import tkinter as tk
import subprocess
import os

def on_start():
    for widget in main_frame.winfo_children():
        widget.destroy()

    loading_label = tk.Label(
        main_frame,
        text="Loading...",
        font=("Helvetica", 16, "bold"),
        fg="black"
    )
    loading_label.pack(expand=True, pady=50)
    window.update_idletasks()

    try:
        script_path = os.path.join(os.path.dirname(__file__), "run_me.py")

        if os.name == 'nt':
            subprocess.Popen(['python', script_path], shell=True)

        window.after(15000, window.destroy)

    except Exception as e:
        loading_label.config(text=f"Error: {str(e)}\nPlease check if run_me.py exists", fg="red")
        retry_button = tk.Button(
            main_frame,
            text="Retry",
            command=on_start,
            font=("Helvetica", 12),
            bg="lightgray"
        )
        retry_button.pack(pady=20)

window = tk.Tk()
window.title("Contoh Tkinter")
window.geometry("1080x600")

main_frame = tk.Frame(window, padx=20, pady=100)
main_frame.pack(expand=True, fill="both")

title_label = tk.Label(
    main_frame,
    text="Distance Recognition",
    font=("Montserrat", 20, "bold"),
    fg="black"
)
title_label.pack(pady=(20, 10))

start_button = tk.Button(
    main_frame,
    text="Start",
    command=on_start,
    font=("Helvetica", 16, "bold"),
    bg="maroon",
    fg="white",
    width=10,
    height=2
)
start_button.pack(expand=True)

window.mainloop() 