from Crypto.Cipher import DES
from django.db.models import CharField, EmailField, IntegerField, TextField, FloatField, SlugField


def pad(text):
    n = len(text) % 8
    return text + (b' ' * (8 - n))


key = b'hello123'
des = DES.new(key, DES.MODE_ECB)


class Secure():
    def encrypt(self, text):
        if not isinstance(text, bytes):
            text = str(text).encode()
        padded_text = pad(text)
        encrypted_text = des.encrypt(padded_text)
        return str(encrypted_text.decode('raw_unicode_escape'))

    def decrypt(self, text):
        decrypted_text = des.decrypt(text.encode("raw_unicode_escape"))
        return decrypted_text.decode().strip()


secure = Secure()


class SecureCharField(CharField):
    def from_db_value(self, value, expression, connection):
        return secure.decrypt(value)

    def get_prep_value(self, value):
        return secure.encrypt(value)


class SecureEmailField(EmailField):
    def from_db_value(self, value, expression, connection):
        return secure.decrypt(value)

    def get_prep_value(self, value):
        return secure.encrypt(value)


class SecureIntegerField(IntegerField):
    def from_db_value(self, value, expression, connection):
        return int(secure.decrypt(value))

    def get_prep_value(self, value):
        return secure.encrypt(str(value))


class SecureTextField(TextField):
    def from_db_value(self, value, expression, connection):
        return secure.decrypt(value)

    def get_prep_value(self, value):
        return secure.encrypt(value)


class SecureFloatField(FloatField):
    def from_db_value(self, value, expression, connection):
        return float(secure.decrypt(value))

    def get_prep_value(self, value):
        return secure.encrypt(str(value))



class SecureSlugField(SlugField):
    def from_db_value(self, value, expression, connection):
        return secure.decrypt(value)

    def get_prep_value(self, value):
        return secure.encrypt(value)
