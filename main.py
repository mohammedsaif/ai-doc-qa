from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os, time, logging, io
import PyPDF2

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class AskRequest(BaseModel):
    question: str


@app.get("/")
def health():
    return {"status": "ok", "message": "Server is alive!"}


@app.post("/ask")
def ask(body: AskRequest):
    logger.info(f"Question received: {body.question[:60]}")
    start = time.time()

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            timeout=30,
            messages=[{"role": "user", "content": body.question}]
        )
        answer = message.content[0].text
        elapsed = round(time.time() - start, 2)
        logger.info(f"Responded in {elapsed}s")
        return {"answer": answer, "time_taken_seconds": elapsed}

    except Exception as e:
        logger.error(f"Claude call failed: {str(e)}")
        raise HTTPException(status_code=500, detail="AI service failed. Please try again.")


@app.post("/upload-and-ask")
async def upload_and_ask(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    logger.info(f"File received: {file.filename} | Question: {question[:50]}")

    try:
        contents = await file.read()

        if file.filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(io.BytesIO(contents))
            text = "".join(page.extract_text() for page in reader.pages)
        else:
            text = contents.decode("utf-8")

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from this file")

        prompt = f"""Here is a document:

---
{text[:8000]}
---

Based only on the document above, answer this question:
{question}

If the answer is not in the document, say "The document does not contain this information." """

        start = time.time()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            timeout=30,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = message.content[0].text
        elapsed = round(time.time() - start, 2)
        logger.info(f"Document Q&A answered in {elapsed}s, chars read: {len(text)}")

        return {
            "filename": file.filename,
            "characters_extracted": len(text),
            "answer": answer,
            "time_taken_seconds": elapsed
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload and ask failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
