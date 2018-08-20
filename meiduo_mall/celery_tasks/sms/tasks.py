from .yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import celery_app


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """

    :param mobile: 手机号码
    :param sms_code: 短信验证码
    :return: None

    """
    # 发送短信
    ccp = CCP()

    sms_time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
    ccp.send_template_sms(mobile, [sms_code, sms_time], constants.SMS_CODE_TEMPLATE_ID)