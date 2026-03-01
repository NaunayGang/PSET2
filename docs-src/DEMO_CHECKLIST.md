# Issue #12 - End-to-End Demo Checklist

This checklist defines the exact submission demo flow requested by issue #12.

## Goal

Validate that the system works end-to-end with Docker Compose and core banking operations.

## Acceptance Criteria Mapping

- [x] System runs via `docker compose up --build`.
- [x] Demo flow includes: create customer + account(s), deposit, withdraw, transfer.
- [x] Final balance and transaction list are verified against expected results.

## How to Run the Demo

1. Start all services:

```bash
docker compose up --build
```

2. In a second terminal, run the scripted E2E demo:

```bash
bash test_api.sh
```

3. Expected success signal:

- Script prints: `E2E Demo Completed Successfully`
- Script exits with code `0`

## What is Verified

The demo script validates:

1. Health endpoint is reachable.
2. Customer and two accounts are created.
3. Operations execute in order:
   - Deposit `1000.00`
   - Withdraw `200.00`
   - Transfer `100.00` from account A to account B
4. Final balances are exactly:
   - Account A: `698.50`
   - Account B: `100.00`
5. Account A transaction list contains exactly `3` transactions.

## Notes

- Fee strategy used by API default facade is flat fee `$0.50` per transaction.
- Final balances include fee impact.
