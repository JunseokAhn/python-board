from functools import wraps
from main import session, redirect, request, url_for

def login_required(f):
    @wraps(f)
    def decoreated_function(*args, **kwargs):
        if session.get("id") is None or session.get("id") == "":
            return redirect(url_for("member_login", next_url=request.url))
        return f(*args, **kwargs)
    return decoreated_function