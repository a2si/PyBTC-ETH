from binascii import hexlify, unhexlify
from hashlib import new, sha256
from os import urandom
from requests import get

from base58 import b58encode
from ecdsa import SECP256k1, SigningKey

from sha3 import keccak_256


class Bitcoin:
    def __ripemd160(self, x: bytes):
        d = new('ripemd160')
        d.update(x)

        return d

    def valid(self, address: str) -> bool:
        bad = ['0', 'O', 'I']

        if len(address) != 26 and len(address) != 34:
            return False
        elif not address.startswith('1') and not address.startswith('3'):
            return False
        elif [s for s in address if s in bad]:
            return False

        return True

    def balance(self, address: str) -> float:
        if not self.valid(address):
            raise TypeError

        stat: dict = (
            get(f'https://blockstream.info/api/address/{address}').json()
        )['chain_stats']

        balance: int = stat['funded_txo_sum']-stat['spent_txo_sum']

        return balance/(10**8)

    def gen(self) -> tuple:
        priv_key = urandom(32)
        fullkey = '80' + hexlify(priv_key).decode()

        sha256a = sha256(unhexlify(fullkey)).hexdigest()
        sha256b = sha256(unhexlify(sha256a)).hexdigest()

        WIF = b58encode(unhexlify(fullkey+sha256b[:8]))

        sk = SigningKey.from_string(priv_key, curve=SECP256k1)
        vk = sk.get_verifying_key()

        publ_key = '04' + hexlify(vk.to_string()).decode()

        hash160 = self.__ripemd160(
            sha256(unhexlify(publ_key)).digest()
        ).digest()

        publ_addr_a = b"\x00" + hash160

        checksum = sha256(
            sha256(publ_addr_a).digest()
        ).digest()[:4]

        publ_addr_b = b58encode(publ_addr_a + checksum)

        return [publ_addr_b.decode(), WIF.decode()]


class Ethereum:
    def __addr(self, addr_str: str) -> str:
        out = ''
        keccak = keccak_256()

        addr = addr_str.lower().replace('0x', '')
        keccak.update(addr.encode('ascii'))
        hash_addr = keccak.hexdigest()

        for i, c in enumerate(addr):
            if int(hash_addr[i], 16) >= 8:
                out += c.upper()
            else:
                out += c

        return '0x' + out

    def valid(self, address: str) -> bool:
        if not address.startswith('0x'):
            return False
        elif not self.__addr(address) == address:
            return False

        return True

    def balance(self, address: str) -> float:
        if not self.valid(address):
            raise TypeError

        balance: int = (
            get('https://api.etherscan.io/api?module=account&action=' +
                f'balance&address={address}').json()
        )['result']

        return int(balance)/(10**18)

    def gen(self) -> tuple:
        keccak = keccak_256()

        priv = SigningKey.generate(curve=SECP256k1)
        pub = priv.get_verifying_key().to_string()

        keccak.update(pub)
        address = keccak.hexdigest()[24:]

        return [self.__addr(address), priv.to_string().hex()]
