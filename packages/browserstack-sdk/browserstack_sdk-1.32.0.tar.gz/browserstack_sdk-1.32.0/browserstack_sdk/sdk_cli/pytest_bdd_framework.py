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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import bstack1llll1ll1l1_opy_
from browserstack_sdk.sdk_cli.utils.bstack1ll111l1_opy_ import bstack1l111llll1l_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1lll1l11111_opy_,
    bstack1lll11l11l1_opy_,
    bstack1ll1llll1ll_opy_,
    bstack11llllll11l_opy_,
    bstack1ll1lllll1l_opy_,
)
import traceback
from bstack_utils.helper import bstack1l1ll111l11_opy_
from bstack_utils.bstack1l1ll11l11_opy_ import bstack1ll1l1lll1l_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1ll1l1l11ll_opy_ import bstack1llll11l11l_opy_
from browserstack_sdk.sdk_cli.bstack111111111l_opy_ import bstack1llllllll1l_opy_
bstack1l1ll11111l_opy_ = bstack1l1ll111l11_opy_()
bstack1l1ll11l1ll_opy_ = bstack1lll1_opy_ (u"ࠨࡕࡱ࡮ࡲࡥࡩ࡫ࡤࡂࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࡷ࠲ࠨᑂ")
bstack1l111l1111l_opy_ = bstack1lll1_opy_ (u"ࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠥᑃ")
bstack11lllll1l1l_opy_ = bstack1lll1_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࡍࡵ࡯࡬ࡇࡹࡩࡳࡺࠢᑄ")
bstack1l111ll1l1l_opy_ = 1.0
_1l1ll1l111l_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack1l11111lll1_opy_ = bstack1lll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠤᑅ")
    bstack1l111111l1l_opy_ = bstack1lll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹ࡟ࡴࡶࡤࡶࡹ࡫ࡤࠣᑆ")
    bstack1l1111ll1l1_opy_ = bstack1lll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱࡳࡠࡨ࡬ࡲ࡮ࡹࡨࡦࡦࠥᑇ")
    bstack1l1111ll111_opy_ = bstack1lll1_opy_ (u"ࠧࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠ࡮ࡤࡷࡹࡥࡳࡵࡣࡵࡸࡪࡪࠢᑈ")
    bstack1l111111lll_opy_ = bstack1lll1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡ࡯ࡥࡸࡺ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࠤᑉ")
    bstack11lllll11ll_opy_: bool
    bstack111111111l_opy_: bstack1llllllll1l_opy_  = None
    bstack11llllllll1_opy_ = [
        bstack1lll1l11111_opy_.BEFORE_ALL,
        bstack1lll1l11111_opy_.AFTER_ALL,
        bstack1lll1l11111_opy_.BEFORE_EACH,
        bstack1lll1l11111_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack1l1111llll1_opy_: Dict[str, str],
        bstack1ll11l11111_opy_: List[str]=[bstack1lll1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦᑊ")],
        bstack111111111l_opy_: bstack1llllllll1l_opy_ = None,
        bstack1ll1ll1l1l1_opy_=None
    ):
        super().__init__(bstack1ll11l11111_opy_, bstack1l1111llll1_opy_, bstack111111111l_opy_)
        self.bstack11lllll11ll_opy_ = any(bstack1lll1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠧᑋ") in item.lower() for item in bstack1ll11l11111_opy_)
        self.bstack1ll1ll1l1l1_opy_ = bstack1ll1ll1l1l1_opy_
    def track_event(
        self,
        context: bstack11llllll11l_opy_,
        test_framework_state: bstack1lll1l11111_opy_,
        test_hook_state: bstack1ll1llll1ll_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1lll1l11111_opy_.TEST or test_framework_state in PytestBDDFramework.bstack11llllllll1_opy_:
            bstack1l111llll1l_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1lll1l11111_opy_.NONE:
            self.logger.warning(bstack1lll1_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡦࡦࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯ࠥࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦ࠿ࠥᑌ") + str(test_hook_state) + bstack1lll1_opy_ (u"ࠥࠦᑍ"))
            return
        if not self.bstack11lllll11ll_opy_:
            self.logger.warning(bstack1lll1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳࡹࡵࡱࡲࡲࡶࡹ࡫ࡤࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡁࠧᑎ") + str(str(self.bstack1ll11l11111_opy_)) + bstack1lll1_opy_ (u"ࠧࠨᑏ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack1lll1_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡦࡺࡳࡩࡨࡺࡥࡥࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᑐ") + str(kwargs) + bstack1lll1_opy_ (u"ࠢࠣᑑ"))
            return
        instance = self.__1l111l11ll1_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack1lll1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࢀࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡣࡵ࡫ࡸࡃࠢᑒ") + str(args) + bstack1lll1_opy_ (u"ࠤࠥᑓ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack11llllllll1_opy_ and test_hook_state == bstack1ll1llll1ll_opy_.PRE:
                bstack1ll11llll1l_opy_ = bstack1ll1l1lll1l_opy_.bstack1ll11lll11l_opy_(EVENTS.bstack111l1l11_opy_.value)
                name = str(EVENTS.bstack111l1l11_opy_.name)+bstack1lll1_opy_ (u"ࠥ࠾ࠧᑔ")+str(test_framework_state.name)
                TestFramework.bstack1l111l1l1ll_opy_(instance, name, bstack1ll11llll1l_opy_)
        except Exception as e:
            self.logger.debug(bstack1lll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣ࡬ࡴࡵ࡫ࠡࡧࡵࡶࡴࡸࠠࡱࡴࡨ࠾ࠥࢁࡽࠣᑕ").format(e))
        try:
            if test_framework_state == bstack1lll1l11111_opy_.TEST:
                if not TestFramework.bstack1llll1l1111_opy_(instance, TestFramework.bstack11llll1ll11_opy_) and test_hook_state == bstack1ll1llll1ll_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__1l111l1ll1l_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack1lll1_opy_ (u"ࠧࡲ࡯ࡢࡦࡨࡨࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧᑖ") + str(test_hook_state) + bstack1lll1_opy_ (u"ࠨࠢᑗ"))
                if test_hook_state == bstack1ll1llll1ll_opy_.PRE and not TestFramework.bstack1llll1l1111_opy_(instance, TestFramework.bstack1l1ll111lll_opy_):
                    TestFramework.bstack1llll1ll111_opy_(instance, TestFramework.bstack1l1ll111lll_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__1l1111l1111_opy_(instance, args)
                    self.logger.debug(bstack1lll1_opy_ (u"ࠢࡴࡧࡷࠤࡹ࡫ࡳࡵ࠯ࡶࡸࡦࡸࡴࠡࡨࡲࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧᑘ") + str(test_hook_state) + bstack1lll1_opy_ (u"ࠣࠤᑙ"))
                elif test_hook_state == bstack1ll1llll1ll_opy_.POST and not TestFramework.bstack1llll1l1111_opy_(instance, TestFramework.bstack1l1ll1111l1_opy_):
                    TestFramework.bstack1llll1ll111_opy_(instance, TestFramework.bstack1l1ll1111l1_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1lll1_opy_ (u"ࠤࡶࡩࡹࠦࡴࡦࡵࡷ࠱ࡪࡴࡤࠡࡨࡲࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡶࡪ࡬ࠨࠪࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧᑚ") + str(test_hook_state) + bstack1lll1_opy_ (u"ࠥࠦᑛ"))
            elif test_framework_state == bstack1lll1l11111_opy_.STEP:
                if test_hook_state == bstack1ll1llll1ll_opy_.PRE:
                    PytestBDDFramework.__11llll1llll_opy_(instance, args)
                elif test_hook_state == bstack1ll1llll1ll_opy_.POST:
                    PytestBDDFramework.__1l111l111l1_opy_(instance, args)
            elif test_framework_state == bstack1lll1l11111_opy_.LOG and test_hook_state == bstack1ll1llll1ll_opy_.POST:
                PytestBDDFramework.__1l111111l11_opy_(instance, *args)
            elif test_framework_state == bstack1lll1l11111_opy_.LOG_REPORT and test_hook_state == bstack1ll1llll1ll_opy_.POST:
                self.__11lllll1111_opy_(instance, *args)
                self.__1l111l1l11l_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack11llllllll1_opy_:
                self.__1l1111ll1ll_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack1lll1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣ࡬ࡦࡴࡤ࡭ࡧࡧࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧᑜ") + str(instance.ref()) + bstack1lll1_opy_ (u"ࠧࠨᑝ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack1l1111ll11l_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack11llllllll1_opy_ and test_hook_state == bstack1ll1llll1ll_opy_.POST:
                name = str(EVENTS.bstack111l1l11_opy_.name)+bstack1lll1_opy_ (u"ࠨ࠺ࠣᑞ")+str(test_framework_state.name)
                bstack1ll11llll1l_opy_ = TestFramework.bstack1l111ll111l_opy_(instance, name)
                bstack1ll1l1lll1l_opy_.end(EVENTS.bstack111l1l11_opy_.value, bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢᑟ"), bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨᑠ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack1lll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤᑡ").format(e))
    def bstack1l1l1ll1lll_opy_(self):
        return self.bstack11lllll11ll_opy_
    def __11lllllllll_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack1lll1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡳࡧࡶࡹࡱࡺࠢᑢ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1ll1l1lll_opy_(rep, [bstack1lll1_opy_ (u"ࠦࡼ࡮ࡥ࡯ࠤᑣ"), bstack1lll1_opy_ (u"ࠧࡵࡵࡵࡥࡲࡱࡪࠨᑤ"), bstack1lll1_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨᑥ"), bstack1lll1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢᑦ"), bstack1lll1_opy_ (u"ࠣࡵ࡮࡭ࡵࡶࡥࡥࠤᑧ"), bstack1lll1_opy_ (u"ࠤ࡯ࡳࡳ࡭ࡲࡦࡲࡵࡸࡪࡾࡴࠣᑨ")])
        return None
    def __11lllll1111_opy_(self, instance: bstack1lll11l11l1_opy_, *args):
        result = self.__11lllllllll_opy_(*args)
        if not result:
            return
        failure = None
        bstack1111111ll1_opy_ = None
        if result.get(bstack1lll1_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᑩ"), None) == bstack1lll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦᑪ") and len(args) > 1 and getattr(args[1], bstack1lll1_opy_ (u"ࠧ࡫ࡸࡤ࡫ࡱࡪࡴࠨᑫ"), None) is not None:
            failure = [{bstack1lll1_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩᑬ"): [args[1].excinfo.exconly(), result.get(bstack1lll1_opy_ (u"ࠢ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹࠨᑭ"), None)]}]
            bstack1111111ll1_opy_ = bstack1lll1_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤᑮ") if bstack1lll1_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࠧᑯ") in getattr(args[1].excinfo, bstack1lll1_opy_ (u"ࠥࡸࡾࡶࡥ࡯ࡣࡰࡩࠧᑰ"), bstack1lll1_opy_ (u"ࠦࠧᑱ")) else bstack1lll1_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨᑲ")
        bstack1l1111lll1l_opy_ = result.get(bstack1lll1_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢᑳ"), TestFramework.bstack1l1111l111l_opy_)
        if bstack1l1111lll1l_opy_ != TestFramework.bstack1l1111l111l_opy_:
            TestFramework.bstack1llll1ll111_opy_(instance, TestFramework.bstack1l1ll11lll1_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack1l111lll111_opy_(instance, {
            TestFramework.bstack1l11lll1lll_opy_: failure,
            TestFramework.bstack1l111lll11l_opy_: bstack1111111ll1_opy_,
            TestFramework.bstack1l1l1111111_opy_: bstack1l1111lll1l_opy_,
        })
    def __1l111l11ll1_opy_(
        self,
        context: bstack11llllll11l_opy_,
        test_framework_state: bstack1lll1l11111_opy_,
        test_hook_state: bstack1ll1llll1ll_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1lll1l11111_opy_.SETUP_FIXTURE:
            instance = self.__1l11111111l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack1l111ll1l11_opy_ bstack11llllll1l1_opy_ this to be bstack1lll1_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᑴ")
            if test_framework_state == bstack1lll1l11111_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l11111ll11_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1lll1l11111_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack1lll1_opy_ (u"ࠣࡰࡲࡨࡪࠨᑵ"), None), bstack1lll1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᑶ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack1lll1_opy_ (u"ࠥࡲࡴࡪࡥࠣᑷ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack1lll1_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦᑸ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1llll1l111l_opy_(target) if target else None
        return instance
    def __1l1111ll1ll_opy_(
        self,
        instance: bstack1lll11l11l1_opy_,
        test_framework_state: bstack1lll1l11111_opy_,
        test_hook_state: bstack1ll1llll1ll_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack1l1111l1l1l_opy_ = TestFramework.bstack1llll1ll1ll_opy_(instance, PytestBDDFramework.bstack1l111111l1l_opy_, {})
        if not key in bstack1l1111l1l1l_opy_:
            bstack1l1111l1l1l_opy_[key] = []
        bstack1l111ll11ll_opy_ = TestFramework.bstack1llll1ll1ll_opy_(instance, PytestBDDFramework.bstack1l1111ll1l1_opy_, {})
        if not key in bstack1l111ll11ll_opy_:
            bstack1l111ll11ll_opy_[key] = []
        bstack1l1111lll11_opy_ = {
            PytestBDDFramework.bstack1l111111l1l_opy_: bstack1l1111l1l1l_opy_,
            PytestBDDFramework.bstack1l1111ll1l1_opy_: bstack1l111ll11ll_opy_,
        }
        if test_hook_state == bstack1ll1llll1ll_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack1lll1_opy_ (u"ࠧࡱࡥࡺࠤᑹ"): key,
                TestFramework.bstack1l111l111ll_opy_: uuid4().__str__(),
                TestFramework.bstack1l111l11lll_opy_: TestFramework.bstack1l1111l11ll_opy_,
                TestFramework.bstack1l111l1lll1_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack11llll1ll1l_opy_: [],
                TestFramework.bstack1l11111l1l1_opy_: hook_name,
                TestFramework.bstack11lllllll11_opy_: bstack1llll11l11l_opy_.bstack1l111l1ll11_opy_()
            }
            bstack1l1111l1l1l_opy_[key].append(hook)
            bstack1l1111lll11_opy_[PytestBDDFramework.bstack1l1111ll111_opy_] = key
        elif test_hook_state == bstack1ll1llll1ll_opy_.POST:
            bstack1l1111111l1_opy_ = bstack1l1111l1l1l_opy_.get(key, [])
            hook = bstack1l1111111l1_opy_.pop() if bstack1l1111111l1_opy_ else None
            if hook:
                result = self.__11lllllllll_opy_(*args)
                if result:
                    bstack11llll1lll1_opy_ = result.get(bstack1lll1_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢᑺ"), TestFramework.bstack1l1111l11ll_opy_)
                    if bstack11llll1lll1_opy_ != TestFramework.bstack1l1111l11ll_opy_:
                        hook[TestFramework.bstack1l111l11lll_opy_] = bstack11llll1lll1_opy_
                hook[TestFramework.bstack1l111llll11_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack11lllllll11_opy_] = bstack1llll11l11l_opy_.bstack1l111l1ll11_opy_()
                self.bstack1l1111111ll_opy_(hook)
                logs = hook.get(TestFramework.bstack1l111ll11l1_opy_, [])
                self.bstack1l1l1l1lll1_opy_(instance, logs)
                bstack1l111ll11ll_opy_[key].append(hook)
                bstack1l1111lll11_opy_[PytestBDDFramework.bstack1l111111lll_opy_] = key
        TestFramework.bstack1l111lll111_opy_(instance, bstack1l1111lll11_opy_)
        self.logger.debug(bstack1lll1_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡨࡰࡱ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࡻ࡬ࡧࡼࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡫ࡳࡴࡱࡳࡠࡵࡷࡥࡷࡺࡥࡥ࠿ࡾ࡬ࡴࡵ࡫ࡴࡡࡶࡸࡦࡸࡴࡦࡦࢀࠤ࡭ࡵ࡯࡬ࡵࡢࡪ࡮ࡴࡩࡴࡪࡨࡨࡂࠨᑻ") + str(bstack1l111ll11ll_opy_) + bstack1lll1_opy_ (u"ࠣࠤᑼ"))
    def __1l11111111l_opy_(
        self,
        context: bstack11llllll11l_opy_,
        test_framework_state: bstack1lll1l11111_opy_,
        test_hook_state: bstack1ll1llll1ll_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1ll1l1lll_opy_(args[0], [bstack1lll1_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣᑽ"), bstack1lll1_opy_ (u"ࠥࡥࡷ࡭࡮ࡢ࡯ࡨࠦᑾ"), bstack1lll1_opy_ (u"ࠦࡵࡧࡲࡢ࡯ࡶࠦᑿ"), bstack1lll1_opy_ (u"ࠧ࡯ࡤࡴࠤᒀ"), bstack1lll1_opy_ (u"ࠨࡵ࡯࡫ࡷࡸࡪࡹࡴࠣᒁ"), bstack1lll1_opy_ (u"ࠢࡣࡣࡶࡩ࡮ࡪࠢᒂ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack1lll1_opy_ (u"ࠣࡵࡦࡳࡵ࡫ࠢᒃ")) else fixturedef.get(bstack1lll1_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣᒄ"), None)
        fixturename = request.fixturename if hasattr(request, bstack1lll1_opy_ (u"ࠥࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࠣᒅ")) else None
        node = request.node if hasattr(request, bstack1lll1_opy_ (u"ࠦࡳࡵࡤࡦࠤᒆ")) else None
        target = request.node.nodeid if hasattr(node, bstack1lll1_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᒇ")) else None
        baseid = fixturedef.get(bstack1lll1_opy_ (u"ࠨࡢࡢࡵࡨ࡭ࡩࠨᒈ"), None) or bstack1lll1_opy_ (u"ࠢࠣᒉ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack1lll1_opy_ (u"ࠣࡡࡳࡽ࡫ࡻ࡮ࡤ࡫ࡷࡩࡲࠨᒊ")):
            target = PytestBDDFramework.__1l111l1l1l1_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack1lll1_opy_ (u"ࠤ࡯ࡳࡨࡧࡴࡪࡱࡱࠦᒋ")) else None
            if target and not TestFramework.bstack1llll1l111l_opy_(target):
                self.__1l11111ll11_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack1lll1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡪࡦࡲ࡬ࡣࡣࡦ࡯ࠥࡺࡡࡳࡩࡨࡸࡂࢁࡴࡢࡴࡪࡩࡹࢃࠠࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࡂࢁࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࢁࠥࡴ࡯ࡥࡧࡀࡿࡳࡵࡤࡦࡿࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࠧᒌ") + str(test_hook_state) + bstack1lll1_opy_ (u"ࠦࠧᒍ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack1lll1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫ࡤࡦࡨࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡩ࡫ࡦࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡷࡥࡷ࡭ࡥࡵ࠿ࠥᒎ") + str(target) + bstack1lll1_opy_ (u"ࠨࠢᒏ"))
            return None
        instance = TestFramework.bstack1llll1l111l_opy_(target)
        if not instance:
            self.logger.warning(bstack1lll1_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࠣࡩࡻ࡫࡮ࡵ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀ࠲ࢀࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫ࡽࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡢࡢࡵࡨ࡭ࡩࡃࡻࡣࡣࡶࡩ࡮ࡪࡽࠡࡶࡤࡶ࡬࡫ࡴ࠾ࠤᒐ") + str(target) + bstack1lll1_opy_ (u"ࠣࠤᒑ"))
            return None
        bstack1l111lll1ll_opy_ = TestFramework.bstack1llll1ll1ll_opy_(instance, PytestBDDFramework.bstack1l11111lll1_opy_, {})
        if os.getenv(bstack1lll1_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡊࡑࡇࡇࡠࡈࡌ࡜࡙࡛ࡒࡆࡕࠥᒒ"), bstack1lll1_opy_ (u"ࠥ࠵ࠧᒓ")) == bstack1lll1_opy_ (u"ࠦ࠶ࠨᒔ"):
            bstack11lllll11l1_opy_ = bstack1lll1_opy_ (u"ࠧࡀࠢᒕ").join((scope, fixturename))
            bstack11lllll1l11_opy_ = datetime.now(tz=timezone.utc)
            bstack11llllll111_opy_ = {
                bstack1lll1_opy_ (u"ࠨ࡫ࡦࡻࠥᒖ"): bstack11lllll11l1_opy_,
                bstack1lll1_opy_ (u"ࠢࡵࡣࡪࡷࠧᒗ"): PytestBDDFramework.__1l1111l1lll_opy_(request.node, scenario),
                bstack1lll1_opy_ (u"ࠣࡨ࡬ࡼࡹࡻࡲࡦࠤᒘ"): fixturedef,
                bstack1lll1_opy_ (u"ࠤࡶࡧࡴࡶࡥࠣᒙ"): scope,
                bstack1lll1_opy_ (u"ࠥࡸࡾࡶࡥࠣᒚ"): None,
            }
            try:
                if test_hook_state == bstack1ll1llll1ll_opy_.POST and callable(getattr(args[-1], bstack1lll1_opy_ (u"ࠦ࡬࡫ࡴࡠࡴࡨࡷࡺࡲࡴࠣᒛ"), None)):
                    bstack11llllll111_opy_[bstack1lll1_opy_ (u"ࠧࡺࡹࡱࡧࠥᒜ")] = TestFramework.bstack1l1l1llll11_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1ll1llll1ll_opy_.PRE:
                bstack11llllll111_opy_[bstack1lll1_opy_ (u"ࠨࡵࡶ࡫ࡧࠦᒝ")] = uuid4().__str__()
                bstack11llllll111_opy_[PytestBDDFramework.bstack1l111l1lll1_opy_] = bstack11lllll1l11_opy_
            elif test_hook_state == bstack1ll1llll1ll_opy_.POST:
                bstack11llllll111_opy_[PytestBDDFramework.bstack1l111llll11_opy_] = bstack11lllll1l11_opy_
            if bstack11lllll11l1_opy_ in bstack1l111lll1ll_opy_:
                bstack1l111lll1ll_opy_[bstack11lllll11l1_opy_].update(bstack11llllll111_opy_)
                self.logger.debug(bstack1lll1_opy_ (u"ࠢࡶࡲࡧࡥࡹ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࠽ࠣᒞ") + str(bstack1l111lll1ll_opy_[bstack11lllll11l1_opy_]) + bstack1lll1_opy_ (u"ࠣࠤᒟ"))
            else:
                bstack1l111lll1ll_opy_[bstack11lllll11l1_opy_] = bstack11llllll111_opy_
                self.logger.debug(bstack1lll1_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࡃࡻࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࠽ࡼࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡽࠡࡶࡵࡥࡨࡱࡥࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࡶࡁࠧᒠ") + str(len(bstack1l111lll1ll_opy_)) + bstack1lll1_opy_ (u"ࠥࠦᒡ"))
        TestFramework.bstack1llll1ll111_opy_(instance, PytestBDDFramework.bstack1l11111lll1_opy_, bstack1l111lll1ll_opy_)
        self.logger.debug(bstack1lll1_opy_ (u"ࠦࡸࡧࡶࡦࡦࠣࡪ࡮ࡾࡴࡶࡴࡨࡷࡂࢁ࡬ࡦࡰࠫࡸࡷࡧࡣ࡬ࡧࡧࡣ࡫࡯ࡸࡵࡷࡵࡩࡸ࠯ࡽࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࠦᒢ") + str(instance.ref()) + bstack1lll1_opy_ (u"ࠧࠨᒣ"))
        return instance
    def __1l11111ll11_opy_(
        self,
        context: bstack11llllll11l_opy_,
        test_framework_state: bstack1lll1l11111_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1llll1ll1l1_opy_.create_context(target)
        ob = bstack1lll11l11l1_opy_(ctx, self.bstack1ll11l11111_opy_, self.bstack1l1111llll1_opy_, test_framework_state)
        TestFramework.bstack1l111lll111_opy_(ob, {
            TestFramework.bstack1ll1111llll_opy_: context.test_framework_name,
            TestFramework.bstack1l1lll11ll1_opy_: context.test_framework_version,
            TestFramework.bstack11lllll1lll_opy_: [],
            PytestBDDFramework.bstack1l11111lll1_opy_: {},
            PytestBDDFramework.bstack1l1111ll1l1_opy_: {},
            PytestBDDFramework.bstack1l111111l1l_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1llll1ll111_opy_(ob, TestFramework.bstack1l11111l11l_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1llll1ll111_opy_(ob, TestFramework.bstack1ll11111ll1_opy_, context.platform_index)
        TestFramework.bstack1lllll1l11l_opy_[ctx.id] = ob
        self.logger.debug(bstack1lll1_opy_ (u"ࠨࡳࡢࡸࡨࡨࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠠࡤࡶࡻ࠲࡮ࡪ࠽ࡼࡥࡷࡼ࠳࡯ࡤࡾࠢࡷࡥࡷ࡭ࡥࡵ࠿ࡾࡸࡦࡸࡧࡦࡶࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷࡂࠨᒤ") + str(TestFramework.bstack1lllll1l11l_opy_.keys()) + bstack1lll1_opy_ (u"ࠢࠣᒥ"))
        return ob
    @staticmethod
    def __1l1111l1111_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1lll1_opy_ (u"ࠨ࡫ࡧࠫᒦ"): id(step),
                bstack1lll1_opy_ (u"ࠩࡷࡩࡽࡺࠧᒧ"): step.name,
                bstack1lll1_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫᒨ"): step.keyword,
            })
        meta = {
            bstack1lll1_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࠬᒩ"): {
                bstack1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᒪ"): feature.name,
                bstack1lll1_opy_ (u"࠭ࡰࡢࡶ࡫ࠫᒫ"): feature.filename,
                bstack1lll1_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬᒬ"): feature.description
            },
            bstack1lll1_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪᒭ"): {
                bstack1lll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᒮ"): scenario.name
            },
            bstack1lll1_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩᒯ"): steps,
            bstack1lll1_opy_ (u"ࠫࡪࡾࡡ࡮ࡲ࡯ࡩࡸ࠭ᒰ"): PytestBDDFramework.__1l111ll1lll_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1l11111l1ll_opy_: meta
            }
        )
    def bstack1l1111111ll_opy_(self, hook: Dict[str, Any]) -> None:
        bstack1lll1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡶࡴࡩࡥࡴࡵࡨࡷࠥࡺࡨࡦࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡷ࡮ࡳࡩ࡭ࡣࡵࠤࡹࡵࠠࡵࡪࡨࠤࡏࡧࡶࡢࠢ࡬ࡱࡵࡲࡥ࡮ࡧࡱࡸࡦࡺࡩࡰࡰ࠱ࠎࠥࠦࠠࠡࠢࠣࠤ࡚ࠥࡨࡪࡵࠣࡱࡪࡺࡨࡰࡦ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡆ࡬ࡪࡩ࡫ࡴࠢࡷ࡬ࡪࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡯࡮ࡴ࡫ࡧࡩࠥࢄ࠯࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠯ࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡌ࡯ࡳࠢࡨࡥࡨ࡮ࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡪࡲࡳࡰࡥ࡬ࡦࡸࡨࡰࡤ࡬ࡩ࡭ࡧࡶ࠰ࠥࡸࡥࡱ࡮ࡤࡧࡪࡹࠠࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦࠥࡽࡩࡵࡪࠣࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢࠡ࡫ࡱࠤ࡮ࡺࡳࠡࡲࡤࡸ࡭࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡏࡦࠡࡣࠣࡪ࡮ࡲࡥࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡲࡧࡴࡤࡪࡨࡷࠥࡧࠠ࡮ࡱࡧ࡭࡫࡯ࡥࡥࠢ࡫ࡳࡴࡱ࠭࡭ࡧࡹࡩࡱࠦࡦࡪ࡮ࡨ࠰ࠥ࡯ࡴࠡࡥࡵࡩࡦࡺࡥࡴࠢࡤࠤࡑࡵࡧࡆࡰࡷࡶࡾࠦ࡯ࡣ࡬ࡨࡧࡹࠦࡷࡪࡶ࡫ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡦࡨࡸࡦ࡯࡬ࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡕ࡬ࡱ࡮ࡲࡡࡳ࡮ࡼ࠰ࠥ࡯ࡴࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦ࡬ࡰࡥࡤࡸࡪࡪࠠࡪࡰࠣࡌࡴࡵ࡫ࡍࡧࡹࡩࡱ࠵ࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠥࡨࡹࠡࡴࡨࡴࡱࡧࡣࡪࡰࡪࠤࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰ࠴ࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤ࡙࡮ࡥࠡࡥࡵࡩࡦࡺࡥࡥࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࡷࠥࡧࡲࡦࠢࡤࡨࡩ࡫ࡤࠡࡶࡲࠤࡹ࡮ࡥࠡࡪࡲࡳࡰ࠭ࡳࠡࠤ࡯ࡳ࡬ࡹࠢࠡ࡮࡬ࡷࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭࠽ࠤ࡙࡮ࡥࠡࡧࡹࡩࡳࡺࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡧࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡰࡴ࡭ࡳࠡࡣࡱࡨࠥ࡮࡯ࡰ࡭ࠣ࡭ࡳ࡬࡯ࡳ࡯ࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡩࡱࡲ࡯ࡤࡲࡥࡷࡧ࡯ࡣ࡫࡯࡬ࡦࡵ࠽ࠤࡑ࡯ࡳࡵࠢࡲࡪࠥࡖࡡࡵࡪࠣࡳࡧࡰࡥࡤࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡷ࡬ࡪࠦࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡵࡪ࡮ࡧࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠼ࠣࡐ࡮ࡹࡴࠡࡱࡩࠤࡕࡧࡴࡩࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡩࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᒱ")
        global _1l1ll1l111l_opy_
        platform_index = os.environ[bstack1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ᒲ")]
        bstack1l1l1ll1ll1_opy_ = os.path.join(bstack1l1ll11111l_opy_, (bstack1l1ll11l1ll_opy_ + str(platform_index)), bstack1l111l1111l_opy_)
        if not os.path.exists(bstack1l1l1ll1ll1_opy_) or not os.path.isdir(bstack1l1l1ll1ll1_opy_):
            return
        logs = hook.get(bstack1lll1_opy_ (u"ࠢ࡭ࡱࡪࡷࠧᒳ"), [])
        with os.scandir(bstack1l1l1ll1ll1_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1ll1l111l_opy_:
                    self.logger.info(bstack1lll1_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨᒴ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack1lll1_opy_ (u"ࠤࠥᒵ")
                    log_entry = bstack1ll1lllll1l_opy_(
                        kind=bstack1lll1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᒶ"),
                        message=bstack1lll1_opy_ (u"ࠦࠧᒷ"),
                        level=bstack1lll1_opy_ (u"ࠧࠨᒸ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1l1l1l1ll_opy_=entry.stat().st_size,
                        bstack1l1l1ll1l11_opy_=bstack1lll1_opy_ (u"ࠨࡍࡂࡐࡘࡅࡑࡥࡕࡑࡎࡒࡅࡉࠨᒹ"),
                        bstack111111l_opy_=os.path.abspath(entry.path),
                        bstack11llllll1ll_opy_=hook.get(TestFramework.bstack1l111l111ll_opy_)
                    )
                    logs.append(log_entry)
                    _1l1ll1l111l_opy_.add(abs_path)
        platform_index = os.environ[bstack1lll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧᒺ")]
        bstack1l111lll1l1_opy_ = os.path.join(bstack1l1ll11111l_opy_, (bstack1l1ll11l1ll_opy_ + str(platform_index)), bstack1l111l1111l_opy_, bstack11lllll1l1l_opy_)
        if not os.path.exists(bstack1l111lll1l1_opy_) or not os.path.isdir(bstack1l111lll1l1_opy_):
            self.logger.info(bstack1lll1_opy_ (u"ࠣࡐࡲࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤ࡫ࡵࡵ࡯ࡦࠣࡥࡹࡀࠠࡼࡿࠥᒻ").format(bstack1l111lll1l1_opy_))
        else:
            self.logger.info(bstack1lll1_opy_ (u"ࠤࡓࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡪࡷࡵ࡭ࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼ࠾ࠥࢁࡽࠣᒼ").format(bstack1l111lll1l1_opy_))
            with os.scandir(bstack1l111lll1l1_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1ll1l111l_opy_:
                        self.logger.info(bstack1lll1_opy_ (u"ࠥࡔࡦࡺࡨࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡳࡶࡴࡩࡥࡴࡵࡨࡨࠥࢁࡽࠣᒽ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack1lll1_opy_ (u"ࠦࠧᒾ")
                        log_entry = bstack1ll1lllll1l_opy_(
                            kind=bstack1lll1_opy_ (u"࡚ࠧࡅࡔࡖࡢࡅ࡙࡚ࡁࡄࡊࡐࡉࡓ࡚ࠢᒿ"),
                            message=bstack1lll1_opy_ (u"ࠨࠢᓀ"),
                            level=bstack1lll1_opy_ (u"ࠢࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࠦᓁ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1l1l1l1ll_opy_=entry.stat().st_size,
                            bstack1l1l1ll1l11_opy_=bstack1lll1_opy_ (u"ࠣࡏࡄࡒ࡚ࡇࡌࡠࡗࡓࡐࡔࡇࡄࠣᓂ"),
                            bstack111111l_opy_=os.path.abspath(entry.path),
                            bstack1l1l1lllll1_opy_=hook.get(TestFramework.bstack1l111l111ll_opy_)
                        )
                        logs.append(log_entry)
                        _1l1ll1l111l_opy_.add(abs_path)
        hook[bstack1lll1_opy_ (u"ࠤ࡯ࡳ࡬ࡹࠢᓃ")] = logs
    def bstack1l1l1l1lll1_opy_(
        self,
        bstack1l1l1ll111l_opy_: bstack1lll11l11l1_opy_,
        entries: List[bstack1ll1lllll1l_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack1lll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡐࡎࡥࡂࡊࡐࡢࡗࡊ࡙ࡓࡊࡑࡑࡣࡎࡊࠢᓄ"))
        req.platform_index = TestFramework.bstack1llll1ll1ll_opy_(bstack1l1l1ll111l_opy_, TestFramework.bstack1ll11111ll1_opy_)
        req.execution_context.hash = str(bstack1l1l1ll111l_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1l1ll111l_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1l1ll111l_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll1ll1ll_opy_(bstack1l1l1ll111l_opy_, TestFramework.bstack1ll1111llll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll1ll1ll_opy_(bstack1l1l1ll111l_opy_, TestFramework.bstack1l1lll11ll1_opy_)
            log_entry.uuid = entry.bstack11llllll1ll_opy_ if entry.bstack11llllll1ll_opy_ else TestFramework.bstack1llll1ll1ll_opy_(bstack1l1l1ll111l_opy_, TestFramework.bstack1ll11ll1l1l_opy_)
            log_entry.test_framework_state = bstack1l1l1ll111l_opy_.state.name
            log_entry.message = entry.message.encode(bstack1lll1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᓅ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack1lll1_opy_ (u"࡚ࠧࡅࡔࡖࡢࡅ࡙࡚ࡁࡄࡊࡐࡉࡓ࡚ࠢᓆ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1l1l1l1ll_opy_
                log_entry.file_path = entry.bstack111111l_opy_
        def bstack1l1ll1111ll_opy_():
            bstack1l111111l1_opy_ = datetime.now()
            try:
                self.bstack1ll1ll1l1l1_opy_.LogCreatedEvent(req)
                bstack1l1l1ll111l_opy_.bstack1lll1lll11_opy_(bstack1lll1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡ࡯ࡳ࡬ࡥࡣࡳࡧࡤࡸࡪࡪ࡟ࡦࡸࡨࡲࡹࡥࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠥᓇ"), datetime.now() - bstack1l111111l1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1lll1_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࡸ࡫࡮ࡥࡡ࡯ࡳ࡬ࡥࡣࡳࡧࡤࡸࡪࡪ࡟ࡦࡸࡨࡲࡹࡥࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣࡿࢂࠨᓈ").format(str(e)))
                traceback.print_exc()
        self.bstack111111111l_opy_.enqueue(bstack1l1ll1111ll_opy_)
    def __1l111l1l11l_opy_(self, instance) -> None:
        bstack1lll1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡒ࡯ࡢࡦࡶࠤࡨࡻࡳࡵࡱࡰࠤࡹࡧࡧࡴࠢࡩࡳࡷࠦࡴࡩࡧࠣ࡫࡮ࡼࡥ࡯ࠢࡷࡩࡸࡺࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡄࡴࡨࡥࡹ࡫ࡳࠡࡣࠣࡨ࡮ࡩࡴࠡࡥࡲࡲࡹࡧࡩ࡯࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡰࡪࡼࡥ࡭ࠢࡦࡹࡸࡺ࡯࡮ࠢࡰࡩࡹࡧࡤࡢࡶࡤࠤࡷ࡫ࡴࡳ࡫ࡨࡺࡪࡪࠠࡧࡴࡲࡱࠏࠦࠠࠡࠢࠣࠤࠥࠦࡃࡶࡵࡷࡳࡲ࡚ࡡࡨࡏࡤࡲࡦ࡭ࡥࡳࠢࡤࡲࡩࠦࡵࡱࡦࡤࡸࡪࡹࠠࡵࡪࡨࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࠦࡳࡵࡣࡷࡩࠥࡻࡳࡪࡰࡪࠤࡸ࡫ࡴࡠࡵࡷࡥࡹ࡫࡟ࡦࡰࡷࡶ࡮࡫ࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨᓉ")
        bstack1l1111lll11_opy_ = {bstack1lll1_opy_ (u"ࠤࡦࡹࡸࡺ࡯࡮ࡡࡰࡩࡹࡧࡤࡢࡶࡤࠦᓊ"): bstack1llll11l11l_opy_.bstack1l111l1ll11_opy_()}
        TestFramework.bstack1l111lll111_opy_(instance, bstack1l1111lll11_opy_)
    @staticmethod
    def __11llll1llll_opy_(instance, args):
        request, bstack1l111111111_opy_ = args
        bstack1l111111ll1_opy_ = id(bstack1l111111111_opy_)
        bstack1l1111l1l11_opy_ = instance.data[TestFramework.bstack1l11111l1ll_opy_]
        step = next(filter(lambda st: st[bstack1lll1_opy_ (u"ࠪ࡭ࡩ࠭ᓋ")] == bstack1l111111ll1_opy_, bstack1l1111l1l11_opy_[bstack1lll1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᓌ")]), None)
        step.update({
            bstack1lll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩᓍ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack1l1111l1l11_opy_[bstack1lll1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᓎ")]) if st[bstack1lll1_opy_ (u"ࠧࡪࡦࠪᓏ")] == step[bstack1lll1_opy_ (u"ࠨ࡫ࡧࠫᓐ")]), None)
        if index is not None:
            bstack1l1111l1l11_opy_[bstack1lll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᓑ")][index] = step
        instance.data[TestFramework.bstack1l11111l1ll_opy_] = bstack1l1111l1l11_opy_
    @staticmethod
    def __1l111l111l1_opy_(instance, args):
        bstack1lll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡸࡪࡨࡲࠥࡲࡥ࡯ࠢࡤࡶ࡬ࡹࠠࡪࡵࠣ࠶࠱ࠦࡩࡵࠢࡶ࡭࡬ࡴࡩࡧ࡫ࡨࡷࠥࡺࡨࡦࡴࡨࠤ࡮ࡹࠠ࡯ࡱࠣࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡦࡸࡧࡴࠢࡤࡶࡪࠦ࠭ࠡ࡝ࡵࡩࡶࡻࡥࡴࡶ࠯ࠤࡸࡺࡥࡱ࡟ࠍࠤࠥࠦࠠࠡࠢࠣࠤ࡮࡬ࠠࡢࡴࡪࡷࠥࡧࡲࡦࠢ࠶ࠤࡹ࡮ࡥ࡯ࠢࡷ࡬ࡪࠦ࡬ࡢࡵࡷࠤࡻࡧ࡬ࡶࡧࠣ࡭ࡸࠦࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨᓒ")
        bstack1l1111l11l1_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1l111111111_opy_ = args[1]
        bstack1l111111ll1_opy_ = id(bstack1l111111111_opy_)
        bstack1l1111l1l11_opy_ = instance.data[TestFramework.bstack1l11111l1ll_opy_]
        step = None
        if bstack1l111111ll1_opy_ is not None and bstack1l1111l1l11_opy_.get(bstack1lll1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᓓ")):
            step = next(filter(lambda st: st[bstack1lll1_opy_ (u"ࠬ࡯ࡤࠨᓔ")] == bstack1l111111ll1_opy_, bstack1l1111l1l11_opy_[bstack1lll1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᓕ")]), None)
            step.update({
                bstack1lll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬᓖ"): bstack1l1111l11l1_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack1lll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨᓗ"): bstack1lll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᓘ"),
                bstack1lll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫᓙ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack1lll1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫᓚ"): bstack1lll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᓛ"),
                })
        index = next((i for i, st in enumerate(bstack1l1111l1l11_opy_[bstack1lll1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᓜ")]) if st[bstack1lll1_opy_ (u"ࠧࡪࡦࠪᓝ")] == step[bstack1lll1_opy_ (u"ࠨ࡫ࡧࠫᓞ")]), None)
        if index is not None:
            bstack1l1111l1l11_opy_[bstack1lll1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᓟ")][index] = step
        instance.data[TestFramework.bstack1l11111l1ll_opy_] = bstack1l1111l1l11_opy_
    @staticmethod
    def __1l111ll1lll_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack1lll1_opy_ (u"ࠪࡧࡦࡲ࡬ࡴࡲࡨࡧࠬᓠ")):
                examples = list(node.callspec.params[bstack1lll1_opy_ (u"ࠫࡤࡶࡹࡵࡧࡶࡸࡤࡨࡤࡥࡡࡨࡼࡦࡳࡰ࡭ࡧࠪᓡ")].values())
            return examples
        except:
            return []
    def bstack1l1ll1ll11l_opy_(self, instance: bstack1lll11l11l1_opy_, bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_]):
        bstack1l111ll1111_opy_ = (
            PytestBDDFramework.bstack1l1111ll111_opy_
            if bstack1lllll1l111_opy_[1] == bstack1ll1llll1ll_opy_.PRE
            else PytestBDDFramework.bstack1l111111lll_opy_
        )
        hook = PytestBDDFramework.bstack1l111ll1ll1_opy_(instance, bstack1l111ll1111_opy_)
        entries = hook.get(TestFramework.bstack11llll1ll1l_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack11lllll1lll_opy_, []))
        return entries
    def bstack1l1l1lll111_opy_(self, instance: bstack1lll11l11l1_opy_, bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_]):
        bstack1l111ll1111_opy_ = (
            PytestBDDFramework.bstack1l1111ll111_opy_
            if bstack1lllll1l111_opy_[1] == bstack1ll1llll1ll_opy_.PRE
            else PytestBDDFramework.bstack1l111111lll_opy_
        )
        PytestBDDFramework.bstack11lllll1ll1_opy_(instance, bstack1l111ll1111_opy_)
        TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack11lllll1lll_opy_, []).clear()
    @staticmethod
    def bstack1l111ll1ll1_opy_(instance: bstack1lll11l11l1_opy_, bstack1l111ll1111_opy_: str):
        bstack1l111l11l1l_opy_ = (
            PytestBDDFramework.bstack1l1111ll1l1_opy_
            if bstack1l111ll1111_opy_ == PytestBDDFramework.bstack1l111111lll_opy_
            else PytestBDDFramework.bstack1l111111l1l_opy_
        )
        bstack1l111l11l11_opy_ = TestFramework.bstack1llll1ll1ll_opy_(instance, bstack1l111ll1111_opy_, None)
        bstack1l11111llll_opy_ = TestFramework.bstack1llll1ll1ll_opy_(instance, bstack1l111l11l1l_opy_, None) if bstack1l111l11l11_opy_ else None
        return (
            bstack1l11111llll_opy_[bstack1l111l11l11_opy_][-1]
            if isinstance(bstack1l11111llll_opy_, dict) and len(bstack1l11111llll_opy_.get(bstack1l111l11l11_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack11lllll1ll1_opy_(instance: bstack1lll11l11l1_opy_, bstack1l111ll1111_opy_: str):
        hook = PytestBDDFramework.bstack1l111ll1ll1_opy_(instance, bstack1l111ll1111_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack11llll1ll1l_opy_, []).clear()
    @staticmethod
    def __1l111111l11_opy_(instance: bstack1lll11l11l1_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack1lll1_opy_ (u"ࠧ࡭ࡥࡵࡡࡵࡩࡨࡵࡲࡥࡵࠥᓢ"), None)):
            return
        if os.getenv(bstack1lll1_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡒࡏࡈࡕࠥᓣ"), bstack1lll1_opy_ (u"ࠢ࠲ࠤᓤ")) != bstack1lll1_opy_ (u"ࠣ࠳ࠥᓥ"):
            PytestBDDFramework.logger.warning(bstack1lll1_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡪࡰࡪࠤࡨࡧࡰ࡭ࡱࡪࠦᓦ"))
            return
        bstack1l11111l111_opy_ = {
            bstack1lll1_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤᓧ"): (PytestBDDFramework.bstack1l1111ll111_opy_, PytestBDDFramework.bstack1l111111l1l_opy_),
            bstack1lll1_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨᓨ"): (PytestBDDFramework.bstack1l111111lll_opy_, PytestBDDFramework.bstack1l1111ll1l1_opy_),
        }
        for when in (bstack1lll1_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦᓩ"), bstack1lll1_opy_ (u"ࠨࡣࡢ࡮࡯ࠦᓪ"), bstack1lll1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᓫ")):
            bstack1l111l1l111_opy_ = args[1].get_records(when)
            if not bstack1l111l1l111_opy_:
                continue
            records = [
                bstack1ll1lllll1l_opy_(
                    kind=TestFramework.bstack1l1l1l11l1l_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack1lll1_opy_ (u"ࠣ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨࠦᓬ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack1lll1_opy_ (u"ࠤࡦࡶࡪࡧࡴࡦࡦࠥᓭ")) and r.created
                        else None
                    ),
                )
                for r in bstack1l111l1l111_opy_
                if isinstance(getattr(r, bstack1lll1_opy_ (u"ࠥࡱࡪࡹࡳࡢࡩࡨࠦᓮ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack11lllll111l_opy_, bstack1l111l11l1l_opy_ = bstack1l11111l111_opy_.get(when, (None, None))
            bstack1l1111lllll_opy_ = TestFramework.bstack1llll1ll1ll_opy_(instance, bstack11lllll111l_opy_, None) if bstack11lllll111l_opy_ else None
            bstack1l11111llll_opy_ = TestFramework.bstack1llll1ll1ll_opy_(instance, bstack1l111l11l1l_opy_, None) if bstack1l1111lllll_opy_ else None
            if isinstance(bstack1l11111llll_opy_, dict) and len(bstack1l11111llll_opy_.get(bstack1l1111lllll_opy_, [])) > 0:
                hook = bstack1l11111llll_opy_[bstack1l1111lllll_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack11llll1ll1l_opy_ in hook:
                    hook[TestFramework.bstack11llll1ll1l_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack11lllll1lll_opy_, [])
            logs.extend(records)
    @staticmethod
    def __1l111l1ll1l_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1l1lll111l_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__1l1111l1ll1_opy_(request.node, scenario)
        bstack1l111l11111_opy_ = feature.filename
        if not bstack1l1lll111l_opy_ or not test_name or not bstack1l111l11111_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1ll11ll1l1l_opy_: uuid4().__str__(),
            TestFramework.bstack11llll1ll11_opy_: bstack1l1lll111l_opy_,
            TestFramework.bstack1ll11l1ll1l_opy_: test_name,
            TestFramework.bstack1l1l11ll1ll_opy_: bstack1l1lll111l_opy_,
            TestFramework.bstack11lllllll1l_opy_: bstack1l111l11111_opy_,
            TestFramework.bstack1l111l1llll_opy_: PytestBDDFramework.__1l1111l1lll_opy_(feature, scenario),
            TestFramework.bstack1l11111ll1l_opy_: code,
            TestFramework.bstack1l1l1111111_opy_: TestFramework.bstack1l1111l111l_opy_,
            TestFramework.bstack1l11l11l11l_opy_: test_name
        }
    @staticmethod
    def __1l1111l1ll1_opy_(node, scenario):
        if hasattr(node, bstack1lll1_opy_ (u"ࠫࡨࡧ࡬࡭ࡵࡳࡩࡨ࠭ᓯ")):
            parts = node.nodeid.rsplit(bstack1lll1_opy_ (u"ࠧࡡࠢᓰ"))
            params = parts[-1]
            return bstack1lll1_opy_ (u"ࠨࡻࡾࠢ࡞ࡿࢂࠨᓱ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __1l1111l1lll_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack1lll1_opy_ (u"ࠧࡵࡣࡪࡷࠬᓲ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack1lll1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭ᓳ")) else [])
    @staticmethod
    def __1l111l1l1l1_opy_(location):
        return bstack1lll1_opy_ (u"ࠤ࠽࠾ࠧᓴ").join(filter(lambda x: isinstance(x, str), location))