import csv
import io
import os
import tempfile
import shutil
import uvicorn
from fastapi import APIRouter, Body, FastAPI, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import insert
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Type

import yaml
from app.services.registrars.assay_result_registrar import AssayResultsRegistrar
from app.services.registrars.assay_run_registrar import AssayRunRegistrar
from app.services.registrars.batch_registrar import BatchRegistrar
from app.services.registrars.compound_registrar import CompoundRegistrar
from app import models
from app import crud
from app.services.registrars.writer import StreamingResultWriter
from app.utils import enums
from app.services.properties.property_service import PropertyService
from app.services.search.engine import SearchEngine
from app.services.search.search_filter_builder import SearchFilterBuilder

from sqlalchemy.sql import text

from app.utils.logging_utils import logger
from app.utils.admin_utils import admin
from app.utils.chemistry_utils import get_molecule_standardization_config
from app.utils.sql_utils import get_direct_fields


# Handle both package imports and direct execution
try:
    # When imported as a package (for tests)
    from . import models
    from .setup.database import SessionLocal
except ImportError:
    # When run directly
    import app.models as models
    from app.setup.database import SessionLocal

# models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="MolTrack API", description="API for managing chemical compounds and batches")
router = APIRouter(prefix="/v1")


# Dependency
def get_db():
    db = SessionLocal()
    logger.debug(db.bind.url)
    logger.debug("Database connection successful")
    try:
        yield db
    finally:
        db.close()


def get_or_raise_exception(get_func, db, *args, not_found_msg=None, **kwargs):
    item = get_func(db, *args, **kwargs)
    if not item:
        msg = not_found_msg or "Item not found"
        raise HTTPException(status_code=404, detail=msg)
    return item


@router.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)


@router.post("/auto-map-columns")
def auto_map_columns(
    entity_type: enums.EntityType = Body(...), columns: List[str] = Body(...), db: Session = Depends(get_db)
) -> Dict[str, str]:
    registrar_map = {
        enums.EntityType.COMPOUND: CompoundRegistrar,
        enums.EntityType.BATCH: BatchRegistrar,
        enums.EntityType.ASSAY_RUN: AssayRunRegistrar,
        enums.EntityType.ASSAY_RESULT: AssayResultsRegistrar,
    }

    registrar_class = registrar_map.get(entity_type)
    if not registrar_class:
        raise ValueError(f"No registrar found for entity type {entity_type}")

    registrar = registrar_class(db, None)
    mapping = {col: registrar._assign_column(col) for col in columns}
    return mapping


@router.get("/users/", response_model=List[models.UserBase])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()


# === Schema endpoints for supplementary data like properties and synonyms ===
# https://github.com/datagrok-ai/mol-track/blob/main/api_design.md#schema---wip
@router.post("/schema/")
def preload_schema(payload: models.SchemaPayload, db: Session = Depends(get_db)):
    try:
        created_synonyms = crud.create_properties(db, payload.synonym_types)
        created_properties = crud.create_properties(db, payload.properties)
        return {
            "status": "success",
            "synonym_types": created_synonyms,
            "property_types": created_properties,
        }
    except Exception as e:
        db.rollback()
        return {"status": "failed", "error": str(e)}


@router.get("/schema/", response_model=List[models.PropertyRetrieve])
def get_schema(db: Session = Depends(get_db)):
    return crud.get_entities_by_entity_type(db)


@router.get("/schema-direct/")
def get_schema_direct():
    return get_direct_fields()


@router.get("/schema/compounds", response_model=List[models.PropertyBase])
def get_schema_compounds(db: Session = Depends(get_db)):
    return crud.get_entities_by_entity_type(db, enums.EntityType.COMPOUND)


@router.get("/schema/compounds/synonyms", response_model=List[models.SynonymTypeBase])
def get_schema_compound_synonyms(db: Session = Depends(get_db)):
    return crud.get_entities_by_entity_type(db, enums.EntityType.COMPOUND, crud.get_synonym_id(db))


def fetch_additions(db: Session):
    return (
        db.query(models.Addition)
        .join(models.BatchAddition, models.Addition.id == models.BatchAddition.addition_id)
        .distinct()
        .all()
    )


@router.get("/schema/batches", response_model=models.SchemaBatchResponse)
def get_schema_batches(db: Session = Depends(get_db)):
    properties = crud.get_entities_by_entity_type(db, enums.EntityType.BATCH)
    additions = fetch_additions(db)
    return models.SchemaBatchResponse(properties=properties, additions=additions)


