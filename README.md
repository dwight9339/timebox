# Timebox
A dead simple, minimalist, cross-platform desktop app for outlining a task and setting a timebox timer.

![Screenshot 2025-06-22 113905](https://github.com/user-attachments/assets/f57e960c-8131-4a3d-a10f-bce7fe024cf5)
![Screenshot 2025-06-22 114144](https://github.com/user-attachments/assets/755bb0ce-e2d6-4fd7-9610-58c96cd967e3)
![Screenshot 2025-06-18 210017](https://github.com/user-attachments/assets/ef36701a-ad1f-4a73-be52-3cd7a103fc1a)


## 🎬 Demo

[![Watch demo](https://github.com/user-attachments/assets/f57e960c-8131-4a3d-a10f-bce7fe024cf5)](https://github.com/user-attachments/assets/f3911ec9-d1d6-4184-881a-3175f73e7412)



## Features

- Set task timers
- Manage task presets
- Preset contexts: Create and manage different *sets* of presets related to different work contexts.
- Optionally set custom path to the contexts folder on your machine
- Runs locally! Disconnect from your distracting networks if needed
 
## Sharing Contexts

Your preset contexts are saved as separate `.json` files in a folder on your machine. By default, this folder is located at `~/.timebox_contexts` but this can be changed via the settings page.

To share a context with someone, just grab the `.json` file from this folder and hand it off. Simple as that!

To import a shared context, just place it in your contexts folder and restart the program, if needed.

Contexts can even be synced by using a shared directory (Dropbox, Google Drive, etc.)

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
