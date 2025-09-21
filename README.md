# 🩺 PURE-IT  
**Portable Utility for Rehabilitation & Examination – Innovative Technology**  

---

## 📖 Overview  
**PURE-IT** is an innovative dual-module system designed for **early screening** and **home-based rehabilitation** of Carpal Tunnel Syndrome (CTS). The system is built to be accessible, safe, and user-friendly, empowering individuals to manage CTS outside clinical settings.

---

## 🧩 System Architecture  
PURE-IT consists of two physically separate modules:  

- **🖥️ Detection Unit** – Captures multi-channel **sEMG** signals and wrist angles using flex sensors.  
  - Data is processed on a **Raspberry Pi 5** with filtering, rectification, and feature extraction (RMS, slope sign change).  
  - A **Support Vector Machine (SVM)** classifier categorizes CTS risk into **low, medium, or high**, displayed on an LCD and optionally sent via Telegram bot.  

- **🧤 Rehabilitation Glove** – Provides therapy using **infrared heat** (850–940 nm) and **targeted vibration** to reduce inflammation, promote healing, and relax hypertonic muscles.  
  - Real-time temperature monitoring automatically shuts off therapy if it exceeds a safety threshold.  
  - Ergonomic, breathable design for comfortable sessions, with timers to avoid overuse.

---

## 🧠 Key Features  
- **Dual-Module Safety** – Physical separation prevents electrical interference between detection and therapy.  
- **Real-Time Analysis** – Onboard processing for instant feedback.  
- **Therapeutic Feedback** – Combines heat and vibration based on physiotherapy principles.  
- **Portable & Wireless** – Battery-powered, safe for home use.  

---

## 🧪 Datasets  
PURE-IT uses two data sources:  
1. **sEMG Data** – Captures muscle activity and physiological markers of CTS.  
2. **Flex Sensor Data** – Measures finger and wrist flexion angles during movement.  

---

## 🎯 Goal  
To deliver a **low-cost, portable, and reliable solution** for CTS detection and rehabilitation, helping patients monitor progress and receive therapy in a safe, convenient way.

