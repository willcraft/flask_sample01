
import base64
from Crypto import Random
from Crypto.Cipher import AES

'''
http://qiita.com/teitei_tk/items/0b8bae99a8700452b718
$ python -c "import string, random; print(''.join([random.choice(string.ascii_letters + string.digits) for i in range(50)]))"

'''
SECRET = 'NjVOZ966OqCFz7n1p2dVqGqyNZHFmyUOeEtTGHeG2lPkf7Tw1k'

# Status Code
class Status():

    SUCCESS = 200

    #リソース作成成功
    CREATIVED = 201

    #内容なし 削除成功
    NO_CONTENT = 204

    #リクエストが不正
    BAD_REQUEST = 400

    #認証が必要
    UNAUTHORIZED = 401

    #アクセスが禁止されている
    FORBIDDEN = 403

    #リソースが見つからない
    NOT_FOUND = 404

    #許可されていないメソッド
    METHOD_NOT_ALLOWED = 405

    #受理できない
    NOT_ACCEPTABLE = 406

    #競合
    CONFLICT = 409

    #指定されたメディアタイプがサポートされていない
    UNSUPPORTED_MEDIA_TYPE = 415

    #サーバ内部エラー
    SERVER_ERROR = 500


# 暗号化・復号化
class AESCipher(object):

    def __init__(self, key, block_size = 32):
        self.bs = block_size
        self.key = key[:block_size] if len(key) >= len(str(block_size)) else self._pad(key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

cipher = AESCipher(SECRET)
