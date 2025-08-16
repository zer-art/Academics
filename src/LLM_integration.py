import os
import json
import time
from datetime import datetime
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

class InterviewConductor:    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI')
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.interview_data = {
            'job_title': '',
            'candidate_name': '',
            'questions': [],
            'responses': [],
            'scores': [],
            'feedback': [],
            'start_time': '',
            'end_time': '',
            'overall_score': 0
        }

        
    
