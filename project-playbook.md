# Week 1 — AI Document Q&A Backend Playbook
### Full explanation: what was built + concepts + test cases per phase

> **How to use this:** Complete every step in a phase. Read the concepts section. Run every test case and confirm it passes. Only move to the next phase when all tests pass.

---

## Phase 1 — Python Setup + Your First Running Server

### Steps
1. Check Python is installed
2. Create a virtual environment
3. Install FastAPI and Uvicorn
4. Write `main.py` with one GET route
5. Run the server

---

### The Code

**Check Python version:**
```bash
python --version
# or
python3 --version
```

**Create project and virtual environment:**
```bash
mkdir ai-doc-qa
cd ai-doc-qa
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

**Install packages:**
```bash
pip install fastapi uvicorn python-dotenv anthropic
```

**Create `main.py`:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok", "message": "Server is alive!"}
```

**Run the server:**
```bash
uvicorn main:app --reload
```

---

### What Was Implemented in the Backend

A minimal HTTP server with one route was created. When a GET request hits `/`, the server responds with a JSON object. The server runs locally on port 8000 and auto-restarts on file save.

---

### Concepts — What's Happening Under the Hood

**Virtual Environment**
Every Python project needs its own isolated environment. Without it, packages from different projects clash.

- Node.js: `node_modules/` is local to each project
- Python without venv: packages install globally and break each other
- Python with venv: a mini Python installation just for this project

When you run `source venv/bin/activate`, your terminal switches to use this project's Python. The `(venv)` prefix in your prompt confirms it is active.

**pip**
pip is Python's package manager — exactly like npm.

| npm | pip |
|---|---|
| `npm install express` | `pip install fastapi` |
| `package.json` | `requirements.txt` |
| `node_modules/` | `venv/lib/site-packages/` |
| `npm install` | `pip install -r requirements.txt` |

**FastAPI**
FastAPI is a Python web framework — like Express.js but for Python. It handles HTTP requests and routes them to your functions.

| Express (JS) | FastAPI (Python) |
|---|---|
| `const app = express()` | `app = FastAPI()` |
| `app.get('/', (req, res) => ...)` | `@app.get("/")` + function below |
| `res.json({status: 'ok'})` | `return {"status": "ok"}` |
| `app.listen(3000)` | `uvicorn main:app` |

**Decorator (`@app.get`)**
The `@app.get("/")` line is called a decorator. It attaches route-handling behaviour to the function directly below it. It tells FastAPI: "when a GET request hits `/`, call this function." You don't need to deeply understand decorators yet — just know this is how routes are defined.

**Uvicorn**
Uvicorn is the server that runs your FastAPI app. The `--reload` flag watches your files and restarts automatically on save — exactly like `nodemon` in Node.js.

**Auto-generated Docs**
FastAPI reads your code and generates a Swagger UI at `/docs`. This gives you a full interactive API tester for free — no frontend needed to test your endpoints.

---

### Test Cases — Phase 1

**TEST 1 — Python version is correct**
```bash
python --version
```
Expected output: `Python 3.10.x` or higher
Fail if: "command not found" — install Python from python.org

---

**TEST 2 — Virtual environment is active**

Look at your terminal prompt after activating. Expected: `(venv)` appears at the start of every line.
Fail if: no `(venv)` — re-run `source venv/bin/activate`

---

**TEST 3 — Packages are installed**
```bash
pip show fastapi
pip show uvicorn
pip show anthropic
```
Expected: each command shows Name, Version, Location.
Fail if: "WARNING: Package not found" — re-run the pip install command

---

**TEST 4 — Server starts without errors**
```bash
uvicorn main:app --reload
```
Expected terminal output:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```
Fail if: `ModuleNotFoundError` — check venv is active

---

**TEST 5 — Health route returns JSON**

Open browser → `http://localhost:8000`

Expected:
```json
{"status": "ok", "message": "Server is alive!"}
```
Fail if: "This site can't be reached" — server is not running

---

**TEST 6 — Swagger UI loads**

Open browser → `http://localhost:8000/docs`

Expected: A page titled "FastAPI" with your GET route listed.
Fail if: 404 — check `main.py` is saved correctly

---

**Phase 1 Complete when:** All 6 tests pass.

---
---

## Phase 2 — Accept User Input + Call Claude API

