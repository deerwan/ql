# =============================================================================
# 极验 V4 验证码 w 参数加密模块
# =============================================================================
# Author: deer
# GitHub: https://github.com/deerwan
#
# Copyright (c) deer. All rights reserved.
#
# 转载要求：
#   任何形式的转载、分发、二次开发，都必须完整保留以下版权信息，
#   不得修改或删除本声明的任何内容，且必须明确标注原作者及原出处。
#
#   作者: deer
#   官方地址: https://github.com/deerwan
#   来源项目: ikuuu-checkin
# =============================================================================
import random
import hashlib
import urllib.parse
import binascii
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.PublicKey.RSA import construct
from Crypto.Cipher import PKCS1_v1_5


class LotParser:
    def __init__(self):
        self.mapping = {"(n[17:18]+n[9:10])+.+(n[16:19])+.+(n[23:30])": "n[10:15]"}
        self.lot = []
        self.lot_res = []
        for k, v in self.mapping.items():
            self.lot = self._parse(k)
            self.lot_res = self._parse(v)

    @staticmethod
    def _parse_slice(s):
        return [int(x) for x in s.split(":")]

    @staticmethod
    def _extract(part):
        return re.search(r"\[(.*?)\]", part).group(1)

    def _parse(self, s):
        parts = s.split("+.+")
        parsed = []
        for part in parts:
            if "+" in part:
                subs = part.split("+")
                parsed_subs = [self._parse_slice(self._extract(sub)) for sub in subs]
                parsed.append(parsed_subs)
            else:
                parsed.append([self._parse_slice(self._extract(part))])
        return parsed

    @staticmethod
    def _build_str(parsed, num):
        result = []
        for p in parsed:
            current = []
            for s in p:
                start = s[0]
                end = s[1] + 1 if len(s) > 1 else start + 1
                current.append(num[start:end])
            result.append("".join(current))
        return ".".join(result)

    def get_dict(self, lot_number):
        i = self._build_str(self.lot, lot_number)
        r = self._build_str(self.lot_res, lot_number)
        parts = i.split(".")
        a = {}
        current = a
        for idx, part in enumerate(parts):
            if idx == len(parts) - 1:
                current[part] = r
            else:
                current[part] = current.get(part, {})
                current = current[part]
        return a


lotParser = LotParser()


class Signer:
    encryptor_pubkey = construct(
        (
            int(
                "00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81".lower(),
                16,
            ),
            int("10001", 16),
        )
    )

    @staticmethod
    def rand_uid():
        result = ""
        for _ in range(4):
            result += hex(int(65536 * (1 + random.random())))[2:].zfill(4)[-4:]
        return result

    @staticmethod
    def encrypt_symmetrical_1(o_text, random_str):
        key = random_str.encode("utf-8")
        iv = b"0000000000000000"
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_bytes = cipher.encrypt(pad(o_text.encode("utf-8"), AES.block_size))
        return encrypted_bytes

    @staticmethod
    def encrypt_asymmetric_1(message: str) -> str:
        message_bytes = message.encode("utf-8")
        cipher = PKCS1_v1_5.new(Signer.encryptor_pubkey)
        encrypted_bytes = cipher.encrypt(message_bytes)
        encrypted_hex = binascii.hexlify(encrypted_bytes).decode("utf-8")
        return encrypted_hex

    @staticmethod
    def encrypt_w(raw_input, pt) -> str:
        if not pt or "0" == pt:
            return urllib.parse.quote_plus(raw_input)
        random_uid = Signer.rand_uid()
        if pt == "1":
            enc_key = Signer.encrypt_asymmetric_1(random_uid)
            enc_input = Signer.encrypt_symmetrical_1(raw_input, random_uid)
        else:
            raise NotImplementedError("This type of encryption is not implemented yet.")
        return binascii.hexlify(enc_input).decode() + enc_key

    @staticmethod
    def generate_pow(lot_number_pow, captcha_id_pow, hash_func, hash_version, bits, date, empty) -> dict:
        bit_remainder = bits % 4
        bit_division = bits // 4
        prefix = "0" * bit_division
        pow_string = f"{hash_version}|{bits}|{hash_func}|{date}|{captcha_id_pow}|{lot_number_pow}|{empty}|"
        while True:
            h = Signer.rand_uid()
            combined = pow_string + h
            hashed_value = None
            if hash_func == "md5":
                hashed_value = hashlib.md5(combined.encode("utf-8")).hexdigest()
            elif hash_func == "sha1":
                hashed_value = hashlib.sha1(combined.encode("utf-8")).hexdigest()
            elif hash_func == "sha256":
                hashed_value = hashlib.sha256(combined.encode("utf-8")).hexdigest()
            if bit_remainder == 0:
                if hashed_value.startswith(prefix):
                    return {"pow_msg": pow_string + h, "pow_sign": hashed_value}
            else:
                if hashed_value.startswith(prefix):
                    length = len(prefix)
                    threshold = None
                    if bit_remainder == 1:
                        threshold = 7
                    elif bit_remainder == 2:
                        threshold = 3
                    elif bit_remainder == 3:
                        threshold = 1
                    if length <= threshold:
                        return {"pow_msg": pow_string + h, "pow_sign": hashed_value}
