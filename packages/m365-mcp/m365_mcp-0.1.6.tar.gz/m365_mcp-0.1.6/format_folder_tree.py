#!/usr/bin/env python3
"""
Format OneDrive folder tree data into ASCII tree representation.

Usage:
    python format_folder_tree.py

This script will use the m365-mcp tool to fetch folder tree data and display it
in a nice ASCII tree format.
"""

import json
from typing import Any


def format_tree(folders: list[dict[str, Any]], prefix: str = "", is_last: bool = True) -> list[str]:
    """
    Recursively format folder tree data into ASCII tree lines.

    Args:
        folders: List of folder dictionaries with 'name' and 'children' keys
        prefix: Current line prefix for tree characters
        is_last: Whether this is the last item in the current level

    Returns:
        List of formatted tree lines
    """
    lines = []

    for i, folder in enumerate(folders):
        is_last_item = (i == len(folders) - 1)

        # Choose the right tree characters
        if is_last_item:
            connector = "└── "
            extension = "    "
        else:
            connector = "├── "
            extension = "│   "

        # Format folder name with metadata
        name = folder.get("name", "Unknown")
        child_count = folder.get("childCount", 0)
        folder_info = f"{name} ({child_count} items)"

        # Add the current folder line
        lines.append(f"{prefix}{connector}{folder_info}")

        # Recursively process children
        children = folder.get("children", [])
        if children:
            child_prefix = prefix + extension
            child_lines = format_tree(children, child_prefix, is_last_item)
            lines.extend(child_lines)

    return lines


def format_folder_tree_response(tree_data: dict[str, Any]) -> str:
    """
    Format the complete folder_get_tree response into ASCII tree.

    Args:
        tree_data: Response from folder_get_tree tool

    Returns:
        Formatted ASCII tree as string
    """
    root_path = tree_data.get("root_path", "/")
    max_depth = tree_data.get("max_depth", 10)
    folders = tree_data.get("folders", [])

    # Build the tree
    lines = [
        f"OneDrive Folder Tree: {root_path}",
        f"Max Depth: {max_depth}",
        f"Total Top-Level Folders: {len(folders)}",
        "",
    ]

    # Add the tree structure
    tree_lines = format_tree(folders)
    lines.extend(tree_lines)

    return "\n".join(lines)


# Example tree data from the previous response
if __name__ == "__main__":
    # This is the data structure returned by folder_get_tree
    example_data = {
        "root_folder_id": None,
        "root_path": "/",
        "max_depth": 3,
        "folders": [
            {
                "id": "D16CEBAA65A1624C!391857",
                "name": "Apps",
                "childCount": 6,
                "path": "/drive/root:",
                "parentId": "D16CEBAA65A1624C!sea8cc6beffdb43d7976fbc7da445c639",
                "modified": "2023-08-16T16:54:25Z",
                "children": [
                    {
                        "id": "D16CEBAA65A1624C!392873",
                        "name": "Designer",
                        "childCount": 2,
                        "path": "/drive/root:/Apps",
                        "parentId": "D16CEBAA65A1624C!391857",
                        "modified": "2023-10-05T07:41:41Z",
                        "children": [
                            {
                                "id": "D16CEBAA65A1624C!421792",
                                "name": "Generated Content",
                                "childCount": 1,
                                "path": "/drive/root:/Apps/Designer",
                                "parentId": "D16CEBAA65A1624C!392873",
                                "modified": "2024-01-16T07:17:16Z",
                                "children": []
                            },
                            {
                                "id": "D16CEBAA65A1624C!392874",
                                "name": "My stuff",
                                "childCount": 2,
                                "path": "/drive/root:/Apps/Designer",
                                "parentId": "D16CEBAA65A1624C!392873",
                                "modified": "2023-10-05T07:41:42Z",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "D16CEBAA65A1624C!453790",
                        "name": "remotely-save",
                        "childCount": 1,
                        "path": "/drive/root:/Apps",
                        "parentId": "D16CEBAA65A1624C!391857",
                        "modified": "2024-05-06T20:41:31Z",
                        "children": [
                            {
                                "id": "D16CEBAA65A1624C!453791",
                                "name": "TAFESA",
                                "childCount": 0,
                                "path": "/drive/root:/Apps/remotely-save",
                                "parentId": "D16CEBAA65A1624C!453790",
                                "modified": "2024-05-06T20:41:32Z",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": "D16CEBAA65A1624C!389713",
                "name": "Desktop",
                "childCount": 49,
                "path": "/drive/root:",
                "parentId": "D16CEBAA65A1624C!sea8cc6beffdb43d7976fbc7da445c639",
                "modified": "2023-05-25T10:25:19Z",
                "children": [
                    {
                        "id": "D16CEBAA65A1624C!sabf53052979249c2a45533470926043b",
                        "name": "ComfyUI-Crystools",
                        "childCount": 22,
                        "path": "/drive/root:/Desktop",
                        "parentId": "D16CEBAA65A1624C!389713",
                        "modified": "2025-06-20T03:07:10Z",
                        "children": [
                            {
                                "id": "D16CEBAA65A1624C!s0611c1deb78e417f923729174117b5d0",
                                "name": ".github",
                                "childCount": 2,
                                "path": "/drive/root:/Desktop/ComfyUI-Crystools",
                                "parentId": "D16CEBAA65A1624C!sabf53052979249c2a45533470926043b",
                                "modified": "2025-06-20T03:07:09Z",
                                "children": []
                            }
                        ]
                    }
                ]
            }
        ]
    }

    # Format and print the tree
    print(format_folder_tree_response(example_data))