### Steps
1. Create `.env` file with your Anthropic API key
2. Create `.gitignore`
3. Add a Pydantic request model
4. Add `POST /ask` route that calls Claude
5. Test the full round trip

---

### The Code

**Create `.env`:**
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Create `.gitignore`:**
```
venv/
.env
__pycache__/
*.pyc
```

**Updated `main.py`:**
```python
from fastapi import FastAPI
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class AskRequest(BaseModel):
    question: str

@app.get("/")
def health():
    return {"status": "ok", "message": "Server is alive!"}

@app.post("/ask")
def ask(body: AskRequest):
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": body.question}
        ]
    )
    return {"answer": message.content[0].text}
```

---

### What Was Implemented in the Backend

A POST endpoint `/ask` was added. It receives a JSON body with a `question` field, passes that question to Claude via the Anthropic SDK, and returns Claude's response as JSON. A Pydantic model validates the incoming request body automatically. The API key is loaded securely from a `.env` file.

---

### Concepts — What's Happening Under the Hood

**Environment Variables and `.env`**
Your API key is a secret — never hardcode it in your Python file. The `.env` file stores secrets separately from code. `load_dotenv()` reads that file and loads values into the system's environment. `os.getenv("ANTHROPIC_API_KEY")` retrieves it at runtime.

| Node.js | Python |
|---|---|
| `.env` file | `.env` file (identical) |
| `process.env.MY_KEY` | `os.getenv("MY_KEY")` |
| `require('dotenv').config()` | `load_dotenv()` |

**Pydantic BaseModel — Request Validation**
`BaseModel` defines the shape of incoming request data — like a TypeScript interface but with automatic runtime validation.

```python
class AskRequest(BaseModel):
    question: str
```

If the caller sends a request without the `question` field, FastAPI automatically returns a 422 error. You didn't write that error — Pydantic generated it.

TypeScript comparison:
- TypeScript interface: type checking only at compile time, no runtime enforcement
- Pydantic BaseModel: type checking plus runtime validation plus automatic error messages

**POST Route and Request Body**
`@app.post("/ask")` creates a POST route. The function parameter `body: AskRequest` tells FastAPI to parse the JSON request body and validate it against `AskRequest`. If valid, `body.question` gives you the value directly.

**The Anthropic SDK**
`client.messages.create(...)` calls Claude's API. Key parameters:

| Parameter | What it does |
|---|---|
| `model` | Which Claude model to use |
| `max_tokens` | Maximum response length |
| `messages` | The conversation as role/content pairs |

`message.content[0].text` extracts the text response. Claude returns a list of content blocks — `[0]` gets the first, `.text` gets the string.

**Full Request Lifecycle**
1. React or curl sends `POST /ask` with `{"question": "..."}`
2. FastAPI receives it, Pydantic validates the body
3. Your function calls the Anthropic SDK — this makes an HTTP call from your server to Anthropic's servers
4. Anthropic returns Claude's response
5. Your function extracts the text and returns JSON
6. FastAPI sends it back to the caller

Your server is the middle layer between the user and Claude. This is the fundamental pattern of every AI backend.

---

### Test Cases — Phase 2

**TEST 1 — API key is being loaded**

Add this temporary route to `main.py`:
```python
@app.get("/check-env")
def check_env():
    key = os.getenv("ANTHROPIC_API_KEY")
    return {"key_loaded": key is not None, "key_prefix": key[:10] if key else "missing"}
```

Open browser → `http://localhost:8000/check-env`

Expected:
```json
{"key_loaded": true, "key_prefix": "sk-ant-api"}
```
Fail if: `key_loaded: false` — check `.env` is in the project root and `load_dotenv()` is called at the top.

Remove this route after testing. Never expose your API key in a response.

---

**TEST 2 — Valid question returns Claude's answer**

In Swagger UI (`/docs`):
- Click `POST /ask` → Try it out
- Request body: `{"question": "What is Python in one sentence?"}`

Expected:
```json
{"answer": "Python is a high-level, interpreted programming language..."}
```
Fail if: 500 error — check your API key is correct and has Anthropic credits

---

**TEST 3 — Missing field returns 422 validation error**

Send this body (missing `question`):
```json
{}
```
Expected response (HTTP 422):
```json
{
  "detail": [
    {"loc": ["body", "question"], "msg": "field required", "type": "value_error.missing"}
  ]
}
```
Fail if: 500 error instead of 422 — your Pydantic model is not set up correctly

