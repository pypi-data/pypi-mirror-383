#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import dataclasses
import datetime
from typing import TYPE_CHECKING, List

from aionetschool.types import JSONType, NSObject, model
from aionetschool.types.attachment import Attachment

if TYPE_CHECKING:
    from aionetschool.client import NetSchoolAPI


@model
class SubjectGroupAssignment:
    id: int
    name: str


@model
class TeacherAssignment:
    id: int
    name: str


@model
class MarkAssignment(NSObject):
    id: int = dataclasses.field(metadata=dict(required=False))
    assignment_name: str = dataclasses.field(
        metadata=dict(data_key="assignmentName", required=False)
    )
    activity_name: str = dataclasses.field(
        metadata=dict(data_key="activityName", required=False)
    )
    problem_name: str = dataclasses.field(
        metadata=dict(data_key="problemName", required=False)
    )
    subject_group: SubjectGroupAssignment = dataclasses.field(
        metadata=dict(data_key="subjectGroup", required=False)
    )
    teachers: List[TeacherAssignment] = dataclasses.field(metadata=dict(required=False))
    product_id: int = dataclasses.field(
        metadata=dict(data_key="productId", required=False)
    )
    is_deleted: bool = dataclasses.field(
        metadata=dict(data_key="isDeleted", required=False)
    )
    weight: int = dataclasses.field(metadata=dict(required=False))
    date: datetime.datetime = dataclasses.field(metadata=dict(required=False))
    description: str = dataclasses.field(metadata=dict(required=False))
    attachments: List[Attachment] = dataclasses.field(metadata=dict(required=False))
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        cls_data: dict = cls.cleanup_data(data)
        if cls_data.get("subject_group"):
            cls_data["subject_group"] = SubjectGroupAssignment(
                id=cls_data["subject_group"]["id"],
                name=cls_data["subject_group"]["name"],
            )
        if cls_data.get("teachers"):
            cls_data["teachers"] = [
                TeacherAssignment(id=x["id"], name=x["name"])
                for x in cls_data["teachers"]
            ]
        if cls_data.get("attachments"):
            cls_data["attachments"] = [
                Attachment.de_json(x, client) for x in cls_data["attachments"]
            ]
        return cls(client=client, **cls_data)


# https://sgo.edu-74.ru/webapi/student/diary/assigns/AID?studentId=SID
@model
class Mark(NSObject):
    id: int = dataclasses.field(metadata=dict(required=False))
    student_id: int = dataclasses.field(
        metadata=dict(data_key="studentId", required=False)
    )
    mark: int | str = dataclasses.field(metadata=dict(required=False))
    result_score: int = dataclasses.field(
        metadata=dict(data_key="resultScore", required=False)
    )
    duty_mark: bool = dataclasses.field(
        metadata=dict(data_key="dutyMark", required=False)
    )
    assignment_id: int = dataclasses.field(
        metadata=dict(data_key="assignmentId", required=False)
    )
    client: "NetSchoolAPI" = None


@model
class Assignment(NSObject):
    id: int = dataclasses.field(metadata=dict(required=False))
    # comment: str = dataclasses.field(metadata=dict(required=False))
    # type: str = dataclasses.field(metadata=dict(required=False))
    # is_duty: bool = dataclasses.field(
    #     metadata=dict(data_key="dutyMark", required=False)
    # )
    type_id: int = dataclasses.field(metadata=dict(data_key="typeId", required=False))
    content: str = dataclasses.field(
        metadata=dict(data_key="assignmentName", required=False)
    )
    weight: int = dataclasses.field(metadata=dict(required=False))
    deadline: datetime.date = dataclasses.field(
        metadata=dict(data_key="dueDate", required=False)
    )
    class_assignment: bool = dataclasses.field(
        metadata=dict(data_key="classAssignment", required=False)
    )
    class_meeting_id: int = dataclasses.field(
        metadata=dict(data_key="classMeetingId", required=False)
    )
    issue_class_meeting_id: int = dataclasses.field(
        metadata=dict(data_key="issueClassMeetingId", required=False)
    )
    mark: Mark = dataclasses.field(metadata=dict(required=False))
    client: "NetSchoolAPI" = None

    @classmethod
    def de_json(cls, data: JSONType, client: "NetSchoolAPI"):
        if not cls.is_dict_model_data(data):
            return None

        cls_data: dict = cls.cleanup_data(data)
        cls_data["mark"] = None
        if "mark" in cls_data:
            cls_data["mark"] = Mark.de_json(cls_data["mark"], client)
        return cls(client=client, **cls_data)


"""
                        {
                            "id": 366487899,
                            "typeId": 10,
                            "assignmentName": "---Не указана---",
                            "weight": 10,
                            "dueDate": "2025-09-03T00:00:00",
                            "classAssignment": true,
                            "classMeetingId": 302575615
                        },
                        {
                            "id": 366487926,
                            "typeId": 3,
                            "assignmentName": "Не задано",
                            "weight": 10,
                            "dueDate": "2025-09-03T00:00:00",
                            "classAssignment": true,
                            "classMeetingId": 302575615
                        },
                        {
                            "id": 357161570,
                            "typeId": 3,
                            "assignmentName": "просмотреть презентацию, в последнем файле ответить на вопросы",
                            "weight": 10,
                            "dueDate": "2025-04-07T00:00:00",
                            "classAssignment": true,
                            "classMeetingId": 270983021,
                            "issueClassMeetingId": 270983101
                        },

                        {
                            "id": 357719619,
                            "typeId": 40,
                            "assignmentName": "Порядок построения изображения на чертежах",
                            "weight": 10,
                            "dueDate": "2025-04-07T00:00:00",
                            "classAssignment": false,
                            "classMeetingId": 271001528,
                            "mark": {
                                "id": 0,
                                "studentId": 590887,
                                "mark": 5,
                                "resultScore": null,
                                "dutyMark": false,
                                "assignmentId": 357719619
                            }
                        },
                        
"""


"""
class AssignmentSchema(BaseSchema):
    id: int = dataclasses.field(metadata=dict(
        allow_none=True, required=False
    ))
    comment: str = dataclasses.field(metadata=dict(
        allow_none=True, required=False
    ))
    type: str = dataclasses.field(metadata=dict(
        allow_none=True, required=False
    ))
    content: str = dataclasses.field(metadata=dict(
        data_key="assignmentName", allow_none=True, required=False
    ))
    mark: typing.Optional[int] = dataclasses.field(metadata=dict(
        data_key="mark", allow_none=True, required=False
    ))
    is_duty: bool = dataclasses.field(metadata=dict(
        data_key="dutyMark", allow_none=True, required=False
    ))
    deadline: datetime.date = dataclasses.field(metadata=dict(
        data_key="dueDate", allow_none=True, required=False
    ))

    @marshmallow.pre_load
    def unwrap_marks(self, assignment: typing.Dict[str, typing.Any], **_) -> typing.Dict[str, typing.Any]:
        mark = assignment.pop("mark", None)
        if mark:
            assignment.update(mark)
        else:
            assignment.update({"mark": None, "dutyMark": False})
        mark_comment = assignment.pop("markComment", None)
        assignment["comment"] = mark_comment["name"] if mark_comment else ""
        assignment["type"] = self.context["assignment_types"][assignment.pop("typeId")]
        return assignment
"""
