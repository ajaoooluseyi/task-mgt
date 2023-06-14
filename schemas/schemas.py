from pydantic import BaseModel


class TaskBase(BaseModel):
    task: str
    description: str = None


class TaskCreate(TaskBase):
    pass



class TaskComplete(BaseModel):
    is_complete: bool


class TaskSchema(TaskBase):
    id: int
    task: str
    description: str = None
    is_complete: bool
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserSchema(UserBase):
    id: int
    is_active: bool
    tasks: list[TaskSchema]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None
