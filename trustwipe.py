#!/usr/bin/env python3
"""
TrustWipe - Secure Data Wiping Tool
Main application entry point with GUI frontend
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
import hashlib
import uuid

class TrustWipeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TrustWipe - Secure Data Wiping Tool")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.selected_device = tk.StringVar()
        self.wipe_method = tk.StringVar(value="zeros")
        self.passes = tk.IntVar(value=3)
        self.is_wiping = False
        
        # Initialize UI
        self.create_widgets()
        self.check_root_privileges()
        self.refresh_devices()
        
    def check_root_privileges(self):
        """Check if running with root privileges"""
        if os.geteuid() != 0:
            messagebox.showerror(
                "Insufficient Privileges", 
                "This application must be run with root privileges.\n\n"
                "Please run: sudo python3 trustwipe.py"
            )
            sys.exit(1)
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="TrustWipe - Secure Data Wiping Tool",
            font=('Arial', 18, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Device selection frame
        device_frame = tk.LabelFrame(
            main_frame, 
            text="1. Select Device to Wipe",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            padx=10,
            pady=10
        )
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.device_listbox = tk.Listbox(
            device_frame,
            height=5,
            font=('Courier', 10),
            bg='#ecf0f1',
            selectmode=tk.SINGLE
        )
        self.device_listbox.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = tk.Button(
            device_frame,
            text="Refresh Devices",
            command=self.refresh_devices,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20
        )
        refresh_btn.pack()
        
        # Wiping options frame
        options_frame = tk.LabelFrame(
            main_frame,
            text="2. Wiping Options",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            padx=10,
            pady=10
        )
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Method selection
        method_frame = tk.Frame(options_frame, bg='#34495e')
        method_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            method_frame,
            text="Wiping Method:",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        ).pack(anchor=tk.W)
        
        methods = [
            ("Zeros (0x00)", "zeros", "Fast - overwrites with zeros"),
            ("Random Data", "random", "Secure - overwrites with random data"),
            ("DoD 5220.22-M", "dod", "Military standard - 3 passes"),
            ("Gutmann (35 passes)", "gutmann", "Most secure - 35 passes")
        ]
        
        for text, value, desc in methods:
            frame = tk.Frame(method_frame, bg='#34495e')
            frame.pack(anchor=tk.W, pady=2)
            
            tk.Radiobutton(
                frame,
                text=text,
                variable=self.wipe_method,
                value=value,
                font=('Arial', 10),
                fg='#ecf0f1',
                bg='#34495e',
                selectcolor='#2c3e50',
                activebackground='#34495e',
                activeforeground='#ecf0f1'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                frame,
                text=f"- {desc}",
                font=('Arial', 9),
                fg='#bdc3c7',
                bg='#34495e'
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Passes selection
        passes_frame = tk.Frame(options_frame, bg='#34495e')
        passes_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            passes_frame,
            text="Number of Passes:",
            font=('Arial', 10, 'bold'),
            fg='#ecf0f1',
            bg='#34495e'
        ).pack(side=tk.LEFT)
        
        passes_spinbox = tk.Spinbox(
            passes_frame,
            from_=1,
            to=35,
            textvariable=self.passes,
            width=5,
            font=('Arial', 10)
        )
        passes_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress frame
        progress_frame = tk.LabelFrame(
            main_frame,
            text="3. Progress",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            padx=10,
            pady=10
        )
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_var = tk.StringVar(value="Ready to wipe...")
        self.progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_var,
            font=('Arial', 10),
            fg='#ecf0f1',
            bg='#34495e'
        )
        self.progress_label.pack(pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg='#2c3e50')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.wipe_btn = tk.Button(
            control_frame,
            text="START WIPING",
            command=self.start_wiping,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=10
        )
        self.wipe_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(
            control_frame,
            text="EMERGENCY STOP",
            command=self.emergency_stop,
            bg='#f39c12',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        certificate_btn = tk.Button(
            control_frame,
            text="View Certificates",
            command=self.view_certificates,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=10
        )
        certificate_btn.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=('Arial', 9),
            fg='#95a5a6',
            bg='#2c3e50',
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def refresh_devices(self):
        """Refresh the list of available storage devices"""
        try:
            self.device_listbox.delete(0, tk.END)
            
            # Get block devices
            result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,TYPE,MODEL'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3 and parts[2] == 'disk':
                            device_info = f"/dev/{parts[0]} - {parts[1]}"
                            if len(parts) > 3:
                                device_info += f" - {' '.join(parts[3:])}"
                            self.device_listbox.insert(tk.END, device_info)
            
            self.status_var.set(f"Found {self.device_listbox.size()} storage devices")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh devices: {str(e)}")
    
    def start_wiping(self):
        """Start the wiping process"""
        # Get selected device
        selection = self.device_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a device to wipe")
            return
        
        device_info = self.device_listbox.get(selection[0])
        device_path = device_info.split(' - ')[0]
        
        # Confirmation dialog
        confirm = messagebox.askyesno(
            "DESTRUCTIVE OPERATION",
            f"WARNING: This will permanently erase ALL data on:\n\n"
            f"{device_info}\n\n"
            f"Method: {self.wipe_method.get()}\n"
            f"Passes: {self.passes.get()}\n\n"
            f"This operation CANNOT be undone!\n\n"
            f"Are you absolutely sure?",
            icon='warning'
        )
        
        if not confirm:
            return
        
        # Second confirmation
        confirm2 = messagebox.askyesno(
            "FINAL CONFIRMATION",
            f"LAST CHANCE!\n\n"
            f"About to wipe: {device_path}\n\n"
            f"Type 'YES' in the next dialog to proceed.",
            icon='warning'
        )
        
        if not confirm2:
            return
        
        # Text confirmation
        confirm_text = tk.simpledialog.askstring(
            "Type Confirmation",
            f"Type 'WIPE {device_path.split('/')[-1].upper()}' to confirm:"
        )
        
        expected = f"WIPE {device_path.split('/')[-1].upper()}"
        if confirm_text != expected:
            messagebox.showerror("Cancelled", "Confirmation text didn't match. Operation cancelled.")
            return
        
        # Start wiping in separate thread
        self.is_wiping = True
        self.wipe_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()
        
        wipe_thread = threading.Thread(
            target=self.perform_wipe,
            args=(device_path,),
            daemon=True
        )
        wipe_thread.start()
    
    def perform_wipe(self, device_path):
        """Perform the actual wiping operation"""
        try:
            # Get system information before wiping
            system_info = self.get_system_info()
            device_info = self.get_device_info(device_path)
            
            wipe_started = datetime.now()
            
            self.progress_var.set(f"Starting optimized wipe of {device_path}...")
            
            # Create progress callback for real-time updates
            def progress_callback(message, progress=None):
                self.progress_var.set(message)
                if progress is not None:
                    self.progress_bar.config(mode='determinate', value=progress)
                self.root.update()  # Force GUI update
            
            # Import backend and create optimized wiper
            from backend import DataWiper
            wiper = DataWiper(device_path, self.wipe_method.get(), self.passes.get(), progress_callback)
            
            # Start wiping with progress monitoring
            success = wiper.wipe()
            
            if not success:
                raise Exception("Wipe operation failed")
            
            wipe_completed = datetime.now()
            
            # Generate certificate
            cert_data = {
                'system_info': system_info,
                'device_info': device_info,
                'wipe_details': {
                    'device_path': device_path,
                    'method': self.wipe_method.get(),
                    'passes': self.passes.get(),
                    'start_time': wipe_started.isoformat(),
                    'end_time': wipe_completed.isoformat(),
                    'duration': str(wipe_completed - wipe_started),
                    'status': 'SUCCESS'
                },
                'certificate_id': str(uuid.uuid4()),
                'generated_at': datetime.now().isoformat()
            }
            
            self.generate_certificate(cert_data)
            
            self.progress_var.set("Wipe completed successfully!")
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate', value=100)
            
            messagebox.showinfo(
                "Wipe Complete",
                f"Data wiping completed successfully!\n\n"
                f"Device: {device_path}\n"
                f"Duration: {wipe_completed - wipe_started}\n\n"
                f"Certificate generated and stored in /boot/trustwipe-certificates/"
            )
            
        except Exception as e:
            self.progress_var.set(f"Error: {str(e)}")
            self.progress_bar.stop()
            messagebox.showerror("Wipe Error", f"Wiping failed: {str(e)}")
        
        finally:
            self.is_wiping = False
            self.wipe_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def wipe_with_zeros(self, device_path):
        """Wipe device with zeros"""
        for pass_num in range(self.passes.get()):
            if not self.is_wiping:
                break
                
            self.progress_var.set(f"Pass {pass_num + 1}/{self.passes.get()}: Writing zeros...")
            
            cmd = ['dd', f'if=/dev/zero', f'of={device_path}', 'bs=1M', 'status=progress']
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
            process.wait()
            
            if process.returncode != 0:
                raise Exception(f"dd command failed: {process.stderr.read()}")
    
    def wipe_with_random(self, device_path):
        """Wipe device with random data"""
        for pass_num in range(self.passes.get()):
            if not self.is_wiping:
                break
                
            self.progress_var.set(f"Pass {pass_num + 1}/{self.passes.get()}: Writing random data...")
            
            cmd = ['dd', f'if=/dev/urandom', f'of={device_path}', 'bs=1M', 'status=progress']
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
            process.wait()
            
            if process.returncode != 0:
                raise Exception(f"dd command failed: {process.stderr.read()}")
    
    def wipe_with_dod(self, device_path):
        """Wipe device using DoD 5220.22-M standard"""
        patterns = [b'\x00', b'\xFF', b'\x55']  # 0x00, 0xFF, random
        
        for pass_num, pattern in enumerate(patterns):
            if not self.is_wiping:
                break
                
            self.progress_var.set(f"DoD Pass {pass_num + 1}/3: Pattern {pattern.hex()}...")
            
            if pattern == b'\x55':  # Use random for third pass
                cmd = ['dd', f'if=/dev/urandom', f'of={device_path}', 'bs=1M', 'status=progress']
            else:
                # Create pattern file
                pattern_file = f'/tmp/pattern_{pattern.hex()}'
                with open(pattern_file, 'wb') as f:
                    f.write(pattern * 1024 * 1024)  # 1MB of pattern
                
                cmd = ['dd', f'if={pattern_file}', f'of={device_path}', 'bs=1M', 'status=progress']
            
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
            process.wait()
            
            if process.returncode != 0:
                raise Exception(f"dd command failed: {process.stderr.read()}")
    
    def wipe_with_gutmann(self, device_path):
        """Wipe device using Gutmann method (35 passes)"""
        self.progress_var.set("Starting Gutmann 35-pass wipe...")
        
        cmd = ['shred', '-v', '-n', '35', '-z', device_path]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        while process.poll() is None:
            if not self.is_wiping:
                process.terminate()
                break
        
        if process.returncode != 0:
            raise Exception(f"shred command failed: {process.stderr.read()}")
    
    def emergency_stop(self):
        """Emergency stop for wiping operation"""
        if messagebox.askyesno("Emergency Stop", "Are you sure you want to stop the wiping operation?"):
            self.is_wiping = False
            self.progress_var.set("Emergency stop requested...")
            # Note: This may not immediately stop dd/shred processes
    
    def get_system_info(self):
        """Collect comprehensive system information"""
        try:
            return {
                'hostname': platform.node(),
                'os': platform.system(),
                'os_release': platform.release(),
                'os_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
                'kernel_version': platform.release(),
                'python_version': platform.python_version()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_device_info(self, device_path):
        """Get detailed information about the device"""
        try:
            info = {}
            
            # Get device size
            try:
                result = subprocess.run(['blockdev', '--getsize64', device_path], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    info['size_bytes'] = int(result.stdout.strip())
                    info['size_human'] = self.human_readable_size(info['size_bytes'])
            except:
                pass
            
            # Get device model and serial
            try:
                device_name = device_path.split('/')[-1]
                with open(f'/sys/block/{device_name}/device/model', 'r') as f:
                    info['model'] = f.read().strip()
            except:
                pass
            
            try:
                device_name = device_path.split('/')[-1]
                with open(f'/sys/block/{device_name}/device/serial', 'r') as f:
                    info['serial'] = f.read().strip()
            except:
                pass
            
            return info
        except Exception as e:
            return {'error': str(e)}
    
    def human_readable_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def generate_certificate(self, cert_data):
        """Generate a certificate after successful wipe"""
        try:
            # Ensure certificate directory exists
            cert_dir = '/boot/trustwipe-certificates'
            os.makedirs(cert_dir, exist_ok=True)
            
            # Generate certificate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            device_name = cert_data['wipe_details']['device_path'].split('/')[-1]
            cert_filename = f'trustwipe_cert_{device_name}_{timestamp}.json'
            cert_path = os.path.join(cert_dir, cert_filename)
            
            # Save certificate
            with open(cert_path, 'w') as f:
                json.dump(cert_data, f, indent=2)
            
            # Generate human-readable certificate
            html_cert = self.generate_html_certificate(cert_data)
            html_path = cert_path.replace('.json', '.html')
            with open(html_path, 'w') as f:
                f.write(html_cert)
            
            # Set permissions
            os.chmod(cert_path, 0o644)
            os.chmod(html_path, 0o644)
            
            self.status_var.set(f"Certificate saved: {cert_path}")
            
        except Exception as e:
            messagebox.showerror("Certificate Error", f"Failed to generate certificate: {str(e)}")
    
    def generate_html_certificate(self, cert_data):
        """Generate HTML certificate"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>TrustWipe Data Erasure Certificate</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .certificate {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 20px; margin-bottom: 30px; }}
        .title {{ color: #e74c3c; font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
        .subtitle {{ color: #666; font-size: 16px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-left: 4px solid #3498db; padding-left: 10px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 2fr; gap: 10px; }}
        .info-label {{ font-weight: bold; color: #555; }}
        .info-value {{ color: #333; }}
        .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; text-align: center; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="certificate">
        <div class="header">
            <div class="title">🔒 DATA ERASURE CERTIFICATE</div>
            <div class="subtitle">TrustWipe Secure Data Wiping Tool</div>
        </div>
        
        <div class="success">
            ✅ DATA ERASED SUCCESSFULLY
        </div>
        
        <div class="section">
            <div class="section-title">Erasure Details</div>
            <div class="info-grid">
                <div class="info-label">Device:</div>
                <div class="info-value">{cert_data['wipe_details']['device_path']}</div>
                <div class="info-label">Method:</div>
                <div class="info-value">{cert_data['wipe_details']['method'].upper()}</div>
                <div class="info-label">Passes:</div>
                <div class="info-value">{cert_data['wipe_details']['passes']}</div>
                <div class="info-label">Started:</div>
                <div class="info-value">{cert_data['wipe_details']['start_time']}</div>
                <div class="info-label">Completed:</div>
                <div class="info-value">{cert_data['wipe_details']['end_time']}</div>
                <div class="info-label">Duration:</div>
                <div class="info-value">{cert_data['wipe_details']['duration']}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">System Information</div>
            <div class="info-grid">
                <div class="info-label">Hostname:</div>
                <div class="info-value">{cert_data['system_info'].get('hostname', 'N/A')}</div>
                <div class="info-label">Operating System:</div>
                <div class="info-value">{cert_data['system_info'].get('os', 'N/A')} {cert_data['system_info'].get('os_release', '')}</div>
                <div class="info-label">Architecture:</div>
                <div class="info-value">{cert_data['system_info'].get('architecture', 'N/A')}</div>
                <div class="info-label">CPU Cores:</div>
                <div class="info-value">{cert_data['system_info'].get('cpu_count', 'N/A')}</div>
                <div class="info-label">Memory:</div>
                <div class="info-value">{self.human_readable_size(cert_data['system_info'].get('memory_total', 0))}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Device Information</div>
            <div class="info-grid">
                <div class="info-label">Size:</div>
                <div class="info-value">{cert_data['device_info'].get('size_human', 'N/A')}</div>
                <div class="info-label">Model:</div>
                <div class="info-value">{cert_data['device_info'].get('model', 'N/A')}</div>
                <div class="info-label">Serial:</div>
                <div class="info-value">{cert_data['device_info'].get('serial', 'N/A')}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Certificate Information</div>
            <div class="info-grid">
                <div class="info-label">Certificate ID:</div>
                <div class="info-value">{cert_data['certificate_id']}</div>
                <div class="info-label">Generated:</div>
                <div class="info-value">{cert_data['generated_at']}</div>
            </div>
        </div>
        
        <div class="footer">
            This certificate confirms that the specified data storage device has been securely erased<br>
            using industry-standard wiping algorithms. The data is unrecoverable.<br><br>
            Generated by TrustWipe v1.0
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def view_certificates(self):
        """Open certificate directory"""
        cert_dir = '/boot/trustwipe-certificates'
        if os.path.exists(cert_dir):
            try:
                subprocess.run(['xdg-open', cert_dir])
            except:
                messagebox.showinfo("Certificates", f"Certificates are stored in: {cert_dir}")
        else:
            messagebox.showinfo("No Certificates", "No certificates found. Complete a wipe operation first.")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = TrustWipeGUI(root)
    
    # Handle window close
    def on_closing():
        if app.is_wiping:
            if messagebox.askokcancel("Quit", "Wiping operation is in progress. Do you want to quit?"):
                app.is_wiping = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
