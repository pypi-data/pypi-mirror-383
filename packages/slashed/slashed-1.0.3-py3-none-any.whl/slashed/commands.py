"""Declarative command system."""

from __future__ import annotations

from abc import abstractmethod
import inspect
from typing import Any, get_type_hints

from slashed.base import BaseCommand, CommandContext
from slashed.exceptions import CommandError


class SlashedCommand(BaseCommand):
    """Base class for declarative commands.

    Allows defining commands using class syntax with explicit parameters:

    Example:
        class AddWorkerCommand(SlashedCommand):
            '''Add a new worker to the pool.'''

            name = "add-worker"
            category = "tools"

            async def execute_command(
                self,
                ctx: CommandContext,  # Optional depending on implementation
                worker_id: str,       # required param (no default)
                host: str,            # required param (no default)
                port: int = 8080,     # optional param (has default)
            ):
                await ctx.output.print(f"Adding worker {worker_id} at {host}:{port}")

        # Context-free command
        class VersionCommand(SlashedCommand):
            '''Show version information.'''

            name = "version"

            async def execute_command(self, major: int, minor: int = 0):
                return f"v{major}.{minor}"
    """

    name: str
    """Command name"""

    category: str = "general"
    """Command category"""

    description: str = ""
    """Optional description override"""

    usage: str | None = None
    """Optional usage override"""

    help_text: str = ""
    """Optional help text override"""

    def __init__(self):
        """Initialize command instance."""
        self.description = (
            self.description or inspect.getdoc(self.__class__) or "No description"
        )
        self.help_text = type(self).help_text or self.description

    def __init_subclass__(cls):
        """Process command class at definition time.

        Validates required attributes and generates description/usage from metadata.
        """
        super().__init_subclass__()

        if not hasattr(cls, "name"):
            msg = f"Command class {cls.__name__} must define 'name' attribute"
            raise TypeError(msg)

        # Get description from docstring if empty
        if not cls.description:
            cls.description = inspect.getdoc(cls) or "No description"

        # Generate usage from execute signature if not set
        if cls.usage is None:
            sig = inspect.signature(cls.execute_command)
            params = list(sig.parameters.items())

            # Skip self parameter
            params = params[1:]

            # Check if first parameter is a context
            if params and cls._is_context_param(params[0][0], cls.execute_command):
                # Skip context parameter
                params = params[1:]

            usage_params = []
            for name, param in params:
                if param.default == inspect.Parameter.empty:
                    usage_params.append(f"<{name}>")
                else:
                    usage_params.append(f"[--{name} <value>]")
            cls.usage = " ".join(usage_params)

    @staticmethod
    def _is_context_param(param_name: str, method) -> bool:
        """Determine if a parameter is likely a context parameter."""
        try:
            hints = get_type_hints(method)
            if param_name in hints:
                hint = hints[param_name]
                # Check if type is CommandContext or a subclass/generic of it
                origin = getattr(hint, "__origin__", hint)
                if origin is CommandContext or (
                    isinstance(origin, type) and issubclass(origin, CommandContext)
                ):
                    return True
        except (TypeError, AttributeError):
            # If we can't determine type hints, check by name
            return param_name in ("ctx", "context")

        return False

    @abstractmethod
    async def execute_command(
        self,
        *args: Any,
        **kwargs: Any,
    ):
        """Execute the command logic.

        This method should be implemented with explicit parameters.
        Parameters without default values are treated as required.

        Args:
            args: Command arguments (may include context as first param)
            kwargs: Command keyword arguments
        """

    async def execute(
        self,
        ctx: CommandContext,
        args: list[str],
        kwargs: dict[str, str],
    ):
        """Execute command by binding command-line arguments to method parameters."""
        # Get concrete method's signature
        method = type(self).execute_command
        sig = inspect.signature(method)

        # Get parameter information (skip self)
        parameters = dict(list(sig.parameters.items())[1:])

        # Check if we need to pass context
        param_names = list(parameters.keys())
        has_ctx = param_names and self._is_context_param(param_names[0], method)

        # Prepare parameters for matching, excluding context if present
        if has_ctx:
            ctx_param_name = param_names[0]
            parameters_for_matching = {
                k: v for k, v in parameters.items() if k != ctx_param_name
            }
            call_args: list[str | CommandContext] = [ctx]  # Add context as first argument
        else:
            parameters_for_matching = parameters
            call_args = []  # No context parameter

        # Get required parameters in order (excluding context if applicable)
        required = [
            name
            for name, param in parameters_for_matching.items()
            if param.default == inspect.Parameter.empty
        ]

        # Check if required args are provided either as positional or keyword
        missing = [
            name
            for idx, name in enumerate(required)
            if name not in kwargs and len(args) < idx + 1
        ]

        if missing:
            msg = f"Missing required arguments: {missing}"
            raise CommandError(msg)

        # Validate keyword arguments
        for name in kwargs:
            if name not in parameters_for_matching:
                msg = f"Unknown argument: {name}"
                raise CommandError(msg)

        # Add positional arguments
        call_args.extend(args)

        # Call with positional args first, then kwargs
        return await self.execute_command(*call_args, **kwargs)
