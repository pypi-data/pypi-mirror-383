"""连续劳务税费试算"""

from ...base import BaseRequest


class LaborCaculatorRequest(BaseRequest):
    """
    连续劳务税费试算（计算器）请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type month_settlement_list: list
    :param month_settlement_list: 月度收入列表
    """

    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        month_settlement_list = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.month_settlement_list = month_settlement_list


class MonthSettlement(BaseRequest):
    """
    月度收入-响应

    :type month: int
    :param month: 月份

    :type month_pre_tax_amount: string
    :param month_pre_tax_amount: 月度收入
    """

    def __init__(
        self,
        month = None,
        month_pre_tax_amount = None
    ):
        super().__init__()
        self.month = month
        self.month_pre_tax_amount = month_pre_tax_amount


class LaborCaculatorResponse(BaseRequest):
    """
    连续劳务税费试算（计算器）返回-响应

    :type year_tax_info: YearTaxInfo
    :param year_tax_info: 综合所得汇算清缴

    :type month_tax_list: list
    :param month_tax_list: 月度税务信息列表
    """

    def __init__(
        self,
        year_tax_info = None,
        month_tax_list = None
    ):
        super().__init__()
        self.year_tax_info = year_tax_info
        self.month_tax_list = month_tax_list


class YearTaxInfo(BaseRequest):
    """
    综合所得汇算清缴信息-响应

    :type continuous_month_personal_tax: string
    :param continuous_month_personal_tax: 连续劳务年度个税

    :type personal_tax: string
    :param personal_tax: 综合所得汇算清缴年度个税

    :type deduct_cost: string
    :param deduct_cost: 年度扣除费用

    :type personal_tax_rate: string
    :param personal_tax_rate: 个税税率

    :type deduct_tax: string
    :param deduct_tax: 速算扣除数

    :type total_tax_rate: string
    :param total_tax_rate: 税负率
    """

    def __init__(
        self,
        continuous_month_personal_tax = None,
        personal_tax = None,
        deduct_cost = None,
        personal_tax_rate = None,
        deduct_tax = None,
        total_tax_rate = None
    ):
        super().__init__()
        self.continuous_month_personal_tax = continuous_month_personal_tax
        self.personal_tax = personal_tax
        self.deduct_cost = deduct_cost
        self.personal_tax_rate = personal_tax_rate
        self.deduct_tax = deduct_tax
        self.total_tax_rate = total_tax_rate


class MontTax(BaseRequest):
    """
    月度税务信息-响应

    :type month: int
    :param month: 月份

    :type pre_tax_amount: string
    :param pre_tax_amount: 含增值税收入

    :type excluding_vat_amount: string
    :param excluding_vat_amount: 不含增值税收入

    :type value_added_tax: string
    :param value_added_tax: 增值税

    :type additional_tax: string
    :param additional_tax: 附加税

    :type personal_tax: string
    :param personal_tax: 个税

    :type personal_tax_rate: string
    :param personal_tax_rate: 个税税率

    :type deduct_tax: string
    :param deduct_tax: 速算扣除数

    :type post_tax_amount: string
    :param post_tax_amount: 税后金额

    :type total_tax_rate: string
    :param total_tax_rate: 税负率
    """

    def __init__(
        self,
        month = None,
        pre_tax_amount = None,
        excluding_vat_amount = None,
        value_added_tax = None,
        additional_tax = None,
        personal_tax = None,
        personal_tax_rate = None,
        deduct_tax = None,
        post_tax_amount = None,
        total_tax_rate = None
    ):
        super().__init__()
        self.month = month
        self.pre_tax_amount = pre_tax_amount
        self.excluding_vat_amount = excluding_vat_amount
        self.value_added_tax = value_added_tax
        self.additional_tax = additional_tax
        self.personal_tax = personal_tax
        self.personal_tax_rate = personal_tax_rate
        self.deduct_tax = deduct_tax
        self.post_tax_amount = post_tax_amount
        self.total_tax_rate = total_tax_rate


class CalcTaxRequest(BaseRequest):
    """
    订单税费试算请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号

    :type pay: string
    :param pay: 测算金额

    :type tax_type: string
    :param tax_type: 测算类型
    """

    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        id_card = None,
        pay = None,
        tax_type = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card
        self.pay = pay
        self.tax_type = tax_type


