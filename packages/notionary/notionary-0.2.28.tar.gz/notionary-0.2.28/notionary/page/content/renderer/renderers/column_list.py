from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class ColumnListRenderer(BlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.COLUMN_LIST

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        syntax = self._syntax_registry.get_column_list_syntax()
        column_list_start = syntax.start_delimiter

        if context.indent_level > 0:
            column_list_start = context.indent_text(column_list_start)

        children_markdown = await context.render_children()

        column_list_end = syntax.end_delimiter
        if context.indent_level > 0:
            column_list_end = context.indent_text(column_list_end)

        if children_markdown:
            context.markdown_result = f"{column_list_start}\n{children_markdown}\n{column_list_end}"
        else:
            context.markdown_result = f"{column_list_start}\n{column_list_end}"
