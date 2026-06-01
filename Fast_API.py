from fastapi import FastAPI, Path, HTTPException, Query
import json 
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
from fastapi.responses import JSONResponse

app = FastAPI(title="Patient Management System API", description="CRUD API built using FastAPI and Pydantic", version="1.0.0")

def load_data():
    with open("JSON_DATA.json") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("JSON_DATA.json", "w")as f:
       json.dump(data, f)

class Patient(BaseModel):
    id : Annotated[str, Field(..., description= "ID of the Patient", examples= ["P001"])]
    name : Annotated[str, Field(..., description= "Enter name of Patient")]
    city : Annotated[str, Field(..., description= "Enter name of city where Patient is living")]
    age : Annotated[int, Field(..., gt= 0 , lt= 100, description="Enter Age of the Patient")]
    gender : Annotated[Literal ["Male", "Female", "Others"], Field(..., description= "Enter Gender of Patient")]
    height : Annotated[float, Field(..., gt= 0, description="Enter Height of the patient")]
    weight : Annotated[float, Field(..., gt= 0, description= "Enter weight od the Patient")]

class PatientResponse(BaseModel):
    message: str
    patient_id: str

class PatientUpdate(BaseModel):
    name : Annotated[Optional[str], Field(default= None ,description= "Enter name of Patient")]
    city : Annotated[Optional[str], Field(default= None ,description= "Enter name of city where Patient is living")]
    age : Annotated[Optional[int], Field(default= None ,gt= 0 , lt= 100, description="Enter Age of the Patient")]
    gender : Annotated[Optional[Literal ["Male", "Female", "Others"]], Field(default= None ,description= "Enter Gender of Patient")]
    height : Annotated[Optional[float], Field(default= None ,gt= 0, description="Enter Height of the patient")]
    weight : Annotated[Optional[float], Field(default= None ,gt= 0, description= "Enter weight od the Patient")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/ (self.height**2),2)
        return bmi
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underwieght"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30: 
            return "Noramal"
        else:
            return "Obese"
        
def view(
    city: str | None = Query(default=None), min_age: int | None = Query(default=None), max_age: int | None = Query(default=None)):
    data = load_data()
    result = {}

    for patient_id, patient in data.items():
        if city and patient["city"].lower() != city.lower():
            continue
        if min_age and patient["age"] < min_age:
            continue
        if max_age and patient["age"] > max_age:
            continue
        result[patient_id] = patient
    return result

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(...,  description="ID of the patient",examples="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code= 404, detail= "Patient not found")

@app.post("/create", response_model=PatientResponse)
def create_patient(patient : Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code= 400, detail= "Patient already exist")
    
    data[patient.id] = patient.model_dump(exclude= {"id"})
    save_data(data)

    return {"message" : "Patient created Successfully"} 

@app.put("/edit/{patient_id}")
def update_patient(patient_id : str , patient_update : PatientUpdate):

    data = load_data()
    if patient_id not in data: 
        raise HTTPException(status_code= 404, detail= "Patient not found")
    
    existing_patient_info = data[patient_id]

    update_patient_info = patient_update.model_dump(exclude_unset= True)

    for key, value in update_patient_info.items():
        existing_patient_info[key] = value

    existing_patient_info["id"] = patient_id
    patient_pydantic_info = Patient(existing_patient_info)

    existing_patient_info = patient_pydantic_info.model_dump(exclude= "id")

    data[patient_id] = existing_patient_info

    return JSONResponse(status_code= 200, content= {"Message" : "Patient Updated"})

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id : str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException (status_code= 404, detail= "Patient not found")
    
    del data[patient_id]

    save_data(data)
    return JSONResponse (status_code= 200, content= {"Message" : "Patient deleted sucessfully"}) 