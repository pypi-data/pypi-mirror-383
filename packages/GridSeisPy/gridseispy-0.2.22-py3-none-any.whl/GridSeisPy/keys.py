from numpy import nan
from .settings import DefaultSetting


class SeisKeys(DefaultSetting):
    """关键字全部小写（作为 mixin，不参与实例布局）"""

    slots = ()

    # 类级常量（原先实例属性改为类属性）
    _kMD, _kTVD, _kSSTVD, _kTWT = 'md', 'tvd', 'sstvd', 'twt'
    _kINLINE, _kXLINE, _kX, _kY = 'inline', 'xline', 'x', 'y'
    _kITRACE, _kTIME, _kDEPTH = 'itrace', 'time', 'depth'

    _vINV, _sINV, _vNAN = -999.25, '-999.25', nan

    # 类级格式映射
    _format = {
        'i4': ['inline', 'xline', 'itrace'],
        'f4': ['md', 'tvd', 'sstvd', 'twt', 'x', 'y', 'time', 'depth'],
    }

    # 类级开关：True 则 kField 返回 depth，False 则返回 time
    _FIELD_IS_DEPTH: bool = False

    @classmethod
    def set_field_is_depth(cls, flag: bool):
        cls._FIELD_IS_DEPTH = bool(flag)

    def ks2fmts(self, keys):
        """keys to formats"""
        dtype = ['O'] * len(keys)
        for i, k in enumerate(keys):
            for item in type(self)._format.items():
                if k in item[1]:
                    dtype[i] = item[0]
        return dtype

    @property
    def vINV(self): return type(self)._vINV

    @property
    def sINV(self): return type(self)._sINV

    @property
    def vNAN(self): return type(self)._vNAN

    @property
    def kMD(self): return type(self)._kMD

    @property
    def kTVD(self): return type(self)._kTVD

    @property
    def kSSTVD(self): return type(self)._kSSTVD

    @property
    def kTWT(self): return type(self)._kTWT

    @property
    def kINLINE(self): return type(self)._kINLINE

    @property
    def kXLINE(self): return type(self)._kXLINE

    @property
    def kX(self): return type(self)._kX

    @property
    def kY(self): return type(self)._kY

    @property
    def kITRACE(self): return type(self)._kITRACE

    @property
    def kTIME(self): return type(self)._kTIME

    @property
    def kDEPTH(self): return type(self)._kDEPTH

    @property
    def kField(self): return self.kDEPTH if type(self)._FIELD_IS_DEPTH else self.kTIME
