from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel
from typing import List

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
    tags: str
    attrs: dict


class Sorter(BaseModel):
    id: str
    location: str
    name: str
    icon: str
    tags: str
    attrs: dict


class PartNullable(BaseModel):
    id: str
    sorter: str | None
    name: str | None
    quantity: int | None
    quantity_type: str | None
    enable_quantity: bool | None
    price: float | None
    notes: str | None
    location: str | None
    tags: str | None = None
    attrs: dict | None


class Part(BaseModel):
    id: str
    sorter: str
    name: str
    quantity: int
    quantity_type: str
    enable_quantity: bool
    price: float
    notes: str
    location: str
    tags: str
    attrs: dict


class PartImageNullable(BaseModel):
    id: str
    image: str | None

class PartIdentify(BaseModel):
    location: str
    api: str

@app.post("/locations/", response_model=Location, status_code=201)
def create_location(location: Location):
    try:
        part_sorter.create_location(
            location.id, location.name, location.icon, location.tags, location.attrs
        )
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
        if loc["id"] == location_id:
            return loc
    raise HTTPException(status_code=404, detail="Location not found")


@app.put("/locations/{location_id}", response_model=Location)
def update_location(location_id: str, location: Location):
    try:
        part_sorter.update_location(
            location_id, location.name, location.icon, location.tags, location.attrs
        )
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
        part_sorter.create_sorter(
            sorter_item.id,
            sorter_item.location,
            sorter_item.name,
            sorter_item.icon,
            sorter_item.tags,
            sorter_item.attrs,
        )
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
        if sort["id"] == sorter_id:
            return sort
    raise HTTPException(status_code=404, detail="Sorter not found")


@app.put("/sorters/{sorter_id}", response_model=Sorter)
def update_sorter(sorter_id: str, sorter_item: Sorter):
    try:
        part_sorter.update_sorter(
            sorter_id,
            sorter_item.location,
            sorter_item.name,
            sorter_item.icon,
            sorter_item.tags,
            sorter_item.attrs,
        )
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


@app.post("/parts_individual/", response_model=Part, status_code=201)
def create_part(part_item: Part):
    try:
        part_sorter.create_part(
            part_item.id,
            part_item.sorter,
            part_item.name,
            part_item.quantity,
            part_item.quantity_type,
            part_item.enable_quantity,
            part_item.tags,
            part_item.price,
            part_item.notes,
            part_item.location,
            part_item.attrs,
        )
        return part_item
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/parts/", response_model=List[Part])
def get_parts():
    parts = part_sorter.get_parts()
    parts_without_images = []
    for part in parts:
        part.pop("image")
        parts_without_images.append(part)
        

    return parts_without_images


@app.get("/parts/{sorter_id}", response_model=List[Part])
def get_parts_from_sorter(sorter_id: str):
    parts: list[dict] = part_sorter.get_parts()
    parts_in_sorter = []

    for part in parts:
        if part["sorter"] == sorter_id:
            part.pop("image")
            parts_in_sorter.append(part)
    return parts_in_sorter


@app.put("/parts_individual/{part_id}", response_model=PartNullable)
def update_part(part_id: str, part_item: PartNullable):
    try:
        part_sorter.update_part(
            part_id,
            part_item.sorter,
            part_item.name,
            part_item.quantity,
            part_item.quantity_type,
            part_item.enable_quantity,
            part_item.tags,
            part_item.price,
            part_item.notes,
            part_item.location,
            part_item.attrs,
        )
        return part_item
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/parts_individual/{part_id}/image", response_model=PartImageNullable)
def set_part_image(part_id: str, part_item: PartImageNullable):
    try:
        part_sorter.set_part_image(part_id, part_item.image)
        return part_item
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/parts_individual/{part_id}")
def get_part(part_id: str):
    parts = part_sorter.get_parts()
    for part in parts:
        if part["id"] == part_id:
            return part
    raise HTTPException(status_code=404, detail="Part not found")


@app.delete("/parts_individual/{part_id}")
def delete_part(part_id: str):
    try:
        part_sorter.delete_part(part_id)
        return {"detail": "Sorter deleted successfully"}
    except sorter.SorterIdInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/part_identify/")
async def identify_part(response: PartIdentify):
    # Define the target endpoint URL of the different server

    # Send the request to the target endpoint on the different server
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(response.api, json={"location": response.location})
            res.raise_for_status()  # Raise an exception for 4xx/5xx responses
            return res.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
