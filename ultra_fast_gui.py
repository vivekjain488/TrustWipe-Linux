#!/usr/bin/env python3
"""
TrustWipe ULTRA-FAST GUI - Optimized for 5GB /dev/sdb
Lightning-fast wiping with real-time performance monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
from datetime import datetime

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ultra_fast_backend import UltraFastDataWiper, ultra_fast_wipe_sdb
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure ultra_fast_backend.py is in the same directory")
    sys.exit(1)

class UltraFastTrustWipeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ TrustWipe ULTRA-FAST - 5GB SDB Optimizer")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0a0a0a')
        
        # Variables
        self.wipe_method = tk.StringVar(value="lightning")
        self.target_device = tk.StringVar(value="/dev/sdb")
        self.is_wiping = False
        self.wiper = None
        self.start_time = None
        
        # Performance tracking
        self.bytes_written = 0
        self.current_speed = 0
        self.peak_speed = 0
        
        # Create the ultra-fast UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create ultra-fast optimized UI"""
        # Title with neon effect
        title_frame = tk.Frame(self.root, bg='#0a0a0a')
        title_frame.pack(fill='x', pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="⚡ TrustWipe ULTRA-FAST ⚡",
            font=('Arial', 32, 'bold'),
            bg='#0a0a0a',
            fg='#00ff41'  # Matrix green
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="5GB /dev/sdb Wiper - Target: Under 30 seconds!",
            font=('Arial', 14, 'bold'),
            bg='#0a0a0a',
            fg='#ffff00'  # Bright yellow
        )
        subtitle_label.pack()
        
        # Speed indicator
        speed_frame = tk.Frame(self.root, bg='#1a1a1a', relief='raised', bd=2)
        speed_frame.pack(fill='x', padx=20, pady=10)
        
        speed_title = tk.Label(
            speed_frame,
            text="🚀 PERFORMANCE MONITOR",
            font=('Arial', 16, 'bold'),
            bg='#1a1a1a',
            fg='#ff0080'
        )
        speed_title.pack(pady=5)
        
        # Performance metrics
        metrics_frame = tk.Frame(speed_frame, bg='#1a1a1a')
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        # Current speed
        self.speed_var = tk.StringVar(value="0.0 MB/s")
        speed_label = tk.Label(
            metrics_frame,
            text="Current Speed:",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#ffffff'
        )
        speed_label.pack(side='left')
        
        self.speed_display = tk.Label(
            metrics_frame,
            textvariable=self.speed_var,
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#00ff41'
        )
        self.speed_display.pack(side='left', padx=10)
        
        # Peak speed
        self.peak_speed_var = tk.StringVar(value="0.0 MB/s")
        peak_label = tk.Label(
            metrics_frame,
            text="Peak Speed:",
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#ffffff'
        )
        peak_label.pack(side='left', padx=(50, 0))
        
        self.peak_speed_display = tk.Label(
            metrics_frame,
            textvariable=self.peak_speed_var,
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#ff4500'  # Orange red
        )
        self.peak_speed_display.pack(side='left', padx=10)
        
        # ETA and time
        time_frame = tk.Frame(speed_frame, bg='#1a1a1a')
        time_frame.pack(fill='x', padx=10, pady=5)
        
        self.eta_var = tk.StringVar(value="ETA: --")
        eta_label = tk.Label(
            time_frame,
            textvariable=self.eta_var,
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#ffff00'
        )
        eta_label.pack(side='left')
        
        self.elapsed_var = tk.StringVar(value="Elapsed: 0s")
        elapsed_label = tk.Label(
            time_frame,
            textvariable=self.elapsed_var,
            font=('Arial', 12, 'bold'),
            bg='#1a1a1a',
            fg='#40e0d0'  # Turquoise
        )
        elapsed_label.pack(side='right')
        
        # Method selection with speed ratings
        method_frame = tk.LabelFrame(
            self.root,
            text="⚡ ULTRA-FAST METHODS",
            font=('Arial', 14, 'bold'),
            bg='#2a2a2a',
            fg='#00ff41',
            relief='raised',
            bd=3
        )
        method_frame.pack(fill='x', padx=20, pady=10)
        
        # Lightning method (fastest)
        lightning_frame = tk.Frame(method_frame, bg='#2a2a2a')
        lightning_frame.pack(fill='x', padx=10, pady=5)
        
        lightning_radio = tk.Radiobutton(
            lightning_frame,
            text="⚡ LIGHTNING WIPE",
            variable=self.wipe_method,
            value="lightning",
            font=('Arial', 14, 'bold'),
            bg='#2a2a2a',
            fg='#ffff00',
            selectcolor='#1a1a1a',
            activebackground='#3a3a3a'
        )
        lightning_radio.pack(side='left')
        
        lightning_speed = tk.Label(
            lightning_frame,
            text="🚀 FASTEST - Memory Buffer Method - 5GB in ~15-20 seconds",
            font=('Arial', 10, 'bold'),
            bg='#2a2a2a',
            fg='#ff4500'
        )
        lightning_speed.pack(side='right')
        
        # Zero method (fast)
        zero_frame = tk.Frame(method_frame, bg='#2a2a2a')
        zero_frame.pack(fill='x', padx=10, pady=5)
        
        zero_radio = tk.Radiobutton(
            zero_frame,
            text="🔢 ULTRA-FAST ZEROS",
            variable=self.wipe_method,
            value="zeros",
            font=('Arial', 14, 'bold'),
            bg='#2a2a2a',
            fg='#00ff41',
            selectcolor='#1a1a1a',
            activebackground='#3a3a3a'
        )
        zero_radio.pack(side='left')
        
        zero_speed = tk.Label(
            zero_frame,
            text="💨 VERY FAST - Optimized DD with 512MB blocks - 5GB in ~25-30 seconds",
            font=('Arial', 10, 'bold'),
            bg='#2a2a2a',
            fg='#40e0d0'
        )
        zero_speed.pack(side='right')
        
        # Random method (secure + fast)
        random_frame = tk.Frame(method_frame, bg='#2a2a2a')
        random_frame.pack(fill='x', padx=10, pady=5)
        
        random_radio = tk.Radiobutton(
            random_frame,
            text="🎲 PARALLEL RANDOM",
            variable=self.wipe_method,
            value="random",
            font=('Arial', 14, 'bold'),
            bg='#2a2a2a',
            fg='#ff0080',
            selectcolor='#1a1a1a',
            activebackground='#3a3a3a'
        )
        random_radio.pack(side='left')
        
        random_speed = tk.Label(
            random_frame,
            text="🧵 MULTI-THREADED - 8 parallel threads - 5GB in ~45-60 seconds",
            font=('Arial', 10, 'bold'),
            bg='#2a2a2a',
            fg='#da70d6'
        )
        random_speed.pack(side='right')
        
        # Device info
        device_frame = tk.LabelFrame(
            self.root,
            text="🎯 TARGET DEVICE",
            font=('Arial', 14, 'bold'),
            bg='#2a2a2a',
            fg='#00ff41',
            relief='raised',
            bd=3
        )
        device_frame.pack(fill='x', padx=20, pady=10)
        
        device_info = tk.Label(
            device_frame,
            text="🎯 Target: /dev/sdb (5GB) | 💾 VMware Optimized | 🚀 Maximum Performance Mode",
            font=('Arial', 12, 'bold'),
            bg='#2a2a2a',
            fg='#ffffff'
        )
        device_info.pack(pady=10)
        
        # Progress section
        progress_frame = tk.LabelFrame(
            self.root,
            text="📊 ULTRA-FAST PROGRESS",
            font=('Arial', 14, 'bold'),
            bg='#2a2a2a',
            fg='#00ff41',
            relief='raised',
            bd=3
        )
        progress_frame.pack(fill='x', padx=20, pady=10)
        
        # Status display
        self.status_var = tk.StringVar(value="🚀 Ready for ULTRA-FAST wipe!")
        self.status_label = tk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=('Arial', 12, 'bold'),
            bg='#2a2a2a',
            fg='#ffff00'
        )
        self.status_label.pack(pady=5)
        
        # High-speed progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "UltraFast.Horizontal.TProgressbar",
            background='#00ff41',
            troughcolor='#1a1a1a',
            bordercolor='#00ff41',
            lightcolor='#00ff41',
            darkcolor='#00ff41'
        )
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=700,
            mode='determinate',
            style="UltraFast.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(pady=10)
        
        # Progress percentage
        self.progress_percent = tk.Label(
            progress_frame,
            text="0%",
            font=('Arial', 16, 'bold'),
            bg='#2a2a2a',
            fg='#00ff41'
        )
        self.progress_percent.pack()
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#0a0a0a')
        button_frame.pack(fill='x', pady=20)
        
        # Ultra-fast start button
        self.start_button = tk.Button(
            button_frame,
            text="⚡ START ULTRA-FAST WIPE ⚡",
            command=self.start_ultra_fast_wipe,
            bg='#ff4500',
            fg='white',
            font=('Arial', 16, 'bold'),
            height=3,
            width=25,
            relief='raised',
            bd=5,
            activebackground='#ff6500'
        )
        self.start_button.pack(side='left', padx=20)
        
        # Benchmark button
        self.benchmark_button = tk.Button(
            button_frame,
            text="🏁 SPEED BENCHMARK",
            command=self.run_benchmark,
            bg='#4169e1',
            fg='white',
            font=('Arial', 14, 'bold'),
            height=3,
            width=20,
            relief='raised',
            bd=5,
            activebackground='#5a7ae1'
        )
        self.benchmark_button.pack(side='left', padx=20)
        
        # Stop button
        self.stop_button = tk.Button(
            button_frame,
            text="⏹️ EMERGENCY STOP",
            command=self.stop_wipe,
            bg='#dc143c',
            fg='white',
            font=('Arial', 14, 'bold'),
            height=3,
            width=18,
            relief='raised',
            state='disabled',
            bd=5
        )
        self.stop_button.pack(side='right', padx=20)
        
        # Start the performance monitor
        self.update_performance_display()
    
    def start_ultra_fast_wipe(self):
        """Start the ultra-fast wiping process"""
        if self.is_wiping:
            return
        
        # Confirmation
        method_name = {
            "lightning": "LIGHTNING WIPE (15-20 seconds)",
            "zeros": "ULTRA-FAST ZEROS (25-30 seconds)",
            "random": "PARALLEL RANDOM (45-60 seconds)"
        }[self.wipe_method.get()]
        
        if not messagebox.askyesno(
            "⚡ ULTRA-FAST WIPE CONFIRMATION",
            f"🎯 Target: /dev/sdb (5GB)\n"
            f"⚡ Method: {method_name}\n"
            f"🚀 Performance: MAXIMUM SPEED\n\n"
            f"This will COMPLETELY WIPE /dev/sdb!\n\n"
            f"Continue with ULTRA-FAST wipe?"
        ):
            return
        
        # Start wiping
        self.is_wiping = True
        self.start_time = time.time()
        self.bytes_written = 0
        self.current_speed = 0
        self.peak_speed = 0
        
        self.start_button.config(state='disabled')
        self.benchmark_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        self.progress_bar['value'] = 0
        self.status_var.set("🚀 ULTRA-FAST WIPE STARTING...")
        
        # Start in thread
        thread = threading.Thread(target=self.perform_ultra_fast_wipe)
        thread.daemon = True
        thread.start()
    
    def perform_ultra_fast_wipe(self):
        """Perform the ultra-fast wipe"""
        try:
            # Create ultra-fast wiper
            self.wiper = UltraFastDataWiper(
                device_path="/dev/sdb",
                method=self.wipe_method.get(),
                callback=self.update_progress
            )
            
            self.wiper.is_running = True
            success = self.wiper.wipe()
            
            # Handle completion
            self.root.after(100, lambda: self.wipe_completed(success))
            
        except Exception as e:
            self.root.after(100, lambda: self.wipe_failed(str(e)))
    
    def update_progress(self, message, progress, bytes_written=0):
        """Update progress with performance metrics"""
        def update_ui():
            # Update status
            self.status_var.set(message)
            
            # Update progress bar
            if progress is not None:
                self.progress_bar['value'] = progress
                self.progress_percent.config(text=f"{progress:.1f}%")
            
            # Update performance metrics
            if bytes_written > 0 and self.start_time:
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    self.current_speed = (bytes_written / (1024*1024)) / elapsed
                    self.peak_speed = max(self.peak_speed, self.current_speed)
                    
                    # Update speed displays
                    self.speed_var.set(f"{self.current_speed:.1f} MB/s")
                    self.peak_speed_var.set(f"{self.peak_speed:.1f} MB/s")
                    
                    # Calculate ETA
                    if self.current_speed > 0:
                        remaining_mb = (5 * 1024) - (bytes_written / (1024*1024))
                        eta_seconds = remaining_mb / self.current_speed
                        self.eta_var.set(f"ETA: {eta_seconds:.0f}s")
                    
                    # Update elapsed time
                    self.elapsed_var.set(f"Elapsed: {elapsed:.1f}s")
        
        self.root.after(10, update_ui)
    
    def wipe_completed(self, success):
        """Handle wipe completion"""
        self.is_wiping = False
        self.start_button.config(state='normal')
        self.benchmark_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        if success:
            elapsed = time.time() - self.start_time if self.start_time else 0
            
            self.status_var.set(f"✅ ULTRA-FAST WIPE COMPLETE! ({elapsed:.1f} seconds)")
            self.progress_bar['value'] = 100
            self.progress_percent.config(text="100%")
            
            # Success message with performance stats
            messagebox.showinfo(
                "⚡ ULTRA-FAST WIPE SUCCESS!",
                f"🎉 5GB /dev/sdb wiped successfully!\n\n"
                f"⏱️ Total time: {elapsed:.1f} seconds\n"
                f"🚀 Peak speed: {self.peak_speed:.1f} MB/s\n"
                f"📊 Average speed: {self.current_speed:.1f} MB/s\n\n"
                f"🏆 ULTRA-FAST PERFORMANCE ACHIEVED!"
            )
        else:
            self.wipe_failed("Wipe operation failed")
    
    def wipe_failed(self, error_msg):
        """Handle wipe failure"""
        self.is_wiping = False
        self.start_button.config(state='normal')
        self.benchmark_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.status_var.set(f"❌ {error_msg}")
        messagebox.showerror("Error", error_msg)
    
    def stop_wipe(self):
        """Emergency stop"""
        if self.wiper:
            self.wiper.stop()
        
        self.is_wiping = False
        self.start_button.config(state='normal')
        self.benchmark_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.status_var.set("⏹️ Wipe stopped by user")
    
    def run_benchmark(self):
        """Run speed benchmark"""
        if self.is_wiping:
            return
        
        if not messagebox.askyesno(
            "🏁 Speed Benchmark",
            "This will test all wiping methods on /dev/sdb.\n"
            "This will wipe the device multiple times!\n\n"
            "Continue?"
        ):
            return
        
        self.status_var.set("🏁 Running speed benchmark...")
        
        # Run benchmark in thread
        def benchmark_thread():
            try:
                from ultra_fast_backend import benchmark_wipe_speed
                results = benchmark_wipe_speed("/dev/sdb")
                
                # Show results
                result_text = "🏆 BENCHMARK RESULTS:\n\n"
                for method, time_taken in sorted(results.items(), key=lambda x: x[1]):
                    speed_mbps = (5 * 1024) / time_taken  # 5GB in MB
                    result_text += f"🥇 {method.upper()}: {time_taken:.1f}s @ {speed_mbps:.1f} MB/s\n"
                
                messagebox.showinfo("🏁 Benchmark Complete", result_text)
                
            except Exception as e:
                messagebox.showerror("Benchmark Error", f"Benchmark failed: {e}")
        
        thread = threading.Thread(target=benchmark_thread)
        thread.daemon = True
        thread.start()
    
    def update_performance_display(self):
        """Update performance display continuously"""
        if self.is_wiping and self.start_time:
            elapsed = time.time() - self.start_time
            self.elapsed_var.set(f"Elapsed: {elapsed:.1f}s")
        
        # Schedule next update
        self.root.after(100, self.update_performance_display)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = UltraFastTrustWipeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
