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
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1lllll11ll1_opy_,
    bstack1llllll1l11_opy_,
    bstack1llllll111l_opy_,
    bstack1lllll1ll11_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l1ll11l1_opy_, bstack11lllll111_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l111l_opy_ import bstack1ll1ll11ll1_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_, bstack1lll11l11l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1ll111ll_opy_ import bstack1lll11ll111_opy_
from browserstack_sdk.sdk_cli.bstack1l1llll1lll_opy_ import bstack1l1llll11l1_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack1lll1llll1_opy_ import bstack11ll1l1l_opy_, bstack11l1111111_opy_, bstack1ll1lll1_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1llll111111_opy_(bstack1l1llll11l1_opy_):
    bstack1l1l11111l1_opy_ = bstack1lll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡤࡳ࡫ࡹࡩࡷࡹࠢጥ")
    bstack1l1lll111l1_opy_ = bstack1lll1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣጦ")
    bstack1l11llllll1_opy_ = bstack1lll1_opy_ (u"ࠥࡲࡴࡴ࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧጧ")
    bstack1l11lll1l11_opy_ = bstack1lll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡶࠦጨ")
    bstack1l11lll11ll_opy_ = bstack1lll1_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡣࡷ࡫ࡦࡴࠤጩ")
    bstack1l1ll11l111_opy_ = bstack1lll1_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡨࡸࡥࡢࡶࡨࡨࠧጪ")
    bstack1l11lllllll_opy_ = bstack1lll1_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡴࡡ࡮ࡧࠥጫ")
    bstack1l1l111111l_opy_ = bstack1lll1_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡳࡵࡣࡷࡹࡸࠨጬ")
    def __init__(self):
        super().__init__(bstack1l1llll1ll1_opy_=self.bstack1l1l11111l1_opy_, frameworks=[bstack1ll1ll11ll1_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll11lllll1_opy_((bstack1lll1l11111_opy_.BEFORE_EACH, bstack1ll1llll1ll_opy_.POST), self.bstack1l11llll111_opy_)
        if bstack11lllll111_opy_():
            TestFramework.bstack1ll11lllll1_opy_((bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.POST), self.bstack1ll111lll11_opy_)
        else:
            TestFramework.bstack1ll11lllll1_opy_((bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.PRE), self.bstack1ll111lll11_opy_)
        TestFramework.bstack1ll11lllll1_opy_((bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.POST), self.bstack1ll11ll1ll1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11llll111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11lll1ll1_opy_ = self.bstack1l11llll11l_opy_(instance.context)
        if not bstack1l11lll1ll1_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡰࡢࡩࡨ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢጭ") + str(bstack1lllll1l111_opy_) + bstack1lll1_opy_ (u"ࠥࠦጮ"))
            return
        f.bstack1llll1ll111_opy_(instance, bstack1llll111111_opy_.bstack1l1lll111l1_opy_, bstack1l11lll1ll1_opy_)
    def bstack1l11llll11l_opy_(self, context: bstack1lllll1ll11_opy_, bstack1l11lllll1l_opy_= True):
        if bstack1l11lllll1l_opy_:
            bstack1l11lll1ll1_opy_ = self.bstack1l1lll1l1ll_opy_(context, reverse=True)
        else:
            bstack1l11lll1ll1_opy_ = self.bstack1l1llll1l1l_opy_(context, reverse=True)
        return [f for f in bstack1l11lll1ll1_opy_ if f[1].state != bstack1lllll11ll1_opy_.QUIT]
    def bstack1ll111lll11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11llll111_opy_(f, instance, bstack1lllll1l111_opy_, *args, **kwargs)
        if not bstack1l1l1ll11l1_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢጯ") + str(kwargs) + bstack1lll1_opy_ (u"ࠧࠨጰ"))
            return
        bstack1l11lll1ll1_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1llll111111_opy_.bstack1l1lll111l1_opy_, [])
        if not bstack1l11lll1ll1_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤጱ") + str(kwargs) + bstack1lll1_opy_ (u"ࠢࠣጲ"))
            return
        if len(bstack1l11lll1ll1_opy_) > 1:
            self.logger.debug(
                bstack1111l1l1ll_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥጳ"))
        bstack1l11lll111l_opy_, bstack1l1l11l1ll1_opy_ = bstack1l11lll1ll1_opy_[0]
        page = bstack1l11lll111l_opy_()
        if not page:
            self.logger.debug(bstack1lll1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡱࡣࡪࡩࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤጴ") + str(kwargs) + bstack1lll1_opy_ (u"ࠥࠦጵ"))
            return
        bstack1ll1ll1l11_opy_ = getattr(args[0], bstack1lll1_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦጶ"), None)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1lll1_opy_ (u"ࠧࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠥጷ")).get(bstack1lll1_opy_ (u"ࠨࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠣጸ")):
            try:
                page.evaluate(bstack1lll1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣጹ"),
                            bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠬጺ") + json.dumps(
                                bstack1ll1ll1l11_opy_) + bstack1lll1_opy_ (u"ࠤࢀࢁࠧጻ"))
            except Exception as e:
                self.logger.debug(bstack1lll1_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥࢁࡽࠣጼ"), e)
    def bstack1ll11ll1ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11llll111_opy_(f, instance, bstack1lllll1l111_opy_, *args, **kwargs)
        if not bstack1l1l1ll11l1_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢጽ") + str(kwargs) + bstack1lll1_opy_ (u"ࠧࠨጾ"))
            return
        bstack1l11lll1ll1_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1llll111111_opy_.bstack1l1lll111l1_opy_, [])
        if not bstack1l11lll1ll1_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤጿ") + str(kwargs) + bstack1lll1_opy_ (u"ࠢࠣፀ"))
            return
        if len(bstack1l11lll1ll1_opy_) > 1:
            self.logger.debug(
                bstack1111l1l1ll_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥፁ"))
        bstack1l11lll111l_opy_, bstack1l1l11l1ll1_opy_ = bstack1l11lll1ll1_opy_[0]
        page = bstack1l11lll111l_opy_()
        if not page:
            self.logger.debug(bstack1lll1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡱࡣࡪࡩࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤፂ") + str(kwargs) + bstack1lll1_opy_ (u"ࠥࠦፃ"))
            return
        status = f.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1l1l1111111_opy_, None)
        if not status:
            self.logger.debug(bstack1lll1_opy_ (u"ࠦࡳࡵࠠࡴࡶࡤࡸࡺࡹࠠࡧࡱࡵࠤࡹ࡫ࡳࡵ࠮ࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢፄ") + str(bstack1lllll1l111_opy_) + bstack1lll1_opy_ (u"ࠧࠨፅ"))
            return
        bstack1l11llll1l1_opy_ = {bstack1lll1_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨፆ"): status.lower()}
        bstack1l11llll1ll_opy_ = f.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1l11lll1lll_opy_, None)
        if status.lower() == bstack1lll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧፇ") and bstack1l11llll1ll_opy_ is not None:
            bstack1l11llll1l1_opy_[bstack1lll1_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨፈ")] = bstack1l11llll1ll_opy_[0][bstack1lll1_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬፉ")][0] if isinstance(bstack1l11llll1ll_opy_, list) else str(bstack1l11llll1ll_opy_)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1lll1_opy_ (u"ࠥࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠣፊ")).get(bstack1lll1_opy_ (u"ࠦࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣፋ")):
            try:
                page.evaluate(
                        bstack1lll1_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨፌ"),
                        bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࠫፍ")
                        + json.dumps(bstack1l11llll1l1_opy_)
                        + bstack1lll1_opy_ (u"ࠢࡾࠤፎ")
                    )
            except Exception as e:
                self.logger.debug(bstack1lll1_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥࢁࡽࠣፏ"), e)
    def bstack1l1ll1ll1ll_opy_(
        self,
        instance: bstack1lll11l11l1_opy_,
        f: TestFramework,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11llll111_opy_(f, instance, bstack1lllll1l111_opy_, *args, **kwargs)
        if not bstack1l1l1ll11l1_opy_:
            self.logger.debug(
                bstack1111l1l1ll_opy_ (u"ࠤࡰࡥࡷࡱ࡟ࡰ࠳࠴ࡽࡤࡹࡹ࡯ࡥ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮࠭ࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥፐ"))
            return
        bstack1l11lll1ll1_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1llll111111_opy_.bstack1l1lll111l1_opy_, [])
        if not bstack1l11lll1ll1_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨፑ") + str(kwargs) + bstack1lll1_opy_ (u"ࠦࠧፒ"))
            return
        if len(bstack1l11lll1ll1_opy_) > 1:
            self.logger.debug(
                bstack1111l1l1ll_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠࡼ࡮ࡨࡲ࠭ࡶࡡࡨࡧࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡸ࠯ࡽࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࢁ࡫ࡸࡣࡵ࡫ࡸࢃࠢፓ"))
        bstack1l11lll111l_opy_, bstack1l1l11l1ll1_opy_ = bstack1l11lll1ll1_opy_[0]
        page = bstack1l11lll111l_opy_()
        if not page:
            self.logger.debug(bstack1lll1_opy_ (u"ࠨ࡭ࡢࡴ࡮ࡣࡴ࠷࠱ࡺࡡࡶࡽࡳࡩ࠺ࠡࡰࡲࠤࡵࡧࡧࡦࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨፔ") + str(kwargs) + bstack1lll1_opy_ (u"ࠢࠣፕ"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack1lll1_opy_ (u"ࠣࡑࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࡔࡻࡱࡧ࠿ࠨፖ") + str(timestamp)
        try:
            page.evaluate(
                bstack1lll1_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥፗ"),
                bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠨፘ").format(
                    json.dumps(
                        {
                            bstack1lll1_opy_ (u"ࠦࡦࡩࡴࡪࡱࡱࠦፙ"): bstack1lll1_opy_ (u"ࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢፚ"),
                            bstack1lll1_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ፛"): {
                                bstack1lll1_opy_ (u"ࠢࡵࡻࡳࡩࠧ፜"): bstack1lll1_opy_ (u"ࠣࡃࡱࡲࡴࡺࡡࡵ࡫ࡲࡲࠧ፝"),
                                bstack1lll1_opy_ (u"ࠤࡧࡥࡹࡧࠢ፞"): data,
                                bstack1lll1_opy_ (u"ࠥࡰࡪࡼࡥ࡭ࠤ፟"): bstack1lll1_opy_ (u"ࠦࡩ࡫ࡢࡶࡩࠥ፠")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack1lll1_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡱ࠴࠵ࡾࠦࡡ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠣࡱࡦࡸ࡫ࡪࡰࡪࠤࢀࢃࠢ፡"), e)
    def bstack1l1l1lll1l1_opy_(
        self,
        instance: bstack1lll11l11l1_opy_,
        f: TestFramework,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11llll111_opy_(f, instance, bstack1lllll1l111_opy_, *args, **kwargs)
        if f.bstack1llll1ll1ll_opy_(instance, bstack1llll111111_opy_.bstack1l1ll11l111_opy_, False):
            return
        self.bstack1ll11l11ll1_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1ll11111ll1_opy_)
        req.test_framework_name = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1ll1111llll_opy_)
        req.test_framework_version = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1l1lll11ll1_opy_)
        req.test_framework_state = bstack1lllll1l111_opy_[0].name
        req.test_hook_state = bstack1lllll1l111_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll1ll1ll_opy_(instance, TestFramework.bstack1ll11ll1l1l_opy_)
        for bstack1l11lll11l1_opy_ in bstack1lll11ll111_opy_.bstack1lllll1l11l_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack1lll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠧ።")
                if bstack1l1l1ll11l1_opy_
                else bstack1lll1_opy_ (u"ࠢࡶࡰ࡮ࡲࡴࡽ࡮ࡠࡩࡵ࡭ࡩࠨ፣")
            )
            session.ref = bstack1l11lll11l1_opy_.ref()
            session.hub_url = bstack1lll11ll111_opy_.bstack1llll1ll1ll_opy_(bstack1l11lll11l1_opy_, bstack1lll11ll111_opy_.bstack1l1l11l11l1_opy_, bstack1lll1_opy_ (u"ࠣࠤ፤"))
            session.framework_name = bstack1l11lll11l1_opy_.framework_name
            session.framework_version = bstack1l11lll11l1_opy_.framework_version
            session.framework_session_id = bstack1lll11ll111_opy_.bstack1llll1ll1ll_opy_(bstack1l11lll11l1_opy_, bstack1lll11ll111_opy_.bstack1l1l111lll1_opy_, bstack1lll1_opy_ (u"ࠤࠥ፥"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll11ll11ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs
    ):
        bstack1l11lll1ll1_opy_ = f.bstack1llll1ll1ll_opy_(instance, bstack1llll111111_opy_.bstack1l1lll111l1_opy_, [])
        if not bstack1l11lll1ll1_opy_:
            self.logger.debug(bstack1lll1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦ፦") + str(kwargs) + bstack1lll1_opy_ (u"ࠦࠧ፧"))
            return
        if len(bstack1l11lll1ll1_opy_) > 1:
            self.logger.debug(bstack1lll1_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠࡼ࡮ࡨࡲ࠭ࡶࡡࡨࡧࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡸ࠯ࡽࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨ፨") + str(kwargs) + bstack1lll1_opy_ (u"ࠨࠢ፩"))
        bstack1l11lll111l_opy_, bstack1l1l11l1ll1_opy_ = bstack1l11lll1ll1_opy_[0]
        page = bstack1l11lll111l_opy_()
        if not page:
            self.logger.debug(bstack1lll1_opy_ (u"ࠢࡨࡧࡷࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ፪") + str(kwargs) + bstack1lll1_opy_ (u"ࠣࠤ፫"))
            return
        return page
    def bstack1ll11lll111_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack1l11lllll11_opy_ = {}
        for bstack1l11lll11l1_opy_ in bstack1lll11ll111_opy_.bstack1lllll1l11l_opy_.values():
            caps = bstack1lll11ll111_opy_.bstack1llll1ll1ll_opy_(bstack1l11lll11l1_opy_, bstack1lll11ll111_opy_.bstack1l1l111llll_opy_, bstack1lll1_opy_ (u"ࠤࠥ፬"))
        bstack1l11lllll11_opy_[bstack1lll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠣ፭")] = caps.get(bstack1lll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࠧ፮"), bstack1lll1_opy_ (u"ࠧࠨ፯"))
        bstack1l11lllll11_opy_[bstack1lll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧ፰")] = caps.get(bstack1lll1_opy_ (u"ࠢࡰࡵࠥ፱"), bstack1lll1_opy_ (u"ࠣࠤ፲"))
        bstack1l11lllll11_opy_[bstack1lll1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠦ፳")] = caps.get(bstack1lll1_opy_ (u"ࠥࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠢ፴"), bstack1lll1_opy_ (u"ࠦࠧ፵"))
        bstack1l11lllll11_opy_[bstack1lll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳࠨ፶")] = caps.get(bstack1lll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣ፷"), bstack1lll1_opy_ (u"ࠢࠣ፸"))
        return bstack1l11lllll11_opy_
    def bstack1ll1l1111l1_opy_(self, page: object, bstack1ll1l111111_opy_, args={}):
        try:
            bstack1l11lll1l1l_opy_ = bstack1lll1_opy_ (u"ࠣࠤࠥࠬ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࠨ࠯࠰࠱ࡦࡸࡺࡡࡤ࡭ࡖࡨࡰࡇࡲࡨࡵࠬࠤࢀࢁࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡵࡩࡹࡻࡲ࡯ࠢࡱࡩࡼࠦࡐࡳࡱࡰ࡭ࡸ࡫ࠨࠩࡴࡨࡷࡴࡲࡶࡦ࠮ࠣࡶࡪࡰࡥࡤࡶࠬࠤࡂࡄࠠࡼࡽࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡥࡷࡹࡧࡣ࡬ࡕࡧ࡯ࡆࡸࡧࡴ࠰ࡳࡹࡸ࡮ࠨࡳࡧࡶࡳࡱࡼࡥࠪ࠽ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡾࡪࡳࡥࡢࡰࡦࡼࢁࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾࡿࠬ࠿ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࢂ࠯ࠨࡼࡣࡵ࡫ࡤࡰࡳࡰࡰࢀ࠭ࠧࠨࠢ፹")
            bstack1ll1l111111_opy_ = bstack1ll1l111111_opy_.replace(bstack1lll1_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧ፺"), bstack1lll1_opy_ (u"ࠥࡦࡸࡺࡡࡤ࡭ࡖࡨࡰࡇࡲࡨࡵࠥ፻"))
            script = bstack1l11lll1l1l_opy_.format(fn_body=bstack1ll1l111111_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠦࡦ࠷࠱ࡺࡡࡶࡧࡷ࡯ࡰࡵࡡࡨࡼࡪࡩࡵࡵࡧ࠽ࠤࡊࡸࡲࡰࡴࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡲ࡬ࠦࡴࡩࡧࠣࡥ࠶࠷ࡹࠡࡵࡦࡶ࡮ࡶࡴ࠭ࠢࠥ፼") + str(e) + bstack1lll1_opy_ (u"ࠧࠨ፽"))