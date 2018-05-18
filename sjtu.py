import requests
import hashlib
import json
import des
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s	[%(levelname)s] %(message)s"
)

class cardError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo

class card:
    def __init__(self, cardno, password):
        self.token = self.login(cardno, password)
        self.cardno = cardno
        self.password = password

    def login(self, cardno, password):
        logging.info("尝试登录")
        data = {
            "account": cardno,
            "password": des.des_encrypt(password).decode("utf-8"),
            "schoolcode": "SJTU",
            "signtype": "SynCard"
        }
        data = self.sign(data)
        r = requests.post("http://card.sjtu.edu.cn/Api/Account/SignIn", data=data)
        ret = json.loads(r.content)
        try:
            if ret["success"] == False:
                raise cardError(ret["msg"])
            else:
                return ret["msg"]
        except cardError as e:
            logging.error(e)

    def sign(self, payload):
        sign = '&'.join('{}={}'.format(key, value) for key, value in payload.items())
        hl = hashlib.md5()
        s = sign + "SJTUsynj"
        hl.update(s.encode(encoding='utf-8'))
        payload["sign"] = hl.hexdigest()
        return payload

    def getCardEaccInfo(self):
        logging.info("获取卡账户信息")
        data = {
            "iplanetdirectorypro": self.token
        }
        data = self.sign(data)

        r = requests.post("http://card.sjtu.edu.cn/Api/Card/GetCardEaccInfo", data=data)
        return json.loads(r.content)

    def getCardInfo(self):
        logging.info("获取卡信息")
        data = {
            "iplanetdirectorypro": self.token,
            "schoolcode": "SJTU"
        }
        data = self.sign(data)

        r = requests.post("http://card.sjtu.edu.cn/Api/Card/GetCardInfo", data=data)
        return json.loads(r.content)

    def bankTransfer(self, amount):
        logging.info("银行卡转账￥" + str(amount))
        data = {
            "amount": str(amount),
            "iplanetdirectorypro": self.token,
            "password": des.des_encrypt(self.password).decode("utf-8"),
            "schoolcode": "SJTU",
            "toaccount": "card"
        }
        data = self.sign(data)

        r = requests.post("http://card.sjtu.edu.cn/Api/Card/BankTransferPlus", data=data)
        ret = json.loads(r.content)
        try:
            if ret["success"] == False:
                raise cardError(ret["msg"])
            else:
                return ret
        except cardError as e:
            logging.error(e)

    def getXiaoQu(self):
        logging.info("获取校区")
        data = {
            "iplanetdirectorypro": self.token,
            "paytypecode": "PowerFeeSims",
            "schoolcode": "SJTU"
        }
        data = self.sign(data)

        r = requests.post("http://card.sjtu.edu.cn/Api/PowerFee/GetXiaoQu", data=data)
        return json.loads(r.content)

    def getBuild(self, xqid):
        logging.info("获取寝室楼")
        data = {
            "iplanetdirectorypro": self.token,
            "paytypecode": "PowerFeeSims",
            "schoolcode": "SJTU",
            "xiaoqu": str(xqid)
        }
        data = self.sign(data)

        r = requests.post("http://card.sjtu.edu.cn/Api/PowerFee/GetBuild", data=data)
        return json.loads(r.content)

    def getBalance(self, xiaoqu, building, buildname, room):
        logging.info("查询 %s %s %s 剩余电费" % (xiaoqu, buildname, room))
        data = {
            "build": building,
            "buildname": buildname,
            "iplanetdirectorypro": self.token,
            "paytypecode": "PowerFeeSims",
            "room": room,
            "schoolcode": "SJTU",
            "xiaoqu": xiaoqu
        }
        data = self.sign(data)

        r = requests.post("http://card.sjtu.edu.cn/Api/PowerFee/GetBanlace", data=data)
        ret = json.loads(r.content)
        try:
            if ret["success"] == False:
                raise cardError(ret["msg"])
            else:
                return ret["obj"]
        except cardError as e:
            logging.error(e)

    def checkLogin(self):
        ret = self.getCardEaccInfo()
        if ret["msg"] == 'NL':
            self.token = self.login(self.cardno, self.password)
            return False
        return ret["obj"]
