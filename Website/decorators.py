from django.shortcuts import redirect
from django.conf import settings

def user_passes_test(test_func=None, login_url=None):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.session):
                return view_func(request, *args, **kwargs)
            return redirect(login_url)
        return _wrapped_view
    return decorator

def user_passes_test2(test_func=None, *sessions_name):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.session):
                for name in sessions_name[0]:
                    if request.session.get(name):
                        print('remove')
                        del request.session[name]
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def user_passes_test3(db, test_func=None, login_url=None):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(db, request.session):
                return view_func(request, *args, **kwargs)
            return redirect(login_url)
        return _wrapped_view
    return decorator


def login_session_required(test_func=None, login_url=None):
    actual_decorator = user_passes_test(
        lambda session: session.get('Email'),
        login_url=login_url
        )
    if test_func:
        return actual_decorator(test_func)
    return actual_decorator

def no_access_for_login(test_func=None, login_url=None):
    actual_decorator = user_passes_test(
        lambda session: not session.get('Email'),
        login_url=login_url
        )
    if test_func:
        return actual_decorator(test_func)
    return actual_decorator

def no_cart_access(db, test_func=None, login_url=None):
    actual_decorator = user_passes_test3(
        db,
        test_func=lambda db, session: db.collection('users').document(session['Email']).get().to_dict()['cart'],
        login_url=login_url
        )
    
    if test_func:
        return actual_decorator(test_func)
    return actual_decorator

def verify_mode_required(test_func=None, login_url=None):
    actual_decorator = user_passes_test(
        lambda session: session.get('verify'),
        login_url=login_url
        )
    if test_func:
        return actual_decorator(test_func)
    return actual_decorator

def refresh_session(test_func=None, *sessions_name):
    actual_decorator = user_passes_test2(
        lambda session: True,
        sessions_name
        )

    if test_func:
        return actual_decorator(test_func)
    return actual_decorator