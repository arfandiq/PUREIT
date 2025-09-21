# =======================================
# PURE-IT ALL-IN-ONE (Detection + Rehab)
# =======================================

import RPi.GPIO as GPIO
import time
from RPLCD.i2c import CharLCD
import serial
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
import os

# ==============================
# GPIO BUTTON
# ==============================
BUTTON_RIGHT = 24
BUTTON_LEFT = 23
BUTTON_SELECT = 22
BUTTON_UP = 27
BUTTON_DOWN = 17
RELAY_PIN = 4  # Rehab motor/relay

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_SELECT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # relay OFF default

# ==============================
# LCD
# ==============================
lcd = CharLCD('PCF8574', 0x27, cols=20, rows=4, auto_linebreaks=False)
lcd.clear()

# ==============================
# MENU
# ==============================
menu_items = ["Detection", "Rehabilitation"]
selected_index = 0

def draw_menu():
    lcd.clear()
    lcd.cursor_pos = (0, 6)
    lcd.write_string("PURE-IT")
    lcd.cursor_pos = (1, 4)
    lcd.write_string("Select Mode")
    for i, item in enumerate(menu_items):
        lcd.cursor_pos = (2 + i, 3)
        lcd.write_string("> " + item if i == selected_index else "  " + item)

# ==============================
# FLEX SENSOR CONFIG
# ==============================
PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
DURATION = 30

kalibrasi = {
    "thumb": (226, 424),
    "index": (251, 649),
    "middle": (202, 554),
    "ring": (189, 514),
    "little": (189, 506)
}

def adc_to_angle(adc_value, adc_min, adc_max):
    adc_value = max(min(adc_value, adc_max), adc_min)
    return (adc_value - adc_min) / (adc_max - adc_min) * 180

# ==============================
# RECORD FLEX SENSOR
# ==============================
def record_flex(lcd):
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    except serial.SerialException:
        lcd.clear()
        lcd.write_string("Error: Cannot open")
        lcd.cursor_pos = (1,0)
        lcd.write_string(f"{PORT}")
        time.sleep(2)
        return []

    time.sleep(2)
    ser.reset_input_buffer()
    data_list = []

    lcd.clear()
    lcd.write_string("Press RED button")
    lcd.cursor_pos = (1,0)
    lcd.write_string("to start detection")

    # Tunggu tombol SELECT ditekan
    while GPIO.input(BUTTON_SELECT) == GPIO.HIGH:
        time.sleep(0.1)

    lcd.clear()
    start_time = time.time()
    while time.time() - start_time < DURATION:
        t = time.time() - start_time
        lcd.cursor_pos = (2, 0)
        lcd.write_string(f"Recording: {int(t)} s   ")

        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue
        values = line.split(",")
        if len(values) != 5:
            continue
        j, i, m, r, l = map(int, values)
        data_list.append([
            t,
            adc_to_angle(j, *kalibrasi["thumb"]),
            adc_to_angle(i, *kalibrasi["index"]),
            adc_to_angle(m, *kalibrasi["middle"]),
            adc_to_angle(r, *kalibrasi["ring"]),
            adc_to_angle(l, *kalibrasi["little"])
        ])
    ser.close()
    lcd.clear()
    lcd.write_string("Processing data...")
    time.sleep(1)
    return data_list

# ==============================
# PREPROCESS
# ==============================
def preprocess_flex(data_list):
    df = pd.DataFrame(data_list, columns=["Time(s)", "Thumb", "Index", "Middle", "Ring", "Little"])
    df = df[(df["Time(s)"] >= 5) & (df["Time(s)"] <= 25)].copy()
    kondisi = []
    for t in df["Time(s)"]:
        if 5 <= t < 10:
            kondisi.append("contraction")
        elif 10 <= t < 15:
            kondisi.append("relaxation")
        elif 15 <= t < 20:
            kondisi.append("contraction")
        elif 20 <= t <= 25:
            kondisi.append("relaxation")
        else:
            kondisi.append("unknown")
    df["Condition"] = kondisi
    return df.reset_index(drop=True)

# ==============================
# LOAD SVM MODEL
# ==============================
def load_svm_model():
    path = "models/svm_flex.pkl"
    if not os.path.exists(path):
        lcd.clear()
        lcd.write_string("Error: SVM model")
        lcd.cursor_pos = (1,0)
        lcd.write_string("not found")
        time.sleep(2)
        return None
    return joblib.load(path)

# ==============================
# EVALUATE
# ==============================
def evaluate_svm(model, df, lcd):
    X = df[["Thumb", "Index", "Middle", "Ring", "Little"]].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    y_pred = model.predict(X_scaled)
    counts = pd.Series(y_pred).value_counts()
    if len(counts) == 1:
        result = "CTS" if counts.index[0]==1 else "No CTS"
    else:
        result = "CTS" if counts.idxmax()==1 else "No CTS"
    lcd.clear()
    lcd.write_string("Detection Result:")
    lcd.cursor_pos = (3,0)
    lcd.write_string(result)
    return result

# ==============================
# REHABILITATION
# ==============================
def run_rehab(lcd, duration=10):
    lcd.clear()
    lcd.write_string("Press RED button")
    lcd.cursor_pos = (1,0)
    lcd.write_string("to start rehab")
    while GPIO.input(BUTTON_SELECT) == GPIO.HIGH:
        time.sleep(0.1)

    lcd.clear()
    start_time = time.time()
    GPIO.output(RELAY_PIN, GPIO.LOW)  # ON
    try:
        while time.time() - start_time < duration:
            t = int(time.time() - start_time)
            lcd.cursor_pos = (2,0)
            lcd.write_string(f"Rehab Time: {t} s  ")
            time.sleep(1)
    finally:
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # OFF
        lcd.clear()
        lcd.write_string("Rehab Finished")
        time.sleep(2)

# ==============================
# MAIN LOOP
# ==============================
try:
    draw_menu()
    while True:
        if GPIO.input(BUTTON_UP) == GPIO.LOW:
            selected_index = (selected_index - 1) % len(menu_items)
            draw_menu()
            time.sleep(0.3)
        if GPIO.input(BUTTON_DOWN) == GPIO.LOW:
            selected_index = (selected_index + 1) % len(menu_items)
            draw_menu()
            time.sleep(0.3)
        if GPIO.input(BUTTON_SELECT) == GPIO.LOW:
            if menu_items[selected_index]=="Detection":
                data = record_flex(lcd)
                if data:
                    df_pp = preprocess_flex(data)
                    model = load_svm_model()
                    if model:
                        evaluate_svm(model, df_pp, lcd)
                        lcd.write_string(" Right/Left to menu")
                        while True:
                            if GPIO.input(BUTTON_RIGHT)==GPIO.LOW or GPIO.input(BUTTON_LEFT)==GPIO.LOW:
                                break
                            time.sleep(0.1)
            else:  # Rehabilitation
                run_rehab(lcd)
                draw_menu()
        time.sleep(0.01)

except KeyboardInterrupt:
    pass
finally:
    lcd.clear()
    GPIO.cleanup()
    print("Program ended. GPIO cleaned.")
