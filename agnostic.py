#!/usr/bin/env python3

"""
Description:
This script updates your IP address on the MyAnonamouse (MAM) website.
It provides a simple graphical interface for entering necessary information.
You can choose how the script gets your IP address: by entering it yourself, fetching it from a website, or from a Docker container.
The script works on Windows, macOS, and Linux.

Author: Your Name
Version: 1.2
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import subprocess
import sys
import os
import re
import json
import configparser

class MAMUpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MyAnonamouse IP Updater")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Initialize variables
        self.config_file = os.path.join(os.path.expanduser("~"), '.mam_updater_config.ini')
        self.settings = configparser.ConfigParser()
        self.load_settings()

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Style configuration
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('TEntry', font=('Arial', 10))

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # MAM Session Cookie
        mam_cookie_label = ttk.Label(main_frame, text="MAM Session Cookie:")
        mam_cookie_label.grid(row=0, column=0, sticky='e', pady=5)
        mam_cookie_label_ttp = CreateToolTip(mam_cookie_label, "Your IP or ASN locked session cookie from the MyAnonamouse website.\nThis is different from your browser session.\nSee the Help section for instructions on how to obtain it.")

        self.mam_cookie_entry = ttk.Entry(main_frame, width=50)
        self.mam_cookie_entry.grid(row=0, column=1, padx=5, pady=5)
        self.mam_cookie_entry.insert(0, self.settings.get('DEFAULT', 'mam_cookie', fallback=''))

        # IP Retrieval Method
        ip_method_label = ttk.Label(main_frame, text="How to Get Your IP Address:")
        ip_method_label.grid(row=1, column=0, sticky='e', pady=5)
        ip_method_label_ttp = CreateToolTip(ip_method_label, "Choose how the script should obtain your IP address.")

        self.ip_method_var = tk.StringVar(value=self.settings.get('DEFAULT', 'ip_method', fallback='Fetch from Website'))
        self.ip_method_menu = ttk.OptionMenu(main_frame, self.ip_method_var, self.ip_method_var.get(), "Enter Manually", "Fetch from Website", "From Docker Container", command=self.update_ip_method_fields)
        self.ip_method_menu.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # IP Retrieval Options Frames
        self.manual_ip_frame = ttk.Frame(main_frame)
        self.external_ip_frame = ttk.Frame(main_frame)
        self.docker_ip_frame = ttk.Frame(main_frame)

        # Manual IP Entry
        manual_ip_label = ttk.Label(self.manual_ip_frame, text="Your IP Address:")
        manual_ip_label.grid(row=0, column=0, sticky='e', pady=5)
        manual_ip_label_ttp = CreateToolTip(manual_ip_label, "Enter your IP address manually.\nExample: 123.45.67.89")

        self.manual_ip_entry = ttk.Entry(self.manual_ip_frame, width=50)
        self.manual_ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.manual_ip_entry.insert(0, self.settings.get('DEFAULT', 'manual_ip', fallback=''))

        # External IP Website
        external_ip_label = ttk.Label(self.external_ip_frame, text="Website to Fetch IP From:")
        external_ip_label.grid(row=0, column=0, sticky='e', pady=5)
        external_ip_label_ttp = CreateToolTip(external_ip_label, "The website that shows your IP address.\nDefault is the MyAnonamouse website.")

        self.external_ip_entry = ttk.Entry(self.external_ip_frame, width=50)
        self.external_ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.external_ip_entry.insert(0, self.settings.get('DEFAULT', 'external_ip_url', fallback='https://www.myanonamouse.net/myip.php'))

        # Docker Container Name
        container_name_label = ttk.Label(self.docker_ip_frame, text="Docker Container Name:")
        container_name_label.grid(row=0, column=0, sticky='e', pady=5)
        container_name_label_ttp = CreateToolTip(container_name_label, "The name of the Docker container to get the IP from.\nUseful if your application runs inside Docker.")

        self.container_name_entry = ttk.Entry(self.docker_ip_frame, width=50)
        self.container_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.container_name_entry.insert(0, self.settings.get('DEFAULT', 'container_name', fallback=''))

        # State Directory
        statedir_label = ttk.Label(main_frame, text="Where to Save Files:")
        statedir_label.grid(row=5, column=0, sticky='e', pady=5)
        statedir_label_ttp = CreateToolTip(statedir_label, "Choose a folder to save temporary files.\nThis can be any folder you have access to.")

        self.statedir_entry = ttk.Entry(main_frame, width=50)
        self.statedir_entry.grid(row=5, column=1, padx=5, pady=5)
        self.statedir_entry.insert(0, self.settings.get('DEFAULT', 'statedir', fallback=os.path.expanduser("~")))

        # Browse Button for State Directory
        self.statedir_browse_button = ttk.Button(main_frame, text="Browse", command=self.browse_statedir)
        self.statedir_browse_button.grid(row=5, column=2, padx=5, pady=5)

        # Run on Startup
        self.run_on_startup_var = tk.IntVar()
        self.run_on_startup_var.set(self.settings.getboolean('DEFAULT', 'run_on_startup', fallback=False))
        self.run_on_startup_check = ttk.Checkbutton(main_frame, text="Run on Startup", variable=self.run_on_startup_var, command=self.toggle_run_on_startup)
        self.run_on_startup_check.grid(row=7, column=1, padx=5, pady=5, sticky='w')
        run_on_startup_ttp = CreateToolTip(self.run_on_startup_check, "Check this box to run the IP updater automatically when your computer starts.")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)

        self.save_button = ttk.Button(button_frame, text="Save Settings", command=self.save_settings)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.update_button = ttk.Button(button_frame, text="Update IP Now", command=self.update_ip)
        self.update_button.pack(side=tk.LEFT, padx=5)

        # Help Button
        help_button = ttk.Button(main_frame, text="Help", command=self.show_help)
        help_button.grid(row=7, column=2, padx=5, pady=5)

        # Output Box
        output_label = ttk.Label(main_frame, text="Output Messages:")
        output_label.grid(row=9, column=0, sticky='nw', pady=5)
        self.output_text = tk.Text(main_frame, wrap=tk.WORD, height=10, width=70, state='disabled')
        self.output_text.grid(row=10, column=0, columnspan=3, padx=5, pady=5)
        output_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        output_scrollbar.grid(row=10, column=3, sticky='ns', pady=5)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

        # Initialize fields based on IP method
        self.update_ip_method_fields(self.ip_method_var.get())

    def show_help(self):
        help_text = """
