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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import bstack1lll111l11l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1lllll11ll1_opy_,
    bstack1llllll1l11_opy_,
    bstack1llllll111l_opy_,
)
from bstack_utils.helper import  bstack1ll1l1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l111l_opy_ import bstack1ll1ll11ll1_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l11111_opy_, bstack1lll11l11l1_opy_, bstack1ll1llll1ll_opy_, bstack1ll1lllll1l_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1llllll11_opy_ import bstack11ll1l111l_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1l1_opy_ import bstack1lll111lll1_opy_
from bstack_utils.percy import bstack11l11111l1_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1llll111l1l_opy_(bstack1lll111l11l_opy_):
    def __init__(self, bstack1l1l1l111l1_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1l1l1l111l1_opy_ = bstack1l1l1l111l1_opy_
        self.percy = bstack11l11111l1_opy_()
        self.bstack11llllll_opy_ = bstack11ll1l111l_opy_()
        self.bstack1l1l11l1lll_opy_()
        bstack1ll1ll11ll1_opy_.bstack1ll11lllll1_opy_((bstack1lllll11ll1_opy_.bstack1lllllll1ll_opy_, bstack1llllll1l11_opy_.PRE), self.bstack1l1l11llll1_opy_)
        TestFramework.bstack1ll11lllll1_opy_((bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.POST), self.bstack1ll11ll1ll1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l1l11ll1_opy_(self, instance: bstack1llllll111l_opy_, driver: object):
        bstack1l1ll1l1111_opy_ = TestFramework.bstack1lllll11111_opy_(instance.context)
        for t in bstack1l1ll1l1111_opy_:
            bstack1l1l1lll11l_opy_ = TestFramework.bstack1llll1ll1ll_opy_(t, bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_, [])
            if any(instance is d[1] for d in bstack1l1l1lll11l_opy_) or instance == driver:
                return t
    def bstack1l1l11llll1_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        driver: object,
        exec: Tuple[bstack1llllll111l_opy_, str],
        bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1ll1ll11ll1_opy_.bstack1ll1111lll1_opy_(method_name):
                return
            platform_index = f.bstack1llll1ll1ll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1ll11111ll1_opy_, 0)
            bstack1l1l1ll111l_opy_ = self.bstack1l1l1l11ll1_opy_(instance, driver)
            bstack1l1l11ll1l1_opy_ = TestFramework.bstack1llll1ll1ll_opy_(bstack1l1l1ll111l_opy_, TestFramework.bstack1l1l11ll1ll_opy_, None)
            if not bstack1l1l11ll1l1_opy_:
                self.logger.debug(bstack1lll1_opy_ (u"ࠥࡳࡳࡥࡰࡳࡧࡢࡩࡽ࡫ࡣࡶࡶࡨ࠾ࠥࡸࡥࡵࡷࡵࡲ࡮ࡴࡧࠡࡣࡶࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥ࡯ࡳࠡࡰࡲࡸࠥࡿࡥࡵࠢࡶࡸࡦࡸࡴࡦࡦࠥዯ"))
                return
            driver_command = f.bstack1ll1111ll1l_opy_(*args)
            for command in bstack11111111l_opy_:
                if command == driver_command:
                    self.bstack1ll1ll1ll_opy_(driver, platform_index)
            bstack111l1l1l_opy_ = self.percy.bstack1l11l1ll11_opy_()
            if driver_command in bstack11ll1ll1l_opy_[bstack111l1l1l_opy_]:
                self.bstack11llllll_opy_.bstack11lll1l111_opy_(bstack1l1l11ll1l1_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠦࡴࡴ࡟ࡱࡴࡨࡣࡪࡾࡥࡤࡷࡷࡩ࠿ࠦࡥࡳࡴࡲࡶࠧደ"), e)
    def bstack1ll11ll1ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1l1ll11l11_opy_ import bstack1ll1l1lll1l_opy_
        bstack1l1l1lll11l_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_, [])
        if not bstack1l1l1lll11l_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢዱ") + str(kwargs) + bstack1lll1_opy_ (u"ࠨࠢዲ"))
            return
        if len(bstack1l1l1lll11l_opy_) > 1:
            self.logger.debug(bstack1lll1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡤࡳ࡫ࡹࡩࡷࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤዳ") + str(kwargs) + bstack1lll1_opy_ (u"ࠣࠤዴ"))
        bstack1l1l1l11111_opy_, bstack1l1l11l1ll1_opy_ = bstack1l1l1lll11l_opy_[0]
        driver = bstack1l1l1l11111_opy_()
        if not driver:
            self.logger.debug(bstack1lll1_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥድ") + str(kwargs) + bstack1lll1_opy_ (u"ࠥࠦዶ"))
            return
        bstack1l1l11lllll_opy_ = {
            TestFramework.bstack1ll11l1ll1l_opy_: bstack1lll1_opy_ (u"ࠦࡹ࡫ࡳࡵࠢࡱࡥࡲ࡫ࠢዷ"),
            TestFramework.bstack1ll11ll1l1l_opy_: bstack1lll1_opy_ (u"ࠧࡺࡥࡴࡶࠣࡹࡺ࡯ࡤࠣዸ"),
            TestFramework.bstack1l1l11ll1ll_opy_: bstack1lll1_opy_ (u"ࠨࡴࡦࡵࡷࠤࡷ࡫ࡲࡶࡰࠣࡲࡦࡳࡥࠣዹ")
        }
        bstack1l1l1l1111l_opy_ = { key: f.bstack1llll1ll1ll_opy_(instance, key) for key in bstack1l1l11lllll_opy_ }
        bstack1l1l11ll11l_opy_ = [key for key, value in bstack1l1l1l1111l_opy_.items() if not value]
        if bstack1l1l11ll11l_opy_:
            for key in bstack1l1l11ll11l_opy_:
                self.logger.debug(bstack1lll1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࠥዺ") + str(key) + bstack1lll1_opy_ (u"ࠣࠤዻ"))
            return
        platform_index = f.bstack1llll1ll1ll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1ll11111ll1_opy_, 0)
        if self.bstack1l1l1l111l1_opy_.percy_capture_mode == bstack1lll1_opy_ (u"ࠤࡷࡩࡸࡺࡣࡢࡵࡨࠦዼ"):
            bstack111l1111_opy_ = bstack1l1l1l1111l_opy_.get(TestFramework.bstack1l1l11ll1ll_opy_) + bstack1lll1_opy_ (u"ࠥ࠱ࡹ࡫ࡳࡵࡥࡤࡷࡪࠨዽ")
            bstack1ll11llll1l_opy_ = bstack1ll1l1lll1l_opy_.bstack1ll11lll11l_opy_(EVENTS.bstack1l1l11ll111_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack111l1111_opy_,
                bstack1llll11l11_opy_=bstack1l1l1l1111l_opy_[TestFramework.bstack1ll11l1ll1l_opy_],
                bstack11ll111l_opy_=bstack1l1l1l1111l_opy_[TestFramework.bstack1ll11ll1l1l_opy_],
                bstack1lll11111_opy_=platform_index
            )
            bstack1ll1l1lll1l_opy_.end(EVENTS.bstack1l1l11ll111_opy_.value, bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦዾ"), bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥዿ"), True, None, None, None, None, test_name=bstack111l1111_opy_)
    def bstack1ll1ll1ll_opy_(self, driver, platform_index):
        if self.bstack11llllll_opy_.bstack1ll1lll111_opy_() is True or self.bstack11llllll_opy_.capturing() is True:
            return
        self.bstack11llllll_opy_.bstack11111lll_opy_()
        while not self.bstack11llllll_opy_.bstack1ll1lll111_opy_():
            bstack1l1l11ll1l1_opy_ = self.bstack11llllll_opy_.bstack1l1lll11l1_opy_()
            self.bstack1l11l1l1l_opy_(driver, bstack1l1l11ll1l1_opy_, platform_index)
        self.bstack11llllll_opy_.bstack1l11llll11_opy_()
    def bstack1l11l1l1l_opy_(self, driver, bstack1l1lllll1_opy_, platform_index, test=None):
        from bstack_utils.bstack1l1ll11l11_opy_ import bstack1ll1l1lll1l_opy_
        bstack1ll11llll1l_opy_ = bstack1ll1l1lll1l_opy_.bstack1ll11lll11l_opy_(EVENTS.bstack1l11l111l1_opy_.value)
        if test != None:
            bstack1llll11l11_opy_ = getattr(test, bstack1lll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫጀ"), None)
            bstack11ll111l_opy_ = getattr(test, bstack1lll1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬጁ"), None)
            PercySDK.screenshot(driver, bstack1l1lllll1_opy_, bstack1llll11l11_opy_=bstack1llll11l11_opy_, bstack11ll111l_opy_=bstack11ll111l_opy_, bstack1lll11111_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack1l1lllll1_opy_)
        bstack1ll1l1lll1l_opy_.end(EVENTS.bstack1l11l111l1_opy_.value, bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣጂ"), bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢጃ"), True, None, None, None, None, test_name=bstack1l1lllll1_opy_)
    def bstack1l1l11l1lll_opy_(self):
        os.environ[bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࠨጄ")] = str(self.bstack1l1l1l111l1_opy_.success)
        os.environ[bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࡡࡆࡅࡕ࡚ࡕࡓࡇࡢࡑࡔࡊࡅࠨጅ")] = str(self.bstack1l1l1l111l1_opy_.percy_capture_mode)
        self.percy.bstack1l1l11lll1l_opy_(self.bstack1l1l1l111l1_opy_.is_percy_auto_enabled)
        self.percy.bstack1l1l11lll11_opy_(self.bstack1l1l1l111l1_opy_.percy_build_id)