from RPLCD.i2c import CharLCD
import time

# Inisialisasi LCD I2C 20x4
lcd = CharLCD('PCF8574', 0x27, cols=20, rows=4, auto_linebreaks=False)

# Bersihkan layar
lcd.clear()
time.sleep(0.1)

# Baris Pertama: "PURE-IT" (7 karakter)
lcd.cursor_pos = (0, 6)  # row 0, col 6
lcd.write_string("PURE-IT")

# Baris Kedua: "Select Mode" (11 karakter)
lcd.cursor_pos = (1, 4)
lcd.write_string("Select Mode")

# Baris Ketiga: "Detection" (9 karakter)
lcd.cursor_pos = (2, 5)
lcd.write_string("Detection")

# Baris Keempat: "Rehabilitation" (14 karakter)
lcd.cursor_pos = (3, 3)
lcd.write_string("Rehabilitation")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    lcd.clear()
