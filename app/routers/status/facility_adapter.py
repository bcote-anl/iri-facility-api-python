from abc import ABC, abstractmethod
from . import models as status_models
import datetime


class FacilityAdapter(ABC):
    """
    Facility-specific code is handled by the implementation of this interface.
    Use the `IRI_API_ADAPTER` environment variable (defaults to `app.demo_adapter.FacilityAdapter`) 
    to install your facility adapter before the API starts.
    """


    @abstractmethod
    async def get_resources(
        self : "FacilityAdapter",
        offset : int,
        limit : int,
        name : str | None = None,
        description : str | None = None,        
        group : str | None = None,
        modified_since : datetime.datetime | None = None,
        resource_type : status_models.ResourceType | None = None,
        ) -> list[status_models.Resource]:
        pass


    @abstractmethod
    async def get_resource(
        self : "FacilityAdapter",
        id : str
        ) -> status_models.Resource:
        pass


    @abstractmethod
    async def get_events(
        self : "FacilityAdapter",
        incident_id : str,
        offset : int,
        limit : int,
        resource_id : str | None = None,
        name : str | None = None,
        description : str | None = None,
        status : status_models.Status | None = None,
        from_ : datetime.datetime | None = None,
        to : datetime.datetime | None = None,
        time : datetime.datetime | None = None,
        modified_since : datetime.datetime | None = None,
        ) -> list[status_models.Event]:
        pass


    @abstractmethod
    async def get_event(
        self : "FacilityAdapter",
        incident_id : str,
        id : str
        ) -> status_models.Event:
        pass


    @abstractmethod
    async def get_incidents(
        self : "FacilityAdapter",
        offset : int,
        limit : int,
        name : str | None = None,
        description : str | None = None,
        status : status_models.Status | None = None,
        type : status_models.IncidentType | None = None,
        from_ : datetime.datetime | None = None,
        to : datetime.datetime | None = None,
        time_ : datetime.datetime | None = None,
        modified_since : datetime.datetime | None = None,
        resource_id : str | None = None,
        ) -> list[status_models.Incident]:
        pass


    @abstractmethod
    async def get_incident(
        self : "FacilityAdapter",
        id : str
        ) -> status_models.Incident:
        pass
