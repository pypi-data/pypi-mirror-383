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
import json
import logging
import datetime
import threading
from bstack_utils.helper import bstack11ll1l11lll_opy_, bstack1ll111111_opy_, get_host_info, bstack11l111ll11l_opy_, \
 bstack11111l1l1_opy_, bstack1ll1l1l1l1_opy_, error_handler, bstack111llll11l1_opy_, bstack1111l11l_opy_
import bstack_utils.accessibility as bstack1l11llll1l_opy_
from bstack_utils.bstack1llll1ll11_opy_ import bstack111llll111_opy_
from bstack_utils.bstack111lll11ll_opy_ import bstack1ll1ll1l1l_opy_
from bstack_utils.percy import bstack11l11111l1_opy_
from bstack_utils.config import Config
bstack1l1111ll1_opy_ = Config.bstack1111l11l1_opy_()
logger = logging.getLogger(__name__)
percy = bstack11l11111l1_opy_()
@error_handler(class_method=False)
def bstack1llll11l1lll_opy_(bs_config, bstack11llll11l1_opy_):
  try:
    data = {
        bstack1lll1_opy_ (u"ࠪࡪࡴࡸ࡭ࡢࡶࠪ⇝"): bstack1lll1_opy_ (u"ࠫ࡯ࡹ࡯࡯ࠩ⇞"),
        bstack1lll1_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡥ࡮ࡢ࡯ࡨࠫ⇟"): bs_config.get(bstack1lll1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫ⇠"), bstack1lll1_opy_ (u"ࠧࠨ⇡")),
        bstack1lll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭⇢"): bs_config.get(bstack1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ⇣"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭⇤"): bs_config.get(bstack1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭⇥")),
        bstack1lll1_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪ⇦"): bs_config.get(bstack1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡉ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩ⇧"), bstack1lll1_opy_ (u"ࠧࠨ⇨")),
        bstack1lll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⇩"): bstack1111l11l_opy_(),
        bstack1lll1_opy_ (u"ࠩࡷࡥ࡬ࡹࠧ⇪"): bstack11l111ll11l_opy_(bs_config),
        bstack1lll1_opy_ (u"ࠪ࡬ࡴࡹࡴࡠ࡫ࡱࡪࡴ࠭⇫"): get_host_info(),
        bstack1lll1_opy_ (u"ࠫࡨ࡯࡟ࡪࡰࡩࡳࠬ⇬"): bstack1ll111111_opy_(),
        bstack1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣࡷࡻ࡮ࡠ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⇭"): os.environ.get(bstack1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬ⇮")),
        bstack1lll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪ࡟ࡵࡧࡶࡸࡸࡥࡲࡦࡴࡸࡲࠬ⇯"): os.environ.get(bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓ࠭⇰"), False),
        bstack1lll1_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࡢࡧࡴࡴࡴࡳࡱ࡯ࠫ⇱"): bstack11ll1l11lll_opy_(),
        bstack1lll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ⇲"): bstack1llll11111l1_opy_(bs_config),
        bstack1lll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡥࡧࡷࡥ࡮ࡲࡳࠨ⇳"): bstack1llll111l1l1_opy_(bstack11llll11l1_opy_),
        bstack1lll1_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹࡥ࡭ࡢࡲࠪ⇴"): bstack1llll111111l_opy_(bs_config, bstack11llll11l1_opy_.get(bstack1lll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡸࡷࡪࡪࠧ⇵"), bstack1lll1_opy_ (u"ࠧࠨ⇶"))),
        bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪ⇷"): bstack11111l1l1_opy_(bs_config),
        bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠧ⇸"): bstack1llll11111ll_opy_(bs_config)
    }
    return data
  except Exception as error:
    logger.error(bstack1lll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡩࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡱࡣࡼࡰࡴࡧࡤࠡࡨࡲࡶ࡚ࠥࡥࡴࡶࡋࡹࡧࡀࠠࠡࡽࢀࠦ⇹").format(str(error)))
    return None
def bstack1llll111l1l1_opy_(framework):
  return {
    bstack1lll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡎࡢ࡯ࡨࠫ⇺"): framework.get(bstack1lll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪ࠭⇻"), bstack1lll1_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠭⇼")),
    bstack1lll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪ⇽"): framework.get(bstack1lll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ⇾")),
    bstack1lll1_opy_ (u"ࠩࡶࡨࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭⇿"): framework.get(bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ∀")),
    bstack1lll1_opy_ (u"ࠫࡱࡧ࡮ࡨࡷࡤ࡫ࡪ࠭∁"): bstack1lll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ∂"),
    bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭∃"): framework.get(bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ∄"))
  }