Welcome to the MyAnonamouse IP Updater!

This tool helps you update your IP address on the MyAnonamouse (MAM) website, ensuring uninterrupted access.

**Important:** This tool requires a special MAM Session Cookie that is different from the one your browser uses.

**How to Obtain the Correct MAM Session Cookie:**

1. **Log into your MAM account:**
   - Go to https://www.myanonamouse.net and log in.

2. **Navigate to Security Settings:**
   - Click on your username at the top of the page.
   - Select "Edit Profile" or "Preferences."
   - Go to the "Security" tab.

3. **Create a New Session:**
   - Choose to create a new session.
   - Set the session type to **IP Locked** or **ASN Locked**.
   - Enable the option to **Allow Dynamic Seedbox IP Setting**.
   - Save the session.

4. **Copy the Session Cookie (`mam_id`):**
   - After creating the session, you'll receive a session identifier (`mam_id`).
   - Copy this value and paste it into the **MAM Session Cookie** field in the application.

---

**Steps to use this tool:**

1. **MAM Session Cookie:**
   - Paste the special `mam_id` value obtained from your MAM security settings.

2. **How to Get Your IP Address:**
   - **Enter Manually:** If you know your IP address, select this and type it in.
   - **Fetch from Website:** The tool will get your IP from a website.
     - Default website is MAM's own IP checker.
   - **From Docker Container:** If you're using Docker, the tool can get the IP from a container.
     - Enter the Docker container's name.

3. **Where to Save Files:**
   - Choose a folder where the tool can save temporary files.
   - This can be any folder you have access to.

4. **Run on Startup:**
   - Check this box if you want the tool to run automatically when your computer starts.

5. **Save Settings:**
   - Click this button to save your information for next time.

6. **Update IP Now:**
   - Click this button to update your IP on MAM immediately.

