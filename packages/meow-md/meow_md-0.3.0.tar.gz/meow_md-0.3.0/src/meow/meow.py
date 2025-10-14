#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.lexers import TextLexer
from pygments.formatters import TerminalFormatter
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich import box
from io import StringIO

# Force pager to `less -R` (preserve colors)
os.environ["PAGER"] = "less"
os.environ["LESS"] = "-RFX"  # -R keep colors, -F quit if fits, -X don't clear screen

console = Console(force_terminal=True, color_system="truecolor", width=120)

md = MarkdownIt("commonmark", {"breaks": True}).enable("table")


HEADING_STYLES = {
    1: "bold white on blue",
    2: "bold green",
    3: "bold yellow",
    4: "bold blue",
    5: "bold magenta",
    6: "bold cyan",
}


def wrap_paragraph(text_obj: Text, width: int = 120) -> Text:
    """Wrap a Rich Text object to specified width."""
    wrapped = Text()
    lines = []

    for line in text_obj.wrap(console, width):
        if line is not None:
            lines.append(line)

    for i, line in enumerate(lines):
        wrapped.append(line)
        # only add newlines between wrapped lines, not after the last one
        if i < len(lines) - 1:
            wrapped.append("\n")

    return wrapped


def blockquote(text_obj: Text, width: int = 120) -> Text:
    """Wrap blockquotes to start every line with a bar prefix."""
    prefix = "❙ "
    wrapped = Text()
    lines = []

    # wrap text according to available width
    for line in text_obj.wrap(console, width - len(prefix)):
        if line is not None:
            lines.append(line)

    # append each line with styled prefix
    for i, line in enumerate(lines):
        wrapped.append(prefix, style="magenta")
        wrapped.append(line)
        if i < len(lines) - 1:
            wrapped.append("\n")

    return wrapped


def strip_yaml_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- at start and end) if present."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip("\n")
    return text


def strip_anchor_links(text: str) -> str:
    """Remove standalone HTML anchor links like <a name="foo"></a>."""
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<a") and stripped.endswith("</a>"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).lstrip("\n")


def parse_inline_markdown(children) -> Text:
    """Parse inline markdown tokens (bold, italic, code, links) into Rich Text."""
    text = Text()
    style_stack = []

    i = 0
    while i < len(children):
        child = children[i]

        if child.type == "text":
            style = ""
            if "em" in style_stack:
                style += " italic"
            if "strong" in style_stack:
                style += " bold"
            text.append(child.content, style=style.strip() or None)

        elif child.type == "code_inline":
            text.append(f" {child.content} ", style="red on black")

        elif child.type == "strong_open":
            style_stack.append("strong")
        elif child.type == "strong_close":
            if "strong" in style_stack:
                style_stack.remove("strong")

        elif child.type == "em_open":
            style_stack.append("em")
        elif child.type == "em_close":
            if "em" in style_stack:
                style_stack.remove("em")

        elif child.type == "link_open":
            href = child.attrs.get("href", "")
            label = ""
            j = i + 1
            while j < len(children) and children[j].type != "link_close":
                if children[j].type == "text":
                    label += children[j].content
                j += 1

            text.append(label, style="bold bright_cyan")
            if href and href != label:
                text.append(" ")
                text.append(href, style="underline cyan")

            i = j

        i += 1

    return text


def render_to_string_with_colors(chunks):
    """Render chunks to a string buffer while preserving ANSI colors."""
    # Create a string buffer to capture console output
    string_buffer = StringIO()
    temp_console = Console(
        file=string_buffer,
        force_terminal=True,
        color_system="truecolor",
        width=console.width,
    )

    temp_console.print()  # Initial blank line
    for chunk in chunks:
        temp_console.print(chunk)

    return string_buffer.getvalue()


def count_display_lines(text_with_ansi):
    """Count the number of display lines in text with ANSI codes."""
    return len(text_with_ansi.splitlines())


