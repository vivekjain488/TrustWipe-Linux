#!/usr/bin/env python3
"""
TrustWipe SAFE - Secure Data Wiping Tool
SAFE GUI that prevents OS destruction and focuses on personal data
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import subprocess
import json
from datetime import datetime
import platform
import psutil
from safe_backend import SafeDataWiper
from safety_manager import SafetyManager
from certificate_generator import CertificateGenerator

class SafeTrustWipeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TrustWipe SAFE - Personal Data Wiping Tool 🔒")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a252f')
        
        # Variables
        self.wipe_type = tk.StringVar(value="personal_data")
        self.wipe_method = tk.StringVar(value="zeros")
        self.passes = tk.IntVar(value=3)
        self.selected_device = tk.StringVar()
        self.is_wiping = False
        self.wiper = None
        
        # Initialize components
        self.safety_manager = SafetyManager()
        self.cert_generator = CertificateGenerator()
        
        # Initialize UI
        self.create_widgets()
        self.check_root_privileges()
        
    def check_root_privileges(self):
        """Check if running with root privileges"""
        if os.geteuid() != 0:
            messagebox.showerror(
                "Insufficient Privileges", 
                "This application must be run with root privileges.\n\n"
                "Please run: sudo python3 safe_trustwipe.py"
            )
            sys.exit(1)
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg='#1a252f')
        title_frame.pack(fill='x', pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="🔒 TrustWipe SAFE",
            font=('Arial', 28, 'bold'),
            bg='#1a252f',
            fg='#27ae60'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Personal Data Wiping Tool - OS Protection Enabled",
            font=('Arial', 12),
            bg='#1a252f',
            fg='#95a5a6'
        )
        subtitle_label.pack()
        
        # Safety Notice
        safety_frame = tk.Frame(self.root, bg='#2c3e50', relief='raised', bd=2)
        safety_frame.pack(fill='x', padx=20, pady=10)
        
        safety_title = tk.Label(
            safety_frame,
            text="🛡️ SAFETY FEATURES ACTIVE",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#e74c3c'
        )
        safety_title.pack(pady=5)
        
        safety_text = tk.Label(
            safety_frame,
            text="• OS Protection: Cannot wipe system drives\n"
                 "• Smart Detection: Automatically identifies personal data\n"
                 "• Safe Operations: Only removes user files and data\n"
                 "• System Preserved: Your Linux installation stays intact",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            justify='left'
        )
        safety_text.pack(pady=5)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#1a252f')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Wipe Type Selection
        type_frame = tk.LabelFrame(
            main_frame,
            text="🎯 What to Wipe",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            relief='raised',
            bd=2
        )
        type_frame.pack(fill='x', pady=10)
        
        # Personal Data Option
        personal_radio = tk.Radiobutton(
            type_frame,
            text="🗂️ Personal Data Only (SAFE - Recommended)",
            variable=self.wipe_type,
            value="personal_data",
            font=('Arial', 11, 'bold'),
            bg='#34495e',
            fg='#27ae60',
            selectcolor='#2c3e50',
            command=self.on_type_change
        )
        personal_radio.pack(anchor='w', padx=10, pady=5)
        
        personal_desc = tk.Label(
            type_frame,
            text="   • Wipes: Documents, Downloads, Pictures, Videos, Browser data, Cache\n"
                 "   • Preserves: Operating System, Applications, System settings",
            font=('Arial', 9),
            bg='#34495e',
            fg='#95a5a6',
            justify='left'
        )
        personal_desc.pack(anchor='w', padx=10)
        
        # Factory Reset Option
        factory_radio = tk.Radiobutton(
            type_frame,
            text="🏭 Factory Reset (SAFE - Advanced)",
            variable=self.wipe_type,
            value="factory_reset",
            font=('Arial', 11, 'bold'),
            bg='#34495e',
            fg='#f39c12',
            selectcolor='#2c3e50',
            command=self.on_type_change
        )
        factory_radio.pack(anchor='w', padx=10, pady=5)
        
        factory_desc = tk.Label(
            type_frame,
            text="   • Wipes: All personal data + user accounts + network settings + logs\n"
                 "   • Preserves: Operating System, Applications, Core system files",
            font=('Arial', 9),
            bg='#34495e',
            fg='#95a5a6',
            justify='left'
        )
        factory_desc.pack(anchor='w', padx=10)
        
        # External Drive Option
        external_radio = tk.Radiobutton(
            type_frame,
            text="💾 External Drive (SAFE - With Protection)",
            variable=self.wipe_type,
            value="external_drive",
            font=('Arial', 11, 'bold'),
            bg='#34495e',
            fg='#e67e22',
            selectcolor='#2c3e50',
            command=self.on_type_change
        )
        external_radio.pack(anchor='w', padx=10, pady=5)
        
        external_desc = tk.Label(
            type_frame,
            text="   • Wipes: Complete external USB/disk drive\n"
                 "   • Protection: Automatic safety checks prevent OS wiping",
            font=('Arial', 9),
            bg='#34495e',
            fg='#95a5a6',
            justify='left'
        )
        external_desc.pack(anchor='w', padx=10)
        
        # Device Selection Frame (for external drives)
        self.device_frame = tk.LabelFrame(
            main_frame,
            text="💾 Select External Drive",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            relief='raised',
            bd=2
        )
        # Will be packed when external_drive is selected
        
        device_inner_frame = tk.Frame(self.device_frame, bg='#34495e')
        device_inner_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            device_inner_frame,
            text="Device:",
            font=('Arial', 10, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side='left')
        
        self.device_combo = ttk.Combobox(
            device_inner_frame,
            textvariable=self.selected_device,
            width=30,
            font=('Arial', 10)
        )
        self.device_combo.pack(side='left', padx=10)
        
        refresh_btn = tk.Button(
            device_inner_frame,
            text="🔄 Refresh",
            command=self.refresh_devices,
            bg='#3498db',
            fg='white',
            font=('Arial', 9, 'bold'),
            relief='raised'
        )
        refresh_btn.pack(side='left', padx=10)
        
        # Method Selection
        method_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ Wiping Method",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            relief='raised',
            bd=2
        )
        method_frame.pack(fill='x', pady=10)
        
        method_inner = tk.Frame(method_frame, bg='#34495e')
        method_inner.pack(fill='x', padx=10, pady=10)
        
        # Method options
        methods = [
            ("zeros", "🔢 Zeros (Fast)", "#27ae60"),
            ("random", "🎲 Random (Secure)", "#f39c12"),
            ("dod", "🛡️ DoD 5220.22-M (Military)", "#e74c3c")
        ]
        
        for value, text, color in methods:
            rb = tk.Radiobutton(
                method_inner,
                text=text,
                variable=self.wipe_method,
                value=value,
                font=('Arial', 10, 'bold'),
                bg='#34495e',
                fg=color,
                selectcolor='#2c3e50'
            )
            rb.pack(anchor='w', pady=2)
        
        # Progress Frame
        progress_frame = tk.LabelFrame(
            main_frame,
            text="📊 Progress",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            relief='raised',
            bd=2
        )
        progress_frame.pack(fill='x', pady=10)
        
        self.progress_var = tk.StringVar(value="Ready to wipe personal data safely")
        self.progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_var,
            font=('Arial', 10),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=500,
            mode='determinate'
        )
        self.progress_bar.pack(pady=5)
        
        # Control Buttons
        button_frame = tk.Frame(main_frame, bg='#1a252f')
        button_frame.pack(fill='x', pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="🚀 START SAFE WIPE",
            command=self.start_wipe,
            bg='#27ae60',
            fg='white',
            font=('Arial', 14, 'bold'),
            height=2,
            width=20,
            relief='raised',
            bd=3
        )
        self.start_button.pack(side='left', padx=10)
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹️ STOP",
            command=self.stop_wipe,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 14, 'bold'),
            height=2,
            width=15,
            relief='raised',
            state='disabled',
            bd=3
        )
        self.stop_button.pack(side='left', padx=10)
        
        # Certificate Button
        self.cert_button = tk.Button(
            button_frame,
            text="📜 Generate Certificate",
            command=self.generate_certificate,
            bg='#9b59b6',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2,
            width=18,
            relief='raised',
            state='disabled',
            bd=3
        )
        self.cert_button.pack(side='right', padx=10)
        
        # Initial setup
        self.on_type_change()
    
    def on_type_change(self):
        """Handle wipe type change"""
        if self.wipe_type.get() == "external_drive":
            self.device_frame.pack(fill='x', pady=10)
            self.refresh_devices()
        else:
            self.device_frame.pack_forget()
    
    def refresh_devices(self):
        """Refresh list of available devices"""
        try:
            devices = []
            
            # Get all block devices
            result = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME,SIZE,TYPE'], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.strip().split('\n'):
                if line and 'disk' in line:
                    parts = line.split()
                    device_name = parts[0]
                    device_size = parts[1] if len(parts) > 1 else "Unknown"
                    device_path = f"/dev/{device_name}"
                    
                    # Check if it's safe (not system drive)
                    safety_check = self.safety_manager.is_safe_for_wiping(device_path)
                    if safety_check['safe']:
                        devices.append(f"{device_path} ({device_size}) ✅ SAFE")
                    else:
                        devices.append(f"{device_path} ({device_size}) 🚨 SYSTEM DRIVE")
            
            self.device_combo['values'] = devices
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh devices: {e}")
    
    def start_wipe(self):
        """Start the wiping process"""
        if self.is_wiping:
            return
        
        # Validate selection
        if self.wipe_type.get() == "external_drive":
            if not self.selected_device.get():
                messagebox.showerror("Error", "Please select a device to wipe")
                return
            
            if "🚨 SYSTEM DRIVE" in self.selected_device.get():
                messagebox.showerror(
                    "SAFETY BLOCK", 
                    "Cannot wipe system drive!\n\n"
                    "This device contains your operating system.\n"
                    "Wiping it would destroy your Linux installation."
                )
                return
        
        # Confirmation dialog
        wipe_type_name = {
            "personal_data": "Personal Data",
            "factory_reset": "Factory Reset",
            "external_drive": "External Drive"
        }[self.wipe_type.get()]
        
        if not messagebox.askyesno(
            "Confirm Safe Wipe",
            f"🔒 Safe Wipe Confirmation\n\n"
            f"Type: {wipe_type_name}\n"
            f"Method: {self.wipe_method.get().upper()}\n\n"
            f"This operation is SAFE and will NOT damage your OS.\n\n"
            f"Continue?"
        ):
            return
        
        # Start wiping in thread
        self.is_wiping = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar['value'] = 0
        
        thread = threading.Thread(target=self.perform_wipe)
        thread.daemon = True
        thread.start()
    
    def perform_wipe(self):
        """Perform the actual wiping operation"""
        try:
            # Create wiper
            self.wiper = SafeDataWiper(
                wipe_type=self.wipe_type.get(),
                method=self.wipe_method.get(),
                passes=self.passes.get(),
                callback=self.update_progress
            )
            
            self.wiper.is_running = True
            
            # Perform wipe based on type
            if self.wipe_type.get() == "personal_data":
                success = self.wiper.wipe_personal_data_only()
            elif self.wipe_type.get() == "factory_reset":
                success = self.wiper.factory_reset_safe()
            elif self.wipe_type.get() == "external_drive":
                device_path = self.selected_device.get().split()[0]  # Extract device path
                success = self.wiper.wipe_external_drive(device_path)
            
            # Handle result
            self.root.after(100, lambda: self.wipe_completed(success))
            
        except Exception as e:
            error_msg = f"Wipe failed: {str(e)}"
            self.root.after(100, lambda: self.wipe_failed(error_msg))
    
    def update_progress(self, message, progress=None):
        """Update progress display"""
        def update_ui():
            self.progress_var.set(message)
            if progress is not None:
                self.progress_bar['value'] = progress
        
        self.root.after(100, update_ui)
    
    def wipe_completed(self, success):
        """Handle wipe completion"""
        self.is_wiping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        if success:
            self.progress_var.set("✅ Safe wipe completed successfully!")
            self.progress_bar['value'] = 100
            self.cert_button.config(state='normal')
            
            messagebox.showinfo(
                "Success",
                "🎉 Safe Wipe Completed!\n\n"
                "Your personal data has been securely wiped.\n"
                "Your operating system remains intact and functional.\n\n"
                "You can now generate a certificate of data erasure."
            )
        else:
            self.wipe_failed("Wipe operation failed")
    
    def wipe_failed(self, error_msg):
        """Handle wipe failure"""
        self.is_wiping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set(f"❌ {error_msg}")
        
        messagebox.showerror("Error", error_msg)
    
    def stop_wipe(self):
        """Stop the wiping process"""
        if self.wiper:
            self.wiper.stop()
        
        self.is_wiping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set("Wipe stopped by user")
    
    def generate_certificate(self):
        """Generate certificate of data erasure"""
        try:
            # Generate certificate
            cert_data = {
                'wipe_type': self.wipe_type.get(),
                'method': self.wipe_method.get(),
                'timestamp': datetime.now().isoformat(),
                'system_info': {
                    'hostname': platform.node(),
                    'os': platform.system(),
                    'version': platform.version()
                }
            }
            
            # Save JSON certificate
            json_file = f"trustwipe_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, 'w') as f:
                json.dump(cert_data, f, indent=2)
            
            # Generate HTML certificate
            html_file = self.cert_generator.generate_html_certificate(cert_data)
            
            messagebox.showinfo(
                "Certificate Generated",
                f"📜 Certificate of Data Erasure Generated!\n\n"
                f"JSON: {json_file}\n"
                f"HTML: {html_file}\n\n"
                f"These certificates verify that your data has been securely wiped."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate certificate: {e}")

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = SafeTrustWipeGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nExiting TrustWipe SAFE...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
