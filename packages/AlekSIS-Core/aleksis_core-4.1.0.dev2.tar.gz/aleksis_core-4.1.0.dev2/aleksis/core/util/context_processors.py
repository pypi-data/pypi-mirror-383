from maintenance_mode.http import (
    _need_maintenance_from_url,
    _need_maintenance_ignore_admin_site,
    _need_maintenance_ignore_ip_addresses,
    _need_maintenance_ignore_tests,
    _need_maintenance_ignore_urls,
    _need_maintenance_ignore_users,
    _need_maintenance_redirects,
    get_maintenance_mode,
)


def need_maintenance_response(request):
    """
    Tells if the given request needs a maintenance response or not.
    """

    value = get_maintenance_mode()
    if not value:
        return value

    value = _need_maintenance_from_url(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_users(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_admin_site(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_tests(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_ip_addresses(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_urls(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_redirects(request)
    if isinstance(value, bool):
        return value

    return True


def need_maintenance_response_context_processor(request):
    return {"need_maintenance_response": need_maintenance_response(request)}
