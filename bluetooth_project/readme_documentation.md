# Bluetooth Proximity Lock System

A professional Python-based system that automatically locks your Windows laptop when your phone moves away and unlocks it when you return, using Bluetooth signal strength (RSSI).

## 🎯 Features

- **Automatic Lock/Unlock**: Seamlessly lock your laptop when you walk away
- **RSSI-Based Detection**: Uses Bluetooth signal strength for accurate proximity detection
- **Hysteresis Protection**: Prevents rapid lock/unlock cycling
- **Comprehensive Logging**: Tracks all events with timestamps and RSSI values
- **Modular Architecture**: Clean, maintainable, and extensible code
- **Error Handling**: Robust error recovery and validation
- **Statistics Tracking**: Monitor system usage and performance

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10 or Windows 11
- **Python**: Version 3.11 (64-bit)
- **Bluetooth**: Built-in or USB Bluetooth adapter
- **Phone**: Any Bluetooth-enabled smartphone (paired with laptop)

### Python Dependencies
```bash
bleak>=0.21.0
```

## 🚀 Installation

### Step 1: Install Python
1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. During installation, **check "Add Python to PATH"**
3. Verify installation:
   ```bash
   python --version
   ```

### Step 2: Install Dependencies
```bash
pip install bleak
```

### Step 3: Download the Project
Clone or download all 5 Python files to the same directory:
- `config.py`
- `bluetooth_scanner.py`
- `system_control.py`
- `logger.py`
- `main.py`

### Step 4: Find Your Phone's MAC Address

**Method 1: Using the built-in scanner**
```bash
python bluetooth_scanner.py
```
This will list all nearby Bluetooth devices with their MAC addresses.

**Method 2: Windows Settings**
1. Open Windows Settings → Bluetooth & Devices
2. Find your phone in the device list
3. Click on it to see device properties

**Method 3: Phone Settings**
- **Android**: Settings → About Phone → Status → Bluetooth Address
- **iPhone**: Settings → General → About → Bluetooth

### Step 5: Configure the System
Edit `config.py` and replace the MAC address:
```python
PHONE_MAC = "XX:XX:XX:XX:XX:XX"  # Replace with your phone's MAC
```

### Step 6: Adjust Thresholds (Optional)
Fine-tune the distance thresholds in `config.py`:
```python
LOCK_THRESHOLD = -80    # Lock when RSSI drops below this
UNLOCK_THRESHOLD = -70  # Unlock when RSSI rises above this
SCAN_INTERVAL = 5       # Seconds between scans
```

## 🎮 Usage

### Starting the System
```bash
python main.py
```

### Stopping the System
Press `Ctrl+C` to stop gracefully. Statistics will be displayed.

### Testing
1. Start the system with your phone nearby
2. Walk away from your laptop (wait ~15 seconds)
3. Your laptop should lock automatically
4. Walk back to your laptop
5. The system will wake the display

## 📊 Understanding RSSI Values

RSSI (Received Signal Strength Indicator) measures Bluetooth signal strength:

| RSSI Range | Distance | Signal Quality |
|------------|----------|----------------|
| -30 to -50 | Very Close | Excellent |
| -50 to -70 | Near | Good |
| -70 to -80 | Medium | Fair |
| -80 to -90 | Far | Poor |
| Below -90  | Very Far | Weak |

**Recommended Settings:**
- **Close proximity**: LOCK: -75, UNLOCK: -65
- **Medium proximity**: LOCK: -80, UNLOCK: -70 (default)
- **Far proximity**: LOCK: -85, UNLOCK: -75

## 📁 Project Structure

```
BluetoothProximityLock/
│
├── config.py                 # Configuration settings
├── bluetooth_scanner.py      # Bluetooth scanning logic
├── system_control.py         # Windows lock/unlock commands
├── logger.py                 # Event logging system
├── main.py                   # Main controller
└── activity_log.txt          # Generated log file
```

## 🔧 Module Details

### config.py
Central configuration hub for all system parameters. Modify this file to customize behavior.

**Key Settings:**
- `PHONE_MAC`: Your phone's Bluetooth MAC address
- `LOCK_THRESHOLD`: RSSI value triggering lock
- `UNLOCK_THRESHOLD`: RSSI value triggering unlock
- `SCAN_INTERVAL`: Time between scans (seconds)
- `CONSECUTIVE_FAIL_THRESHOLD`: Scan failures before locking

### bluetooth_scanner.py
Handles all Bluetooth operations using the `bleak` library.

**Features:**
- Asynchronous device scanning
- RSSI retrieval
- Device proximity checking
- Diagnostic mode for device discovery

**Standalone Usage:**
```bash
python bluetooth_scanner.py
```

### system_control.py
Manages Windows system operations.

**Functions:**
- `lock_system()`: Locks the workstation
- `wake_system()`: Simulates user activity to wake display
- Statistics tracking

**Standalone Testing:**
```bash
python system_control.py
```

### logger.py
Comprehensive event logging system.

**Features:**
- Timestamped event logging
- File and console output
- Event categorization
- RSSI tracking

**Standalone Testing:**
```bash
python logger.py
```

### main.py
Main controller that orchestrates all modules.

