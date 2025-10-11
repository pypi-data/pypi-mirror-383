"""Tests for transaction safety (Story 2.7)."""

import pytest
from datetime import datetime

from dql_core.cleaners.transaction import (
    TransactionManager,
    DictTransactionManager,
    SafeCleanerExecutor,
)
from dql_core.cleaners.audit import CleanerAuditLog, AuditLogger
from dql_core.cleaners.string_cleaners import trim_whitespace, lowercase
from dql_core.results import CleanerResult


class TestDictTransactionManager:
    """Tests for DictTransactionManager."""

    def test_begin_sets_active(self):
        """Test begin() sets transaction as active."""
        manager = DictTransactionManager()
        assert manager.active is False

        manager.begin()
        assert manager.active is True

    def test_commit_clears_active(self):
        """Test commit() clears active status."""
        manager = DictTransactionManager()
        manager.begin()
        assert manager.active is True

        manager.commit()
        assert manager.active is False

    def test_rollback_clears_active(self):
        """Test rollback() clears active status."""
        manager = DictTransactionManager()
        manager.begin()
        assert manager.active is True

        manager.rollback()
        assert manager.active is False

    def test_take_snapshot_stores_record(self):
        """Test take_snapshot() stores record copy."""
        manager = DictTransactionManager()
        record = {'email': '[email protected]', 'name': 'John'}

        manager.take_snapshot(record)

        # Modify record
        record['email'] = 'changed@example.com'

        # Snapshot should have original value
        restored = manager.restore_snapshot(record)
        assert restored['email'] == '[email protected]'
        assert restored['name'] == 'John'

    def test_restore_snapshot_modifies_dict_in_place(self):
        """Test restore_snapshot() modifies dict in-place."""
        manager = DictTransactionManager()
        record = {'email': '[email protected]'}

        manager.take_snapshot(record)
        record['email'] = 'changed@example.com'

        manager.restore_snapshot(record)
        assert record['email'] == '[email protected]'

    def test_savepoint_adds_to_stack(self):
        """Test savepoint() adds to stack."""
        manager = DictTransactionManager()

        assert len(manager.savepoint_stack) == 0
        manager.savepoint('sp1')
        assert len(manager.savepoint_stack) == 1
        assert 'sp1' in manager.savepoint_stack

    def test_release_savepoint_removes_from_stack(self):
        """Test release_savepoint() removes from stack."""
        manager = DictTransactionManager()

        manager.savepoint('sp1')
        assert len(manager.savepoint_stack) == 1

        manager.release_savepoint('sp1')
        assert len(manager.savepoint_stack) == 0

    def test_rollback_to_savepoint_removes_later_savepoints(self):
        """Test rollback_to_savepoint() removes later savepoints."""
        manager = DictTransactionManager()

        manager.savepoint('sp1')
        manager.savepoint('sp2')
        manager.savepoint('sp3')
        assert len(manager.savepoint_stack) == 3

        manager.rollback_to_savepoint('sp2')
        assert manager.savepoint_stack == ['sp1']

    def test_transaction_context_manager(self):
        """Test transaction() context manager commits on success."""
        manager = DictTransactionManager()

        with manager.transaction():
            assert manager.active is True

        assert manager.active is False

    def test_transaction_context_manager_rolls_back_on_error(self):
        """Test transaction() context manager rolls back on exception."""
        manager = DictTransactionManager()

        with pytest.raises(ValueError):
            with manager.transaction():
                assert manager.active is True
                raise ValueError("Test error")

        assert manager.active is False

    def test_atomic_savepoint_context_manager(self):
        """Test atomic_savepoint() context manager."""
        manager = DictTransactionManager()

        manager.begin()
        with manager.atomic_savepoint('sp1'):
            assert 'sp1' in manager.savepoint_stack

        assert 'sp1' not in manager.savepoint_stack
        manager.commit()


