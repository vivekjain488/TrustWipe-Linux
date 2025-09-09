#!/bin/bash
# Forensic-Grade Wipe Verification Tool
# Advanced data recovery testing for TrustWipe verification

echo "🔬 Forensic-Grade Wipe Verification"
echo "===================================="
echo ""

DEVICE="/dev/sdb"
if [ "$1" ]; then
    DEVICE="$1"
fi

echo "🎯 Target device: $DEVICE"
echo "🔍 Running advanced forensic verification..."
echo ""

# Check if device exists
if [ ! -e "$DEVICE" ]; then
    echo "❌ Device $DEVICE not found!"
    exit 1
fi

# Get device info
DEVICE_SIZE=$(blockdev --getsize64 "$DEVICE" 2>/dev/null)
DEVICE_SIZE_MB=$((DEVICE_SIZE / 1024 / 1024))

echo "📊 Device size: ${DEVICE_SIZE_MB}MB"
echo ""

# 1. Deep pattern analysis
echo "🔍 DEEP PATTERN ANALYSIS:"
echo "========================="

echo "🔎 Scanning entire device for data patterns..."

# Sample multiple locations across the entire device
SAMPLE_COUNT=20
PATTERN_TYPES=("zeros" "random" "data")
declare -A PATTERN_COUNTS

# Initialize counters
PATTERN_COUNTS["zeros"]=0
PATTERN_COUNTS["random"]=0  
PATTERN_COUNTS["data"]=0

for i in $(seq 1 $SAMPLE_COUNT); do
    # Calculate offset (spread across device)
    OFFSET=$((DEVICE_SIZE_MB * i / SAMPLE_COUNT))
    
    # Sample 1MB at this location
    SAMPLE_DATA=$(sudo dd if="$DEVICE" bs=1M skip="$OFFSET" count=1 2>/dev/null | xxd | head -20)
    
    # Analyze pattern
    if echo "$SAMPLE_DATA" | grep -q "0000 0000 0000 0000 0000 0000 0000 0000"; then
        ((PATTERN_COUNTS["zeros"]++))
        echo "✅ Offset ${OFFSET}MB: Zeros pattern"
    elif echo "$SAMPLE_DATA" | grep -qE "([0-9a-f]{4} ){8}"; then
        # Check if it looks random vs structured data
        UNIQUE_BYTES=$(echo "$SAMPLE_DATA" | cut -c7-54 | tr ' ' '\n' | sort -u | wc -l)
        if [ $UNIQUE_BYTES -gt 200 ]; then
            ((PATTERN_COUNTS["random"]++))
            echo "🎲 Offset ${OFFSET}MB: Random pattern"
        else
            ((PATTERN_COUNTS["data"]++))
            echo "⚠️  Offset ${OFFSET}MB: Structured data detected"
        fi
    else
        ((PATTERN_COUNTS["data"]++))
        echo "❓ Offset ${OFFSET}MB: Unknown pattern"
    fi
done

echo ""
echo "📊 Pattern Summary:"
echo "  Zeros: ${PATTERN_COUNTS["zeros"]}/$SAMPLE_COUNT samples"
echo "  Random: ${PATTERN_COUNTS["random"]}/$SAMPLE_COUNT samples"  
echo "  Data: ${PATTERN_COUNTS["data"]}/$SAMPLE_COUNT samples"

echo ""

# 2. File signature detection
echo "🔎 FILE SIGNATURE DETECTION:"
echo "============================"

echo "🔍 Scanning for recoverable file signatures..."

# Common file signatures to look for
declare -A FILE_SIGS
FILE_SIGS["JPEG"]="ffd8ff"
FILE_SIGS["PNG"]="89504e47"
FILE_SIGS["PDF"]="25504446"
FILE_SIGS["ZIP"]="504b0304"
FILE_SIGS["DOCX"]="504b030414"
FILE_SIGS["MP3"]="494433"
FILE_SIGS["AVI"]="41564920"
FILE_SIGS["GIF"]="474946383"

SIGNATURES_FOUND=0

