from rest_framework.throttling import UserRateThrottle

class LoginThrottle(UserRateThrottle):
    scope = 'login'

class UsersThrottle(UserRateThrottle):
    scope = 'user'