**Responsibilities:**
- State machine management
- Scan loop coordination
- Configuration validation
- Statistics reporting

## 🐛 Troubleshooting

### Issue: "Phone MAC address not configured"
**Solution**: Edit `config.py` and set your phone's MAC address.

### Issue: "Bluetooth adapter error"
**Solution**: 
1. Ensure Bluetooth is enabled on your laptop
2. Check Device Manager for Bluetooth adapter
3. Update Bluetooth drivers
4. Restart Bluetooth service

### Issue: System locks immediately
**Solution**: 
1. Ensure your phone is paired with the laptop
2. Make sure Bluetooth is enabled on your phone
3. Increase `LOCK_THRESHOLD` (make it less negative, e.g., -75)
4. Increase `CONSECUTIVE_FAIL_THRESHOLD` to 3 or 4

### Issue: System doesn't unlock
**Solution**:
1. Decrease `UNLOCK_THRESHOLD` (make it more negative, e.g., -75)
2. Ensure phone is close to laptop (within 3-5 meters)
3. Check logs for RSSI values

### Issue: Rapid lock/unlock cycling
**Solution**: Increase the gap between thresholds (hysteresis):
```python
LOCK_THRESHOLD = -85
UNLOCK_THRESHOLD = -70  # 15 dBm gap
```

### Issue: "BleakError" or scan failures
**Solution**:
1. Restart Bluetooth on Windows
2. Run as Administrator
3. Check for conflicting Bluetooth applications
4. Increase `SCAN_TIMEOUT` to 5.0

## 📝 Logs

All events are logged to `activity_log.txt` with:
- Timestamp
- Event type
- RSSI value
- Action taken

**Example Log:**
```
[2025-10-09 14:23:15] [SYSTEM_START] Bluetooth Proximity Lock system started | RSSI: N/A
[2025-10-09 14:23:20] [PHONE_DETECTED] Target device detected in range | RSSI: -65 dBm
[2025-10-09 14:25:40] [PHONE_DETECTED] Target device detected in range | RSSI: -82 dBm
[2025-10-09 14:25:45] [SYSTEM_LOCKED] System locked due to proximity threshold | RSSI: -82 dBm
[2025-10-09 14:28:10] [PHONE_DETECTED] Target device detected in range | RSSI: -68 dBm
[2025-10-09 14:28:15] [SYSTEM_UNLOCKED] System unlocked - device in proximity | RSSI: -68 dBm
```

## 🔐 Security Considerations

### Strengths
- No network connectivity required
- No cloud services or third-party dependencies
- Local operation only
- Bluetooth range limited (typically 10-30 meters)

### Limitations
- Physical proximity can be spoofed if attacker has your phone
- Bluetooth signals can sometimes penetrate walls
- System doesn't encrypt Bluetooth communications (uses OS)

### Best Practices
1. Use in conjunction with strong password protection
2. Enable BitLocker for disk encryption
3. Set Windows to require password immediately after lock
4. Don't rely solely on proximity lock for high-security scenarios

## ⚙️ Advanced Configuration

### Running on Startup
Create a batch file `start_proximity_lock.bat`:
```batch
@echo off
cd /d "C:\path\to\BluetoothProximityLock"
python main.py
```

Add to Windows Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At log on
4. Action: Start a program
5. Program: Path to your .bat file

### Multiple Devices
To monitor multiple phones, modify `config.py`:
```python
PHONE_MACS = [
    "XX:XX:XX:XX:XX:XX",  # Phone 1
    "YY:YY:YY:YY:YY:YY",  # Phone 2
]
```
(Requires modification of `bluetooth_scanner.py` to handle multiple MACs)

### Custom Actions
Extend `system_control.py` to add custom actions:
- Send notifications
- Run custom scripts
- Control smart home devices
- Log to cloud services

## 🤝 Contributing

This is a professional, production-ready system. Potential improvements:
- Support for macOS and Linux
- GUI interface
- Mobile app for configuration
- Machine learning for adaptive thresholds
- Multiple device support

## 📄 License

MIT License - Free to use and modify

## 👨‍💻 Author

Professional Development Team - Version 1.0.0

## 🆘 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs in `activity_log.txt`
3. Run diagnostic mode: `python bluetooth_scanner.py`
4. Verify configuration in `config.py`

## 🎓 How It Works

1. **Scanning**: System continuously scans for your phone's Bluetooth signal
2. **RSSI Measurement**: Measures signal strength (RSSI) in dBm
3. **Threshold Comparison**: Compares RSSI to configured thresholds
4. **Hysteresis**: Different thresholds for lock/unlock prevent rapid cycling
5. **Action Execution**: Locks or wakes system based on proximity
6. **Logging**: Records all events and RSSI values

## 🚦 Status Indicators

During operation, watch for these console messages:

- `[SCAN] Device found` - Phone detected successfully
- `[SCAN] Target device not detected` - Phone out of range
- `[ACTION] Executing system lock` - Locking workstation
- `[ACTION] Simulating system wake` - Waking display
- `[ERROR]` - Error occurred (check details)
- `[WARNING]` - Non-critical issue

---

**Happy secure computing! 🔒📱💻**