@router.get("/schema/batches/synonyms", response_model=models.SchemaBatchResponse)
def get_schema_batch_synonyms(db: Session = Depends(get_db)):
    synonym_types = crud.get_entities_by_entity_type(db, enums.EntityType.BATCH, crud.get_synonym_id(db))
    additions = fetch_additions(db)
    return models.SchemaBatchResponse(synonym_types=synonym_types, additions=additions)


# === Compounds endpoints ===
# https://github.com/datagrok-ai/mol-track/blob/main/api_design.md#register-virtual-compounds
def process_registration(
    registrar_class: Type,
    file: UploadFile,
    mapping: Optional[str],
    error_handling,
    output_format,
    db: Session,
):
    extension = file.filename.split(".")[-1].lower()
    if extension not in ["csv", "sdf"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only CSV or SDF allowed.")

    registrar = registrar_class(db=db, mapping=mapping, error_handling=error_handling)

    tmp = tempfile.SpooledTemporaryFile(mode="w+b", max_size=50 * 1024 * 1024)
    shutil.copyfileobj(file.file, tmp)
    tmp.seek(0)

    processor = registrar.process_csv if extension == "csv" else registrar.process_sdf

    def row_generator():
        try:
            with io.TextIOWrapper(tmp, encoding="utf-8", newline="") as text_stream:
                for chunk_rows in processor(text_stream, chunk_size=5000):
                    registrar.register_all(chunk_rows)
                    yield registrar.output_rows.copy()
                    registrar.cleanup_chunk()
        finally:
            tmp.close()
            registrar.cleanup()

    media_type_map = {
        "csv": "text/csv",
        "json": "application/json",
        "sdf": "chemical/x-mdl-sdfile",
    }

    result_writer = StreamingResultWriter(output_format.value)
    return StreamingResponse(
        result_writer.stream_rows(row_generator()),
        media_type=media_type_map.get(output_format.value, "application/octet-stream"),
        headers={"Content-Disposition": f"attachment; filename=registration_result.{output_format.value}"},
    )


@router.post("/compounds/")
def register_compounds(
    file: UploadFile = File(...),
    mapping: Optional[str] = Form(None),
    error_handling: enums.ErrorHandlingOptions = Form(enums.ErrorHandlingOptions.reject_all),
    output_format: enums.OutputFormat = Form(enums.OutputFormat.json),
    db: Session = Depends(get_db),
):
    return process_registration(
        CompoundRegistrar,
        file,
        mapping,
        error_handling,
        output_format,
        db,
    )


@router.get("/compounds/", response_model=List[models.CompoundResponse])
def get_compounds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    compounds = crud.read_compounds(db, skip=skip, limit=limit)
    return compounds


@router.get("/compounds", response_model=models.CompoundResponse)
def get_compound_by_any_synonym(
    property_value: str, property_name: Optional[str] = None, db: Session = Depends(get_db)
):
    return get_or_raise_exception(
        crud.get_compound_by_synonym, db, property_value, property_name, not_found_msg="Compound not found"
    )


@router.get("/compounds/synonyms", response_model=List[models.PropertyWithValue])
def get_compound_synonyms(property_value: str, property_name: Optional[str] = None, db: Session = Depends(get_db)):
    compound = get_or_raise_exception(
        crud.get_compound_by_synonym, db, property_value, property_name, not_found_msg="Compound not found"
    )
    return [prop for prop in compound.properties if prop.semantic_type_id == crud.get_synonym_id(db)]


@router.get("/compounds/properties", response_model=List[models.PropertyWithValue])
def get_compound_properties(property_value: str, property_name: Optional[str] = None, db: Session = Depends(get_db)):
    compound = get_or_raise_exception(
        crud.get_compound_by_synonym, db, property_value, property_name, not_found_msg="Compound not found"
    )
    return compound.properties


@router.put("/compounds/{corporate_compound_id}", response_model=models.CompoundResponse)
def update_compound_by_id(
    corporate_compound_id: str,
    update_data: models.CompoundUpdate,
    db: Session = Depends(get_db),
):
    return crud.update_compound(db, corporate_compound_id, "corporate_compound_id", update_data)


@router.delete("/compounds/{corporate_compound_id}", response_model=models.Compound)
def delete_compound_by_id(corporate_compound_id: str, db: Session = Depends(get_db)):
    return crud.delete_compound(db, corporate_compound_id, "corporate_compound_id")


# TODO: Create the utils module and move there
def clean_empty_values(d: dict) -> dict:
    return {k: (None if isinstance(v, str) and v.strip() == "" else v) for k, v in d.items()}


# === Additions endpoints ===
# https://github.com/datagrok-ai/mol-track/blob/main/api_design.md#additions
@router.post("/additions/")
def create_additions(csv_file: Optional[UploadFile] = File(None), db: Session = Depends(get_db)):
    if not csv_file:
        raise HTTPException(status_code=400, detail="CSV file is required.")

    if csv_file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    try:
        content = csv_file.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        input_additions = [models.AdditionBase.model_validate(clean_empty_values(row)) for row in reader]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")

    try:
        created_additions = crud.create_additions(db=db, additions=input_additions)
        return {
            "status": "success",
            "additions": created_additions,
        }
    except Exception as e:
        db.rollback()
        return {"status": "failed", "error": str(e)}


@router.get("/additions/", response_model=List[models.Addition])
def read_additions_v1(db: Session = Depends(get_db)):
    return crud.get_additions(db)


@router.get("/additions/salts", response_model=List[models.Addition])
def read_additions_salts_v1(db: Session = Depends(get_db)):
    return crud.get_additions(db, role=enums.AdditionsRole.SALT)


@router.get("/additions/solvates", response_model=List[models.Addition])
def read_additions_solvates_v1(db: Session = Depends(get_db)):
    return crud.get_additions(db, role=enums.AdditionsRole.SOLVATE)


@router.get("/additions/{addition_id}", response_model=models.Addition)
def read_addition_v1(addition_id: int, db: Session = Depends(get_db)):
    return crud.get_addition_by_id(db, addition_id=addition_id)


@router.put("/additions/{addition_id}", response_model=models.Addition)
def update_addition_v1(addition_id: int, addition_update: models.AdditionUpdate, db: Session = Depends(get_db)):
    return crud.update_addition_by_id(db, addition_id, addition_update)


@router.delete("/additions/{addition_id}", response_model=models.Addition)
def delete_addition(addition_id: int, db: Session = Depends(get_db)):
    dependent_batch_addition = crud.get_batch_addition_for_addition(db, addition_id)
    if dependent_batch_addition is not None:
        raise HTTPException(status_code=400, detail="Addition has dependent batches")
    return crud.delete_addition_by_id(db, addition_id=addition_id)


# === Batches endpoints ===
# https://github.com/datagrok-ai/mol-track/blob/main/api_design.md#register-batches
@router.post("/batches/")
def register_batches(
    file: UploadFile = File(...),
    mapping: Optional[str] = Form(None),
    error_handling: enums.ErrorHandlingOptions = Form(enums.ErrorHandlingOptions.reject_all),
    output_format: enums.OutputFormat = Form(enums.OutputFormat.json),
    db: Session = Depends(get_db),
):
    return process_registration(BatchRegistrar, file, mapping, error_handling, output_format, db)


@router.get("/batches/", response_model=List[models.BatchResponse])
def get_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    batches = crud.get_batches(db, skip=skip, limit=limit)
    return batches


@router.get("/batches", response_model=models.BatchResponse)
def get_batch_by_any_synonym(property_value: str, property_name: Optional[str] = None, db: Session = Depends(get_db)):
    return get_or_raise_exception(
        crud.get_batch_by_synonym, db, property_value, property_name, not_found_msg="Batch not found"
    )


@router.get("/batches/properties", response_model=List[models.PropertyWithValue])
def get_batch_properties(property_value: str, property_name: Optional[str] = None, db: Session = Depends(get_db)):
    batch = get_or_raise_exception(
        crud.get_batch_by_synonym, db, property_value, property_name, not_found_msg="Batch not found"
    )
    return batch.properties


@router.get("/batches/synonyms", response_model=List[models.PropertyWithValue])
def get_batch_synonyms(property_value: str, property_name: Optional[str] = None, db: Session = Depends(get_db)):
    batch = get_or_raise_exception(
        crud.get_batch_by_synonym, db, property_value, property_name, not_found_msg="Batch not found"
    )
    return [prop for prop in batch.properties if prop.semantic_type_id == crud.get_synonym_id(db)]


@router.get("/batches/additions", response_model=List[models.BatchAddition])
def get_batch_additions(property_value: str, property_name: Optional[str] = None, db: Session = Depends(get_db)):
    batch = get_or_raise_exception(
        crud.get_batch_by_synonym, db, property_value, property_name, not_found_msg="Batch not found"
    )
    return batch.batch_additions


@router.delete("/batches/{corporate_batch_id}", response_model=models.Batch)
def delete_batch_by_any_synonym(corporate_batch_id: str, db: Session = Depends(get_db)):
    return crud.delete_batch_by_synonym(db, corporate_batch_id, "corporate_batch_id")


# === Assay data endpoints ===
# https://github.com/datagrok-ai/mol-track/blob/main/api_design.md#assay-data-domain
@router.post("/assays")
def create_assays(payload: List[models.AssayCreateBase], db: Session = Depends(get_db)):
    all_properties = {}
    for p in crud.get_properties(db):
        all_properties.setdefault(p.name, []).append(p)
    property_service = PropertyService(all_properties, db, enums.EntityType.ASSAY.value)

    assays_to_insert = [
        {"name": assay.name, "created_by": admin.admin_user_id, "updated_by": admin.admin_user_id} for assay in payload
    ]

    stmt = insert(models.Assay).returning(models.Assay.id)
    inserted_ids = [row[0] for row in db.execute(stmt.values(assays_to_insert)).fetchall()]

    detail_records = []
    property_records = []
    detail_logs = []

    for assay_id, assay in zip(inserted_ids, payload):
        try:
            entity_ids = {"assay_id": assay_id}
            inserted, record = property_service.build_details_records(
                models.AssayDetail,
                properties=assay.extra_fields,
                entity_ids=entity_ids,
                entity_type=enums.EntityType.ASSAY,
                include_user_fields=False,
            )
            detail_records.extend(inserted)
            detail_logs.append({"status": "success", **assay.extra_fields, "registration_error": ""})
        except Exception as e:
            detail_logs.append(
                {"status": "failed", **assay.extra_fields, "registration_error": f"Error processing details: {e}"}
            )

        for prop_data in assay.assay_result_properties:
            prop_info = property_service.get_property_info(prop_data.name, enums.EntityType.ASSAY_RESULT)
            property_records.append(
                {
                    "assay_id": assay_id,
                    "property_id": prop_info["property"].id,
                    "required": prop_data.required,
                }
            )

    if detail_records:
        db.execute(insert(models.AssayDetail).values(detail_records))
    if property_records:
        db.execute(insert(models.AssayProperty).values(property_records))

    db.commit()
    return {"status": "success", "created": assays_to_insert, "details": detail_logs}


@router.get("/assays/", response_model=list[models.AssayResponse])
def get_assays(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assays = crud.get_assays(db, skip=skip, limit=limit)
    return assays


@router.get("/assays/{assay_id}", response_model=models.AssayResponse)
def get_assay_by_id(assay_id: int, db: Session = Depends(get_db)):
    db_assay = crud.get_assay(db, assay_id=assay_id)
    if db_assay is None:
        raise HTTPException(status_code=404, detail="Assay not found")
    return db_assay


@router.post("/assay_runs/")
def create_assay_runs(
    file: UploadFile = File(...),
    mapping: Optional[str] = Form(None),
    error_handling: enums.ErrorHandlingOptions = Form(enums.ErrorHandlingOptions.reject_all),
    output_format: enums.OutputFormat = Form(enums.OutputFormat.json),
    db: Session = Depends(get_db),
):
    return process_registration(AssayRunRegistrar, file, mapping, error_handling, output_format, db)


@router.get("/assay_runs/", response_model=list[models.AssayRunResponse])
def get_assay_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assay_runs = crud.get_assay_runs(db, skip=skip, limit=limit)
    return assay_runs


@router.get("/assay_runs/{assay_run_id}", response_model=models.AssayRunResponse)
def get_assay_run_by_id(assay_run_id: int, db: Session = Depends(get_db)):
    db_assay_run = crud.get_assay_run(db, assay_run_id=assay_run_id)
    if db_assay_run is None:
        raise HTTPException(status_code=404, detail="Assay run found")
    return db_assay_run


@router.post("/assay_results/")
def create_assay_results(
    file: UploadFile = File(...),
    mapping: Optional[str] = Form(None),
    error_handling: enums.ErrorHandlingOptions = Form(enums.ErrorHandlingOptions.reject_all),
    output_format: enums.OutputFormat = Form(enums.OutputFormat.json),
    db: Session = Depends(get_db),
):
    return process_registration(AssayResultsRegistrar, file, mapping, error_handling, output_format, db)


@router.get("/assay_results/", response_model=list[models.AssayResultResponse])
def get_assay_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assay_results = crud.get_assay_results(db, skip=skip, limit=limit)
    return assay_results


@router.get("/validators/")
def get_validators(entity: enums.EntityType, db: Session = Depends(get_db)):
    return crud.get_validators_for_entity(db, entity)


@router.post("/validators/")
def register_validators(
    entity: enums.EntityType = Form(enums.EntityType.COMPOUND),
    name: str = Form(..., embed=True),
    description: Optional[str] = Form(None, embed=True),
    expression: str = Form(..., embed=True),
    db: Session = Depends(get_db),
):
    return crud.create_validator(db, entity, name, expression, description)


@router.delete("/validators/{validator_name}")
def delete_validator_by_name(validator_name: str, db: Session = Depends(get_db)):
    return crud.delete_validator_by_name(db, validator_name)


@router.patch("/admin/update-standardization-config")
async def update_standardization_config(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = file.filename.lower()
    if not (filename.endswith(".yaml") or filename.endswith(".yml")):
        raise HTTPException(status_code=400, detail="Uploaded file must be a YAML file (.yaml or .yml)")

    try:
        content = await file.read()
        yaml.safe_load(content)
        yaml_str = content.decode("utf-8")

        setting = db.query(models.Settings).filter(models.Settings.name == "Molecule standardization rules").first()
        if not setting:
            raise HTTPException(status_code=404, detail="Standardization configuration setting not found")

        setting.value = yaml_str
        db.commit()
        config = get_molecule_standardization_config(db)
        config.clear_cache()

    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the configuration: {str(e)}")

    return JSONResponse(content={"message": "Standardization configuration updated successfully."})


@router.patch("/admin/settings")
def update_settings(
    name: enums.SettingName = Form(...),
    value: str = Form(...),
    db: Session = Depends(get_db),
):
    def parse_int(value: str, field_name: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{field_name} must be an integer")

    if name == enums.SettingName.COMPOUND_MATCHING_RULE:
        try:
            rule_enum = enums.CompoundMatchingRule(value)
        except ValueError:
            allowed = [r.value for r in enums.CompoundMatchingRule]
            raise HTTPException(
                status_code=400, detail=f"Invalid compound matching rule value. Must be one of: {allowed}"
            )
        return update_compound_matching_rule(rule_enum, db)

    setting_handlers = {
        enums.SettingName.COMPOUND_SEQUENCE_START: lambda v: set_molregno_sequence_start(
            parse_int(v, "Compound sequence start"), db
        ),
        enums.SettingName.BATCH_SEQUENCE_START: lambda v: set_batchregno_sequence_start(
            parse_int(v, "Batch sequence start"), db
        ),
        enums.SettingName.CORPORATE_COMPOUND_ID_PATTERN: lambda v: update_institution_id_pattern(
            enums.EntityTypeReduced.COMPOUND, v, db
        ),
        enums.SettingName.CORPORATE_BATCH_ID_PATTERN: lambda v: update_institution_id_pattern(
            enums.EntityTypeReduced.BATCH, v, db
        ),
        enums.SettingName.CORPORATE_COMPOUND_ID_FRIENDLY_NAME: lambda v: update_institution_id_friendly_name(
            enums.EntityTypeReduced.COMPOUND, v, db
        ),
        enums.SettingName.CORPORATE_BATCH_ID_FRIENDLY_NAME: lambda v: update_institution_id_friendly_name(
            enums.EntityTypeReduced.BATCH, v, db
        ),
    }

    handler = setting_handlers.get(name)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Unknown setting: {name}")

    return handler(value)


def update_compound_matching_rule(rule: enums.CompoundMatchingRule, db: Session = Depends(get_db)):
    """
    Update the compound matching rule.
    """
    try:
        old_value_query = db.execute(text("SELECT value FROM moltrack.settings WHERE name = 'Compound Matching Rule'"))
        old_value = old_value_query.scalar()

        if old_value == rule.value:
            return {"status": "success", "message": f"Compound matching rule is already set to {rule.value}"}

        db.execute(
            text("UPDATE moltrack.settings SET value = :rule WHERE name = 'Compound Matching Rule'"),
            {"rule": rule.value},
        )
        db.commit()
        return {"status": "success", "message": f"Compound matching rule updated from {old_value} to {rule.value}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating compound matching rule: {str(e)}")


def update_institution_id_friendly_name(
    entity_type: enums.EntityTypeReduced,
    friendly_name: str,
    db: Session = Depends(get_db),
):
    """
    Update the friendly name for corporate compound or batch IDs.
    """

    if not friendly_name:
        raise HTTPException(status_code=400, detail="Friendly name cannot be empty.")

    property_name = "corporate_batch_id" if entity_type == enums.EntityTypeReduced.BATCH else "corporate_compound_id"
    setting_name = (
        "corporate_batch_id_friendly_name"
        if entity_type == enums.EntityTypeReduced.BATCH
        else "corporate_compound_id_friendly_name"
    )

    try:
        db.execute(
            text("UPDATE moltrack.properties SET friendly_name = :name WHERE name = :property"),
            {"property": property_name, "name": friendly_name},
        )

        db.execute(
            text("UPDATE moltrack.settings SET value = :name WHERE name = :setting"),
            {"setting": setting_name, "name": friendly_name},
        )
        db.commit()
        return {"status": "success", "message": f"Friendly name for {entity_type.value} updated to '{friendly_name}'"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating friendly name: {str(e)}")


def update_institution_id_pattern(
    entity_type: enums.EntityTypeReduced,
    pattern: str,
    db: Session = Depends(get_db),
):
    """
    Update the pattern for generating corporate IDs for compounds or batches.
    """

    EXPECTED_PATTERN = r"^.{0,10}\{\:0?[1-9]d\}.{0,10}$"
    import re

    if not pattern or not re.match(EXPECTED_PATTERN, pattern):
        raise HTTPException(
            status_code=400,
            detail="""Invalid pattern format.
                    The pattern must contain '{:d}'.
                    You can also use '{:0Nd}' for zero-padded numbers (numbers will be padded with zeros to N digits).,
                    Pattern can also have prefix and postfix, meant for identification of institution.
                    Example: 'DG-{:05d}' for ids in format 'DG-00001', 'DG-00002' etc.""",
        )

    property_name = "corporate_batch_id" if entity_type == enums.EntityTypeReduced.BATCH else "corporate_compound_id"
    setting_name = (
        "corporate_batch_id_pattern"
        if entity_type == enums.EntityTypeReduced.BATCH
        else "corporate_compound_id_pattern"
    )

    try:
        db.execute(
            text("UPDATE moltrack.properties SET pattern = :pattern WHERE name = :property"),
            {"property": property_name, "pattern": pattern},
        )

        db.execute(
            text("UPDATE moltrack.settings SET value = :pattern WHERE name = :setting"),
            {"setting": setting_name, "pattern": pattern},
        )
        db.commit()
        return {
            "status": "success",
            "message": f"Corporate ID pattern for {entity_type.value} updated to {pattern}, ids will be looking like {pattern.format(1)}",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating corporate ID pattern: {str(e)}")


def set_molregno_sequence_start(start_value: int, db: Session = Depends(get_db)):
    return seq_start_update(start_value, "moltrack.molregno_seq", db)


def set_batchregno_sequence_start(start_value: int, db: Session = Depends(get_db)):
    return seq_start_update(start_value, "moltrack.batch_regno_seq", db)


def seq_start_update(start_value: int, seq_name, db: Session):
    """
    Set the starting value for the sequence.
    """
    if start_value < 1:
        raise HTTPException(status_code=400, detail="Start value must be greater than 0")

    max_batchregno = db.execute(text(f"SELECT last_value FROM {seq_name}")).scalar_one()

    if start_value <= max_batchregno:
        raise HTTPException(
            status_code=400,
            detail=f"Start value {start_value} must be greater than the current max {seq_name} {max_batchregno}",
        )

    try:
        setting_name = "compound_sequence_start" if "molregno" in seq_name else "batch_sequence_start"
        db.execute(
            text("UPDATE moltrack.settings SET value = :start_value WHERE name = :setting_name"),
            {"start_value": str(start_value), "setting_name": setting_name},
        )
        db.execute(text("SELECT setval(:seq_name, :start_value)"), {"seq_name": seq_name, "start_value": start_value})
        db.commit()
        return {"status": "success", "message": f"The {seq_name} set to {start_value}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error setting {seq_name}: {str(e)}")


# === Search endpoints ===
# TODO: Maybe we should move this to a separate module?
def advanced_search(request: models.SearchRequest, db: Session = Depends(get_db)):
    """
    Advanced multi-level search endpoint supporting compounds, batches, and assay_results.
    """
    try:
        engine = SearchEngine(db)
        return engine.search(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search/compounds")
def search_compounds_advanced(
    output: List[str] = Body(...),
    aggregations: Optional[List[models.Aggregation]] = Body([]),
    filter: Optional[models.Filter] = Body(None),
    output_format: enums.SearchOutputFormat = Body(enums.SearchOutputFormat.json),
    limit: Optional[int] = Body(None),
    db: Session = Depends(get_db),
):
    """
    Endpoint for compound-level searches.

    Automatically sets level to 'compounds' and accepts filter parameters directly.
    """
    request = models.SearchRequest(
        level=enums.SearchEntityType.COMPOUNDS.value,
        output=output,
        filter=filter,
        output_format=output_format,
        aggregations=aggregations,
        limit=limit,
    )
    return advanced_search(request, db)


@router.post("/search/batches")
def search_batches_advanced(
    output: List[str] = Body(...),
    aggregations: Optional[List[models.Aggregation]] = Body([]),
    filter: Optional[models.Filter] = Body(None),
    output_format: enums.SearchOutputFormat = Body(enums.SearchOutputFormat.json),
    limit: Optional[int] = Body(None),
    db: Session = Depends(get_db),
):
    """
    Endpoint for batch-level searches.

    Automatically sets level to 'batches' and accepts filter parameters directly.
    """
    request = models.SearchRequest(
        level=enums.SearchEntityType.BATCHES.value,
        output=output,
        filter=filter,
        output_format=output_format,
        aggregations=aggregations,
        limit=limit,
    )
    return advanced_search(request, db)


@router.post("/search/assay-results")
def search_assay_results_advanced(
    output: List[str] = Body(...),
    aggregations: Optional[List[models.Aggregation]] = Body([]),
    filter: Optional[models.Filter] = Body(None),
    output_format: enums.SearchOutputFormat = Body(enums.SearchOutputFormat.json),
    limit: Optional[int] = Body(None),
    db: Session = Depends(get_db),
):
    """
    Endpoint for assay result-level searches.

    Automatically sets level to 'assay_results' and accepts filter parameters directly.
    """
    request = models.SearchRequest(
        level=enums.SearchEntityType.ASSAY_RESULTS.value,
        output=output,
        filter=filter,
        output_format=output_format,
        aggregations=aggregations,
        limit=limit,
    )
    return advanced_search(request, db)


@router.post("/search/assays")
def search_assays_advanced(
    output: List[str] = Body(...),
    aggregations: Optional[List[models.Aggregation]] = Body([]),
    filter: Optional[models.Filter] = Body(None),
    output_format: enums.SearchOutputFormat = Body(enums.SearchOutputFormat.json),
    limit: Optional[int] = Body(None),
    db: Session = Depends(get_db),
):
    """
    Endpoint for assay-level searches.

    Automatically sets level to 'assays' and accepts filter parameters directly.
    """
    request = models.SearchRequest(
        level=enums.SearchEntityType.ASSAYS.value,
        output=output,
        filter=filter,
        output_format=output_format,
        aggregations=aggregations,
        limit=limit,
    )
    return advanced_search(request, db)


@router.post("/search/assay-runs")
def search_assay_runs_advanced(
    output: List[str] = Body(...),
    aggregations: Optional[List[models.Aggregation]] = Body([]),
    filter: Optional[models.Filter] = Body(None),
    output_format: enums.SearchOutputFormat = Body(enums.SearchOutputFormat.json),
    limit: Optional[int] = Body(None),
    db: Session = Depends(get_db),
):
    """
    Endpoint for assay run-level searches.

    Automatically sets level to 'assay_runs' and accepts filter parameters directly.
    """
    request = models.SearchRequest(
        level=enums.SearchEntityType.ASSAY_RUNS.value,
        output=output,
        filter=filter,
        output_format=output_format,
        aggregations=aggregations,
        limit=limit,
    )
    return advanced_search(request, db)


@router.post("/search/generate-filter")
def generate_search_filter(expression: str, db: Session = Depends(get_db)):
    try:
        builder = SearchFilterBuilder(db)
        filter = builder.build_filter(expression)

        return filter
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


app.include_router(router)

def main():
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
