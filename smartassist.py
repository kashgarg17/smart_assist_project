import os
from gtts import gTTS
import speech_recognition as sr
import cv2
import mediapipe as mp

# -------------------- TEXT TO SPEECH --------------------
def speak(text):
    print(f"TTS: {text}")
    tts = gTTS(text=text, lang='en')
    tts.save("voice.mp3")
    os.system("start voice.mp3")  # Windows
    # Linux: xdg-open voice.mp3 | Android: termux-open voice.mp3


# -------------------- SPEECH TO TEXT --------------------
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print("STT:", text)
            return text.lower()
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected.")
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError:
            print("Could not request results from Google STT service.")
        return ""


# -------------------- SIGN LANGUAGE DETECTION --------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands()

finger_messages = {
    0: "No hand detected",
    1: "Hi 👋",
    2: "Yes 👍",
    3: "No 👎",
    4: "Stop ✋",
    5: "Thank you 🙏"
}

def count_fingers(hand_landmarks):
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4
    fingers = []

    if hand_landmarks.landmark[thumb_tip].x > hand_landmarks.landmark[thumb_tip - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

def detect_sign_language():
    cap = cv2.VideoCapture(0)
    print("✋ Showing Sign Language... (Press 'q' to exit)")

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        message = "Show a gesture"

        if result.multi_hand_landmarks:
            for hand_landmark in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmark,
                    mp_hands.HAND_CONNECTIONS
                )
                finger_count = count_fingers(hand_landmark)
                message = finger_messages.get(finger_count, "Unknown gesture")

        cv2.putText(
            frame,
            message,
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

        cv2.imshow("Sign Language to Text", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# -------------------- SIMPLE VOICE ASSISTANT --------------------
def voice_assistant():
    speak("Hello, I am your assistant. How can I help you?")
    command = listen()

    if command == "":
        speak("I didn't catch that. Could you please repeat?")
        command = listen()

    if "your name" in command:
        speak("I am a Python based assistant")
    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
    elif command != "":
        speak("Sorry, I can't do that yet.")
    else:
        speak("Still couldn't hear anything. Please check your microphone.")


# -------------------- MAIN MENU --------------------
def main():
    while True:
        print("\nSelect a Feature:")
        print("1. Text to Speech")
        print("2. Speech to Text")
        print("3. Sign Language Detection")
        print("4. Voice Assistant")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            text = input("Enter text to speak: ")
            speak(text)
        elif choice == "2":
            text = listen()
            print("You said:", text)
        elif choice == "3":
            detect_sign_language()
        elif choice == "4":
            voice_assistant()
        elif choice == "5":
            speak("Exiting. Stay safe!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
