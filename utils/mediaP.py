import cv2
import numpy as np
import mediapipe as mp
import socket
import speech_recognition as sr
from fs import faceswap  

class PoseDetection:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.last_state = None
        self.conn = None

    @staticmethod
    def three_angle(a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        return angle


    #TODO STT를 위한 함수
    def start_stt(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        with microphone as source:
            while True:
                print("STT 실행. '그만'이라고 말하면 종료")
                audio_data = recognizer.listen(source, phrase_time_limit=2)
                try:
                    text = recognizer.recognize_google(audio_data, language='ko-KR')
                    print(f"당신이 말한 것: {text}")
                    if self.conn:
                        self.conn.sendall(f"STT:{text}".encode())
                    if "그만" in text:
                        print("STT 종료됨.")
                        return
                except sr.UnknownValueError:
                    print("음성을 이해할 수 없습니다.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    return
                
    def run_pose_detection(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Could not open video capture")
            return
        if cv2.waitkey(1) == ord('a'):
            cv2.imwrite('images/cap.jpg', frame)
            faceswap('images/arrow6.jpg', 'images/ic1.jpg')

        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            host, port = 'localhost', 50000
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                s.listen()
                self.conn, addr = s.accept()
                with self.conn:
                    print('Connected by', addr)
                    while True:
                        ret, frame = cap.read()
                        new_state = None
                        if not ret:
                            print("Failed to grab frame")
                            break

                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        image.flags.writeable = False
                        result = pose.process(image)
                        image.flags.writeable = True
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                        self.mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                        try:
                            landmarks = result.pose_landmarks.landmark
                            
                            # Get coordinates
                            shoulder_left = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                            landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                            shoulder_right = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                            landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                            elbow_left = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                        landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                            elbow_right = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                        landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                            wrist_left = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                        landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                            wrist_right = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                        landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                            # 어깨와 손목의 좌표
                            shoulder_right = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                            landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                            wrist_right = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                        landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                            
                            # Calculate angles
                            angle_left = self.three_angle(self, shoulder_left, elbow_left, wrist_left)
                            angle_right = self.three_angle(shoulder_right, elbow_right, wrist_right)
                            
                            
                            # 어깨와 손목의 y좌표가 비슷한지 확인 (옆으로 팔이 뻗어 있는지)
                            y_threshold = 0.05
                            x_threshold = 0.05
                            is_arm_stretched_left = abs(shoulder_left[1] - wrist_left[1]) < y_threshold and abs(shoulder_left[0] - wrist_left[0]) > x_threshold
                            is_arm_stretched_right = abs(shoulder_right[1] - wrist_right[1]) < y_threshold and abs(shoulder_right[0] - wrist_right[0]) > x_threshold

                            # 팔이 어느 정도 위로 올라갔는지 확인
                            arm_lifted_left = elbow_left[1] > shoulder_left[1]
                            arm_lifted_right = elbow_right[1] > shoulder_right[1]

                            # Classification
                            if angle_right < 90:
                                new_state = "start"
                            elif is_arm_stretched_left and arm_lifted_left:
                                new_state = "ready"
                            elif is_arm_stretched_right and arm_lifted_right:
                                new_state = "shot"
                            elif angle_left < 90:
                                new_state = "change"
                            else:
                                new_state = "Unknown"

                        except Exception as e:
                            print("Error occurred:", e)
                        if new_state != self.last_state:
                            self.last_state = new_state
                            self.conn.sendall(f"POSE:{new_state}".encode())
                            
                        cv2.imshow('pose', image)
                        
                        if cv2.waitKey(10) & 0xFF == ord('q'):
                            break


        cap.release()
        cv2.destroyAllWindows()

cap.release()
cv2.destroyAllWindows()