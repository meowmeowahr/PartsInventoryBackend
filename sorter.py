from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from models import Base, Location, Sorter, Part
import json
from typing import List, Dict, Optional


class SorterIdInvalidException(Exception):
    pass


class PartSorter:
    def __init__(self, database_url: str = "sqlite:///partsdb.sqlite"):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def create_tables(self):
        """Create tables using SQLAlchemy models (use alembic upgrade instead)"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Tables created using SQLAlchemy models")

    # Location methods
    def create_location(self, uid: str, name: str, icon: str, tags: str, attributes: dict):
        with self.get_session() as session:
            if session.query(Location).filter(Location.id == uid).first():
                raise SorterIdInvalidException(f"Another location with id: {uid} already exists")
            
            location = Location(
                id=uid,
                name=name,
                icon=icon,
                tags=tags,
                attrs=json.dumps(attributes)
            )
            session.add(location)
            session.commit()
            logger.info(f"Created new location with id: {uid}")

    def delete_location(self, uid: str):
        with self.get_session() as session:
            location = session.query(Location).filter(Location.id == uid).first()
            if not location:
                raise SorterIdInvalidException(f"Location with id: {uid} does not exist")
            
            session.delete(location)
            session.commit()
            logger.info(f"Deleted location with id: {uid}")

    def get_locations(self) -> List[Dict]:
        try:
            with self.get_session() as session:
                locations = session.query(Location).all()
                result = []
                for location in locations:
                    location_dict = {
                        'id': location.id,
                        'name': location.name,
                        'icon': location.icon,
                        'tags': location.tags,
                        'attrs': location.attributes
                    }
                    result.append(location_dict)
                return result
        except SQLAlchemyError as e:
            logger.error(f"Experienced error getting locations, returning empty list: {repr(e)}")
            return []

    def get_location_ids(self) -> List[str]:
        try:
            with self.get_session() as session:
                location_ids = session.query(Location.id).all()
                return [lid[0] for lid in location_ids]
        except SQLAlchemyError as e:
            logger.error(f"Experienced error getting location ids, returning empty list: {repr(e)}")
            return []

    def update_location(
        self,
        uid: str,
        name: str | None = None,
        icon: str | None = None,
        tags: str | None = None,
        attributes: dict | None = None,
    ):
        with self.get_session() as session:
            location = session.query(Location).filter(Location.id == uid).first()
            if not location:
                raise SorterIdInvalidException(f"Location with id: {uid} does not exist")
            
            if name is not None:
                location.name = name
            if icon is not None:
                location.icon = icon
            if tags is not None:
                location.tags = tags
            if attributes is not None:
                location.attrs = json.dumps(attributes)
            
            session.commit()
            logger.info(f"Updated location with id: {uid}")

    # Sorter methods
    def create_sorter(
        self, uid: str, location: str, name: str, icon: str, tags: str, attributes: dict
    ):
        with self.get_session() as session:
            if not session.query(Location).filter(Location.id == location).first():
                raise SorterIdInvalidException(
                    f"Location ID: {location} not in locations"
                )

            if session.query(Sorter).filter(Sorter.id == uid).first():
                raise SorterIdInvalidException(f"Sorter ID: {uid} already exists")

            sorter = Sorter(
                id=uid,
                location=location,
                name=name,
                icon=icon,
                tags=tags,
                attrs=json.dumps(attributes)
            )
            session.add(sorter)
            session.commit()
            logger.info(f"Created new sorter with id: {uid}")

    def delete_sorter(self, uid: str):
        with self.get_session() as session:
            sorter = session.query(Sorter).filter(Sorter.id == uid).first()
            if not sorter:
                raise SorterIdInvalidException(f"Sorter with id: {uid} does not exist")
            
            session.delete(sorter)
            session.commit()
            logger.info(f"Deleted sorter with id: {uid}")

    def get_sorters(self) -> List[Dict]:
        try:
            with self.get_session() as session:
                sorters = session.query(Sorter).all()
                result = []
                for sorter in sorters:
                    sorter_dict = {
                        'id': sorter.id,
                        'location': sorter.location,
                        'name': sorter.name,
                        'icon': sorter.icon,
                        'tags': sorter.tags,
                        'attrs': sorter.attributes
                    }
                    result.append(sorter_dict)
                return result
        except SQLAlchemyError as e:
            logger.error(f"Experienced error getting sorters, returning empty list: {repr(e)}")
            return []

    def get_sorter_ids(self) -> List[str]:
        try:
            with self.get_session() as session:
                sorter_ids = session.query(Sorter.id).all()
                return [sid[0] for sid in sorter_ids]
        except SQLAlchemyError as e:
            logger.error(f"Experienced error getting sorter ids, returning empty list: {repr(e)}")
            return []

    def update_sorter(
        self,
        uid: str,
        location: str | None = None,
        name: str | None = None,
        icon: str | None = None,
        tags: str | None = None,
        attributes: dict | None = None,
    ):
        with self.get_session() as session:
            sorter = session.query(Sorter).filter(Sorter.id == uid).first()
            if not sorter:
                raise SorterIdInvalidException(f"Sorter with id: {uid} does not exist")
            
            if location is not None:
                sorter.location = location
            if name is not None:
                sorter.name = name
            if icon is not None:
                sorter.icon = icon
            if tags is not None:
                sorter.tags = tags
            if attributes is not None:
                sorter.attrs = json.dumps(attributes)
            
            session.commit()
            logger.info(f"Updated sorter with id: {uid}")

    # Part methods
    def create_part(
        self,
        uid: str,
        sorter: str,
        name: str,
        quantity: int,
        quantity_type: str,
        enable_quantity: bool,
        tags: str,
        price: float,
        notes: str,
        location: str,
        attributes: dict,
    ):
        with self.get_session() as session:
            if not session.query(Sorter).filter(Sorter.id == sorter).first():
                raise SorterIdInvalidException(f"Sorter ID: {sorter} not found")

            if session.query(Part).filter(Part.id == uid).first():
                raise SorterIdInvalidException(f"Part ID: {uid} already exists")

            part = Part(
                id=uid,
                sorter=sorter,
                name=name,
                tags=tags,
                quantity=quantity,
                quantity_type=quantity_type,
                enable_quantity=enable_quantity,
                price=price,
                notes=notes,
                location=location,
                attrs=json.dumps(attributes)
            )
            session.add(part)
            session.commit()
            logger.info(f"Created new part with id: {uid}")

    def set_part_image(self, uid: str, image: str | None):
        with self.get_session() as session:
            part = session.query(Part).filter(Part.id == uid).first()
            if not part:
                raise SorterIdInvalidException(f"Part with id: {uid} does not exist")
            
            part.image = image
            session.commit()
            logger.info(f"Updated image for part with id: {uid}")

    def delete_part(self, uid: str):
        with self.get_session() as session:
            part = session.query(Part).filter(Part.id == uid).first()
            if not part:
                raise SorterIdInvalidException(f"Part with id: {uid} does not exist")
            
            session.delete(part)
            session.commit()
            logger.info(f"Deleted part with id: {uid}")

    def get_parts(self) -> List[Dict]:
        try:
            with self.get_session() as session:
                parts = session.query(Part).all()
                result = []
                for part in parts:
                    part_dict = {
                        'id': part.id,
                        'sorter': part.sorter,
                        'name': part.name,
                        'image': part.image,
                        'image_hash': part.image_hash,
                        'tags': part.tags,
                        'quantity': part.quantity,
                        'quantity_type': part.quantity_type,
                        'enable_quantity': part.enable_quantity,
                        'price': float(part.price) if part.price else 0.0,
                        'notes': part.notes,
                        'location': part.location,
                        'created_at': part.created_at,
                        'updated_at': part.updated_at,
                        'attrs': part.attributes
                    }
                    result.append(part_dict)
                return result
        except SQLAlchemyError as e:
            logger.error(f"Experienced error getting parts, returning empty list: {repr(e)}")
            return []

    def get_part_ids(self) -> List[str]:
        try:
            with self.get_session() as session:
                part_ids = session.query(Part.id).all()
                return [pid[0] for pid in part_ids]
        except SQLAlchemyError as e:
            logger.error(f"Experienced error getting part ids, returning empty list: {repr(e)}")
            return []

    def update_part(
        self,
        uid: str,
        sorter: str | None = None,
        name: str | None = None,
        quantity: int | None = None,
        quantity_type: str | None = None,
        enable_quantity: bool | None = None,
        tags: str | None = None,
        price: float | None = None,
        notes: str | None = None,
        location: str | None = None,
        attributes: dict | None = None,
    ):
        with self.get_session() as session:
            part = session.query(Part).filter(Part.id == uid).first()
            if not part:
                raise SorterIdInvalidException(f"Part with id: {uid} does not exist")
            
            if sorter is not None:
                part.sorter = sorter
            if name is not None:
                part.name = name
            if quantity is not None:
                part.quantity = quantity
            if quantity_type is not None:
                part.quantity_type = quantity_type
            if enable_quantity is not None:
                part.enable_quantity = enable_quantity
            if tags is not None:
                part.tags = tags
            if price is not None:
                part.price = price
            if notes is not None:
                part.notes = notes
            if location is not None:
                part.location = location
            if attributes is not None:
                part.attrs = json.dumps(attributes)
            
            session.commit()
            logger.info(f"Updated part with id: {uid}")