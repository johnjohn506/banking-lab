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
