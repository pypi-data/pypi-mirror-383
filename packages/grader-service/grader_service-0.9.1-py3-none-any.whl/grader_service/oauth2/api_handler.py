"""Base API handlers"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
import warnings
from functools import lru_cache
from http.client import responses
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.exc import SQLAlchemyError
from tornado import web

from ..handlers.base_handler import BaseHandler
from ..utils import isoformat

PAGINATION_MEDIA_TYPE = "application/jupyterhub-pagination+json"


class APIHandler(BaseHandler):
    """Base class for API endpoints

    Differences from page handlers:

    - JSON responses and errors
    - strict content-security-policy
    - methods for REST API models
    """

    # accept token-based authentication for API requests
    _accept_token_auth = True

    @property
    def content_security_policy(self):
        return "; ".join([super().content_security_policy, "default-src 'none'"])

    def get_content_type(self):
        return "application/json"

    @property
    @lru_cache()
    def accepts_pagination(self):
        """Return whether the client accepts the pagination preview media type"""
        accept_header = self.request.headers.get("Accept", "")
        if not accept_header:
            return False
        accepts = {s.strip().lower() for s in accept_header.strip().split(",")}
        return PAGINATION_MEDIA_TYPE in accepts

    def check_referer(self):
        """DEPRECATED"""
        warnings.warn(
            "check_referer is deprecated in JupyterHub 3.2 and always returns True",
            DeprecationWarning,
            stacklevel=2,
        )
        return True

    def check_post_content_type(self):
        """Check request content-type, e.g. for cross-site POST requests

        Cross-site POST via form will include content-type
        """
        content_type = self.request.headers.get("Content-Type")
        if not content_type:
            # not specified, e.g. from a script
            return True

        # parse content type for application/json
        fields = content_type.lower().split(";")
        if not any(f.lstrip().startswith("application/json") for f in fields):
            self.log.warning(f"Not allowing POST with content-type: {content_type}")
            return False

        return True

    async def prepare(self):
        await super().prepare()
        # tornado only checks xsrf on non-GET
        # we also check xsrf on GETs to API endpoints
        # make sure this runs after auth, which happens in super().prepare()
        if self.request.method not in {"HEAD", "OPTIONS"} and self.settings.get("xsrf_cookies"):
            self.check_xsrf_cookie()

    def check_xsrf_cookie(self):
        if getattr(self, "_token_authenticated", False):
            # if token-authenticated, ignore XSRF
            return
        return super().check_xsrf_cookie()

    def get_current_user_cookie(self):
        """Extend get_user_cookie to add checks for CORS"""
        cookie_user = super().get_current_user_cookie()
        # CORS checks for cookie-authentication
        # check these only if there is a cookie user,
        # avoiding misleading "Blocking Cross Origin" messages
        # when there's no cookie set anyway.
        if cookie_user:
            if self.request.method.upper() == "POST" and not self.check_post_content_type():
                return None
        return cookie_user

    def get_json_body(self):
        """Return the body of the request as JSON data."""
        if not self.request.body:
            return None
        body = self.request.body.strip().decode("utf-8")
        try:
            model = json.loads(body)
        except Exception:
            self.log.debug("Bad JSON: %r", body)
            self.log.error("Couldn't parse JSON", exc_info=True)
            raise web.HTTPError(400, reason="Invalid JSON in body of request")
        return model

    def write_error(self, status_code, **kwargs):
        """Write JSON errors instead of HTML"""
        exc_info = kwargs.get("exc_info")
        message = ""
        exception = None
        status_message = responses.get(status_code, "Unknown Error")
        if exc_info:
            exception = exc_info[1]
            # get the custom message, if defined
            try:
                message = exception.log_message % exception.args
            except Exception:
                pass

            # construct the custom reason, if defined
            reason = getattr(exception, "reason", "")
            if reason:
                status_message = reason

        if exception and isinstance(exception, SQLAlchemyError):
            try:
                exception_str = str(exception)
                self.log.warning("Rolling back session due to database error %s", exception_str)
            except Exception:
                self.log.warning("Rolling back session due to database error %s", type(exception))
            self.db.rollback()

        self.set_header("Content-Type", "application/json")
        if isinstance(exception, web.HTTPError):
            # allow setting headers from exceptions
            # since exception handler clears headers
            headers = getattr(exception, "headers", None)
            if headers:
                for key, value in headers.items():
                    self.set_header(key, value)
            # Content-Length must be recalculated.
            self.clear_header("Content-Length")

        self.write(json.dumps({"status": status_code, "message": message or status_message}))

    def token_model(self, token):
        """Get the JSON model for an APIToken"""

        owner_key = "user"
        owner = token.user.name

        model = {
            owner_key: owner,
            "id": token.api_id,
            "kind": "api_token",
            # deprecated field, but leave it present.
            "roles": [],
            "scopes": [],
            "created": isoformat(token.created),
            "last_activity": isoformat(token.last_activity),
            "expires_at": isoformat(token.expires_at),
            "note": token.note,
            "session_id": token.session_id,
            "oauth_client": token.oauth_client.description or token.oauth_client.identifier,
        }
        return model

    def _filter_model(self, model, access_map, entity, kind, keys=None):
        """
        Filter the model based on the available scopes and the entity requested for.
        If keys is a dictionary, update it with the allowed keys for the model.
        """
        allowed_keys = set()
        # for scope in access_map:
        #   scope_filter = self.get_scope_filter(scope)
        #   if scope_filter(entity, kind=kind):
        #       allowed_keys |= access_map[scope]
        model = {key: model[key] for key in allowed_keys if key in model}
        if isinstance(keys, set):
            keys.update(allowed_keys)
        return model

    _user_model_types = {
        "name": str,
        "admin": bool,
        "groups": list,
        "roles": list,
        "auth_state": dict,
    }

    _group_model_types = {"name": str, "users": list, "roles": list}

    _service_model_types = {
        "name": str,
        "admin": bool,
        "url": str,
        "oauth_client_allowed_scopes": list,
        "api_token": str,
        "info": dict,
        "display": bool,
        "oauth_no_confirm": bool,
        "command": list,
        "cwd": str,
        "environment": dict,
        "user": str,
        "oauth_client_id": str,
        "oauth_redirect_uri": str,
    }

    def _check_model(self, model, model_types, name):
        """Check a model provided by a REST API request

        Args:
            model (dict): user-provided model
            model_types (dict): dict of key:type used to validate types and keys
            name (str): name of the model, used in error messages
        """
        if not isinstance(model, dict):
            raise web.HTTPError(400, reason="Invalid JSON data: %r" % model)
        if not set(model).issubset(set(model_types)):
            raise web.HTTPError(400, reason="Invalid JSON keys: %r" % model)
        for key, value in model.items():
            if not isinstance(value, model_types[key]):
                raise web.HTTPError(
                    400, "%s.%s must be %s, not: %r" % (name, key, model_types[key], type(value))
                )

    def _check_user_model(self, model):
        """Check a request-provided user model from a REST API"""
        self._check_model(model, self._user_model_types, "user")
        for username in model.get("users", []):
            if not isinstance(username, str):
                raise web.HTTPError(400, ("usernames must be str, not %r", type(username)))

    def _check_group_model(self, model):
        """Check a request-provided group model from a REST API"""
        self._check_model(model, self._group_model_types, "group")
        for groupname in model.get("groups", []):
            if not isinstance(groupname, str):
                raise web.HTTPError(400, ("group names must be str, not %r", type(groupname)))

    def _check_service_model(self, model):
        """Check a request-provided service model from a REST API"""
        self._check_model(model, self._service_model_types, "service")
        service_name = model.get("name")
        if not isinstance(service_name, str):
            raise web.HTTPError(400, ("Service name must be str, not %r", type(service_name)))

    def get_api_pagination(self):
        default_limit = self.settings["api_page_default_limit"]
        max_limit = self.settings["api_page_max_limit"]
        if not self.accepts_pagination:
            # if new pagination Accept header is not used,
            # default to the higher max page limit to reduce likelihood
            # of missing users due to pagination in code that hasn't been updated
            default_limit = max_limit
        offset = self.get_argument("offset", None)
        limit = self.get_argument("limit", default_limit)
        try:
            offset = abs(int(offset)) if offset is not None else 0
            limit = abs(int(limit))
            if limit > max_limit:
                limit = max_limit
            if limit < 1:
                limit = 1
        except Exception:
            raise web.HTTPError(400, "Invalid argument type, offset and limit must be integers")
        return offset, limit

    def paginated_model(self, items, offset, limit, total_count):
        """Return the paginated form of a collection (list or dict)

        A dict with { items: [], _pagination: {}}
        instead of a single list (or dict).

        pagination info includes the current offset and limit,
        the total number of results for the query,
        and information about how to build the next page request
        if there is one.
        """
        next_offset = offset + limit
        data = {
            "items": items,
            "_pagination": {"offset": offset, "limit": limit, "total": total_count, "next": None},
        }
        if next_offset < total_count:
            # if there's a next page
            next_url_parsed = urlparse(self.request.full_url())
            query = parse_qs(next_url_parsed.query)
            query["offset"] = [next_offset]
            query["limit"] = [limit]
            next_url_parsed = next_url_parsed._replace(query=urlencode(query, doseq=True))
            next_url = urlunparse(next_url_parsed)
            data["_pagination"]["next"] = {"offset": next_offset, "limit": limit, "url": next_url}
        return data

    def options(self, *args, **kwargs):
        self.finish()


class API404(APIHandler):
    """404 for API requests

    Ensures JSON 404 errors for malformed URLs
    """

    def check_xsrf_cookie(self):
        pass

    async def prepare(self):
        await super().prepare()
        raise web.HTTPError(404)
