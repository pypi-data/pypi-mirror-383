# coding: UTF-8
import sys
bstack1111l1_opy_ = sys.version_info [0] == 2
bstack1ll11l_opy_ = 2048
bstack11lll1_opy_ = 7
def bstack1lll1_opy_ (bstack11111l1_opy_):
    global bstack11lll1l_opy_
    bstack1llllll_opy_ = ord (bstack11111l1_opy_ [-1])
    bstack1l1l_opy_ = bstack11111l1_opy_ [:-1]
    bstack1l1_opy_ = bstack1llllll_opy_ % len (bstack1l1l_opy_)
    bstack1ll1lll_opy_ = bstack1l1l_opy_ [:bstack1l1_opy_] + bstack1l1l_opy_ [bstack1l1_opy_:]
    if bstack1111l1_opy_:
        bstack111l_opy_ = unicode () .join ([unichr (ord (char) - bstack1ll11l_opy_ - (bstack1l1l11l_opy_ + bstack1llllll_opy_) % bstack11lll1_opy_) for bstack1l1l11l_opy_, char in enumerate (bstack1ll1lll_opy_)])
    else:
        bstack111l_opy_ = str () .join ([chr (ord (char) - bstack1ll11l_opy_ - (bstack1l1l11l_opy_ + bstack1llllll_opy_) % bstack11lll1_opy_) for bstack1l1l11l_opy_, char in enumerate (bstack1ll1lll_opy_)])
    return eval (bstack111l_opy_)
import os
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1lllll1111l_opy_,
    bstack1llllll111l_opy_,
    bstack1lllll11ll1_opy_,
    bstack1llllll1l11_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
