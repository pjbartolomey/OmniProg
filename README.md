# 🛠️ OmniProg

I make no warranty or responsibility for anything associated with this program. Use it at your responsibility and risk.

OmniProg is a desktop application developed in Python featuring an interactive Graphical User Interface (GUI). It is designed to simplify the management, communication, and control of firmware and hardware drivers by acting as a unified frontend for external programming tools.

## 🚀 Key Features

* **Advanced Graphical Interface:** Built with **PySide6 (Qt)** to ensure a smooth, modern, and responsive user experience.
* **Unified Frontend:** Streamlines hardware interaction by interfacing with external tools like **FlashMagic** and **MPLAB IPE**.
* **Firmware Management:** Dedicated modules tailored for flashing, verifying, and managing firmware across devices.
* **Driver Control:** Direct low-level communication and handling of specific hardware libraries.
* **Flexible Configuration:** Effortless parameter management via local `.ini` configuration files.

## 📦 Requirements & Installation

This project is fully compatible with **Linux (Debian-based distributions)** and other systems running Python 3.

### 1. Clone the Repository
Open your terminal and clone the project using the simplest HTTPS method:
```bash
git clone https://github.com
cd OmniProg
```

### 2. Install Dependencies
Ensure you have Python 3 installed, then install the required libraries (including PySide6) from the requirements file:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Launch the main application by executing:
```bash
python3 OmniProg.py
```

## 📂 Project Structure

* `OmniProg.py`: The main entry point that initializes and launches the application.
* `omni_firmware.py` & `omni_drivers.py`: Low-level modules managing hardware interaction and external tool integration.
* `OmniProg.ui` & `OmniProg_ui.py`: User interface design files generated via Qt.
* `OmniProg.ini`: Local configuration file used to store application parameters and preferences.

## 🔨 How to Build an Executable (Optional)

If you want to package OmniProg into a standalone executable file, you can use **PyInstaller**. This allows the program to run on machines without requiring a Python installation.

### 1. Install PyInstaller
Make sure PyInstaller is installed in your environment:
```bash
pip install pyinstaller
```

### 2. Generate the Executable
Run the following command in the project root folder to build a single, windowed application (without an attached terminal window):
```bash
pyinstaller --noconfirm --onedir --windowed --add-data "OmniProg.ini:." OmniProg.py
```

The final bundle will be generated inside the `dist/` directory.


---
*Developed with 💻 on Linux. Contributions and feedback are welcome!*
