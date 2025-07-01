from fastapi import FastAPI
#from fastapi.params import Body
from pydantic import BaseModel
from langgraph_agent import run_agent
import uvicorn

app = FastAPI()

class ChatRequest(BaseModel):
    message:str

@app.post("/chat")
def chat(request: ChatRequest):
    user_input = request.message
    result = run_agent(user_input)
    return {"reply":result.get("reply")}

    
