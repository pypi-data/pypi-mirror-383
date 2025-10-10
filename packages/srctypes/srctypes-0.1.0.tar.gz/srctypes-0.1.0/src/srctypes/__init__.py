try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

source_code = Annotated[str, "source_code"]

css = Annotated[source_code, "css"]
scss = Annotated[source_code, "scss"]
sass = Annotated[source_code, "sass"]
less = Annotated[source_code, "less"]
stylus = Annotated[source_code, "stylus"]

js = Annotated[source_code, "js"]
ts = Annotated[source_code, "ts"]

sql = Annotated[source_code, "sql"]
mysql = Annotated[source_code, "mysql"]
pgsql = Annotated[source_code, "pgsql"]
sqlite = Annotated[source_code, "sqlite"]
jinja2_sql = Annotated[source_code, "jinja2_sql"]
django_sql = Annotated[source_code, "django_sql"]

json = Annotated[source_code, "json"]
yaml = Annotated[source_code, "yaml"]
toml = Annotated[source_code, "toml"]
ini = Annotated[source_code, "ini"]
xml = Annotated[source_code, "xml"]

html = Annotated[source_code, "html"]
django = Annotated[source_code, "django"]
jinja = Annotated[source_code, "jinja"]
