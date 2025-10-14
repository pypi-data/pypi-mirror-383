import warnings
from typing import Any

from sqlalchemy.orm import RelationshipProperty, object_session, relationship

from liminal.orm.base_model import BaseModel
from liminal.orm.column import Column


def single_relationship(
    target_class_name: str, entity_link_field: Column, backref: str | None = None
) -> RelationshipProperty:
    """Wrapper for SQLAlchemy's relationship function. Liminal's recommendation for defining a relationship from
    a class to a linked entity field. This means the representation of that field is a single entity_id.

    Parameters
    ----------
    target_class_name : str
        Class name of the entity schema class that is being linked.
    entity_link_field : Column
        Column on the current class that links to the target class.
    backref : str | None, optional
        backref argument for the SQLAlchemy relationship. setting backrefcreates a new property on the related class that points back to the original class.
        This makes it easy to navigate the relationship in both directions without having to explicitly define the reverse relationship.

    Returns
    -------
    SQLAlchemy RelationshipProperty
    """
    return relationship(
        target_class_name,
        foreign_keys=entity_link_field,
        backref=backref if backref else None,
        uselist=False,
    )


def multi_relationship(*args: Any, **kwargs: Any) -> RelationshipProperty:
    """Wrapper for generating a multi-relationship. Supporting the usage of a deprecated signature until v5 release."""
    if len(args) == 2 and isinstance(args[1], Column):
        return multi_relationship_v2(*args, **kwargs)
    else:
        return multi_relationship_deprecated(*args, **kwargs)


def multi_relationship_deprecated(
    target_class_name: str, current_class_name: str, entity_link_field_name: str
) -> RelationshipProperty:
    """
    DEPRECATED: USE THE FUNCTION BELOW INSTEAD.
    Wrapper for SQLAlchemy's relationship function. Liminal's recommendation for defining a relationship from
    a class to a linked entity field that has is_multi=True. This means the representation of that field is a list of entity_ids.
    Parameters
    ----------
    target_class_name : str
        Class name of the entity schema class that is being linked.
    current_class_name : str
        Name of the current class that is linking to the target class. This is not used.
    entity_link_field_name : str
        Name of the column on the current class that links to the target class.

    Returns
    -------
    SQLAlchemy RelationshipProperty
    """
    warnings.warn(
        "This version of multi_relationship is deprecated. New function signature is multi_relationship(target_class_name: str, entity_link_field: Column). Support for this signature will end with the v5 release.",
        FutureWarning,
        stacklevel=2,
    )

    def getter(self: Any) -> list[Any]:
        target_table = BaseModel.get_all_subclasses(names={target_class_name})[0]
        session = object_session(self)

        linked_entities = (
            session.query(target_table)
            .filter(target_table.id.in_(getattr(self, entity_link_field_name)))
            .all()
        )
        return linked_entities

    return property(getter)


def multi_relationship_v2(
    target_class_name: str, entity_link_field: Column
) -> RelationshipProperty:
    """Wrapper for SQLAlchemy's relationship function. Liminal's recommendation for defining a relationship from
    a class to a linked entity field that has is_multi=True. This means the representation of that field is a list of entity_ids.
    Parameters
    ----------
    target_class_name : str
        Class name of the entity schema class that is being linked.
    entity_link_field : Column
        Column on the current class that links to the target class.

    Returns
    -------
    SQLAlchemy RelationshipProperty
    """

    def getter(self: Any) -> list[Any]:
        target_table = BaseModel.get_all_subclasses(names={target_class_name})[0]
        session = object_session(self)

        linked_entities = (
            session.query(target_table)
            .filter(target_table.id.in_(getattr(self, entity_link_field.name)))
            .all()
        )
        return linked_entities

    return property(getter)
