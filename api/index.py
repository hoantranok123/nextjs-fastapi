from typing import Union

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from starlette.background import BackgroundTask
import logging
import sys
app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")


@app.get("/api/healthchecker")
def healthchecker():
  return {"status": "success", "message": "Integrate FastAPI Framework with Next.js"}

origins = [
  "https://nextjs-fastapi-fawn.vercel.app",
  "http://localhost:8080"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def log_info(req_body, res_body):
  logging.info(req_body)
  logging.info(res_body)


@app.middleware('http')
async def some_middleware(request: Request, call_next):
  req_body = await request.body()
  response = await call_next(request)
  
  res_body = b''
  async for chunk in response.body_iterator:
    res_body += chunk
  
  task = BackgroundTask(log_info, req_body, res_body)
  return Response(content=res_body, status_code=response.status_code, 
    headers=dict(response.headers), media_type=response.media_type, background=task)


class TodoCreate(BaseModel):
  title: str


class TodoUpdate(BaseModel):
  title: Union[str, None] = None
  completed: Union[bool, None] = None


class TodoItem(BaseModel):
  id: int
  title: str
  completed: bool

# In-memory storage for todo items
todos = []

# Route to create a new todo item
@app.post("/api/todos")
def create_todo_item(todo: TodoCreate):
  new_todo = TodoItem(id=len(todos) + 1, title=todo.title, completed=False)
  todos.append(new_todo)
  return new_todo

# Route to get all todo items
@app.get("/api/todos")
def get_all_todo_items():
  return todos

# Route to get a specific todo item by ID
@app.get("/api/todos/{todo_id}")
def get_todo_item(todo_id: int):
  for todo in todos:
    if todo.id == todo_id:
      return todo
  return {"error": "Todo item not found"}

# Route to update a specific todo item by ID
@app.patch("/api/todos/{todo_id}")
def update_todo_item(todo_id: int, todo: TodoUpdate):
  for todo_item in todos:
    if todo_item.id == todo_id:
      todo_item.title = todo.title if todo.title is not None else todo_item.title
      todo_item.completed = todo.completed if todo.completed is not None else todo_item.completed
      return todo_item
  return {"error": "Todo item not found"}

# Route to delete a specific todo item by ID
@app.delete("/api/todos/{todo_id}")
def delete_todo_item(todo_id: int):
  for i, todo_item in enumerate(todos):
    if todo_item.id == todo_id:
      del todos[i]
      return {"message": "Todo item deleted"}
  return {"error": "Todo item not found"}
