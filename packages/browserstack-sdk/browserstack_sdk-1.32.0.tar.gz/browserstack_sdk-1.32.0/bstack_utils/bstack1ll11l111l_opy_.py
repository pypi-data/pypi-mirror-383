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
import threading
import logging
import bstack_utils.accessibility as bstack1l11llll1l_opy_
from bstack_utils.helper import bstack1ll1l1l1l1_opy_
logger = logging.getLogger(__name__)
def bstack1llll111ll_opy_(bstack111l11l1l_opy_):
  return True if bstack111l11l1l_opy_ in threading.current_thread().__dict__.keys() else False
def bstack1l11111ll_opy_(context, *args):
    tags = getattr(args[0], bstack1lll1_opy_ (u"ࠫࡹࡧࡧࡴࠩត"), [])
    bstack1l111ll111_opy_ = bstack1l11llll1l_opy_.bstack1l1l111ll_opy_(tags)
    threading.current_thread().isA11yTest = bstack1l111ll111_opy_
    try:
      bstack11ll11111_opy_ = threading.current_thread().bstackSessionDriver if bstack1llll111ll_opy_(bstack1lll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫថ")) else context.browser
      if bstack11ll11111_opy_ and bstack11ll11111_opy_.session_id and bstack1l111ll111_opy_ and bstack1ll1l1l1l1_opy_(
              threading.current_thread(), bstack1lll1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬទ"), None):
          threading.current_thread().isA11yTest = bstack1l11llll1l_opy_.bstack1l1111ll_opy_(bstack11ll11111_opy_, bstack1l111ll111_opy_)
    except Exception as e:
       logger.debug(bstack1lll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡹࡧࡲࡵࠢࡤ࠵࠶ࡿࠠࡪࡰࠣࡦࡪ࡮ࡡࡷࡧ࠽ࠤࢀࢃࠧធ").format(str(e)))
def bstack11l1ll111_opy_(bstack11ll11111_opy_):
    if bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬន"), None) and bstack1ll1l1l1l1_opy_(
      threading.current_thread(), bstack1lll1_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨប"), None) and not bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠪࡥ࠶࠷ࡹࡠࡵࡷࡳࡵ࠭ផ"), False):
      threading.current_thread().a11y_stop = True
      bstack1l11llll1l_opy_.bstack11l1l1l1_opy_(bstack11ll11111_opy_, name=bstack1lll1_opy_ (u"ࠦࠧព"), path=bstack1lll1_opy_ (u"ࠧࠨភ"))