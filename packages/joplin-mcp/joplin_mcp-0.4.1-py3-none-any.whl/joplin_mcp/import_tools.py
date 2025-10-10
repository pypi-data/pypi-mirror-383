"""MCP import tools for Joplin MCP server."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

from .config import JoplinMCPConfig

# Local imports
from .import_engine import JoplinImportEngine, get_joplin_client
from .importers import (
    CSVImporter,
    GenericImporter,
    HTMLImporter,
    JEXImporter,
    MarkdownImporter,
    RAWImporter,
)
from .types.import_types import ImportOptions
from .importers.utils import looks_like_raw_export

logger = logging.getLogger(__name__)


def format_import_result(result, operation_name: str = "IMPORT_BATCH") -> str:
    """Format import result for MCP response."""
    status = (
        "SUCCESS"
        if result.is_complete_success
        else "PARTIAL_SUCCESS" if result.is_partial_success else "FAILED"
    )

    response = f"""OPERATION: {operation_name}
STATUS: {status}
TOTAL_PROCESSED: {result.total_processed}
SUCCESSFUL_IMPORTS: {result.successful_imports}
FAILED_IMPORTS: {result.failed_imports}
SKIPPED_ITEMS: {result.skipped_items}
PROCESSING_TIME: {result.processing_time:.2f}s"""

    if result.created_notebooks:
        response += f"\nCREATED_NOTEBOOKS: {', '.join(result.created_notebooks)}"

    if result.created_tags:
        response += f"\nCREATED_TAGS: {', '.join(result.created_tags)}"

    if result.errors:
        response += f"\nERRORS: {len(result.errors)} error(s)"
        for error in result.errors[:5]:  # Show first 5 errors
            response += f"\n  - {error}"
        if len(result.errors) > 5:
            response += f"\n  ... and {len(result.errors) - 5} more errors"

    if result.warnings:
        response += f"\nWARNINGS: {len(result.warnings)} warning(s)"
        for warning in result.warnings[:3]:  # Show first 3 warnings
            response += f"\n  - {warning}"
        if len(result.warnings) > 3:
            response += f"\n  ... and {len(result.warnings) - 3} more warnings"

    # Add success message
    if result.is_complete_success:
        response += f"\nMESSAGE: Import completed successfully - all {result.successful_imports} items imported"
    elif result.is_partial_success:
        response += f"\nMESSAGE: Import partially successful - {result.successful_imports}/{result.total_processed} items imported"
    else:
        response += "\nMESSAGE: Import failed - no items were successfully imported"

    # Compact per-run summary (kept short for LLM context)
    try:
        if (
            getattr(result, "notes_rewritten", 0)
            or getattr(result, "resources_uploaded", 0)
            or getattr(result, "resources_reused", 0)
            or getattr(result, "unresolved_links", 0)
        ):
            response += (
                f"\nSUMMARY: modified_notes={getattr(result, 'notes_rewritten', 0)}, "
                f"uploaded_resources={getattr(result, 'resources_uploaded', 0)}, "
                f"reused_resources={getattr(result, 'resources_reused', 0)}, "
                f"unresolved_links={getattr(result, 'unresolved_links', 0)}"
            )
    except Exception:
        pass

    return response


def get_importer_for_format(file_format: str, options: ImportOptions):
    """Get the appropriate importer for the specified format."""
    format_map = {
        "md": MarkdownImporter,
        "markdown": MarkdownImporter,
        "jex": JEXImporter,
        "html": HTMLImporter,
        "htm": HTMLImporter,
        "csv": CSVImporter,
        "raw": RAWImporter,
        "generic": GenericImporter,
    }

    importer_class = format_map.get(file_format.lower())
    if not importer_class:
        # Fall back to generic importer for unknown formats
        return GenericImporter(options)

    return importer_class(options)


def detect_source_format(source_path: str) -> str:
    """Detect format from file or directory path."""
    path = Path(source_path)

    if path.is_file():
        return detect_file_format(source_path)
    elif path.is_dir():
        return detect_directory_format(source_path)
    else:
        raise ValueError(f"Source path does not exist: {source_path}")


def detect_file_format(file_path: str) -> str:
    """Detect file format from file extension."""
    path = Path(file_path)
    extension = path.suffix.lstrip(".").lower()

    # Map extensions to formats
    extension_map = {
        "md": "md",
        "markdown": "markdown",
        "mdown": "md",
        "mkd": "md",
        "jex": "jex",
        "html": "html",
        "htm": "html",
        "csv": "csv",
        
    }

    detected_format = extension_map.get(extension)
    if not detected_format:
        # Fall back to generic format for unknown file types
        return "generic"

    return detected_format


def detect_directory_format(directory_path: str) -> str:
    """Detect format from directory contents.

    Rules:
    - Classify as RAW only when the directory itself looks like a Joplin export
      (resources folder at the root and markdown present at or under the root),
      to avoid misclassifying mixed trees that contain a nested RAW subfolder.
    - If multiple supported types (md/html/csv) are present, return "generic" so the
      GenericImporter can delegate per-file and handle mixed content.
    - Otherwise, return the single supported format present.
    """
    path = Path(directory_path)

    if not path.exists() or not path.is_dir():
        raise ValueError(f"Directory not found: {directory_path}")

    # RAW detection using shared heuristic (root-level sensitive)
    if looks_like_raw_export(path):
        return "raw"

    # Scan extensions in tree
    extension_counts = {}
    for file_path in path.rglob("*"):
        if file_path.is_file():
            extension = file_path.suffix.lstrip(".").lower()
            extension_counts[extension] = extension_counts.get(extension, 0) + 1

    if not extension_counts:
        raise ValueError(f"No files found in directory: {directory_path}")

    # Supported mapping
    extension_map = {
        "md": "md",
        "markdown": "md",
        "mdown": "md",
        "mkd": "md",
        "html": "html",
        "htm": "html",
        "csv": "csv",
    }

    # Collect supported types present
    present_supported = {extension_map[ext] for ext in extension_counts.keys() if ext in extension_map}

    if not present_supported:
        # Fall back to generic when no recognized types
        return "generic"

    if len(present_supported) > 1:
        # Mixed content – use GenericImporter
        return "generic"

    # Single supported type present
    return next(iter(present_supported))


async def import_source(
    source_path: str,
    target_notebook: Optional[str] = None,
    import_options: Optional[Dict[str, Any]] = None,
) -> str:
    """Import from file or directory source.

    Args:
        source_path: Path to file or directory to import
        target_notebook: Target notebook name
        import_options: Import configuration options

    Returns:
        Formatted import result
    """
    from pathlib import Path

    # Create import options
    options = ImportOptions(
        handle_duplicates=(
            import_options.get("handle_duplicates", "rename")
            if import_options
            else "rename"
        ),
        create_missing_notebooks=(
            import_options.get("create_missing_notebooks", True)
            if import_options
            else True
        ),
        create_missing_tags=(
            import_options.get("create_missing_tags", True) if import_options else True
        ),
    )

    # Detect format
    detected_format = detect_source_format(source_path)

    # Get appropriate importer
    importer = get_importer_for_format(detected_format, options)

    # Validate source
    await importer.validate(source_path)

    # Parse based on source type
    path = Path(source_path)
    if path.is_file():
        notes = await importer.parse(source_path)
    elif path.is_dir():
        if hasattr(importer, "parse_directory"):
            notes = await importer.parse_directory(source_path)
        else:
            # Fallback: use base class directory parsing
            notes = await importer.parse_directory(source_path)
    else:
        raise ValueError(f"Invalid source path: {source_path}")

    if not notes:
        return f"No notes imported from {source_path}"

    # Set target notebook if specified
    if target_notebook:
        for note in notes:
            if not note.notebook:  # Don't override existing notebook assignments
                note.notebook = target_notebook

    # Get Joplin client and import
    config = JoplinMCPConfig()
    client = get_joplin_client(config)
    engine = JoplinImportEngine(client, config)

    result = await engine.import_batch(notes, options)

    return format_import_result(result)
