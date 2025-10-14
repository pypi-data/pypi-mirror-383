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
from bstack_utils.constants import bstack11ll111ll11_opy_
def bstack1ll1lll1l_opy_(bstack11ll111ll1l_opy_):
    from browserstack_sdk.sdk_cli.cli import cli
    from bstack_utils.helper import bstack1l1ll111ll_opy_
    host = bstack1l1ll111ll_opy_(cli.config, [bstack1lll1_opy_ (u"ࠦࡦࡶࡩࡴࠤខ"), bstack1lll1_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡫ࠢគ"), bstack1lll1_opy_ (u"ࠨࡡࡱ࡫ࠥឃ")], bstack11ll111ll11_opy_)
    return bstack1lll1_opy_ (u"ࠧࡼࡿ࠲ࡿࢂ࠭ង").format(host, bstack11ll111ll1l_opy_)