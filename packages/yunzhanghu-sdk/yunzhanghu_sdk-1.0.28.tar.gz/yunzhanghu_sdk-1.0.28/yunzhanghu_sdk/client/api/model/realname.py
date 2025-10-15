"""实名信息收集"""

from ...base import BaseRequest


class CollectRealNameInfoRequest(BaseRequest):
    """
    -请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type realname_result: int
    :param realname_result: 实名认证结果

    :type realname_time: string
    :param realname_time: 实名认证通过时间

    :type realname_type: int
    :param realname_type: 实名认证方式

    :type realname_trace_id: string
    :param realname_trace_id: 实名认证唯一可追溯编码

    :type realname_platform: string
    :param realname_platform: 认证平台

    :type face_image: string
    :param face_image: 人脸照片

    :type face_verify_score: string
    :param face_verify_score: 人脸识别验证分数

    :type bank_no: string
    :param bank_no: 银行卡号

    :type bank_phone: string
    :param bank_phone: 银行预留手机号

    :type reviewer: string
    :param reviewer: 平台企业审核人

    :type face_image_collect_type: int
    :param face_image_collect_type: 人脸照片收集类型
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        id_card = None,
        realname_result = None,
        realname_time = None,
        realname_type = None,
        realname_trace_id = None,
        realname_platform = None,
        face_image = None,
        face_verify_score = None,
        bank_no = None,
        bank_phone = None,
        reviewer = None,
        face_image_collect_type = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.id_card = id_card
        self.realname_result = realname_result
        self.realname_time = realname_time
        self.realname_type = realname_type
        self.realname_trace_id = realname_trace_id
        self.realname_platform = realname_platform
        self.face_image = face_image
        self.face_verify_score = face_verify_score
        self.bank_no = bank_no
        self.bank_phone = bank_phone
        self.reviewer = reviewer
        self.face_image_collect_type = face_image_collect_type


class CollectRealNameInfoResponse(BaseRequest):
    """
    -响应

    :type status: string
    :param status: 录入状态
    """
    def __init__(
        self,
        status = None
    ):
        super().__init__()
        self.status = status


class QueryRealNameInfoRequest(BaseRequest):
    """
    -请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        id_card = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.id_card = id_card


class QueryRealNameInfoResponse(BaseRequest):
    """
    -响应

    :type realname_result: int
    :param realname_result: 实名认证结果

    :type realname_time: string
    :param realname_time: 实名认证通过时间

    :type realname_type: int
    :param realname_type: 实名认证方式

    :type realname_trace_id: string
    :param realname_trace_id: 实名认证唯一可追溯编码

    :type realname_platform: string
    :param realname_platform: 认证平台

    :type face_image: string
    :param face_image: 是否存在人脸照片

    :type face_verify_score: string
    :param face_verify_score: 人脸识别验证分数

    :type bank_no: string
    :param bank_no: 银行卡号

    :type bank_phone: string
    :param bank_phone: 银行预留手机号

    :type reviewer: string
    :param reviewer: 平台企业审核人
    """
    def __init__(
        self,
        realname_result = None,
        realname_time = None,
        realname_type = None,
        realname_trace_id = None,
        realname_platform = None,
        face_image = None,
        face_verify_score = None,
        bank_no = None,
        bank_phone = None,
        reviewer = None
    ):
        super().__init__()
        self.realname_result = realname_result
        self.realname_time = realname_time
        self.realname_type = realname_type
        self.realname_trace_id = realname_trace_id
        self.realname_platform = realname_platform
        self.face_image = face_image
        self.face_verify_score = face_verify_score
        self.bank_no = bank_no
        self.bank_phone = bank_phone
        self.reviewer = reviewer
