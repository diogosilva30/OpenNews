# Fix for flask-testing bug. See: https://github.com/jarus/flask-testing/issues/143
import werkzeug

werkzeug.cached_property = werkzeug.utils.cached_property
