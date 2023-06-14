from database.database import engine, get_db
from models.models import Base, Task, User
from schemas import schemas
from services import services
from sqlalchemy.orm import Session

from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/", response_model=list[schemas.UserSchema], status_code=status.HTTP_200_OK)
def read_users(session: Session = Depends(get_db)):
    users = services.get_users(session)

    return users


@app.post(
    "/signup", response_model=schemas.UserSchema, status_code=status.HTTP_201_CREATED
)
def signup(payload: schemas.UserCreate = Body(), session: Session = Depends(get_db)):
    existing_user = session.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = services.get_password_hash(payload.password)
    user = User(username=payload.username, hashed_password=hashed_password)
    return services.create_user(session, user=user)


@app.post("/login", response_model=schemas.Token, status_code=status.HTTP_202_ACCEPTED)
def login(
    payload: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)
):
    user = services.authenticate_user(payload.username, payload.password, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = services.create_access_token(
        data={"sub": user.username}, expires_delta=services.access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(oauth2_scheme)):
    services.revoked_tokens.add(token)
    return {"Success": "Logged out successfully"}


# CRUD


@app.get(
    "/user/task",
    response_model=list[schemas.TaskSchema],
    status_code=status.HTTP_200_OK,
)
def get_user_tasks(
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task = session.query(Task).filter(Task.owner_id == current_user.id).all()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User Unauthorized"
        )

    return task


@app.get(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
    status_code=status.HTTP_200_OK,
)
def get_user_task_by_ID(
    task_id: int,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task = (
        session.query(Task)
        .filter(Task.owner_id == current_user.id, Task.id == task_id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User Unauthorized or Task does not exist",
        )

    return task


@app.post(
    "/user/task", response_model=schemas.TaskSchema, status_code=status.HTTP_201_CREATED
)
def create_task_for_user(
    task: schemas.TaskCreate,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    db_task = Task(
        task=task.task, description=task.description, owner_id=current_user.id
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.put(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_task(
    task_id: int,
    task: schemas.TaskBase,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task_to_update = (
        session.query(Task)
        .filter(Task.owner_id == current_user.id, Task.id == task_id)
        .first()
    )

    if not task_to_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User Unauthorized or Task does not exist",
        )

    task_to_update.task = task.task
    task_to_update.description = task.description

    session.commit()
    return task_to_update


@app.post(
    "/user/task/{task_id}",
    response_model=schemas.TaskSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def mark_as_complete(
    task_id: int,
    task: schemas.TaskComplete,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task_to_update = (
        session.query(Task)
        .filter(Task.owner_id == current_user.id, Task.id == task_id)
        .first()
    )

    if not task_to_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User Unauthorized or Task does not exist",
        )

    task_to_update.is_complete = task.is_complete

    session.commit()
    return task_to_update


@app.delete("/user/task/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    current_user: User = Depends(services.get_current_active_user),
    session: Session = Depends(get_db),
):
    task = (
        session.query(Task)
        .filter(Task.owner_id == current_user.id, Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User Unauthorized or Task ID does not exist",
        )

    session.delete(task)
    session.commit()
    session.close()
    return {"Success": "Task deleted!"}
