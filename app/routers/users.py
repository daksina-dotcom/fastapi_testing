from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud
from typing import List
from ..utils import create_token
from ..auth import get_current_user,require_rank

router = APIRouter(prefix="/soldiers")


@router.get("/", response_model=List[schemas.SoldierOut])
def get_all_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Lieutenant", "Major", "Colonel"]))):
    return crud.get_all(db)


@router.post("/bulk-create", response_model=List[schemas.SoldierOut])
def create_soldiers_info(
    soldiers: List[schemas.SoldierCreate], db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Major", "Colonel"]))
):
    db_soldier = crud.bulk_create(db, soldiers)
    if not db_soldier:
        raise HTTPException(status_code=409,detail="Email already registered")
    return db_soldier


@router.patch("/bulk-promote", response_model=dict)
def promote_soldiers_info(promote: schemas.BulkPromote, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Major", "Colonel"]))):
    db_update = crud.bulk_promote(db, promote.soldier_ids, promote.new_rank)
    if db_update == "not_found":
        raise HTTPException(
            status_code=404,
            detail="One or more soldiers data not found,promotion failed",
        )
    if db_update == "already_updated":
        raise HTTPException(
            status_code=409,
            detail=" One or more soldiers already updated to the specified rank",
        )
    return db_update


@router.delete("/bulk-delete")
def delete_soldiers_info(remove: schemas.BulkDelete, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Colonel"]))):
    db_delete = crud.bulk_delete(db, remove.soldier_ids)
    if not db_delete:
        raise HTTPException(
            status_code=404,
            detail="One or more soldiers data not found,deletion failed",
        )
    return db_delete


@router.post("/login", response_model=schemas.Token)
def authenticate(login: schemas.SoldierLogin, db: Session = Depends(get_db)):
    db_auth = crud.authenticate_soldier(db, login.email_id, login.password)
    if not db_auth:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    access_token = create_token(data={"sub": db_auth.soldier_id, "rank": db_auth.rank})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/{soldier_id}", response_model=schemas.SoldierOut)
def get_soldier_info(soldier_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Lieutenant", "Major", "Colonel"]))):
    db_soldier = crud.get_soldier(db, soldier_id)
    if not db_soldier:
        raise HTTPException(status_code=404, detail="Soldier Not Found")
    return db_soldier


@router.post("/", response_model=schemas.SoldierCreateResponse)
def create_soldier_info(
    soldier_dict: schemas.SoldierCreate, db: Session = Depends(get_db)):
    db_soldier = crud.create_soldier(db, soldier_dict)
    if not db_soldier:
        raise HTTPException(status_code=409,detail="Email already registered")
    return db_soldier


@router.patch("/{soldier_id}", response_model=schemas.SoldierOut)
def update_soldier_info(
    soldier_id: int, updated: schemas.SoldierUpdate, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)
    ,user = Depends(require_rank(["Major", "Colonel"]))
):
    db_update = crud.update_soldier(db, soldier_id, updated)
    if not db_update:
        raise HTTPException(status_code=404, detail="Soldier Not Found")
    if updated.rank is not None and user.get("rank") == "Major":
        raise HTTPException(
            status_code=403, 
            detail="Majors cannot change soldier ranks."
        )
    return db_update


@router.delete("/{soldier_id}")
def delete_soldier_info(soldier_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Colonel"]))):
    db_delete = crud.delete_soldier(db, soldier_id)
    if not db_delete:
        raise HTTPException(status_code=404, detail="Soldier Not Found")
    return db_delete


@router.post("/{soldier_id}/vacation", response_model=schemas.VacationOut)
def create_vacation(
    soldier_id: int, vacation: schemas.VacationCreate, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Major", "Colonel"]))
):
    db_vacation = crud.create_vacation(db, vacation, soldier_id)
    if not db_vacation:
        raise HTTPException(
            status_code=400, detail="Soldier not found or eligible for Vacation"
        )
    return db_vacation


@router.delete("/{soldier_id}/vacation")
def delete_vacation(soldier_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Colonel"]))):
    db_vacation = crud.delete_vacation(db, soldier_id)
    if not db_vacation:
        raise HTTPException(status_code=400, detail="No Vacation Data Found")
    return db_vacation


@router.post("/{soldier_id}/veteran", response_model=schemas.VeteranOut)
def retire_soldier(
    soldier_id: int, veteran: schemas.VeteranCreate, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user),user = Depends(require_rank(["Colonel"]))
):
    db_veteran = crud.retire_soldier(db, veteran, soldier_id)
    if not db_veteran:
        raise HTTPException(
            status_code=400, detail="Soldier already retired or discharged"
        )
    return db_veteran
