import datetime
import re

from peewee import *
from abc import abstractmethod
from common import *

db = SqliteDatabase('trace.db')


class BaseModel(Model):

    @abstractmethod
    def validation(self):
        pass

    def save(self, **kwargs):
        if self.id is not None:
            self.modified = datetime.datetime.now()
        return super(BaseModel, self).save(**kwargs)

    class Meta:
        database = db


# ユーザテーブル
class User(BaseModel):
    name = CharField(null = True)
    mail = CharField(index = True)
    password = CharField()
    created = DateTimeField(formats = '%Y-%m-%d %H:%M:%S', default = datetime.datetime.now)
    modified = DateTimeField(formats = '%Y-%m-%d %H:%M:%S', default = datetime.datetime.now)

    # TODO: IDがautoincrimentではない

    def validation(self):

        errors = []

        if not self.name:
            errors.append("名前を入力してください。")

        if not self.mail:
            errors.append("メールアドレスを入力してください。")
        elif re.match(r"^([a-zA-Z0-9])+([a-zA-Z0-9\._-])*@([a-zA-Z0-9_-])+([a-zA-Z0-9\._-]+)+$", self.mail) is None:
            errors.append("正しいメールアドレスを入力してください。")
        elif User.select().where(User.mail == self.mail).exists():
            if self.id is None:
                errors.append("このメールアドレスはすでに登録されています。")
            else:
                # TODO: メアド変更時に他のユーザと被っていないかの確認が必要
                pass

        if not self.password:
            errors.append("パスワードを入力してください。")
        elif len(self.password) < 6 or len(self.password) > 12:
            errors.append("パスワードは6〜12文字で入力してください。")

        return errors


    def save(self, **kwargs):
        self.password = cipher.encrypt(self.password)
        return super(User, self).save(**kwargs)


# 位置情報テーブル
class Userlocation(BaseModel):
    user = ForeignKeyField(User)
    lat = DoubleField()
    lng = DoubleField()
    created = DateTimeField(default = datetime.datetime.now)

    def validation(self):

        errors = []

        if self.lat is None:
            errors.append("緯度を入力してください。")

        if self.lng is None:
            errors.append("経度を入力してください。")

        return errors
