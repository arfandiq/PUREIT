import RPi.GPIO as GPIO
import time

# -----------------------------
# KONFIGURASI GPIO
# -----------------------------
BUTTON_RIGHT = 24
BUTTON_LEFT = 23
BUTTON_SELECT = 22
BUTTON_UP = 27
BUTTON_DOWN = 17

GPIO.setmode(GPIO.BCM)  # gunakan nomor GPIO, bukan nomor pin fisik
GPIO.setup(BUTTON_RIGHT, GPIO.IN)
GPIO.setup(BUTTON_LEFT, GPIO.IN)
GPIO.setup(BUTTON_SELECT, GPIO.IN)
GPIO.setup(BUTTON_UP, GPIO.IN)
GPIO.setup(BUTTON_DOWN, GPIO.IN)

print("Program berjalan. Tekan tombol, tekan Ctrl+C untuk keluar.\n")

try:
    while True:
        if GPIO.input(BUTTON_RIGHT) == GPIO.HIGH:
            print("Button KANAN ditekan")
            time.sleep(0.2)  # debounce sederhana

        if GPIO.input(BUTTON_LEFT) == GPIO.HIGH:
            print("Button KIRI ditekan")
            time.sleep(0.2)

        if GPIO.input(BUTTON_SELECT) == GPIO.HIGH:
            print("Button PILIH/OK ditekan")
            time.sleep(0.2)

        if GPIO.input(BUTTON_UP) == GPIO.HIGH:
            print("Button ATAS ditekan")
            time.sleep(0.2)

        if GPIO.input(BUTTON_DOWN) == GPIO.HIGH:
            print("Button BAWAH ditekan")
            time.sleep(0.2)

        time.sleep(0.01)  # loop ringan supaya CPU tidak 100%
except KeyboardInterrupt:
    print("\nProgram dihentikan oleh user.")
finally:
    GPIO.cleanup()
    print("GPIO dibersihkan. Program selesai.")
