#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import dataclasses
import datetime
from typing import TYPE_CHECKING, List, Optional

from aionetschool.enums import Role
from aionetschool.types import Assignment, JSONType, NSObject, model

if TYPE_CHECKING:
    from aionetschool.client import NetSchoolAPI


@model
class Lesson(NSObject):
    day: datetime.date
    start: datetime.time = dataclasses.field(
        metadata=dict(data_key="startTime", required=False)
    )
    end: datetime.time = dataclasses.field(
        metadata=dict(data_key="endTime", required=False)
    )
    room: Optional[str] = dataclasses.field(metadata=dict(required=False))
    number: int = dataclasses.field(metadata=dict(required=False))
    subject: str = dataclasses.field(
        metadata=dict(data_key="subjectName", required=False)
    )
    is_distance_lesson: bool = dataclasses.field(
        metadata=dict(data_key="isDistanceLesson", required=False)
    )
    is_ea_lesson: bool = dataclasses.field(
        metadata=dict(data_key="isEaLesson", required=False)
    )
    class_meeting_id: int = dataclasses.field(
        metadata=dict(data_key="classmeetingId", required=False)
    )
    relay: int = dataclasses.field(metadata=dict(data_key="relay", required=False))
    assignments: List[Assignment] = dataclasses.field(
        default_factory=list, metadata=dict(required=False)
    )  # type: ignore
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        cls_data: dict = cls.cleanup_data(data)
        cls_data["assignments"] = [
            Assignment.de_json(assignment, client)
            for assignment in cls_data["assignments"]
        ]
        return cls(client=client, **cls_data)


@model
class Day(NSObject):
    day: datetime.date = dataclasses.field(
        default=None, metadata=dict(data_key="date", required=False)
    )
    lessons: List[Lesson] = dataclasses.field(
        default=None, metadata=dict(data_key="lessons", required=False)
    )
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        cls_data: dict = cls.cleanup_data(data)
        cls_data["lessons"] = [
            Lesson.de_json(lesson, client) for lesson in cls_data["lessons"]
        ]
        return cls(client=client, **cls_data)


@model
class Diary(NSObject):
    start: datetime.date = dataclasses.field(
        default=None, metadata=dict(data_key="weekStart", required=False)
    )
    end: datetime.date = dataclasses.field(
        default=None, metadata=dict(data_key="weekEnd", required=False)
    )
    days: List[Day] = dataclasses.field(
        default=None, metadata=dict(data_key="weekDays", required=False)
    )
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        cls_data: dict = cls.cleanup_data(data)
        cls_data["days"] = [Day.de_json(day, client) for day in cls_data["days"]]
        return cls(client=client, **cls_data)


"""
@dataclasses.dataclass
class DaySchema(BaseSchema):
    lessons: typing.List[LessonSchema] = dataclasses.field(metadata=dict(
        allow_none=True, required=False
    )) # type: ignore
    day: datetime.date = dataclasses.field(metadata=dict(
        data_key="date", allow_none=True, required=False
    ))
"""


"""
@dataclasses.dataclass
class LessonSchema(BaseSchema):
    day: datetime.date
    start: datetime.time = dataclasses.field(metadata=dict(
        data_key="startTime", allow_none=True, required=False
    ))
    end: datetime.time = dataclasses.field(metadata=dict(
        data_key="endTime", allow_none=True, required=False
    ))
    room: typing.Optional[str] = dataclasses.field(metadata=dict(
        missing="", allow_none=True, required=False
    ))
    number: int = dataclasses.field(metadata=dict(
        allow_none=True, required=False
    ))
    subject: str = dataclasses.field(metadata=dict(
        data_key="subjectName", allow_none=True, required=False
    ))
    is_distance_lesson: bool = dataclasses.field(metadata=dict(
        data_key="isDistanceLesson", allow_none=True, required=False
    ))
    is_ea_lesson: bool = dataclasses.field(metadata=dict(
        data_key="isEaLesson", allow_none=True, required=False
    ))
    class_meeting_id: int = dataclasses.field(metadata=dict(
        data_key="classmeetingId", allow_none=True, required=False
    ))
    relay: int = dataclasses.field(metadata=dict(
        data_key="relay", allow_none=True, required=False
    ))
    assignments: typing.List[AssignmentSchema] = dataclasses.field(default_factory=list, metadata=dict(
        allow_none=True, required=False
    ))  # type: ignore
"""
