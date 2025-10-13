# SSO related functions for pyocient
import base64
import json
import logging
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from textwrap import dedent
from time import monotonic, sleep
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse

import pkce
import requests

import pyocient.ocient_protocol_pb2 as proto
from pyocient import api

logger = logging.getLogger(__name__)

# when we are handing an SSO authenticaction flow callback,
# this is the path and port we listen on.  This is consistent
# with JDBC.  We only open this port for the duration of the
# authentication flow
LOCAL_SSO_CALLBACK_PATH = "/ocient/oauth2/v1/callback"
LOCAL_SSO_CALLBACK_PORT = 7050


def sso_local_callback_url() -> str:
    return f"http://127.0.0.1:{LOCAL_SSO_CALLBACK_PORT}{LOCAL_SSO_CALLBACK_PATH}"


def sso_get_credentials_from_code(
    sso_code: str, sso_state: Optional[str], sso_redirect_state: Optional[Dict[Any, Any]]
) -> Tuple[str, str]:
    """
    Given a "code" and "state" returned from an SSO authenticator, turn it into the user and password that
    the Ocient Hyperscale Data Warehouse expects
    """
    logger.debug("Starting sso_get_credentials_from_code")
    if not sso_state:
        raise api.Error("Received SSO code without matching state")

    if not sso_redirect_state:
        raise api.Error("Missing SSO redirect state")

    if uuid.UUID(sso_state) != sso_redirect_state["correlation_id"]:
        raise api.Error("Session and sso state mismatch")

    # Use the authentication server's token endpoint, turn the code into an actual access token
    response = requests.post(
        sso_redirect_state["token_endpoint"],
        data={
            "grant_type": "authorization_code",
            "client_id": sso_redirect_state["client_id"],
            "code": sso_code,
            "code_verifier": sso_redirect_state["code_verifier"],
            "scope": sso_redirect_state["scopes"],
            "redirect_uri": sso_redirect_state["redirect_url"],
        },
        verify=api.Connection.SSO_SERVER_CERTIFICATE_VERIFICATION,
    )

    logger.debug(f"Received token_endpoint response {response.json()}")

    # This is a magic value understood by the Ocient Hyperscale Data Warehouse server indicating that
    # the password contains a base64 encoded json document with tokens (likely
    # access, id, and refresh tokens, depending on the flow)
    user = "oauth_tokens"

    js = json.dumps(response.json())

    # and base64 encode the string representation of the JSON
    # document
    password = base64.b64encode(js.encode("utf-8")).decode("utf-8")

    return user, password


def _sso_authorization_flow(
    auth: proto.Authenticator,  # type: ignore[name-defined]
    sso_callback_url: Optional[str],
    scopes: str,
    config_data: Dict[str, str],
    sso_timeout: float,
) -> None:
    """
    Perform the authorization flow with the SSO server.  this routine raises an SSORedirection exception
    """
    logger.debug("starting sso authorization flow")

    callback_url = sso_callback_url or sso_local_callback_url()

    code_verifier, code_challenge = pkce.generate_pkce_pair()

    # Create the state we will return in the SSORedirection exception
    state = {
        "client_id": auth.openidauthenticator.clientId,
        "scopes": scopes,
        "redirect_url": callback_url,
        "token_endpoint": config_data.get("token_endpoint"),
        "correlation_id": uuid.uuid4(),
        "code_verifier": code_verifier,
    }

    # Construct the authorization URI and return it our caller in an
    # SSORedirection exception
    auth_url = (
        config_data["authorization_endpoint"]
        + "?"
        + urlencode(
            {
                "client_id": auth.openidauthenticator.clientId,
                "state": str(state["correlation_id"]),
                "response_mode": "query",
                "response_type": "code",
                "redirect_uri": callback_url,
                "scope": scopes,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "consent": "prompt",
            },
        )
    )

    logger.debug(f"raising SSORedirection exception with url {auth_url}")

    # Raise the SSO redirection exception
    raise api.SSORedirection(authURL=auth_url, state=state)


