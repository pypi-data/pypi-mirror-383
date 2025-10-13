from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import BlockColor, CreateToggleBlock, CreateToggleData
from notionary.page.content.parser.parsers import (
    BlockParsingContext,
    LineParser,
    ParentBlockContext,
)
from notionary.page.content.syntax.service import SyntaxRegistry


class ToggleParser(LineParser):
    def __init__(self, syntax_registry: SyntaxRegistry, rich_text_converter: MarkdownRichTextConverter) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_toggle_syntax()
        self._heading_syntax = syntax_registry.get_toggleable_heading_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_toggle_start(context) or self._is_toggle_end(context) or self._is_toggle_content(context)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_toggle_start(context):
            await self._start_toggle(context)

        if self._is_toggle_end(context):
            await self._finalize_toggle(context)

        if self._is_toggle_content(context):
            self._add_toggle_content(context)

    def _is_toggle_start(self, context: BlockParsingContext) -> bool:
        if not self._syntax.regex_pattern.match(context.line):
            return False

        # Exclude toggleable heading patterns to be more resilient to wrong order of chain
        return not self.is_heading_start(context.line)

    def is_heading_start(self, line: str) -> bool:
        return self._heading_syntax.regex_pattern.match(line) is not None

    def _is_toggle_end(self, context: BlockParsingContext) -> bool:
        if not self._syntax.end_regex_pattern.match(context.line):
            return False

        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        return isinstance(current_parent.block, CreateToggleBlock)

    async def _start_toggle(self, context: BlockParsingContext) -> None:
        block = await self._create_toggle_block(context.line)
        if not block:
            return

        parent_context = ParentBlockContext(
            block=block,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    async def _create_toggle_block(self, line: str) -> CreateToggleBlock | None:
        if not (match := self._syntax.regex_pattern.match(line)):
            return None

        title = match.group(1).strip()
        rich_text = await self._rich_text_converter.to_rich_text(title)

        toggle_content = CreateToggleData(rich_text=rich_text, color=BlockColor.DEFAULT, children=[])
        return CreateToggleBlock(toggle=toggle_content)

    async def _finalize_toggle(self, context: BlockParsingContext) -> None:
        toggle_context = context.parent_stack.pop()
        await self._assign_toggle_children_if_any(toggle_context, context)

        if self._is_nested_in_other_parent_context(context):
            self._assign_to_parent_context(context, toggle_context)
        else:
            context.result_blocks.append(toggle_context.block)

    def _is_nested_in_other_parent_context(self, context: BlockParsingContext) -> bool:
        return context.parent_stack

    def _assign_to_parent_context(self, context: BlockParsingContext, toggle_context: ParentBlockContext) -> None:
        parent_context = context.parent_stack[-1]
        parent_context.add_child_block(toggle_context.block)

    async def _assign_toggle_children_if_any(
        self, toggle_context: ParentBlockContext, context: BlockParsingContext
    ) -> None:
        all_children = []

        # Process text lines
        if toggle_context.child_lines:
            children_text = "\n".join(toggle_context.child_lines)
            text_blocks = await self._parse_nested_content(children_text, context)
            all_children.extend(text_blocks)

        if toggle_context.child_blocks:
            all_children.extend(toggle_context.child_blocks)

        toggle_context.block.toggle.children = all_children

    def _is_toggle_content(self, context: BlockParsingContext) -> bool:
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not isinstance(current_parent.block, CreateToggleBlock):
            return False

        return not (
            self._syntax.regex_pattern.match(context.line) or self._syntax.end_regex_pattern.match(context.line)
        )

    def _add_toggle_content(self, context: BlockParsingContext) -> None:
        context.parent_stack[-1].add_child_line(context.line)

    async def _parse_nested_content(self, text: str, context: BlockParsingContext) -> list:
        if not text.strip():
            return []

        return await context.parse_nested_content(text)
