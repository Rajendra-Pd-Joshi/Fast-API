from fastapi import FastAPI ,Path , HTTPException , Query
import json

app = FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
        return data

@app.get("/")
def hello():
    return {'message':'Patient management syste api'}

@app.get("/about")
def about():
    return {'message':' a fully functional api to manage your patient data'}


@app.get('/view')
def view():
    data = load_data()

    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id:str = Path(...,description='id of the patient in the db',example='P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail = 'Patient not found')


@app.get('/sort')
def sort_patients(sort_by: str = Query(...,description='sort on the basis of heights weight or bmi'),order : str = Query('asc',description='sort in asc or desc order')):

    valid_fields = ['heights','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail = f'invalid field select from {valid_fields}')
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='invalid field select either asc or desc')

    sort_order = True if order == 'desc' else False
    data = load_data()

    sorted_data = sorted(data.values(),key= lambda x: x.get(sort_by,0),reverse=False)

    return sorted_data 