class CalcTaxResponse(BaseRequest):
    """
    订单税费试算返回-响应

    :type pay: string
    :param pay: 测算金额

    :type tax: string
    :param tax: 税费总额

    :type after_tax_amount: string
    :param after_tax_amount: 税后结算金额

    :type tax_detail: CalcTaxDetail
    :param tax_detail: 缴税明细

    :type before_tax_amount: string
    :param before_tax_amount: 税前订单金额

    :type user_tax: string
    :param user_tax: 用户税费总额

    :type dealer_tax: string
    :param dealer_tax: 平台企业税费总额

    :type broker_tax: string
    :param broker_tax: 云账户税费总额

    :type user_fee: string
    :param user_fee: 用户服务费

    :type status: string
    :param status: 结果

    :type status_detail: string
    :param status_detail: 结果详细状态码

    :type status_message: string
    :param status_message: 结果说明

    :type status_detail_message: string
    :param status_detail_message: 结果详细状态码描述

    :type user_real_excluding_vat_amount: string
    :param user_real_excluding_vat_amount: 用户实收金额（未扣除追缴的增附税）

    :type user_remaining_repayment_amount: string
    :param user_remaining_repayment_amount: 用户还未缴清的增附税

    :type user_recover_tax_amount: string
    :param user_recover_tax_amount: 已追缴增附税（本笔订单）

    :type user_total_recover_tax_amount: string
    :param user_total_recover_tax_amount: 待追缴增附税总金额
    """

    def __init__(
        self,
        pay = None,
        tax = None,
        after_tax_amount = None,
        tax_detail = None,
        before_tax_amount = None,
        user_tax = None,
        dealer_tax = None,
        broker_tax = None,
        user_fee = None,
        status = None,
        status_detail = None,
        status_message = None,
        status_detail_message = None,
        user_real_excluding_vat_amount = None,
        user_remaining_repayment_amount = None,
        user_recover_tax_amount = None,
        user_total_recover_tax_amount = None
    ):
        super().__init__()
        self.pay = pay
        self.tax = tax
        self.after_tax_amount = after_tax_amount
        self.tax_detail = tax_detail
        self.before_tax_amount = before_tax_amount
        self.user_tax = user_tax
        self.dealer_tax = dealer_tax
        self.broker_tax = broker_tax
        self.user_fee = user_fee
        self.status = status
        self.status_detail = status_detail
        self.status_message = status_message
        self.status_detail_message = status_detail_message
        self.user_real_excluding_vat_amount = user_real_excluding_vat_amount
        self.user_remaining_repayment_amount = user_remaining_repayment_amount
        self.user_recover_tax_amount = user_recover_tax_amount
        self.user_total_recover_tax_amount = user_total_recover_tax_amount


class CalcTaxDetail(BaseRequest):
    """
    税费明细-响应

    :type personal_tax: string
    :param personal_tax: 预扣个税

    :type value_added_tax: string
    :param value_added_tax: 预扣增值税

    :type additional_tax: string
    :param additional_tax: 预扣附加税费

    :type user_personal_tax: string
    :param user_personal_tax: 用户预扣个税

    :type dealer_personal_tax: string
    :param dealer_personal_tax: 平台企业预扣个税

    :type broker_personal_tax: string
    :param broker_personal_tax: 云账户预扣个税

    :type user_value_added_tax: string
    :param user_value_added_tax: 用户预扣增值税

    :type dealer_value_added_tax: string
    :param dealer_value_added_tax: 平台企业预扣增值税

    :type broker_value_added_tax: string
    :param broker_value_added_tax: 云账户预扣增值税

    :type user_additional_tax: string
    :param user_additional_tax: 用户预扣附加税费

    :type dealer_additional_tax: string
    :param dealer_additional_tax: 平台企业预扣附加税费

    :type broker_additional_tax: string
    :param broker_additional_tax: 云账户预扣附加税费

    :type personal_tax_rate: string
    :param personal_tax_rate: 预扣个税税率

    :type deduct_tax: string
    :param deduct_tax: 预扣个税速算扣除数
    """

    def __init__(
        self,
        personal_tax = None,
        value_added_tax = None,
        additional_tax = None,
        user_personal_tax = None,
        dealer_personal_tax = None,
        broker_personal_tax = None,
        user_value_added_tax = None,
        dealer_value_added_tax = None,
        broker_value_added_tax = None,
        user_additional_tax = None,
        dealer_additional_tax = None,
        broker_additional_tax = None,
        personal_tax_rate = None,
        deduct_tax = None
    ):
        super().__init__()
        self.personal_tax = personal_tax
        self.value_added_tax = value_added_tax
        self.additional_tax = additional_tax
        self.user_personal_tax = user_personal_tax
        self.dealer_personal_tax = dealer_personal_tax
        self.broker_personal_tax = broker_personal_tax
        self.user_value_added_tax = user_value_added_tax
        self.dealer_value_added_tax = dealer_value_added_tax
        self.broker_value_added_tax = broker_value_added_tax
        self.user_additional_tax = user_additional_tax
        self.dealer_additional_tax = dealer_additional_tax
        self.broker_additional_tax = broker_additional_tax
        self.personal_tax_rate = personal_tax_rate
        self.deduct_tax = deduct_tax


class CalculationYearH5UrlRequest(BaseRequest):
    """
    连续劳务年度税费测算-H5 请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type color: string
    :param color: 主题颜色
    """

    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        color = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.color = color


class CalculationYearH5UrlResponse(BaseRequest):
    """
    连续劳务年度税费测算-H5 返回-响应

    :type url: string
    :param url: 年度劳务测算 H5 页面 URL
    """

    def __init__(
        self,
        url = None
    ):
        super().__init__()
        self.url = url


class CalculationH5UrlRequest(BaseRequest):
    """
    连续劳务单笔结算税费测算-H5 请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号

    :type color: string
    :param color: 主题颜色
    """

    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        id_card = None,
        color = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card
        self.color = color


class CalculationH5UrlResponse(BaseRequest):
    """
    连续劳务单笔结算税费测算-H5 返回-响应

    :type url: string
    :param url: 连续劳务单笔结算税费测算 H5 页面 URL
    """

    def __init__(
        self,
        url = None
    ):
        super().__init__()
        self.url = url