---

**TEST 4 — Domain-relevant question works**

Send:
```json
{"question": "What kind of data does pharma analytics typically involve?"}
```
Expected: A meaningful answer from Claude about pharma data.
This confirms your prompt is passing through and Claude is responding correctly.

---

**Phase 2 Complete when:** All 4 tests pass. You have a working AI endpoint.

---
---

## Phase 3 — Error Handling + Logging

### Steps
1. Set up Python's logging module
2. Log incoming requests and response times
3. Wrap the Claude call in try/except
4. Add a timeout to prevent hanging
5. Return clean error responses with HTTPException

---

### The Code

**Updated `main.py`:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os, time, logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class AskRequest(BaseModel):
    question: str

@app.get("/")
def health():
    return {"status": "ok"}

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
```

---

### What Was Implemented in the Backend

Three things were added to the existing `/ask` route. First, structured logging now records every incoming question and response time to the terminal with timestamps. Second, the Claude API call is wrapped in a try/except block so any failure — network error, rate limit, timeout — is caught and converted into a clean HTTP 500 response instead of crashing the server. Third, a 30-second timeout was added to the Claude call so a slow response doesn't freeze the request handler indefinitely.

---

### Concepts — What's Happening Under the Hood

**Why Error Handling Matters for AI**
Claude is an external service. It can be slow, hit rate limits, or temporarily fail. Without error handling, any failure causes your entire Python server to throw an unhandled exception — the server crashes and the user gets a connection refused error. Error handling keeps your server alive and returns useful messages instead.

This is exactly like wrapping `fetch()` in a try/catch in React — except you are doing it server-side.

**Python Logging vs print()**
`print()` works but has no structure. Python's `logging` module adds timestamps, log levels, and context automatically.

```python
# print — basic, unstructured
print("Question received")

# logging — structured and timestamped
logger.info("Question received: What is Python?")
# Output: 2026-01-15 14:32:01,234 [INFO] Question received: What is Python?
```

| JavaScript | Python logging |
|---|---|
| `console.log(...)` | `logger.info(...)` |
| `console.warn(...)` | `logger.warning(...)` |
| `console.error(...)` | `logger.error(...)` |

**try/except**
Python's `try/except` is identical in purpose to JavaScript's `try/catch`:

```python
# Python
try:
    result = call_claude()
except Exception as e:
    logger.error(str(e))
    raise HTTPException(status_code=500, detail="Failed")
```

```javascript
// JavaScript equivalent
try {
    const result = await callClaude()
} catch (e) {
    console.error(e.message)
    res.status(500).json({ error: 'Failed' })
}
```

**HTTPException**
`raise HTTPException(status_code=500, detail="...")` stops the function and returns an HTTP error response. It is the Python equivalent of `res.status(500).json({ detail: '...' })` in Express. FastAPI converts it to JSON automatically.

**Timeout**
`timeout=30` tells the Anthropic SDK to throw an error if Claude has not responded in 30 seconds. Without this, a slow Claude response would make your server hang on that request indefinitely. The timeout triggers the `except` block, which returns a clean 500 error instead.

**Response Timing**
```python
start = time.time()
# call claude
elapsed = round(time.time() - start, 2)
```
`time.time()` returns the current time in seconds as a float. Subtracting start from end gives elapsed time. This is how you track how long your AI calls take — critical for spotting slow responses in production.

---

### Test Cases — Phase 3

**TEST 1 — Logs appear in terminal on valid request**

Send any valid question. Then check your terminal window. Expected:
```
2026-01-15 14:32:01,234 [INFO] Question received: What is machine learning?
2026-01-15 14:32:03,891 [INFO] Responded in 2.66s
```
Fail if: no logs appear — check `logging.basicConfig(...)` is set up and `logger = logging.getLogger(__name__)` is present

---

**TEST 2 — Response includes `time_taken_seconds`**

Send any valid question. Expected response:
```json
{"answer": "...", "time_taken_seconds": 2.66}
```
Fail if: field is missing — check the return statement includes `"time_taken_seconds": elapsed`

---

**TEST 3 — Server handles invalid API key gracefully**

Temporarily change your API key in `.env` to an invalid value:
```
ANTHROPIC_API_KEY=sk-ant-invalid-key-for-testing
```
Restart the server. Send a question. Expected response (HTTP 500):
```json
{"detail": "AI service failed. Please try again."}
```
Expected terminal log:
```
2026-01-15 14:35:12,001 [ERROR] Claude call failed: Authentication error...
```
The server must NOT crash — it stays running and handles the next request normally.
Fail if: server crashes entirely — your try/except is not wrapping the Claude call.

Restore your real API key after this test.

---

**TEST 4 — Error log level appears distinctly**

During Test 3, confirm the terminal shows `[ERROR]` not `[INFO]` for the failure line. The log levels must be visually distinct.

---

**TEST 5 — Empty question is handled**

Send: `{"question": ""}`

Expected: Claude still responds (with something like "you didn't ask anything") or you can add explicit validation:
```python
if not body.question.strip():
    raise HTTPException(status_code=400, detail="Question cannot be empty")
