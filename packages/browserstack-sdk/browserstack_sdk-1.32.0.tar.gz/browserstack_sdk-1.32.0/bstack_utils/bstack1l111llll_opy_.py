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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11ll111l1ll_opy_ import bstack11ll11111ll_opy_
from bstack_utils.constants import *
import json
class bstack1ll1111ll1_opy_:
    def __init__(self, bstack1ll1111111_opy_, bstack11ll1111l11_opy_):
        self.bstack1ll1111111_opy_ = bstack1ll1111111_opy_
        self.bstack11ll1111l11_opy_ = bstack11ll1111l11_opy_
        self.bstack11ll1111ll1_opy_ = None
    def __call__(self):
        bstack11ll111l111_opy_ = {}
        while True:
            self.bstack11ll1111ll1_opy_ = bstack11ll111l111_opy_.get(
                bstack1lll1_opy_ (u"ࠨࡰࡨࡼࡹࡥࡰࡰ࡮࡯ࡣࡹ࡯࡭ࡦࠩច"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11ll1111l1l_opy_ = self.bstack11ll1111ll1_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11ll1111l1l_opy_ > 0:
                sleep(bstack11ll1111l1l_opy_ / 1000)
            params = {
                bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩឆ"): self.bstack1ll1111111_opy_,
                bstack1lll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭ជ"): int(datetime.now().timestamp() * 1000)
            }
            bstack11ll1111lll_opy_ = bstack1lll1_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨឈ") + bstack11ll111l1l1_opy_ + bstack1lll1_opy_ (u"ࠧ࠵ࡡࡶࡶࡲࡱࡦࡺࡥ࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࠤញ")
            if self.bstack11ll1111l11_opy_.lower() == bstack1lll1_opy_ (u"ࠨࡲࡦࡵࡸࡰࡹࡹࠢដ"):
                bstack11ll111l111_opy_ = bstack11ll11111ll_opy_.results(bstack11ll1111lll_opy_, params)
            else:
                bstack11ll111l111_opy_ = bstack11ll11111ll_opy_.bstack11ll111l11l_opy_(bstack11ll1111lll_opy_, params)
            if str(bstack11ll111l111_opy_.get(bstack1lll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧឋ"), bstack1lll1_opy_ (u"ࠨ࠴࠳࠴ࠬឌ"))) != bstack1lll1_opy_ (u"ࠩ࠷࠴࠹࠭ឍ"):
                break
        return bstack11ll111l111_opy_.get(bstack1lll1_opy_ (u"ࠪࡨࡦࡺࡡࠨណ"), bstack11ll111l111_opy_)