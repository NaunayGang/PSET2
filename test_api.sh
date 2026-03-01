#!/usr/bin/env bash

set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8000}"

print_header() {
  echo "========================================="
  echo "   PSET2 Banking API - E2E Demo"
  echo "========================================="
  echo "API URL: $API_URL"
  echo
}

pretty_json() {
  python -m json.tool
}

json_get() {
  local key="$1"
  python - "$key" <<'PY'
import json
import sys

key = sys.argv[1]
payload = json.load(sys.stdin)
value = payload[key]
if isinstance(value, (int, float)):
    print(f"{value:.2f}")
else:
    print(value)
PY
}

assert_eq() {
  local actual="$1"
  local expected="$2"
  local message="$3"

  if [[ "$actual" != "$expected" ]]; then
    echo "✗ Assertion failed: $message"
    echo "  expected: $expected"
    echo "  actual:   $actual"
    exit 1
  fi

  echo "✓ $message ($actual)"
}

print_header

echo ">>> 1) Health check"
curl -s "$API_URL/health" | pretty_json
echo

echo ">>> 2) Create customer"
CUSTOMER_RESPONSE=$(curl -s -X POST "$API_URL/customers" \
  -H "Content-Type: application/json" \
  -d '{"name": "Demo User", "email": "demo.user.e2e@example.com"}')
echo "$CUSTOMER_RESPONSE" | pretty_json
CUSTOMER_ID=$(echo "$CUSTOMER_RESPONSE" | json_get id)
echo "✓ Customer created: $CUSTOMER_ID"
echo

echo ">>> 3) Create account A"
ACCOUNT_A_RESPONSE=$(curl -s -X POST "$API_URL/accounts" \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\": \"$CUSTOMER_ID\", \"currency\": \"USD\"}")
echo "$ACCOUNT_A_RESPONSE" | pretty_json
ACCOUNT_A_ID=$(echo "$ACCOUNT_A_RESPONSE" | json_get id)
echo "✓ Account A created: $ACCOUNT_A_ID"
echo

echo ">>> 4) Create account B"
ACCOUNT_B_RESPONSE=$(curl -s -X POST "$API_URL/accounts" \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\": \"$CUSTOMER_ID\", \"currency\": \"USD\"}")
echo "$ACCOUNT_B_RESPONSE" | pretty_json
ACCOUNT_B_ID=$(echo "$ACCOUNT_B_RESPONSE" | json_get id)
echo "✓ Account B created: $ACCOUNT_B_ID"
echo

echo ">>> 5) Deposit 1000.00 into account A"
DEPOSIT_RESPONSE=$(curl -s -X POST "$API_URL/transactions/deposit" \
  -H "Content-Type: application/json" \
  -d "{\"account_id\": \"$ACCOUNT_A_ID\", \"amount\": \"1000.00\", \"description\": \"E2E deposit\"}")
echo "$DEPOSIT_RESPONSE" | pretty_json
echo

echo ">>> 6) Withdraw 200.00 from account A"
WITHDRAW_RESPONSE=$(curl -s -X POST "$API_URL/transactions/withdraw" \
  -H "Content-Type: application/json" \
  -d "{\"account_id\": \"$ACCOUNT_A_ID\", \"amount\": \"200.00\", \"description\": \"E2E withdraw\"}")
echo "$WITHDRAW_RESPONSE" | pretty_json
echo

echo ">>> 7) Transfer 100.00 from account A to account B"
TRANSFER_RESPONSE=$(curl -s -X POST "$API_URL/transactions/transfer" \
  -H "Content-Type: application/json" \
  -d "{\"from_account_id\": \"$ACCOUNT_A_ID\", \"to_account_id\": \"$ACCOUNT_B_ID\", \"amount\": \"100.00\", \"description\": \"E2E transfer\"}")
echo "$TRANSFER_RESPONSE" | pretty_json
echo

echo ">>> 8) Verify account balances reflect operations"
ACCOUNT_A_FINAL=$(curl -s "$API_URL/accounts/$ACCOUNT_A_ID")
ACCOUNT_B_FINAL=$(curl -s "$API_URL/accounts/$ACCOUNT_B_ID")
echo "Account A:"
echo "$ACCOUNT_A_FINAL" | pretty_json
echo "Account B:"
echo "$ACCOUNT_B_FINAL" | pretty_json

ACCOUNT_A_BALANCE=$(echo "$ACCOUNT_A_FINAL" | json_get balance)
ACCOUNT_B_BALANCE=$(echo "$ACCOUNT_B_FINAL" | json_get balance)

# With flat fee $0.50:
# Account A = 0 + (1000 - 0.50) - (200 + 0.50) - (100 + 0.50) = 698.50
# Account B = 0 + 100.00 = 100.00
assert_eq "$ACCOUNT_A_BALANCE" "698.50" "Final balance of account A"
assert_eq "$ACCOUNT_B_BALANCE" "100.00" "Final balance of account B"
echo

echo ">>> 9) Verify transaction list for account A"
TXN_LIST=$(curl -s "$API_URL/accounts/$ACCOUNT_A_ID/transactions")
echo "$TXN_LIST" | pretty_json

TXN_COUNT=$(python - <<'PY' <<< "$TXN_LIST"
import json
import sys
items = json.load(sys.stdin)
print(len(items))
PY
)
assert_eq "$TXN_COUNT" "3" "Account A transaction count"
echo

echo "========================================="
echo "   E2E Demo Completed Successfully"
echo "========================================="
echo "Summary:"
echo "- Customer: $CUSTOMER_ID"
echo "- Account A: $ACCOUNT_A_ID (final balance: $ACCOUNT_A_BALANCE)"
echo "- Account B: $ACCOUNT_B_ID (final balance: $ACCOUNT_B_BALANCE)"
echo "- Operations: deposit, withdraw, transfer"
