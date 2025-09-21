from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
from openai import Client, chat
from google.colab import userdata
import os
from openai import OpenAI
from Filtering import get_contexts, onlineSearch, get_youtube_content
from fastapi import File, UploadFile
from PyPDF2 import PdfReader
import io
from fastapi import Form
import traceback
from fastapi.responses import JSONResponse
import google.generativeai as genai
import re


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials = False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_question(question: str = Form(...),
   page_content: str = Form(None),
   youtube_video: str = Form(None),
   uploaded_doc: UploadFile = File(None),
   search_box: bool = Form(False),
   chat_history: str = Form(None)
):
  try:

    chunks = {}
    if(youtube_video):
      videoId_match = re.search(r"v=[A-Za-z0-9_-]{11}",youtube_video)
      videoId = str(videoId_match.group(0)[2:])
      chunks['Youtube Video Content'] = get_youtube_content(videoId)
    if(page_content):
      chunks['Page content'] = page_content
    # if(request.memory_content):
    #   for i in request.memory_content:
    #     chunks.append(i)
    if(uploaded_doc):
      file_bytes = await uploaded_doc.read()
      reader = PdfReader(io.BytesIO(file_bytes))
      pdf = []
      for page in reader.pages:
        if page.extract_text():
          pdf.append(page.extract_text())
      pdf = "\n\n".join(pdf)
      chunks['Pdf document'] = pdf
    if(search_box):
      response = onlineSearch(question)
      chunks['Online search'] = response

    context_responses = get_contexts(question,chunks)
    if(chat_history):
      context_responses['Chat History'] = chat_history
    # print("CONTEXT RESPONSES")
    # print(context_responses)


    prompt = f"""You are a helpful Browser assistant who is answering user's questions based on the provided information.

    Question: {question}
    Tagged Context: {context_responses}
    
    Instructions:
    Context which has tag as 'Chat History' is the Conversation History.
    Prioritize information from the given context. But Use Conversation History to maintain continuity only when relevant to the question.
    Also use Conversation History to maintain user preferences, or style.
    Answer the Question only from the sources that have the relevant answer. Ignore the sources that mention the answer is not present in the context.
    Do not make up anything. 
    When combining sources, weave them naturally (e.g., "From the page we know…, the video explains…, earlier you mentioned…").

    """

    # os.environ["OPEN_API_KEY"] = "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"
    # client = OpenAI(
    #       api_key=os.getenv("OPEN_API_KEY"),
    #       base_url="https://openrouter.ai/api/v1"
      # default_headers={
      #     "HTTP-Referer": "http://localhost",     # Optional but good practice
      #     "X-Title": "MyBrowserExtension"         # Optional
      # }
    # )

    # API_KEY=userdata.get('GOOGLE_API_KEY')
    genai.configure(api_key ="AIzaSyA8oRPN777XkvWppZxdZYrJ3YXl-OJ2InA" )
    model = genai.GenerativeModel("gemini-2.5-flash")

    
    response = model.generate_content(prompt)
    return {"answer": response.text.strip()}

  except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print("❌ Backend error:\n", error_msg)
        return JSONResponse(status_code=500, content={"error": str(e), "trace": error_msg})
