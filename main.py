import json
import uuid
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED

import config
from connections.extensions import db
from models.answer import Answer
from models.question import Question
from models.token import Token
from models.user import User, UserInDB
from util import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    get_user,
)

app = FastAPI(debug=True)


@app.post("/api/login/access-token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/profile")
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/api/profile/upload")
async def upload_profile(req: Request):
    raw_body = await req.body()
    user_body = raw_body.decode()
    user = json.loads(user_body)
    db["user"].update_one(
        {"_id.username": user["username"]},
        {"$set": {"sex": user["sex"], "age": user["age"], "phone": user["phone"]}},
    )
    return get_user(user["username"])


@app.get("/api/hello")
def hello():
    return {"message": ""}


@app.post("/api/register")
async def register_user(req: Request):
    raw_body = await req.body()
    user_body = raw_body.decode()
    new_user = UserInDB(**json.loads(user_body))

    new_user.hashed_password = get_password_hash(new_user.password)

    db["user"].insert_one({"_id": {"username": new_user.username}, **new_user.__dict__})

    return "SUCCESS"


@app.get("/api/questions")
async def get_questions():
    questiones = db["questions"].find({})

    questionList = [
        {"qId": i["qId"], "title": i["title"], "description": i["description"]}
        for i in questiones
    ]
    return questionList


@app.get("/api/questions/{qId}")
async def get_question(qId: str):
    question = db["questions"].find_one({"_id.qid": qId})

    if not question:
        return None
    else:
        return {
            "qId": question["qId"],
            "title": question["title"],
            "description": question["description"],
        }


@app.get("/api/questions/{qId}/answers")
async def get_answers(qId: str):
    question = db["questions"].find_one({"_id.qid": qId})

    if not question:
        return None
    return question["answerList"]


@app.get("/api/questions/{qId}/answers/{aId}")
async def get_answer(qId: str, aId: str):
    question = db["questions"].find_one({"_id.qid": qId})

    if not question:
        return None

    for answer in question["answerList"]:
        if answer["aId"] == aId:
            return answer
        else:
            return None


@app.post("/api/questions/add")
async def addQuestion(req: Request):  # type: ignore
    raw_body = await req.body()
    question_body = raw_body.decode()
    question = Question(**json.loads(question_body))
    question.qId = str(uuid.uuid1())
    data = question.__dict__
    data["author"] = question.author.__dict__
    db["questions"].insert_one({"_id": {"qid": question.qId}, **data})
    return True


@app.post("/api/questions/{qId}/answers/add")
async def addQuestion(qId: str, req: Request):
    raw_body = await req.body()
    answer_body = raw_body.decode()
    answer = Answer(**json.loads(answer_body))
    answer.aId = str(uuid.uuid1())
    data = answer.__dict__
    data["author"] = answer.author.__dict__
    db["questions"].update_one({"_id.qid": qId}, {"$push": {"answerList": data}})
    return True


@app.post("/api/search")
async def search(req: Request):
    raw_body = await req.body()
    search_body = raw_body.decode()
    query = json.loads(search_body)["query"]
    questiones = db["questions"].find(
        {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"author.username": {"$regex": query, "$options": "i"}},
            ]
        }
    )
    questionList = [
        {"qId": i["qId"], "title": i["title"], "description": i["description"]}
        for i in questiones
    ]
    return questionList
