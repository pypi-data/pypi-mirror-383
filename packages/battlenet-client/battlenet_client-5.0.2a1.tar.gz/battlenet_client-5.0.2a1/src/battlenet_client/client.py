from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from collections.abc import Callable
from typing import Optional
from requests import Response
# import jose

from .oauth import auth_host

try:
    import psycopg
    import psycopg_binary
except ImportError:
    try:
        import mysql.connector
    except ImportError:
        try:
            import pymongo
        except ImportError:
            try:
                import redis
            except ImportError:
                try:
                    import sqlite3
                except ImportError:
                    Cache = None
                else:
                    from battlenet_client.cache.sqlite import SQLiteCache as Cache
            else:
                from battlenet_client.cache.redis import RedisCache as Cache
        else:
            from battlenet_client.cache.mongodb import MongoDBCache as Cache
    else:
        from battlenet_client.cache.mysql import MySQLCache as Cache
else:
    from battlenet_client.cache.postgresql import PostgresCache as Cache


class BattlenetClient:
    oauth = None
    state = None
    region = None
    client_id = None
    client_secret = None
    redirect_uri = None
    cache = None

    def __init__(self, region: str, oauth: OAuth2Session, cache_uri: Optional[str] = None):
        self.region = region
        self.oauth = oauth

        if cache_uri:
            self.cache = Cache(cache_uri)

    @classmethod
    def client_credential(cls, region: str,  client_id: str, client_secret: str, *,
                          auto_refresh_url: Optional[str] = None, auto_refresh_kwargs: Optional[dict] = None,
                          cache_uri: Optional[str] = None):
        """ Creates an instance of client credential grant oauth2 session

        Args:
            region (str): The region where the client is connected
            client_id (str): Client ID issued by develop.battle.net
            client_secret (str): Client secret issued by develop.battle.net
            auto_refresh_url (Optional[str]): Auto-refresh URL when token expires
            auto_refresh_kwargs (Optional[dict]): Extra arguments passed to OAuth2Session for automatic token refresh
            cache_uri (Optional[str]): URI for the cache system

        Returns:
            instance of BattlenetClient configured for client credentials grant oauth2 session
        """
        cls.client_id = client_id
        cls.client_secret = client_secret


        if auto_refresh_url and auto_refresh_kwargs:
            oauth = OAuth2Session(client=BackendApplicationClient(client_id=client_id),
                                  auto_refresh_url=auto_refresh_url,
                                  auto_refresh_kwargs=auto_refresh_kwargs,
                                  update_token=cls.token_updater)
        else:
            oauth = OAuth2Session(client=BackendApplicationClient(client_id=client_id))

        oauth.fetch_token(token_url=f"{auth_host(region)}/token", client_id=client_id, client_secret=client_secret)
        return cls(region, oauth, cache_uri)

    @classmethod
    def authorization_code(cls, region, client_id: str, redirect_uri: str, scope: list[str], *,
                           auto_refresh_url: Optional[str] = None, auto_refresh_kwargs: Optional[dict] = None,
                           updater: Callable[[dict], None] = None, cache_uri: Optional[str] = None):
        """ Creates an instance of authorization code grant oauth2 session

        Args:
            region (str): The region where the client is connected
            client_id (str): Client ID issued by develop.battle.net
            redirect_uri (str): URL to send to authorization service to return
            scope (list[str]): list of scopes to grant
            auto_refresh_url (Optional[str]): Auto-refresh URL when token expires
            auto_refresh_kwargs (Optional[dict]): Extra arguments passed to OAuth2Session for automatic token refresh
            updater (callable, optional): the function to perform the automatic update
            cache_uri (Optional[str]): URI for the cache system

        Returns:
            instance of BattlenetClient configured for authorization code grant oauth2 session
        """

        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope, auto_refresh_url=auto_refresh_url,
                              auto_refresh_kwargs=auto_refresh_kwargs, updater=updater)



        return cls(region, oauth, cache_uri)

    @classmethod
    def open_id(cls):
        """TODO: Future release"""
        pass

    def get_authorization_url(self) -> tuple[str, str]:
        """ Creates an authorization url grant oauth2 URL

        Returns:
              tuple[str, str]: authorization url and authorization state
        """
        url, self.state = self.oauth.authorization_url(f"{auth_host(self.region)}/authorize")
        return url, self.state

    def callback(self, auth_uri: str, client_secret: str, response: Response) -> None:
        """ Creates an authorization code grant oauth2 session

        Args:
            auth_uri (str): URL to acquire the authorization url
            client_secret (str): Client secret issued by develop.battle.net
            response (Response): response from authorization server
        """
        self.oauth.fetch_token(auth_uri, authorization_response=response, client_secret=client_secret)

    def token_updater(self, token: dict):
        """ Function to update the token after a refresh

        Args:
            token (dict): token returned from authorization server
        """
        self.oauth.token = token
        self.oauth.access_token = token["access_token"]

    def fetch_token(self, scope: str, grant_type: str = 'client_credentials',
                    redirect_uri: Optional[str]=None) -> None:
        """ Fetches the token from the authorization server

        Args:
            scope (str): scope for the authorization
            grant_type (str, optional): grant type for the authorization defaults to 'client_credentials'
            redirect_uri (str, optional): redirect uri for the authorization server
        """
        data = {"region": self.region.lower(), "grant_type": grant_type, "scope": scope, "code": "code", "redirect_uri": redirect_uri}

        self.oauth.post(f"{auth_host(self.region)}/token", data=data)

    def user_info(self):
        """Returns basic information about the user associated with the current bearer token."""
        return self.oauth.get(f"{auth_host(self.region)}/userinfo")

    def check_token(self) -> bool:
        """ Verifies that a given bearer token is valid and retrieves metadata about the token, including the client_id
        used to create the token, expiration timestamp, and scopes granted to the token.

        Returns:
            bool: True if the token is valid, False otherwise
        """
        return self.oauth.post(f"{auth_host(self.region)}/check_token",
                               data={"token": self.oauth.token['access_token']}).status_code == 200

    def get(self, url, **kwargs):
        """Conveneince function for GET requests"""
        return self.oauth.get(url, **kwargs)

    def post(self, url, **kwargs):
        """Conveneince function for POST requests"""
        return self.oauth.post(url, **kwargs)

    def put(self, url, **kwargs):
        """Conveneince function for PUT requests"""
        return self.oauth.put(url, **kwargs)

    def delete(self, url, **kwargs):
        """Conveneince function for DELETE requests"""
        return self.oauth.delete(url, **kwargs)

    def add_cache(self, cache_uri: str):
        """ Initializes connection for cache

        Args:
            cache_uri (str): URI for the cache system
        """
        self.cache = Cache(cache_uri)
