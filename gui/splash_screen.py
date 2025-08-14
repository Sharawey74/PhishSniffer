import tkinter as tk
import ttkbootstrap as ttk
import time
import threading
import traceback
from model.training import train_custom_model

def simulate_loading(app):
    """Simulate loading progress with animation"""

    def update_progress():
        try:
            for i in range(101):
                time.sleep(0.02)  # Faster loading for demo
                app.progress["value"] = i

                # Train custom model at 50%
                if i == 50:
                    train_custom_model(app)

                # Update splash screen
                if i == 100:
                    time.sleep(0.5)  # Pause at 100%
                    if app.splash.winfo_exists():
                        app.splash.destroy()
                    app.root.deiconify()  # Show main window
                    app.setup_main_ui()  # Setup main UI components
        except Exception as e:
            print(f"Error in loading: {e}")
            traceback.print_exc()
            # Ensure we show the main window even if there's an error
            if hasattr(app, 'splash') and app.splash.winfo_exists():
                app.splash.destroy()
            app.root.deiconify()
            app.setup_main_ui()

    # Start progress in a separate thread to keep UI responsive
    threading.Thread(target=update_progress, daemon=True).start()

def show_splash(app):
    """Display welcome splash screen with animation"""
    # Create splash window
    app.splash = tk.Toplevel(app.root)
    app.splash.title("")
    app.splash.geometry("600x400")
    app.splash.overrideredirect(True)  # No window decorations
    app.splash.configure(bg="#1a1a1a")

    # Center the splash screen
    screen_width = app.splash.winfo_screenwidth()
    screen_height = app.splash.winfo_screenheight()
    x = (screen_width - 600) // 2
    y = (screen_height - 400) // 2
    app.splash.geometry(f"600x400+{x}+{y}")

    # Create a canvas for animations
    canvas = tk.Canvas(app.splash, bg="#1a1a1a", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Logo/icon
    logo_frame = ttk.Frame(canvas, bootstyle="dark")
    logo_frame.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

    shield_icon = ttk.Label(
        logo_frame,
        text="🛡️",
        font=("Segoe UI", 60),
        bootstyle="light"
    )
    shield_icon.pack(anchor=tk.CENTER)

    # App name
    title_label = ttk.Label(
        canvas,
        text="PHISHING DETECTOR",
        font=("Segoe UI", 24, "bold"),
        bootstyle="light"
    )
    title_label.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

    # Tagline
    tagline_label = ttk.Label(
        canvas,
        text="Advanced email security with machine learning",
        font=("Segoe UI", 12),
        bootstyle="secondary"
    )
    tagline_label.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

    # Progress bar
    app.progress = ttk.Progressbar(
        canvas,
        length=400,
        mode="determinate",
        bootstyle="success-striped"
    )
    app.progress.place(relx=0.5, rely=0.8, anchor=tk.CENTER, width=400)

    # Version and copyright
    version_label = ttk.Label(
        canvas,
        text=f"v1.0.0 • {app.current_datetime}",
        font=("Segoe UI", 8),
        bootstyle="secondary"
    )
    version_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    # Start loading animation
    simulate_loading(app)

