from sentence_transformers import SentenceTransformer, util
from openai import Client
# from google.colab import userdata
import os
# from openai import OpenAI
import google.generativeai as genai
import requests
from youtube_transcript_api import YouTubeTranscriptApi

def get_contexts(question:str,contexts:dict):
    responses = {}
    # os.environ["OPEN_API_KEY"] = "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"
    # client = OpenAI(
    #       api_key=os.getenv("OPEN_API_KEY"),
    #       base_url="https://openrouter.ai/api/v1"
    #   # default_headers={
    #   #     "HTTP-Referer": "http://localhost",     # Optional but good practice
    #   #     "X-Title": "MyBrowserExtension"         # Optional
    #   # }
    # )
    API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key = API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    for tag,context in contexts.items():
      prompt = f"""You are a helpful Browser assistant who is answering user's questions.

      User Question: {question}
      Context from source {tag}: {context}
   
      Instructions:
      Answer the given Question only from the given Context.
      Do not make up anything. If you cannot answer, mention that the answer is not present in the context.


      """
      response = model.generate_content(prompt)
      responses[tag] = response.text.strip()
    return responses

  # except Exception as e:
  #   import traceback
  #   responses[tag] = f"[EXCEPTION] {str(e)}\nTraceback:\n{traceback.format_exc()}"

def onlineSearch(question:str):
  payload = {
        "api_key": "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",
        "query": question,
        "num_results": 3  # adjust how many results you want
    }
  response = requests.post(url = "https://api.tavily.com/search",
  headers = {"Content-Type": "application/json"},
  json = payload)
  # print(response.json())
  return response.json().get('results')[0]['content']

def get_youtube_content(videoId: str):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(videoId)
        texts = " ".join(text.text for text in transcript)
        return texts
    except Exception as e:
        return f"Transcript Not Available ({str(e)})"
    
  
      
