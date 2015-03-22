import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
 
class Companies(Base):
    __tablename__ = 'companies'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'         : self.id,
       }
 
class Models(Base):
    __tablename__ = 'models'


    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    wheel_size = Column(String(250))
    price = Column(String(8))
    company_id = Column(Integer,ForeignKey('companies.id'))
    company = relationship(Companies) 

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'description'         : self.description,
           'id'         : self.id,
           'price'         : self.price,
           'wheel_size'         : self.wheel_size,
       }
 

engine = create_engine('sqlite:///bikecatalog.db')
 

Base.metadata.create_all(engine)