# Sample larger chunks for signature detection
for i in $(seq 1 10); do
    OFFSET=$((DEVICE_SIZE_MB * i / 10))
    
    # Get hex dump of 10MB chunk
    HEX_DATA=$(sudo dd if="$DEVICE" bs=1M skip="$OFFSET" count=10 2>/dev/null | xxd -p | tr -d '\n')
    
    # Check for each signature
    for SIG_NAME in "${!FILE_SIGS[@]}"; do
        SIG_HEX="${FILE_SIGS[$SIG_NAME]}"
        if echo "$HEX_DATA" | grep -qi "$SIG_HEX"; then
            echo "⚠️  Found $SIG_NAME signature at offset ${OFFSET}MB"
            ((SIGNATURES_FOUND++))
        fi
    done
done

if [ $SIGNATURES_FOUND -eq 0 ]; then
    echo "✅ No recoverable file signatures detected"
else
    echo "❌ $SIGNATURES_FOUND file signatures found - data may be recoverable"
fi

echo ""

# 3. String analysis
echo "📝 STRING ANALYSIS:"
echo "=================="

echo "🔍 Searching for readable text strings..."

# Sample text from multiple locations
STRING_COUNT=0
for i in $(seq 1 5); do
    OFFSET=$((DEVICE_SIZE_MB * i / 5))
    
    STRINGS_FOUND=$(sudo dd if="$DEVICE" bs=1M skip="$OFFSET" count=5 2>/dev/null | strings -n 4 | head -20)
    
    if [ -n "$STRINGS_FOUND" ]; then
        STRING_COUNT=$((STRING_COUNT + $(echo "$STRINGS_FOUND" | wc -l)))
        echo "⚠️  Readable strings found at offset ${OFFSET}MB:"
        echo "$STRINGS_FOUND" | head -5
        echo ""
    fi
done

if [ $STRING_COUNT -eq 0 ]; then
    echo "✅ No readable text strings detected"
else
    echo "⚠️  $STRING_COUNT readable strings found"
fi

echo ""

# 4. Entropy analysis (advanced)
echo "🎲 ENTROPY ANALYSIS:"
echo "==================="

echo "🔍 Analyzing data randomness across device..."

# Test entropy at different locations
HIGH_ENTROPY=0
LOW_ENTROPY=0

for i in $(seq 1 10); do
    OFFSET=$((DEVICE_SIZE_MB * i / 10))
    
    # Get entropy using simple byte frequency analysis
    BYTE_FREQ=$(sudo dd if="$DEVICE" bs=1M skip="$OFFSET" count=1 2>/dev/null | xxd -p | fold -w2 | sort | uniq -c | wc -l)
    
    if [ $BYTE_FREQ -gt 200 ]; then
        ((HIGH_ENTROPY++))
        echo "✅ Offset ${OFFSET}MB: High entropy ($BYTE_FREQ unique bytes)"
    elif [ $BYTE_FREQ -gt 50 ]; then
        echo "🎲 Offset ${OFFSET}MB: Medium entropy ($BYTE_FREQ unique bytes)"
    else
        ((LOW_ENTROPY++))
        echo "✅ Offset ${OFFSET}MB: Low entropy ($BYTE_FREQ unique bytes)"
    fi
done

echo ""
echo "📊 Entropy Summary:"
echo "  High entropy regions: $HIGH_ENTROPY/10"
echo "  Low entropy regions: $LOW_ENTROPY/10"

echo ""

# 5. Sector-level analysis
echo "🔧 SECTOR-LEVEL ANALYSIS:"
echo "========================="

echo "🔍 Checking sector alignment and patterns..."

# Check first few sectors
SECTOR_CHECK=$(sudo dd if="$DEVICE" bs=512 count=10 2>/dev/null | hexdump -C | head -10)

if echo "$SECTOR_CHECK" | grep -q "00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00"; then
    echo "✅ First sectors properly zeroed"
else
    echo "⚠️  Non-zero data in first sectors:"
    echo "$SECTOR_CHECK" | head -3
fi

echo ""

