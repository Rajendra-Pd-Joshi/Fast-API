# FastAPI & Pydantic — Learning Notes

<p align="center">
  <img src="assets/fastapi_thumbnail.png" alt="FastAPI learning thumbnail" width="800">
</p>

A hands-on learning repository for building Python APIs with **FastAPI** and validating structured data with **Pydantic**. The repository contains Jupyter notebooks, example patient data, and visual assets used alongside the lessons.

## Contents

| File | What you'll learn |
|---|---|
| [Pydantic_Notes.ipynb](Pydantic_Notes.ipynb) | Pydantic fundamentals and data validation, using typed models and field definitions to describe and validate Python data. The notebook also accompanies the Pydantic live-class recordings. |
| [HTTP_get_Concepts.ipynb](HTTP_get_Concepts.ipynb) | API, REST and HTTP basics; GET requests; path and query parameters; status codes; FastAPI endpoints; validation and error handling; sorting; and interactive API documentation. |
| [patients.json](patients.json) | Sample patient records used by the Patient Management System API notebook. |
| `assets/` | FastAPI, Pydantic, and GitHub profile visuals. |

## FastAPI notebook: Patient Management API

The HTTP GET notebook builds a small, read-only Patient Management System API backed by a JSON file. It demonstrates:

- Creating an application with `FastAPI()` and registering routes with `@app.get()`.
- Returning Python dictionaries and lists as JSON responses.
- Loading sample records from `patients.json`.
- Retrieving all records with `GET /view` and an individual record with `GET /patient/{patient_id}`.
- Using `Path()` for path parameters and `Query()` for query parameters.
- Sorting records by height, weight, or BMI in ascending or descending order.
- Handling errors with `HTTPException` and appropriate HTTP status codes.
- Validating allowed query values with Python's `Literal` type.
- Testing endpoints with FastAPI's `TestClient`.
- Exploring generated OpenAPI documentation with Swagger UI and ReDoc.

### Example endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Basic API message / health check |
| GET | `/about` | Brief API description |
| GET | `/view` | Return all patient records |
| GET | `/patient/{patient_id}` | Return one patient by ID |
| GET | `/sort?sort_by=bmi&order=desc` | Sort records by a supported field |

These routes are examples from the notebook; they are not a separately deployed public API.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/Rajendra-Pd-Joshi/Fast-API.git
cd Fast-API
```

### 2. Create and activate a virtual environment (recommended)

**Windows PowerShell**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

For the FastAPI notebook and running its example server:

```bash
python -m pip install fastapi uvicorn jupyter httpx
```

Open the notebooks in Jupyter:

```bash
jupyter notebook
```

> **Note:** The HTTP GET notebook uses FastAPI's `TestClient` for in-notebook endpoint tests. If your installed FastAPI/Starlette version reports a test-client dependency error, install a compatible `httpx` version. Run notebook cells in order.

## Run the example API

The HTTP GET notebook includes a consolidated `main.py` example. If you have saved that code as `main.py` in the repository root, and `patients.json` is in the same directory, start the development server with:

```bash
uvicorn main:app --reload
```

Then visit:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **OpenAPI schema:** http://127.0.0.1:8000/openapi.json

The server command expects a `main.py` file; the repository's consolidated application is shown inside the notebook.

## Concepts covered

- API, REST, HTTP methods, URLs, and endpoints
- GET semantics and status codes
- FastAPI route decorators and JSON responses
- Path parameters versus query parameters
- Type hints and Pydantic-backed validation
- Error handling with `HTTPException`
- Sorting and validating request parameters
- Automated endpoint checks with `TestClient`
- Automatic interactive API documentation

## Learning suggestions

1. Read the Pydantic notebook to understand structured data and validation.
2. Work through the HTTP GET notebook from top to bottom.
3. Execute the examples and inspect their response bodies and status codes.
4. Try the practice exercises at the end of the HTTP GET notebook, such as filtering patients by city or age and adding a statistics endpoint.
5. Experiment with the generated documentation at `/docs`.

## References

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [FastAPI path parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI query parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [MDN: HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)

---

Made for learning and practicing **FastAPI, Pydantic, and Python API development**.
