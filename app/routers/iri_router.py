from abc import ABC, abstractmethod
import os
import logging
import importlib
from fastapi import Request, Depends, HTTPException, APIRouter
from fastapi.security import APIKeyHeader
from .account.models import User

bearer_token = APIKeyHeader(name="Authorization")


def get_real_ip(request : Request) -> str|None:
    # logging.debug("Request headers=%s" % request.headers)
    # logging.debug("client=%s" % request.client.host)
    ip_addr = request.headers.get('HTTP_X_REAL_IP')
    if not ip_addr:
        ip_addr = request.headers.get('x-real-ip')
        if not ip_addr:
            ip_addr = request.client.host
    return ip_addr


class IriRouter(APIRouter):
    def __init__(self, router_adapter=None, **kwargs):
        super().__init__(**kwargs)
        self.create_adapter(router_adapter)


    def create_adapter(self, router_adapter):
        # Load the facility-specific adapter
        router_name = self.prefix.replace("/", "").strip()

        # if there is no adapter specified for this router, 
        # and IRI_SHOW_MISSING_ROUTES is not true,
        # hide the router
        env_var = f"IRI_API_ADAPTER_{router_name}"
        logging.getLogger().info(f"Loading adapter from {env_var}")
        if env_var not in os.environ and os.environ.get("IRI_SHOW_MISSING_ROUTES") not in ["true", "1", "on", "yes"]:
            logging.getLogger().info(f"Hiding route: {router_name}")
            self.include_in_schema = False
            return
        
        # find and load the actual implementation
        adapter_name = os.environ.get(env_var, "app.demo_adapter.DemoAdapter")
        logging.getLogger().info(f"Using {router_name} adapter: {adapter_name}")
        parts = adapter_name.rsplit(".", 1)
        module = importlib.import_module(parts[0])    
        AdapterClass = getattr(module, parts[1])
        if not issubclass(AdapterClass, router_adapter):
            raise Exception(f"{adapter_name} should implement FacilityAdapter")
        logging.getLogger().info(f"\tSuccessfully loaded {router_name} adapter.")

        # assign it
        self.adapter = AdapterClass()


    async def current_user(
        self,
        request : Request, 
        api_key: str = Depends(bearer_token),
    ):
        user_id = None
        try:
            user_id = await self.adapter.get_current_user(api_key, get_real_ip(request))
        except Exception as exc:
            logging.getLogger().error(f"Error parsing IRI_API_PARAMS: {exc}")
        if not user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        request.state.current_user_id = user_id
        request.state.api_key = api_key


class AuthenticatedAdapter(ABC):


    @abstractmethod
    async def get_current_user(
        self : "AuthenticatedAdapter",
        api_key: str,
        ip_address: str|None,
        ) -> str:
        """
            Decode the api_key and return the authenticated user's id.
            This method is not called directly, rather authorized endpoints "depend" on it.
            (https://fastapi.tiangolo.com/tutorial/dependencies/)
        """
        pass


    @abstractmethod
    async def get_user(
        self : "AuthenticatedAdapter",
        user_id: str,
        api_key: str,
        ) -> User:
        """
            Retrieve additional user information (name, email, etc.) for the given user_id.
        """
        pass
