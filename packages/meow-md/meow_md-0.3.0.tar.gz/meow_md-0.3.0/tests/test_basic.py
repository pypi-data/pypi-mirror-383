import unittest
from rich.text import Text
from rich.table import Table
from meow.meow import wrap_paragraph, blockquote, render_markdown


class TestMarkdownRenderer(unittest.TestCase):
    def test_wrap_paragraph_basic(self):
        text = Text("Hello world, this is a test.")
        wrapped = wrap_paragraph(text, width=10)
        self.assertIsInstance(wrapped, Text)
        self.assertIn("Hello", wrapped.plain)

    def test_blockquote_prefix(self):
        text = Text("Blockquote content")
        bq = blockquote(text, width=20)
        self.assertIsInstance(bq, Text)
        self.assertTrue(bq.plain.startswith("❙ "))

    def test_render_markdown_heading(self):
        md_text = "# Heading\n\nSome text"
        output = render_markdown(md_text)
        self.assertIsInstance(output, list)
        self.assertTrue(any("Heading" in chunk.plain for chunk in output))

    def test_render_markdown_list(self):
        md_text = "- Item 1\n- Item 2"
        output = render_markdown(md_text)
        self.assertTrue(any("•" in chunk.plain for chunk in output))

    def test_render_markdown_inline(self):
        md_text = "This is `code` and a [link](https://example.com)"
        output = render_markdown(md_text)
        self.assertTrue(any("code" in chunk.plain for chunk in output))
        self.assertTrue(any("link" in chunk.plain for chunk in output))

    def test_render_markdown_blockquote(self):
        md_text = "> A blockquote line"
        output = render_markdown(md_text)
        self.assertTrue(any("A blockquote line" in chunk.plain for chunk in output))

    def test_render_markdown_skip_yaml(self):
        md_text = "---\nname: Test\n---\n# Heading\nContent"
        output = render_markdown(md_text)
        # YAML frontmatter should not appear
        self.assertFalse(any("name: Test" in chunk.plain for chunk in output))
        self.assertTrue(any("Heading" in chunk.plain for chunk in output))

    def test_render_markdown_code_block_indent(self):
        md_text = "```\nprint('hello')\n```"
        output = render_markdown(md_text)
        # Look for a line starting with exactly two spaces
        code_lines = [chunk.plain for chunk in output if "print" in chunk.plain]
        self.assertTrue(any(line.startswith("  ") for line in code_lines))

    def test_render_markdown_bold_and_italic(self):
        md_text = "This has *italic* and **bold** text, and ***both*** styles together."
        output = render_markdown(md_text)
        italics_found = False
        bold_found = False
        both_found = False
        for chunk in output:
            for start, end, style in chunk.spans:
                if "italic" in style and "bold" not in style:
                    if "italic" in chunk.plain[start:end]:
                        italics_found = True
                if "bold" in style and "italic" not in style:
                    if "bold" in chunk.plain[start:end]:
                        bold_found = True
                if "bold" in style and "italic" in style:
                    if "both" in chunk.plain[start:end]:
                        both_found = True
        self.assertTrue(italics_found, "Italic text not styled correctly")
        self.assertTrue(bold_found, "Bold text not styled correctly")
        self.assertTrue(both_found, "Bold+italic text not styled correctly")

    def test_render_markdown_inline_code_style(self):
        md_text = "Here is some `inline` code."
        output = render_markdown(md_text)
        code_found = False
        for chunk in output:
            for start, end, style in chunk.spans:
                if "red" in style and "black" in style:
                    if "inline" in chunk.plain[start:end]:
                        code_found = True
        self.assertTrue(code_found, "Inline code not styled red on black")

    def test_render_markdown_table_basic(self):
        """Test that a basic markdown table is rendered as a Rich Table."""
        md_text = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        output = render_markdown(md_text)

        # Find Table objects in output
        tables = [chunk for chunk in output if isinstance(chunk, Table)]
        self.assertEqual(len(tables), 1, "Expected exactly one table to be rendered")

        table = tables[0]
        # Check that headers are present
        self.assertEqual(len(table.columns), 2, "Expected 2 columns")
        self.assertEqual(table.columns[0].header, "Header 1")
        self.assertEqual(table.columns[1].header, "Header 2")

    def test_render_markdown_table_with_alignment(self):
        """Test that table alignment is respected."""
        md_text = """
| Left | Center | Right |
|:-----|:------:|------:|
| L1   | C1     | R1    |
"""
        output = render_markdown(md_text)
        tables = [chunk for chunk in output if isinstance(chunk, Table)]
        self.assertEqual(len(tables), 1)

        table = tables[0]
        self.assertEqual(len(table.columns), 3)
        self.assertEqual(table.columns[0].justify, "left")
        self.assertEqual(table.columns[1].justify, "center")
        self.assertEqual(table.columns[2].justify, "right")

    def test_render_markdown_table_with_inline_formatting(self):
        """Test that inline markdown (bold, italic, code) works in table cells."""
        md_text = """
| Format | Example |
|--------|---------|
| Bold   | **bold text** |
| Italic | *italic text* |
| Code   | `code` |
"""
        output = render_markdown(md_text)
        tables = [chunk for chunk in output if isinstance(chunk, Table)]
        self.assertEqual(len(tables), 1)

        table = tables[0]
        # Check that we have the expected number of rows
        self.assertEqual(len(table.rows), 3)

        # Verify cells contain the formatted text
        # Rich Table stores rows as lists of renderables
        row_texts = []
        for row in table.rows:
            row_texts.append(
                [
                    str(cell.plain) if hasattr(cell, "plain") else str(cell)
                    for cell in row
                ]
            )

        # Check that content is present (exact styling verification is complex with Rich)
        self.assertTrue(
            any("bold text" in str(cell) for row in row_texts for cell in row)
        )
        self.assertTrue(
            any("italic text" in str(cell) for row in row_texts for cell in row)
        )
        self.assertTrue(any("code" in str(cell) for row in row_texts for cell in row))

    def test_render_markdown_table_multiple_rows(self):
        """Test table with multiple data rows."""
        md_text = """
| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |
| Carol | 35 |
"""
        output = render_markdown(md_text)
        tables = [chunk for chunk in output if isinstance(chunk, Table)]
        self.assertEqual(len(tables), 1)

        table = tables[0]
        self.assertEqual(len(table.rows), 3, "Expected 3 data rows")

    def test_render_markdown_table_empty_cells(self):
        """Test that tables handle empty cells gracefully."""
        md_text = """
| Col1 | Col2 | Col3 |
|------|------|------|
| A    |      | C    |
|      | B    |      |
"""
        output = render_markdown(md_text)
        tables = [chunk for chunk in output if isinstance(chunk, Table)]
        self.assertEqual(len(tables), 1)

        table = tables[0]
        self.assertEqual(len(table.rows), 2)

    def test_render_markdown_table_with_links(self):
        """Test that links work inside table cells."""
        md_text = """
| Site | URL |
|------|-----|
| Example | [Link](https://example.com) |
"""
        output = render_markdown(md_text)
        tables = [chunk for chunk in output if isinstance(chunk, Table)]
        self.assertEqual(len(tables), 1)

        # Verify the link text appears in the table
        table = tables[0]
        self.assertEqual(len(table.rows), 1)
        # Check that link content is present
        row_content = str(table.rows[0])
        self.assertIn("Link", row_content)

    def test_render_markdown_no_table_without_header(self):
        """Test that malformed tables (no header) don't crash."""
        md_text = """
|------|------|
| A    | B    |
"""
        output = render_markdown(md_text)
        # Should not crash, just won't render as a table
        self.assertIsInstance(output, list)

    def test_render_markdown_table_followed_by_paragraph(self):
        """Test that content after a table renders correctly."""
        md_text = """
| Header |
|--------|
| Cell   |

This is a paragraph after the table.
"""
        output = render_markdown(md_text)

        # Should have a table and some text
        tables = [chunk for chunk in output if isinstance(chunk, Table)]
        self.assertEqual(len(tables), 1)

        # Check paragraph appears
        text_chunks = [chunk for chunk in output if isinstance(chunk, Text)]
        paragraph_found = any(
            "paragraph after the table" in chunk.plain for chunk in text_chunks
        )
        self.assertTrue(paragraph_found)


if __name__ == "__main__":
    unittest.main()
