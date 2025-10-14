#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

from enum import Enum


class AutoName(Enum):
    def __repr__(self):
        return f"'{str(self.value)}'"

    def __str__(self):
        return str(self.value)

    def _generate_next_value_(self, *args):
        return self.lower().capitalize()
