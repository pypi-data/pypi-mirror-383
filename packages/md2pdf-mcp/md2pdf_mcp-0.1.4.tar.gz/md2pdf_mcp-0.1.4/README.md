# md2pdf-mcp

MCP Server for Markdown to PDF conversion.

## Description

This server provides a tool to convert Markdown text to PDF files using the `convert_markdown` library. It's designed to work as an MCP (Model Context Protocol) server that can be integrated with various AI assistants and applications.

## Features

- Convert Markdown text to well-formatted PDF files
- Random filename generation using UUID to avoid conflicts
- Configurable output directory via environment variables
- Returns resource links with metadata for easy integration
- Built on FastMCP for reliable MCP server functionality

## Installation

You can install and run this tool using `uvx`:

```bash
uvx --from md2pdf-mcp md2pdf
```

## Usage

### As MCP Server

Configure the server in your MCP client configuration:

```json
{
    "mcpServers": {
        "md2pdf": {
            "command": "uvx",
            "args": ["--from", "md2pdf-mcp", "md2pdf"],
            "env": {
                "PDF_OUTPUT_DIR": "/path/to/output/folder"
            }
        }
    }
}
```

### Available Tools

The server provides one tool:

#### `convert_md_to_pdf`

Converts Markdown text to a PDF file.

**Parameters:**
- `markdown_text` (string): The Markdown content to convert

**Returns:**
A JSON string containing:
- `type`: "resource_link"
- `uri`: File URI of the generated PDF
- `name`: Generated filename (UUID-based)
- `mimeType`: "application/pdf"
- `annotations`: Metadata including audience, priority, and last modified timestamp

### Environment Variables

- `PDF_OUTPUT_DIR`: Directory where PDF files will be saved (defaults to user's home directory)

### Example Usage

Once the server is running, you can call the tool through your MCP client:

```json
{
    "mcpServers": {
        "md2pdf": {
            "command": "uvx",
            "args": ["--from", "md2pdf-mcp", "md2pdf"],
            "env": {
                "PDF_OUTPUT_DIR": "/path/to/output/folder"
            }
        }
    }
}
```

## License

MIT License