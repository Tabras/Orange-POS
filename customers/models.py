"""
db entites, mappers and db table settings
cem ikta, www.devsniper.com
"""
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.types import DateTime
from sqlalchemy.types import String
from zope.sqlalchemy import ZopeTransactionExtension
import transaction

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class BaseExtension(MapperExtension):  
    """Base entension class for all entities """  
  
    def before_insert(self, mapper, connection, instance):  
        """ set the created_at  """  
        instance.created_at = datetime.now()  
  
    def before_update(self, mapper, connection, instance):  
        """ set the updated_at  """  
        instance.updated_at = datetime.now()
        

class BaseEntity(object):  

    __mapper_args__ = { 'extension': BaseExtension() }
    __table_args__ = {
        'sqlite_autoincrement': True,
    }  
    # for before insert before update base extension class 
    created_at = Column(DateTime())
    updated_at = Column(DateTime())



        
class Customer(Base, BaseEntity):
    """Customer entity class """
    __tablename__ = 'users'
    
    id = Column(Integer(), primary_key=True)
    first_name = Column(String(50)) 
    middle_name = Column(String(50))
    last_name = Column(String(50))
    

    
      
    def __init__(self,first_name, middle_name, last_name):
        self.firstName = first_name
        self.middle_name = middle_name
        self.lastName  = last_name
       
    def getFullName(self):
        return self.first_name + " " + self.last_name



def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    

class Address(Base, BaseEntity):
	"""Address Entity Class """
	__tablename__ = 'addresses'
	
	id = Column(Integer(), primary_key=True)
	user_id = Column(Integer())
	city = Column(String)
	zip_code = Column(String)
	state = Column(String(2))
	street = Column(String)
	
	def __init__(self, user_id, city, zip_code, state, street):
		self.user_id = user_id
		self.city = city
		self.zip_code = zip_code
		self.state = state
		self.street = street
		
	def assembleAddress(self):
		if self.street:
			return self.street + " " + self.city + ", " + self.state + " " +\
			self.zip_code
		else:
			return self.city + ", " + self.state + " " + self.zip_code
		
class Email(Base, BaseEntity):
	__tablename__ = 'emails'
	
	id = Column(Integer(), primary_key=True)
	user_id = Column(Integer())
	email = Column(String())
	email_type = Column(String())
	
	def __init__(self, user_id, email, email_type):
		self.user_id = user_id
		self.email = email
		self.email_type = email_type
	
class Phone(Base, BaseEntity):
	__tablename__ = 'phones'
	
	id = Column(Integer(), primary_key=True)
	user_id = Column(Integer())
	phone_type = Column(String())
	number = Column(String())
	
	def __init__(self, user_id, phone_type, number):
		self.user_id = user_id
		self.phone_type = phone_type
		self.number = number
	
	def assemblePhone():
		return phone_type + " Phone: " + number
		
class State(Base):
	__tablename__ = 'states'
	
	state_name = Column(String(), primary_key=True)
	state_code = Column(String(2))
	
	def __init__(self, state_name, state_code):
		self.state_name = state_name
		self.state_code = state_code
	
class Service(Base, BaseEntity):
	__tablename__ = 'services'
	
	id = Column(Integer(), primary_key=True)
	name = Column(String())
	description = Column(String())
	price = Column(Integer())
	service_type = Column(String())
	
	def __init__(self, name, description, price, service_type):
		self.name = name
		self.description = description
		self.price = price
		self.service_type = service_type
		
class Item(Base, BaseEntity):
	__tablename__ = 'items'
	
	id = Column(Integer(), primary_key=True)
	name = Column(String())
	description = Column(String())
	price = Column(Integer())
	stock = Column(Integer())
	
	def __init__(self, name, description, price, stock):
		self.name = name
		self.description = description
		self.price = price
		self.stock = stock
		
class Receipt(Base, BaseEntity):
	__tablename__ = 'receipts'
	
	id = Column(Integer(), primary_key=True)
	user_id = Column(Integer())
	date_received = Column(DateTime())
	date_delievered = Column(DateTime())
	total_cost = Column(Integer())
	discount = Column(Integer())
	
	def __init__(self, user_id, date_received, date_delievered, total_cost, discount):
		self.user_id = user_id
		self.date_received = date_received
		self.date_delievered = date_delievered
		self.total_cost = total_cost
		self.discount = discount
	
class CustomServiceOrder(Base, BaseEntity):
	__tablename__ = 'customserviceorders'
	
	id = Column(Integer(), primary_key=True)
	name = Column(String())
	description = Column(String())
	price = Column(Integer())
	receipt_id = Column(Integer())
	
	def __init__(self, name, description, price, receipt_id):
		self.name = name
		self.description = description
		self.price = price
		self.receipt_id = receipt_id
		
class CustomItemOrder(Base, BaseEntity):
	__tablename__ = 'customitemorders'
	
	id = Column(Integer(), primary_key=True)
	name = Column(String())
	description = Column(String())
	price = Column(Integer())
	receipt_id = Column(Integer())
	
	def __init__(self, name, description, price, receipt_id):
		self.name = name
		self.description = description
		self.price = price
		self.receipt_id = receipt_id
		
class ItemOrder(Base, BaseEntity):
	__tablename__ = 'itemorders'
	
	id = Column(Integer(), primary_key=True)
	receipt_id = Column(Integer())
	item_id = Column(Integer())
	quantity = Column(Integer())
	cost = Column(Integer())
	
	def __init__(self, receipt_id, item_id, quantity, cost):
		self.receipt_id = receipt_id
		self.item_id = item_id
		self.quantity = quantity
		self.cost = cost
		
class ServiceOrder(Base, BaseEntity):
	__tablename__ = 'serviceorders'
	
	id = Column(Integer(), primary_key=True)
	receipt_id = Column(Integer())
	service_id = Column(Integer())
	quantity = Column(Integer())
	cost = Column(Integer())
	
	def __init__(self, receipt_id, service_id, quantity, cost):
		self.receipt_id = receipt_id
		self.service_id = service_id
		self.quantity = quantity
		self.cost = cost
		


	
		
