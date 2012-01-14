from customers.models import Country, DBSession
from formencode import validators
from formencode.schema import Schema
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import or_
from webhelpers import paginate
from webhelpers.paginate import Page
import logging
import transaction

log = logging.getLogger(__name__)

class CountryForm(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    code = validators.MaxLength(2, not_empty=True)  
    name = validators.String(not_empty=True)    

@view_config(route_name="country_list")
def list(request):
    """countries list """
    search = request.params.get("search", "")
        
    sort= "code"
    if request.GET.get("sort") and request.GET.get("sort") in ["code", "name"]:
        sort = request.GET.get("sort")
    
    direction = "asc"
    if request.GET.get("direction") and request.GET.get("direction") in ["asc", "desc"]:
        direction = request.GET.get("direction")
     
    # db query     
    dbsession = DBSession()
    query = dbsession.query(Country).\
        filter(or_(Country.code.like(search + "%"), 
                   Country.name.like(search + "%"))).\
                   order_by(sort + " " + direction)
    
    # paginate
    page_url = paginate.PageURL_WebOb(request)
    countries = Page(query, 
                     page=int(request.params.get("page", 1)), 
                     items_per_page=10, 
                     url=page_url)
    
    if "partial" in request.params:
        # Render the partial list page
        return render_to_response("country/listPartial.html",
                                  {"countries": countries},
                                  request=request)
    else:
        # Render the full list page
        return render_to_response("country/list.html",
                                  {"countries": countries},
                                  request=request)

@view_config(route_name="country_search")
def search(request):
    """countries list searching """
    sort = request.GET.get("sort") if request.GET.get("sort") else "code" 
    direction = "desc" if request.GET.get("direction") == "asc" else "asc" 
    query = {"sort": sort, "direction": direction}
    
    return HTTPFound(location = request.route_url("country_list", _query=query))

@view_config(route_name="country_new", renderer="country/new.html")
def new(request):
    """new country """
    form = Form(request, schema=CountryForm)    
    if "form_submitted" in request.POST and form.validate():
        dbsession = DBSession()
        country = form.bind(Country())
        # TODO: db error control?
        dbsession.add(country)
        request.session.flash("warning;New Country is saved!")
        return HTTPFound(location = request.route_url("country_list"))
        
    return dict(form=FormRenderer(form), 
                action_url=request.route_url("country_new"))

@view_config(route_name="country_edit", renderer="country/edit.html")
def edit(request):
    """country edit """
    id = request.matchdict['id']
    dbsession = DBSession()
    country = dbsession.query(Country).filter_by(id=id).one()
    if country is None:
        request.session.flash("error;Country not found!")
        return HTTPFound(location=request.route_url("country_list"))        
    

    form = Form(request, schema=CountryForm, obj=country)    
    if "form_submitted" in request.POST and form.validate():
        form.bind(country)
        dbsession.add(country)
        request.session.flash("warning;The Country is saved!")
        return HTTPFound(location = request.route_url("country_list"))

    action_url = request.route_url("country_edit", id=id)
    return dict(form=FormRenderer(form), 
                action_url=action_url)

@view_config(route_name="country_delete")
def delete(request):
    """country delete """
    id = request.matchdict['id']
    dbsession = DBSession()
    country = dbsession.query(Country).filter_by(id=id).first()
    if country is None:
        request.session.flash("error;Country not found!")
        return HTTPFound(location=request.route_url("country_list"))        
    
    try:
        transaction.begin()
        dbsession.delete(country);
        transaction.commit()
        request.session.flash("warning;The country is deleted!")
    except IntegrityError:
        # delete error
        transaction.abort()
        request.session.flash("error;The country could not be deleted!")
    
    return HTTPFound(location=request.route_url("country_list"))
