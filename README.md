# Codebase Overview

## TLDR;

Use this code to connect either ChatGPT or Gemini to a Fitbit account through an MCP server.

## Repository Purpose

This repository provides a set of web applications and backend scripts for interacting with LLMs (such as Gemini and ChatGPT) and managing Fitbit data. It leverages **Streamlit** for web interfaces and **FastAPI** for backend API endpoints, integrating with Google and OpenAI’s language models as well as Fitbit data sources.

---

## File Summaries

### 1. `streamlit_app_gemini.py`

- **Purpose:**  
  Web application interface built with Streamlit for interacting with Google’s Gemini LLM.
- **Key Features:**  
  - Accepts user queries and displays Gemini’s responses.
  - Handles user session states and prompt management.
  - Clean and minimal UI for LLM interaction.

### 2. `streamlit_app_chatgpt.py`

- **Purpose:**  
  Web application interface built with Streamlit for interacting with OpenAI’s ChatGPT LLM.
- **Key Features:**  
  - Similar to the Gemini app, but uses the OpenAI API.
  - Handles user queries and displays ChatGPT responses.
  - Provides session and prompt history.

### 3. `main.py`

- **Purpose:**  
  Main entry point for the FastAPI backend service.
- **Key Features:**  
  - Starts the API server.
  - Sets up all routes and core API configuration.
  - Likely includes startup events and root endpoint.

### 4. `fitbit_router.py`

- **Purpose:**  
  FastAPI router for handling Fitbit-related API endpoints.
- **Key Features:**  
  - Contains routes for accessing and managing Fitbit data.
  - Handles API requests, data formatting, and error handling specific to Fitbit integrations.
  - Intended for modular integration into the main FastAPI application.

### 5. `requirements.txt`

- **Purpose:**  
  Lists all required Python packages to run the codebase.
- **Key Libraries:**  
    - `fastapi`, `uvicorn` (backend web API)
    - `streamlit` (web apps)
    - `httpx`, `requests` (HTTP requests)
    - `python-dotenv` (environment variable management)
    - `openai`, `google-generativeai` (LLM APIs)
    - `pydantic` (data validation)

---

## How the Pieces Fit Together

- **Frontend:**  
  The two Streamlit apps (`streamlit_app_gemini.py` and `streamlit_app_chatgpt.py`) provide user interfaces to interact with different LLMs.

- **Backend:**  
  `main.py` launches the FastAPI server, registering routes from `fitbit_router.py` and likely other modules. The backend provides APIs for Fitbit data handling and potentially serves as a backend for the Streamlit apps.

- **Fitbit Integration:**  
  All Fitbit API routes and logic are modularized in `fitbit_router.py`, which is included by the main FastAPI app.

- **Dependencies:**  
  All dependencies are listed in `requirements.txt` for easy installation and reproducibility.

---

## Getting Started

1. **Install requirements:**  
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the backend API:**  
   ```bash
   uvicorn main:app --reload
   ```

3. **Launch Streamlit apps:**  
   ```bash
   streamlit run streamlit_app_gemini.py
   # or
   streamlit run streamlit_app_chatgpt.py
   ```

---

## Generating Your Required Secrets

Add every secret below to a local `.env` file.  
Example:

```dotenv
FITBIT_CLIENT_ID=xxxxxxxxxxxx
FITBIT_CLIENT_SECRET=xxxxxxxxxxxx
FITBIT_REDIRECT_URI=http://localhost:8000/fitbit/auth/fitbit/callback
FITBIT_USER_ID=xxxxxxxx
OPENAI_API_KEY_FB=sk-xxxxxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxx
```

---

### 1 · Fitbit API Credentials

**FITBIT_CLIENT_ID** and **FITBIT_CLIENT_SECRET**

1. Sign in (or create) a free developer account at **https://dev.fitbit.com**.  
2. Navigate to **Manage → Register An App** and fill in the form (choose OAuth 2.0 type **“Server”**).  
3. After saving, the portal shows your **Client ID** and **Client Secret** — copy both into the `.env`.

**FITBIT_REDIRECT_URI**

1. While editing the same Fitbit app, locate **OAuth 2.0 Redirect URLs**.  
2. Enter the URL your backend will listen on during OAuth (e.g. `http://localhost:8000/fitbit/auth/fitbit/callback` in development).  
3. Use *exactly* that string for `FITBIT_REDIRECT_URI` in the `.env`.

**FITBIT_USER_ID**

*Quick method (mobile app)*  
1. Open the Fitbit mobile app.  
2. Tap **Today → profile icon → Personal information**.  
3. Copy the long, encoded ID shown under your name.

*API method*  
1. Complete the OAuth flow with your new Client ID/Secret and Redirect URI.  
2. Call `GET https://api.fitbit.com/1/user/-/profile.json` with the access token.  
3. Read `user.encodedId` from the JSON and place it in `FITBIT_USER_ID`.

---

### 2 · OpenAI Key (`OPENAI_API_KEY_FB`)

1. Log in at **https://platform.openai.com**.  
2. Click **“API Keys”** in the left sidebar.  
3. Choose **“Create new secret key”**, give it a name, and copy it immediately.  
4. Add the key to `OPENAI_API_KEY_FB` in the `.env`.

---

### 3 · Gemini Key (`GEMINI_API_KEY`)

**Option A — Google AI Studio (fast)**  
1. Go to **https://aistudio.google.com**.  
2. Select **API Keys → “Create API key”**.  
3. Copy the key and store it in `GEMINI_API_KEY`.

**Option B — Google Cloud Console**  
1. Open the Cloud Console and create / select a project.  
2. Enable the **Gemini API**.  
3. Navigate to **APIs & Services → Credentials → Create Credential → API key**.  
4. (Optional) Add key restrictions, then copy it into `GEMINI_API_KEY`.


---
