import tkinter as tk
import subprocess
import os

def on_start():
    # Hapus semua widget di main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    # Tampilkan loading di frame yang sama
    loading_label = tk.Label(
        main_frame,
        text="Loading...",
        font=("Helvetica", 16, "bold"),
        fg="black"
    )
    loading_label.pack(expand=True, pady=50)
    
    # Paksa update GUI agar loading terlihat
    window.update_idletasks()  
    
    # Path ke Python interpreter di venv (Windows)
    python_path = os.path.join("..", ".venv", "Scripts", "python.exe")
    
    try:
        # Jalankan run_me.py
        subprocess.Popen([python_path, 'run_me.py'])
    except Exception as e:
        loading_label.config(text=f"Error: {str(e)}", fg="red")
        return
    
    # Tutup window setelah 500ms (agar loading sempat terlihat)
    window.after(15000, window.destroy)

# Buat window utama
window = tk.Tk()
window.title("Contoh Tkinter")
window.geometry("1080x600")

main_frame = tk.Frame(window, padx=20, pady=100)
main_frame.pack(expand=True, fill="both")

# Judul
title_label = tk.Label(
    main_frame,
    text="Aplikasi",
    font=("Montserrat", 20, "bold"),
    fg="black"
)
title_label.pack(pady=(20, 10))

# Tombol Start
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

# Jalankan aplikasi
window.mainloop()