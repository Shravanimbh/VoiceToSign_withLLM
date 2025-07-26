import os
import speech_recognition as sr
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from googletrans import Translator
from deep_translator import GoogleTranslator


# === CONFIGURATION ===
PHRASE_GIF_FOLDER = "ISL_Gifs"      # For "good morning.gif"
LETTER_IMG_FOLDER = "letters"       # For "A.jpg" to "Z.jpg"

# === Function to show animated GIFs ===
def show_gif(canvas, root, path):
    img = Image.open(path)
    width, height = img.size

    # Resize canvas and window to GIF size
    canvas.config(width=width, height=height)
    root.geometry(f"{width}x{height}")

    frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA')) for frame in ImageSequence.Iterator(img)]

    def animate(index):
        canvas.create_image(0, 0, anchor='nw', image=frames[index])
        canvas.image = frames[index]
        canvas.after(100, animate, (index + 1) % len(frames))

    animate(0)

# === Function to show static images ===
def show_image(canvas, path):
    img = Image.open(path).resize((400, 400))  # Adjust size if needed
    photo = ImageTk.PhotoImage(img)
    canvas.config(width=400, height=400)
    canvas.create_image(0, 0, anchor='nw', image=photo)
    canvas.image = photo

# === Function to play phrase or fallback letters ===
def play_sequence(canvas, root, text):
    from PIL import ImageDraw

    cleaned = text.strip().lower()
    phrase_path = os.path.join(PHRASE_GIF_FOLDER, f"{cleaned}.gif")

    if os.path.exists(phrase_path):
        print(f"✅ Showing full phrase: {cleaned}.gif")
        show_gif(canvas, root, phrase_path)
    else:
        print("⚠️ Phrase GIF not found. Showing letters together.")

        letters = [ch.upper() for ch in cleaned if ch.isalpha()]
        images = []

        for letter in letters:
            letter_path = os.path.join(LETTER_IMG_FOLDER, f"{letter}.jpg")
            if os.path.exists(letter_path):
                img = Image.open(letter_path).resize((100, 100))  # Resize if needed
                images.append(img)

        if not images:
            print("❌ No valid letter images found.")
            return

        # Combine all letter images horizontally
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        combined = Image.new("RGB", (total_width, max_height), (255, 255, 255))
        x_offset = 0
        for img in images:
            combined.paste(img, (x_offset, 0))
            x_offset += img.width

        combined = combined.resize((min(total_width, 800), max_height))  # Resize if too wide
        photo = ImageTk.PhotoImage(combined)
        canvas.config(width=photo.width(), height=photo.height())
        canvas.create_image(0, 0, anchor='nw', image=photo)
        canvas.image = photo

import requests


from googletrans import Translator

def translate_to_english(text):
    try:
        translator = Translator()
        translated = translator.translate(text, src='auto', dest='en')
        print(f"🌐 Translated to English: '{text}' → '{translated.text}'")
        return translated.text
    except Exception as e:
        print("❌ Translation failed:", e)
        return text


# === FUNCTION TO CALL LLM (Ollama with LLaMA) ===
def simplify_with_llm(original_text):

    import requests
    protected_phrases = ["good morning", "good night", "thank you", "i am sorry"]
    orig = original_text.strip().lower()

    if orig in protected_phrases:
        print(f"🛡️ Protected phrase detected, skipping simplification: '{orig}'")
        return orig

    prompt = (
        f"Keep the original meaning and return a phrase suitable for basic sign language translation. "
        f"Only simplify if necessary (like removing polite extras). Do NOT shorten important words. "
        f"Respond with just the core phrase in double quotes.\n\n"
        f"Input: {original_text}\n"
        f"Output:"
    )

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        print("📡 Sending to LLM...")
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        print(f"📨 Raw LLM response: {response.text}")
        response.raise_for_status()
        text = response.json()["response"].strip().lower()

        import re
        match = re.search(r'"([^"]+)"', text)
        if match:
            simplified = match.group(1)
        else:
            simplified = text.split("\n")[0]

        print(f"🧠 LLM simplified: '{original_text}' → '{simplified}'")
        return simplified
    except Exception as e:
        print(f"❌ LLM request failed: {e}")
        return orig


# === Speech to text and display ===
def voice_to_sign():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return

    # 🌐 Translate to English before LLM
    translated_text = translate_to_english(text)

    # 🔁 Simplify the translated text with LLM
    simplified_text = simplify_with_llm(translated_text)

    root = tk.Toplevel()
    root.title("Sign Language Display")
    canvas = tk.Canvas(root)
    canvas.pack()

    # 🔁 Use simplified text for sign language GIF/letters
    play_sequence(canvas, root, simplified_text)
    root.mainloop()

# === MAIN WINDOW TO TRIGGER VOICE ===
if __name__ == "__main__":
    app = tk.Tk()
    app.title("Voice to Sign")
    button = tk.Button(app, text="Speak", command=voice_to_sign, font=("Arial", 20))
    button.pack(pady=30)
    app.mainloop()
