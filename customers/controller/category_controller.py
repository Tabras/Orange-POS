from customers.models import Category
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

class CategoryForm(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    name = validators.String(not_empty=True)

@view_config(route_name="category_list", renderer="category/list.html")
def list(request):
    """categories list """
    search = request.params.get("search", "")
        
    sort= "name"
    if request.GET.get("sort") and request.GET.get("sort") == "name":
        sort = request.GET.get("sort")
    
    direction = "asc"
    if request.GET.get("direction") and request.GET.get("direction") in ["asc", "desc"]:
        direction = request.GET.get("direction")
     
    # db query     
    dbsession = DBSession()
    query = dbsession.query(Category).\
        filter(Category.name.like(search + "%")).\
        order_by(sort + " " + direction)

    # paginate
    page_url = paginate.PageURL_WebOb(request)
    categories = Page(query, 
                     page=int(request.params.get("page", 1)), 
                     items_per_page=10, 
                     url=page_url)

    return {"categories": categories}

@view_config(route_name="category_search")
def search(request):
    """categories list searching """
    sort = request.GET.get("sort") if request.GET.get("sort") else "name" 
    direction = "desc" if request.GET.get("direction") == "asc" else "asc" 
    query = {"sort": sort, "direction": direction}
    
    return HTTPFound(location=request.route_url("category_list", _query=query))

@view_config(route_name="category_new", renderer="category/new.html")
def new(request):
    """new country """
    form = Form(request, schema=CategoryForm)    
    if "form_submitted" in request.POST and form.validate():
        dbsession = DBSession()
        category = form.bind(Category())
        # TODO: db error control?
        dbsession.add(category)
        request.session.flash("warning;New Category is saved!")
        return HTTPFound(location = request.route_url("category_list"))
        
    return dict(form=FormRenderer(form), 
                action_url=request.route_url("category_new"))

@view_config(route_name="category_edit", renderer="category/edit.html")
def edit(request):
    """category edit """
    id = request.matchdict['id']
    dbsession = DBSession()
    category = dbsession.query(Category).filter_by(id=id).one()
    if category is None:
        request.session.flash("error;Category not found!")
        return HTTPFound(location=request.route_url("category_list"))        
    

    form = Form(request, schema=CategoryForm, obj=category)    
    if "form_submitted" in request.POST and form.validate():
        form.bind(category)
        dbsession.add(category)
        request.session.flash("warning;The Category is saved!")
        return HTTPFound(location = request.route_url("category_list"))

    action_url = request.route_url("category_edit", id=id)
    return dict(form=FormRenderer(form), 
                action_url=action_url)
    
@view_config(route_name="category_delete")
def delete(request):
    """category delete """
    id = request.matchdict['id']
    dbsession = DBSession()
    category = dbsession.query(Category).filter_by(id=id).first()
    if category is None:
        request.session.flash("error;Category not found!")
        return HTTPFound(location=request.route_url("category_list"))        
    
    try:
        transaction.begin()
        dbsession.delete(category);
        transaction.commit()
        request.session.flash("warning;The category is deleted!")
    except IntegrityError:
        # delete error
        transaction.abort()
        request.session.flash("error;The category could not be deleted!")
    
    return HTTPFound(location=request.route_url("category_list"))
