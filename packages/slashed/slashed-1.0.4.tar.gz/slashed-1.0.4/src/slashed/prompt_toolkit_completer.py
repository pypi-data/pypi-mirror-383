"""Command completion system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from prompt_toolkit.completion import Completer, Completion

from slashed import CompletionContext
from slashed.log import get_logger
from slashed.store import CommandStore
from slashed.utils import get_first_line


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable

    from prompt_toolkit.document import Document

    from slashed import CommandContext
    from slashed.base import OutputWriter


logger = get_logger(__name__)


class PromptToolkitCompleter[TContextData = Any](Completer):
    """Adapts our completion system to prompt-toolkit."""

    def __init__(
        self,
        store: CommandStore | None = None,
        data: TContextData | None = None,
        output_writer: OutputWriter | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize completer.

        Args:
            store: Command store. Creates an empty one if not provided.
            data: Context data
            output_writer: Optional custom output writer
            metadata: Additional metadata
        """
        self._store = store or CommandStore()
        # Cast to CommandContext[T] since we know the type is preserved
        self._context: CommandContext[TContextData] = store.create_context(  # type: ignore
            data, output_writer, metadata
        )

    def get_completions(
        self, document: Document, complete_event: Any
    ) -> Iterable[Completion]:
        """Sync completions - not used but required by interface."""
        return []

    async def get_completions_async(
        self, document: Document, complete_event: Any
    ) -> AsyncGenerator[Completion]:
        """Get completions for the current context."""
        text = document.text.lstrip()

        if not text.startswith("/"):
            return

        completion_context = CompletionContext[TContextData](
            document, command_context=self._context
        )

        try:
            # If we have a command, use its completer
            if " " in text:  # Has arguments
                cmd_name = text.split()[0][1:]  # Remove slash
                if (command := self._store.get_command(cmd_name)) and (
                    completer := command.get_completer()
                ):
                    current_word = completion_context.current_word
                    async for item in completer.get_completions(completion_context):
                        if current_word and not item.text.startswith(current_word):
                            continue
                        start_pos = -len(current_word) if current_word else 0
                        yield Completion(
                            item.text,
                            start_position=start_pos,
                            display_meta=get_first_line(item.metadata),
                        )
                    return

            # Otherwise complete command names
            word = text[1:]  # Remove slash
            for cmd in self._store.list_commands():
                if cmd.name.startswith(word):
                    yield Completion(
                        cmd.name,
                        start_position=-len(word),
                        display_meta=get_first_line(cmd.description),
                    )

        except RuntimeError as e:
            if "No command context available" in str(e):
                logger.debug(
                    "Command completion failed: command context not provided to "
                    "PromptToolkitCompleter. This is required for argument completion "
                    "but command name completion will still work. Text: '%s'",
                    text,
                )
            else:
                msg = "Unexpected RuntimeError during completion for text '%s': %s"
                logger.debug(msg, text, str(e), exc_info=True)
        except Exception as e:  # noqa: BLE001
            msg = "Completion failed for text '%s': %s (%s)"
            logger.debug(msg, text, str(e), type(e).__name__, exc_info=True)
