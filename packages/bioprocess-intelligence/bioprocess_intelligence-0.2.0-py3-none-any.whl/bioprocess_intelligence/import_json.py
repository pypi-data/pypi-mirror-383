"""JSON import functionality for Bioprocess Intelligence client."""
import json
from typing import Dict, Any, Optional


def import_process_from_json(json_data: str, collection_id: str, timezone: str,
                           client, async_mode: Optional[bool] = None) -> Dict[str, Any]:
    """Import process data from JSON string.

    Args:
        json_data: JSON string containing process data
        collection_id: ID of the collection to import into (maps to topic_id internally)
        timezone: Timezone for date processing (e.g., "UTC", "Europe/Berlin")
        client: BioprocessIntelligenceClient instance
        async_mode: Use background processing (default: None, let backend decide)

    Returns:
        Import result with ok status, processId (sync) or backgroundTaskId (async)
    """
    # Basic JSON format validation only
    try:
        json.loads(json_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")

    # Call client method (maps collection_id to topic_id internally)
    return client.import_process_from_json(
        json_data=json_data,
        collection_id=collection_id,
        timezone=timezone,
        async_mode=async_mode
    )


def import_process_from_json_file(file_path: str, collection_id: str, timezone: str,
                                client, async_mode: Optional[bool] = None) -> Dict[str, Any]:
    """Import process data from a JSON file.

    Args:
        file_path: Path to JSON file
        collection_id: ID of the collection to import into
        timezone: Timezone for date processing
        client: BioprocessIntelligenceClient instance
        async_mode: Use background processing (default: None, let backend decide)

    Returns:
        Import result with ok status, processId (sync) or backgroundTaskId (async)
    """
    import os

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = f.read()

    return import_process_from_json(json_data, collection_id, timezone, client, async_mode)