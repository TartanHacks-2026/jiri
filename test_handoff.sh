#!/bin/bash
# Test script for Siri-to-App Handoff feature

echo "🧪 Testing Siri-to-App Handoff Feature"
echo "======================================="
echo ""

# Test 1: Voice-only (no handoff)
echo "📝 Test 1: Voice-only interaction (should NOT handoff)"
echo "Request: 'what is the weather'"
echo ""
curl -s -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id":"","user_text":"what is the weather","client":"shortcut","meta":{"voice":true}}' | python3 -m json.tool
echo ""
echo "✅ Expected: handoff_to_app = false"
echo ""
echo "---"
echo ""

# Test 2: Visual trigger (handoff)
echo "📝 Test 2: Visual trigger (SHOULD handoff)"
echo "Request: 'book an uber'"
echo ""
curl -s -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id":"","user_text":"book an uber","client":"shortcut","meta":{"voice":true}}' | python3 -m json.tool
echo ""
echo "✅ Expected: handoff_to_app = true, deep_link_url = 'jiri://continue?session_id=...'"
echo ""
echo "---"
echo ""

# Test 3: Another handoff trigger
echo "📝 Test 3: Another handoff trigger"
echo "Request: 'show me my calendar'"
echo ""
curl -s -X POST http://localhost:8000/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id":"","user_text":"show me my calendar","client":"shortcut","meta":{"voice":true}}' | python3 -m json.tool
echo ""
echo "✅ Expected: handoff_to_app = true"
echo ""
echo "======================================="
echo "🎉 Testing complete!"
