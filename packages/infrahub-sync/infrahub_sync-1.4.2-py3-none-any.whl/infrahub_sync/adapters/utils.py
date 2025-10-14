from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from diffsync import Adapter


def build_mapping(adapter: Adapter, reference: str, obj, field) -> str:
    """This is used when references are encountered to attempt to resolve them for mapping."""
    # Get object class and model name from the store
    object_class, modelname = adapter.store._get_object_class_and_model(model=reference)

    # Find the schema element matching the model name
    schema_element = next(
        (element for element in adapter.config.schema_mapping if element.name == modelname),
        None,
    )
    if not schema_element:
        msg = (
            f"Schema mapping for model '{reference}' not found when attempting to resolve "
            f"reference for {field.name}. The reference must be an existing schema mapping."
        )
        raise ValueError(msg)

    # Collect all relevant field mappings for identifiers
    new_identifiers = []

    # Convert schema_element.fields to a dictionary for fast lookup
    field_dict = {field.name: field.mapping for field in schema_element.fields}

    # Loop through object_class._identifiers to find corresponding field mappings
    for identifier in object_class._identifiers:
        if identifier in field_dict:
            new_identifiers.append(field_dict[identifier])

    # Construct the unique identifier, using a fallback if a key isn't found
    unique_id = "__".join(str(obj.get(key, "")) for key in new_identifiers)
    return unique_id


def get_value(obj: Any, name: str) -> Any | None:
    """Query a value in dot notation recursively"""
    if "." not in name:
        # Check if the object is a dictionary and use appropriate method to access the attribute.
        if isinstance(obj, dict):
            return obj.get(name)
        return getattr(obj, name, None)

    first_name, remaining_part = name.split(".", maxsplit=1)

    # Check if the object is a dictionary and use appropriate method to access the attribute.
    sub_obj = obj.get(first_name) if isinstance(obj, dict) else getattr(obj, first_name, None)

    if not sub_obj:
        return None
    return get_value(obj=sub_obj, name=remaining_part)


def derive_identifier_key(obj: dict[str, Any]) -> str | None:
    """Try to get obj.id, and if it doesn't exist, try to get a key ending with _id"""
    obj_id = obj.get("id")
    if obj_id is None:
        for key, value in obj.items():
            if key.endswith("_id") and value:
                obj_id = value
                break

    # If we still didn't find any id, raise ValueError
    if obj_id is None:
        msg = "No suitable identifier key found in object"
        raise ValueError(msg)
    return obj_id
