import tkinter as tk
from gui.main_window import PhishingDetectorApp

if __name__ == "__main__":
    root = tk.Tk()
    app = PhishingDetectorApp(root)
    root.mainloop()