def _sso_device_flow(
    auth: proto.Authenticator,  # type: ignore[name-defined]
    scopes: str,
    config_data: Dict[str, str],
    sso_timeout: float,
) -> Tuple[str, str]:
    """
    This is the device authorization flow. Rather than launching a browser,
    we print a messsage to stdout telling the caller what link to go to
    """
    logger.debug("starting sso device flow")
    response = requests.post(
        config_data["device_authorization_endpoint"],
        data={
            "client_id": auth.openidauthenticator.clientId,
            "scope": scopes,
        },
        verify=api.Connection.SSO_SERVER_CERTIFICATE_VERIFICATION,
    )

    # This should definitely have:
    # - device_code
    # - user_code
    # - verification_uri
    #
    # it may have
    # - verification_uri_complete
    # - interval
    js = response.json()

    logger.debug(f"Received device_authorization response {js}")

    interval = float(js.get("interval", "5"))
    device_code = js.get("device_code")

    # This message is consistent with the JDBC driver
    print(
        dedent(
            f"""
                Please enter the following code at the verification_uri:
                    verification_uri_complete: {js.get("verification_uri_complete", "n/a")}
                    verification_uri: {js.get("verification_uri")}
                    user_code: {js.get("user_code")}
                    """
        )
    )

    # This exact message is looked for in system tests
    logger.info(f"[pyocient] Please authenticate at: {js.get('verification_uri_complete', 'n/a')}")

    # Now we start polling the token endpoint to see if the user entered the URL
    start_time = monotonic()
    while True:
        if monotonic() - start_time > sso_timeout:
            raise api.Error("Timeout waiting for SSO response")

        response = requests.post(
            config_data["token_endpoint"],
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": auth.openidauthenticator.clientId,
                "device_code": device_code,
            },
            verify=api.Connection.SSO_SERVER_CERTIFICATE_VERIFICATION,
        )

        js = response.json()

        logger.debug(f"Received token_endpoint response {js}")

        # If we actually got an access token, we are done
        if "access_token" in js:
            # This is a magic value understood by the server
            user = "oauth_tokens"

            # Convert the json response to a string
            js = json.dumps(response.json())

            # and base64 encode the string representation of the JSON
            # document
            password = base64.b64encode(js.encode("utf-8")).decode("utf-8")

            return user, password

        if "error" in js:
            if js["error"] == "authorization_pending":
                interval += 5
                sleep(interval)
                continue

            if js["error"] == "slow_down":
                sleep(interval)
                continue

        raise api.Error(f"{js.get('error', 'general error')} : {js.get('error_description', 'something went wrong')}")

    raise api.Error("Unable to execute SSO device flow")


def sso_get_credentials(
    authenticators: List[proto.Authenticator],  # type: ignore[name-defined]
    sso_oauth_flow: Optional[str],
    sso_callback_url: Optional[str],
    sso_timeout: float,
    identity_provider: Optional[str],
) -> Tuple[str, str]:
    """
    Get SSO credentials. We will either do an authorization flow or a device flow based on
    the `sso_oauth_flow` value or whether we have the capability to launch a browser
    """

    # Decide if we should try to launch a browser.  If the sso_oauth_flow is 'deviceGrant'
    # we don't want to.  Otherwise, see if the `webbrowser` module thinks it can launch
    # a browser
    browser_launcher = None
    if sso_oauth_flow != "deviceGrant":
        try:
            browser_launcher = webbrowser.get()
        except webbrowser.Error:
            pass

    # if user specified an identity provider, try that one first
    if isinstance(identity_provider, str):
        for auth in authenticators:
            if auth.openidauthenticator.identityprovider == identity_provider:
                if auth.openidauthenticator.disabled:
                    raise api.Error("The requested security integration is disabled", "08001", -1200)

                # First get the authenticator URL
                response = requests.get(
                    auth.openidauthenticator.issuer + "/.well-known/openid-configuration",
                    verify=api.Connection.SSO_SERVER_CERTIFICATE_VERIFICATION,
                )
                if response.status_code >= 400:
                    break
                config_data = response.json()
                scopes = " ".join(auth.openidauthenticator.scope)
                redirect_ssl_str = "http"  # Eventually this should be "https" if auth.openidauthenticator.redirectSSL else "http" but I don't think there is SSL_SSO_CALLBACK support for pyocient yet.

                redirect_uri = (
                    f"{redirect_ssl_str}://{auth.openidauthenticator.redirectHost}:{LOCAL_SSO_CALLBACK_PORT}{LOCAL_SSO_CALLBACK_PATH}"
                    if auth.openidauthenticator.redirectHost
                    else sso_callback_url
                )
                logging.log(logging.DEBUG, f"Redirect URI: {redirect_uri}")

                # If we should launch a browser or if we have been handed an explicit callback URL,
                # do the authorization flow
                if (browser_launcher or redirect_uri) and sso_oauth_flow != "deviceGrant":
                    _sso_authorization_flow(auth, redirect_uri, scopes, config_data, sso_timeout)
                else:
                    return _sso_device_flow(auth, scopes, config_data, sso_timeout)

    disabled = False
    # Try each of the authenticators in turn
    for auth in authenticators:
        # If disabled skip the authenticator but mark disabled as true
        if auth.openidauthenticator.disabled:
            disabled = True
            continue

        # First get the authenticator URL
        response = requests.get(
            auth.openidauthenticator.issuer + "/.well-known/openid-configuration",
            verify=api.Connection.SSO_SERVER_CERTIFICATE_VERIFICATION,
        )
        if response.status_code >= 400:
            continue
        config_data = response.json()

        scopes = " ".join(auth.openidauthenticator.scope)

        redirect_uri = (
            f"http://{auth.openidauthenticator.redirectHost}:{LOCAL_SSO_CALLBACK_PORT}{LOCAL_SSO_CALLBACK_PATH}"
            if auth.openidauthenticator.redirectHost
            else sso_callback_url
        )

        # If we should launch a browser or if we have been handed an explicit callback URL,
        # do the authorization flow
        if sso_oauth_flow != "deviceGrant":
            _sso_authorization_flow(auth, redirect_uri, scopes, config_data, sso_timeout)
        else:
            return _sso_device_flow(auth, scopes, config_data, sso_timeout)

    if disabled:
        raise api.Error("The security integration is disabled", "08001", -1200)

    raise api.Error("No SSO credentials found")


