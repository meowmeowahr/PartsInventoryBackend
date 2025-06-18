from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, LargeBinary, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import json

Base = declarative_base()

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    tags = Column(String)
    attrs = Column(Text, nullable=False)
    
    # Relationships
    sorters = relationship("Sorter", back_populates="location_ref", cascade="all, delete-orphan")
    parts = relationship("Part", back_populates="location_ref")
    
    @property
    def attributes(self):
        if isinstance(self.attrs, str):
            try:
                return json.loads(self.attrs)
            except json.JSONDecodeError:
                return {}
        return self.attrs or {}
    
    @attributes.setter
    def attributes(self, value):
        self.attrs = json.dumps(value) if value else "{}"

class Sorter(Base):
    __tablename__ = 'sorters'
    
    id = Column(String, primary_key=True)
    location = Column(String, ForeignKey('locations.id'), nullable=False)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    tags = Column(String)
    attrs = Column(Text, nullable=False)
    
    # Relationships
    location_ref = relationship("Location", back_populates="sorters")
    parts = relationship("Part", back_populates="sorter_ref", cascade="all, delete-orphan")
    
    @property
    def attributes(self):
        if isinstance(self.attrs, str):
            try:
                return json.loads(self.attrs)
            except json.JSONDecodeError:
                return {}
        return self.attrs or {}
    
    @attributes.setter
    def attributes(self, value):
        self.attrs = json.dumps(value) if value else "{}"

class Part(Base):
    __tablename__ = 'parts'
    
    id = Column(String, primary_key=True)
    sorter = Column(String, ForeignKey('sorters.id'), nullable=False)
    name = Column(String, nullable=False)
    image = Column(LargeBinary)
    image_hash = Column(LargeBinary)
    tags = Column(String, nullable=False, default='')
    quantity = Column(Integer, nullable=False)
    quantity_type = Column(String, nullable=False, default='pcs')
    enable_quantity = Column(Boolean, nullable=False, default=True)
    price = Column(Float(precision=10), nullable=False, default=0.00)
    notes = Column(Text)
    location = Column(String, ForeignKey('locations.id'), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    attrs = Column(Text, nullable=False)
    
    # Relationships
    sorter_ref = relationship("Sorter", back_populates="parts")
    location_ref = relationship("Location", back_populates="parts")
    
    @property
    def attributes(self):
        if isinstance(self.attrs, str):
            try:
                return json.loads(self.attrs)
            except json.JSONDecodeError:
                return {}
        return self.attrs or {}
    
    @attributes.setter
    def attributes(self, value):
        self.attrs = json.dumps(value) if value else "{}"