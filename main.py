import tkinter as tk
from voice_to_sign import voice_to_sign

def launch_app():
    voice_to_sign()

root = tk.Tk()
root.title("Sign Language Communication")
root.geometry("600x400")
root.configure(bg="#F5F5F5")

label = tk.Label(root, text="Sign Language Communication", font=("Helvetica", 22, "bold"), bg="#F5F5F5")
label.pack(pady=40)

btn = tk.Button(root, text="🎤 Voice to Sign", font=("Helvetica", 16), command=launch_app, bg="#2196F3", fg="white", padx=20, pady=10)
btn.pack(pady=10)

root.mainloop()
