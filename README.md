# AI Virtual Mouse

A futuristic, contactless mouse controller that allows you to control your computer cursor using hand gestures and voice commands. Built with Python, OpenCV, and MediaPipe.

## 🚀 Features

- **Hand Tracking**: Real-time hand detection using MediaPipe.
- **Cursor Control**: Move your cursor smoothly by moving your index finger.
- **Clicking**:
  - **Left Click**: Pinch your Index Finger and Thumb.
  - **Right Click**: Pinch your Middle Finger and Thumb.
- **Scrolling**: Move your Middle Finger up or down relative to your Index Finger to scroll.
- **Voice Commands**: Control your PC with voice! (e.g., "Open Chrome", "Scroll Down", "Enter").
- **Smoothed Movement**: integrated smoothing algorithm for jitter-free cursor control.

## 🛠️ Technologies Used

- **Python 3.x**
- **OpenCV** (Computer Vision)
- **MediaPipe** (Hand Tracking)
- **PyAutoGUI** (Mouse & Keyboard Control)
- **SpeechRecognition** (Voice Commands)
- **NumPy** (Math calculations)

## 📦 Installation

1. **Clone the repository** (or download usage files):
   ```bash
   git clone [https://github.com/yourusername/AI-Mouse.git](https://github.com/yourusername/AI-Mouse.git)
   cd AI-Mouse
   Install the required libraries: You can install all dependencies using pip:
bash
pip install opencv-python mediapipe pyautogui numpy SpeechRecognition pyaudio
Note: pyaudio is required for microphone input. If you have trouble installing it on Windows, try pip install pipwin then pipwin install pyaudio.


🎮 How to Use
Run the script:
bash
python AI-Mouse.py
Gestures Guide:
Move Cursor: Point with your Index Finger and move your hand.
Left Click: Bring your Thumb and Index Finger together.
Right Click: Bring your Thumb and Middle Finger together.
Scroll: Raise your Middle Finger above your Index finger to scroll UP, or lower it to scroll DOWN.
Voice Commands: The system listens for commands in the background. Try saying:
"Open Chrome"
"Scroll Up" / "Scroll Down"
"Close Tab"
"Enter"
⚙️ Configuration
You can adjust settings inside 
AI-Mouse.py
 to customize sensitivity:

frame_r (Frame Reduction): Adjusts the size of the active control area.
smoothing_factor: Increase this value for smoother (but slightly slower) mouse movement.
📝 License
This project is open-source and available under the 
MIT License