class bstack1lll11ll111_opy_(bstack1lllll1111l_opy_):
    bstack1l11l111l11_opy_ = bstack1lll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠣᐨ")
    bstack1l1l111lll1_opy_ = bstack1lll1_opy_ (u"ࠤࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥࠤᐩ")
    bstack1l1l11l11l1_opy_ = bstack1lll1_opy_ (u"ࠥ࡬ࡺࡨ࡟ࡶࡴ࡯ࠦᐪ")
    bstack1l1l111llll_opy_ = bstack1lll1_opy_ (u"ࠦࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᐫ")
    bstack1l11l111lll_opy_ = bstack1lll1_opy_ (u"ࠧࡽ࠳ࡤࡧࡻࡩࡨࡻࡴࡦࡵࡦࡶ࡮ࡶࡴࠣᐬ")
    bstack1l11l111111_opy_ = bstack1lll1_opy_ (u"ࠨࡷ࠴ࡥࡨࡼࡪࡩࡵࡵࡧࡶࡧࡷ࡯ࡰࡵࡣࡶࡽࡳࡩࠢᐭ")
    NAME = bstack1lll1_opy_ (u"ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦᐮ")
    bstack1l11l111ll1_opy_: Dict[str, List[Callable]] = dict()
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lll1l1l1ll_opy_: Any
    bstack1l11l111l1l_opy_: Dict
    def __init__(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        methods=[bstack1lll1_opy_ (u"ࠣ࡮ࡤࡹࡳࡩࡨࠣᐯ"), bstack1lll1_opy_ (u"ࠤࡦࡳࡳࡴࡥࡤࡶࠥᐰ"), bstack1lll1_opy_ (u"ࠥࡲࡪࡽ࡟ࡱࡣࡪࡩࠧᐱ"), bstack1lll1_opy_ (u"ࠦࡨࡲ࡯ࡴࡧࠥᐲ"), bstack1lll1_opy_ (u"ࠧࡪࡩࡴࡲࡤࡸࡨ࡮ࠢᐳ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.platform_index = platform_index
        self.bstack1lllll111ll_opy_(methods)
    def bstack1lllll1llll_opy_(self, instance: bstack1llllll111l_opy_, method_name: str, bstack1lllll1l1l1_opy_: timedelta, *args, **kwargs):
        pass
    def bstack1llllll11ll_opy_(
        self,
        target: object,
        exec: Tuple[bstack1llllll111l_opy_, str],
        bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1lllll111l1_opy_, bstack1l11l1111ll_opy_ = bstack1lllll1l111_opy_
        bstack1l11l1111l1_opy_ = bstack1lll11ll111_opy_.bstack1l111lllll1_opy_(bstack1lllll1l111_opy_)
        if bstack1l11l1111l1_opy_ in bstack1lll11ll111_opy_.bstack1l11l111ll1_opy_:
            bstack1l11l11111l_opy_ = None
            for callback in bstack1lll11ll111_opy_.bstack1l11l111ll1_opy_[bstack1l11l1111l1_opy_]:
                try:
                    bstack1l111llllll_opy_ = callback(self, target, exec, bstack1lllll1l111_opy_, result, *args, **kwargs)
                    if bstack1l11l11111l_opy_ == None:
                        bstack1l11l11111l_opy_ = bstack1l111llllll_opy_
                except Exception as e:
                    self.logger.error(bstack1lll1_opy_ (u"ࠨࡥࡳࡴࡲࡶࠥ࡯࡮ࡷࡱ࡮࡭ࡳ࡭ࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬࠼ࠣࠦᐴ") + str(e) + bstack1lll1_opy_ (u"ࠢࠣᐵ"))
                    traceback.print_exc()
            if bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.PRE and callable(bstack1l11l11111l_opy_):
                return bstack1l11l11111l_opy_
            elif bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.POST and bstack1l11l11111l_opy_:
                return bstack1l11l11111l_opy_
    def bstack1llll1lll1l_opy_(
        self, method_name, previous_state: bstack1lllll11ll1_opy_, *args, **kwargs
    ) -> bstack1lllll11ll1_opy_:
        if method_name == bstack1lll1_opy_ (u"ࠨ࡮ࡤࡹࡳࡩࡨࠨᐶ") or method_name == bstack1lll1_opy_ (u"ࠩࡦࡳࡳࡴࡥࡤࡶࠪᐷ") or method_name == bstack1lll1_opy_ (u"ࠪࡲࡪࡽ࡟ࡱࡣࡪࡩࠬᐸ"):
            return bstack1lllll11ll1_opy_.bstack1llll1l11l1_opy_
        if method_name == bstack1lll1_opy_ (u"ࠫࡩ࡯ࡳࡱࡣࡷࡧ࡭࠭ᐹ"):
            return bstack1lllll11ll1_opy_.bstack1lllll11l11_opy_
        if method_name == bstack1lll1_opy_ (u"ࠬࡩ࡬ࡰࡵࡨࠫᐺ"):
            return bstack1lllll11ll1_opy_.QUIT
        return bstack1lllll11ll1_opy_.NONE
    @staticmethod
    def bstack1l111lllll1_opy_(bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_]):
        return bstack1lll1_opy_ (u"ࠨ࠺ࠣᐻ").join((bstack1lllll11ll1_opy_(bstack1lllll1l111_opy_[0]).name, bstack1llllll1l11_opy_(bstack1lllll1l111_opy_[1]).name))
    @staticmethod
    def bstack1ll11lllll1_opy_(bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_], callback: Callable):
        bstack1l11l1111l1_opy_ = bstack1lll11ll111_opy_.bstack1l111lllll1_opy_(bstack1lllll1l111_opy_)
        if not bstack1l11l1111l1_opy_ in bstack1lll11ll111_opy_.bstack1l11l111ll1_opy_:
            bstack1lll11ll111_opy_.bstack1l11l111ll1_opy_[bstack1l11l1111l1_opy_] = []
        bstack1lll11ll111_opy_.bstack1l11l111ll1_opy_[bstack1l11l1111l1_opy_].append(callback)
    @staticmethod
    def bstack1ll1111lll1_opy_(method_name: str):
        return True
    @staticmethod
    def bstack1ll11l1lll1_opy_(method_name: str, *args) -> bool:
        return True
    @staticmethod
    def bstack1ll11llllll_opy_(instance: bstack1llllll111l_opy_, default_value=None):
        return bstack1lllll1111l_opy_.bstack1llll1ll1ll_opy_(instance, bstack1lll11ll111_opy_.bstack1l1l111llll_opy_, default_value)
    @staticmethod
    def bstack1l1lll1l1l1_opy_(instance: bstack1llllll111l_opy_) -> bool:
        return True
    @staticmethod
    def bstack1ll111111ll_opy_(instance: bstack1llllll111l_opy_, default_value=None):
        return bstack1lllll1111l_opy_.bstack1llll1ll1ll_opy_(instance, bstack1lll11ll111_opy_.bstack1l1l11l11l1_opy_, default_value)
    @staticmethod
    def bstack1ll1111ll1l_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1ll111ll11l_opy_(method_name: str, *args):
        if not bstack1lll11ll111_opy_.bstack1ll1111lll1_opy_(method_name):
            return False
        if not bstack1lll11ll111_opy_.bstack1l11l111lll_opy_ in bstack1lll11ll111_opy_.bstack1l11l1l1lll_opy_(*args):
            return False
        bstack1l1lllll1l1_opy_ = bstack1lll11ll111_opy_.bstack1l1llllllll_opy_(*args)
        return bstack1l1lllll1l1_opy_ and bstack1lll1_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢᐼ") in bstack1l1lllll1l1_opy_ and bstack1lll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᐽ") in bstack1l1lllll1l1_opy_[bstack1lll1_opy_ (u"ࠤࡶࡧࡷ࡯ࡰࡵࠤᐾ")]
    @staticmethod
    def bstack1ll111l1111_opy_(method_name: str, *args):
        if not bstack1lll11ll111_opy_.bstack1ll1111lll1_opy_(method_name):
            return False
        if not bstack1lll11ll111_opy_.bstack1l11l111lll_opy_ in bstack1lll11ll111_opy_.bstack1l11l1l1lll_opy_(*args):
            return False
        bstack1l1lllll1l1_opy_ = bstack1lll11ll111_opy_.bstack1l1llllllll_opy_(*args)
        return (
            bstack1l1lllll1l1_opy_
            and bstack1lll1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᐿ") in bstack1l1lllll1l1_opy_
            and bstack1lll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡴࡥࡵ࡭ࡵࡺࠢᑀ") in bstack1l1lllll1l1_opy_[bstack1lll1_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᑁ")]
        )
    @staticmethod
    def bstack1l11l1l1lll_opy_(*args):
        return str(bstack1lll11ll111_opy_.bstack1ll1111ll1l_opy_(*args)).lower()