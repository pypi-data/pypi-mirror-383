"""
Convert tool for MCP Browser Tools

Provides the convert_to_markdown tool for converting PDF or HTML content to markdown.
"""

import asyncio
import time
import tempfile
import os
from typing import Callable, Dict, Any, Optional, Annotated, Union
from pathlib import Path

from pydantic import BaseModel, Field
from loguru import logger
from markitdown import MarkItDown
import markdownify

from navmcp.utils.net import validate_url_security, normalize_url

class ConvertToMarkdownInput(BaseModel):
    """Input schema for convert_to_markdown tool."""
    content_type: str = Field(
        description="Type of content to convert: 'url' for web pages, 'html' for HTML content, 'pdf_url' for PDF files, 'docx_url' for DOCX files from URL, or 'docx' for local DOCX content",
        examples=["url", "html", "pdf_url", "docx_url", "docx"]
    )
    content: str = Field(
        description="The content to convert - URL for 'url'/'pdf_url'/'docx_url' types, HTML string for 'html', or local DOCX path for 'docx' type",
        examples=[
            "https://www.example.com", 
            "<html><body><h1>Hello World</h1></body></html>",
            "https://www.example.com/document.pdf",
            "https://www.example.com/document.docx",
            "tmp/test.docx"
        ],
        min_length=1,
        max_length=50000
    )

