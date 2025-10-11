"""Tests for CleanerChain (Story 2.6)."""

import pytest
from dql_core.cleaners.chain import CleanerChain
from dql_core.cleaners import CleanerRegistry
from dql_core.results import CleanerResult


class TestCleanerChainBasics:
    """Tests for basic CleanerChain functionality."""

    def test_empty_chain_returns_success(self):
        """Test empty chain returns success result."""
        chain = CleanerChain()
        result = chain.execute({'field': 'value'}, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value is None
        assert result.after_value is None

    def test_chain_add_returns_self(self):
        """Test add() returns self for chaining."""
        registry = CleanerRegistry()

        def cleaner_factory(field_name):
            def cleaner_func(record, context):
                """Test cleaner."""
                return CleanerResult(success=True, modified=False)
            return cleaner_func

        registry.register('test_cleaner', cleaner_factory)

        chain = CleanerChain(registry=registry)
        result = chain.add('test_cleaner', 'field')

        assert result is chain  # Should return self

    def test_chain_length(self):
        """Test __len__ returns number of cleaners."""
        registry = CleanerRegistry()

        def cleaner_factory(field_name):
            def cleaner_func(record, context):
                """Test cleaner."""
                return CleanerResult(success=True, modified=False)
            return cleaner_func

        registry.register('test_cleaner', cleaner_factory)

        chain = CleanerChain(registry=registry)
        assert len(chain) == 0

        chain.add('test_cleaner', 'field1')
        assert len(chain) == 1

        chain.add('test_cleaner', 'field2')
        assert len(chain) == 2

    def test_chain_repr(self):
        """Test __repr__ shows cleaner names."""
        registry = CleanerRegistry()

        def cleaner_factory(field_name):
            def cleaner_func(record, context):
                """Test cleaner."""
                return CleanerResult(success=True, modified=False)
            return cleaner_func

        registry.register('cleaner1', cleaner_factory)
        registry.register('cleaner2', cleaner_factory)

        chain = CleanerChain(registry=registry)
        chain.add('cleaner1', 'field')
        chain.add('cleaner2', 'field')

        repr_str = repr(chain)
        assert 'CleanerChain' in repr_str
        assert 'cleaner1' in repr_str
        assert 'cleaner2' in repr_str


class TestCleanerChainExecution:
    """Tests for CleanerChain execution behavior."""

    def test_executes_cleaners_sequentially(self):
        """Test cleaners execute in order added."""
        execution_order = []

        def cleaner1(record, context):
            """First cleaner."""
            execution_order.append(1)
            record['value'] = record['value'] + '_c1'
            return CleanerResult(success=True, modified=True,
                               before_value=record['value'], after_value=record['value'])

        def cleaner2(record, context):
            """Second cleaner."""
            execution_order.append(2)
            record['value'] = record['value'] + '_c2'
            return CleanerResult(success=True, modified=True,
                               before_value=record['value'], after_value=record['value'])

        chain = CleanerChain()
        chain.add(cleaner1)
        chain.add(cleaner2)

        record = {'value': 'start'}
        result = chain.execute(record, {})

        assert result.success is True
        assert result.modified is True
        assert execution_order == [1, 2]  # Executed in order
        assert record['value'] == 'start_c1_c2'

    def test_short_circuits_on_error(self):
        """Test chain stops on first error."""
        execution_order = []

        def success_cleaner(record, context):
            """Successful cleaner."""
            execution_order.append('success')
            return CleanerResult(success=True, modified=False)

        def failing_cleaner(record, context):
            """Failing cleaner."""
            execution_order.append('fail')
            return CleanerResult(success=False, modified=False, error="Failed!")

        def should_not_execute(record, context):
            """Should not execute."""
            execution_order.append('skipped')
            return CleanerResult(success=True, modified=False)

        chain = CleanerChain()
        chain.add(success_cleaner)
        chain.add(failing_cleaner)
        chain.add(should_not_execute)

        result = chain.execute({'field': 'value'}, {})

        assert result.success is False
        assert 'Failed!' in result.error
        assert execution_order == ['success', 'fail']  # Third cleaner not executed
        assert 'skipped' not in execution_order

    def test_aggregates_modifications(self):
        """Test chain tracks if any cleaner modified record."""
        def no_modify(record, context):
            """No modification."""
            return CleanerResult(success=True, modified=False)

        def modifies(record, context):
            """Modifies record."""
            record['field'] = 'modified'
            return CleanerResult(success=True, modified=True,
                               before_value='old', after_value='modified')

        chain = CleanerChain()
        chain.add(no_modify)
        chain.add(modifies)
        chain.add(no_modify)

        result = chain.execute({'field': 'old'}, {})

        assert result.success is True
        assert result.modified is True  # At least one cleaner modified

    def test_passes_context_between_cleaners(self):
        """Test context is shared between cleaners."""
        def cleaner1(record, context):
            """First cleaner adds to context."""
            assert 'cleaner_chain' in context
            assert context['cleaner_chain']['total_steps'] == 2
            assert context['cleaner_chain']['current_step'] == 0
            return CleanerResult(success=True, modified=False)

        def cleaner2(record, context):
            """Second cleaner checks context."""
            assert 'cleaner_chain' in context
            assert context['cleaner_chain']['total_steps'] == 2
            assert context['cleaner_chain']['current_step'] == 1
            assert 'previous_result' in context
            return CleanerResult(success=True, modified=False)

        chain = CleanerChain()
        chain.add(cleaner1)
        chain.add(cleaner2)

        result = chain.execute({'field': 'value'}, {})
        assert result.success is True

    def test_context_has_chain_metadata(self):
        """Test context includes chain metadata."""
        captured_context = {}

        def capture_context(record, context):
            """Capture context for inspection."""
            captured_context.update(context)
            return CleanerResult(success=True, modified=False)

        chain = CleanerChain()
        chain.add(capture_context)

        chain.execute({'field': 'value'}, {})

        assert 'cleaner_chain' in captured_context
        assert 'total_steps' in captured_context['cleaner_chain']
        assert 'current_step' in captured_context['cleaner_chain']
        assert 'cleaner_names' in captured_context['cleaner_chain']

    def test_context_has_previous_result(self):
        """Test second cleaner receives previous_result in context."""
        previous_result_received = {}

        def cleaner1(record, context):
            """First cleaner."""
            return CleanerResult(success=True, modified=True,
                               before_value='old', after_value='new')

        def cleaner2(record, context):
            """Second cleaner checks previous_result."""
            assert 'previous_result' in context
            previous_result_received['result'] = context['previous_result']
            return CleanerResult(success=True, modified=False)

        chain = CleanerChain()
        chain.add(cleaner1)
        chain.add(cleaner2)

        chain.execute({'field': 'value'}, {})

        assert 'result' in previous_result_received
        assert previous_result_received['result'].success is True
        assert previous_result_received['result'].modified is True

    def test_context_isolation(self):
        """Test input context is not mutated."""
        original_context = {'custom_key': 'original_value'}

        def cleaner_func(record, context):
            """Cleaner that modifies context."""
            context['custom_key'] = 'modified_value'
            return CleanerResult(success=True, modified=False)

        chain = CleanerChain()
        chain.add(cleaner_func)

        chain.execute({'field': 'value'}, original_context)

        # Original context should be unchanged (deepcopy)
        assert original_context['custom_key'] == 'original_value'


class TestCleanerChainWithBuiltinCleaners:
    """Tests using built-in cleaners with CleanerChain."""

    def test_chain_with_string_cleaners(self):
        """Test chain with string cleaner names."""
        from dql_core.cleaners import default_cleaner_registry

        chain = CleanerChain(registry=default_cleaner_registry)
        chain.add('trim_whitespace', 'email')
        chain.add('lowercase', 'email')

        record = {'email': '  [email protected]  '}
        result = chain.execute(record, {})

        assert result.success is True
        assert result.modified is True
        assert record['email'] == '[email protected]'

    def test_chain_with_direct_functions(self):
        """Test chain with direct cleaner functions."""
        def custom_cleaner(record, context):
            """Custom cleaner."""
            record['field'] = record['field'].upper()
            return CleanerResult(success=True, modified=True,
                               before_value='old', after_value=record['field'])

        chain = CleanerChain()
        chain.add(custom_cleaner)

        record = {'field': 'hello'}
        result = chain.execute(record, {})

        assert result.success is True
        assert result.modified is True
        assert record['field'] == 'HELLO'

    def test_chain_mixed_names_and_functions(self):
        """Test chain with mix of names and direct functions."""
        from dql_core.cleaners import default_cleaner_registry

        def custom_cleaner(record, context):
            """Custom cleaner."""
            record['email'] = '!' + record['email']
            return CleanerResult(success=True, modified=True)

        chain = CleanerChain(registry=default_cleaner_registry)
        chain.add('trim_whitespace', 'email')
        chain.add(custom_cleaner)
        chain.add('lowercase', 'email')

        record = {'email': '  [email protected]  '}
        result = chain.execute(record, {})

        assert result.success is True
        assert result.modified is True
        assert record['email'] == '![email protected]'


class TestCleanerChainFromNames:
    """Tests for CleanerChain.from_names factory method."""

    def test_from_names_creates_chain(self):
        """Test from_names creates chain from list of names."""
        from dql_core.cleaners import default_cleaner_registry

        chain = CleanerChain.from_names(
            ['trim_whitespace', 'lowercase'],
            field_name='email',
            registry=default_cleaner_registry
        )

        assert len(chain) == 2
        assert chain.cleaner_names == ['trim_whitespace', 'lowercase']

    def test_from_names_executes_correctly(self):
        """Test from_names chain executes correctly."""
        from dql_core.cleaners import default_cleaner_registry

        chain = CleanerChain.from_names(
            ['trim_whitespace', 'lowercase', 'normalize_email'],
            field_name='email',
            registry=default_cleaner_registry
        )

        record = {'email': '  [email protected]  '}
        result = chain.execute(record, {})

        assert result.success is True
        assert result.modified is True
        assert record['email'] == '[email protected]'

    def test_from_names_empty_list(self):
        """Test from_names with empty list."""
        chain = CleanerChain.from_names([], field_name='email')

        assert len(chain) == 0

        result = chain.execute({'email': 'test'}, {})
        assert result.success is True
        assert result.modified is False


class TestCleanerChainErrorHandling:
    """Tests for CleanerChain error handling."""

    def test_error_includes_cleaner_name(self):
        """Test error message includes cleaner name."""
        def failing_cleaner(record, context):
            """Failing cleaner."""
            return CleanerResult(success=False, modified=False, error="Original error")

        failing_cleaner.__name__ = 'my_failing_cleaner'

        chain = CleanerChain()
        chain.add(failing_cleaner)

        result = chain.execute({'field': 'value'}, {})

        assert result.success is False
        assert 'my_failing_cleaner' in result.error
        assert 'Original error' in result.error

    def test_tracks_modifications_before_error(self):
        """Test chain tracks modifications that happened before error."""
        def modifies(record, context):
            """Modifies record."""
            record['field'] = 'modified'
            return CleanerResult(success=True, modified=True,
                               before_value='old', after_value='modified')

        def fails(record, context):
            """Fails."""
            return CleanerResult(success=False, modified=False, error="Failed")

        chain = CleanerChain()
        chain.add(modifies)
        chain.add(fails)

        record = {'field': 'old'}
        result = chain.execute(record, {})

        assert result.success is False
        assert result.modified is True  # First cleaner did modify
        assert record['field'] == 'modified'  # Modification persisted
