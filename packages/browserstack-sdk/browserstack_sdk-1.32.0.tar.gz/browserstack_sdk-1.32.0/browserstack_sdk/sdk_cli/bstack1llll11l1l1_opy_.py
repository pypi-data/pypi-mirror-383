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
import json
import time
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1lllll11ll1_opy_,
    bstack1llllll1l11_opy_,
    bstack1lllll1111l_opy_,
    bstack1llllll111l_opy_,
    bstack1lllll1ll11_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll11l111l_opy_ import bstack1ll1ll11ll1_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_, bstack1lll11l11l1_opy_
from browserstack_sdk.sdk_cli.bstack1l1llll1lll_opy_ import bstack1l1llll11l1_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l1ll11l1_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1lll111lll1_opy_(bstack1l1llll11l1_opy_):
    bstack1l1l11111l1_opy_ = bstack1lll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡥࡴ࡬ࡺࡪࡸࡳࠣᏕ")
    bstack1l1lll111l1_opy_ = bstack1lll1_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤᏖ")
    bstack1l11llllll1_opy_ = bstack1lll1_opy_ (u"ࠦࡳࡵ࡮ࡠࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠨᏗ")
    bstack1l11lll1l11_opy_ = bstack1lll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧᏘ")
    bstack1l11lll11ll_opy_ = bstack1lll1_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡤࡸࡥࡧࡵࠥᏙ")
    bstack1l1ll11l111_opy_ = bstack1lll1_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡩࡲࡦࡣࡷࡩࡩࠨᏚ")
    bstack1l11lllllll_opy_ = bstack1lll1_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥ࡮ࡢ࡯ࡨࠦᏛ")
    bstack1l1l111111l_opy_ = bstack1lll1_opy_ (u"ࠤࡦࡦࡹࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡴࡶࡤࡸࡺࡹࠢᏜ")
    def __init__(self):
        super().__init__(bstack1l1llll1ll1_opy_=self.bstack1l1l11111l1_opy_, frameworks=[bstack1ll1ll11ll1_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll11lllll1_opy_((bstack1lll1l11111_opy_.BEFORE_EACH, bstack1ll1llll1ll_opy_.POST), self.bstack1l11l11l1l1_opy_)
        TestFramework.bstack1ll11lllll1_opy_((bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.PRE), self.bstack1ll111lll11_opy_)
        TestFramework.bstack1ll11lllll1_opy_((bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.POST), self.bstack1ll11ll1ll1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l11l1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1l1lll11l_opy_ = self.bstack1l11l11llll_opy_(instance.context)
        if not bstack1l1l1lll11l_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠥࡷࡪࡺ࡟ࡢࡥࡷ࡭ࡻ࡫࡟ࡥࡴ࡬ࡺࡪࡸࡳ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࠨᏝ") + str(bstack1lllll1l111_opy_) + bstack1lll1_opy_ (u"ࠦࠧᏞ"))
        f.bstack1llll1ll111_opy_(instance, bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_, bstack1l1l1lll11l_opy_)
        bstack1l11l1l1111_opy_ = self.bstack1l11l11llll_opy_(instance.context, bstack1l11l11ll11_opy_=False)
        f.bstack1llll1ll111_opy_(instance, bstack1lll111lll1_opy_.bstack1l11llllll1_opy_, bstack1l11l1l1111_opy_)
    def bstack1ll111lll11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l11l1l1_opy_(f, instance, bstack1lllll1l111_opy_, *args, **kwargs)
        if not f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l11lllllll_opy_, False):
            self.__1l11l1l11ll_opy_(f,instance,bstack1lllll1l111_opy_)
    def bstack1ll11ll1ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l11l1l1_opy_(f, instance, bstack1lllll1l111_opy_, *args, **kwargs)
        if not f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l11lllllll_opy_, False):
            self.__1l11l1l11ll_opy_(f, instance, bstack1lllll1l111_opy_)
        if not f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1l111111l_opy_, False):
            self.__1l11l1l1l11_opy_(f, instance, bstack1lllll1l111_opy_)
    def bstack1l11l1l111l_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        driver: object,
        exec: Tuple[bstack1llllll111l_opy_, str],
        bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1l1lll1l1l1_opy_(instance):
            return
        if f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1l111111l_opy_, False):
            return
        driver.execute_script(
            bstack1lll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠥᏟ").format(
                json.dumps(
                    {
                        bstack1lll1_opy_ (u"ࠨࡡࡤࡶ࡬ࡳࡳࠨᏠ"): bstack1lll1_opy_ (u"ࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥᏡ"),
                        bstack1lll1_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦᏢ"): {bstack1lll1_opy_ (u"ࠤࡶࡸࡦࡺࡵࡴࠤᏣ"): result},
                    }
                )
            )
        )
        f.bstack1llll1ll111_opy_(instance, bstack1lll111lll1_opy_.bstack1l1l111111l_opy_, True)
    def bstack1l11l11llll_opy_(self, context: bstack1lllll1ll11_opy_, bstack1l11l11ll11_opy_= True):
        if bstack1l11l11ll11_opy_:
            bstack1l1l1lll11l_opy_ = self.bstack1l1lll1l1ll_opy_(context, reverse=True)
        else:
            bstack1l1l1lll11l_opy_ = self.bstack1l1llll1l1l_opy_(context, reverse=True)
        return [f for f in bstack1l1l1lll11l_opy_ if f[1].state != bstack1lllll11ll1_opy_.QUIT]
    @measure(event_name=EVENTS.bstack1111111l1_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def __1l11l1l1l11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1lll1_opy_ (u"ࠥࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠣᏤ")).get(bstack1lll1_opy_ (u"ࠦࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣᏥ")):
            bstack1l1l1lll11l_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_, [])
            if not bstack1l1l1lll11l_opy_:
                self.logger.debug(bstack1lll1_opy_ (u"ࠧࡹࡥࡵࡡࡤࡧࡹ࡯ࡶࡦࡡࡧࡶ࡮ࡼࡥࡳࡵ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࠣᏦ") + str(bstack1lllll1l111_opy_) + bstack1lll1_opy_ (u"ࠨࠢᏧ"))
                return
            driver = bstack1l1l1lll11l_opy_[0][0]()
            status = f.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1l1l1111111_opy_, None)
            if not status:
                self.logger.debug(bstack1lll1_opy_ (u"ࠢࡴࡧࡷࡣࡦࡩࡴࡪࡸࡨࡣࡩࡸࡩࡷࡧࡵࡷ࠿ࠦ࡮ࡰࠢࡶࡸࡦࡺࡵࡴࠢࡩࡳࡷࠦࡴࡦࡵࡷ࠰ࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࠤᏨ") + str(bstack1lllll1l111_opy_) + bstack1lll1_opy_ (u"ࠣࠤᏩ"))
                return
            bstack1l11llll1l1_opy_ = {bstack1lll1_opy_ (u"ࠤࡶࡸࡦࡺࡵࡴࠤᏪ"): status.lower()}
            bstack1l11llll1ll_opy_ = f.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1l11lll1lll_opy_, None)
            if status.lower() == bstack1lll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᏫ") and bstack1l11llll1ll_opy_ is not None:
                bstack1l11llll1l1_opy_[bstack1lll1_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫᏬ")] = bstack1l11llll1ll_opy_[0][bstack1lll1_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨᏭ")][0] if isinstance(bstack1l11llll1ll_opy_, list) else str(bstack1l11llll1ll_opy_)
            driver.execute_script(
                bstack1lll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠦᏮ").format(
                    json.dumps(
                        {
                            bstack1lll1_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࠢᏯ"): bstack1lll1_opy_ (u"ࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦᏰ"),
                            bstack1lll1_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧᏱ"): bstack1l11llll1l1_opy_,
                        }
                    )
                )
            )
            f.bstack1llll1ll111_opy_(instance, bstack1lll111lll1_opy_.bstack1l1l111111l_opy_, True)
    @measure(event_name=EVENTS.bstack1ll1llll_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def __1l11l1l11ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1lll1_opy_ (u"ࠥࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠣᏲ")).get(bstack1lll1_opy_ (u"ࠦࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨᏳ")):
            test_name = f.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1l11l11l11l_opy_, None)
            if not test_name:
                self.logger.debug(bstack1lll1_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠ࡮࡫ࡶࡷ࡮ࡴࡧࠡࡶࡨࡷࡹࠦ࡮ࡢ࡯ࡨࠦᏴ"))
                return
            bstack1l1l1lll11l_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_, [])
            if not bstack1l1l1lll11l_opy_:
                self.logger.debug(bstack1lll1_opy_ (u"ࠨࡳࡦࡶࡢࡥࡨࡺࡩࡷࡧࡢࡨࡷ࡯ࡶࡦࡴࡶ࠾ࠥࡴ࡯ࠡࡵࡷࡥࡹࡻࡳࠡࡨࡲࡶࠥࡺࡥࡴࡶ࠯ࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࠣᏵ") + str(bstack1lllll1l111_opy_) + bstack1lll1_opy_ (u"ࠢࠣ᏶"))
                return
            for bstack1l1l1l11111_opy_, bstack1l11l11ll1l_opy_ in bstack1l1l1lll11l_opy_:
                if not bstack1ll1ll11ll1_opy_.bstack1l1lll1l1l1_opy_(bstack1l11l11ll1l_opy_):
                    continue
                driver = bstack1l1l1l11111_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack1lll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂࠨ᏷").format(
                        json.dumps(
                            {
                                bstack1lll1_opy_ (u"ࠤࡤࡧࡹ࡯࡯࡯ࠤᏸ"): bstack1lll1_opy_ (u"ࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦᏹ"),
                                bstack1lll1_opy_ (u"ࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢᏺ"): {bstack1lll1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᏻ"): test_name},
                            }
                        )
                    )
                )
            f.bstack1llll1ll111_opy_(instance, bstack1lll111lll1_opy_.bstack1l11lllllll_opy_, True)
    def bstack1l1ll1ll1ll_opy_(
        self,
        instance: bstack1lll11l11l1_opy_,
        f: TestFramework,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l11l1l1_opy_(f, instance, bstack1lllll1l111_opy_, *args, **kwargs)
        bstack1l1l1lll11l_opy_ = [d for d, _ in f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_, [])]
        if not bstack1l1l1lll11l_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡷࡪࡹࡳࡪࡱࡱࡷࠥࡺ࡯ࠡ࡮࡬ࡲࡰࠨᏼ"))
            return
        if not bstack1l1l1ll11l1_opy_():
            self.logger.debug(bstack1lll1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࡸࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠧᏽ"))
            return
        for bstack1l11l11lll1_opy_ in bstack1l1l1lll11l_opy_:
            driver = bstack1l11l11lll1_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack1lll1_opy_ (u"ࠣࡑࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࡔࡻࡱࡧ࠿ࠨ᏾") + str(timestamp)
            driver.execute_script(
                bstack1lll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠢ᏿").format(
                    json.dumps(
                        {
                            bstack1lll1_opy_ (u"ࠥࡥࡨࡺࡩࡰࡰࠥ᐀"): bstack1lll1_opy_ (u"ࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨᐁ"),
                            bstack1lll1_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣᐂ"): {
                                bstack1lll1_opy_ (u"ࠨࡴࡺࡲࡨࠦᐃ"): bstack1lll1_opy_ (u"ࠢࡂࡰࡱࡳࡹࡧࡴࡪࡱࡱࠦᐄ"),
                                bstack1lll1_opy_ (u"ࠣࡦࡤࡸࡦࠨᐅ"): data,
                                bstack1lll1_opy_ (u"ࠤ࡯ࡩࡻ࡫࡬ࠣᐆ"): bstack1lll1_opy_ (u"ࠥࡨࡪࡨࡵࡨࠤᐇ")
                            }
                        }
                    )
                )
            )
    def bstack1l1l1lll1l1_opy_(
        self,
        instance: bstack1lll11l11l1_opy_,
        f: TestFramework,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l11l1l1_opy_(f, instance, bstack1lllll1l111_opy_, *args, **kwargs)
        keys = [
            bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_,
            bstack1lll111lll1_opy_.bstack1l11llllll1_opy_,
        ]
        bstack1l1l1lll11l_opy_ = []
        for key in keys:
            bstack1l1l1lll11l_opy_.extend(f.bstack1llll1ll1ll_opy_(instance, key, []))
        if not bstack1l1l1lll11l_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡻ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡲࡩࠦࡡ࡯ࡻࠣࡷࡪࡹࡳࡪࡱࡱࡷࠥࡺ࡯ࠡ࡮࡬ࡲࡰࠨᐈ"))
            return
        if f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1ll11l111_opy_, False):
            self.logger.debug(bstack1lll1_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦࡃࡃࡖࠣࡥࡱࡸࡥࡢࡦࡼࠤࡨࡸࡥࡢࡶࡨࡨࠧᐉ"))
            return
        self.bstack1ll11l11ll1_opy_()
        bstack1l111111l1_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1ll11111ll1_opy_)
        req.test_framework_name = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1ll1111llll_opy_)
        req.test_framework_version = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1l1lll11ll1_opy_)
        req.test_framework_state = bstack1lllll1l111_opy_[0].name
        req.test_hook_state = bstack1lllll1l111_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1ll11ll1l1l_opy_)
        for bstack1l1l1l11111_opy_, driver in bstack1l1l1lll11l_opy_:
            try:
                webdriver = bstack1l1l1l11111_opy_()
                if webdriver is None:
                    self.logger.debug(bstack1lll1_opy_ (u"ࠨࡗࡦࡤࡇࡶ࡮ࡼࡥࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤ࡮ࡹࠠࡏࡱࡱࡩࠥ࠮ࡲࡦࡨࡨࡶࡪࡴࡣࡦࠢࡨࡼࡵ࡯ࡲࡦࡦࠬࠦᐊ"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack1lll1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠨᐋ")
                    if bstack1ll1ll11ll1_opy_.bstack1llll1ll1ll_opy_(driver, bstack1ll1ll11ll1_opy_.bstack1l11l1l11l1_opy_, False)
                    else bstack1lll1_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࡡࡪࡶ࡮ࡪࠢᐌ")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1ll1ll11ll1_opy_.bstack1llll1ll1ll_opy_(driver, bstack1ll1ll11ll1_opy_.bstack1l1l11l11l1_opy_, bstack1lll1_opy_ (u"ࠤࠥᐍ"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1ll1ll11ll1_opy_.bstack1llll1ll1ll_opy_(driver, bstack1ll1ll11ll1_opy_.bstack1l1l111lll1_opy_, bstack1lll1_opy_ (u"ࠥࠦᐎ"))
                caps = None
                if hasattr(webdriver, bstack1lll1_opy_ (u"ࠦࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᐏ")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack1lll1_opy_ (u"࡙ࠧࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭࡮ࡼࠤࡷ࡫ࡴࡳ࡫ࡨࡺࡪࡪࠠࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠦࡤࡪࡴࡨࡧࡹࡲࡹࠡࡨࡵࡳࡲࠦࡤࡳ࡫ࡹࡩࡷ࠴ࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᐐ"))
                    except Exception as e:
                        self.logger.debug(bstack1lll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡪࡩࡹࠦࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠥ࡬ࡲࡰ࡯ࠣࡨࡷ࡯ࡶࡦࡴ࠱ࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴ࠼ࠣࠦᐑ") + str(e) + bstack1lll1_opy_ (u"ࠢࠣᐒ"))
                try:
                    bstack1l11l11l1ll_opy_ = json.dumps(caps).encode(bstack1lll1_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢᐓ")) if caps else bstack1l11l11l111_opy_ (u"ࠤࡾࢁࠧᐔ")
                    req.capabilities = bstack1l11l11l1ll_opy_
                except Exception as e:
                    self.logger.debug(bstack1lll1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡤࡤࡷࡣࡪࡼࡥ࡯ࡶ࠽ࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡱࡨࠥࡹࡥࡳ࡫ࡤࡰ࡮ࢀࡥࠡࡥࡤࡴࡸࠦࡦࡰࡴࠣࡶࡪࡷࡵࡦࡵࡷ࠾ࠥࠨᐕ") + str(e) + bstack1lll1_opy_ (u"ࠦࠧᐖ"))
            except Exception as e:
                self.logger.error(bstack1lll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡦࡵ࡭ࡻ࡫ࡲࠡ࡫ࡷࡩࡲࡀࠠࠣᐗ") + str(str(e)) + bstack1lll1_opy_ (u"ࠨࠢᐘ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll11lll111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l1lll11l_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_, [])
        if not bstack1l1l1ll11l1_opy_() and len(bstack1l1l1lll11l_opy_) == 0:
            bstack1l1l1lll11l_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l11llllll1_opy_, [])
        if not bstack1l1l1lll11l_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᐙ") + str(kwargs) + bstack1lll1_opy_ (u"ࠣࠤᐚ"))
            return {}
        if len(bstack1l1l1lll11l_opy_) > 1:
            self.logger.debug(bstack1lll1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࢀࡲࡥ࡯ࠪࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷ࠮ࢃࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᐛ") + str(kwargs) + bstack1lll1_opy_ (u"ࠥࠦᐜ"))
            return {}
        bstack1l1l1l11111_opy_, bstack1l1l11l1ll1_opy_ = bstack1l1l1lll11l_opy_[0]
        driver = bstack1l1l1l11111_opy_()
        if not driver:
            self.logger.debug(bstack1lll1_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᐝ") + str(kwargs) + bstack1lll1_opy_ (u"ࠧࠨᐞ"))
            return {}
        capabilities = f.bstack1llll1ll1ll_opy_(bstack1l1l11l1ll1_opy_, bstack1ll1ll11ll1_opy_.bstack1l1l111llll_opy_)
        if not capabilities:
            self.logger.debug(bstack1lll1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠣࡪࡴࡻ࡮ࡥࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᐟ") + str(kwargs) + bstack1lll1_opy_ (u"ࠢࠣᐠ"))
            return {}
        return capabilities.get(bstack1lll1_opy_ (u"ࠣࡣ࡯ࡻࡦࡿࡳࡎࡣࡷࡧ࡭ࠨᐡ"), {})
    def bstack1ll11ll11ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l1lll11l_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l1lll111l1_opy_, [])
        if not bstack1l1l1ll11l1_opy_() and len(bstack1l1l1lll11l_opy_) == 0:
            bstack1l1l1lll11l_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1lll111lll1_opy_.bstack1l11llllll1_opy_, [])
        if not bstack1l1l1lll11l_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠤࡪࡩࡹࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡨࡷ࡯ࡶࡦࡴ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࡳࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᐢ") + str(kwargs) + bstack1lll1_opy_ (u"ࠥࠦᐣ"))
            return
        if len(bstack1l1l1lll11l_opy_) > 1:
            self.logger.debug(bstack1lll1_opy_ (u"ࠦ࡬࡫ࡴࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡪࡲࡪࡸࡨࡶ࠿ࠦࡻ࡭ࡧࡱࠬࡩࡸࡩࡷࡧࡵࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᐤ") + str(kwargs) + bstack1lll1_opy_ (u"ࠧࠨᐥ"))
        bstack1l1l1l11111_opy_, bstack1l1l11l1ll1_opy_ = bstack1l1l1lll11l_opy_[0]
        driver = bstack1l1l1l11111_opy_()
        if not driver:
            self.logger.debug(bstack1lll1_opy_ (u"ࠨࡧࡦࡶࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡥࡴ࡬ࡺࡪࡸ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᐦ") + str(kwargs) + bstack1lll1_opy_ (u"ࠢࠣᐧ"))
            return
        return driver