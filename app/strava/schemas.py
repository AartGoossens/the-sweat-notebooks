from enum import Enum
from pydantic import BaseModel


class EventObjectType(str, Enum):
    activity = 'activity'
    athlete = 'athlete'


class EventAspectType(str, Enum):
    create = 'create'
    update = 'update'
    delete = 'delete'


class Updates(BaseModel):
    title: str = None
    type: str = None
    private: bool = None


class Event(BaseModel):
    aspect_type: EventAspectType
    event_time: str
    object_id: int
    object_type: EventObjectType
    owner_id: int
    subscription_id: int
    updates: Updates


class Activity(BaseModel):
    id: int
