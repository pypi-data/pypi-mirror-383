from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import (
    BlockColor,
    CreateNumberedListItemBlock,
    NumberedListItemData,
)
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.service import SyntaxRegistry


class NumberedListParser(LineParser):
    def __init__(self, syntax_registry: SyntaxRegistry, rich_text_converter: MarkdownRichTextConverter) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_numbered_list_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._syntax.regex_pattern.match(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_numbered_list_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_numbered_list_block(self, text: str) -> CreateNumberedListItemBlock | None:
        match = self._syntax.regex_pattern.match(text)
        if not match:
            return None

        content = match.group(3)
        rich_text = await self._rich_text_converter.to_rich_text(content)

        numbered_list_content = NumberedListItemData(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateNumberedListItemBlock(numbered_list_item=numbered_list_content)
