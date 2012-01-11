"""
db entites, mappers and db table settings
cem ikta, www.devsniper.com
"""
from datetime import datetime
from sqlalchemy.dialects.mysql.base import TINYINT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import BIGINT
from sqlalchemy.types import DateTime
from sqlalchemy.types import TEXT
from sqlalchemy.types import Unicode
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
    __table_args__ = {
        'mysql_engine': 'InnoDB',  
        'mysql_charset': 'utf8'  
    }  
    # for before insert before update base extension class  
    __mapper_args__ = { 'extension': BaseExtension() }    


class Country(Base, BaseEntity):  
    """Country entity class """  
    __tablename__ = 'country'  
  
    id = Column('country_id', BIGINT(unsigned=True), primary_key=True)  
    code = Column(Unicode(10), nullable=False, unique=True)  
    name = Column(Unicode(100), nullable=False, unique=True)
    created_by_user = Column(Unicode(50))  
    created_at = Column(DateTime)  
    updated_by_user = Column(Unicode(50))  
    updated_at = Column(DateTime)  
  
    def __init__(self, code="", name=""):  
        self.code = code  
        self.name = name
        
class Category(Base, BaseEntity):
    """ Category entity class """
    __tablename__ = 'category'
    
    id = Column('category_id', BIGINT(unsigned=True), primary_key=True) 
    name = Column(Unicode(100), nullable=False, unique=True)
    created_by_user = Column(Unicode(50))  
    created_at = Column(DateTime)  
    updated_by_user = Column(Unicode(50))  
    updated_at = Column(DateTime)  
    
    def __init__(self, name=""):
        self.name = name
        
class Customer(Base, BaseEntity):
    """Customer entity class """
    __tablename__ = 'customer'
    
    id = Column('customer_id', BIGINT(unsigned=True), primary_key=True) 
    company_name = Column(Unicode(100), nullable=False, unique=True)
    # foreing key
    # nullable = false, the customer must have a category
    category_id = Column(BIGINT(unsigned=True), ForeignKey('category.category_id', 
        name="fk_customer_category", onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    category = relationship("Category", passive_deletes=True, passive_updates=True)
    contact_title = Column(Unicode(50))
    contact_first_name = Column(Unicode(50))
    contact_last_name = Column(Unicode(50))
    address = Column(TEXT)
    city = Column(Unicode(50))
    region = Column(Unicode(50))
    postal_code = Column(Unicode(50))
    # foreing key, nullable =  true 
    country_id = Column(BIGINT(unsigned=True), ForeignKey('country.country_id', 
        name='fk_customer_country', onupdate='CASCADE', ondelete='RESTRICT'), nullable=True)
    country = relationship("Country", passive_deletes=True, passive_updates=True)
    phone = Column(Unicode(50))
    fax = Column(Unicode(50))
    mobile = Column(Unicode(50))
    email = Column(Unicode(50))
    homepage = Column(Unicode(50))
    skype = Column(Unicode(50))
    notes = Column(TEXT)
    created_by_user = Column(Unicode(50))  
    created_at = Column(DateTime)  
    updated_by_user = Column(Unicode(50))  
    updated_at = Column(DateTime)  
    
    def __init__(self, company_name="", category_id=0, contact_title="",
                  contact_first_name="", contact_last_name="", address="",
                  city="", region="", postal_code="", country_id=0, phone="",
                  fax="", mobile="", email="", homepage="", skype="", active=True, 
                  notes=""):
        self.company_name = company_name
        self.category_id = category_id
        self.contact_title = contact_title
        self.contact_first_name = contact_first_name
        self.contact_last_name = contact_last_name
        self.address = address
        self.city = city
        self.region = region
        self.postal_code = postal_code
        self.country_id = country_id 
        self.phone = phone
        self.fax = fax
        self.mobile = mobile
        self.email = email
        self.homepage = homepage
        self.skype = skype
        self.active = active
        self.notes = notes


def populate():
    """add default data to tables """
    try:
        transaction.begin()
        dbsession = DBSession()
        dbsession.add_all([
                           Country("TR", "Turkey"), 
                           Country("DE", "Germany"), 
                           Country("GB", "England"),
                           Category("Discounter"),
                           Category("Reseller"),
                           Category("End user") 
                           ])
        transaction.commit()
    except IntegrityError:
        transaction.abort()
    

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    populate()
    