def bstack1llll11111ll_opy_(bs_config):
  bstack1lll1_opy_ (u"ࠣࠤࠥࠎࠥࠦࡒࡦࡶࡸࡶࡳࡹࠠࡵࡪࡨࠤࡹ࡫ࡳࡵࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦࠣࡷࡹࡧࡲࡵ࠰ࠍࠤࠥࠨࠢࠣ∅")
  if not bs_config:
    return {}
  bstack1111lll1l1l_opy_ = bstack111llll111_opy_(bs_config).bstack1111l1ll1ll_opy_(bs_config)
  return bstack1111lll1l1l_opy_
def bstack11ll1l1ll1_opy_(bs_config, framework):
  bstack1ll1llll11_opy_ = False
  bstack1111lllll_opy_ = False
  bstack1llll1111111_opy_ = False
  if bstack1lll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭∆") in bs_config:
    bstack1llll1111111_opy_ = True
  elif bstack1lll1_opy_ (u"ࠪࡥࡵࡶࠧ∇") in bs_config:
    bstack1ll1llll11_opy_ = True
  else:
    bstack1111lllll_opy_ = True
  bstack1l1l1l1ll_opy_ = {
    bstack1lll1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ∈"): bstack1ll1ll1l1l_opy_.bstack1llll1111lll_opy_(bs_config, framework),
    bstack1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ∉"): bstack1l11llll1l_opy_.bstack1lll1l1l1l_opy_(bs_config),
    bstack1lll1_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ∊"): bs_config.get(bstack1lll1_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭∋"), False),
    bstack1lll1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪ∌"): bstack1111lllll_opy_,
    bstack1lll1_opy_ (u"ࠩࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠨ∍"): bstack1ll1llll11_opy_,
    bstack1lll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧ∎"): bstack1llll1111111_opy_
  }
  return bstack1l1l1l1ll_opy_
