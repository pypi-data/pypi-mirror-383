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
from bstack_utils.bstack1l1ll11l11_opy_ import bstack1ll1l1lll1l_opy_
from bstack_utils.constants import EVENTS
class bstack1ll1ll11ll1_opy_(bstack1lllll1111l_opy_):
    bstack1l11l111l11_opy_ = bstack1lll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠦᖐ")
    NAME = bstack1lll1_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢᖑ")
    bstack1l1l11l11l1_opy_ = bstack1lll1_opy_ (u"ࠨࡨࡶࡤࡢࡹࡷࡲࠢᖒ")
    bstack1l1l111lll1_opy_ = bstack1lll1_opy_ (u"ࠢࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢᖓ")
    bstack11llll111ll_opy_ = bstack1lll1_opy_ (u"ࠣ࡫ࡱࡴࡺࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᖔ")
    bstack1l1l111llll_opy_ = bstack1lll1_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᖕ")
    bstack1l11l1l11l1_opy_ = bstack1lll1_opy_ (u"ࠥ࡭ࡸࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡮ࡵࡣࠤᖖ")
    bstack11llll11l11_opy_ = bstack1lll1_opy_ (u"ࠦࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠣᖗ")
    bstack11llll11l1l_opy_ = bstack1lll1_opy_ (u"ࠧ࡫࡮ࡥࡧࡧࡣࡦࡺࠢᖘ")
    bstack1ll11111ll1_opy_ = bstack1lll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠ࡫ࡱࡨࡪࡾࠢᖙ")
    bstack1l11lll1111_opy_ = bstack1lll1_opy_ (u"ࠢ࡯ࡧࡺࡷࡪࡹࡳࡪࡱࡱࠦᖚ")
    bstack11lll1lllll_opy_ = bstack1lll1_opy_ (u"ࠣࡩࡨࡸࠧᖛ")
    bstack1l1ll11llll_opy_ = bstack1lll1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨᖜ")
    bstack1l11l111lll_opy_ = bstack1lll1_opy_ (u"ࠥࡻ࠸ࡩࡥࡹࡧࡦࡹࡹ࡫ࡳࡤࡴ࡬ࡴࡹࠨᖝ")
    bstack1l11l111111_opy_ = bstack1lll1_opy_ (u"ࠦࡼ࠹ࡣࡦࡺࡨࡧࡺࡺࡥࡴࡥࡵ࡭ࡵࡺࡡࡴࡻࡱࡧࠧᖞ")
    bstack11lll1llll1_opy_ = bstack1lll1_opy_ (u"ࠧࡷࡵࡪࡶࠥᖟ")
    bstack11llll111l1_opy_: Dict[str, List[Callable]] = dict()
    bstack1l11ll1l1ll_opy_: str
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lll1l1l1ll_opy_: Any
    bstack1l11l111l1l_opy_: Dict
    def __init__(
        self,
        bstack1l11ll1l1ll_opy_: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        bstack1lll1l1l1ll_opy_: Dict[str, Any],
        methods=[bstack1lll1_opy_ (u"ࠨ࡟ࡠ࡫ࡱ࡭ࡹࡥ࡟ࠣᖠ"), bstack1lll1_opy_ (u"ࠢࡴࡶࡤࡶࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࠢᖡ"), bstack1lll1_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࠤᖢ"), bstack1lll1_opy_ (u"ࠤࡴࡹ࡮ࡺࠢᖣ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.bstack1l11ll1l1ll_opy_ = bstack1l11ll1l1ll_opy_
        self.platform_index = platform_index
        self.bstack1lllll111ll_opy_(methods)
        self.bstack1lll1l1l1ll_opy_ = bstack1lll1l1l1ll_opy_
    @staticmethod
    def session_id(target: object, strict=True):
        return bstack1lllll1111l_opy_.get_data(bstack1ll1ll11ll1_opy_.bstack1l1l111lll1_opy_, target, strict)
    @staticmethod
    def hub_url(target: object, strict=True):
        return bstack1lllll1111l_opy_.get_data(bstack1ll1ll11ll1_opy_.bstack1l1l11l11l1_opy_, target, strict)
    @staticmethod
    def bstack11llll11111_opy_(target: object, strict=True):
        return bstack1lllll1111l_opy_.get_data(bstack1ll1ll11ll1_opy_.bstack11llll111ll_opy_, target, strict)
    @staticmethod
    def capabilities(target: object, strict=True):
        return bstack1lllll1111l_opy_.get_data(bstack1ll1ll11ll1_opy_.bstack1l1l111llll_opy_, target, strict)
    @staticmethod
    def bstack1l1lll1l1l1_opy_(instance: bstack1llllll111l_opy_) -> bool:
        return bstack1lllll1111l_opy_.bstack1llll1ll1ll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l11l1l11l1_opy_, False)
    @staticmethod
    def bstack1ll111111ll_opy_(instance: bstack1llllll111l_opy_, default_value=None):
        return bstack1lllll1111l_opy_.bstack1llll1ll1ll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l1l11l11l1_opy_, default_value)
    @staticmethod
    def bstack1ll11llllll_opy_(instance: bstack1llllll111l_opy_, default_value=None):
        return bstack1lllll1111l_opy_.bstack1llll1ll1ll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l1l111llll_opy_, default_value)
    @staticmethod
    def bstack1ll11111111_opy_(hub_url: str, bstack11lll1lll11_opy_=bstack1lll1_opy_ (u"ࠥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠢᖤ")):
        try:
            bstack11llll1111l_opy_ = str(urlparse(hub_url).netloc) if hub_url else None
            return bstack11llll1111l_opy_.endswith(bstack11lll1lll11_opy_)
        except:
            pass
        return False
    @staticmethod
    def bstack1ll1111lll1_opy_(method_name: str):
        return method_name == bstack1lll1_opy_ (u"ࠦࡪࡾࡥࡤࡷࡷࡩࠧᖥ")
    @staticmethod
    def bstack1ll11l1lll1_opy_(method_name: str, *args):
        return (
            bstack1ll1ll11ll1_opy_.bstack1ll1111lll1_opy_(method_name)
            and bstack1ll1ll11ll1_opy_.bstack1l11l1l1lll_opy_(*args) == bstack1ll1ll11ll1_opy_.bstack1l11lll1111_opy_
        )
    @staticmethod
    def bstack1ll111ll11l_opy_(method_name: str, *args):
        if not bstack1ll1ll11ll1_opy_.bstack1ll1111lll1_opy_(method_name):
            return False
        if not bstack1ll1ll11ll1_opy_.bstack1l11l111lll_opy_ in bstack1ll1ll11ll1_opy_.bstack1l11l1l1lll_opy_(*args):
            return False
        bstack1l1lllll1l1_opy_ = bstack1ll1ll11ll1_opy_.bstack1l1llllllll_opy_(*args)
        return bstack1l1lllll1l1_opy_ and bstack1lll1_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᖦ") in bstack1l1lllll1l1_opy_ and bstack1lll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᖧ") in bstack1l1lllll1l1_opy_[bstack1lll1_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢᖨ")]
    @staticmethod
    def bstack1ll111l1111_opy_(method_name: str, *args):
        if not bstack1ll1ll11ll1_opy_.bstack1ll1111lll1_opy_(method_name):
            return False
        if not bstack1ll1ll11ll1_opy_.bstack1l11l111lll_opy_ in bstack1ll1ll11ll1_opy_.bstack1l11l1l1lll_opy_(*args):
            return False
        bstack1l1lllll1l1_opy_ = bstack1ll1ll11ll1_opy_.bstack1l1llllllll_opy_(*args)
        return (
            bstack1l1lllll1l1_opy_
            and bstack1lll1_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᖩ") in bstack1l1lllll1l1_opy_
            and bstack1lll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡣࡳ࡫ࡳࡸࠧᖪ") in bstack1l1lllll1l1_opy_[bstack1lll1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᖫ")]
        )
    @staticmethod
    def bstack1l11l1l1lll_opy_(*args):
        return str(bstack1ll1ll11ll1_opy_.bstack1ll1111ll1l_opy_(*args)).lower()
    @staticmethod
    def bstack1ll1111ll1l_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1llllllll_opy_(*args):
        return args[1] if len(args) > 1 and isinstance(args[1], dict) else None
    @staticmethod
    def bstack11ll1ll1l1_opy_(driver):
        command_executor = getattr(driver, bstack1lll1_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᖬ"), None)
        if not command_executor:
            return None
        hub_url = str(command_executor) if isinstance(command_executor, (str, bytes)) else None
        hub_url = str(command_executor._url) if not hub_url and getattr(command_executor, bstack1lll1_opy_ (u"ࠧࡥࡵࡳ࡮ࠥᖭ"), None) else None
        if not hub_url:
            client_config = getattr(command_executor, bstack1lll1_opy_ (u"ࠨ࡟ࡤ࡮࡬ࡩࡳࡺ࡟ࡤࡱࡱࡪ࡮࡭ࠢᖮ"), None)
            if not client_config:
                return None
            hub_url = getattr(client_config, bstack1lll1_opy_ (u"ࠢࡳࡧࡰࡳࡹ࡫࡟ࡴࡧࡵࡺࡪࡸ࡟ࡢࡦࡧࡶࠧᖯ"), None)
        return hub_url
    def bstack1l11ll11ll1_opy_(self, instance, driver, hub_url: str):
        result = False
        if not hub_url:
            return result
        command_executor = getattr(driver, bstack1lll1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᖰ"), None)
        if command_executor:
            if isinstance(command_executor, (str, bytes)):
                setattr(driver, bstack1lll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᖱ"), hub_url)
                result = True
            elif hasattr(command_executor, bstack1lll1_opy_ (u"ࠥࡣࡺࡸ࡬ࠣᖲ")):
                setattr(command_executor, bstack1lll1_opy_ (u"ࠦࡤࡻࡲ࡭ࠤᖳ"), hub_url)
                result = True
        if result:
            self.bstack1l11ll1l1ll_opy_ = hub_url
            bstack1ll1ll11ll1_opy_.bstack1llll1ll111_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1l1l11l11l1_opy_, hub_url)
            bstack1ll1ll11ll1_opy_.bstack1llll1ll111_opy_(
                instance, bstack1ll1ll11ll1_opy_.bstack1l11l1l11l1_opy_, bstack1ll1ll11ll1_opy_.bstack1ll11111111_opy_(hub_url)
            )
        return result
    @staticmethod
    def bstack1l111lllll1_opy_(bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_]):
        return bstack1lll1_opy_ (u"ࠧࡀࠢᖴ").join((bstack1lllll11ll1_opy_(bstack1lllll1l111_opy_[0]).name, bstack1llllll1l11_opy_(bstack1lllll1l111_opy_[1]).name))
    @staticmethod
    def bstack1ll11lllll1_opy_(bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_], callback: Callable):
        bstack1l11l1111l1_opy_ = bstack1ll1ll11ll1_opy_.bstack1l111lllll1_opy_(bstack1lllll1l111_opy_)
        if not bstack1l11l1111l1_opy_ in bstack1ll1ll11ll1_opy_.bstack11llll111l1_opy_:
            bstack1ll1ll11ll1_opy_.bstack11llll111l1_opy_[bstack1l11l1111l1_opy_] = []
        bstack1ll1ll11ll1_opy_.bstack11llll111l1_opy_[bstack1l11l1111l1_opy_].append(callback)
    def bstack1lllll1llll_opy_(self, instance: bstack1llllll111l_opy_, method_name: str, bstack1lllll1l1l1_opy_: timedelta, *args, **kwargs):
        if not instance or method_name in (bstack1lll1_opy_ (u"ࠨࡳࡵࡣࡵࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࠨᖵ")):
            return
        cmd = args[0] if method_name == bstack1lll1_opy_ (u"ࠢࡦࡺࡨࡧࡺࡺࡥࠣᖶ") and args and type(args) in [list, tuple] and isinstance(args[0], str) else None
        bstack11lll1lll1l_opy_ = bstack1lll1_opy_ (u"ࠣ࠼ࠥᖷ").join(map(str, filter(None, [method_name, cmd])))
        instance.bstack1lll1lll11_opy_(bstack1lll1_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳ࠼ࠥᖸ") + bstack11lll1lll1l_opy_, bstack1lllll1l1l1_opy_)
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
        bstack1l11l1111l1_opy_ = bstack1ll1ll11ll1_opy_.bstack1l111lllll1_opy_(bstack1lllll1l111_opy_)
        self.logger.debug(bstack1lll1_opy_ (u"ࠥࡳࡳࡥࡨࡰࡱ࡮࠾ࠥࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࡀࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᖹ") + str(kwargs) + bstack1lll1_opy_ (u"ࠦࠧᖺ"))
        if bstack1lllll111l1_opy_ == bstack1lllll11ll1_opy_.QUIT:
            if bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.PRE:
                bstack1ll11llll1l_opy_ = bstack1ll1l1lll1l_opy_.bstack1ll11lll11l_opy_(EVENTS.bstack11l1111l1_opy_.value)
                bstack1lllll1111l_opy_.bstack1llll1ll111_opy_(instance, EVENTS.bstack11l1111l1_opy_.value, bstack1ll11llll1l_opy_)
                self.logger.debug(bstack1lll1_opy_ (u"ࠧ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼࡿࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࢀࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡾࠢ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡾࠤᖻ").format(instance, method_name, bstack1lllll111l1_opy_, bstack1l11l1111ll_opy_))
        if bstack1lllll111l1_opy_ == bstack1lllll11ll1_opy_.bstack1llll1l11l1_opy_:
            if bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.POST and not bstack1ll1ll11ll1_opy_.bstack1l1l111lll1_opy_ in instance.data:
                session_id = getattr(target, bstack1lll1_opy_ (u"ࠨࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠥᖼ"), None)
                if session_id:
                    instance.data[bstack1ll1ll11ll1_opy_.bstack1l1l111lll1_opy_] = session_id
        elif (
            bstack1lllll111l1_opy_ == bstack1lllll11ll1_opy_.bstack1lllllll1ll_opy_
            and bstack1ll1ll11ll1_opy_.bstack1l11l1l1lll_opy_(*args) == bstack1ll1ll11ll1_opy_.bstack1l11lll1111_opy_
        ):
            if bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.PRE:
                hub_url = bstack1ll1ll11ll1_opy_.bstack11ll1ll1l1_opy_(target)
                if hub_url:
                    instance.data.update(
                        {
                            bstack1ll1ll11ll1_opy_.bstack1l1l11l11l1_opy_: hub_url,
                            bstack1ll1ll11ll1_opy_.bstack1l11l1l11l1_opy_: bstack1ll1ll11ll1_opy_.bstack1ll11111111_opy_(hub_url),
                            bstack1ll1ll11ll1_opy_.bstack1ll11111ll1_opy_: int(
                                os.environ.get(bstack1lll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠢᖽ"), str(self.platform_index))
                            ),
                        }
                    )
                bstack1l1lllll1l1_opy_ = bstack1ll1ll11ll1_opy_.bstack1l1llllllll_opy_(*args)
                bstack11llll11111_opy_ = bstack1l1lllll1l1_opy_.get(bstack1lll1_opy_ (u"ࠣࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢᖾ"), None) if bstack1l1lllll1l1_opy_ else None
                if isinstance(bstack11llll11111_opy_, dict):
                    instance.data[bstack1ll1ll11ll1_opy_.bstack11llll111ll_opy_] = copy.deepcopy(bstack11llll11111_opy_)
                    instance.data[bstack1ll1ll11ll1_opy_.bstack1l1l111llll_opy_] = bstack11llll11111_opy_
            elif bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.POST:
                if isinstance(result, dict):
                    framework_session_id = result.get(bstack1lll1_opy_ (u"ࠤࡹࡥࡱࡻࡥࠣᖿ"), dict()).get(bstack1lll1_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࡍࡩࠨᗀ"), None)
                    if framework_session_id:
                        instance.data.update(
                            {
                                bstack1ll1ll11ll1_opy_.bstack1l1l111lll1_opy_: framework_session_id,
                                bstack1ll1ll11ll1_opy_.bstack11llll11l11_opy_: datetime.now(tz=timezone.utc),
                            }
                        )
        elif (
            bstack1lllll111l1_opy_ == bstack1lllll11ll1_opy_.bstack1lllllll1ll_opy_
            and bstack1ll1ll11ll1_opy_.bstack1l11l1l1lll_opy_(*args) == bstack1ll1ll11ll1_opy_.bstack11lll1llll1_opy_
            and bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.POST
        ):
            instance.data[bstack1ll1ll11ll1_opy_.bstack11llll11l1l_opy_] = datetime.now(tz=timezone.utc)
        if bstack1l11l1111l1_opy_ in bstack1ll1ll11ll1_opy_.bstack11llll111l1_opy_:
            bstack1l11l11111l_opy_ = None
            for callback in bstack1ll1ll11ll1_opy_.bstack11llll111l1_opy_[bstack1l11l1111l1_opy_]:
                try:
                    bstack1l111llllll_opy_ = callback(self, target, exec, bstack1lllll1l111_opy_, result, *args, **kwargs)
                    if bstack1l11l11111l_opy_ == None:
                        bstack1l11l11111l_opy_ = bstack1l111llllll_opy_
                except Exception as e:
                    self.logger.error(bstack1lll1_opy_ (u"ࠦࡪࡸࡲࡰࡴࠣ࡭ࡳࡼ࡯࡬࡫ࡱ࡫ࠥࡩࡡ࡭࡮ࡥࡥࡨࡱ࠺ࠡࠤᗁ") + str(e) + bstack1lll1_opy_ (u"ࠧࠨᗂ"))
                    traceback.print_exc()
            if bstack1lllll111l1_opy_ == bstack1lllll11ll1_opy_.QUIT:
                if bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.POST:
                    bstack1ll11llll1l_opy_ = bstack1lllll1111l_opy_.bstack1llll1ll1ll_opy_(instance, EVENTS.bstack11l1111l1_opy_.value)
                    if bstack1ll11llll1l_opy_!=None:
                        bstack1ll1l1lll1l_opy_.end(EVENTS.bstack11l1111l1_opy_.value, bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᗃ"), bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠢ࠻ࡧࡱࡨࠧᗄ"), True, None)
            if bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.PRE and callable(bstack1l11l11111l_opy_):
                return bstack1l11l11111l_opy_
            elif bstack1l11l1111ll_opy_ == bstack1llllll1l11_opy_.POST and bstack1l11l11111l_opy_:
                return bstack1l11l11111l_opy_
    def bstack1llll1lll1l_opy_(
        self, method_name, previous_state: bstack1lllll11ll1_opy_, *args, **kwargs
    ) -> bstack1lllll11ll1_opy_:
        if method_name == bstack1lll1_opy_ (u"ࠣࡡࡢ࡭ࡳ࡯ࡴࡠࡡࠥᗅ") or method_name == bstack1lll1_opy_ (u"ࠤࡶࡸࡦࡸࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࠤᗆ"):
            return bstack1lllll11ll1_opy_.bstack1llll1l11l1_opy_
        if method_name == bstack1lll1_opy_ (u"ࠥࡵࡺ࡯ࡴࠣᗇ"):
            return bstack1lllll11ll1_opy_.QUIT
        if method_name == bstack1lll1_opy_ (u"ࠦࡪࡾࡥࡤࡷࡷࡩࠧᗈ"):
            if previous_state != bstack1lllll11ll1_opy_.NONE:
                command_name = bstack1ll1ll11ll1_opy_.bstack1l11l1l1lll_opy_(*args)
                if command_name == bstack1ll1ll11ll1_opy_.bstack1l11lll1111_opy_:
                    return bstack1lllll11ll1_opy_.bstack1llll1l11l1_opy_
            return bstack1lllll11ll1_opy_.bstack1lllllll1ll_opy_
        return bstack1lllll11ll1_opy_.NONE