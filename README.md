# Timebox
A dead simple, minimalist, cross-platform desktop app for outlining a task and setting a timebox timer.

![Screenshot 2025-06-19 112430](https://github.com/user-attachments/assets/ef56c195-f3ec-421f-a294-442b55ef5c7b)
![Screenshot 2025-06-19 112602](https://github.com/user-attachments/assets/7af1b569-7e32-4f92-9d18-a2c639aec4f8)
![Screenshot 2025-06-18 210017](https://github.com/user-attachments/assets/ef36701a-ad1f-4a73-be52-3cd7a103fc1a)

## Features

- Set task timers
- Manage task presets
- Optionally: Set custom path to presets file
 
## Planned Features

- Automated timer window sizing: Timer windows automatically adjusted to fit their contents
- Preset Contexts: Switch between different sets of presets
- Configurable alert timing: Provide more options for time alerts
- Configure sounds to play for time alerts or timer expiration
- Break up entries in the DoD items field visually with automated "-" characters at the beginning of each line

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

1. Create and activate a virtual environment:
```
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Build the binary:
```
# On Windows (to prevent CMD window creation)
pyinstaller --onefile --windowed timebox.py

# On Mac/Linux
pyinstaller --onefile timebox.py
```

The executable will be created in the `dist` directory. Note that `pyinstaller` works on Windows, Mac, or Linux but binaries must be built on the target operating system (i.e. building on Windows produces a `.exe`, building on Mac a `.app`, building on Linux produces an ELF binary)
