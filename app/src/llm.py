from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GEMINI
from app.src.prompt import sys_prompt
from langchain.prompts import PromptTemplate
import os 


llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  
            google_api_key= GEMINI, 
            temperature=0.2 
        )


def generate_interview_questions(role: str):
    user_role = role
    sys_prompt =f"""
    You are a highly skilled and experienced interviewer conducting a mock interview for the position of {user_role}. Your goal is to assess the candidate's technical knowledge, problem-solving abilities, and communication skills."""
    
    prompt_template = PromptTemplate(
        input_variables=["role"],
        template=sys_prompt + prompt
    )
    
    formatted_prompt = prompt_template.format(role=user_role)
    
    response = llm(formatted_prompt)
    return response