def render_markdown(text: str):
    """Render Markdown text to Rich Text objects, skipping YAML frontmatter and fenced YAML blocks."""
    # remove YAML frontmatter first
    text = strip_yaml_frontmatter(text)
    text = strip_anchor_links(text)

    tokens = md.parse(text)
    output = []

    current_heading_level = None
    list_stack = []
    pending_list_marker = None
    in_blockquote = False
    in_list = False

    # Table state
    in_table = False
    table_headers = []
    table_rows = []
    table_alignments = []

    i = 0
    while i < len(tokens):
        token = tokens[i]

        # TABLES
        if token.type == "table_open":
            in_table = True
            table_headers = []
            table_rows = []
            table_alignments = []

        elif token.type == "table_close":
            # Render the complete table
            if table_headers:
                table = Table(
                    box=box.SQUARE, show_header=True, header_style="bold white"
                )

                # Add columns with alignments
                for idx, header in enumerate(table_headers):
                    align = (
                        table_alignments[idx] if idx < len(table_alignments) else "left"
                    )
                    table.add_column(header, justify=align)

                # Add rows
                for row in table_rows:
                    table.add_row(*row)

                output.append(table)
                output.append(Text())

            in_table = False
            table_headers = []
            table_rows = []
            table_alignments = []

        elif token.type == "thead_open":
            pass
        elif token.type == "thead_close":
            pass
        elif token.type == "tbody_open":
            pass
        elif token.type == "tbody_close":
            pass

        elif token.type == "tr_open":
            pass
        elif token.type == "tr_close":
            pass

        elif token.type == "th_open":
            # Capture alignment from token attrs
            align = "left"
            if hasattr(token, "attrs") and token.attrs:
                style_attr = token.attrs.get("style", "")
                if "text-align:center" in style_attr:
                    align = "center"
                elif "text-align:right" in style_attr:
                    align = "right"
            table_alignments.append(align)

            # Get the header content from next inline token
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                inline_token = tokens[i + 1]
                header_text = parse_inline_markdown(inline_token.children or [])
                table_headers.append(str(header_text.plain))
                i += 1  # Skip the inline token

        elif token.type == "th_close":
            pass

        elif token.type == "td_open":
            # Get the cell content from next inline token
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                inline_token = tokens[i + 1]
                cell_text = parse_inline_markdown(inline_token.children or [])

                # Initialize new row if needed
                if not table_rows or len(table_rows[-1]) == len(table_headers):
                    table_rows.append([])

                table_rows[-1].append(cell_text)
                i += 1  # Skip the inline token

        elif token.type == "td_close":
            pass

        # HEADINGS
        elif token.type == "heading_open":
            current_heading_level = int(token.tag[1])

        elif token.type == "inline" and current_heading_level is not None:
            # extract text content from children
            content_parts = [
                child.content for child in token.children if child.type == "text"
            ]
            content = "".join(content_parts)

            # skip headings that are just '---' (they were YAML frontmatter)
            if content.strip() == "---":
                current_heading_level = None
                i += 1
                continue

            hashes = "#" * current_heading_level
            style = HEADING_STYLES.get(current_heading_level, "bold")

            if current_heading_level == 1:
                output.append(Text(f" {content} ", style=style))
            else:
                output.append(Text(f"{hashes} {content}", style=style))
            output.append(Text())
            current_heading_level = None

        elif token.type == "heading_close":
            pass

        # CODE BLOCKS
        elif token.type == "fence":
            lang = token.info.lower().strip() if token.info else ""
            code = token.content.rstrip("\n")

            # detect YAML frontmatter
            is_yaml = (lang in ("yaml", "yml")) or code.startswith("---")
            if is_yaml:
                i += 1
                continue  # skip YAML completely

            try:
                if lang:
                    lexer = get_lexer_by_name(lang)
                else:
                    lexer = TextLexer()
            except Exception:
                lexer = TextLexer()

            formatter = TerminalFormatter(bg="dark")
            highlighted = highlight(code, lexer, formatter)

            # prefix each line with 2 spaces
            for line in highlighted.rstrip("\n").split("\n"):
                indented = Text("  ")
                indented.append(Text.from_ansi(line, no_wrap=True))
                output.append(indented)

            # add bottom margin
            output.append(Text())

        # LISTS
        elif token.type == "bullet_list_open":
            list_stack.append(("ul", 0))
            in_list = True
        elif token.type == "ordered_list_open":
            list_stack.append(("ol", 1))
            in_list = True

        elif token.type == "list_item_open":
            if list_stack:
                depth = len(list_stack)
                typ, num = list_stack[-1]
                indent = "  " * (depth - 1)
                if typ == "ul":
                    pending_list_marker = f"{indent}• "
                elif typ == "ol":
                    pending_list_marker = f"{indent}{num}. "
                    list_stack[-1] = (typ, num + 1)

        elif token.type == "list_item_close":
            pending_list_marker = None

        elif token.type in ("bullet_list_close", "ordered_list_close"):
            list_stack.pop()
            if not list_stack:
                in_list = False
                output.append(Text())

        # BLOCKQUOTES
        elif token.type == "blockquote_open":
            in_blockquote = True

        elif token.type == "blockquote_close":
            in_blockquote = False

        # PARAGRAPH MARKERS
        elif token.type == "paragraph_open":
            pass
        elif token.type == "paragraph_close":
            if not in_list:
                output.append(Text())

        # INLINE (only process if not inside a table)
        elif token.type == "inline" and not in_table:
            line_text = Text()

            if pending_list_marker:
                line_text.append(pending_list_marker, style="bold")

            children = token.children or []
            style_stack = []

            j = 0
            while j < len(children):
                child = children[j]

                if child.type == "text":
                    style = ""
                    if "em" in style_stack:
                        style += " italic"
                    if "strong" in style_stack:
                        style += " bold"
                    if in_blockquote:
                        style += " italic"
                    line_text.append(child.content, style=style.strip() or None)

                elif child.type == "code_inline":
                    line_text.append(f" {child.content} ", style="red on black")

                elif child.type == "strong_open":
                    style_stack.append("strong")
                elif child.type == "strong_close":
                    if "strong" in style_stack:
                        style_stack.remove("strong")

                elif child.type == "em_open":
                    style_stack.append("em")
                elif child.type == "em_close":
                    if "em" in style_stack:
                        style_stack.remove("em")

                elif child.type == "link_open":
                    href = child.attrs.get("href", "")
                    label = ""
                    k = j + 1
                    while k < len(children) and children[k].type != "link_close":
                        if children[k].type == "text":
                            label += children[k].content
                        k += 1

                    line_text.append(label, style="bold bright_cyan")
                    if href and href != label:
                        line_text.append(" ")
                        line_text.append(href, style="underline cyan")

                    j = k

                j += 1

            if in_blockquote:
                output.append(blockquote(line_text, console.width))
            else:
                output.append(wrap_paragraph(line_text, console.width))

        i += 1

    return output


