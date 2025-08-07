from foodgram.validators import validate_username


class UsernameValidationMixin:
    def validate_username(self, username):
        return validate_username(username)
