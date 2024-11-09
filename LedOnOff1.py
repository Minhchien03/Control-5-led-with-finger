import pyfirmata
import time

board = pyfirmata.Arduino('COM4')

# Định nghĩa các chân điều khiển LED
LED_PINS = [2, 4, 7,8, 12]

# Thiết lập các chân làm đầu ra (OUTPUT)
for pin in LED_PINS:
    board.digital[pin].mode = pyfirmata.OUTPUT

while True:
    # Bật các LED
    for pin in LED_PINS:
        board.digital[pin].write(1)
    time.sleep(0.5)
    
    # Tắt các LED
    for pin in LED_PINS:
        board.digital[pin].write(0)
    time.sleep(0.5)
