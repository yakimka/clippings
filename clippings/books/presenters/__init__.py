from jinja2 import Environment, PackageLoader, StrictUndefined

jinja_env = Environment(
    loader=PackageLoader(__name__, "templates"),
    undefined=StrictUndefined,
    autoescape=True,
)
