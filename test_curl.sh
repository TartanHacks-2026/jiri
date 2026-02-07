#!/bin/bash
# Test script for Jiri /turn endpoint

BASE_URL="${1:-http://localhost:8000}"
SESSION_ID=""

echo "🧪 Testing Jiri Voice Backend at $BASE_URL"
echo "========================================="
echo ""

# Test 1: Health check
echo "1️⃣  Health Check"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# Test 2: First turn (new session)
echo "2️⃣  First Turn (Hello)"
RESPONSE=$(curl -s -X POST "$BASE_URL/turn" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"","user_text":"hello","client":"shortcut","meta":{"voice":true,"timezone":"America/New_York","device":"iphone"}}')
echo "$RESPONSE" | python3 -m json.tool
SESSION_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")
echo "📍 Session ID: $SESSION_ID"
echo ""

# Test 3: Second turn (with session)
echo "3️⃣  Second Turn (Remember name)"
curl -s -X POST "$BASE_URL/turn" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"user_text\":\"remember my name is Nihal\",\"client\":\"shortcut\",\"meta\":{\"voice\":true}}" | python3 -m json.tool
echo ""

# Test 4: Third turn (recall name)
echo "4️⃣  Third Turn (What is my name?)"
curl -s -X POST "$BASE_URL/turn" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"user_text\":\"what is my name\",\"client\":\"shortcut\",\"meta\":{\"voice\":true}}" | python3 -m json.tool
echo ""

# Test 5: Capabilities check
echo "5️⃣  Capabilities Check"
curl -s -X POST "$BASE_URL/turn" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"user_text\":\"what can you do\",\"client\":\"shortcut\",\"meta\":{\"voice\":true}}" | python3 -m json.tool
echo ""

# Test 6: End conversation
echo "6️⃣  End Conversation (stop)"
curl -s -X POST "$BASE_URL/turn" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"user_text\":\"stop\",\"client\":\"shortcut\",\"meta\":{\"voice\":true}}" | python3 -m json.tool
echo ""

echo "✅ All tests completed!"