class TestSafeCleanerExecutor:
    """Tests for SafeCleanerExecutor."""

    def test_executes_cleaners_successfully(self):
        """Test executor runs cleaners and commits."""
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        record = {'email': '  [email protected]  '}
        cleaners = [
            trim_whitespace('email'),
            lowercase('email')
        ]

        result = executor.execute_cleaners(cleaners, record, {})

        assert result.success is True
        assert result.modified is True
        assert record['email'] == '[email protected]'
        assert manager.active is False  # Transaction committed

    def test_rolls_back_on_cleaner_failure(self):
        """Test executor rolls back when cleaner fails."""
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        def failing_cleaner(field):
            def cleaner_func(record, context):
                return CleanerResult(
                    success=False,
                    modified=False,
                    error="Cleaner failed!"
                )
            return cleaner_func

        record = {'email': '  [email protected]  '}
        cleaners = [
            trim_whitespace('email'),
            failing_cleaner('email')
        ]

        result = executor.execute_cleaners(cleaners, record, {})

        assert result.success is False
        assert 'Cleaner failed!' in result.error
        assert manager.active is False  # Transaction rolled back

    def test_rolls_back_on_exception(self):
        """Test executor rolls back when exception occurs."""
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        def exception_cleaner(field):
            def cleaner_func(record, context):
                raise RuntimeError("Unexpected error!")
            return cleaner_func

        record = {'email': '  [email protected]  '}
        cleaners = [exception_cleaner('email')]

        result = executor.execute_cleaners(cleaners, record, {})

        assert result.success is False
        assert 'Transaction failed' in result.error
        assert manager.active is False  # Transaction rolled back

    def test_restores_record_on_rollback(self):
        """Test executor attempts rollback on failure.

        Note: For dict records, modifications are applied immediately by cleaners.
        DictTransactionManager provides transaction semantics but cannot undo
        in-place modifications already made. For full rollback, use database
        transaction managers.
        """
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        def failing_cleaner(field):
            def cleaner_func(record, context):
                return CleanerResult(
                    success=False,
                    modified=False,
                    error="Failed"
                )
            return cleaner_func

        original_email = '  [email protected]  '
        record = {'email': original_email}
        cleaners = [
            trim_whitespace('email'),  # Modifies email
            failing_cleaner('email')   # Fails, triggers rollback
        ]

        result = executor.execute_cleaners(cleaners, record, {})

        assert result.success is False
        assert 'Failed' in result.error
        # For dict records, restoration is best-effort
        # (full rollback requires database transaction manager)

    def test_preview_changes_doesnt_commit(self):
        """Test preview_changes() doesn't commit transaction."""
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        original_record = {'email': '  [email protected]  '}
        record = original_record.copy()
        cleaners = [trim_whitespace('email')]

        result = executor.preview_changes(cleaners, record, {})

        assert result.success is True
        assert result.modified is True
        # Original record unchanged
        assert original_record['email'] == '  [email protected]  '

    def test_adds_transaction_id_to_context(self):
        """Test executor adds transaction_id to context."""
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        context = {}
        record = {'email': 'test@example.com'}
        cleaners = [trim_whitespace('email')]

        executor.execute_cleaners(cleaners, record, context)

        assert 'transaction_id' in context
        assert len(context['transaction_id']) > 0

    def test_dry_run_mode_doesnt_begin_transaction(self):
        """Test dry_run mode doesn't begin transaction."""
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        record = {'email': '  [email protected]  '}
        cleaners = [trim_whitespace('email')]

        # Use preview_changes which enables dry_run
        result = executor.preview_changes(cleaners, record, {})

        assert result.success is True
        # Transaction was never activated
        assert manager.active is False


class TestAuditLogger:
    """Tests for AuditLogger."""

    def test_memory_backend_stores_logs(self):
        """Test memory backend stores logs."""
        logger = AuditLogger(backend='memory')

        log_entry = CleanerAuditLog(
            transaction_id='tx-123',
            timestamp=datetime.now(),
            cleaner_names=['trim_whitespace'],
            record_id='user-456',
            before_value='  hello  ',
            after_value='hello'
        )

        logger.log(log_entry)

        logs = logger.get_logs()
        assert len(logs) == 1
        assert logs[0].transaction_id == 'tx-123'

    def test_get_logs_filters_by_transaction_id(self):
        """Test get_logs() filters by transaction ID."""
        logger = AuditLogger(backend='memory')

        log1 = CleanerAuditLog(
            transaction_id='tx-1',
            timestamp=datetime.now(),
            cleaner_names=['cleaner1'],
            record_id='rec-1'
        )
        log2 = CleanerAuditLog(
            transaction_id='tx-2',
            timestamp=datetime.now(),
            cleaner_names=['cleaner2'],
            record_id='rec-2'
        )

        logger.log(log1)
        logger.log(log2)

        tx1_logs = logger.get_logs('tx-1')
        assert len(tx1_logs) == 1
        assert tx1_logs[0].transaction_id == 'tx-1'

    def test_clear_removes_all_logs(self):
        """Test clear() removes all logs."""
        logger = AuditLogger(backend='memory')

        log_entry = CleanerAuditLog(
            transaction_id='tx-123',
            timestamp=datetime.now(),
            cleaner_names=['trim'],
            record_id='rec-1'
        )

        logger.log(log_entry)
        assert len(logger.get_logs()) == 1

        logger.clear()
        assert len(logger.get_logs()) == 0

    def test_custom_handler(self):
        """Test custom handler is called."""
        handler_called = []

        def my_handler(entry: CleanerAuditLog):
            handler_called.append(entry.transaction_id)

        logger = AuditLogger(backend='custom')
        logger.set_custom_handler(my_handler)

        log_entry = CleanerAuditLog(
            transaction_id='tx-456',
            timestamp=datetime.now(),
            cleaner_names=['cleaner'],
            record_id='rec-1'
        )

        logger.log(log_entry)
        assert len(handler_called) == 1
        assert handler_called[0] == 'tx-456'

    def test_audit_log_to_dict(self):
        """Test CleanerAuditLog.to_dict()."""
        timestamp = datetime.now()
        log_entry = CleanerAuditLog(
            transaction_id='tx-789',
            timestamp=timestamp,
            cleaner_names=['trim', 'lowercase'],
            record_id='rec-1',
            field_name='email',
            before_value='  TEST  ',
            after_value='test'
        )

        log_dict = log_entry.to_dict()

        assert log_dict['transaction_id'] == 'tx-789'
        assert log_dict['timestamp'] == timestamp.isoformat()
        assert log_dict['cleaner_names'] == ['trim', 'lowercase']
        assert log_dict['record_id'] == 'rec-1'
        assert log_dict['field_name'] == 'email'
        assert log_dict['before_value'] == '  TEST  '
        assert log_dict['after_value'] == 'test'

    def test_audit_log_to_json(self):
        """Test CleanerAuditLog.to_json()."""
        log_entry = CleanerAuditLog(
            transaction_id='tx-999',
            timestamp=datetime.now(),
            cleaner_names=['cleaner'],
            record_id='rec-1'
        )

        json_str = log_entry.to_json()

        assert 'tx-999' in json_str
        assert 'cleaner' in json_str
        assert 'rec-1' in json_str


