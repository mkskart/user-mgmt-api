"""CRUD helpers with sane primary‑key handling (no ID reuse)."""
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from loguru import logger

from backend.app import models, schemas


# ──────────────────────────
# Query helpers
# ──────────────────────────
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    logger.info(f"Pulling user information with id --> {user_id}")
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    logger.info(f"email lookup → {email!r}")
    return (
        db.query(models.User)
        .filter(models.User.email.ilike(email.strip()))   # ← ilike = case‑insensitive
        .first()
    )


def get_users_by_name(db: Session, name: str) -> List[models.User]:
    pattern = f"%{name}%"
    logger.info(f"Pulling user information with name lookup --> {name}")
    return (
        db.query(models.User)
        .filter(models.User.name.ilike(pattern))
        .order_by(models.User.id)
        .all()
    )


def list_users(db: Session) -> List[models.User]:
    logger.info("Pulling user list")
    return db.query(models.User).order_by(models.User.id).all()


# ──────────────────────────
# Mutations
# ──────────────────────────
def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    if get_user_by_email(db, payload.email):
        logger.error(f"{payload.email} already in use")
        raise ValueError("User with that email already exists")

    user = models.User(name=payload.name, email=payload.email)
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        logger.error(f"Integrity error creating user: {exc}")
        raise

    db.refresh(user)
    logger.success(f"User {user.email} created (id={user.id})")
    return user


def update_user(db: Session, user_id: int, payload: schemas.UserUpdate) -> models.User:
    user = get_user(db, user_id)
    if not user:
        logger.error(f"User {user_id} not found")
        raise LookupError("User not found")

    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        if get_user_by_email(db, payload.email) and payload.email != user.email:
            logger.error(f"User {payload.email} already in use; cannot update")
            raise ValueError("Email already in use")
        user.email = payload.email

    db.commit()
    db.refresh(user)
    logger.info(f"User id={user.id} updated")
    return user


def delete_user(db: Session, user_id: int) -> None:
    """Delete a user; keep remaining IDs untouched."""
    user = get_user(db, user_id)
    if not user:
        logger.error(f"User {user_id} not found")
        raise LookupError("User not found")

    db.delete(user)
    db.commit()
    logger.warning(f"User id={user_id} deleted")

    _reset_pk_sequence(db)


# ──────────────────────────
# Internal helper
# ──────────────────────────
def _reset_pk_sequence(db: Session) -> None:
    """
    Sync users_id_seq with MAX(id) so the next insert is correct.
    Existing rows keep their IDs.
    """
    db.execute(
        text(
            "SELECT setval("
            " pg_get_serial_sequence('users','id'), "
            " COALESCE((SELECT MAX(id) FROM users), 1)"
            ")"
        )
    )
    db.commit()
    logger.debug("PK sequence aligned with MAX(id)")