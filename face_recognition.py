import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import cv2
import face_recognition
import os
from datetime import datetime

# Speak out the Output printed texts
import pyttsx3
def speak_word(word):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 175)
    engine.say(word)
    engine.runAndWait()

class CustomDialog(simpledialog.Dialog):
    def buttonbox(self):
        box = tk.Frame(self)

        ok_button = tk.Button(box, text="Search", width=20, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_button = tk.Button(box, text="Exit", width=5, command=self.cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def apply(self):
        self.result = self.user_label_entry.get()

def get_user_label():
    root = tk.Tk()
    root.withdraw()
    root.title("Culprit Identification")

    class UserLabelDialog(CustomDialog):
        def body(self, master):
            tk.Label(master, text="Enter Culprit ID:", font=("Helvetica", 14)).grid(row=1, columnspan=2, pady=10)
            self.user_label_entry = tk.Entry(master, font=("Helvetica", 14))
            self.user_label_entry.grid(row=2, column=0, columnspan=2, pady=10)

            self.geometry("400x300")
            self.resizable(0,0)

            return self.user_label_entry

    dialog = UserLabelDialog(root)
    user_label = dialog.result

    return user_label

def load_user_images(directory_path):
    user_encodings = []
    labels = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            user_image_path = os.path.join(directory_path, filename)
            user_image = face_recognition.load_image_file(user_image_path)

            face_locations = face_recognition.face_locations(user_image)

            if face_locations:
                user_encoding = face_recognition.face_encodings(user_image, face_locations)[0]
                user_encodings.append(user_encoding)
                labels.append(os.path.splitext(filename)[0])
            else:
                print(f"No face detected in '{filename}'\n")
                speak_word(f"No face detected in '{filename}'\nProcessing Data")
                print("Processing Data...")
    speak_word("Data Processing Task Completed")
    print("Data Processing Task Completed")
    return user_encodings, labels

def match_faces(user_encodings, labels, video_sources, user_images_directory):
    speak_word("Enter Culprit Identification Number")
    user_label = get_user_label().lower()
    file_path = os.path.join(user_images_directory, user_label)
    print(file_path+".jpg")

    if not os.path.exists(file_path+".jpg") and not os.path.exists(file_path+".png"):
        print("Culprit Image not available!")
        speak_word("Culprit Image not available. Update your database and try again")
        return

    speak_word(f"Realtime Search Started. Activating Camera-{video_sources} Searching: {user_label}")
    video_captures = [cv2.VideoCapture(source) for source in video_sources]

    while True:
        frames = [capture.read()[1] for capture in video_captures]

        for frame, video_source in zip(frames, video_sources):
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(user_encodings, face_encoding)
                color = (0, 0, 255)
                label = "Unknown"

                if any(matches):
                    idx = matches.index(True)
                    color = (0, 255, 0)
                    label = labels[idx]
                    if label == user_label:
                        current_datetime = datetime.now()
                        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                        if (video_source == 0):
                            camera_location = "Kundalahalli Main Road"
                        if (video_source == 1):
                            camera_location = "Second Cross, ITPL Main Road"
                        print(f"{label}: Match found on {camera_location}-Camera at {formatted_datetime}")
                        speak_word(f"{label}: Match found on {camera_location} Camera")
                        result = messagebox.askyesno(f"Match found on {camera_location}", "Do you want to proceed?")
                        if result:
                            continue
                        else:
                            speak_word("System Shutdown Protocol Activate")
                            return

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, f"{label}", (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            cv2.imshow(f'Video Source {video_source}', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            speak_word("System Shutdown Protocol Activate")
            break

    for capture in video_captures:
        capture.release()
    cv2.destroyAllWindows()

def get_user_images_directory():
    root = tk.Tk()
    root.withdraw()
    os.system('cls')
    print("\t\tCulprit Identification Demo")
    print("*"*60)
    speak_word("Choose your database directory")
    user_images_directory = filedialog.askdirectory(title="Select Directory Containing Culprit Images")
    return user_images_directory


if __name__ == "__main__":
    user_images_directory = get_user_images_directory()
    print("\nInitializing Database Directory. Please Wait...")
    speak_word("Initializing Database Directory. Please Wait...")

    if not user_images_directory:
        speak_word("Directory not selected. Exiting")
        print("Directory not selected. Exiting...")
    else:
        video_sources = [0]
        user_encodings, labels = load_user_images(user_images_directory)
        match_faces(user_encodings, labels, video_sources, user_images_directory)