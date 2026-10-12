# Banking Lab

A small banking application for customers, checking accounts, and savings accounts. It checks that a customer is at least 18, keeps a savings balance at or above the equivalent of $100, and records deposits, withdrawals, currency conversions, and transfers.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Setup

From the project root:

```powershell
uv sync
```

## Run the application

```powershell
uv run python tests/test_banking.py
```

The menu can add a customer, add a checking or savings account, deposit, withdraw, convert a balance, and transfer between two accounts of the same customer. Choose `7` to exit.

An account number must be exactly 10 digits. A savings account must open with at least $100, or the equivalent in EUR or GBP.

## Checks

Run the same checks that continuous integration runs:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

`ruff format .` rewrites files that are not formatted.

## Continuous integration

`.github/workflows/ci.yml` runs Ruff and pytest on every pull request. The workflow installs Python 3.12 with uv and uses the locked dependencies.
