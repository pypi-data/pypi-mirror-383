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
import re
from bstack_utils.bstack1lll1llll1_opy_ import bstack1llllll1l1l1_opy_
def bstack1llllll1ll11_opy_(fixture_name):
    if fixture_name.startswith(bstack1lll1_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡴࡧࡷࡹࡵࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᾣ")):
        return bstack1lll1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࠭ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩᾤ")
    elif fixture_name.startswith(bstack1lll1_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᾥ")):
        return bstack1lll1_opy_ (u"ࠪࡷࡪࡺࡵࡱ࠯ࡰࡳࡩࡻ࡬ࡦࠩᾦ")
    elif fixture_name.startswith(bstack1lll1_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᾧ")):
        return bstack1lll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࠭ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩᾨ")
    elif fixture_name.startswith(bstack1lll1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᾩ")):
        return bstack1lll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯࠯ࡰࡳࡩࡻ࡬ࡦࠩᾪ")
def bstack1lllllll111l_opy_(fixture_name):
    return bool(re.match(bstack1lll1_opy_ (u"ࠨࡠࡢࡼࡺࡴࡩࡵࡡࠫࡷࡪࡺࡵࡱࡾࡷࡩࡦࡸࡤࡰࡹࡱ࠭ࡤ࠮ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡽ࡯ࡲࡨࡺࡲࡥࠪࡡࡩ࡭ࡽࡺࡵࡳࡧࡢ࠲࠯࠭ᾫ"), fixture_name))
def bstack1llllll1l11l_opy_(fixture_name):
    return bool(re.match(bstack1lll1_opy_ (u"ࠩࡡࡣࡽࡻ࡮ࡪࡶࡢࠬࡸ࡫ࡴࡶࡲࡿࡸࡪࡧࡲࡥࡱࡺࡲ࠮ࡥ࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫࡟࠯ࠬࠪᾬ"), fixture_name))
def bstack1llllll1l111_opy_(fixture_name):
    return bool(re.match(bstack1lll1_opy_ (u"ࠪࡢࡤࡾࡵ࡯࡫ࡷࡣ࠭ࡹࡥࡵࡷࡳࢀࡹ࡫ࡡࡳࡦࡲࡻࡳ࠯࡟ࡤ࡮ࡤࡷࡸࡥࡦࡪࡺࡷࡹࡷ࡫࡟࠯ࠬࠪᾭ"), fixture_name))
def bstack1llllll11lll_opy_(fixture_name):
    if fixture_name.startswith(bstack1lll1_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᾮ")):
        return bstack1lll1_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭ᾯ"), bstack1lll1_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫᾰ")
    elif fixture_name.startswith(bstack1lll1_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᾱ")):
        return bstack1lll1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࠭࡮ࡱࡧࡹࡱ࡫ࠧᾲ"), bstack1lll1_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡄࡐࡑ࠭ᾳ")
    elif fixture_name.startswith(bstack1lll1_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡸࡪࡧࡲࡥࡱࡺࡲࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᾴ")):
        return bstack1lll1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠳ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠨ᾵"), bstack1lll1_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡊࡇࡃࡉࠩᾶ")
    elif fixture_name.startswith(bstack1lll1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᾷ")):
        return bstack1lll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯࠯ࡰࡳࡩࡻ࡬ࡦࠩᾸ"), bstack1lll1_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡂࡎࡏࠫᾹ")
    return None, None
def bstack1llllll1ll1l_opy_(hook_name):
    if hook_name in [bstack1lll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨᾺ"), bstack1lll1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬΆ")]:
        return hook_name.capitalize()
    return hook_name
def bstack1llllll1l1ll_opy_(hook_name):
    if hook_name in [bstack1lll1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠬᾼ"), bstack1lll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡲ࡫ࡴࡩࡱࡧࠫ᾽")]:
        return bstack1lll1_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫι")
    elif hook_name in [bstack1lll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪ࠭᾿"), bstack1lll1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡤ࡮ࡤࡷࡸ࠭῀")]:
        return bstack1lll1_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡄࡐࡑ࠭῁")
    elif hook_name in [bstack1lll1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧῂ"), bstack1lll1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡦࡶ࡫ࡳࡩ࠭ῃ")]:
        return bstack1lll1_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡊࡇࡃࡉࠩῄ")
    elif hook_name in [bstack1lll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡲࡨࡺࡲࡥࠨ῅"), bstack1lll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡦࡰࡦࡹࡳࠨῆ")]:
        return bstack1lll1_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡂࡎࡏࠫῇ")
    return hook_name
def bstack1lllllll1111_opy_(node, scenario):
    if hasattr(node, bstack1lll1_opy_ (u"ࠩࡦࡥࡱࡲࡳࡱࡧࡦࠫῈ")):
        parts = node.nodeid.rsplit(bstack1lll1_opy_ (u"ࠥ࡟ࠧΈ"))
        params = parts[-1]
        return bstack1lll1_opy_ (u"ࠦࢀࢃࠠ࡜ࡽࢀࠦῊ").format(scenario.name, params)
    return scenario.name
def bstack1llllll1llll_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack1lll1_opy_ (u"ࠬࡩࡡ࡭࡮ࡶࡴࡪࡩࠧΉ")):
            examples = list(node.callspec.params[bstack1lll1_opy_ (u"࠭࡟ࡱࡻࡷࡩࡸࡺ࡟ࡣࡦࡧࡣࡪࡾࡡ࡮ࡲ࡯ࡩࠬῌ")].values())
        return examples
    except:
        return []
def bstack1llllll1lll1_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack1llllll11l1l_opy_(report):
    try:
        status = bstack1lll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ῍")
        if report.passed or (report.failed and hasattr(report, bstack1lll1_opy_ (u"ࠣࡹࡤࡷࡽ࡬ࡡࡪ࡮ࠥ῎"))):
            status = bstack1lll1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩ῏")
        elif report.skipped:
            status = bstack1lll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫῐ")
        bstack1llllll1l1l1_opy_(status)
    except:
        pass
def bstack1l1l1ll1l1_opy_(status):
    try:
        bstack1llllll11ll1_opy_ = bstack1lll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫῑ")
        if status == bstack1lll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬῒ"):
            bstack1llllll11ll1_opy_ = bstack1lll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ΐ")
        elif status == bstack1lll1_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨ῔"):
            bstack1llllll11ll1_opy_ = bstack1lll1_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩ῕")
        bstack1llllll1l1l1_opy_(bstack1llllll11ll1_opy_)
    except:
        pass
def bstack1llllll11l11_opy_(item=None, report=None, summary=None, extra=None):
    return