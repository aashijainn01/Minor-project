import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
import speech_recognition as sr
import threading
import math

# --- Configuration ---
# Disable fail-safe to prevent corners from crashing script (use with caution)
# or keep it enabled but ensure we clamp coordinates.
pyautogui.FAILSAFE = False 
pyautogui.PAUSE = 0  # Remove built-in delay for smoother movement

class AIVirtualMouse:
    def __init__(self):
        # Screen and Camera Setup
        self.screen_width, self.screen_height = pyautogui.size()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640) # Width
        self.cap.set(4, 480) # Height
        
        # Hand Tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Smoothing Variables
        self.smoothing_factor = 5
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0

        # ROI (Region of Interest) - The "active" box in the camera view
        # Moving hand inside this box covers the whole screen.
        self.frame_r = 100 # Frame Reduction (pixels from edges)

        # State Variables
        self.last_click_time = 0
        self.dragging = False
        self.voice_command = ""
        
        # Start Voice Thread
        self.voice_thread = threading.Thread(target=self.listen_voice, daemon=True)
        self.voice_thread.start()

    def listen_voice(self):
        r = sr.Recognizer()
        while True:
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    # Short timeout to keep loop responsive
                    audio = r.listen(source, phrase_time_limit=3, timeout=5)
                    text = r.recognize_google(audio).lower()
                    print(f"Voice recognized: {text}")
                    self.voice_command = text
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                # print(f"Voice Error: {e}")
                pass

    def process_voice_commands(self):
        if not self.voice_command:
            return

        cmd = self.voice_command
        if "open chrome" in cmd:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.1)
            pyautogui.typewrite("chrome\n")
        elif "scroll down" in cmd:
            pyautogui.scroll(-300)
        elif "scroll up" in cmd:
            pyautogui.scroll(300)
        elif "close tab" in cmd:
            pyautogui.hotkey('ctrl', 'w')
        elif "enter" in cmd:
            pyautogui.press('enter')
        
        self.voice_command = "" # Reset command

    def get_distance(self, p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def run(self):
        p_time = 0
        
        while True:
            success, img = self.cap.read()
            if not success:
                break

            # 1. Find Hand Landmarks
            img = cv2.flip(img, 1) # Mirror view
            h, w, c = img.shape
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = self.hands.process(img_rgb)
            
            # Draw ROI Box
            cv2.rectangle(img, (self.frame_r, self.frame_r), (w - self.frame_r, h - self.frame_r), (255, 0, 255), 2)

            if result.multi_hand_landmarks:
                for hand_lms in result.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                    
                    lm_list = []
                    for id, lm in enumerate(hand_lms.landmark):
                        px, py = int(lm.x * w), int(lm.y * h)
                        lm_list.append([id, px, py])

                    if lm_list:
                        # Tip IDs: Index=8, Middle=12, Thumb=4
                        x1, y1 = lm_list[8][1:]
                        x2, y2 = lm_list[12][1:]
                        x_thumb, y_thumb = lm_list[4][1:]

                        # 2. Check which fingers are up (Basic check based on y-coordinates)
                        # This can be improved, but using distance logic for now as per original script style
                        
                        # 3. Moving Mode: Index finger is the cursor
                        # Convert Coordinates with ROI
                        
                        # Map x1 from range (frame_r, w-frame_r) to (0, screen_width)
                        # We use numpy interp for easy mapping
                        x3 = np.interp(x1, (self.frame_r, w - self.frame_r), (0, self.screen_width))
                        y3 = np.interp(y1, (self.frame_r, h - self.frame_r), (0, self.screen_height))

                        # 4. Smoothen Values
                        self.curr_x = self.prev_x + (x3 - self.prev_x) / self.smoothing_factor
                        self.curr_y = self.prev_y + (y3 - self.prev_y) / self.smoothing_factor

                        # Move Mouse
                        # Clamp values to screen size to be safe
                        clamped_x = max(0, min(self.screen_width, self.curr_x))
                        clamped_y = max(0, min(self.screen_height, self.curr_y))
                        pyautogui.moveTo(clamped_x, clamped_y)
                        
                        self.prev_x, self.prev_y = self.curr_x, self.curr_y

                        # 5. Clicking Mode
                        dist_thumb_index = self.get_distance((x_thumb, y_thumb), (x1, y1))
                        dist_thumb_middle = self.get_distance((x_thumb, y_thumb), (x2, y2))
                        
                        # Debug distances
                        # cv2.putText(img, f"Dist: {int(dist_thumb_index)}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)

                        # Left Click (Pinch Index + Thumb)
                        if dist_thumb_index < 30:
                            # Debounce click
                            if time.time() - self.last_click_time > 0.3:
                                cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                                pyautogui.click()
                                self.last_click_time = time.time()
                            
                            # Dragging logic could go here if sustained pinch
                        
                        # Right Click (Pinch Middle + Thumb)
                        elif dist_thumb_middle < 30:
                             if time.time() - self.last_click_time > 0.3:
                                cv2.circle(img, (x2, y2), 15, (0, 0, 255), cv2.FILLED)
                                pyautogui.rightClick()
                                self.last_click_time = time.time()

                        # Scroll (Middle finger relative to Index)
                        # If Middle finger is significantly higher/lower than Index, scroll
                        # Note: This can be tricky. A better gesture might be "Both fingers up" vs "Index up"
                        # But sticking to original logic:
                        if y2 < y1 - 40: # Middle finger well above index
                             pyautogui.scroll(50)
                             cv2.putText(img, "Scroll Up", (20, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
                        elif y2 > y1 + 40:
                             pyautogui.scroll(-50)
                             cv2.putText(img, "Scroll Down", (20, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

            # Voice Command Feedback
            self.process_voice_commands()
            if self.voice_command:
                cv2.putText(img, f"Cmd: {self.voice_command}", (20, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            # Frame Rate
            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time
            cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            cv2.imshow("AI Mouse Optimized", img)
            if cv2.waitKey(1) & 0xFF == 27: # Esc to exit
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = AIVirtualMouse()
    app.run()
