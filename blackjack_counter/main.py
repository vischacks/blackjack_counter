import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from blackjack_gui import BlackjackCounterGUI

def get_game_window():
    script = '''
    tell application "System Events"
        set windowData to ""
        repeat with proc in processes where background only is false
            tell proc
                repeat with win in windows
                    set winTitle to name of win
                    set winSize to size of win
                    set windowData to windowData & "%%%" & winTitle & "###" & (item 1 of winSize as text) & "x" & (item 2 of winSize as text)
                end repeat
            end tell
        end repeat
        return windowData
    end tell
    '''

    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
        window_entries = [entry for entry in result.stdout.split('%%%') if entry.strip()]
        
        matched_windows = []
        for entry in window_entries:
            if "###" in entry:
                title, size = entry.split("###", 1)
                if any(s in title.lower() for s in ['blackjack', 'casino', 'bj', '21']) or ('black' in title.lower() and 'jack' in title.lower()):
                    matched_windows.append({'title': title.strip(), 'size': size})
        
        if not matched_windows:
            print("No blackjack tables found. Detected windows:\n" + "\n".join([e.split('###')[0] for e in window_entries[:5]]))
            sys.exit(1)
            
        if len(matched_windows) > 1:
            root = tk.Tk()
            root.title("Select Blackjack Table")
            root.geometry("400x300")

            frame = ttk.Frame(root)
            frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

            tk.Label(frame, text="Multiple tables detected. Please select:", font=('Helvetica', 12)).pack()

            listbox = tk.Listbox(frame, height=10)
            listbox.pack(fill=tk.BOTH, expand=True)

            for idx, win in enumerate(matched_windows, 1):
                listbox.insert(tk.END, f"{idx}. {win['title']} ({win['size']})")

            selected_index = []

            def on_select():
                try:
                    selected_index.append(listbox.curselection()[0])
                    root.destroy()
                except IndexError:
                    pass

            ttk.Button(frame, text="Select", command=on_select).pack(pady=10)
            root.mainloop()

            if selected_index:
                return matched_windows[selected_index[0]]
            print("No selection made. Exiting.")
            sys.exit(0)

        return matched_windows[0]
        
    except subprocess.CalledProcessError as e:
        print(f"Window detection failed: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Error finding game window: {str(e)}")
        sys.exit(1)

def main():
    root = tk.Tk()
    app = BlackjackCounterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()