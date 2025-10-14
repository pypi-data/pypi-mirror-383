#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2025
#            ✈ https://t.me/kamekuro
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html


class NetSchoolAPIError(Exception):
    pass


class AuthError(NetSchoolAPIError):
    def __init__(self, resp=None):
        self.resp = resp


class SchoolNotFoundError(NetSchoolAPIError):
    def __init__(self, resp=None):
        self.resp = resp


class NoResponseFromServer(NetSchoolAPIError):
    pass