**Need more help?**
- Feel free to contact support or refer to the user guide for detailed instructions.
"""
        messagebox.showinfo("Help", help_text)

    def update_ip_method_fields(self, method):
        # Clear previous frames
        self.manual_ip_frame.grid_forget()
        self.external_ip_frame.grid_forget()
        self.docker_ip_frame.grid_forget()

        if method == "Enter Manually":
            self.manual_ip_frame.grid(row=2, column=0, columnspan=3, pady=5)
        elif method == "Fetch from Website":
            self.external_ip_frame.grid(row=2, column=0, columnspan=3, pady=5)
        elif method == "From Docker Container":
            self.docker_ip_frame.grid(row=2, column=0, columnspan=3, pady=5)

    def browse_statedir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.statedir_entry.delete(0, tk.END)
            self.statedir_entry.insert(0, directory)

    def load_settings(self):
        if os.path.exists(self.config_file):
            self.settings.read(self.config_file)
        else:
            self.settings['DEFAULT'] = {}

    def save_settings(self):
        self.settings['DEFAULT']['mam_cookie'] = self.mam_cookie_entry.get()
        self.settings['DEFAULT']['ip_method'] = self.ip_method_var.get()
        self.settings['DEFAULT']['manual_ip'] = self.manual_ip_entry.get() if self.ip_method_var.get() == 'Enter Manually' else ''
        self.settings['DEFAULT']['external_ip_url'] = self.external_ip_entry.get() if self.ip_method_var.get() == 'Fetch from Website' else ''
        self.settings['DEFAULT']['container_name'] = self.container_name_entry.get() if self.ip_method_var.get() == 'From Docker Container' else ''
        self.settings['DEFAULT']['statedir'] = self.statedir_entry.get()
        self.settings['DEFAULT']['url'] = 'https://t.myanonamouse.net/json/dynamicSeedbox.php'
        self.settings['DEFAULT']['run_on_startup'] = str(self.run_on_startup_var.get())

        with open(self.config_file, 'w') as configfile:
            self.settings.write(configfile)
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")

        # Update run on startup
        self.toggle_run_on_startup()

    def toggle_run_on_startup(self):
        run_on_startup = self.run_on_startup_var.get()
        if run_on_startup:
            self.set_run_on_startup()
        else:
            self.remove_run_on_startup()

    def set_run_on_startup(self):
        # Platform-specific implementation
        if sys.platform.startswith('win'):
            self.set_run_on_startup_windows()
        elif sys.platform.startswith('linux'):
            self.set_run_on_startup_linux()
        elif sys.platform.startswith('darwin'):
            self.set_run_on_startup_mac()
        else:
            messagebox.showwarning("Unsupported OS", "Run on startup is not supported on this operating system.")

    def remove_run_on_startup(self):
        # Platform-specific implementation
        if sys.platform.startswith('win'):
            self.remove_run_on_startup_windows()
        elif sys.platform.startswith('linux'):
            self.remove_run_on_startup_linux()
        elif sys.platform.startswith('darwin'):
            self.remove_run_on_startup_mac()

    def set_run_on_startup_windows(self):
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        script_path = os.path.abspath(sys.argv[0])
        shortcut_path = os.path.join(startup_folder, 'MAMUpdater.lnk')
        try:
            import winshell
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.IconLocation = script_path
            shortcut.save()
        except ImportError:
            messagebox.showerror("Module Missing", "Please install the 'winshell' and 'pywin32' modules to enable 'Run on Startup' on Windows.")
            self.run_on_startup_var.set(0)

    def remove_run_on_startup_windows(self):
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, 'MAMUpdater.lnk')
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

    def set_run_on_startup_linux(self):
        autostart_dir = os.path.join(os.path.expanduser('~'), '.config', 'autostart')
        os.makedirs(autostart_dir, exist_ok=True)
        desktop_entry = os.path.join(autostart_dir, 'MAMUpdater.desktop')
        script_path = os.path.abspath(sys.argv[0])
        with open(desktop_entry, 'w') as f:
            f.write(f"""[Desktop Entry]
