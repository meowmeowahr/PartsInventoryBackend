from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

import sorter  # Make sure to import your database module here

app = FastAPI()


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

part_sorter = sorter.PartSorter()


class Location(BaseModel):
    id: str
    name: str
    icon: str
    tags: Optional[str] = None
    attrs: dict


class Sorter(BaseModel):
    id: str
    location: str
    name: str
    icon: str
    tags: Optional[str] = None
    attrs: dict


@app.post("/locations/", response_model=Location, status_code=201)
def create_location(location: Location):
    try:
        part_sorter.create_location(location.id, location.name, location.icon, location.tags, location.attrs)
        return location
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/locations/", response_model=List[Location])
def get_locations():
    return part_sorter.get_locations()


@app.get("/locations/{location_id}", response_model=Location)
def get_location(location_id: str):
    locations = part_sorter.get_locations()
    for loc in locations:
        if loc['id'] == location_id:
            return loc
    raise HTTPException(status_code=404, detail="Location not found")


@app.put("/locations/{location_id}", response_model=Location)
def update_location(location_id: str, location: Location):
    try:
        part_sorter.update_location(location_id, location.name, location.icon, location.tags, location.attrs)
        return location
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/locations/{location_id}")
def delete_location(location_id: str):
    try:
        part_sorter.delete_location(location_id)
        return {"detail": "Location deleted successfully"}
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/sorters/", response_model=Sorter, status_code=201)
def create_sorter(sorter_item: Sorter):
    try:
        part_sorter.create_sorter(sorter_item.id, sorter_item.location, sorter_item.name, sorter_item.icon, sorter_item.tags, sorter_item.attrs)
        return sorter_item
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/sorters/", response_model=List[Sorter])
def get_sorters():
    return part_sorter.get_sorters()


@app.get("/sorters/{sorter_id}", response_model=Sorter)
def get_sorter(sorter_id: str):
    sorters = part_sorter.get_sorters()
    for sort in sorters:
        if sort['id'] == sorter_id:
            return sort
    raise HTTPException(status_code=404, detail="Sorter not found")


@app.put("/sorters/{sorter_id}", response_model=Sorter)
def update_sorter(sorter_id: str, sorter_item: Sorter):
    try:
        part_sorter.update_sorter(sorter_id, sorter_item.location, sorter_item.name, sorter_item.icon, sorter_item.tags, sorter_item.attrs)
        return sorter_item
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/sorters/{sorter_id}")
def delete_sorter(sorter_id: str):
    try:
        part_sorter.delete_sorter(sorter_id)
        return {"detail": "Sorter deleted successfully"}
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
