# src/banking.py
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# Custom exception for insufficient funds
class InsufficientFundsError(Exception):
    def __init__(self, message: str, amount: float) -> None:
        self.amount = amount
        super().__init__(message)

# BankAccount class
class BankAccount:
    _USD_VALUE = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27}
    _SAVINGS_MINIMUM_USD = 100.0

# BankAccount constructor
    def __init__(
        self,
        account_number: str,
        currency: str = "USD",
        account_type: str = "checking",
        balance: float = 0.0,
    ) -> None:
        self.__account_number = account_number
        self.__currency = currency
        self._account_type = account_type
        self.balance = balance

# Account number property
    @property
    def account_number(self) -> str:
        return self.__account_number

    @property
    def currency(self) -> str:
        return self.__currency

    @property
    def account_type(self) -> str:
        return self._account_type

# Balance property
    @property
    def balance(self) -> float:
        return self.__balance

# Balance setter
    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            logger.error(
                "Rejected negative balance %.2f for %s",
                value,
                self.__account_number,
            )
            raise ValueError("Balance cannot be negative")
        self.__balance = value

# Validate amount method
    @staticmethod
    def validate_amount(amount: float) -> None:
        if amount < 0:
            raise ValueError("Amount cannot be negative")

# Validate account number method
    @staticmethod
    def is_valid_account_number(account_number: str) -> bool:
        return account_number.isdigit() and len(account_number) == 10

# Validate non-negative amount method
    def _validate_non_negative(self, amount: float) -> None:
        if amount < 0:
            logger.error(
                "Rejected negative amount %.2f for %s",
                amount,
                self.account_number,
            )
            self.validate_amount(amount)

# Minimum balance method
    def _minimum_balance(self) -> float:
        if self._account_type != "savings":
            return 0.0
        usd_value = self._USD_VALUE[self.currency]
        return self._SAVINGS_MINIMUM_USD / usd_value

# Open with deposit method
    @classmethod
    def open_with_deposit(cls, account_number: str, amount: float) -> "BankAccount":
        account = cls(account_number)
        account.deposit(amount)
        return account

# Create savings method
    @classmethod
    def create_savings(
        cls,
        account_number: str,
        currency: str = "USD",
        account_type: str = "savings",
        balance: float = 0.0,
    ) -> "BankAccount":
        minimum = cls._SAVINGS_MINIMUM_USD / cls._USD_VALUE[currency]
        if balance < minimum:
            logger.error(
                "Rejected savings opening balance %.2f for %s. Minimum: %.2f",
                balance,
                account_number,
                minimum,
            )
            raise ValueError("Savings balance cannot be below the minimum")
        return cls(account_number, currency, account_type, balance)

# Deposit method
    def deposit(self, amount: float) -> float:
        self._validate_non_negative(amount)
        self.balance += amount
        logger.info(
            "Deposited %.2f into %s. Balance: %.2f",
            amount,
            self.account_number,
            self.balance,
        )
        return self.balance

# Withdraw method
    def withdraw(self, amount: float) -> float:
        self._validate_non_negative(amount)
        if self.balance - amount < self._minimum_balance():
            logger.error(
                "Withdrawal of %.2f rejected for %s. Balance: %.2f",
                amount,
                self.account_number,
                self.balance,
            )
            raise InsufficientFundsError("Insufficient funds", amount)
        self.balance -= amount
        logger.info(
            "Withdrew %.2f from %s. Balance: %.2f",
            amount,
            self.account_number,
            self.balance,
        )
        return self.balance

# Convert currency method
    def convert_currency(self, target_currency: str, exchange_rate: float) -> None:
        if exchange_rate <= 0:
            logger.error(
                "Rejected exchange rate %.2f for %s",
                exchange_rate,
                self.account_number,
            )
            raise ValueError("Exchange rate must be positive")
        converted = self.balance * exchange_rate
        logger.info(
            "Converted %.2f %s to %.2f %s",
            self.balance,
            self.currency,
            converted,
            target_currency,
        )
        return converted