```
Either outcome is acceptable. What matters is no unhandled crash.

---

**Phase 3 Complete when:** Server stays alive through failures, logs appear for every request, all errors return clean JSON.

---
---

## Phase 4 — Accept a Document + Answer Questions About It

### Steps
1. Install PyPDF2 for PDF reading
2. Add `/upload-and-ask` route accepting a file and a question
3. Extract text from .txt and .pdf files
4. Build a grounded prompt combining document and question
5. Return Claude's answer with metadata

---

### The Code

**Install PDF support:**
```bash
pip install pypdf2
pip freeze > requirements.txt
```

**Add to `main.py`:**
```python
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import PyPDF2, io

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
```

---

### What Was Implemented in the Backend

A new endpoint `/upload-and-ask` was added. It accepts two inputs simultaneously: a binary file upload and a text question sent as form data. The backend reads the file bytes, extracts the text content (handling both .txt and .pdf formats), injects that text into a prompt alongside the question, and sends the combined prompt to Claude. Claude's answer is returned along with metadata including the filename, how many characters were extracted, and how long the call took.

---

### Concepts — What's Happening Under the Hood

**File Uploads with `UploadFile`**
`UploadFile` is FastAPI's built-in file handler — like `multer` in Express. The browser sends files as `multipart/form-data`, a special binary encoding. FastAPI receives it and gives you:
- `file.filename` — the original filename
- `await file.read()` — the raw bytes of the file

`await` is needed because reading a file is an async operation.

**`async def` vs `def`**
This route uses `async def` instead of `def` because it uses `await`. In FastAPI:
- `def` — synchronous, runs in a thread pool
- `async def` — asynchronous, runs in the event loop

Use `async def` when your function uses `await`. This is the same async/await pattern you already know from JavaScript.

**Form Data vs JSON Body**
The `/ask` route uses a JSON body. The `/upload-and-ask` route uses form data because you cannot send binary files inside JSON.

| Format | When used | FastAPI type |
|---|---|---|
| JSON body | Text and structured data | `BaseModel` |
| Form data | Files alongside text fields | `File(...)` and `Form(...)` |

The `...` inside `File(...)` and `Form(...)` means the field is required.

**Text Extraction**

For `.txt` files: `contents.decode("utf-8")` converts raw bytes to a Python string. Bytes are the raw binary representation — decode interprets them as readable UTF-8 text.

For `.pdf` files: PDFs store text in a compressed binary format. `PyPDF2.PdfReader` parses the structure and `page.extract_text()` pulls readable text from each page.

**Prompt Grounding**
```python
prompt = f"""Here is a document:
---
{text[:8000]}
---
Based only on the document above, answer this question: {question}"""
```

You are injecting the document directly into the prompt. This is called grounding — giving Claude context it does not already have. The phrase "based only on the document above" prevents Claude from using its general training knowledge and forces it to answer only from your document.

`text[:8000]` limits to 8000 characters to stay within a safe token budget. One token is approximately 4 characters, so 8000 characters is roughly 2000 tokens. This is the manual version of RAG (Retrieval-Augmented Generation), which you will build properly in Week 2.

**Re-raising HTTPException**
```python
except HTTPException:
    raise
except Exception as e:
    ...