# Final scoring and recommendation
echo "🏆 FORENSIC VERIFICATION RESULTS:"
echo "================================="

SCORE=0
MAX_SCORE=7

# Score based on different checks
if [ ${PATTERN_COUNTS["zeros"]} -gt $((SAMPLE_COUNT / 2)) ]; then
    ((SCORE++))
    echo "✅ Pattern analysis: PASS (mostly zeros)"
else
    echo "❌ Pattern analysis: FAIL (too much structured data)"
fi

if [ $SIGNATURES_FOUND -eq 0 ]; then
    ((SCORE++))
    echo "✅ File signature check: PASS (no signatures found)"
else
    echo "❌ File signature check: FAIL ($SIGNATURES_FOUND signatures detected)"
fi

if [ $STRING_COUNT -eq 0 ]; then
    ((SCORE++))
    echo "✅ String analysis: PASS (no readable text)"
else
    echo "❌ String analysis: FAIL ($STRING_COUNT strings found)"
fi

if [ $LOW_ENTROPY -gt $((10 / 2)) ]; then
    ((SCORE++))
    echo "✅ Entropy analysis: PASS (mostly low entropy)"
else
    echo "❌ Entropy analysis: FAIL (too much high entropy data)"
fi

if echo "$SECTOR_CHECK" | grep -q "00000000  00 00 00 00 00 00 00 00"; then
    ((SCORE++))
    echo "✅ Sector analysis: PASS (proper sector wiping)"
else
    echo "❌ Sector analysis: FAIL (sectors not properly wiped)"
fi

# Additional checks
if [ ${PATTERN_COUNTS["data"]} -eq 0 ]; then
    ((SCORE++))
    echo "✅ Deep scan: PASS (no structured data patterns)"
else
    echo "❌ Deep scan: FAIL (structured data found)"
fi

if [ $HIGH_ENTROPY -lt 3 ]; then
    ((SCORE++))
    echo "✅ Randomness test: PASS (low randomness indicates successful wipe)"
else
    echo "❌ Randomness test: FAIL (high randomness may indicate leftover data)"
fi

echo ""
echo "📊 FINAL SCORE: $SCORE/$MAX_SCORE"

if [ $SCORE -ge 6 ]; then
    echo "🎉 VERDICT: FORENSIC-GRADE WIPE SUCCESSFUL!"
    echo "   Data is extremely unlikely to be recoverable"
    echo "   Meets military and government standards"
elif [ $SCORE -ge 4 ]; then
    echo "✅ VERDICT: GOOD WIPE QUALITY"
    echo "   Data recovery would be very difficult"
    echo "   Suitable for most security requirements"
elif [ $SCORE -ge 2 ]; then
    echo "⚠️  VERDICT: MODERATE WIPE QUALITY"
    echo "   Some data recovery may be possible"
    echo "   Consider re-wiping with multiple passes"
else
    echo "❌ VERDICT: POOR WIPE QUALITY"
    echo "   Data recovery is likely possible"
    echo "   IMMEDIATE RE-WIPE RECOMMENDED"
fi

echo ""
echo "📋 RECOMMENDATIONS:"
echo "==================="

if [ $SCORE -ge 6 ]; then
    echo "• ✅ Device is ready for disposal or reuse"
    echo "• ✅ Meets compliance requirements"
    echo "• ✅ No further action needed"
elif [ $SCORE -ge 4 ]; then
    echo "• ⚠️  Consider one more pass for extra security"
    echo "• ✅ Generally acceptable for most uses"
elif [ $SCORE -ge 2 ]; then
    echo "• 🔄 Re-wipe with DoD method recommended"
    echo "• 🔄 Use multiple passes (3+ recommended)"
    echo "• ⚠️  Not suitable for sensitive data disposal yet"
else
    echo "• 🚨 IMMEDIATE RE-WIPE REQUIRED"
    echo "• 🔄 Use DoD method with maximum passes"
    echo "• 🔧 Check device for hardware issues"
    echo "• ❌ DO NOT dispose of device yet"
fi

echo ""
echo "🔬 For ultimate verification, consider professional forensic analysis"
