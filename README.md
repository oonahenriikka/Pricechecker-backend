How to run the project:

1. Clone the repo
   git clone https://github.com/oonahenriikka/Pricechecker-backend.git
   cd Pricechecker-backend

2. Create and activate virtual environment
   python -m venv venv
   venv\Scripts\activate          # Windows

3. Install dependencies
   pip install fastapi uvicorn sqlalchemy pydantic pytest httpx "passlib[argon2]" "python-jose[cryptography]" python-multipart argon2-cffi

4. Run the server
   uvicorn app.main:app --reload

5. Open browser → http://127.0.0.1:8000/docs

6. (Optional) Run tests
   pytest -q   
