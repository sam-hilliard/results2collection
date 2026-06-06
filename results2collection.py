#!/usr/bin/env python3

import copy
import json
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_passing_request_names(results):
    """
    Returns the names of all requests that had at least one passing test.
    """
    passing = set()

    for result in results.get("results", []):
        tests = result.get("tests", {})

        if any(value is True for value in tests.values()):
            passing.add(result["name"])

    return passing


def filter_items(items, passing_names):
    """
    Recursively copies only folders/requests that match passing_names.
    Preserves folder hierarchy.
    """
    output = []

    for item in items:
        # Folder
        if "item" in item:
            filtered_children = filter_items(
                item["item"],
                passing_names,
            )

            if filtered_children:
                folder = copy.deepcopy(item)
                folder["item"] = filtered_children
                output.append(folder)

        # Request
        elif item.get("name") in passing_names:
            output.append(copy.deepcopy(item))

    return output


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python results2collection.py collection.json results.json",
            file=sys.stderr,
        )
        sys.exit(1)

    collection = load_json(sys.argv[1])
    results = load_json(sys.argv[2])

    passing_names = get_passing_request_names(results)

    new_collection = {
        "info": copy.deepcopy(collection["info"]),
        "item": filter_items(
            collection.get("item", []),
            passing_names,
        ),
    }

    with open("results-collection.json", "w", encoding="utf-8") as f:
        json.dump(new_collection, f, indent=2)


if __name__ == "__main__":
    main()
