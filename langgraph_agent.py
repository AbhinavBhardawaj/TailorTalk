from typing import Optional, TypedDict
import os, dateparser
#from openai import OpenAI
from dotenv import load_dotenv
from datetime import timedelta,datetime
from calendar_utils import calendar_check_availability as cal_check, book_event as calendar_book
from langgraph.graph import StateGraph, END
#from langchain_community.llms import Ollama
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

load_dotenv()
#client = OpenAI()
class BookingState(TypedDict, total = False):
    input: str # users message
    intent: str # check availability or book the event
    datetime_start: Optional[str] # iso datetime string
    datetime_end: Optional[str]
    is_available: Optional[bool] # result-> availability check
    booking_confirmed: Optional[bool] # whether the user said yes to book
    booking_link: Optional[str] #link of booked event
    reply: Optional[str] # message to user

#openai.api_key = os.getenv("OPENAI_API_KEY")
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def parse_intent(state: dict)->dict:
    user_input = state.get("input","")

    prompt = (
        "You are an intent classifier for a calendar booking assistant.\n"
        "Classify the user's intent as one of the following:\n"
        "- check_availability\n"
        "- book_meeting\n"
        "- cancel_meeting\n"
        "Respond only with the intent label.\n"
        f"User: {user_input}\n"
        "Intent:"
    )

    # response = client.chat.completions.create(
    #     model = 'gpt-3.5-turbo',
    #     messages = [
    #         {"role":"system", "content": system_prompt},
    #         {"role":"user", "content": user_input},
    #     ]
    # )

    intent = llm.invoke(prompt).strip().split("\n")[0]

    return {"intent": intent}

def extract_time_info(state:dict)->dict:
    user_input = state.get("input","")

    start_time = dateparser.parse(user_input) # parses natural language time to datetime

    if not start_time:
        return {'reply': '<> Sorry, I could not understand the time. Can u rephrase?'}

    end_time = start_time + timedelta(hours = 1)

    return {
        'datetime_start': start_time.isoformat(),
        'datetime_end': end_time.isoformat(),
    }
    
def check_availability_node(state:dict)->dict:
    start = state.get('datetime_start')
    end = state.get('datetime_end')
    
    if not start or not end:
        return {"reply":'I am unable to find a valid time. Can you try again?'}
    
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)

    available = cal_check(start_dt, end_dt)

    return {
        'is_available': available,
        'reply': f'The time {start} to {end} is avaialable' if available else f'This slot {start} to {end} is already book. Try Another slot!!'
    }

def book_event_node(state:dict)->dict:
    confirmed = state.get("booking_confirmed",False)
    start = state.get('datetime_start')
    end = state.get('datetime_end')

    if not confirmed:
        return {"reply":"Booking was not confirmed. Let me know if you would like to try again."}

    if not start or not end:
            return {"reply":"Missing time information. Try Again!"}
    
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)

    link = calendar_book("TailorTalk booking",start_dt,end_dt)

    return {
        'booking_link':link,
        'reply': f'Your Event is booked, You can view it here:{link}'
    }

def confirm_booking_node(state:dict)->dict:
    if state.get('booking_confirmed') is True:
        return {'reply':'Booking Confirmed. Proceeding to book the meeting'}
    
    return{
        'reply':'Would you like me to book this meeting now? Please reply yes or no.'
    }

builder = StateGraph(BookingState)

builder.add_node("parse_intent",parse_intent)
builder.add_node("extract_time_info",extract_time_info)
builder.add_node("check_availability",check_availability_node)
builder.add_node("confirm_booking",confirm_booking_node)
builder.add_node("book_event",book_event_node)

builder.set_entry_point("parse_intent")
builder.add_edge("parse_intent","extract_time_info")
builder.add_edge("extract_time_info","check_availability")
builder.add_edge("check_availability","confirm_booking")
builder.add_edge("confirm_booking","book_event")

builder.add_edge("book_event", END)

graph = builder.compile()

def run_agent(user_input: str, state_overrides = None):
    state = {"input": user_input}
    if state_overrides:
        state.update(state_overrides)
    result = graph.invoke(state)
    return result


