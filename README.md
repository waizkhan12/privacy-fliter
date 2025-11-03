# 🔒 Bluetooth Proximity Lock System

### 📡 Smart PC Locking Using Bluetooth Proximity Detection

The **Bluetooth Proximity Lock System** is an intelligent automation tool built in Python that automatically **locks or sleeps your computer** when your trusted Bluetooth device (like your phone or smartwatch) moves out of range.

This project provides a hands-free layer of security and convenience, blending **IoT**, **automation**, and **system-level scripting**.

---

## ⚙️ Features

- ✅ **Hands-Free PC Locking** – Locks or sleeps your computer automatically when you leave the Bluetooth range.    
- ✅ **Custom Range Control** – Adjust the signal threshold for sensitivity.  
- ✅ **Low CPU Usage** – Optimized for background execution with minimal performance impact.  
- ✅ **Cross-Platform Ready** – Works on Windows (tested), adaptable for Linux/macOS with small tweaks.  

---

## 🧠 How It Works

1. The script continuously scans for your chosen Bluetooth device using the `bleak` library.  
2. If your device’s signal disappears (out of range), the system triggers a **lock or sleep** command.  

> ⚙️ You can customize the script to either **lock**, **sleep**, or **hibernate** your PC when out of range.

---

## 🧩 Requirements

Before running the program, make sure you have the following installed:

- **Python 3.11+**
- **pip**
- **Bluetooth adapter (built-in or external)**
- **Windows 10/11**

Install all required dependencies:

```bash
pip install -r requirements.txt
