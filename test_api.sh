#!/usr/bin/env bash
#
# Script de prueba del API Banking - PSET2
# Este script demuestra todas las funcionalidades del sistema bancario
#

set -e # Exit on error

API_URL="${API_URL:-http://127.0.0.1:8000}"

echo "========================================="
echo "   PSET2 Banking API - Test Suite"
echo "========================================="
echo ""
echo "API URL: $API_URL"
echo ""

# Test 1: Health Check
echo ">>> Test 1: Health Check"
curl -s "$API_URL/health" | python -m json.tool
echo -e "\n"

# Test 2: Create Customer
echo ">>> Test 2: Create Customer"
CUSTOMER_RESPONSE=$(curl -s -X POST "$API_URL/customers" \
	-H "Content-Type: application/json" \
	-d '{"name": "Juan Pérez", "email": "juan.perez@example.com"}')
echo "$CUSTOMER_RESPONSE" | python -m json.tool
CUSTOMER_ID=$(echo "$CUSTOMER_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Customer created with ID: $CUSTOMER_ID"
echo ""

# Test 3: Get Customer
echo ">>> Test 3: Get Customer by ID"
curl -s "$API_URL/customers/$CUSTOMER_ID" | python -m json.tool
echo ""

# Test 4: Create Account
echo ">>> Test 4: Create Account"
ACCOUNT_RESPONSE=$(curl -s -X POST "$API_URL/accounts" \
	-H "Content-Type: application/json" \
	-d "{\"customer_id\": \"$CUSTOMER_ID\", \"currency\": \"USD\"}")
echo "$ACCOUNT_RESPONSE" | python -m json.tool
ACCOUNT_ID=$(echo "$ACCOUNT_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Account created with ID: $ACCOUNT_ID"
echo ""

# Test 5: Check Initial Balance
echo ">>> Test 5: Check Initial Balance"
curl -s "$API_URL/accounts/$ACCOUNT_ID/balance" | python -m json.tool
echo ""

# Test 6: Deposit
echo ">>> Test 6: Deposit \$1000.00"
curl -s -X POST "$API_URL/transactions/deposit" \
	-H "Content-Type: application/json" \
	-d "{\"account_id\": \"$ACCOUNT_ID\", \"amount\": 1000.00}" | python -m json.tool
echo ""

# Test 7: Check Balance After Deposit
echo ">>> Test 7: Check Balance After Deposit"
curl -s "$API_URL/accounts/$ACCOUNT_ID/balance" | python -m json.tool
echo ""

# Test 8: Withdraw
echo ">>> Test 8: Withdraw \$200.00"
curl -s -X POST "$API_URL/transactions/withdraw" \
	-H "Content-Type: application/json" \
	-d "{\"account_id\": \"$ACCOUNT_ID\", \"amount\": 200.00}" | python -m json.tool
echo ""

# Test 9: Check Balance After Withdraw
echo ">>> Test 9: Check Balance After Withdraw"
curl -s "$API_URL/accounts/$ACCOUNT_ID/balance" | python -m json.tool
echo ""

# Test 10: Create Second Account for Transfer
echo ">>> Test 10: Create Second Account for Transfer"
ACCOUNT2_RESPONSE=$(curl -s -X POST "$API_URL/accounts" \
	-H "Content-Type: application/json" \
	-d "{\"customer_id\": \"$CUSTOMER_ID\", \"currency\": \"USD\"}")
echo "$ACCOUNT2_RESPONSE" | python -m json.tool
ACCOUNT2_ID=$(echo "$ACCOUNT2_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Second account created with ID: $ACCOUNT2_ID"
echo ""

# Test 11: Transfer
echo ">>> Test 11: Transfer \$100.00 from Account 1 to Account 2"
curl -s -X POST "$API_URL/transactions/transfer" \
	-H "Content-Type: application/json" \
	-d "{\"from_account_id\": \"$ACCOUNT_ID\", \"to_account_id\": \"$ACCOUNT2_ID\", \"amount\": 100.00}" | python -m json.tool
echo ""

# Test 12: Check Both Balances
echo ">>> Test 12: Check Both Account Balances"
echo "Account 1 Balance:"
curl -s "$API_URL/accounts/$ACCOUNT_ID/balance" | python -m json.tool
echo ""
echo "Account 2 Balance:"
curl -s "$API_URL/accounts/$ACCOUNT2_ID/balance" | python -m json.tool
echo ""

# Test 13: List Transactions
echo ">>> Test 13: List Transactions for Account 1"
curl -s "$API_URL/accounts/$ACCOUNT_ID/transactions" | python -m json.tool
echo ""

# Test 14: List All Customers
echo ">>> Test 14: List All Customers"
curl -s "$API_URL/customers" | python -m json.tool
echo ""

echo "========================================="
echo "   All Tests Completed Successfully!"
echo "========================================="
echo ""
echo "Summary:"
echo "- Customer created: $CUSTOMER_ID"
echo "- Account 1 created: $ACCOUNT_ID"
echo "- Account 2 created: $ACCOUNT2_ID"
echo "- Performed: 1 deposit, 1 withdrawal, 1 transfer"
echo ""
echo "You can access the API documentation at:"
echo "  $API_URL/docs"
echo ""
