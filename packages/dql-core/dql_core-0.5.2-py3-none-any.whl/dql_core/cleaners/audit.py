"""Audit logging for cleaner execution (Story 2.7)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional
import json
from pathlib import Path


@dataclass
class CleanerAuditLog:
    """
    Audit log entry for cleaner modifications.

    Captures complete audit trail of cleaner executions including
    transaction ID, timestamp, cleaners executed, and value changes.

    Attributes:
        transaction_id: Unique transaction identifier
        timestamp: When modification occurred
        cleaner_names: Names of cleaners executed
        record_id: ID of modified record
        field_name: Name of field modified (optional)
        before_value: Value before cleaning
        after_value: Value after cleaning
    """

    transaction_id: str
    timestamp: datetime
    cleaner_names: List[str]
    record_id: str
    field_name: Optional[str] = None
    before_value: Any = None
    after_value: Any = None

    def to_dict(self) -> dict:
        """
        Convert audit log to dictionary.

        Returns:
            Dictionary representation of audit log
        """
        return {
            'transaction_id': self.transaction_id,
            'timestamp': self.timestamp.isoformat(),
            'cleaner_names': self.cleaner_names,
            'record_id': self.record_id,
            'field_name': self.field_name,
            'before_value': str(self.before_value),
            'after_value': str(self.after_value),
        }

    def to_json(self) -> str:
        """
        Convert audit log to JSON string.

        Returns:
            JSON representation of audit log
        """
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """
    Logger for cleaner audit trail.

    Supports multiple backends for audit log persistence:
    - memory: In-memory storage (default, for testing)
    - file: Append to audit log file
    - database: Store in database table (future)
    - custom: User-provided handler function

    Example:
        >>> logger = AuditLogger(backend='memory')
        >>> log_entry = CleanerAuditLog(
        ...     transaction_id='tx-123',
        ...     timestamp=datetime.now(),
        ...     cleaner_names=['trim_whitespace'],
        ...     record_id='user-456',
        ...     before_value='  hello  ',
        ...     after_value='hello'
        ... )
        >>> logger.log(log_entry)
        >>> logs = logger.get_logs('tx-123')
    """

    def __init__(self, backend: str = 'memory', file_path: Optional[str] = None):
        """
        Initialize audit logger.

        Args:
            backend: Logging backend ('memory', 'file', 'database', 'custom')
            file_path: Path to audit log file (required for 'file' backend)
        """
        self.backend = backend
        self.file_path = file_path
        self._memory_logs: List[CleanerAuditLog] = []
        self._custom_handler: Optional[callable] = None

    def log(self, entry: CleanerAuditLog) -> None:
        """
        Log cleaner modification.

        Args:
            entry: Audit log entry to persist

        Raises:
            ValueError: If backend is 'file' but no file_path configured
        """
        if self.backend == 'memory':
            self._memory_logs.append(entry)
        elif self.backend == 'file':
            self._log_to_file(entry)
        elif self.backend == 'database':
            self._log_to_database(entry)
        elif self.backend == 'custom':
            if self._custom_handler:
                self._custom_handler(entry)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def get_logs(self, transaction_id: Optional[str] = None) -> List[CleanerAuditLog]:
        """
        Retrieve audit logs.

        Args:
            transaction_id: Filter by transaction ID (optional)

        Returns:
            List of audit log entries

        Example:
            >>> all_logs = logger.get_logs()
            >>> tx_logs = logger.get_logs('tx-123')
        """
        if self.backend != 'memory':
            # For non-memory backends, always return empty
            # (retrieval from file/database not implemented)
            return []

        if transaction_id:
            return [
                log for log in self._memory_logs
                if log.transaction_id == transaction_id
            ]
        return self._memory_logs.copy()

    def clear(self) -> None:
        """
        Clear all logs (memory backend only).

        Example:
            >>> logger.clear()
        """
        if self.backend == 'memory':
            self._memory_logs.clear()

    def set_custom_handler(self, handler: callable) -> None:
        """
        Set custom handler for audit logging.

        Args:
            handler: Function that takes CleanerAuditLog and persists it

        Example:
            >>> def my_handler(entry: CleanerAuditLog):
            ...     print(f"Logged: {entry.transaction_id}")
            >>> logger = AuditLogger(backend='custom')
            >>> logger.set_custom_handler(my_handler)
        """
        self._custom_handler = handler
        self.backend = 'custom'

    def _log_to_file(self, entry: CleanerAuditLog) -> None:
        """
        Write log entry to file.

        Args:
            entry: Audit log entry

        Raises:
            ValueError: If no file_path configured
        """
        if not self.file_path:
            raise ValueError("file_path required for file backend")

        log_file = Path(self.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Append JSON entry to file
        with open(log_file, 'a') as f:
            f.write(entry.to_json() + '\n')

    def _log_to_database(self, entry: CleanerAuditLog) -> None:
        """
        Write log entry to database.

        Args:
            entry: Audit log entry

        Note:
            Database persistence not yet implemented.
            Placeholder for future enhancement.
        """
        # Future: Insert into audit_logs table
        #   INSERT INTO audit_logs (transaction_id, timestamp, ...)
        #   VALUES (entry.transaction_id, entry.timestamp, ...)
        pass