class ConvertToMarkdownOutput(BaseModel):
    """Output schema for convert_to_markdown tool."""
    markdown: str = Field(description="Converted markdown content")
    original_format: str = Field(description="Original format of the content")
    conversion_success: bool = Field(description="Whether conversion was successful")
    status: str = Field(description="Status: 'ok' or 'error'")
    error: Optional[str] = Field(None, description="Error message if status is 'error'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

def setup_convert_tools(mcp, get_browser_manager: Callable):
    """Setup conversion-related MCP tools."""
    # MarkItDown handles HTML, PDF, and DOCX

    # DEBUG: Print all registered tool names after setup
    import sys
    def _debug_print_tools():
        try:
            print("Registered tools in MCP (convert):", file=sys.stderr)
            print("Attributes of mcp:", dir(mcp), file=sys.stderr)
            if hasattr(mcp, "get_tools"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If already running, schedule and wait for result
                        future = asyncio.ensure_future(mcp.get_tools())
                        loop.run_until_complete(future)
                        tool_list = future.result()
                    else:
                        tool_list = loop.run_until_complete(mcp.get_tools())
                    print("Tool list:", tool_list, file=sys.stderr)
                except Exception as e:
                    print(f"Error running get_tools: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error printing tool names: {e}", file=sys.stderr)

    @mcp.tool()
    async def convert_file_to_markdown(
        input_path: Annotated[str, Field(
            description="Path to the HTML or PDF file to convert"
        )],
        output_path: Annotated[str, Field(
            description="Path to write the markdown output file"
        )],
        element_id: Annotated[Optional[str], Field(
            description="Optional id of the HTML element to extract and convert. If provided and found, only that element's content will be converted."
        )] = ""
    ) -> Dict[str, Any]:
        """
        Convert a local HTML or PDF file to markdown and write to output_path.

        Usage:
        - To convert the entire file, omit element_id.
        - To convert only a specific HTML element, provide element_id (e.g., "article-details").
        If element_id is provided and found in HTML, only that element's content will be converted.

        Example:
        convert_file_to_markdown(
            input_path="tmp/pubmed_40055694.html",
            output_path="tmp/pubmed_40055694.md",
            element_id="article-details"
        )
        """
        start_time = time.time()
        try:
            ext = Path(input_path).suffix.lower()
            md_converter = MarkItDown()
            markdown = ""
            original_format = ""
            if ext == ".html":
                if element_id and element_id != "":
                    from bs4 import BeautifulSoup
                    with open(input_path, "r", encoding="utf-8") as f:
                        html = f.read()
                    soup = BeautifulSoup(html, "html.parser")
                    target = soup.find(id=element_id)
                    if target:
                        html_fragment = str(target)
                        # Convert only the fragment
                        import io
                        stream = io.BytesIO(html_fragment.encode("utf-8"))
                        markdown = markdownify.markdownify(stream, heading_style="ATX")
                        original_format = "html"
                    else:
                        # Fallback to full file if id not found
                        error_msg = f"Element with id '{element_id}' not found. Converting full file instead."
                        result = md_converter.convert_local(input_path)
                        markdown = result.text_content
                        original_format = "html"
                        markdown = f"<!-- {error_msg} -->\n" + markdown
                else:
                    result = md_converter.convert_local(input_path)
                    markdown = result.text_content
                    original_format = "html"
            elif ext == ".pdf":
                result = md_converter.convert_local(input_path)
                markdown = result.text_content
                original_format = "pdf"
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file extension: {ext}",
                    "status": "error"
                }
            # Write markdown to output_path
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            duration = time.time() - start_time
            return {
                "success": True,
                "status": "ok",
                "original_format": original_format,
                "output_path": output_path,
                "duration_seconds": round(duration, 2)
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "status": "error",
                "duration_seconds": round(duration, 2)
            }

    @mcp.tool()
    async def convert_to_markdown(
        content_type: Annotated[str, Field(
            description="Type of content to convert: 'url' for web pages, 'html' for HTML content, 'pdf_url' for PDF files, 'docx_url' for DOCX files from URL, or 'docx' for local DOCX content",
            examples=["url", "html", "pdf_url", "docx_url", "docx"]
        )],
        content: Annotated[str, Field(
            description="The content to convert - URL for 'url'/'pdf_url'/'docx_url' types, HTML string for 'html', or local DOCX path for 'docx' type",
            examples=[
                "https://www.example.com", 
                "<html><body><h1>Hello World</h1></body></html>",
                "https://www.example.com/document.pdf",
                "https://www.example.com/document.docx",
                "tmp/test.docx"
            ],
            min_length=1,
            max_length=50000
        )]
    ) -> ConvertToMarkdownOutput:
        """
        Convert PDF, HTML, or DOCX content to markdown format using MarkItDown.
        
        This tool can convert content from various sources:
        - Web pages (URLs) - fetches HTML and converts to markdown
        - HTML content - directly converts HTML string to markdown  
        - PDF files (URLs) - downloads PDF and converts to markdown
        - DOCX files (URLs or local) - downloads or reads DOCX and converts to markdown
        
        The conversion uses Microsoft's MarkItDown library for all formats.
        
        Key features:
        - Supports HTML, PDF, and DOCX conversion
        - Handles web page and DOCX fetching automatically
        - Preserves document structure and formatting
        - Provides detailed error reporting
        
        Use cases:
        - Converting web pages or DOCX to markdown for documentation
        - Processing PDF/DOCX documents for text analysis
        - Converting HTML content for markdown-based workflows
        - Creating readable text versions of documents
        
        Args:
            content_type: The type of content ('url', 'html', 'pdf_url', 'docx_url', 'docx')
            content: The content to convert (URL, HTML string, or local DOCX path)
            
        Returns:
            ConvertToMarkdownOutput with markdown content and metadata
        """
        start_time = time.time()
        logger.info(f"Converting {content_type} content to markdown")
        try:
            valid_types = ['url', 'html', 'pdf_url', 'docx_url', 'docx']
            if content_type not in valid_types:
                return ConvertToMarkdownOutput(
                    markdown="",
                    original_format="unknown",
                    conversion_success=False,
                    status="error",
                    error=f"Invalid content_type. Must be one of: {valid_types}"
                )
            md_converter = MarkItDown()
            # HTML
            if content_type == 'html':
                result = await _convert_html_content(md_converter, content)
            # PDF/HTML URLs
            elif content_type in ['url', 'pdf_url']:
                is_valid, error_msg = validate_url_security(content, allow_private=False)
                if not is_valid:
                    logger.warning(f"URL validation failed for {content}: {error_msg}")
                    return ConvertToMarkdownOutput(
                        markdown="",
                        original_format="url",
                        conversion_success=False,
                        status="error",
                        error=f"URL validation failed: {error_msg}"
                    )
                normalized_url = normalize_url(content)
                result = await _convert_url_content(md_converter, normalized_url, content_type)
            # DOCX from URL
            elif content_type == 'docx_url':
                is_valid, error_msg = validate_url_security(content, allow_private=False)
                if not is_valid:
                    logger.warning(f"URL validation failed for {content}: {error_msg}")
                    return ConvertToMarkdownOutput(
                        markdown="",
                        original_format="docx",
                        conversion_success=False,
                        status="error",
                        error=f"URL validation failed: {error_msg}"
                    )
                import requests
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
                    try:
                        r = requests.get(content)
                        r.raise_for_status()
                        temp_docx.write(r.content)
                        temp_docx_path = temp_docx.name
                        # Use MarkItDown for DOCX
                        result_obj = md_converter.convert_local(temp_docx_path)
                        markdown = result_obj.text_content
                        result = ConvertToMarkdownOutput(
                            markdown=markdown,
                            original_format="docx",
                            conversion_success=True,
                            status="ok",
                            metadata={"source": "docx_url", "url": content}
                        )
                    except Exception as e:
                        result = ConvertToMarkdownOutput(
                            markdown="",
                            original_format="docx",
                            conversion_success=False,
                            status="error",
                            error=f"DOCX conversion failed: {str(e)}"
                        )
                    finally:
                        try:
                            os.unlink(temp_docx_path)
                        except Exception:
                            pass
            # DOCX local file
            elif content_type == 'docx':
                if not os.path.exists(content):
                    return ConvertToMarkdownOutput(
                        markdown="",
                        original_format="docx",
                        conversion_success=False,
                        status="error",
                        error=f"DOCX file not found: {content}"
                    )
                try:
                    result_obj = md_converter.convert_local(content)
                    markdown = result_obj.text_content
                    result = ConvertToMarkdownOutput(
                        markdown=markdown,
                        original_format="docx",
                        conversion_success=True,
                        status="ok",
                        metadata={"source": "docx_local", "file_path": content}
                    )
                except Exception as e:
                    result = ConvertToMarkdownOutput(
                        markdown="",
                        original_format="docx",
                        conversion_success=False,
                        status="error",
                        error=f"DOCX conversion failed: {str(e)}"
                    )
            # Add timing metadata
            duration = time.time() - start_time
            result.metadata["duration_seconds"] = round(duration, 2)
            result.metadata["timestamp"] = time.time()
            result.metadata["content_type"] = content_type
            logger.info(f"Conversion completed in {duration:.2f}s - Status: {result.status}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Unexpected error during conversion: {error_msg}")
            return ConvertToMarkdownOutput(
                markdown="",
                original_format=content_type,
                conversion_success=False,
                status="error",
                error=f"Unexpected error: {error_msg}",
                metadata={"duration_seconds": round(duration, 2)}
            )

    # Call debug print after tool registration
    _debug_print_tools()

async def _convert_html_content(md_converter: MarkItDown, html_content: str) -> ConvertToMarkdownOutput:
    """Convert HTML string content to markdown."""
    try:
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_file_path = temp_file.name
        
        try:
            # Convert using MarkItDown
            result = md_converter.convert_local(temp_file_path)
            
            return ConvertToMarkdownOutput(
                markdown=result.text_content,
                original_format="html",
                conversion_success=True,
                status="ok",
                metadata={"source": "html_string", "file_size": len(html_content)}
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
                
    except Exception as e:
        logger.error(f"Error converting HTML content: {str(e)}")
        return ConvertToMarkdownOutput(
            markdown="",
            original_format="html",
            conversion_success=False,
            status="error",
            error=f"HTML conversion failed: {str(e)}"
        )

async def _convert_url_content(md_converter: MarkItDown, url: str, content_type: str) -> ConvertToMarkdownOutput:
    """Convert URL content (web page or PDF) to markdown."""
    try:
        # Use MarkItDown's URL conversion capability
        result = md_converter.convert_url(url)
        
        # Determine original format based on content type
        original_format = "pdf" if content_type == "pdf_url" else "html"
        
        return ConvertToMarkdownOutput(
            markdown=result.text_content,
            original_format=original_format,
            conversion_success=True,
            status="ok",
            metadata={
                "source": "url",
                "url": url,
                "title": getattr(result, 'title', ''),
                "content_length": len(result.text_content)
            }
        )
        
    except Exception as e:
        logger.error(f"Error converting URL content {url}: {str(e)}")
        original_format = "pdf" if content_type == "pdf_url" else "html"
        
        return ConvertToMarkdownOutput(
            markdown="",
            original_format=original_format,
            conversion_success=False,
            status="error",
            error=f"URL conversion failed: {str(e)}"
        )