```
The first `except` re-raises `HTTPException` unchanged — so your 400 "no text extracted" error passes through without being overwritten. Without this, the outer `except Exception` would catch the 400 and replace it with a generic 500. Always re-raise HTTP exceptions before your generic catch.

---

### Test Cases — Phase 4

**TEST 1 — Upload a .txt file and get a grounded answer**

Create `test_doc.txt` with this content:
```
Mohammed Saif is a senior frontend developer with 11 years of experience.
He has worked with React, Angular, and Vue.js.
His domain experience includes pharma analytics, IoT, and logistics.
He is currently transitioning to AI engineering.
```

In Swagger UI → `POST /upload-and-ask`:
- Upload `test_doc.txt`
- Question: `What domains has Mohammed worked in?`

Expected response:
```json
{
  "filename": "test_doc.txt",
  "characters_extracted": 234,
  "answer": "Mohammed has worked in pharma analytics, IoT, and logistics.",
  "time_taken_seconds": 1.84
}
```
Fail if: answer mentions things not in the document — check your prompt includes "based only on the document above"

---

**TEST 2 — Claude respects document boundaries**

Same file, new question: `What is Mohammed's email address?`

Expected answer: something like "The document does not contain this information."
Fail if: Claude invents an email address — your grounding instruction is not strong enough

---

**TEST 3 — Upload a PDF file**

Upload any small PDF with readable text. Ask a question about its content.

Expected: `characters_extracted` is greater than 0 and the answer is relevant.
Fail if: `characters_extracted: 0` — the PDF may be image-based (scanned). Try a different PDF with actual selectable text.

---

**TEST 4 — Terminal shows file metadata logs**

After any upload, check terminal:
```
2026-01-15 [INFO] File received: test_doc.txt | Question: What domains...
2026-01-15 [INFO] Document Q&A answered in 1.84s, chars read: 234
```
Fail if: logs do not appear — check `logger.info(...)` calls are in the route

---

**TEST 5 — Empty file returns 400 not 500**

Create an empty file `empty.txt` (0 bytes). Upload it with any question.

Expected (HTTP 400):
```json
{"detail": "No text could be extracted from this file"}
```
Fail if: 500 error — your `if not text.strip()` check is missing

---

**TEST 6 — requirements.txt includes pypdf2**

```bash
cat requirements.txt
```
Expected: `pypdf2` appears alongside fastapi, uvicorn, anthropic, python-dotenv.
Fail if: missing — run `pip freeze > requirements.txt`

---

**Phase 4 Complete when:** All 6 tests pass. You can upload a document and get document-grounded answers.

---
---

## Phase 5 — Deploy to Railway + Call from React

### Steps
1. Add CORS middleware so React can call the API
2. Create `Procfile` (tells Railway how to start your app)
3. Create `runtime.txt` (tells Railway which Python version)
4. Push to GitHub
5. Deploy on Railway and add the API key as an env var
6. Get your public URL and call it from React

---

### The Code

**Add CORS to `main.py`** right after `app = FastAPI()`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Create `Procfile`** (no file extension):
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Create `runtime.txt`:**
```
python-3.11.0
```

**Push to GitHub:**
```bash
git init
git add .
git commit -m "Week 1: AI Document Q&A API"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-doc-qa.git
git push -u origin main
```

**Call from React:**
```javascript
// Simple question
const askQuestion = async (question) => {
  const res = await fetch("https://YOUR-URL.up.railway.app/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  const data = await res.json();
  return data.answer;
};

// File upload — do NOT set Content-Type manually
const uploadAndAsk = async (file, question) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("question", question);
  const res = await fetch("https://YOUR-URL.up.railway.app/upload-and-ask", {
    method: "POST",
    body: formData
  });
  const data = await res.json();
  return data.answer;
};
```

---

### What Was Implemented in the Backend

CORS middleware was added so browsers allow cross-origin requests from your React frontend. A `Procfile` was created to tell Railway the exact command to start the server. A `runtime.txt` specifies the Python version. The app was pushed to GitHub, which Railway uses as the deployment source. The API key was added to Railway's Variables dashboard — it gets injected as an environment variable at runtime, same as `.env` does locally.

---

### Concepts — What's Happening Under the Hood

**CORS**
CORS (Cross-Origin Resource Sharing) is a browser security rule. When your React app on one domain calls your API on a different domain, the browser sends a preflight `OPTIONS` request asking "is this allowed?" Your server must respond with the right headers — otherwise the browser blocks the request before it reaches your code.

