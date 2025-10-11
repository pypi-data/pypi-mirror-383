from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from sqlalchemy import insert, tuple_
from app import models
from app.utils.admin_utils import admin

from typing import Type, Dict, Any
from app.utils import enums, sql_utils
from typing import TypeVar

T = TypeVar("T")


def create_properties(db: Session, properties: list[models.PropertyInput]) -> list[dict]:
    for prop in properties:
        if prop.semantic_type_name:
            semantic_type = db.query(models.SemanticType).filter_by(name=prop.semantic_type_name).first()
            prop.semantic_type_id = semantic_type.id
            delattr(prop, "semantic_type_name")

    return bulk_create_if_not_exists(db, models.Property, models.PropertyBase, properties)


def get_properties(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Property).offset(skip).limit(limit).all()


def bulk_create_if_not_exists(
    db: Session,
    model_cls: Type,
    base_model_cls: Type,
    items: List[Any],
    *,
    name_attr: str = "name",
    validate: bool = True,
) -> List[Dict[str, Any]]:
    """
    Bulk insert records into the database for the given SQLModel class, only if records with the same
    unique identifier (specified by `name_attr`) do not already exist.

    This function is designed for efficient batch creation of SQLModel instances,
    validating input items against a base SQLModel class before insertion, and
    adding audit fields such as created_by and updated_by automatically.

    Args:
        db (Session): SQLAlchemy session used to query and insert data.
        model_cls (Type[SQLModel]): The SQLModel ORM model class representing the target table.
        base_model_cls (Type[SQLModel]): The SQLModel base class used for validation and serialization.
        items (List[SQLModel]): List of SQLModel instances to insert.
        name_attr (str, optional): Attribute name used to check uniqueness (default: "name").
        validate (bool, optional): Whether to validate each item using `base_model_cls` before insert (default: True).

    Returns:
        List[Dict[str, Any]]: List of inserted records.
    """
    reserved_names = [field["name"] for field in sql_utils.get_direct_fields()]
    reserved_names.append("smiles")
    has_entity_type = hasattr(model_cls, "entity_type")

    def get_key(item):
        if has_entity_type:
            return (getattr(item, name_attr), getattr(item, "entity_type"))
        return getattr(item, name_attr)

    input_keys = [get_key(item) for item in items]

    if has_entity_type:
        existing_entities = set(
            db.query(getattr(model_cls, name_attr), getattr(model_cls, "entity_type"))
            .filter(tuple_(getattr(model_cls, name_attr), getattr(model_cls, "entity_type")).in_(input_keys))
            .all()
        )
    else:
        existing_entities = set(
            value
            for (value,) in db.query(getattr(model_cls, name_attr))
            .filter(getattr(model_cls, name_attr).in_(input_keys))
            .all()
        )

    to_insert = []
    inserted_input_items = []
    result = []

    for item in items:
        item_name = getattr(item, name_attr)
        item_key = get_key(item)

        if item_name in reserved_names:
            result.append(
                {"name": item_name}
                | {
                    "registration_status": "failed",
                    "registration_error_message": f"{item_name} is a reserved name and cannot be used",
                }
            )
            continue

        if item_key in existing_entities:
            result.append(
                item.model_dump()
                | {"registration_status": "Skipped", "registration_error_message": f"{item_name} already exists"}
            )
            continue

        try:
            validated = base_model_cls.model_validate(item) if validate else item
            data = validated.model_dump()
            data.update(
                {
                    "created_by": admin.admin_user_id,
                    "updated_by": admin.admin_user_id,
                }
            )
            to_insert.append(data)
            inserted_input_items.append(item)
        except Exception as e:
            result.append(
                item.model_dump() | {"registration_status": "failed", "registration_error_message": str(e.args[0])}
            )

    if to_insert:
        try:
            stmt = insert(model_cls).values(to_insert).returning(model_cls)
            db_result = db.execute(stmt).fetchall()
            db.commit()

            for i, row in enumerate(db_result):
                result.append(model_cls.model_validate(row[0]).model_dump() | {"registration_status": "success"})
        except Exception as e:
            reason = f"Insert error: {str(e.args[0])}"
            for item in inserted_input_items:
                result.append(
                    item.model_dump() | {"registration_status": "failed", "registration_error_message": f"{reason}"}
                )

    return result


def get_synonym_id(db: Session) -> int:
    result = db.query(models.SemanticType.id).filter(models.SemanticType.name == "Synonym").scalar()
    if result is None:
        raise HTTPException(status_code=400, detail="Semantic type 'Synonym' not found.")
    return result


def get_entities_by_entity_type(
    db: Session,
    entity_type: Optional[enums.EntityType] = None,
    semantic_type_id: Optional[int] = None,
):
    query = db.query(models.Property)
    if entity_type is not None:
        query = query.filter(models.Property.entity_type == entity_type)
    if semantic_type_id is not None:
        query = query.filter(models.Property.semantic_type_id == semantic_type_id)
    return query.all()


def enrich_properties(owner, detail_attr: str, id_attr: str) -> list[models.PropertyWithValue]:
    enriched = []
    owner_id = getattr(owner, "id")
    for prop in owner.properties:
        details = getattr(prop, detail_attr, [])
        detail = next((d for d in details if getattr(d, id_attr, None) == owner_id), None)
        enriched.append(
            models.PropertyWithValue(
                **prop.dict(),
                value_qualifier=handle_value_qualifier(getattr(detail, "value_qualifier", None)),
                value_num=getattr(detail, "value_num", None),
                value_string=getattr(detail, "value_string", None),
                value_datetime=getattr(detail, "value_datetime", None),
                value_uuid=getattr(detail, "value_uuid", None),
            )
        )
    return enriched


def handle_value_qualifier(value_qualifier: int | None):
    if value_qualifier is None:
        return None

    value_qualifier_map = {
        enums.ValueQualifier.EQUALS.value: "=",
        enums.ValueQualifier.LESS_THAN.value: "<",
        enums.ValueQualifier.GREATER_THAN.value: ">",
    }
    return value_qualifier_map[value_qualifier]


def enrich_model(owner, response_class: Type[T], detail_attr: str, id_attr: str) -> T:
    """
    Generic enrichment function.

    Args:
        owner: The SQLModel object to enrich (e.g., Assay, AssayResult).
        response_class: The corresponding Response model class (e.g., AssayResponse).
        detail_attr: Attribute name where the detail rows live (e.g., 'assay_details').
        id_attr: Foreign key attribute name (e.g., 'assay_id').

    Returns:
        An enriched response model instance of type `response_class`.
    """
    resp = response_class.model_validate(owner, from_attributes=True)
    if hasattr(owner, "properties"):
        resp.properties = enrich_properties(owner, detail_attr, id_attr)
    return resp
