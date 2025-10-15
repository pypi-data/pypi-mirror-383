"""连续劳务税费试算"""

from .model.calculatelabor import *
from ..base import BaseClient
from ...utils import Utils


class CalculateLaborServiceClient(BaseClient):
    """连续劳务税费试算客户端"""

    def __init__(self, config):
        super().__init__(config)

    def labor_caculator(self, request: LaborCaculatorRequest):
        """ 连续劳务税费试算（计算器）

        :type request: LaborCaculatorRequest
        :param request: the LaborCaculatorRequest request parameters class.

        :return: LaborCaculatorResponse
        """
        return self._post(
            "/api/tax/v1/labor-caculator",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def calc_tax(self, request: CalcTaxRequest):
        """ 订单税费试算

        :type request: CalcTaxRequest
        :param request: the CalcTaxRequest request parameters class.

        :return: CalcTaxResponse
        """
        return self._post(
            "/api/payment/v1/calc-tax",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def calculation_year_h5_url(self, request: CalculationYearH5UrlRequest):
        """ 连续劳务年度税费测算-H5

        :type request: CalculationYearH5UrlRequest
        :param request: the CalculationYearH5UrlRequest request parameters class.

        :return: CalculationYearH5UrlResponse
        """
        return self._get(
            "/api/labor/service/calculation/year/h5url",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def calculation_h5_url(self, request: CalculationH5UrlRequest):
        """ 连续劳务单笔结算税费测算-H5

        :type request: CalculationH5UrlRequest
        :param request: the CalculationH5UrlRequest request parameters class.

        :return: CalculationH5UrlResponse
        """
        return self._get(
            "/api/labor/service/calculation/h5url",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
