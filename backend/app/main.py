"""Flask application entry‑point."""
from flask import Flask, jsonify, request, abort
from sqlalchemy.orm import Session

from backend.app.logger import logger  # noqa: F401 ensures logger config early
from backend.app.database import get_db
from backend.app import crud, schemas
from backend.app.auth import login_handler, require_auth
from backend.app import init_app as init_db_app

app = Flask(__name__)
init_db_app()  # Create tables at container start


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


# ---- Auth ----
@app.route("/login", methods=["POST"])
def login():
    return jsonify(login_handler())


# ---- Users CRUD ----
@app.route("/users", methods=["POST"])
@require_auth
def create_user():
    with next(get_db()) as db:  # type: Session
        payload = schemas.UserCreate(**request.get_json())
        try:
            user = crud.create_user(db, payload)
            return jsonify(schemas.UserOut.from_orm(user).dict()), 201
        except ValueError as ve:
            abort(400, description=str(ve))


@app.route("/users", methods=["GET"])
@require_auth
def list_users():
    with next(get_db()) as db:
        users = crud.list_users(db)
        return jsonify([schemas.UserOut.from_orm(u).dict() for u in users])

@app.route("/users/name/<string:name>", methods=["GET"])
@require_auth
def get_users_by_name(name: str):
    with next(get_db()) as db:
        users = crud.get_users_by_name(db, name)
        if not users:
            logger.error(f"User(s) with name {name} not found")
            abort(404, description=f"User(s) with name {name} not found")
        return jsonify([schemas.UserOut.from_orm(u).dict() for u in users])


@app.route("/users/<int:user_id>", methods=["GET"])
@require_auth
def get_user(user_id: int):
    with next(get_db()) as db:
        user = crud.get_user(db, user_id)
        if not user:
            logger.error(f"User with id {user_id} not found")
            abort(404, description=f"User with id {user_id} not found")
        return jsonify(schemas.UserOut.from_orm(user).dict())

@app.route("/users/email/<string:email>", methods=["GET"])
@require_auth
def get_user_by_email(email: str):
    with next(get_db()) as db:
        user = crud.get_user_by_email(db, email)
        if not user:
            logger.error("User with email --> {0} not found".format(email))
            abort(404, description="User with email {0} not found".format(email))
        return jsonify(schemas.UserOut.from_orm(user).dict())


@app.route("/users/<int:user_id>", methods=["PUT"])
@require_auth
def update_user(user_id: int):
    with next(get_db()) as db:
        payload = schemas.UserUpdate(**request.get_json())
        try:
            user = crud.update_user(db, user_id, payload)
            return jsonify(schemas.UserOut.from_orm(user).dict())
        except (LookupError, ValueError) as exc:
            abort(404 if isinstance(exc, LookupError) else 400, description=str(exc))


@app.route("/users/<int:user_id>", methods=["DELETE"])
@require_auth
def delete_user(user_id: int):
    with next(get_db()) as db:
        try:
            crud.delete_user(db, user_id)
            return {"response" : f"User with id {user_id} deleted"}
        except LookupError as exc:
            abort(404, description=str(exc))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
    