Type=Application
Exec=python3 "{script_path}"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=MAM IP Updater
Comment=Updates the IP address on MyAnonamouse
""")

    def remove_run_on_startup_linux(self):
        autostart_dir = os.path.join(os.path.expanduser('~'), '.config', 'autostart')
        desktop_entry = os.path.join(autostart_dir, 'MAMUpdater.desktop')
        if os.path.exists(desktop_entry):
            os.remove(desktop_entry)

    def set_run_on_startup_mac(self):
        # macOS implementation requires creating a Launch Agent
        launch_agents_dir = os.path.join(os.path.expanduser('~'), 'Library', 'LaunchAgents')
        os.makedirs(launch_agents_dir, exist_ok=True)
        plist_path = os.path.join(launch_agents_dir, 'com.mam.updater.plist')
        script_path = os.path.abspath(sys.argv[0])
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
         "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mam.updater</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        with open(plist_path, 'w') as f:
            f.write(plist_content)

    def remove_run_on_startup_mac(self):
        launch_agents_dir = os.path.join(os.path.expanduser('~'), 'Library', 'LaunchAgents')
        plist_path = os.path.join(launch_agents_dir, 'com.mam.updater.plist')
        if os.path.exists(plist_path):
            os.remove(plist_path)

    def update_ip(self):
        mam_cookie = self.mam_cookie_entry.get().strip()
        ip_method = self.ip_method_var.get()
        statedir = self.statedir_entry.get().strip()
        url = 'https://t.myanonamouse.net/json/dynamicSeedbox.php'

        if not mam_cookie or not statedir:
            self.append_output("Error: Please fill in all required fields marked with *.\n")
            return

        cachefile = os.path.join(statedir, 'MAM.ip')
        cookiefile = os.path.join(statedir, 'MAM.cookie')

        # Ensure the state directory exists
        try:
            os.makedirs(statedir, exist_ok=True)
        except Exception as e:
            self.append_output(f"Error creating directory '{statedir}': {e}\n")
            return

        # Retrieve the current IP address based on the selected method
        if ip_method == "Enter Manually":
            current_ip = self.manual_ip_entry.get().strip()
            if not current_ip:
                self.append_output("Error: Please enter your IP address.\n")
                return
        elif ip_method == "Fetch from Website":
            external_ip_url = self.external_ip_entry.get().strip()
            current_ip = self.get_external_ip(external_ip_url)
            if not current_ip:
                return
        elif ip_method == "From Docker Container":
            container_name = self.container_name_entry.get().strip()
            if not container_name:
                self.append_output("Error: Please enter the Docker container name.\n")
                return
            current_ip = self.get_docker_ip(container_name)
            if not current_ip:
                return
        else:
            self.append_output("Error: Invalid IP retrieval method selected.\n")
            return

        # Update MAM.ip file regardless of IP change
        try:
            with open(cachefile, 'w') as f:
                f.write(current_ip)
        except Exception as e:
            self.append_output(f"Error writing to file '{cachefile}': {e}\n")
            return

        # Create the cookie file with the special session cookie
        try:
            with open(cookiefile, 'w') as f:
                f.write(f"""# Netscape HTTP Cookie File
# This file was generated by the MAM IP Updater script
.t.myanonamouse.net\tTRUE\t/\tFALSE\t0\tmam_id\t{mam_cookie}
""")
        except Exception as e:
            self.append_output(f"Error creating file '{cookiefile}': {e}\n")
            return

        # Update the dynamic seedbox IP
        success, message = self.update_seedbox_ip(mam_cookie, cookiefile, url)
        self.append_output(message + "\n")

    def get_external_ip(self, external_ip_url):
        try:
            result = subprocess.run(['curl', '-s', external_ip_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            response = result.stdout.strip()
            if not response:
                self.append_output("Error: Failed to retrieve IP address from the website.\n")
                return None

            # Extract IP address using regex
            ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', response)
            if ip_match:
                current_ip = ip_match.group(0)
                return current_ip
            else:
                self.append_output("Error: No valid IP address found in the website's response.\n")
                return None
        except subprocess.CalledProcessError as e:
            self.append_output(f"Error retrieving IP address: {e}\n")
            return None

    def get_docker_ip(self, container_name):
        try:
            result = subprocess.run(['docker', 'exec', container_name, 'curl', '-s', 'https://www.myanonamouse.net/myip.php'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            response = result.stdout.strip()
            if not response:
                self.append_output(f"Error: Failed to retrieve IP address from Docker container '{container_name}'.\n")
                return None

            # Extract IP address using regex
            ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', response)
            if ip_match:
                current_ip = ip_match.group(0)
                return current_ip
            else:
                self.append_output("Error: No valid IP address found in the container's response.\n")
                return None
        except subprocess.CalledProcessError as e:
            self.append_output(f"Error retrieving IP address: {e}\n")
            return None

    def update_seedbox_ip(self, mam_cookie, cookiefile, url):
        try:
            command = [
                'curl', '-s',
                '-b', f"mam_id={mam_cookie}",
                '-c', cookiefile,
                url
            ]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            response = result.stdout.strip()
            if not response:
                return False, "Error: Failed to get a response from the MyAnonamouse website."
            response_json = json.loads(response)
            success = response_json.get('Success')
            message = response_json.get('msg')
            if success == True:
                return True, f"Success: {message}"
            else:
                return False, f"Failed: {message}"
        except subprocess.CalledProcessError as e:
            return False, f"Error updating IP address: {e}"
        except json.JSONDecodeError:
            return False, "Error: Received invalid response from the MyAnonamouse website."

    def append_output(self, text):
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.configure(state='disabled')
        self.output_text.see(tk.END)

class CreateToolTip(object):
    """
    Create a tooltip for a given widget.
    """
    def __init__(self, widget, text='Widget info'):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)

    def show_tooltip(self, _event):
        x = self.widget.winfo_rootx() + 50
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Removes the window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, background="lightyellow", relief='solid', borderwidth=1, wraplength=300)
        label.pack(ipadx=1)

    def hide_tooltip(self, _event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

if __name__ == '__main__':
    root = tk.Tk()
    app = MAMUpdaterApp(root)
    root.mainloop()