def local_sso_callback(auth_url: str, sso_timeout: float) -> Tuple[str, str]:
    """
    This function starts up a web server and waits for the browser
    to call us back after an SSO authentication flow.  All in all
    this is a terrible implementation, since we can't use ephemeral
    ports for reasons described here:
    https://community.auth0.com/t/random-local-ports-on-redirect-uri/28623/9

    In general, a much better model is generally for some higher level caller
    to handle the callback
    """

    class ContextHTTPServer(HTTPServer):
        """
        This class implements an HTTP server, with some context
        that can be updated when a request is received
        """

        def __init__(self, *args: Any, **kwargs: Any):
            HTTPServer.__init__(self, *args, **kwargs)
            self.oidc_code: Optional[str] = None
            self.state: Optional[str] = None

        def handle_timeout(self) -> None:
            raise TimeoutError("SSO callback timed out")

    class SingleRequestHandler(BaseHTTPRequestHandler):
        """
        Handler for a single request that basically just
        stores the `code` and `state` parameters in
        the server
        """

        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"SSO Authentication complete!")

            parsed = urlparse(self.path)

            if parsed.path != LOCAL_SSO_CALLBACK_PATH:
                raise api.Error("Invalid SSO Callback path")

            qs = parse_qs(parsed.query)

            if "code" not in qs:
                raise api.Error("Malformed SSO callback. Missing OIDC code parameter")

            if "state" not in qs:
                raise api.Error("Malformed SSO callback. Missing state parameter")

            assert isinstance(self.server, ContextHTTPServer)
            self.server.oidc_code = " ".join(qs["code"])
            self.server.state = " ".join(qs["state"])

    with ContextHTTPServer(("localhost", LOCAL_SSO_CALLBACK_PORT), SingleRequestHandler) as server:
        server.timeout = sso_timeout
        # Open the browser to send a request to the server
        if webbrowser.open_new(auth_url):
            # Wait for a single request
            try:
                server.handle_request()
            except TimeoutError:
                raise api.Error("SSO callback timed out w/ browser")

            if not server.oidc_code:
                raise api.Error("Missing OIDC authentication code in SSO callback")

            if not server.state:
                raise api.Error("Missing state in SSO callback")

            return server.oidc_code, server.state
        else:
            auth_str = f"Could not open default browser with Desktop library. Please authenticate at: {auth_url}"
            logger.warning(auth_str)
            print(auth_str)

            # Wait for a single request
            try:
                server.handle_request()
            except TimeoutError:
                raise api.Error("SSO callback timed out")

            if not server.oidc_code:
                raise api.Error("Missing OIDC authentication code in SSO callback")

            if not server.state:
                raise api.Error("Missing state in SSO callback")

            return server.oidc_code, server.state
