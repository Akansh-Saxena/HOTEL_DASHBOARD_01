# Phase 4: Integration & Global Deployment

This guide covers how to push your local FastAPI backend and Next.js frontend to the web so they can communicate globally, securely, and seamlessly.

## 1. Backend Deployment (Render.com)

Render provides a fast and free way to deploy Python web services.

### Steps
1. **GitHub Repository**: Initialize a GitHub repository for your `backend` folder. Commit and push your code to GitHub.
   ```bash
   cd backend
   git init
   git add .
   git commit -m "Initial commit for FastAPI backend"
   git branch -M main
   # Link to your remote GitHub repo and push
   ```
2. **Render Dashboard**: Go to [Render.com](https://render.com/), sign in, and click **New +** > **Web Service**.
3. **Connect GitHub**: Select your backend repository.
4. **Configuration**:
   - **Name**: `aether-api` (or similar)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt` (Make sure your `requirements.txt` is in the root of the backend directory)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**: Click on "Advanced" to add Env Vars:
   - `SECRET_KEY`: `your_super_secret_jwt_key_here`
   - `AMADEUS_API_KEY`: `your_amadeus_key` (Optional)
   - `AMADEUS_API_SECRET`: `your_amadeus_secret` (Optional)
   - `GOOGLE_PLACES_API_KEY`: `your_google_key` (Optional)
6. **Deploy**: Click **Create Web Service**. 
7. **Copy URL**: Once live, copy your new global API URL (e.g., `https://aether-api.onrender.com`).

---

## 2. Frontend Deployment (Vercel.com)

Vercel is optimized for Next.js applications, offering seamless deployment.

### Steps
1. **GitHub Repository**: Ensure your `frontend` directory is pushed to GitHub as well (either separately or as part of a monorepo).
   ```bash
   cd frontend
   git init
   git add .
   git commit -m "Initial Next.js setup with JWT Auth"
   git branch -M main
   # Link to your remote GitHub repo and push
   ```
2. **Vercel Dashboard**: Go to [Vercel.com](https://vercel.com/) and click **Add New** > **Project**.
3. **Import Project**: Import your frontend GitHub repository.
   - If it's a monorepo, set the **Root Directory** to `frontend`.
4. **Environment Variables**:
   Under "Environment Variables", add:
   - `NEXT_PUBLIC_API_URL`: Paste your Render API URL (e.g., `https://aether-api.onrender.com`). **Do not include a trailing slash.**
5. **Deploy**: Click **Deploy**. Vercel will build and launch your Next.js application.

---

## 3. Post-Deployment Verification
1. Access your new Vercel `.vercel.app` URL.
2. Ensure you are redirected to the Login page. 
3. Try logging in with the test user details (`admin@aether.com` and password). Note: Currently, the backend uses a mock user registry, so you must **register a user first** before logging in. 
4. Upon successful login, you should be routed back to the main dashboard displaying real-time Hotel mock rates fetched securely from your Render global API!
