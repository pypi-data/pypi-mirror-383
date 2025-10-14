# md2pdf

MCP Server for Markdown to PDF conversion.

## Description

This server provides a tool to convert Markdown text to PDF files using WeasyPrint. It's designed to work as an MCP (Model Context Protocol) server that can be integrated with various AI assistants and applications.

## Features

- Convert Markdown text to well-formatted PDF files
- Professional styling with clean typography
- Support for code highlighting, tables, and other Markdown extensions
- Configurable output directory via environment variables
- Random filename generation to avoid conflicts

## Installation

You can install and run this tool using `uvx`:

```bash
uvx md2pdf
```

Or install it permanently:

```bash
pip install md2pdf
```

## Usage

### As MCP Server

Run the server:

```json
{
    "mcpServers": {
        "serper": {
            "command": "uvx",
            "args": ["md2pdf"],
            "env": {
                "PDF_OUTPUT_DIR": "<Output folder>"
            }
        }
    }
}
```

### Environment Variables

- `PDF_OUTPUT_DIR`: Directory where PDF files will be saved (defaults to home directory)

## Requirements

- Python 3.8+
- WeasyPrint dependencies (may require system packages for PDF generation)

## License

MIT License