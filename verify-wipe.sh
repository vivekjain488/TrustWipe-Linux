#!/bin/bash
# TrustWipe Data Verification Tool
# Check if data has been properly wiped from /dev/sdb

echo "🔍 TrustWipe Data Verification Tool"
echo "==================================="
echo ""

# Default device
DEVICE="/dev/sdb"

# Allow custom device
if [ "$1" ]; then
    DEVICE="$1"
fi

echo "🎯 Checking device: $DEVICE"
echo ""

# 1. Check if device exists
if [ ! -e "$DEVICE" ]; then
    echo "❌ Device $DEVICE not found!"
    exit 1
fi

# 2. Get device info
echo "📊 DEVICE INFORMATION:"
echo "======================"
if command -v lsblk >/dev/null 2>&1; then
    lsblk $DEVICE 2>/dev/null || echo "Device info not available"
else
    ls -la $DEVICE
fi

echo ""
DEVICE_SIZE=$(blockdev --getsize64 $DEVICE 2>/dev/null || echo "Unknown")
if [ "$DEVICE_SIZE" != "Unknown" ]; then
    DEVICE_SIZE_GB=$((DEVICE_SIZE / 1024 / 1024 / 1024))
    echo "💾 Size: $DEVICE_SIZE bytes (~${DEVICE_SIZE_GB}GB)"
fi

echo ""

# 3. Check for data patterns
echo "🔍 DATA PATTERN ANALYSIS:"
echo "========================="

echo "🔎 Checking first 1MB for data patterns..."
FIRST_MB_CHECK=$(sudo dd if=$DEVICE bs=1M count=1 2>/dev/null | hexdump -C | head -20)

if echo "$FIRST_MB_CHECK" | grep -q "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"; then
    echo "✅ Found zeros pattern (typical after wiping)"
else
    echo "⚠️  Non-zero data detected in first MB"
fi

echo ""
echo "🔎 Checking random sample locations..."

# Sample 5 random locations
for i in {1..5}; do
    # Generate random offset (avoid very end of device)
    if [ "$DEVICE_SIZE" != "Unknown" ] && [ $DEVICE_SIZE -gt 1048576 ]; then
        MAX_OFFSET=$((DEVICE_SIZE / 1048576 - 1))  # Convert to MB and leave buffer
        OFFSET=$((RANDOM % MAX_OFFSET))
        
        SAMPLE=$(sudo dd if=$DEVICE bs=1M skip=$OFFSET count=1 2>/dev/null | hexdump -C | head -5)
        
        if echo "$SAMPLE" | grep -q "00 00 00 00 00 00 00 00"; then
            echo "✅ Location ${OFFSET}MB: Zeros detected"
        elif echo "$SAMPLE" | grep -qE "[a-fA-F1-9]"; then
            echo "⚠️  Location ${OFFSET}MB: Data patterns found"
        else
            echo "❓ Location ${OFFSET}MB: Unclear pattern"
        fi
    fi
done

echo ""

# 4. File system check
echo "💽 FILESYSTEM CHECK:"
echo "==================="
FILE_CHECK=$(sudo file -s $DEVICE 2>/dev/null || echo "Cannot determine")
echo "File type: $FILE_CHECK"

if echo "$FILE_CHECK" | grep -q "filesystem\|partition\|boot"; then
    echo "⚠️  WARNING: Filesystem structures detected!"
    echo "    This suggests data may not be completely wiped"
else
    echo "✅ No recognizable filesystem found"
fi

echo ""

# 5. Entropy analysis (basic)
echo "🎲 RANDOMNESS TEST:"
echo "=================="
echo "🔎 Analyzing data entropy in first 10MB..."

ENTROPY_TEST=$(sudo dd if=$DEVICE bs=1M count=10 2>/dev/null | hexdump -C | cut -c11-58 | sort | uniq -c | wc -l)

if [ "$ENTROPY_TEST" -lt 10 ]; then
    echo "✅ Low entropy detected (likely zeros or simple pattern)"
elif [ "$ENTROPY_TEST" -lt 100 ]; then
    echo "⚠️  Medium entropy (could be wiped with random data)"
else
    echo "❌ High entropy (suggests original data may still exist)"
fi

echo ""

# 6. Quick file recovery test
echo "🔬 RECOVERY ATTEMPT TEST:"
echo "========================="
echo "🔎 Attempting to find recoverable file signatures..."

# Look for common file headers
RECOVERY_TEST=$(sudo dd if=$DEVICE bs=1M count=100 2>/dev/null | strings | grep -E "(JPEG|PNG|PDF|ZIP|docx|xlsx)" | head -5)

if [ -z "$RECOVERY_TEST" ]; then
    echo "✅ No recoverable file signatures found"
else
    echo "⚠️  Possible recoverable file traces:"
    echo "$RECOVERY_TEST"
fi

echo ""

# 7. Summary and recommendations
echo "📋 VERIFICATION SUMMARY:"
echo "========================"

# Count indicators
GOOD_INDICATORS=0
WARNING_INDICATORS=0

# Check results and count
if echo "$FIRST_MB_CHECK" | grep -q "00 00 00 00 00 00 00 00"; then
    ((GOOD_INDICATORS++))
else
    ((WARNING_INDICATORS++))
fi

if ! echo "$FILE_CHECK" | grep -q "filesystem\|partition\|boot"; then
    ((GOOD_INDICATORS++))
else
    ((WARNING_INDICATORS++))
fi

if [ "$ENTROPY_TEST" -lt 50 ]; then
    ((GOOD_INDICATORS++))
else
    ((WARNING_INDICATORS++))
fi

if [ -z "$RECOVERY_TEST" ]; then
    ((GOOD_INDICATORS++))
else
    ((WARNING_INDICATORS++))
fi

echo "✅ Good indicators: $GOOD_INDICATORS"
echo "⚠️  Warning indicators: $WARNING_INDICATORS"
echo ""

if [ $GOOD_INDICATORS -ge 3 ]; then
    echo "🎉 RESULT: Data appears to be SUCCESSFULLY WIPED!"
    echo "   The device shows strong signs of proper data destruction."
elif [ $WARNING_INDICATORS -le 2 ]; then
    echo "✅ RESULT: Data appears to be MOSTLY WIPED"
    echo "   Some minor traces detected but likely acceptable."
else
    echo "❌ RESULT: Data may NOT be completely wiped!"
    echo "   Consider running TrustWipe again with a different method."
fi

echo ""
echo "💡 NEXT STEPS:"
echo "=============="
if [ $WARNING_INDICATORS -gt 2 ]; then
    echo "• Run TrustWipe again with DoD method for extra security"
    echo "• Use multiple passes: sudo ./run-ultra-cli.sh --method random --passes 3"
    echo "• Consider professional data recovery tools for verification"
else
    echo "• ✅ Wipe verification successful!"
    echo "• Device is safe for disposal or reuse"
    echo "• Keep TrustWipe completion certificate for records"
fi

echo ""
echo "🔒 For forensic-grade verification, consider professional tools like:"
echo "   • NIST DBAN verification"
echo "   • Professional data recovery services"
echo "   • Hardware-level verification tools"
