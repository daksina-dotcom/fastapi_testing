from sqlalchemy.orm import Session
from . import models, schemas
from .utils import hash_password, verify_password
from typing import List


def authenticate_soldier(db: Session, email_id: str, password: str):
    db_auth = (
        db.query(models.Soldier).filter(models.Soldier.email_id == email_id).first()
    )
    if not db_auth:
        return False
    if not verify_password(password, db_auth.secret_password):
        return False
    return db_auth


def create_soldier(db: Session, soldier_dict: schemas.SoldierCreate):
    existing = db.query(models.Soldier).filter(models.Soldier.email_id == soldier_dict.email_id).first()
    if existing:
        return None
    hashed = hash_password(soldier_dict.secret_password)
    db_soldier = models.Soldier(
        **soldier_dict.model_dump(exclude={"secret_password"}), secret_password=hashed
    )
    db.add(db_soldier)
    db.commit()
    db.refresh(db_soldier)
    return {"result": "Success","data": db_soldier}


def get_soldier(db: Session, soldier_id: int):
    db_soldier = db.query(models.Soldier).filter(models.Soldier.soldier_id == soldier_id).first()
    if db_soldier:
        return db_soldier
    return None


def update_soldier(db: Session, soldier_id: int, updated: schemas.SoldierUpdate):
    db_soldier = get_soldier(db, soldier_id)
    if not db_soldier:
        raise HTTPException(status=422,detail="Required field not given correctly")
    if updated.status == "Active":
        db.query(models.Vacation).filter(models.Vacation.soldier_id == soldier_id).delete()
    for key, val in updated.model_dump(exclude_unset=True).items():
        setattr(db_soldier, key, val)
    db.commit()
    db.refresh(db_soldier)
    return db_soldier


def delete_soldier(db: Session, soldier_id: int):
    db_soldier = get_soldier(db, soldier_id)
    if db_soldier:
        db.delete(db_soldier)
        db.commit()
        return {"result": "Successfully deleted soldier data"}
    return None


def bulk_create(db: Session, soldiers: List[schemas.SoldierCreate]):
    db_soldiers = []
    for soldier in soldiers:
        existing = db.query(models.Soldier).filter(models.Soldier.email_id == soldier.email_id).first()
        if existing:
            return None
        hashed = hash_password(soldier.secret_password)
        db_soldier = models.Soldier(
            **soldier.model_dump(exclude={"secret_password"}), secret_password=hashed
        )
        db_soldiers.append(db_soldier)
    db.add_all(db_soldiers)
    db.commit()
    return db_soldiers


def get_all(db: Session):
    return db.query(models.Soldier).all()


def bulk_promote(db: Session, soldier_ids: List[int], new_rank: str):
    q = db.query(models.Soldier).filter(models.Soldier.soldier_id.in_(soldier_ids))
    total_count = q.count()
    if total_count == 0:
        return "not_found"
    count = (q.filter(models.Soldier.rank != new_rank)).count()
    if count == 0:
        return "already_updated"
    q.update({"rank": new_rank}, synchronize_session=False)
    db.commit()
    return {
        "result": f"Successfully updated soldier data, ids: {soldier_ids}"
    }


def bulk_delete(db: Session, soldier_ids: List[int]):
    q = db.query(models.Soldier).filter(models.Soldier.soldier_id.in_(soldier_ids))
    delete_count = q.delete(synchronize_session=False)
    if delete_count == 0:
        return None
    db.commit()
    return {"result": f"Successfully deleted {delete_count} rows of soldier data"}


def create_vacation(db: Session, vacation: schemas.VacationCreate, soldier_id: int):
    db_soldier = (
        db.query(models.Soldier).filter(models.Soldier.soldier_id == soldier_id).first()
    )
    if not db_soldier or db_soldier.status != "Active":
        return None
    db_vacation = models.Vacation(**vacation.model_dump(), soldier_id=soldier_id)
    db_soldier.status = "Inactive"
    db.add(db_vacation)
    db.commit()
    return db_vacation


def delete_vacation(db: Session, soldier_id: int):
    db_vacation = (
        db.query(models.Vacation)
        .filter(models.Vacation.soldier_id == soldier_id)
        .first()
    )
    db_soldier = (
        db.query(models.Soldier).filter(models.Soldier.soldier_id == soldier_id).first()
    )
    if not db_vacation:
        return None
    db.delete(db_vacation)
    db_soldier.status = "Active"
    db.commit()
    return {"result": f"Vacation removed successfully for Soldier Id: {soldier_id}"}


def retire_soldier(db: Session, veteran: schemas.VeteranCreate, soldier_id: int):
    db_soldier = (
        db.query(models.Soldier).filter(models.Soldier.soldier_id == soldier_id).first()
    )
    if not db_soldier or db_soldier.status in ["Retired", "Discharged"]:
        return None
    if db_soldier.vacation_record:
        db.delete(db_soldier.vacation_record)
    db_soldier.status = "Retired"
    db_veteran = models.Veteran(
        soldier_id=db_soldier.soldier_id, **veteran.model_dump()
    )
    db.add(db_veteran)
    db.commit()
    db.refresh(db_veteran)
    return db_veteran
