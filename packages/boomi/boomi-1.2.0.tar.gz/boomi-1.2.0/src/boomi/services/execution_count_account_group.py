
from typing import Union
from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..net.transport.api_error import ApiError
from ..net.environment.environment import Environment
from ..models.utils.cast_models import cast_models
from ..net.transport.utils import parse_xml_to_dict
from ..models import (
    ExecutionCountAccountGroupQueryConfig,
    ExecutionCountAccountGroupQueryResponse,
)


class ExecutionCountAccountGroupService(BaseService):

    @cast_models
    def query_execution_count_account_group(
        self, request_body: ExecutionCountAccountGroupQueryConfig = None
    ) -> Union[ExecutionCountAccountGroupQueryResponse, str]:
        """The authenticating user for a QUERY operation must have the Dashboard privilege.

         For general information about the structure of QUERY filters, their sample payloads, and how to handle the paged results, refer to [Query filters](#section/Introduction/Query-filters) and [Query paging](#section/Introduction/Query-paging).

        :param request_body: The request body., defaults to None
        :type request_body: ExecutionCountAccountGroupQueryConfig, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: Union[ExecutionCountAccountGroupQueryResponse, str]
        """

        Validator(ExecutionCountAccountGroupQueryConfig).is_optional().validate(
            request_body
        )

        serialized_request = (
            Serializer(
                f"{self.base_url or Environment.DEFAULT.url}/ExecutionCountAccountGroup/query",
                [self.get_access_token(), self.get_basic_auth()],
            )
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response, status, content = self.send_request(serialized_request)
        if content == "application/json":
            return ExecutionCountAccountGroupQueryResponse._unmap(response)
        if content == "application/xml":
            return ExecutionCountAccountGroupQueryResponse._unmap(parse_xml_to_dict(response))
        raise ApiError("Error on deserializing the response.", status, response)

    @cast_models
    def query_more_execution_count_account_group(
        self, request_body: str
    ) -> Union[ExecutionCountAccountGroupQueryResponse, str]:
        """To learn about using `queryMore`, refer to [Query paging](#section/Introduction/Query-paging).

        :param request_body: The request body.
        :type request_body: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: Union[ExecutionCountAccountGroupQueryResponse, str]
        """

        Validator(str).validate(request_body)

        serialized_request = (
            Serializer(
                f"{self.base_url or Environment.DEFAULT.url}/ExecutionCountAccountGroup/queryMore",
                [self.get_access_token(), self.get_basic_auth()],
            )
            .serialize()
            .set_method("POST")
            .set_body(request_body, "text/plain")
        )

        response, status, content = self.send_request(serialized_request)
        if content == "application/json":
            return ExecutionCountAccountGroupQueryResponse._unmap(response)
        if content == "application/xml":
            return ExecutionCountAccountGroupQueryResponse._unmap(parse_xml_to_dict(response))
        raise ApiError("Error on deserializing the response.", status, response)
