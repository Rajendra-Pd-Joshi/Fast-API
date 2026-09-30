"""
Patient Management System API  (FastAPI + Pydantic)

Endpoints
    GET    /                        health check
    GET    /about                   about message
    GET    /view                    all patients
    GET    /patient/{patient_id}    one patient
    GET    /sort                    sorted patients (?sort_by=&order=)
    POST   /create                  create a patient          (Create)
    PUT    /update/{patient_id}     update given fields       (Update)
    DELETE /delete/{patient_id}     delete a patient          (Delete)

Run:  uvicorn main:app --reload      then open  http://127.0.0.1:8000/docs
"""
import json
from typing import Annotated, Literal, Optional

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field, ValidationError, computed_field, field_validator

app = FastAPI(
    title="Patient Management System API",
    description="A REST API to manage patient records using FastAPI and Pydantic.",
    version="1.0.0",
)

# The JSON file that acts as our tiny database.
DATA_FILE = "patients.json"


# ───────────────────────────── Pydantic models ─────────────────────────────

class Patient(BaseModel):
    """A COMPLETE patient record (used for create + for reading/validating stored data)."""

    id: Annotated[str, Field(..., description="ID of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the patient is living")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal["male", "female", "others"], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in meters")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kilograms")]

    # Clean the RAW gender text BEFORE the Literal check runs, so 'Female', 'MALE', ' other ' all work.
    # This also protects us from old records already saved with a capital letter (e.g. 'Female').
    @field_validator("gender", mode="before")
    @classmethod
    def normalize_gender(cls, value):
        if isinstance(value, str):
            value = value.strip().lower()
            if value == "other":          # accept the singular spelling too
                value = "others"
        return value

    # Calculated by the server from height & weight; the client never sends these.
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        return "Obese"


class PatientUpdate(BaseModel):
    """
    Body of a PUT request: every field is OPTIONAL, so the client sends only what changes.
    There is no `id` (the id comes from the URL) and no bmi/verdict (calculated by the server).
    The rules (gt, lt, Literal) are repeated so a provided value is still validated.
    """

    name: Optional[str] = Field(default=None, description="Name of the patient")
    city: Optional[str] = Field(default=None, description="City where the patient is living")
    age: Optional[int] = Field(default=None, gt=0, lt=120, description="Age of the patient")
    gender: Optional[Literal["male", "female", "others"]] = Field(default=None, description="Gender of the patient")
    height: Optional[float] = Field(default=None, gt=0, description="Height in meters")
    weight: Optional[float] = Field(default=None, gt=0, description="Weight in kilograms")


# ───────────────────────────── JSON file helpers ─────────────────────────────

def load_data() -> dict:
    """Read all patients ({id: record}); return an empty dict if the file does not exist yet."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data(data: dict) -> None:
    """Write the COMPLETE dictionary back (mode 'w' overwrites the whole file)."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ───────────────────────────── GET endpoints ─────────────────────────────

@app.get("/")
def hello():
    return {"message": "Patient Management System API"}


@app.get("/about")
def about():
    return {"message": "A fully functional API to manage patient records"}


@app.get("/view")
def view():
    """Return every patient exactly as stored."""
    return load_data()


@app.get("/patient/{patient_id}")
def view_patient(
    patient_id: Annotated[str, Path(description="ID of the patient in the database", examples=["P001"])]
):
    """Return one patient, or 404 if the id does not exist."""
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Rebuild the model so bmi / verdict are always recalculated from height & weight.
    return Patient(id=patient_id, **data[patient_id])


@app.get("/sort")
def sort_patients(
    sort_by: Annotated[str, Query(description="Sort by height, weight, or bmi", examples=["bmi"])],
    # NOTE: with Annotated, the default value goes AFTER the "=", never inside Query(...).
    order: Annotated[str, Query(description="Sort order: asc or desc")] = "asc",
):
    """Return all patients sorted by height, weight or bmi."""
    valid_fields = ["height", "weight", "bmi"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field. Choose from {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order. Choose 'asc' or 'desc'")

    data = load_data()
    patients = [Patient(id=pid, **info) for pid, info in data.items()]

    # getattr(patient, 'bmi') → works for normal AND computed fields
    return sorted(patients, key=lambda p: getattr(p, sort_by), reverse=(order == "desc"))


# ───────────────────────────── POST: create ─────────────────────────────

@app.post("/create", status_code=201)          # 201 Created is the default success code for this endpoint
def create_patient(patient: Patient):
    """The JSON body is validated against `Patient` before this function runs (else 422)."""
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=409, detail="Patient already exists")

    # id is the dictionary key, so it is left out of the stored record
    data[patient.id] = patient.model_dump(exclude={"id"})
    save_data(data)

    return {"message": "Patient created successfully", "patient": patient}


# ───────────────────────────── PUT: update ─────────────────────────────

@app.put("/update/{patient_id}")
def update_patient(patient_id: str, changes: PatientUpdate):
    """Update ONLY the fields that the client sent; keep everything else unchanged."""
    data = load_data()

    # 1) The patient must exist
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2) Only the fields the client really sent.
    #    exclude_unset=True → drop fields that were not in the request body
    #    exclude_none=True  → also drop explicit nulls (a null would otherwise overwrite good data
    #                         with None and crash the validation below with a 500 error)
    changes_dict = changes.model_dump(exclude_unset=True, exclude_none=True)

    if not changes_dict:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    # 3) Merge: start from the stored record and overwrite the changed fields
    merged = data[patient_id].copy()
    merged.update(changes_dict)

    # 4) Validate the COMPLETE updated record (also recalculates bmi & verdict).
    #    We build this model by hand, so a bad stored value would raise a plain Python error (HTTP 500).
    #    Catch it and answer with a readable 422 instead.
    try:
        updated_patient = Patient(id=patient_id, **merged)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=e.errors(include_url=False, include_context=False, include_input=False),
        )

    # 5) Save (id stays the key, so exclude it from the stored record)
    data[patient_id] = updated_patient.model_dump(exclude={"id"})
    save_data(data)

    return {"message": "Patient updated successfully", "patient": updated_patient}


# ───────────────────────────── DELETE ─────────────────────────────

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    """Remove a patient permanently."""
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    del data[patient_id]      # remove the key (and its record) from the dict
    save_data(data)           # persist the change

    return {"message": "Patient deleted successfully"}