#!/usr/bin/env python3
"""
Markdown Formatter

Provides specialized formatting for Markdown files, focusing on document structure
rather than programming constructs like classes and methods.
"""

from typing import Dict, List, Any, Optional
from .base_formatter import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """Formatter specialized for Markdown documents"""

    def __init__(self):
        super().__init__()
        self.language = "markdown"

    def format_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Format summary for Markdown files"""
        file_path = analysis_result.get("file_path", "")
        elements = analysis_result.get("elements", [])
        
        # Count different types of Markdown elements
        headers = [e for e in elements if e.get("type") == "heading"]
        links = [e for e in elements if e.get("type") in ["link", "autolink", "reference_link"]]
        images = [e for e in elements if e.get("type") in ["image", "reference_image"]]
        code_blocks = [e for e in elements if e.get("type") == "code_block"]
        lists = [e for e in elements if e.get("type") in ["list", "task_list"]]
        
        summary = {
            "headers": [{"name": h.get("text", "").strip(), "level": h.get("level", 1)} for h in headers],
            "links": [{"text": l.get("text", ""), "url": l.get("url", "")} for l in links],
            "images": [{"alt": i.get("alt", ""), "url": i.get("url", "")} for i in images],
            "code_blocks": [{"language": cb.get("language", ""), "lines": cb.get("line_count", 0)} for cb in code_blocks],
            "lists": [{"type": l.get("list_type", ""), "items": l.get("item_count", 0)} for l in lists]
        }
        
        result = {
            "file_path": file_path,
            "language": "markdown",
            "summary": summary
        }
        
        return self._format_json_output("Summary Results", result)

    def format_structure(self, analysis_result: Dict[str, Any]) -> str:
        """Format structure analysis for Markdown files"""
        file_path = analysis_result.get("file_path", "")
        elements = analysis_result.get("elements", [])
        line_count = analysis_result.get("line_count", 0)
        
        # Organize elements by type
        headers = [e for e in elements if e.get("type") == "heading"]
        links = [e for e in elements if e.get("type") in ["link", "autolink", "reference_link"]]
        images = [e for e in elements if e.get("type") in ["image", "reference_image"]]
        code_blocks = [e for e in elements if e.get("type") == "code_block"]
        lists = [e for e in elements if e.get("type") in ["list", "task_list"]]
        tables = [e for e in elements if e.get("type") == "table"]
        
        structure = {
            "file_path": file_path,
            "language": "markdown",
            "headers": [
                {
                    "text": h.get("text", "").strip(),
                    "level": h.get("level", 1),
                    "line_range": h.get("line_range", {})
                } for h in headers
            ],
            "links": [
                {
                    "text": l.get("text", ""),
                    "url": l.get("url", ""),
                    "line_range": l.get("line_range", {})
                } for l in links
            ],
            "images": [
                {
                    "alt": i.get("alt", ""),
                    "url": i.get("url", ""),
                    "line_range": i.get("line_range", {})
                } for i in images
            ],
            "code_blocks": [
                {
                    "language": cb.get("language", ""),
                    "line_count": cb.get("line_count", 0),
                    "line_range": cb.get("line_range", {})
                } for cb in code_blocks
            ],
            "lists": [
                {
                    "type": l.get("list_type", ""),
                    "item_count": l.get("item_count", 0),
                    "line_range": l.get("line_range", {})
                } for l in lists
            ],
            "tables": [
                {
                    "columns": t.get("column_count", 0),
                    "rows": t.get("row_count", 0),
                    "line_range": t.get("line_range", {})
                } for t in tables
            ],
            "statistics": {
                "header_count": len(headers),
                "link_count": len(links),
                "image_count": len(images),
                "code_block_count": len(code_blocks),
                "list_count": len(lists),
                "table_count": len(tables),
                "total_lines": line_count
            },
            "analysis_metadata": analysis_result.get("analysis_metadata", {})
        }
        
        return self._format_json_output("Structure Analysis Results", structure)

    def format_advanced(self, analysis_result: Dict[str, Any], output_format: str = "json") -> str:
        """Format advanced analysis for Markdown files"""
        file_path = analysis_result.get("file_path", "")
        elements = analysis_result.get("elements", [])
        line_count = analysis_result.get("line_count", 0)
        element_count = len(elements)
        
        # Calculate Markdown-specific metrics
        headers = [e for e in elements if e.get("type") == "heading"]
        links = [e for e in elements if e.get("type") in ["link", "autolink", "reference_link"]]
        images = [e for e in elements if e.get("type") in ["image", "reference_image"]]
        code_blocks = [e for e in elements if e.get("type") == "code_block"]
        lists = [e for e in elements if e.get("type") in ["list", "task_list"]]
        tables = [e for e in elements if e.get("type") == "table"]
        
        # Calculate document structure metrics
        header_levels = [h.get("level", 1) for h in headers]
        max_header_level = max(header_levels) if header_levels else 0
        avg_header_level = sum(header_levels) / len(header_levels) if header_levels else 0
        
        # Calculate content metrics
        total_code_lines = sum(cb.get("line_count", 0) for cb in code_blocks)
        total_list_items = sum(l.get("item_count", 0) for l in lists)
        
        # External vs internal links
        external_links = [l for l in links if l.get("url") and l.get("url", "").startswith(("http://", "https://"))]
        internal_links = [l for l in links if not (l.get("url") and l.get("url", "").startswith(("http://", "https://")))]
        
        advanced_data = {
            "file_path": file_path,
            "language": "markdown",
            "line_count": line_count,
            "element_count": element_count,
            "success": True,
            "elements": elements,
            "document_metrics": {
                "header_count": len(headers),
                "max_header_level": max_header_level,
                "avg_header_level": round(avg_header_level, 2),
                "link_count": len(links),
                "external_link_count": len(external_links),
                "internal_link_count": len(internal_links),
                "image_count": len(images),
                "code_block_count": len(code_blocks),
                "total_code_lines": total_code_lines,
                "list_count": len(lists),
                "total_list_items": total_list_items,
                "table_count": len(tables)
            },
            "content_analysis": {
                "has_toc": any("table of contents" in h.get("text", "").lower() for h in headers),
                "has_code_examples": len(code_blocks) > 0,
                "has_images": len(images) > 0,
                "has_external_links": len(external_links) > 0,
                "document_complexity": self._calculate_document_complexity(headers, links, code_blocks, tables)
            }
        }
        
        if output_format == "text":
            return self._format_advanced_text(advanced_data)
        else:
            return self._format_json_output("Advanced Analysis Results", advanced_data)

    def format_table(self, analysis_result: Dict[str, Any], table_type: str = "full") -> str:
        """Format table output for Markdown files"""
        file_path = analysis_result.get("file_path", "")
        elements = analysis_result.get("elements", [])
        
        # Get document title from first header
        headers = [e for e in elements if e.get("type") == "heading"]
        title = headers[0].get("text", "").strip() if headers else file_path.split("/")[-1]
        
        output = [f"# {title}\n"]
        
        # Document Overview
        output.append("## Document Overview\n")
        output.append(f"| Property | Value |")
        output.append(f"|----------|-------|")
        output.append(f"| File | {file_path} |")
        output.append(f"| Language | markdown |")
        output.append(f"| Total Lines | {analysis_result.get('line_count', 0)} |")
        output.append(f"| Total Elements | {len(elements)} |")
        output.append("")
        
        # Headers Section
        if headers:
            output.append("## Document Structure\n")
            output.append("| Level | Header | Line |")
            output.append("|-------|--------|------|")
            for header in headers:
                level = "#" * header.get("level", 1)
                text = header.get("text", "").strip()
                line = header.get("line_range", {}).get("start", "")
                output.append(f"| {level} | {text} | {line} |")
            output.append("")
        
        # Links Section
        links = [e for e in elements if e.get("type") in ["link", "autolink", "reference_link"]]
        if links:
            output.append("## Links\n")
            output.append("| Text | URL | Type | Line |")
            output.append("|------|-----|------|------|")
            for link in links:
                text = link.get("text", "")
                url = link.get("url", "") or ""
                link_type = "External" if url and url.startswith(("http://", "https://")) else "Internal"
                line = link.get("line_range", {}).get("start", "")
                output.append(f"| {text} | {url} | {link_type} | {line} |")
            output.append("")
        
        # Images Section
        images = [e for e in elements if e.get("type") in ["image", "reference_image"]]
        if images:
            output.append("## Images\n")
            output.append("| Alt Text | URL | Line |")
            output.append("|----------|-----|------|")
            for image in images:
                alt = image.get("alt", "")
                url = image.get("url", "")
                line = image.get("line_range", {}).get("start", "")
                output.append(f"| {alt} | {url} | {line} |")
            output.append("")
        
        # Code Blocks Section
        code_blocks = [e for e in elements if e.get("type") == "code_block"]
        if code_blocks:
            output.append("## Code Blocks\n")
            output.append("| Language | Lines | Line Range |")
            output.append("|----------|-------|------------|")
            for cb in code_blocks:
                language = cb.get("language", "text")
                lines = cb.get("line_count", 0)
                line_range = cb.get("line_range", {})
                start = line_range.get("start", "")
                end = line_range.get("end", "")
                range_str = f"{start}-{end}" if start and end else str(start)
                output.append(f"| {language} | {lines} | {range_str} |")
            output.append("")
        
        # Lists Section
        lists = [e for e in elements if e.get("type") in ["list", "task_list"]]
        if lists:
            output.append("## Lists\n")
            output.append("| Type | Items | Line |")
            output.append("|------|-------|------|")
            for lst in lists:
                list_type = lst.get("list_type", "unordered")
                items = lst.get("item_count", 0)
                line = lst.get("line_range", {}).get("start", "")
                output.append(f"| {list_type} | {items} | {line} |")
            output.append("")
        
        # Tables Section
        tables = [e for e in elements if e.get("type") == "table"]
        if tables:
            output.append("## Tables\n")
            output.append("| Columns | Rows | Line |")
            output.append("|---------|------|------|")
            for table in tables:
                columns = table.get("column_count", 0)
                rows = table.get("row_count", 0)
                line = table.get("line_range", {}).get("start", "")
                output.append(f"| {columns} | {rows} | {line} |")
            output.append("")
        
        # Blockquotes Section
        blockquotes = [e for e in elements if e.get("type") == "blockquote"]
        if blockquotes:
            output.append("## Blockquotes\n")
            output.append("| Content | Line |")
            output.append("|---------|------|")
            for bq in blockquotes:
                content = bq.get("text", "")[:50] + "..." if len(bq.get("text", "")) > 50 else bq.get("text", "")
                line = bq.get("line_range", {}).get("start", "")
                output.append(f"| {content} | {line} |")
            output.append("")
        
        # Horizontal Rules Section
        horizontal_rules = [e for e in elements if e.get("type") == "horizontal_rule"]
        if horizontal_rules:
            output.append("## Horizontal Rules\n")
            output.append("| Type | Line |")
            output.append("|------|------|")
            for hr in horizontal_rules:
                line = hr.get("line_range", {}).get("start", "")
                output.append(f"| Horizontal Rule | {line} |")
            output.append("")
        
        # HTML Elements Section
        html_elements = [e for e in elements if e.get("type") in ["html_block", "html_inline"]]
        if html_elements:
            output.append("## HTML Elements\n")
            output.append("| Type | Content | Line |")
            output.append("|------|---------|------|")
            for html in html_elements:
                element_type = html.get("type", "")
                content = html.get("name", "")[:30] + "..." if len(html.get("name", "")) > 30 else html.get("name", "")
                line = html.get("line_range", {}).get("start", "")
                output.append(f"| {element_type} | {content} | {line} |")
            output.append("")
        
        # Text Formatting Section
        formatting_elements = [e for e in elements if e.get("type") in ["strong_emphasis", "emphasis", "inline_code", "strikethrough"]]
        if formatting_elements:
            output.append("## Text Formatting\n")
            output.append("| Type | Content | Line |")
            output.append("|------|---------|------|")
            for fmt in formatting_elements:
                format_type = fmt.get("type", "")
                content = fmt.get("text", "")[:30] + "..." if len(fmt.get("text", "")) > 30 else fmt.get("text", "")
                line = fmt.get("line_range", {}).get("start", "")
                output.append(f"| {format_type} | {content} | {line} |")
            output.append("")
        
        # Footnotes Section
        footnotes = [e for e in elements if e.get("type") in ["footnote_reference", "footnote_definition"]]
        if footnotes:
            output.append("## Footnotes\n")
            output.append("| Type | Content | Line |")
            output.append("|------|---------|------|")
            for fn in footnotes:
                footnote_type = fn.get("type", "")
                content = fn.get("text", "")[:30] + "..." if len(fn.get("text", "")) > 30 else fn.get("text", "")
                line = fn.get("line_range", {}).get("start", "")
                output.append(f"| {footnote_type} | {content} | {line} |")
            output.append("")
        
        # Reference Definitions Section
        references = [e for e in elements if e.get("type") == "reference_definition"]
        if references:
            output.append("## Reference Definitions\n")
            output.append("| Content | Line |")
            output.append("|---------|------|")
            for ref in references:
                content = ref.get("name", "")[:50] + "..." if len(ref.get("name", "")) > 50 else ref.get("name", "")
                line = ref.get("line_range", {}).get("start", "")
                output.append(f"| {content} | {line} |")
            output.append("")
        
        return "\n".join(output)

    def _format_advanced_text(self, data: Dict[str, Any]) -> str:
        """Format advanced analysis in text format"""
        output = ["--- Advanced Analysis Results ---"]
        
        # Basic info
        output.append(f'"File: {data["file_path"]}"')
        output.append(f'"Language: {data["language"]}"')
        output.append(f'"Lines: {data["line_count"]}"')
        output.append(f'"Elements: {data["element_count"]}"')
        
        # Document metrics
        metrics = data["document_metrics"]
        output.append(f'"Headers: {metrics["header_count"]}"')
        output.append(f'"Max Header Level: {metrics["max_header_level"]}"')
        output.append(f'"Links: {metrics["link_count"]}"')
        output.append(f'"External Links: {metrics["external_link_count"]}"')
        output.append(f'"Images: {metrics["image_count"]}"')
        output.append(f'"Code Blocks: {metrics["code_block_count"]}"')
        output.append(f'"Code Lines: {metrics["total_code_lines"]}"')
        output.append(f'"Lists: {metrics["list_count"]}"')
        output.append(f'"Tables: {metrics["table_count"]}"')
        
        # Content analysis
        content = data["content_analysis"]
        output.append(f'"Has TOC: {content["has_toc"]}"')
        output.append(f'"Has Code: {content["has_code_examples"]}"')
        output.append(f'"Has Images: {content["has_images"]}"')
        output.append(f'"Has External Links: {content["has_external_links"]}"')
        output.append(f'"Document Complexity: {content["document_complexity"]}"')
        
        return "\n".join(output)

    def _calculate_document_complexity(self, headers: List[Dict], links: List[Dict], 
                                     code_blocks: List[Dict], tables: List[Dict]) -> str:
        """Calculate document complexity based on structure and content"""
        score = 0
        
        # Header complexity
        if headers:
            header_levels = [h.get("level", 1) for h in headers]
            max_level = max(header_levels)
            score += len(headers) * 2  # Base score for headers
            score += max_level * 3     # Deeper nesting increases complexity
        
        # Content complexity
        score += len(links) * 1        # Links add moderate complexity
        score += len(code_blocks) * 5  # Code blocks add significant complexity
        score += len(tables) * 3       # Tables add moderate complexity
        
        # Classify complexity
        if score < 20:
            return "Simple"
        elif score < 50:
            return "Moderate"
        elif score < 100:
            return "Complex"
        else:
            return "Very Complex"

    def _format_json_output(self, title: str, data: Dict[str, Any]) -> str:
        """Format JSON output with title"""
        import json
        output = [f"--- {title} ---"]
        output.append(json.dumps(data, indent=2, ensure_ascii=False))
        return "\n".join(output)