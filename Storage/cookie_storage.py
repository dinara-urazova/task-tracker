from flask import request

COOKIE_NAME = "task_tracker_session"


class CookieStorage:
    def get_cookie_value(self) -> str:
        return request.cookies.get(COOKIE_NAME)
