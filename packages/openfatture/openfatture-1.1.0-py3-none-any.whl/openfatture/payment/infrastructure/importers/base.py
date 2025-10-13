"""Base interface for bank statement importers.

Defines the contract that all importers must implement using the Adapter pattern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session, object_session

from openfatture.payment.domain.models import BankTransaction
from openfatture.storage.database.base import SessionLocal

if TYPE_CHECKING:
    from ...domain.models import BankAccount, BankTransaction


class FileFormat(str, Enum):
    """Supported bank statement file formats."""

    CSV = "csv"
    OFX = "ofx"
    QIF = "qif"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value


@dataclass
class ImportResult:
    """Result of an import operation.

    Contains statistics and details about the import process.
    """

    success_count: int = 0
    error_count: int = 0
    duplicate_count: int = 0
    transactions: list["BankTransaction"] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    import_date: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def total_count(self) -> int:
        """Total number of transactions processed."""
        return self.success_count + self.error_count + self.duplicate_count

    @property
    def success_rate(self) -> float:
        """Percentage of successful imports (0.0-1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "success_count": self.success_count,
            "error_count": self.error_count,
            "duplicate_count": self.duplicate_count,
            "total_count": self.total_count,
            "success_rate": float(self.success_rate),
            "errors": self.errors,
            "import_date": self.import_date.isoformat(),
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"ImportResult(success={self.success_count}/{self.total_count}, "
            f"errors={self.error_count}, duplicates={self.duplicate_count})"
        )


class BaseImporter(ABC):
    """Abstract base class for bank statement importers.

    Implements the Template Method pattern with hooks for customization.
    Each concrete importer (CSV, OFX, QIF) implements the parse method.

    Subclassing:
        1. Implement parse() method to extract transactions from file
        2. Optionally override detect_encoding() for special encoding detection
        3. Optionally override validate_file() for format-specific validation
    """

    def __init__(self, file_path: Path) -> None:
        """Initialize importer with file path.

        Args:
            file_path: Path to bank statement file
        """
        self.file_path = file_path

    @abstractmethod
    def parse(self, account: "BankAccount") -> list["BankTransaction"]:
        """Parse bank statement and extract transactions.

        This is the core method that each importer must implement.

        Args:
            account: BankAccount to associate transactions with

        Returns:
            List of parsed BankTransaction entities

        Raises:
            ValueError: If file format is invalid
            IOError: If file cannot be read
        """
        pass

    def import_transactions(
        self, account: "BankAccount", skip_duplicates: bool = True
    ) -> ImportResult:
        """Import transactions from file with duplicate detection.

        Template Method that orchestrates the import process:
        1. Validate file
        2. Parse transactions
        3. Detect duplicates (if enabled)
        4. Return result with statistics

        Args:
            account: BankAccount to import into
            skip_duplicates: Whether to skip duplicate transactions

        Returns:
            ImportResult with statistics and imported transactions
        """
        result = ImportResult()

        try:
            # Validate file
            self.validate_file()

            # Parse transactions
            transactions = self.parse(account)

            session = object_session(account)
            created_session = False
            if session is None:
                if SessionLocal is None:
                    raise RuntimeError(
                        "Database not initialised. Call init_db() before importing statements."
                    )
                session = SessionLocal()
                created_session = True

            # Process each transaction
            for transaction in transactions:
                try:
                    if skip_duplicates and self._transaction_exists(session, account, transaction):
                        result.duplicate_count += 1
                        continue

                    result.transactions.append(transaction)
                    result.success_count += 1

                except Exception as e:
                    result.error_count += 1
                    result.errors.append(f"Transaction import error: {str(e)}")

            if created_session:
                session.close()

        except Exception as e:
            result.error_count += 1
            result.errors.append(f"File parsing error: {str(e)}")
            raise

        return result

    def validate_file(self) -> None:
        """Validate that file exists and is readable.

        Can be overridden by subclasses for format-specific validation.

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if self.file_path.stat().st_size == 0:
            raise ValueError(f"File is empty: {self.file_path}")

    def detect_encoding(self) -> str:
        """Detect file encoding.

        Default implementation tries common encodings. Can be overridden
        by subclasses for more sophisticated detection.

        Returns:
            Encoding name (e.g., "utf-8", "iso-8859-1")
        """
        # Try common encodings
        encodings = ["utf-8", "iso-8859-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(self.file_path, encoding=encoding) as f:
                    f.read(1024)  # Try to read first 1KB
                return encoding
            except UnicodeDecodeError:
                continue

        # Fallback to UTF-8
        return "utf-8"

    def __repr__(self) -> str:
        """Human-readable string representation."""
        return f"<{self.__class__.__name__}(file='{self.file_path.name}')>"

    @staticmethod
    def _transaction_exists(
        session: Session,
        account: "BankAccount",
        transaction: "BankTransaction",
    ) -> bool:
        """Check whether a transaction with the same signature already exists."""

        with session.no_autoflush:
            existing = (
                session.query(BankTransaction)
                .filter(
                    BankTransaction.account_id == account.id,
                    BankTransaction.date == transaction.date,
                    BankTransaction.amount == transaction.amount,
                    BankTransaction.description == transaction.description,
                )
                .first()
            )
        return existing is not None
