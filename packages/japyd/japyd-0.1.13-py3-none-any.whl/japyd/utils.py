import json
import typing as t

from .jsonapi import Relationship, Resource, ResourceIdentifier, TopLevel


@t.overload
def extract_relationship(toplevel: dict | str, relationship: str) -> list[dict] | dict:
    """Extracts from dict or a JSON string."""


@t.overload
def extract_relationship(toplevel: TopLevel, relationship: Relationship | str) -> list[Resource] | Resource:
    """Extracts from a TopLevel model as a single resource."""


def extract_relationship(toplevel, relationship):
    """Returns the resource associated with the relationship if defined in included.

    :param toplevel: The toplevel jsonapi structure.
    :param relationship: The relationship to extract or the relationship path to extract.
    """
    tl = toplevel
    if isinstance(tl, str):
        tl = json.loads(tl)
    if isinstance(tl, dict):
        tl = TopLevel.model_validate(tl)
    if not tl.data:
        raise AttributeError("Wrong toplevel strucure: no data.")

    if isinstance(relationship, str):
        identifiers = get_relation_identifiers(tl, tl.data, relationship)
    elif isinstance(relationship, Relationship):
        identifiers = relationship.data
    else:
        raise AttributeError("Wrong relationship strucure.")

    if isinstance(identifiers, list):
        # Set in dictionary to avoid duplicate
        resources = {}
        for ident in identifiers:
            res = extract_from_resource_identifier(tl, ident)
            if isinstance(toplevel, str) or isinstance(toplevel, dict):
                resources[f"{res.type}{res.id}"] = res.model_dump()
            else:
                resources[f"{res.type}{res.id}"] = res
        return list(resources.values())

    res = extract_from_resource_identifier(tl, t.cast(ResourceIdentifier, identifiers))
    if isinstance(toplevel, str) or isinstance(toplevel, dict):
        return res.model_dump()
    return res


def extract_from_resource_identifier(toplevel: TopLevel, identifier: ResourceIdentifier) -> Resource:
    """Returns the resource associated with the resource identifier if defined in included.

    :param toplevel: The toplevel jsonapi structure.
    :param identifier: The resource identifier.
    """

    # Get all attributes values of the included resources
    if toplevel.included:
        for r in toplevel.included:
            if r.type == identifier.type and r.id == identifier.id:
                return r
    raise AttributeError(f"Cannot extract identifier {identifier} from {toplevel}")


def get_relation_identifiers(toplevel, data, relationship: str) -> ResourceIdentifier | list[ResourceIdentifier]:
    if isinstance(data, list):
        flat_list = []
        for d in data:
            rel = d.relationships[relationship].data
            flat_list.extend(rel) if isinstance(rel, list) else flat_list.append(rel)
        return flat_list

    if "." not in relationship:
        if relationship not in data.relationships:
            raise AttributeError(f"Cannot extract relationship {relationship} from {toplevel}")
        return data.relationships[relationship].data

    # Composed relationships
    relationship, other, *_ = relationship.split(".", 1)
    res = extract_relationship(toplevel, relationship)
    if isinstance(res, list):
        flat_list = []
        for r in res:
            rel = get_relation_identifiers(toplevel, r, other)
            flat_list.extend(rel) if isinstance(rel, list) else flat_list.append(rel)
        return flat_list
    else:
        return get_relation_identifiers(toplevel, res, other)


def flatten_resource(res: Resource | dict, *, more: dict | None = None) -> dict:
    """Returns the resource attributes with the 'id' added. Can add more data if needed."""
    more = more or {}
    if isinstance(res, Resource):
        return {"id": res.id, **res.attributes, **more}
    return {"id": res["id"], **res["attributes"], **more}


def to_bool(val: t.Any) -> bool:
    if isinstance(val, str):
        return val.lower() in ["true", "1", "yes", "y"]
    return bool(val)


def to_string_or_numeric(value: str) -> str | int | float:
    if value.startswith("'"):
        return value.strip("'")
    return float(value) if "." in value else int(value)
