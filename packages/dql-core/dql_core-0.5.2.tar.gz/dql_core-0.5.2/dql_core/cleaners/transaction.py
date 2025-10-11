"""Transaction management for cleaner execution (Story 2.7)."""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from typing import Any, List, Callable, Optional
import uuid

from dql_core.cleaners.chain import CleanerChain
from dql_core.results import CleanerResult


class TransactionManager(ABC):
    """
    Abstract transaction manager for cleaner execution.

    Provides database-agnostic transaction management with support
    for transactions, savepoints, and context managers.
    """

    def __init__(self):
        """Initialize transaction manager."""
        self.active = False
        self.savepoint_stack: List[str] = []

    @abstractmethod
    def begin(self) -> None:
        """Begin a new transaction."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        pass

    @abstractmethod
    def savepoint(self, name: str) -> None:
        """
        Create a savepoint within the transaction.

        Args:
            name: Savepoint identifier
        """
        pass

    @abstractmethod
    def release_savepoint(self, name: str) -> None:
        """
        Release a savepoint (commit nested transaction).

        Args:
            name: Savepoint identifier
        """
        pass

    @abstractmethod
    def rollback_to_savepoint(self, name: str) -> None:
        """
        Rollback to a savepoint.

        Args:
            name: Savepoint identifier
        """
        pass

    @contextmanager
    def transaction(self):
        """
        Context manager for transaction execution.

        Automatically begins transaction on entry and commits on exit.
        Rolls back if exception is raised.

        Usage:
            >>> with manager.transaction():
            ...     # do work
            ...     pass

        Yields:
            self (TransactionManager)
        """
        try:
            self.begin()
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    @contextmanager
    def atomic_savepoint(self, name: str):
        """
        Context manager for savepoint execution.

        Automatically creates savepoint on entry and releases on exit.
        Rolls back to savepoint if exception is raised.

        Usage:
            >>> with manager.atomic_savepoint('sp1'):
            ...     # do work
            ...     pass

        Args:
            name: Savepoint identifier

        Yields:
            None
        """
        try:
            self.savepoint(name)
            yield
            self.release_savepoint(name)
        except Exception:
            self.rollback_to_savepoint(name)
            raise


class DictTransactionManager(TransactionManager):
    """
    In-memory transaction manager for dict records.

    Provides transaction semantics for dict-based records without
    requiring a database. Useful for testing and simple use cases.

    Uses deepcopy to snapshot record state and restore on rollback.
    """

    def __init__(self):
        """Initialize dict transaction manager."""
        super().__init__()
        self._snapshot: Optional[Any] = None
        self._savepoint_snapshots: dict[str, Any] = {}

    def begin(self) -> None:
        """Begin transaction (mark as active)."""
        self.active = True
        # Don't clear snapshot - it may have been taken before begin()

    def commit(self) -> None:
        """Commit transaction (clear snapshots)."""
        if self.active:
            self._snapshot = None
            self._savepoint_snapshots.clear()
            self.savepoint_stack.clear()
            self.active = False

    def rollback(self) -> None:
        """
        Rollback transaction (restore from snapshot).

        Note: Actual restoration must be done by SafeCleanerExecutor
        since we need to restore the original record reference.
        """
        if self.active:
            self._snapshot = None
            self._savepoint_snapshots.clear()
            self.savepoint_stack.clear()
            self.active = False

    def take_snapshot(self, record: Any) -> None:
        """
        Take snapshot of record state.

        Args:
            record: Record to snapshot
        """
        self._snapshot = deepcopy(record)

    def restore_snapshot(self, record: Any) -> Any:
        """
        Restore record from snapshot.

        Args:
            record: Record to restore (modified in-place if dict)

        Returns:
            Restored record (or snapshot copy if not dict)
        """
        if self._snapshot is None:
            return record

        if isinstance(record, dict):
            # Restore dict in-place
            record.clear()
            record.update(self._snapshot)
            return record
        else:
            # Return snapshot copy for other types
            return deepcopy(self._snapshot)

    def savepoint(self, name: str) -> None:
        """
        Create savepoint snapshot.

        Args:
            name: Savepoint identifier
        """
        self.savepoint_stack.append(name)
        # Snapshot will be taken by executor when needed

    def release_savepoint(self, name: str) -> None:
        """
        Release savepoint.

        Args:
            name: Savepoint identifier
        """
        if name in self.savepoint_stack:
            self.savepoint_stack.remove(name)
        if name in self._savepoint_snapshots:
            del self._savepoint_snapshots[name]

    def rollback_to_savepoint(self, name: str) -> None:
        """
        Rollback to savepoint.

        Args:
            name: Savepoint identifier
        """
        # Rollback handled by executor
        if name in self.savepoint_stack:
            # Remove this and later savepoints
            idx = self.savepoint_stack.index(name)
            self.savepoint_stack = self.savepoint_stack[:idx]

    def take_savepoint_snapshot(self, name: str, record: Any) -> None:
        """
        Take savepoint snapshot.

        Args:
            name: Savepoint identifier
            record: Record to snapshot
        """
        self._savepoint_snapshots[name] = deepcopy(record)

    def restore_savepoint_snapshot(self, name: str, record: Any) -> Any:
        """
        Restore record from savepoint snapshot.

        Args:
            name: Savepoint identifier
            record: Record to restore

        Returns:
            Restored record
        """
        if name not in self._savepoint_snapshots:
            return record

        snapshot = self._savepoint_snapshots[name]

        if isinstance(record, dict):
            record.clear()
            record.update(snapshot)
            return record
        else:
            return deepcopy(snapshot)


class SafeCleanerExecutor:
    """
    Execute cleaners with transaction safety.

    Ensures all-or-nothing cleaner execution with automatic rollback
    on failure. Supports dry-run mode and audit logging.

    Example:
        >>> manager = DictTransactionManager()
        >>> executor = SafeCleanerExecutor(manager)
        >>> cleaners = [trim_whitespace('email'), lowercase('email')]
        >>> record = {'email': '  [email protected]  '}
        >>> result = executor.execute_cleaners(cleaners, record, {})
        >>> print(result.success, record['email'])
        True [email protected]
    """

    def __init__(
        self,
        transaction_manager: TransactionManager,
        audit_logger: Optional['AuditLogger'] = None
    ):
        """
        Initialize safe cleaner executor.

        Args:
            transaction_manager: TransactionManager instance
            audit_logger: Optional audit logger for change tracking
        """
        self.transaction_manager = transaction_manager
        self.audit_logger = audit_logger
        self.dry_run = False

    def execute_cleaners(
        self,
        cleaners: List[Callable],
        record: Any,
        context: dict
    ) -> CleanerResult:
        """
        Execute cleaner chain with transaction safety.

        Wraps cleaner execution in a transaction, commits if all
        cleaners succeed, rolls back if any fail.

        Args:
            cleaners: List of cleaner functions
            record: Record to clean
            context: Execution context

        Returns:
            Consolidated CleanerResult with transaction status

        Behavior:
            - Begins transaction before execution
            - Executes cleaners sequentially via CleanerChain
            - Commits if all succeed
            - Rolls back if any fail
            - Logs modifications to audit log (if configured)
        """
        transaction_id = str(uuid.uuid4())
        context['transaction_id'] = transaction_id

        try:
            # Begin transaction
            if not self.dry_run:
                self.transaction_manager.begin()

            # Take snapshot for potential rollback (after begin)
            if isinstance(self.transaction_manager, DictTransactionManager):
                self.transaction_manager.take_snapshot(record)

            # Create cleaner chain
            chain = CleanerChain()
            for cleaner in cleaners:
                chain.add(cleaner)

            # Execute chain
            result = chain.execute(record, context)

            # Log modifications
            if self.audit_logger and result.modified:
                self._log_modifications(transaction_id, chain.cleaner_names, record, result)

            # Check result
            if result.success:
                # Commit transaction
                if not self.dry_run:
                    self.transaction_manager.commit()
                return result
            else:
                # Rollback transaction
                if not self.dry_run:
                    self.transaction_manager.rollback()
                    # Restore record if dict transaction manager
                    if isinstance(self.transaction_manager, DictTransactionManager):
                        self.transaction_manager.restore_snapshot(record)
                return result

        except Exception as e:
            # Rollback on exception
            if not self.dry_run and self.transaction_manager.active:
                self.transaction_manager.rollback()
                # Restore record if dict transaction manager
                if isinstance(self.transaction_manager, DictTransactionManager):
                    self.transaction_manager.restore_snapshot(record)

            return CleanerResult(
                success=False,
                modified=False,
                error=f"Transaction failed: {str(e)}"
            )

    def preview_changes(
        self,
        cleaners: List[Callable],
        record: Any,
        context: dict
    ) -> CleanerResult:
        """
        Preview cleaner changes without committing (dry-run).

        Executes cleaners on a deep copy of the record to preview
        changes without modifying the original or committing to database.

        Args:
            cleaners: List of cleaner functions
            record: Record to clean (will be copied)
            context: Execution context

        Returns:
            CleanerResult with preview of changes

        Example:
            >>> result = executor.preview_changes(cleaners, record, {})
            >>> print(f"Would change: {result.before_value} → {result.after_value}")
        """
        # Make copy of record to avoid mutations
        record_copy = deepcopy(record)

        # Enable dry-run mode
        self.dry_run = True

        try:
            result = self.execute_cleaners(cleaners, record_copy, context)
            return result
        finally:
            self.dry_run = False

    def _log_modifications(
        self,
        transaction_id: str,
        cleaner_names: List[str],
        record: Any,
        result: CleanerResult
    ) -> None:
        """
        Log cleaner modifications to audit log.

        Args:
            transaction_id: Transaction identifier
            cleaner_names: Names of cleaners executed
            record: Modified record
            result: Cleaner execution result
        """
        if self.audit_logger:
            from dql_core.cleaners.audit import CleanerAuditLog

            # Extract record ID
            record_id = 'unknown'
            if isinstance(record, dict):
                record_id = str(record.get('id', 'unknown'))
            elif hasattr(record, 'id'):
                record_id = str(record.id)

            log_entry = CleanerAuditLog(
                transaction_id=transaction_id,
                timestamp=datetime.now(),
                cleaner_names=cleaner_names,
                record_id=record_id,
                before_value=result.before_value,
                after_value=result.after_value
            )
            self.audit_logger.log(log_entry)
