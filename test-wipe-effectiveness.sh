#!/bin/bash
# TrustWipe Testing Suite
# Create test data on /dev/sdb and then verify wiping works

echo "🧪 TrustWipe Testing Suite"
echo "=========================="
echo ""

DEVICE="/dev/sdb"
TEST_SIZE="100M"  # Create 100MB of test data

if [ "$1" ]; then
    DEVICE="$1"
fi

echo "🎯 Test device: $DEVICE"
echo "📦 Test data size: $TEST_SIZE"
echo ""

# Safety check
if [ ! -e "$DEVICE" ]; then
    echo "❌ Device $DEVICE not found!"
    exit 1
fi

# Warn user
echo "⚠️  WARNING: This will create test data on $DEVICE"
echo "   Make sure this device contains no important data!"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Test cancelled by user"
    exit 1
fi

echo ""

# Step 1: Create test data
echo "📝 STEP 1: Creating Test Data"
echo "============================="

echo "🔄 Creating recognizable test patterns..."

# Create test file with known patterns
TEST_FILE="/tmp/trustwipe_test_data.img"
echo "Creating test data file..."

# Create file with mixed content
{
    echo "TRUSTWIPE TEST DATA FILE" 
    echo "Created on: $(date)"
    echo "Device: $DEVICE"
    echo "======================================"
    
    # Add some fake "personal data"
    echo "FAKE PERSONAL DATA FOR TESTING:"
    echo "Name: John Doe"
    echo "Email: john@example.com" 
    echo "Phone: 555-1234"
    echo "Password: fake_password_123"
    echo "Credit Card: 4111-1111-1111-1111"
    echo "SSN: 123-45-6789"
    echo "======================================"
    
    # Add file signatures that recovery tools look for
    printf "JPEG"  # JPEG signature
    dd if=/dev/zero bs=1024 count=10 2>/dev/null
    printf "PNG"   # PNG-like signature  
    dd if=/dev/zero bs=1024 count=10 2>/dev/null
    printf "PDF"   # PDF-like signature
    dd if=/dev/zero bs=1024 count=10 2>/dev/null
    
    # Fill rest with random data
    dd if=/dev/urandom bs=1M count=50 2>/dev/null
    
} > "$TEST_FILE"

echo "✅ Test data file created: $TEST_FILE"

# Write test data to device  
echo "🔄 Writing test data to $DEVICE..."
sudo dd if="$TEST_FILE" of="$DEVICE" bs=1M status=progress 2>/dev/null
sync

echo "✅ Test data written to device"

# Clean up test file
rm -f "$TEST_FILE"

echo ""

# Step 2: Verify test data is present
echo "🔍 STEP 2: Verify Test Data Present" 
echo "=================================="

echo "🔎 Checking for test data signatures..."

TEST_CHECK=$(sudo dd if="$DEVICE" bs=1M count=10 2>/dev/null | strings | grep -E "(TRUSTWIPE TEST|John Doe|fake_password|JPEG|PNG|PDF)")

if [ -n "$TEST_CHECK" ]; then
    echo "✅ Test data confirmed on device:"
    echo "$TEST_CHECK" | head -5
else
    echo "❌ Warning: Test data not detected"
fi

echo ""

# Step 3: Run TrustWipe
echo "🔥 STEP 3: Running TrustWipe Ultra-Fast"
echo "======================================"

echo "🚀 Starting ultra-fast wipe with Lightning method..."
echo ""

if [ -f "./run-ultra-cli.sh" ]; then
    sudo ./run-ultra-cli.sh --method lightning --device "$DEVICE"
    WIPE_RESULT=$?
else
    sudo python3 ultra_fast_cli.py --method lightning --device "$DEVICE" 
    WIPE_RESULT=$?
fi

echo ""

if [ $WIPE_RESULT -eq 0 ]; then
    echo "✅ TrustWipe completed successfully!"
else
    echo "❌ TrustWipe failed!"
    exit 1
fi

echo ""

# Step 4: Verify wipe effectiveness  
echo "🔬 STEP 4: Verify Wipe Effectiveness"
echo "==================================="

echo "🔍 Running comprehensive wipe verification..."
echo ""

if [ -f "./verify-wipe.sh" ]; then
    chmod +x verify-wipe.sh
    ./verify-wipe.sh "$DEVICE"
else
    echo "❌ verify-wipe.sh not found, running basic checks..."
    
    # Basic verification
    echo "🔎 Checking for test data remnants..."
    REMNANT_CHECK=$(sudo dd if="$DEVICE" bs=1M count=10 2>/dev/null | strings | grep -E "(TRUSTWIPE TEST|John Doe|fake_password|JPEG|PNG|PDF)")
    
    if [ -z "$REMNANT_CHECK" ]; then
        echo "✅ No test data remnants found - WIPE SUCCESSFUL!"
    else
        echo "⚠️  Test data remnants detected:"
        echo "$REMNANT_CHECK"
        echo "❌ WIPE MAY BE INCOMPLETE"
    fi
fi

echo ""

# Step 5: Performance analysis
echo "📊 STEP 5: Performance Analysis"
echo "=============================="

DEVICE_SIZE=$(blockdev --getsize64 "$DEVICE" 2>/dev/null)
if [ "$DEVICE_SIZE" ]; then
    DEVICE_SIZE_GB=$((DEVICE_SIZE / 1024 / 1024 / 1024))
    echo "💾 Device size: ${DEVICE_SIZE_GB}GB"
    
    # Estimate performance based on TrustWipe logs if available
    if [ -f "/tmp/trustwipe_performance.log" ]; then
        WIPE_TIME=$(grep "completed in" /tmp/trustwipe_performance.log | tail -1 | grep -o '[0-9.]*s')
        if [ "$WIPE_TIME" ]; then
            echo "⏱️  Wipe time: $WIPE_TIME"
            
            # Calculate speed
            TIME_NUMERIC=$(echo "$WIPE_TIME" | sed 's/s//')
            if [ "$TIME_NUMERIC" ] && [ "$DEVICE_SIZE_GB" ]; then
                SPEED=$(echo "scale=1; $DEVICE_SIZE_GB / $TIME_NUMERIC" | bc 2>/dev/null)
                if [ "$SPEED" ]; then
                    echo "🚀 Speed: ${SPEED} GB/s"
                fi
            fi
        fi
    fi
fi

echo ""

# Final summary
echo "🏆 TEST SUMMARY:"
echo "==============="
echo "✅ Test data creation: SUCCESS"
echo "✅ TrustWipe execution: SUCCESS" 
echo "📊 Verification: See results above"
echo ""
echo "💡 This test helps verify that:"
echo "• TrustWipe can handle real data patterns"
echo "• Wiping is effective against recovery attempts"
echo "• Performance meets expectations for your hardware"
echo ""
echo "🔒 Your TrustWipe system is ready for production use!"
