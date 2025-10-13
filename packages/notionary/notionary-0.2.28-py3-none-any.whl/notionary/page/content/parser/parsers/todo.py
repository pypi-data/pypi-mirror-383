"""Parser for todo/checkbox blocks."""

from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BlockColor, CreateToDoBlock, ToDoData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.service import SyntaxRegistry


class TodoParser(LineParser):
    def __init__(self, syntax_registry: SyntaxRegistry, rich_text_converter: MarkdownRichTextConverter) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_todo_syntax()
        self._syntax_done = syntax_registry.get_todo_done_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False

        return (
            self._syntax.regex_pattern.match(context.line) is not None
            or self._syntax_done.regex_pattern.match(context.line) is not None
        )

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_todo_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_todo_block(self, text: str) -> CreateToDoBlock | None:
        done_match = self._syntax_done.regex_pattern.match(text)
        todo_match = None if done_match else self._syntax.regex_pattern.match(text)

        if done_match:
            content = done_match.group(1)
            checked = True
        elif todo_match:
            content = todo_match.group(1)
            checked = False
        else:
            return None

        rich_text = await self._rich_text_converter.to_rich_text(content)
        todo_content = ToDoData(
            rich_text=rich_text,
            checked=checked,
            color=BlockColor.DEFAULT,
        )
        return CreateToDoBlock(to_do=todo_content)
