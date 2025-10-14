#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

from ._base import JSONType, NSObject, model
from .announcements import Announcement
from .assignment import Assignment, MarkAssignment, Mark
from .attachment import Attachment
from .diary import Day, Diary, Lesson
from .mail import MessageMin, Mail
from .message import Message
from .school import School
from .student import Student, UserSettings

__all__ = [
    "Announcement",
    "Assignment",
    "Attachment",
    "Day",
    "Diary",
    "JSONType",
    "Lesson",
    "Mail",
    "Mark",
    "MarkAssignment",
    "Message",
    "MessageMin",
    "NSObject",
    "School",
    "Student",
    "UserSettings",
    "model",
]