def show_help():
    """Display help information."""
    help_text = """meow — A terminal markdown viewer with syntax highlighting

USAGE:
    meow FILE.md [OPTIONS]

OPTIONS:
    --force     Render non-markdown files as markdown anyway
    -h, --help  Show this help message

EXAMPLES:
    meow README.md
    meow notes.txt --force
    meow --help

DESCRIPTION:
    meow renders markdown files with cute syntax highlighting and smart paging (like git log). Only pages when content is taller than your terminal.

    Supports headings, code blocks, lists, blockquotes, links, bold/italic text, inline code, and tables.
"""
    print(help_text)


def main():
    # Handle help first
    if "-h" in sys.argv or "--help" in sys.argv:
        show_help()
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: meow FILE.md [--force]")
        print("Try 'meow --help' for more information.")
        sys.exit(1)

    # Parse arguments
    force_render = "--force" in sys.argv
    file_args = [arg for arg in sys.argv[1:] if arg not in ("--force", "-h", "--help")]

    if not file_args:
        print("Usage: meow FILE.md [--force]")
        print("Try 'meow --help' for more information.")
        sys.exit(1)

    path = Path(file_args[0])

    # Check if file exists
    if not path.exists():
        print(f"Error: File '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Check if it's a markdown file (unless --force is used)
    if not force_render:
        markdown_extensions = {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
        if path.suffix.lower() not in markdown_extensions:
            print(
                f"Error: '{path}' doesn't appear to be a markdown file.",
                file=sys.stderr,
            )
            print(
                f"Expected extensions: {', '.join(sorted(markdown_extensions))}",
                file=sys.stderr,
            )
            print("Use --force to render anyway.", file=sys.stderr)
            sys.exit(1)

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(
            f"Error: '{path}' contains non-UTF-8 content and cannot be displayed.",
            file=sys.stderr,
        )
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading '{path}'.", file=sys.stderr)
        sys.exit(1)

    rendered_chunks = render_markdown(text)

    # Render to string with ANSI colors
    colored_output = render_to_string_with_colors(rendered_chunks)

    # Count lines to determine if we need paging
    total_lines = count_display_lines(colored_output)
    terminal_height = console.size.height

    # Use paging if content is taller than terminal
    if total_lines > terminal_height:
        # Use subprocess to pipe to less with color support
        try:
            # Use less with options: -R (raw control chars), -F (quit if one screen), -X (no init)
            less_process = subprocess.Popen(
                ["less", "-RFX"], stdin=subprocess.PIPE, text=True
            )
            less_process.communicate(input=colored_output)
        except FileNotFoundError:
            # Fallback if less is not available
            print(colored_output, end="")
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            less_process.terminate()
    else:
        # Print directly for short content
        print(colored_output, end="")


if __name__ == "__main__":
    main()
