from customers.models import  Customer, Address, Email, Phone, DBSession
from formencode import validators
from formencode.schema import Schema
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from sqlalchemy.exc import IntegrityError
from webhelpers import paginate
from webhelpers.paginate import Page
import logging
import transaction

log = logging.getLogger(__name__)

class CustomerForm(Schema):
    """ customer form schema for validation
        TODO: DRY code, sqlalchemy model validation instead?
    """
    filter_extra_fields = True
    allow_extra_fields = True
    first_name = validators.String()
    middle_name = validators.String()
    last_name = validators.String()

class LocationForm(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    city = validators.String()
    street = validators.String()
    state = validators.String()
    zip = validators.String()
    updated_at = validators.String()
    
class EmailForm(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    emailAddress = validators.String()

class PhoneForm(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    phoneNumber = validators.String()
    
class OrderForm(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    date_received = validators.DateValidator()
    date_delievered = validators.DateValidator()
    total_cost = validators.String()
        

@view_config(route_name="customer_list")
def list(request):
    """customers list """
    search = request.params.get("search", "")
        
    sort= "first_name"
    if request.GET.get("sort") and request.GET.get("sort") in \
            ["contact_first_name", "contact_last_name"]:
        sort = request.GET.get("sort")
        
    
    direction = "asc"
    if request.GET.get("direction") and request.GET.get("direction") in ["asc", "desc"]:
        direction = request.GET.get("direction")

    # db query     
    dbsession = DBSession()
    query = dbsession.query(Customer).\
        filter(Customer.first_name.like(search + "%")).\
                   order_by(sort + " " + direction)
    
    # paginate
    page_url = paginate.PageURL_WebOb(request)
    customers = Page(query, 
                     page=int(request.params.get("page", 1)), 
                     items_per_page=30, 
                     url=page_url)
        
    if "partial" in request.params:
        # Render the partial list page
        return render_to_response("customer/listPartial.html",
                                  {"customers": customers},
                                  request=request)
    else:
        # Render the full list page
        return render_to_response("customer/list.html",
                                  {"customers": customers},
                                  request=request)


@view_config(route_name="customer_search")
def search(request):
    """customers list searching """
    sort = request.GET.get("sort") if request.GET.get("sort") else "first_name" 
    direction = "desc" if request.GET.get("direction") == "asc" else "asc" 
    query = {"sort": sort, "direction": direction}
    
    return HTTPFound(location = request.route_url("customer_list", _query=query))

@view_config(route_name="customer_new", renderer="customer/new.html")
def new(request):
    """new customer """
    #categories = get_categories()
    #countries = get_countries()
    
    generalForm = Form(request, schema=CustomerForm)
    locationForm = Form(request, schema=LocationForm)    
    if "form_submitted" in request.POST and generalForm.validate():
        dbsession = DBSession()
        customer = generalForm.bind(Customer())
        dbsession.add(customer)
        request.session.flash("warning;New Customer is saved!")
        return HTTPFound(location = request.route_url("customer_list"))
    
    if "location_submitted" in request.POST and locationForm.validate():
        dbsession = DBSession()
        location = locationForm.bind(Address())
        dbsession.add(location)
        request.session.flash("warning;Customer Address is saved!")
        
    return dict(generalForm=FormRenderer(generalForm), 
                action_url=request.route_url("customer_new"))

@view_config(route_name="customer_edit", renderer="customer/edit.html")
def edit(request):
    """customer edit """
    id = request.matchdict['id']
    dbsession = DBSession()
    customer = dbsession.query(Customer).filter_by(id=id).one()
    print customer
    address = dbsession.query(Address).filter_by(user_id=id).one()
    
    
    if customer is None or address is None:
        request.session.flash("error;Customer not found!")
        return HTTPFound(location=request.route_url("customer_list"))        
    

    generalForm = Form(request, schema=CustomerForm, obj=customer)
    locationForm = Form(request, schema=LocationForm, obj=address)
       
    if "general_submitted" in request.POST and generalForm.validate():
        generalForm.bind(customer)
        dbsession.add(customer)
        request.session.flash("success; Successful call to update customer")
    if "location_submitted" in request.POST:
        locationForm.bind(address)
        dbsession.add(address)
        request.session.flash("success; Successful call to update location")
        


    action_url = request.route_url("customer_edit", id=id)
    return dict(generalForm=FormRenderer(generalForm),
                locationForm=FormRenderer(locationForm), 
                action_url=action_url)

@view_config(route_name="customer_delete")
def delete(request):
    """customer delete """
    id = request.matchdict['id']
    dbsession = DBSession()
    customer = dbsession.query(Customer).filter_by(id=id).first()
    address = dbsession.query(Address).filter_by(user_id=id).first()
    emails = dbsession.query(Email).filter_by(user_id=id).first()
    phones = dbsession.query(Phone).filter_by(user_id=id).first()
    
    if customer is None:
        request.session.flash("error;Customer not found!")
        return HTTPFound(location=request.route_url("customer_list"))        
    
    try:
        transaction.begin()
        dbsession.delete(customer)
        dbsession.delete(address)
        dbsession.delete(emails)
        dbsession.delete(phones)
        transaction.commit()
        request.session.flash("warning;The customer is deleted!")
    except IntegrityError:
        # delete error
        transaction.abort()
        request.session.flash("error;The customer could not be deleted!")
    
    return HTTPFound(location=request.route_url("customer_list"))

#def get_countries():
#    """Gets all countires with id, name value pairs """
#    dbsession = DBSession()
#    countries_q = dbsession.query(Country).order_by(Country.name)
#    countries = [(country.id, country.name) for country in countries_q.all()]
#    
#    return countries

#def get_categories():
#    """Gets all categories with id name value pairs """
#    dbsession = DBSession()
#    categories_q = dbsession.query(Category).order_by(Category.name)
#    categories = [(category.id, category.name) for category in categories_q.all()]
#    
#    return categories
