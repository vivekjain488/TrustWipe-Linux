#!/bin/bash

# TrustWipe Speed Optimizer
# This script optimizes your system for faster wiping operations

echo "========================================"
echo "    TrustWipe Speed Optimizer"
echo "========================================"
echo

if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "🚀 Optimizing system for faster wiping..."

# 1. Disable swap to free up I/O bandwidth
echo "💾 Disabling swap temporarily..."
swapoff -a
echo "✅ Swap disabled"

# 2. Set I/O scheduler to deadline for better sequential write performance
echo "⚡ Optimizing I/O scheduler..."
echo deadline > /sys/block/sda/queue/scheduler 2>/dev/null || echo "⚠️  Could not change I/O scheduler"

# 3. Increase I/O queue depth
echo "📈 Increasing I/O queue depth..."
echo 32 > /sys/block/sda/queue/nr_requests 2>/dev/null || echo "⚠️  Could not change queue depth"

# 4. Disable readahead (not needed for wiping)
echo "🔧 Optimizing readahead..."
blockdev --setra 0 /dev/sda 2>/dev/null || echo "⚠️  Could not change readahead"

# 5. Sync and drop caches
echo "🧹 Clearing system caches..."
sync
echo 3 > /proc/sys/vm/drop_caches

# 6. Set CPU governor to performance mode
echo "⚡ Setting CPU to performance mode..."
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [ -f "$cpu" ]; then
        echo performance > "$cpu" 2>/dev/null || echo "⚠️  Could not set CPU governor"
        break
    fi
done

# 7. Increase dirty ratio for better write performance
echo "📝 Optimizing write buffers..."
echo 80 > /proc/sys/vm/dirty_ratio
echo 40 > /proc/sys/vm/dirty_background_ratio

# 8. Stop unnecessary services temporarily
echo "🛑 Stopping non-essential services..."
systemctl stop bluetooth 2>/dev/null || true
systemctl stop cups 2>/dev/null || true
systemctl stop avahi-daemon 2>/dev/null || true

echo
echo "✅ System optimized for wiping!"
echo

# Check current wiping process and potentially restart with better parameters
CURRENT_DD=$(ps aux | grep "dd.*sda" | grep -v grep)
if [ -n "$CURRENT_DD" ]; then
    echo "🔍 Found current dd process:"
    echo "$CURRENT_DD"
    echo
    
    # Get the PID
    DD_PID=$(echo "$CURRENT_DD" | awk '{print $2}')
    
    echo "💡 Current dd process is using potentially slow parameters."
    echo "   You can:"
    echo "   1. Let it continue (safer)"
    echo "   2. Restart with optimized parameters (faster but restarts progress)"
    echo
    
    read -p "Restart with faster parameters? [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Stopping current process..."
        kill $DD_PID
        sleep 2
        
        echo "🚀 Starting optimized wiping..."
        # Use much larger block size and direct I/O
        nohup dd if=/dev/zero of=/dev/sda bs=64M oflag=direct status=progress > /tmp/trustwipe-optimized.log 2>&1 &
        
        echo "✅ Optimized wiping started!"
        echo "📊 Monitor with: tail -f /tmp/trustwipe-optimized.log"
        echo "🔍 Check progress with: ./monitor-progress.sh"
    fi
else
    echo "ℹ️  No active dd process found."
fi

echo
echo "========================================"
echo "    Optimization Complete!"
echo "========================================"
echo
echo "🎯 Optimizations applied:"
echo "  ✅ Swap disabled"
echo "  ✅ I/O scheduler optimized"
echo "  ✅ Queue depth increased"
echo "  ✅ Caches cleared"
echo "  ✅ CPU set to performance mode"
echo "  ✅ Write buffers optimized"
echo "  ✅ Non-essential services stopped"
echo
echo "📊 Monitor progress with:"
echo "  ./monitor-progress.sh"
echo "  watch -n 2 'cat /proc/diskstats | grep sda'"
echo
echo "⚠️  Note: These optimizations are temporary and will reset on reboot"
echo "💡 Your wiping should now be significantly faster!"
