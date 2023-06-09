from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    disabled: bool = False
    photo: str = ""
    sex: str = ""
    age: int = 0
    phone: str = ""


class UserInDB(User):
    hashed_password: str = None
