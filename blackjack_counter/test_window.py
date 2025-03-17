import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

print('=== Test Window Detection ===')

# Use same AppleScript implementation as main.py
script = '''
tell application "System Events"
    set windowList to {}
    repeat with proc in processes where background only is false
        tell proc
            repeat with win in windows
                set end of windowList to {title:name, size:{size of win}, position:{position of win}}
            end repeat
        end tell
    end repeat
    return windowList
end tell
'''

try:
    proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    output = proc.stdout.strip()
    
    if not output:
        print('No windows found')
        exit()

    # Parse AppleScript output
    windows = [w.strip('{}') for w in output.split('},')]
    print(f'Found {len(windows)} windows:')
    
    for i, win in enumerate(windows, 1):
        try:
            title_part = [p for p in win.split(',') if 'title:' in p][0].split('title:')[1].strip()
            size_part = [p for p in win.split(',') if 'size:' in p][0].split('size:')[1].strip()
            width, height = size_part.replace('{', '').replace('}', '').split(', ')
            print(f'{i}. {title_part} ({width}x{height})')
        except Exception as e:
            print(f'{i}. Error parsing window: {e}')

except Exception as e:
    print(f'Error getting windows: {e}')
    exit(1)

# Create simple Tkinter UI to verify display
root = tk.Tk()
root.title("Window Test Results")
root.geometry("400x300")

frame = ttk.Frame(root)
frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Detected Windows:", font=('Helvetica', 12)).pack()

listbox = tk.Listbox(frame, height=10)
listbox.pack(fill=tk.BOTH, expand=True)

for win in windows:
    try:
        title = win.split('title:')[1].split(',')[0].strip()
        listbox.insert(tk.END, title)
    except:
        continue

root.mainloop()