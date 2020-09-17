import datetime
import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from stock_web.settings import SECRET_KEY


def create_token(payload, minutes=1):
    headers = {
        'typ': 'jwt',
        'alg': 'HS256'
    }
    # 构造payload，原来带有超时时间也可以
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)  # 超时时间1分钟
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm="HS256", headers=headers).decode('utf-8')
    return token


class JwtQueryParamsAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return Response({'msg': 'without token'}, status=status.HTTP_401_UNAUTHORIZED)
        token = token.split(' ')[-1]
        # 1.切割，2.检验时间，3.检测第三段的合法性
        try:
            payload = jwt.decode(token, SECRET_KEY, True)
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed({'code': 1003, 'error': 'token timeout'})
        except jwt.DecodeError:
            raise AuthenticationFailed({'code': 1003, 'error': 'token decode error'})
        except jwt.InvalidTokenError:
            raise AuthenticationFailed({'code': 1003, 'error': 'token Invalid'})

        # 三种操作
        # 1.抛出异常，后续不执行
        # 2.return一个元组（1，2）认证通过，在视图中调用request.user是元组的第一个值；request.auth
        # 3.None
        return payload, token
