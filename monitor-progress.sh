#!/bin/bash

# TrustWipe Progress Monitor
# Use this to check if your wiping operation is actually working

echo "========================================"
echo "    TrustWipe Progress Monitor"
echo "========================================"
echo

# Check if TrustWipe processes are running
echo "🔍 Checking TrustWipe processes..."
TRUSTWIPE_PROCS=$(ps aux | grep -E "(trustwipe|dd.*sda|shred.*sda)" | grep -v grep)
if [ -n "$TRUSTWIPE_PROCS" ]; then
    echo "✅ TrustWipe processes found:"
    echo "$TRUSTWIPE_PROCS"
else
    echo "❌ No TrustWipe processes found"
fi

echo
echo "🔍 Checking disk activity on /dev/sda..."

# Check disk I/O statistics
if command -v iostat >/dev/null 2>&1; then
    echo "📊 Current I/O statistics:"
    iostat -x 1 2 | grep sda | tail -1
else
    echo "⚠️  iostat not available, checking /proc/diskstats..."
    echo "📊 Disk statistics:"
    cat /proc/diskstats | grep -w sda
fi

echo
echo "🔍 Checking write activity..."

# Monitor writes to sda
WRITE_COUNT_1=$(cat /proc/diskstats | grep -w sda | awk '{print $7}')
sleep 2
WRITE_COUNT_2=$(cat /proc/diskstats | grep -w sda | awk '{print $7}')

WRITE_DIFF=$((WRITE_COUNT_2 - WRITE_COUNT_1))
if [ $WRITE_DIFF -gt 0 ]; then
    echo "✅ DISK IS BEING WRITTEN TO! ($WRITE_DIFF sectors written in 2 seconds)"
    echo "   Your wiping is actively working!"
else
    echo "❌ NO WRITE ACTIVITY detected - wiping may be stuck"
fi

echo
echo "🔍 Checking TrustWipe logs..."
if [ -d "/var/log/trustwipe" ]; then
    LOG_FILE=$(ls -t /var/log/trustwipe/wipe_*.log 2>/dev/null | head -1)
    if [ -n "$LOG_FILE" ]; then
        echo "📋 Latest log entries:"
        tail -5 "$LOG_FILE"
    else
        echo "⚠️  No log files found"
    fi
else
    echo "⚠️  Log directory not found"
fi

echo
echo "🔍 System resource usage..."
echo "💾 Memory usage:"
free -h | head -2

echo "⚡ CPU usage:"
top -bn1 | grep "Cpu(s)" | head -1

# Check if system is responsive
echo
echo "🔍 System responsiveness test..."
START_TIME=$(date +%s%3N)
ls / >/dev/null 2>&1
END_TIME=$(date +%s%3N)
RESPONSE_TIME=$((END_TIME - START_TIME))

if [ $RESPONSE_TIME -lt 1000 ]; then
    echo "✅ System is responsive (${RESPONSE_TIME}ms)"
else
    echo "⚠️  System is slow (${RESPONSE_TIME}ms) - this is normal during wiping"
fi

echo
echo "========================================"
echo "    Monitor Summary"
echo "========================================"

# Overall assessment
if [ -n "$TRUSTWIPE_PROCS" ] && [ $WRITE_DIFF -gt 0 ]; then
    echo "🎉 STATUS: WIPING IS WORKING CORRECTLY"
    echo "   ✅ Process is running"
    echo "   ✅ Disk is being written to"
    echo "   ⏳ Please be patient - wiping 80GB takes time"
    
    # Estimate time remaining (rough calculation)
    SECTORS_PER_SEC=$((WRITE_DIFF / 2))
    if [ $SECTORS_PER_SEC -gt 0 ]; then
        TOTAL_SECTORS=$(cat /sys/block/sda/size 2>/dev/null || echo "156250000")
        REMAINING_TIME=$((TOTAL_SECTORS / SECTORS_PER_SEC / 60))
        echo "   ⏱️  Estimated remaining: ~${REMAINING_TIME} minutes"
    fi
    
elif [ -n "$TRUSTWIPE_PROCS" ]; then
    echo "⚠️  STATUS: PROCESS RUNNING BUT NOT WRITING"
    echo "   ✅ Process is running"
    echo "   ❌ No disk activity detected"
    echo "   💡 May be in initialization phase"
    
else
    echo "❌ STATUS: NO WIPING PROCESS FOUND"
    echo "   ❌ TrustWipe is not running"
    echo "   💡 Process may have crashed or completed"
fi

echo
echo "Commands to monitor continuously:"
echo "  watch -n 5 '$0'           # Run this script every 5 seconds"
echo "  sudo iotop -a -o -d 1     # Monitor I/O activity"
echo "  watch 'cat /proc/diskstats | grep sda'  # Watch disk stats"

echo
echo "To stop wiping if needed:"
echo "  sudo pkill -f 'dd.*sda'   # Stop dd process"
echo "  sudo pkill -f trustwipe   # Stop TrustWipe GUI"
