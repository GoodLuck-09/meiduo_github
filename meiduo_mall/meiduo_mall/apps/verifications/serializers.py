from rest_framework import serializers
from django_redis import get_redis_connection
from redis.exceptions import RedisError
import logging

logger = logging.getLogger('django')


class CheckImageCodeSerializer(serializers.Serializer):
    # 图片验证码序列化器
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4, max_length=4)

    def validate(self, attrs):
        # 校验图片验证码是否正确， 查询redis数据库获取真实的验证码
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        redis_conn = get_redis_connection('verify_codes')

        real_image_id = redis_conn.get('img_%s' % image_code_id)

        if real_image_id is None:
            # 真实验证码不存在或者过期
            raise serializers.ValidationError("无效的图片验证码")
        try:

            # 删除验证码，防止用户对同一个验证码进行请求
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        # 对比  python3 redis返回的是bytes类型的值
        real_image_id = real_image_id.decode()
        if real_image_id.lower() != text.lower():
            raise serializers.ValidationError("图片验证码错误")

        # redis中发送短信验证码的标志，油reids维护60S的时间
        mobile = self.context['view'].kwargs['mobile']

        send_flag = redis_conn.get('send_flag%s' % mobile )

        if send_flag:
            raise serializers.ValidationError("发送短信过于频繁")

        return attrs







