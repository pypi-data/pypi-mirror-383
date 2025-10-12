"""Builder MCP - Model Context Protocol server for Airbyte connector building.

This module provides MCP tools for autonomous AI ownership of connector building processes,
including manifest validation, stream testing, and configuration management.

The focus is on end-to-end AI ownership rather than AI assist, enabling AI agents to
fully control the connector development workflow including testing and PR creation.
"""

import csv
import logging
from pathlib import Path
from typing import Annotated

import requests
from fastmcp import FastMCP
from pydantic import Field

from connector_builder_mcp._guidance import (
    CONNECTOR_BUILDER_CHECKLIST,
    TOPIC_MAPPING,
)
from connector_builder_mcp.manifest_scaffold import (
    create_connector_manifest_scaffold,
)
from connector_builder_mcp.secrets import register_secrets_tools
from connector_builder_mcp.validation_testing import (
    execute_dynamic_manifest_resolution_test,
    execute_stream_test_read,
    run_connector_readiness_test_report,
    validate_manifest,
)


logger = logging.getLogger(__name__)

_REGISTRY_URL = "https://connectors.airbyte.com/files/registries/v0/oss_registry.json"
_MANIFEST_ONLY_LANGUAGE = "manifest-only"
_MANIFEST_SCHEMA_URL = "https://raw.githubusercontent.com/airbytehq/airbyte-python-cdk/refs/heads/main/airbyte_cdk/sources/declarative/declarative_component_schema.yaml"
_HTTP_OK = 200


def get_connector_builder_checklist() -> str:
    """Get the comprehensive development checklist for building declarative source connectors.

    This checklist provides a step-by-step guide for building connectors using the Connector Builder MCP Server,
    with emphasis on proper validation, pagination testing, and avoiding common pitfalls.

    Returns:
        Complete development checklist in markdown format
    """
    logger.info("Getting connector builder development checklist")
    return CONNECTOR_BUILDER_CHECKLIST


def get_connector_builder_docs(
    topic: Annotated[
        str | None,
        Field(
            description="Specific YAML reference topic to get detailed documentation for. If not provided, returns high-level overview and topic list."
        ),
    ] = None,
) -> str:
    """Get connector builder documentation and guidance.

    Args:
        topic: Optional specific topic from YAML reference documentation

    Returns:
        High-level overview with topic list, or detailed topic-specific documentation
    """
    logger.info(f"Getting connector builder docs for topic: {topic}")

    if not topic:
        return """# Connector Builder Documentation

**Important**: Before starting development, call the `get_connector_builder_checklist()` tool.
Save its contents to a new text file if you are able. The checklist provides step-by-step guidance
for building connectors and helps avoid common pitfalls like pagination issues and incomplete validation.

For detailed guidance on specific components and features, you can request documentation for any of these topics:

""" + "\n".join(f"- **{topic}**: {desc}" for topic, (_, desc) in TOPIC_MAPPING.items())

    return _get_topic_specific_docs(topic)


def _get_topic_specific_docs(topic: str) -> str:
    """Get detailed documentation for a specific topic using raw GitHub URLs."""
    logger.info(f"Fetching detailed docs for topic: {topic}")

    if topic not in TOPIC_MAPPING:
        return f"# {topic} Documentation\n\nTopic '{topic}' not found. Please check the available topics list from the overview.\n\nAvailable topics: {', '.join(TOPIC_MAPPING.keys())}"

    full_url: str
    topic_path, _ = TOPIC_MAPPING[topic]
    if "https://" in topic_path:
        full_url = topic_path
    else:
        full_url = f"https://raw.githubusercontent.com/airbytehq/airbyte/master/{topic_path}"

    try:
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()

        markdown_content = response.text
        return f"# '{topic}' Documentation\n\n{markdown_content}"

    except Exception as e:
        logger.error(f"Error fetching documentation for topic '{topic}': {e}")

        return (
            f"Unable to fetch detailed documentation for topic '{topic}' "
            f"using path '{topic_path}' and full URL '{full_url}'."
            f"\n\nError: {e!s}"
        )


def _is_manifest_only_connector(connector_name: str) -> bool:
    """Check if a connector is manifest-only by querying the registry.

    Args:
        connector_name: Name of the connector (e.g., 'source-faker')

    Returns:
        True if the connector is manifest-only, False otherwise or on error
    """
    try:
        response = requests.get(_REGISTRY_URL, timeout=30)
        response.raise_for_status()
        registry_data = response.json()

        for connector_list in [
            registry_data.get("sources", []),
            registry_data.get("destinations", []),
        ]:
            for connector in connector_list:
                docker_repo = connector.get("dockerRepository", "")
                repo_connector_name = docker_repo.replace("airbyte/", "")

                if repo_connector_name == connector_name:
                    language = connector.get("language")
                    tags = connector.get("tags", [])

                    return (
                        language == _MANIFEST_ONLY_LANGUAGE
                        or f"language:{_MANIFEST_ONLY_LANGUAGE}" in tags
                    )

    except Exception as e:
        logger.warning(f"Failed to fetch registry data for {connector_name}: {e}")
        return False
    else:
        # No exception and no match found.
        logger.info(f"Connector {connector_name} was not found in the registry.")
        return False


