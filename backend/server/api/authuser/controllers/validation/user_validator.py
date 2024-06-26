from pygments.lexers import data

from ..user import CustomUser

class BaseUserValidator:
    def __init__(self, data):
        self.raw_data = data

        self.update = False
        if 'id' in data:
            self.update = True

        self.valid = True
        self.errors = {}

    def set_error(self, key, reason):
        self.valid = False
        self.errors[key] = reason

    def validate_payload(self):
        if not (self.raw_data.get('username') and self.raw_data.get('fullname')
                and self.raw_data.get('email')
            ):
            self.set_error("form", "Missing username, fullname or email")

    def validate_username(self):
        username = self.raw_data.get('username')

        query = CustomUser.objects.filter(username=username)
        if self.update:
            query = query.exclude(id=self.raw_data.get('id'))

        if not username:
            return
        if len(username) > 20:
            self.set_error(key='username', reason='Username too long')
        elif query.exists():
            self.set_error(key='username', reason='Duplicate username')

    def validate_email(self):
        email = self.raw_data.get('email')

        query = CustomUser.objects.filter(email=email)
        if self.update:
            query = query.exclude(id=self.raw_data.get('id'))

        if not email:
            return
        if len(email) > 100:
            self.set_error(key='email', reason='Email too long')
        elif query.exists():
            self.set_error(key='email', reason='Duplicate email')
        elif email and email.endswith('student.42roma.it'):
            self.set_error(key='email', reason='Email cannot be from 42roma.')

    def validate_full_name(self):
        full_name = self.raw_data.get('full_name')
        if not full_name:
            return
        if len(full_name) > 50:
            self.set_error(key='full_name', reason='Name too long')

    def validate(self):
        self.validate_payload()
        self.validate_username()
        self.validate_email()
        self.validate_full_name()
        return self.errors

class UserUpdateValidator(BaseUserValidator):
    pass

class UserStoreValidator(BaseUserValidator):
    def start(self):
        if not (self.raw_data.get('password')):
            self.set_error("form", "Password is missing")

    def validate(self):
        self.start()
        super().validate()
        return self.errors