@error_handler(class_method=False)
def bstack1llll11111l1_opy_(bs_config):
  try:
    bstack1llll111l1ll_opy_ = json.loads(os.getenv(bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬ∏"), bstack1lll1_opy_ (u"ࠬࢁࡽࠨ∐")))
    bstack1llll111l1ll_opy_ = bstack1llll1111ll1_opy_(bs_config, bstack1llll111l1ll_opy_)
    return {
        bstack1lll1_opy_ (u"࠭ࡳࡦࡶࡷ࡭ࡳ࡭ࡳࠨ∑"): bstack1llll111l1ll_opy_
    }
  except Exception as error:
    logger.error(bstack1lll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤ࡬࡫ࡴࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡵࡨࡸࡹ࡯࡮ࡨࡵࠣࡪࡴࡸࠠࡕࡧࡶࡸࡍࡻࡢ࠻ࠢࠣࡿࢂࠨ−").format(str(error)))
    return {}
def bstack1llll1111ll1_opy_(bs_config, bstack1llll111l1ll_opy_):
  if ((bstack1lll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ∓") in bs_config or not bstack11111l1l1_opy_(bs_config)) and bstack1l11llll1l_opy_.bstack1lll1l1l1l_opy_(bs_config)):
    bstack1llll111l1ll_opy_[bstack1lll1_opy_ (u"ࠤ࡬ࡲࡨࡲࡵࡥࡧࡈࡲࡨࡵࡤࡦࡦࡈࡼࡹ࡫࡮ࡴ࡫ࡲࡲࠧ∔")] = True
  return bstack1llll111l1ll_opy_
def bstack1llll11ll111_opy_(array, bstack1llll1111l1l_opy_, bstack1lll1llllll1_opy_):
  result = {}
  for o in array:
    key = o[bstack1llll1111l1l_opy_]
    result[key] = o[bstack1lll1llllll1_opy_]
  return result
def bstack1llll11lll1l_opy_(bstack11lll11l1_opy_=bstack1lll1_opy_ (u"ࠪࠫ∕")):
  bstack1lll1lllllll_opy_ = bstack1l11llll1l_opy_.on()
  bstack1llll1111l11_opy_ = bstack1ll1ll1l1l_opy_.on()
  bstack1llll111l111_opy_ = percy.bstack11l1111ll_opy_()
  if bstack1llll111l111_opy_ and not bstack1llll1111l11_opy_ and not bstack1lll1lllllll_opy_:
    return bstack11lll11l1_opy_ not in [bstack1lll1_opy_ (u"ࠫࡈࡈࡔࡔࡧࡶࡷ࡮ࡵ࡮ࡄࡴࡨࡥࡹ࡫ࡤࠨ∖"), bstack1lll1_opy_ (u"ࠬࡒ࡯ࡨࡅࡵࡩࡦࡺࡥࡥࠩ∗")]
  elif bstack1lll1lllllll_opy_ and not bstack1llll1111l11_opy_:
    return bstack11lll11l1_opy_ not in [bstack1lll1_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ∘"), bstack1lll1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ∙"), bstack1lll1_opy_ (u"ࠨࡎࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࠬ√")]
  return bstack1lll1lllllll_opy_ or bstack1llll1111l11_opy_ or bstack1llll111l111_opy_
@error_handler(class_method=False)
def bstack1llll11l1ll1_opy_(bstack11lll11l1_opy_, test=None):
  bstack1llll111l11l_opy_ = bstack1l11llll1l_opy_.on()
  if not bstack1llll111l11l_opy_ or bstack11lll11l1_opy_ not in [bstack1lll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ∛")] or test == None:
    return None
  return {
    bstack1lll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ∜"): bstack1llll111l11l_opy_ and bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ∝"), None) == True and bstack1l11llll1l_opy_.bstack1l1l111ll_opy_(test[bstack1lll1_opy_ (u"ࠬࡺࡡࡨࡵࠪ∞")])
  }
def bstack1llll111111l_opy_(bs_config, framework):
  bstack1ll1llll11_opy_ = False
  bstack1111lllll_opy_ = False
  bstack1llll1111111_opy_ = False
  if bstack1lll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ∟") in bs_config:
    bstack1llll1111111_opy_ = True
  elif bstack1lll1_opy_ (u"ࠧࡢࡲࡳࠫ∠") in bs_config:
    bstack1ll1llll11_opy_ = True
  else:
    bstack1111lllll_opy_ = True
  bstack1l1l1l1ll_opy_ = {
    bstack1lll1_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ∡"): bstack1ll1ll1l1l_opy_.bstack1llll1111lll_opy_(bs_config, framework),
    bstack1lll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ∢"): bstack1l11llll1l_opy_.bstack11l1l1l1l1_opy_(bs_config),
    bstack1lll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ∣"): bs_config.get(bstack1lll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪ∤"), False),
    bstack1lll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ∥"): bstack1111lllll_opy_,
    bstack1lll1_opy_ (u"࠭ࡡࡱࡲࡢࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ∦"): bstack1ll1llll11_opy_,
    bstack1lll1_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫ∧"): bstack1llll1111111_opy_
  }
  return bstack1l1l1l1ll_opy_