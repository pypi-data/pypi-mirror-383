"""实名信息收集"""

from .model.realname import *
from ..base import BaseClient
from ...utils import Utils


class RealNameServiceClient(BaseClient):
    """实名信息收集客户端"""

    def __init__(self, config):
        super().__init__(config)

    def collect_real_name_info(self, request: CollectRealNameInfoRequest):
        """ 用户实名认证信息收集

        :type request: CollectRealNameInfoRequest
        :param request: the CollectRealNameInfoRequest request parameters class.

        :return: CollectRealNameInfoResponse
        """
        return self._post(
            "/api/user/v1/collect/realname/info",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def query_real_name_info(self, request: QueryRealNameInfoRequest):
        """ 用户实名认证信息查询

        :type request: QueryRealNameInfoRequest
        :param request: the QueryRealNameInfoRequest request parameters class.

        :return: QueryRealNameInfoResponse
        """
        return self._get(
            "/api/user/v1/query/realname/info",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
