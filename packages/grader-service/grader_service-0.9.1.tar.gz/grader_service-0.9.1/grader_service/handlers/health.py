from http import HTTPStatus

from tornado.web import HTTPError

from grader_service.handlers.base_handler import GraderBaseHandler
from grader_service.orm.lecture import Lecture, LectureState
from grader_service.registry import VersionSpecifier, register_handler


@register_handler(path=r"\/api\/health\/?", version_specifier=VersionSpecifier.ALL)
class HealthHandler(GraderBaseHandler):
    """
    Tornado Handler class for http requests to /health.
    """

    async def get(self):
        """
        Check health of service
        :return permissions of the user
        """
        try:
            self.session.query(Lecture).filter(Lecture.state == LectureState.active).all()
        except Exception as e:
            self.log.error(e)
            raise HTTPError(HTTPStatus.INTERNAL_SERVER_ERROR, reason="Database Error")

        response = {"health": "OK"}
        self.write_json(response)
