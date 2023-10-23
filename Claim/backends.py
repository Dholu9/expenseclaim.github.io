from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmployeeIDBackend(ModelBackend):
    def authenticate(self, request, last_name=None, password=None, **kwargs):
        UserModel = get_user_model()
        if last_name is None:
            return None
        try:
            user = UserModel.objects.get(last_name=last_name)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
