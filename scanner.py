import cv2
import pyautogui
import sounddevice as sd
import soundfile as sf
import tkinter as tk
import os
# import threading
from pyzbar import pyzbar
from PIL import Image, ImageTk

class BarcodeReaderGUI:
    def __init__(self, master):

        # Get a list of available webcams
        self.webcam_list = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.webcam_list.append("Webcam " + str(i))
            cap.release()

        # Create a tkinter button to select the webcam
        self.webcam_button = tk.Button(
            master, text="Apply", command=self.select_webcam)
        self.webcam_button.pack(side=tk.BOTTOM)

        # Create a tkinter menu to select the webcam
        self.webcam_var = tk.StringVar(value=self.webcam_list[0])
        self.webcam_menu = tk.OptionMenu(
            master, self.webcam_var, *self.webcam_list)
        self.webcam_menu.pack(side=tk.BOTTOM)

        # Create a tkinter label to display the barcode data
        self.barcode_label = tk.Label(
            master, text="Data Barcode akan muncul disini")
        self.barcode_label.pack(side=tk.TOP)

        # Get the index of the selected webcam
        self.webcam_idx = int(self.webcam_var.get().split()[-1])

        # Create a video capture object for the selected webcam
        self.cap = cv2.VideoCapture(self.webcam_idx)

        # Get the resolution of the webcam
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        height += 75

        # Create a tkinter canvas to display the video stream
        master.geometry('{}x{}'.format(width, height))
        self.canvas = tk.Canvas(master, width=width, height=height)
        self.canvas.pack(side=tk.TOP)

        # Start the main loop to update the GUI
        self.update_gui()

    def update_gui(self):
        # Read the next frame
        ret, frame = self.cap.read()

        # Apply brightness adjustment to the frame
        brightness = 0
        frame = cv2.add(frame, brightness)

        # Apply square focus on the middle of the frame
        height, width, _ = frame.shape
        margin = min(height, width) // 4
        # cv2.rectangle(frame, (margin, margin), (width - margin,
        #             height - margin), (255, 255, 255), 2)

        # Crop the frame to the focus area
        focus_frame = frame[margin:height-margin, margin:width-margin]

        # Find and decode barcodes
        barcodes = pyzbar.decode(focus_frame)

        # Loop through each barcode
        for barcode in barcodes:
            # Extract the barcode data as a string
            barcode_data = barcode.data.decode("utf-8")

            # Type the barcode data into the active application
            pyautogui.typewrite(barcode_data[:12])

            # Update the tkinter label with the barcode data
            self.barcode_label.configure(
                text="Barcode data: " + barcode_data[:12])

            # Play a notification sound
            data, fs = sf.read(
                root_path+"\\src\\notification_sound.mp3", dtype='float32')
            sd.play(data, fs)
            status = sd.wait()

            # Draw a green rectangle around the barcode area
            x, y, w, h = barcode.rect
            x += margin
            y += margin
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Convert the OpenCV frame to a PIL image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Convert the PIL image to a tkinter PhotoImage and display it on the canvas
        photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

        # Schedule the next update of the GUI
        self.canvas.after(10, self.update_gui)

    def select_webcam(self):
        # Update the index of the selected webcam
        self.webcam_idx = int(self.webcam_var.get().split()[-1])

        # Release the current video capture object
        self.cap.release()

        # Create a new video capture object for the selected webcam
        self.cap = cv2.VideoCapture(self.webcam_idx)

    def __del__(self):
        # Release the video capture object when the GUI is closed
        self.cap.release()


# Create a tkinter root window and a BarcodeReaderGUI object
root = tk.Tk()
root.title("Barcode Scanner")
root_path = os.path.abspath(os.path.dirname(__file__))
root.iconbitmap(root_path+"\icon.ico")
app = BarcodeReaderGUI(root)

# Start the tkinter event loop
root.mainloop()