`CORSMiddleware` handles this automatically. `allow_origins=["*"]` allows any domain during development. In production you would change this to your exact frontend URL for security.

You have seen CORS errors from the React side before. Now you are the one fixing them from the server side.

**Procfile**
Railway needs to know how to start your app. The `Procfile` is a single line naming the process type and its start command.

- `--host 0.0.0.0` makes the server listen on all network interfaces, not just localhost, so it is reachable from outside the container
- `--port $PORT` lets Railway assign the port dynamically. Your server must use whatever port Railway provides — it will not always be 8000

**Environment Variables on Railway**
On your laptop, secrets live in `.env`. On Railway, they live in the Variables dashboard. Railway injects them as environment variables at runtime. `os.getenv("ANTHROPIC_API_KEY")` works identically in both environments. Your `.env` file never goes to Railway.

**What Railway Does on Deploy**
1. Clones your GitHub repository
2. Reads `runtime.txt` and installs Python 3.11
3. Runs `pip install -r requirements.txt`
4. Reads `Procfile` and starts your server
5. Assigns a public URL
6. Every future `git push` triggers an automatic redeploy

This is identical to how Vercel deploys your React apps — just for a Python backend.

**FormData in React — No Content-Type Header**
When sending a file with `FormData`, do not set `Content-Type: multipart/form-data` manually. The browser sets it automatically and includes a `boundary` string that separates the fields. If you set it manually, you omit the boundary and the server cannot parse the body.

---

### Test Cases — Phase 5

**TEST 1 — CORS headers are present**

With your server running locally, open DevTools in your browser. Send a request from your React app on `localhost:3000` to `localhost:8000`. Check the Network tab response headers. Expected:
```
access-control-allow-origin: *
```
Fail if: CORS error in the browser console — restart your server after adding the middleware

---

**TEST 2 — Procfile format is correct**

```bash
cat Procfile
```
Expected exact content:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```
Fail if: file has a `.txt` extension or any typos — Railway will not detect it

---

**TEST 3 — requirements.txt has all packages**

```bash
cat requirements.txt
```
Expected: contains fastapi, uvicorn, anthropic, python-dotenv, pypdf2
Fail if: any package is missing — run `pip freeze > requirements.txt`

---

**TEST 4 — Railway build completes successfully**

In Railway dashboard, click your deployment and open the build log. Expected final line:
```
Build successful
```
Fail if: `ModuleNotFoundError` — a package is missing from `requirements.txt`

---

**TEST 5 — Public URL returns health response**

Open browser → `https://YOUR-URL.up.railway.app/`

Expected:
```json
{"status": "ok"}
```
Fail if: "Application error" — check Railway logs and confirm env variables are set

---

**TEST 6 — Public API answers a question**

Open `https://YOUR-URL.up.railway.app/docs` → test `POST /ask` with:
```json
{"question": "What is FastAPI?"}
```
Expected: a valid answer from Claude.
Fail if: HTTP 500 — `ANTHROPIC_API_KEY` is missing from Railway Variables

---

**TEST 7 — React frontend calls the deployed API**

In your React app, add a button that calls `askQuestion("What is AI engineering?")` and logs the result. Open DevTools Console. Expected: Claude's answer printed with no CORS errors.
Fail if: CORS error — the middleware was added but the server was not restarted

---

**Phase 5 Complete when:** All 7 tests pass. Your API is live, callable from anywhere, and your React app is getting AI responses.

---
---

## Full Project Summary

| Phase | What you built | Key concept learned |
|---|---|---|
| 1 | Running FastAPI server | Python env, pip, HTTP routes, auto docs |
| 2 | POST /ask calling Claude | Request validation, env vars, Anthropic SDK |
| 3 | Error handling and logging | try/except, timeouts, structured logs |
| 4 | File upload and document Q&A | async, file parsing, prompt grounding |
| 5 | Deployed and React connected | CORS, Railway, production env vars |

## Final Folder Structure

```
ai-doc-qa/
├── main.py              <- all API routes
├── .env                 <- secrets, never commit
├── .gitignore
├── requirements.txt     <- like package.json
├── Procfile             <- Railway start command
├── runtime.txt          <- Python version
└── venv/                <- local packages, never commit
```

---

*Mohammed Saif — AI Backend Playbook v2 — 2026*