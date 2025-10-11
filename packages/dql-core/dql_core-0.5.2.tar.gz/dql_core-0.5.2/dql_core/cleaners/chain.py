"""Cleaner chaining for sequential execution (Story 2.6)."""

from typing import Any, List, Union, Callable
from copy import deepcopy

from dql_core.results import CleanerResult
from dql_core.cleaners.registry import default_cleaner_registry


class CleanerChain:
    """
    Execute multiple cleaners in sequence with context sharing.

    Cleaners are executed in order. Execution stops on first error (short-circuit).
    Context is passed between cleaners to enable metadata sharing.

    Example:
        >>> chain = CleanerChain()
        >>> chain.add('trim_whitespace', 'email')
        >>> chain.add('lowercase', 'email')
        >>> chain.add('normalize_email', 'email')
        >>> result = chain.execute(record, {})

        >>> # Chainable syntax
        >>> chain = (CleanerChain()
        ...     .add('trim_whitespace', 'email')
        ...     .add('lowercase', 'email')
        ...     .add('normalize_email', 'email'))

        >>> # From names factory
        >>> chain = CleanerChain.from_names(
        ...     ['trim_whitespace', 'lowercase', 'normalize_email'],
        ...     field_name='email'
        ... )
    """

    def __init__(self, registry=None):
        """
        Initialize empty cleaner chain.

        Args:
            registry: CleanerRegistry to use for name lookups (defaults to default_cleaner_registry)
        """
        self.registry = registry or default_cleaner_registry
        self.cleaners: List[Callable] = []
        self.cleaner_names: List[str] = []

    def add(self, cleaner: Union[str, Callable], *args, **kwargs) -> 'CleanerChain':
        """
        Add a cleaner to the chain.

        Supports two patterns:
        1. String name: Looks up cleaner in registry and calls factory with args/kwargs
        2. Direct function: Uses function as-is (must match cleaner signature)

        Args:
            cleaner: Cleaner name (str) or cleaner function (Callable)
            *args: Arguments to pass to cleaner factory (if cleaner is a name)
            **kwargs: Keyword arguments to pass to cleaner factory (if cleaner is a name)

        Returns:
            Self (for method chaining)

        Example:
            >>> # Add by name with field argument
            >>> chain.add('trim_whitespace', 'email')

            >>> # Add direct function
            >>> def custom_cleaner(record, context):
            ...     return CleanerResult(success=True, modified=False)
            >>> chain.add(custom_cleaner)

            >>> # Chainable syntax
            >>> chain.add('trim_whitespace', 'email').add('lowercase', 'email')
        """
        if isinstance(cleaner, str):
            # Look up by name
            cleaner_factory = self.registry.get(cleaner)
            cleaner_func = cleaner_factory(*args, **kwargs)
            self.cleaner_names.append(cleaner)
        else:
            # Direct function
            cleaner_func = cleaner
            # Extract name from function or use repr
            cleaner_name = getattr(cleaner, '__name__', repr(cleaner))
            self.cleaner_names.append(cleaner_name)

        self.cleaners.append(cleaner_func)
        return self

    def execute(self, record: Any, context: dict) -> CleanerResult:
        """
        Execute all cleaners in sequence.

        Behavior:
        - Executes cleaners sequentially in order added
        - Stops on first error (short-circuit)
        - Passes context between cleaners (with metadata)
        - Aggregates modification tracking
        - Returns consolidated CleanerResult

        Args:
            record: Record to clean
            context: Context dict (will be copied to avoid mutation)

        Returns:
            Consolidated CleanerResult with chain execution results

        Context additions:
            - context['cleaner_chain']: Chain metadata (current_step, total_steps, cleaner_names)
            - context['previous_result']: Result from previous cleaner in chain

        Example:
            >>> record = {'email': '  [email protected]  '}
            >>> result = chain.execute(record, {})
            >>> print(result.success, result.modified, record['email'])
            True True [email protected]
        """
        # Handle empty chain
        if not self.cleaners:
            return CleanerResult(
                success=True,
                modified=False,
                before_value=None,
                after_value=None,
                error=None
            )

        # Initialize tracking
        total_modified = False
        all_before_values = []
        all_after_values = []
        chain_context = deepcopy(context)

        # Add chain metadata to context
        chain_context['cleaner_chain'] = {
            'total_steps': len(self.cleaners),
            'current_step': 0,
            'cleaner_names': self.cleaner_names.copy()
        }

        # Execute cleaners
        for i, cleaner_func in enumerate(self.cleaners):
            # Update current step
            chain_context['cleaner_chain']['current_step'] = i

            # Execute cleaner
            result = cleaner_func(record, chain_context)

            # Check for error - short-circuit
            if not result.success:
                return CleanerResult(
                    success=False,
                    modified=total_modified,
                    before_value=all_before_values[0] if all_before_values else None,
                    after_value=all_after_values[-1] if all_after_values else None,
                    error=f"Cleaner '{self.cleaner_names[i]}' failed: {result.error}"
                )

            # Track modifications
            if result.modified:
                total_modified = True
                all_before_values.append(result.before_value)
                all_after_values.append(result.after_value)

            # Update context with previous result
            chain_context['previous_result'] = result

        # Return consolidated result
        return CleanerResult(
            success=True,
            modified=total_modified,
            before_value=all_before_values[0] if all_before_values else None,
            after_value=all_after_values[-1] if all_after_values else None,
            error=None
        )

    @classmethod
    def from_names(cls, cleaner_names: List[str], field_name: str, registry=None) -> 'CleanerChain':
        """
        Create chain from list of cleaner names (all applied to same field).

        This is a convenience factory method for the common case where multiple
        cleaners are applied to the same field.

        Args:
            cleaner_names: List of cleaner names (e.g., ['trim_whitespace', 'lowercase'])
            field_name: Field to apply all cleaners to
            registry: CleanerRegistry to use (defaults to default_cleaner_registry)

        Returns:
            CleanerChain instance with all cleaners added

        Example:
            >>> chain = CleanerChain.from_names(
            ...     ['trim_whitespace', 'lowercase', 'normalize_email'],
            ...     field_name='email'
            ... )
            >>> result = chain.execute(record, {})
        """
        chain = cls(registry)
        for name in cleaner_names:
            chain.add(name, field_name)
        return chain

    def __len__(self) -> int:
        """Return number of cleaners in chain."""
        return len(self.cleaners)

    def __repr__(self) -> str:
        """Return string representation of chain."""
        return f"CleanerChain(cleaners={self.cleaner_names})"