def get_connector_manifest(
    connector_name: Annotated[
        str,
        Field(description="Name of the connector (e.g., 'source-stripe')"),
    ],
    version: Annotated[
        str,
        Field(
            description="Version of the connector manifest to retrieve. If not provided, defaults to 'latest'"
        ),
    ] = "latest",
) -> str:
    """Get the raw connector manifest YAML from connectors.airbyte.com.

    Args:
        connector_name: Name of the connector (e.g., 'source-stripe')
        version: Version of the connector manifest to retrieve (defaults to 'latest')

    Returns:
        Raw YAML content of the connector manifest
    """
    logger.info(f"Getting connector manifest for {connector_name} version {version}")

    cleaned_version = version.removeprefix("v")
    is_manifest_only = _is_manifest_only_connector(connector_name)

    logger.info(
        f"Connector {connector_name} is {'manifest-only' if is_manifest_only else 'not manifest-only'}."
    )
    if not is_manifest_only:
        return "ERROR: This connector is not manifest-only."

    manifest_url = f"https://connectors.airbyte.com/metadata/airbyte/{connector_name}/{cleaned_version}/manifest.yaml"

    try:
        response = requests.get(manifest_url, timeout=30)
        response.raise_for_status()

        return response.text

    except Exception as e:
        logger.error(f"Error fetching connector manifest for {connector_name}: {e}")
        return (
            f"# Error fetching manifest for connector '{connector_name}' version "
            f"'{version}' from {manifest_url}\n\nError: {str(e)}"
        )


# @mcp.tool() // Deferred
def get_manifest_yaml_json_schema() -> str:
    """Retrieve the connector manifest JSON schema from the Airbyte repository.

    This tool fetches the official JSON schema used to validate connector manifests.
    The schema defines the structure, required fields, and validation rules for
    connector YAML configurations.

    Returns:
        Response containing the schema in YAML format
    """
    # URL to the manifest schema in the Airbyte Python CDK repository

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "connector-schema-tool",
    }

    response = requests.get(
        _MANIFEST_SCHEMA_URL,
        headers=headers,
        timeout=30,
    )
    if response.status_code == _HTTP_OK:
        return response.text

    response.raise_for_status()  # Raise HTTPError for bad responses
    raise RuntimeError(
        "Something went wrong. Expected success or exception but neither occurred."
    )  # pragma: no cover # This line should not be reached


def find_connectors_by_class_name(class_names: str) -> list[str]:
    """Find connectors that use ALL specified class names/components.

    This tool searches for connectors that implement specific declarative component classes.

    Examples of valid class names:
    - DynamicDeclarativeStream (for dynamic stream discovery)
    - HttpComponentsResolver (for HTTP-based component resolution)
    - ConfigComponentsResolver (for config-based component resolution)
    - OAuthAuthenticator (for OAuth authentication)
    - ApiKeyAuthenticator (for API key authentication)

    Args:
        class_names: Comma-separated string of exact class names to search for.
                    Use class names like "DynamicDeclarativeStream", not feature
                    descriptions like "dynamic streams" or "pagination".

    Returns:
        List of connector names that use ALL specified class names
    """
    if not class_names.strip():
        return []

    class_name_list = [f.strip() for f in class_names.split(",") if f.strip()]
    if not class_name_list:
        return []

    csv_path = Path(__file__).parent / "resources" / "generated" / "connector-feature-index.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Feature index file not found: {csv_path}")

    feature_to_connectors: dict[str, set[str]] = {}

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            feature = row["FeatureUsage"]
            connector = row["ConnectorName"]

            if feature not in feature_to_connectors:
                feature_to_connectors[feature] = set()
            feature_to_connectors[feature].add(connector)

    result_connectors = None

    for class_name in class_name_list:
        if class_name not in feature_to_connectors:
            return []

        connectors_with_class = feature_to_connectors[class_name]

        if result_connectors is None:
            result_connectors = connectors_with_class.copy()
        else:
            result_connectors = result_connectors.intersection(connectors_with_class)

    return sorted(result_connectors) if result_connectors else []


def register_connector_builder_tools(app: FastMCP) -> None:
    """Register connector builder tools with the FastMCP app.

    Args:
        app: FastMCP application instance
    """
    app.tool(validate_manifest)
    app.tool(execute_stream_test_read)
    app.tool(run_connector_readiness_test_report)
    app.tool(execute_dynamic_manifest_resolution_test)
    app.tool(get_manifest_yaml_json_schema)
    app.tool(get_connector_builder_checklist)
    app.tool(get_connector_builder_docs)
    app.tool(get_connector_manifest)
    app.tool(find_connectors_by_class_name)
    app.tool(create_connector_manifest_scaffold)
    register_secrets_tools(app)
