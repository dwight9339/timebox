# Timebox
A simple cross-platform desktop app for outlining a task and setting a timebox timer.

![Screenshot 2025-06-18 205755](https://github.com/user-attachments/assets/5acdd5f8-004a-4504-bad7-e9da9a22ac02)
![Screenshot 2025-06-18 204734](https://github.com/user-attachments/assets/e5daffa9-40a0-4f0a-adf6-8659aa216959)
![Screenshot 2025-06-18 210017](https://github.com/user-attachments/assets/ef36701a-ad1f-4a73-be52-3cd7a103fc1a)

## To run:
1. Clone the repository:
```
git clone https://github.com/yourusername/timebox.git
cd timebox
```

2. Run with Python:
```
python ./timebox.py
```

## Building from source
To create a standalone executable:

1. Install PyInstaller:
```
pip install pyinstaller
```

2. Build the binary:
```
pyinstaller --onefile timebox.py
```

The executable will be created in the `dist` directory. Note that `pyinstaller` works on Windows, Mac, or Linux but binaries must be built on the target operating system (i.e. building on Windows produces a `.exe`, building on Mac a `.app`, building on Linux produces an ELF binary)
