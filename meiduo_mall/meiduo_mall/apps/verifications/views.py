from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.views import APIView
from meiduo_mall.libs import constants
from meiduo_mall.libs.captcha.captcha import captcha
from django.http.response import HttpResponse
from rest_framework.generics import GenericAPIView
from . import serializers
import random
from meiduo_mall.libs.yuntongxun.sms import CCP
from rest_framework.response import Response


class ImageCodeView(APIView):
    """
    图片验证码

    """
    def get(self, request, image_code_id):
        """
        获取图片验证码
        """

        # 生成验证码图片
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type="images/jpg")


class SMSCodeView(GenericAPIView):
    serializer_class = serializers.CheckImageCodeSerializer

    def get(self, request, mobile):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 校验通过，生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 保存验证码及发送记录
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex("send_flag_%s" % mobile, constants.SMS_SEND_INTERVAL, 1)

        # 使用redis管道代替之前的直接执行命令，可以一次执行多条命令
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SMS_SEND_INTERVAL, 1)

        # 让管道执行命令
        pl.execute()

        # 发送短信
        # ccp = CCP()

        # sms_time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        # ccp.send_template_sms(mobile, [sms_code, sms_time], constants.SMS_CODE_TEMPLATE_ID)

        return Response({'message': 'ok'})




