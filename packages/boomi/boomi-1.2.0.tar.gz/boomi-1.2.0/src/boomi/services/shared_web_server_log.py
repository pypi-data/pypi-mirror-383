
from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..net.environment.environment import Environment
from ..models.utils.cast_models import cast_models


class SharedWebServerLogService(BaseService):

    @cast_models
    def create_shared_web_server_log(self) -> None:
        """This API is documented externally. Please visit the following link for full details:

        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        """

        serialized_request = (
            Serializer(
                f"{self.base_url or Environment.DEFAULT.url}/SharedWebServerLog",
                [self.get_access_token(), self.get_basic_auth()],
            )
            .serialize()
            .set_method("POST")
        )

        self.send_request(serialized_request)
