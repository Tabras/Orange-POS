from customers.models import Category
from customers.models import Country
from customers.models import Customer
from customers.models import DBSession
from formencode import validators
from formencode.schema import Schema
from pyramid.httpexceptions import HTTPFound
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
    company_name = validators.String(not_empty=True)
    category_id = validators.Int()
    contact_title = validators.String()
    contact_first_name = validators.String(not_empty=True)
    contact_last_name = validators.String(not_empty=True)
    address = validators.String()
    city = validators.String()
    region = validators.String()
    postal_code = validators.String()
    country_id = validators.Int()
    phone = validators.String()
    fax = validators.String()
    mobile = validators.String()
    email = validators.String()
    homepage = validators.String()
    skype = validators.String()
    notes = validators.String()

@view_config(route_name="customer_list", renderer="customer/list.html")
def list(request):
    """customers list """
    search = request.params.get("search", "")
        
    sort= "company_name"
    if request.GET.get("sort") and request.GET.get("sort") in \
            ["company_name", "contact_first_name", "contact_last_name", "category"]:
        sort = request.GET.get("sort")
    if sort == "category":
        sort = "category.name"    
    
    direction = "asc"
    if request.GET.get("direction") and request.GET.get("direction") in ["asc", "desc"]:
        direction = request.GET.get("direction")

    # db query     
    dbsession = DBSession()
    query = dbsession.query(Customer).join(Category).\
        filter(Customer.company_name.like(search + "%")).\
                   order_by(sort + " " + direction)
    
    # paginate
    page_url = paginate.PageURL_WebOb(request)
    customers = Page(query, 
                     page=int(request.params.get("page", 1)), 
                     items_per_page=10, 
                     url=page_url)

    return {"customers": customers}

@view_config(route_name="customer_search")
def search(request):
    """customers list searching """
    sort = request.GET.get("sort") if request.GET.get("sort") else "company_name" 
    direction = "desc" if request.GET.get("direction") == "asc" else "asc" 
    query = {"sort": sort, "direction": direction}
    
    return HTTPFound(location = request.route_url("customer_list", _query=query))

@view_config(route_name="customer_new", renderer="customer/new.html")
def new(request):
    """new customer """
    categories = get_categories()
    countries = get_countries()
    
    form = Form(request, schema=CustomerForm)    
    if "form_submitted" in request.POST and form.validate():
        dbsession = DBSession()
        customer = form.bind(Customer())
        dbsession.add(customer)
        request.session.flash("warning;New Customer is saved!")
        return HTTPFound(location = request.route_url("customer_list"))
        
    return dict(form=FormRenderer(form),
                categories=categories, 
                countries=countries, 
                action_url=request.route_url("customer_new"))

@view_config(route_name="customer_edit", renderer="customer/edit.html")
def edit(request):
    """customer edit """
    id = request.matchdict['id']
    dbsession = DBSession()
    customer = dbsession.query(Customer).filter_by(id=id).one()
    if customer is None:
        request.session.flash("error;Customer not found!")
        return HTTPFound(location=request.route_url("customer_list"))        
    
    categories = get_categories()
    countries = get_countries()

    form = Form(request, schema=CustomerForm, obj=customer)    
    if "form_submitted" in request.POST and form.validate():
        form.bind(customer)
        dbsession.add(customer)
        request.session.flash("warning;The Customer is saved!")
        return HTTPFound(location = request.route_url("customer_list"))

    action_url = request.route_url("customer_edit", id=id)
    return dict(form=FormRenderer(form),
                categories=categories, 
                countries=countries, 
                action_url=action_url)

@view_config(route_name="customer_delete")
def delete(request):
    """customer delete """
    id = request.matchdict['id']
    dbsession = DBSession()
    customer = dbsession.query(Customer).filter_by(id=id).first()
    if customer is None:
        request.session.flash("error;Customer not found!")
        return HTTPFound(location=request.route_url("customer_list"))        
    
    try:
        transaction.begin()
        dbsession.delete(customer);
        transaction.commit()
        request.session.flash("warning;The customer is deleted!")
    except IntegrityError:
        # delete error
        transaction.abort()
        request.session.flash("error;The customer could not be deleted!")
    
    return HTTPFound(location=request.route_url("customer_list"))

def get_countries():
    """Gets all countires with id, name value pairs """
    dbsession = DBSession()
    countries_q = dbsession.query(Country).order_by(Country.name)
    countries = [(country.id, country.name) for country in countries_q.all()]
    
    return countries

def get_categories():
    """Gets all categories with id name value pairs """
    dbsession = DBSession()
    categories_q = dbsession.query(Category).order_by(Category.name)
    categories = [(category.id, category.name) for category in categories_q.all()]
    
    return categories
