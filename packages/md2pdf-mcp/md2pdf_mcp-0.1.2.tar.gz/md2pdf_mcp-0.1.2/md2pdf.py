#!/usr/bin/env python3
"""
MCP Server for Markdown to PDF conversion.

This server provides a tool to convert Markdown text to PDF files.
"""

import logging
import os
import uuid
import convert_markdown
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("md2pdf")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("md2pdf-mcp")

@mcp.tool()
async def convert_md_to_pdf(markdown_text: str) -> str:
    """
    Convert Markdown text to PDF.

    Args:
        markdown_text (str): The Markdown text to convert.

    Returns:
        str: The JSON string with PDF metadata.
    """
    try:
        pdf_dir = os.getenv('PDF_OUTPUT_DIR', os.path.expanduser('~'))
        pdf_filename = f"{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        os.makedirs(pdf_dir, exist_ok=True)

        # Use WeasyPrint to convert HTML to PDF
        # weasyprint.HTML(string=full_html).write_pdf(pdf_path)
        convert_markdown.to(
            markdown=markdown_text,
            format="pdf",
            output_file=pdf_path,
        )
        logger.info("PDF generated successfully: %s", pdf_path)
        current_time = datetime.now().isoformat() + "Z"
        return f"""
{{
    "type": "resource_link",
    "uri": "file://{pdf_path}",
    "name": "{pdf_filename}",
    "mimeType": "application/pdf",
    "annotations": {{
        "audience": ["user", "assistant"],
        "priority": 0.7,
        "lastModified": "{current_time}"
    }}
}}
"""

    except Exception as e:
        logger.error("Error converting Markdown to PDF: %s", e)
        raise

def main():
    """Main entry point for the application."""
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()