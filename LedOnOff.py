import cv2
import mediapipe as mp
import math
import pyfirmata
import time

# Khởi tạo kết nối với Arduino
board = pyfirmata.Arduino('COM4')

# Định nghĩa các chân điều khiển LED
LED_PINS = {
    1: 2,
    2: 4,
    3: 7,
    4: 8,
    5: 12
}

# Thiết lập các chân làm đầu ra (OUTPUT)
for pin in set(LED_PINS.values()):
    board.digital[pin].mode = pyfirmata.OUTPUT

def den_bat(pin):
    board.digital[pin].write(1)

def den_tat(pin):
    board.digital[pin].write(0)

# Khởi tạo MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Khởi tạo camera
cap = cv2.VideoCapture(0)

# Hàm tính khoảng cách giữa hai điểm
def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

# Hàm tính góc giữa ba điểm
def calculate_angle(p1, p2, p3):
    v1 = (p1.x - p2.x, p1.y - p2.y)
    v2 = (p3.x - p2.x, p3.y - p2.y)
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    magnitude_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
    cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
    angle = math.degrees(math.acos(min(1.0, max(-1.0, cos_angle))))
    return angle

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Định nghĩa ID của các đầu ngón tay và gốc ngón tay
            finger_tips = [4, 8, 12, 16, 20]  # Đầu ngón cái, trỏ, giữa, áp út, út
            finger_bases = [1, 5, 9, 13, 17]  # Gốc ngón cái, trỏ, giữa, áp út, út
            led_states = []

            for i, tip_id in enumerate(finger_tips):
                # Tính khoảng cách từ đầu ngón tay đến gốc
                distance = calculate_distance(hand_landmarks.landmark[tip_id], hand_landmarks.landmark[finger_bases[i]])
                
                # Xác định trạng thái "mở" của ngón tay
                if i == 0:  # Kiểm tra riêng cho ngón cái
                    thumb_angle = calculate_angle(
                        hand_landmarks.landmark[2],
                        hand_landmarks.landmark[3],
                        hand_landmarks.landmark[4]
                    )
                    is_open = thumb_angle > 170
                else:
                    is_open = distance > 0.07

                led_states.append(is_open)
                
                # Bật LED nếu ngón tay đang mở, tắt nếu ngón tay gập
                if is_open:
                    den_bat(LED_PINS[i + 1])
                    # Vẽ hình tròn lên đầu ngón tay
                    x_tip = int(hand_landmarks.landmark[tip_id].x * frame.shape[1])
                    y_tip = int(hand_landmarks.landmark[tip_id].y * frame.shape[0])
                    cv2.circle(frame, (x_tip, y_tip), 10, (0, 0, 255), -1)
                else:
                    den_tat(LED_PINS[i + 1])

            # Hiển thị số lượng ngón tay mở ra
            count_fingers = sum(led_states)
            cv2.putText(frame, str(count_fingers), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            print("Số ngón tay mở:", count_fingers)

    cv2.imshow('Finger Count', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        for pin in set(LED_PINS.values()):
            board.digital[pin].write(0)
        break

cap.release()
cv2.destroyAllWindows()