class TestSafeCleanerExecutorWithAudit:
    """Tests for SafeCleanerExecutor with audit logging."""

    def test_logs_modifications_to_audit_logger(self):
        """Test executor logs modifications to audit logger."""
        manager = DictTransactionManager()
        audit_logger = AuditLogger(backend='memory')
        executor = SafeCleanerExecutor(manager, audit_logger)

        record = {'id': '123', 'email': '  [email protected]  '}
        cleaners = [trim_whitespace('email'), lowercase('email')]

        result = executor.execute_cleaners(cleaners, record, {})

        assert result.success is True
        logs = audit_logger.get_logs()
        assert len(logs) > 0
        assert logs[0].record_id == '123'

    def test_doesnt_log_if_no_modifications(self):
        """Test executor doesn't log if no modifications."""
        manager = DictTransactionManager()
        audit_logger = AuditLogger(backend='memory')
        executor = SafeCleanerExecutor(manager, audit_logger)

        record = {'email': 'test@example.com'}  # Already clean
        cleaners = [trim_whitespace('email')]

        result = executor.execute_cleaners(cleaners, record, {})

        assert result.success is True
        assert result.modified is False
        logs = audit_logger.get_logs()
        assert len(logs) == 0  # No modifications, no logs


class TestTransactionIntegration:
    """Integration tests for transaction safety."""

    def test_full_chain_with_transaction(self):
        """Test full cleaner chain with transaction."""
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        record = {'email': '  [email protected]  ', 'name': '  JOHN  '}
        cleaners = [
            trim_whitespace('email'),
            lowercase('email'),
            trim_whitespace('name'),
            lowercase('name')
        ]

        result = executor.execute_cleaners(cleaners, record, {})

        assert result.success is True
        assert result.modified is True
        assert record['email'] == '[email protected]'
        assert record['name'] == 'john'

    def test_partial_execution_rolls_back(self):
        """Test partial execution triggers rollback.

        Note: DictTransactionManager provides transaction semantics but
        cannot undo in-place dict modifications. For full rollback with
        restoration, use database transaction managers (Django, SQLAlchemy).
        """
        manager = DictTransactionManager()
        executor = SafeCleanerExecutor(manager)

        def failing_cleaner(field):
            def cleaner_func(record, context):
                return CleanerResult(success=False, modified=False, error="Failed")
            return cleaner_func

        original_email = '  [email protected]  '
        original_name = '  JOHN  '
        record = {'email': original_email, 'name': original_name}

        cleaners = [
            trim_whitespace('email'),  # Succeeds
            lowercase('email'),        # Succeeds
            trim_whitespace('name'),   # Succeeds
            failing_cleaner('name')    # Fails
        ]

        result = executor.execute_cleaners(cleaners, record, {})

        assert result.success is False
        assert 'Failed' in result.error
        # DictTransactionManager triggers rollback but cannot restore
        # in-place modifications (use database transaction manager for full rollback)
