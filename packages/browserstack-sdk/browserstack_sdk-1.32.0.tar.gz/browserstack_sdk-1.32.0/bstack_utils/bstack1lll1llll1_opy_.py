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
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11l11ll1l1l_opy_, bstack1l11l1lll_opy_, bstack1ll1l1l1l1_opy_, bstack11l11l11ll_opy_, \
    bstack11l11l11l11_opy_
from bstack_utils.measure import measure
def bstack11lllllll_opy_(bstack1lllll11l1l1_opy_):
    for driver in bstack1lllll11l1l1_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1111111l1_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
def bstack11l1111111_opy_(driver, status, reason=bstack1lll1_opy_ (u"ࠧࠨ ")):
    bstack1l1111ll1_opy_ = Config.bstack1111l11l1_opy_()
    if bstack1l1111ll1_opy_.bstack111111ll11_opy_():
        return
    bstack1ll1ll111l_opy_ = bstack11ll1l1l_opy_(bstack1lll1_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫ "), bstack1lll1_opy_ (u"ࠩࠪ‪"), status, reason, bstack1lll1_opy_ (u"ࠪࠫ‫"), bstack1lll1_opy_ (u"ࠫࠬ‬"))
    driver.execute_script(bstack1ll1ll111l_opy_)
@measure(event_name=EVENTS.bstack1111111l1_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
def bstack1ll1lll1_opy_(page, status, reason=bstack1lll1_opy_ (u"ࠬ࠭‭")):
    try:
        if page is None:
            return
        bstack1l1111ll1_opy_ = Config.bstack1111l11l1_opy_()
        if bstack1l1111ll1_opy_.bstack111111ll11_opy_():
            return
        bstack1ll1ll111l_opy_ = bstack11ll1l1l_opy_(bstack1lll1_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩ‮"), bstack1lll1_opy_ (u"ࠧࠨ "), status, reason, bstack1lll1_opy_ (u"ࠨࠩ‰"), bstack1lll1_opy_ (u"ࠩࠪ‱"))
        page.evaluate(bstack1lll1_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦ′"), bstack1ll1ll111l_opy_)
    except Exception as e:
        print(bstack1lll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡪࡺࡴࡪࡰࡪࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡻࡾࠤ″"), e)
def bstack11ll1l1l_opy_(type, name, status, reason, bstack1l1l11l1_opy_, bstack1llll11ll_opy_):
    bstack11111llll_opy_ = {
        bstack1lll1_opy_ (u"ࠬࡧࡣࡵ࡫ࡲࡲࠬ‴"): type,
        bstack1lll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ‵"): {}
    }
    if type == bstack1lll1_opy_ (u"ࠧࡢࡰࡱࡳࡹࡧࡴࡦࠩ‶"):
        bstack11111llll_opy_[bstack1lll1_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ‷")][bstack1lll1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ‸")] = bstack1l1l11l1_opy_
        bstack11111llll_opy_[bstack1lll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭‹")][bstack1lll1_opy_ (u"ࠫࡩࡧࡴࡢࠩ›")] = json.dumps(str(bstack1llll11ll_opy_))
    if type == bstack1lll1_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭※"):
        bstack11111llll_opy_[bstack1lll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ‼")][bstack1lll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ‽")] = name
    if type == bstack1lll1_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫ‾"):
        bstack11111llll_opy_[bstack1lll1_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ‿")][bstack1lll1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ⁀")] = status
        if status == bstack1lll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ⁁") and str(reason) != bstack1lll1_opy_ (u"ࠧࠨ⁂"):
            bstack11111llll_opy_[bstack1lll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ⁃")][bstack1lll1_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ⁄")] = json.dumps(str(reason))
    bstack1l1l1ll11l_opy_ = bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭⁅").format(json.dumps(bstack11111llll_opy_))
    return bstack1l1l1ll11l_opy_
def bstack1l111lll1l_opy_(url, config, logger, bstack1l1lll1l1l_opy_=False):
    hostname = bstack1l11l1lll_opy_(url)
    is_private = bstack11l11l11ll_opy_(hostname)
    try:
        if is_private or bstack1l1lll1l1l_opy_:
            file_path = bstack11l11ll1l1l_opy_(bstack1lll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ⁆"), bstack1lll1_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩ⁇"), logger)
            if os.environ.get(bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡑࡓ࡙ࡥࡓࡆࡖࡢࡉࡗࡘࡏࡓࠩ⁈")) and eval(
                    os.environ.get(bstack1lll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡃࡂࡎࡢࡒࡔ࡚࡟ࡔࡇࡗࡣࡊࡘࡒࡐࡔࠪ⁉"))):
                return
            if (bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ⁊") in config and not config[bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ⁋")]):
                os.environ[bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡎࡐࡖࡢࡗࡊ࡚࡟ࡆࡔࡕࡓࡗ࠭⁌")] = str(True)
                bstack1lllll11l11l_opy_ = {bstack1lll1_opy_ (u"ࠩ࡫ࡳࡸࡺ࡮ࡢ࡯ࡨࠫ⁍"): hostname}
                bstack11l11l11l11_opy_(bstack1lll1_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩ⁎"), bstack1lll1_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩ⁏"), bstack1lllll11l11l_opy_, logger)
    except Exception as e:
        pass
def bstack11lll1lll_opy_(caps, bstack1lllll111lll_opy_):
    if bstack1lll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭⁐") in caps:
        caps[bstack1lll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ⁑")][bstack1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭⁒")] = True
        if bstack1lllll111lll_opy_:
            caps[bstack1lll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ⁓")][bstack1lll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ⁔")] = bstack1lllll111lll_opy_
    else:
        caps[bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳࡨࡧ࡬ࠨ⁕")] = True
        if bstack1lllll111lll_opy_:
            caps[bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⁖")] = bstack1lllll111lll_opy_
def bstack1llllll1l1l1_opy_(bstack111l1111ll_opy_):
    bstack1lllll11l111_opy_ = bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩ⁗"), bstack1lll1_opy_ (u"࠭ࠧ⁘"))
    if bstack1lllll11l111_opy_ == bstack1lll1_opy_ (u"ࠧࠨ⁙") or bstack1lllll11l111_opy_ == bstack1lll1_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩ⁚"):
        threading.current_thread().testStatus = bstack111l1111ll_opy_
    else:
        if bstack111l1111ll_opy_ == bstack1lll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⁛"):
            threading.current_thread().testStatus = bstack111l1111ll_opy_