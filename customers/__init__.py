from customers.models import initialize_sql
from customers.utils.subscribers import add_renderer_globals
from customers.utils.subscribers import csrf_validation
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.events import NewRequest
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config
# from pyramid.session import UnencryptedCookieSessionFactoryConfig

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, "sqlalchemy.")
    initialize_sql(engine)
    
    # default session factory, not secure, use pyramid beaker
    # session_factory = UnencryptedCookieSessionFactoryConfig("mysession")
    
    # pyramid_beaker add-on
    session_factory = session_factory_from_settings(settings)
    
    config = Configurator(
        settings=settings, 
        session_factory=session_factory
    )
    
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(csrf_validation, NewRequest)    
    
    
    # mako settings for file extension .html
    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")

    config.add_static_view("static", "customers:static", cache_max_age=3600)
    
    # home 
    config.add_route("home", "/")
    config.add_route("home_dashboard", "/home/dashboard")
    
    # country routes
    config.add_route("country_list", "/countries/list")
    config.add_route("country_search", "/countries/search")
    config.add_route("country_new", "/countries/new")
    config.add_route("country_edit", "/countries/{id}/edit")
    config.add_route("country_delete", "/countries/{id}/delete")
    
    # category routes
    config.add_route("category_list", "/categories/list")
    config.add_route("category_search", "/categories/search")
    config.add_route("category_new", "/categories/new")
    config.add_route("category_edit", "/categories/{id}/edit")
    config.add_route("category_delete", "/categories/{id}/delete")
    
    # customer routes
    config.add_route("customer_list", "/customers/list")
    config.add_route("customer_search", "/customers/search")
    config.add_route("customer_new", "/customers/new")
    config.add_route("customer_edit", "/customers/{id}/edit")
    config.add_route("customer_delete", "/customers/{id}/delete")
    
    config.scan()
    return config.make_wsgi_app()
