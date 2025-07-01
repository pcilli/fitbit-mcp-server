## Generating Your Required Secrets

Add every secret below to a local `.env` file (never commit this file).  
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

## Running the Application Locally

1. **Start the FastAPI backend**

   ```bash
   # inside the project root
   uvicorn main:app --reload --port 8000
   ```

   *`--reload`* auto‑restarts the server when you edit code.  
   If your entrypoint file is not `main.py`, adjust the `module:app` part accordingly.

2. **Authorize with Fitbit**

   1. Open a browser at **http://localhost:8000** (or **http://localhost:8000/docs** for the Swagger UI).  
   2. Click the *“Authorize with Fitbit”* link / button (typically exposed at `/auth/fitbit`).  
   3. Log in to Fitbit and grant permissions. Fitbit will redirect back to your `FITBIT_REDIRECT_URI`, and the backend will cache the access & refresh tokens.

3. **Launch the Streamlit front‑end**

   In a second terminal:

   ```bash
   streamlit run streamlit_app_chatgpt.py
   ```
   
or

   ```bash
   streamlit run streamlit_app_gemini.py
   ```

   Change the script path if your UI file lives elsewhere.  
   The Streamlit app will open in your default browser (usually at **http://localhost:8501**).

You can now chat with the bot – the UI will call the backend on **port 8000** using the Fitbit tokens you just authorised.

