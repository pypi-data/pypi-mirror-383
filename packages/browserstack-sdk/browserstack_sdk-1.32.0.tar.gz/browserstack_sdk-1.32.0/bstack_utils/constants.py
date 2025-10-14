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
import re
from enum import Enum
bstack1lll11ll1_opy_ = {
  bstack1lll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨឦ"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧࡵࠫឧ"),
  bstack1lll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫឨ"): bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡭ࡨࡽࠬឩ"),
  bstack1lll1_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ឪ"): bstack1lll1_opy_ (u"ࠫࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨឫ"),
  bstack1lll1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬឬ"): bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡳࡦࡡࡺ࠷ࡨ࠭ឭ"),
  bstack1lll1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬឮ"): bstack1lll1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࠩឯ"),
  bstack1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬឰ"): bstack1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࠩឱ"),
  bstack1lll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩឲ"): bstack1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪឳ"),
  bstack1lll1_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬ឴"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡤࡦࡤࡸ࡫ࠬ឵"),
  bstack1lll1_opy_ (u"ࠨࡥࡲࡲࡸࡵ࡬ࡦࡎࡲ࡫ࡸ࠭ា"): bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡲࡸࡵ࡬ࡦࠩិ"),
  bstack1lll1_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࠨី"): bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࠨឹ"),
  bstack1lll1_opy_ (u"ࠬࡧࡰࡱ࡫ࡸࡱࡑࡵࡧࡴࠩឺ"): bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡰࡱ࡫ࡸࡱࡑࡵࡧࡴࠩុ"),
  bstack1lll1_opy_ (u"ࠧࡷ࡫ࡧࡩࡴ࠭ូ"): bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡷ࡫ࡧࡩࡴ࠭ួ"),
  bstack1lll1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࡐࡴ࡭ࡳࠨើ"): bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡱ࡫࡮ࡪࡷࡰࡐࡴ࡭ࡳࠨឿ"),
  bstack1lll1_opy_ (u"ࠫࡹ࡫࡬ࡦ࡯ࡨࡸࡷࡿࡌࡰࡩࡶࠫៀ"): bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫࡬ࡦ࡯ࡨࡸࡷࡿࡌࡰࡩࡶࠫេ"),
  bstack1lll1_opy_ (u"࠭ࡧࡦࡱࡏࡳࡨࡧࡴࡪࡱࡱࠫែ"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡧࡦࡱࡏࡳࡨࡧࡴࡪࡱࡱࠫៃ"),
  bstack1lll1_opy_ (u"ࠨࡶ࡬ࡱࡪࢀ࡯࡯ࡧࠪោ"): bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡶ࡬ࡱࡪࢀ࡯࡯ࡧࠪៅ"),
  bstack1lll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬំ"): bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡷࡪࡲࡥ࡯࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ះ"),
  bstack1lll1_opy_ (u"ࠬࡳࡡࡴ࡭ࡆࡳࡲࡳࡡ࡯ࡦࡶࠫៈ"): bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡳࡡࡴ࡭ࡆࡳࡲࡳࡡ࡯ࡦࡶࠫ៉"),
  bstack1lll1_opy_ (u"ࠧࡪࡦ࡯ࡩ࡙࡯࡭ࡦࡱࡸࡸࠬ៊"): bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡪࡦ࡯ࡩ࡙࡯࡭ࡦࡱࡸࡸࠬ់"),
  bstack1lll1_opy_ (u"ࠩࡰࡥࡸࡱࡂࡢࡵ࡬ࡧࡆࡻࡴࡩࠩ៌"): bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡰࡥࡸࡱࡂࡢࡵ࡬ࡧࡆࡻࡴࡩࠩ៍"),
  bstack1lll1_opy_ (u"ࠫࡸ࡫࡮ࡥࡍࡨࡽࡸ࠭៎"): bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡸ࡫࡮ࡥࡍࡨࡽࡸ࠭៏"),
  bstack1lll1_opy_ (u"࠭ࡡࡶࡶࡲ࡛ࡦ࡯ࡴࠨ័"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡶࡶࡲ࡛ࡦ࡯ࡴࠨ៑"),
  bstack1lll1_opy_ (u"ࠨࡪࡲࡷࡹࡹ្ࠧ"): bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡪࡲࡷࡹࡹࠧ៓"),
  bstack1lll1_opy_ (u"ࠪࡦ࡫ࡩࡡࡤࡪࡨࠫ។"): bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦ࡫ࡩࡡࡤࡪࡨࠫ៕"),
  bstack1lll1_opy_ (u"ࠬࡽࡳࡍࡱࡦࡥࡱ࡙ࡵࡱࡲࡲࡶࡹ࠭៖"): bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡽࡳࡍࡱࡦࡥࡱ࡙ࡵࡱࡲࡲࡶࡹ࠭ៗ"),
  bstack1lll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡄࡱࡵࡷࡗ࡫ࡳࡵࡴ࡬ࡧࡹ࡯࡯࡯ࡵࠪ៘"): bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡥ࡫ࡶࡥࡧࡲࡥࡄࡱࡵࡷࡗ࡫ࡳࡵࡴ࡬ࡧࡹ࡯࡯࡯ࡵࠪ៙"),
  bstack1lll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭៚"): bstack1lll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪ៛"),
  bstack1lll1_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡏࡲࡦ࡮ࡲࡥࠨៜ"): bstack1lll1_opy_ (u"ࠬࡸࡥࡢ࡮ࡢࡱࡴࡨࡩ࡭ࡧࠪ៝"),
  bstack1lll1_opy_ (u"࠭ࡡࡱࡲ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭៞"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡱࡲ࡬ࡹࡲࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ៟"),
  bstack1lll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡏࡧࡷࡻࡴࡸ࡫ࠨ០"): bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡸࡷࡹࡵ࡭ࡏࡧࡷࡻࡴࡸ࡫ࠨ១"),
  bstack1lll1_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡔࡷࡵࡦࡪ࡮ࡨࠫ២"): bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡲࡪࡺࡷࡰࡴ࡮ࡔࡷࡵࡦࡪ࡮ࡨࠫ៣"),
  bstack1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡎࡴࡳࡦࡥࡸࡶࡪࡉࡥࡳࡶࡶࠫ៤"): bstack1lll1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹࡹࠧ៥"),
  bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩ៦"): bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩ៧"),
  bstack1lll1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩ៨"): bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡳࡺࡸࡣࡦࠩ៩"),
  bstack1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭៪"): bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭៫"),
  bstack1lll1_opy_ (u"࠭ࡨࡰࡵࡷࡒࡦࡳࡥࠨ៬"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡨࡰࡵࡷࡒࡦࡳࡥࠨ៭"),
  bstack1lll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡔ࡫ࡰࠫ៮"): bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡧࡱࡥࡧࡲࡥࡔ࡫ࡰࠫ៯"),
  bstack1lll1_opy_ (u"ࠪࡷ࡮ࡳࡏࡱࡶ࡬ࡳࡳࡹࠧ៰"): bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡷ࡮ࡳࡏࡱࡶ࡬ࡳࡳࡹࠧ៱"),
  bstack1lll1_opy_ (u"ࠬࡻࡰ࡭ࡱࡤࡨࡒ࡫ࡤࡪࡣࠪ៲"): bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡰ࡭ࡱࡤࡨࡒ࡫ࡤࡪࡣࠪ៳"),
  bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪ៴"): bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪ៵"),
  bstack1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫ៶"): bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫ៷")
}
bstack11l1ll1111l_opy_ = [
  bstack1lll1_opy_ (u"ࠫࡴࡹࠧ៸"),
  bstack1lll1_opy_ (u"ࠬࡵࡳࡗࡧࡵࡷ࡮ࡵ࡮ࠨ៹"),
  bstack1lll1_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ៺"),
  bstack1lll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ៻"),
  bstack1lll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠬ៼"),
  bstack1lll1_opy_ (u"ࠩࡵࡩࡦࡲࡍࡰࡤ࡬ࡰࡪ࠭៽"),
  bstack1lll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪ៾"),
]
bstack11ll111ll_opy_ = {
  bstack1lll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭៿"): [bstack1lll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭᠀"), bstack1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡢࡒࡆࡓࡅࠨ᠁")],
  bstack1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ᠂"): bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫ᠃"),
  bstack1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ᠄"): bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡐࡄࡑࡊ࠭᠅"),
  bstack1lll1_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩ᠆"): bstack1lll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡘࡏࡋࡇࡆࡘࡤࡔࡁࡎࡇࠪ᠇"),
  bstack1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ᠈"): bstack1lll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ᠉"),
  bstack1lll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ᠊"): bstack1lll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡄࡖࡆࡒࡌࡆࡎࡖࡣࡕࡋࡒࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࠪ᠋"),
  bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ᠌"): bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࠩ᠍"),
  bstack1lll1_opy_ (u"ࠬࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩ᠎"): bstack1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡘࡅࡓࡗࡑࡣ࡙ࡋࡓࡕࡕࠪ᠏"),
  bstack1lll1_opy_ (u"ࠧࡢࡲࡳࠫ᠐"): [bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡒࡓࡣࡎࡊࠧ᠑"), bstack1lll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡓࡔࠬ᠒")],
  bstack1lll1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬ᠓"): bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡗࡉࡑ࡟ࡍࡑࡊࡐࡊ࡜ࡅࡍࠩ᠔"),
  bstack1lll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩ᠕"): bstack1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩ᠖"),
  bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ᠗"): [bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡕࡂࡔࡇࡕ࡚ࡆࡈࡉࡍࡋࡗ࡝ࠬ᠘"), bstack1lll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡒࡆࡒࡒࡖ࡙ࡏࡎࡈࠩ᠙")],
  bstack1lll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧ᠚"): bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘ࡚ࡘࡂࡐࡕࡆࡅࡑࡋࠧ᠛"),
  bstack1lll1_opy_ (u"ࠬࡹ࡭ࡢࡴࡷࡗࡪࡲࡥࡤࡶ࡬ࡳࡳࡌࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࡪࡹࡅࡏࡘࠪ᠜"): bstack1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡕࡒࡄࡊࡈࡗ࡙ࡘࡁࡕࡋࡒࡒࡤ࡙ࡍࡂࡔࡗࡣࡘࡋࡌࡆࡅࡗࡍࡔࡔ࡟ࡇࡇࡄࡘ࡚ࡘࡅࡠࡄࡕࡅࡓࡉࡈࡆࡕࠪ᠝")
}
bstack1l1l11ll_opy_ = {
  bstack1lll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ᠞"): [bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨࡶࡤࡴࡡ࡮ࡧࠪ᠟"), bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡷࡶࡩࡷࡔࡡ࡮ࡧࠪᠠ")],
  bstack1lll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ᠡ"): [bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵࡢ࡯ࡪࡿࠧᠢ"), bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧᠣ")],
  bstack1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᠤ"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᠥ"),
  bstack1lll1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ᠦ"): bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ᠧ"),
  bstack1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᠨ"): bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᠩ"),
  bstack1lll1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬᠪ"): [bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡶࡰࡱࠩᠫ"), bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ᠬ")],
  bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬᠭ"): bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡮ࡲࡧࡦࡲࠧᠮ"),
  bstack1lll1_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡖࡨࡷࡹࡹࠧᠯ"): bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡶࡪࡸࡵ࡯ࡖࡨࡷࡹࡹࠧᠰ"),
  bstack1lll1_opy_ (u"ࠬࡧࡰࡱࠩᠱ"): bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡰࡱࠩᠲ"),
  bstack1lll1_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩᠳ"): bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩᠴ"),
  bstack1lll1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᠵ"): bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᠶ"),
  bstack1lll1_opy_ (u"ࠦࡸࡳࡡࡳࡶࡖࡩࡱ࡫ࡣࡵ࡫ࡲࡲࡋ࡫ࡡࡵࡷࡵࡩࡇࡸࡡ࡯ࡥ࡫ࡩࡸࡉࡌࡊࠤᠷ"): bstack1lll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠯ࡵࡰࡥࡷࡺࡓࡦ࡮ࡨࡧࡹ࡯࡯࡯ࡈࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࡦࡵࠥᠸ"),
}
bstack1l1ll1l1_opy_ = {
  bstack1lll1_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩᠹ"): bstack1lll1_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫᠺ"),
  bstack1lll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪᠻ"): [bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫᠼ"), bstack1lll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᠽ")],
  bstack1lll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩᠾ"): bstack1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᠿ"),
  bstack1lll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪᡀ"): bstack1lll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧᡁ"),
  bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ᡂ"): [bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪᡃ"), bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩᡄ")],
  bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᡅ"): bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᡆ"),
  bstack1lll1_opy_ (u"࠭ࡲࡦࡣ࡯ࡑࡴࡨࡩ࡭ࡧࠪᡇ"): bstack1lll1_opy_ (u"ࠧࡳࡧࡤࡰࡤࡳ࡯ࡣ࡫࡯ࡩࠬᡈ"),
  bstack1lll1_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᡉ"): [bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡳࡴ࡮ࡻ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᡊ"), bstack1lll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫᡋ")],
  bstack1lll1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪᡌ"): [bstack1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡘࡹ࡬ࡄࡧࡵࡸࡸ࠭ᡍ"), bstack1lll1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹ࠭ᡎ")]
}
bstack1lllll1lll_opy_ = [
  bstack1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸ࠭ᡏ"),
  bstack1lll1_opy_ (u"ࠨࡲࡤ࡫ࡪࡒ࡯ࡢࡦࡖࡸࡷࡧࡴࡦࡩࡼࠫᡐ"),
  bstack1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨᡑ"),
  bstack1lll1_opy_ (u"ࠪࡷࡪࡺࡗࡪࡰࡧࡳࡼࡘࡥࡤࡶࠪᡒ"),
  bstack1lll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࠭ᡓ"),
  bstack1lll1_opy_ (u"ࠬࡹࡴࡳ࡫ࡦࡸࡋ࡯࡬ࡦࡋࡱࡸࡪࡸࡡࡤࡶࡤࡦ࡮ࡲࡩࡵࡻࠪᡔ"),
  bstack1lll1_opy_ (u"࠭ࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࡒࡵࡳࡲࡶࡴࡃࡧ࡫ࡥࡻ࡯࡯ࡳࠩᡕ"),
  bstack1lll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᡖ"),
  bstack1lll1_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭ᡗ"),
  bstack1lll1_opy_ (u"ࠩࡰࡷ࠿࡫ࡤࡨࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᡘ"),
  bstack1lll1_opy_ (u"ࠪࡷࡪࡀࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᡙ"),
  bstack1lll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬᡚ"),
]
bstack11lllll11_opy_ = [
  bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩᡛ"),
  bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪᡜ"),
  bstack1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ᡝ"),
  bstack1lll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᡞ"),
  bstack1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᡟ"),
  bstack1lll1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬᡠ"),
  bstack1lll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧᡡ"),
  bstack1lll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩᡢ"),
  bstack1lll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩᡣ"),
  bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬᡤ"),
  bstack1lll1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬᡥ"),
  bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࠩᡦ"),
  bstack1lll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯࡙ࡥࡷ࡯ࡡࡣ࡮ࡨࡷࠬᡧ"),
  bstack1lll1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡘࡦ࡭ࠧᡨ"),
  bstack1lll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᡩ"),
  bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᡪ"),
  bstack1lll1_opy_ (u"ࠧࡳࡧࡵࡹࡳ࡚ࡥࡴࡶࡶࠫᡫ"),
  bstack1lll1_opy_ (u"ࠨࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤ࠷ࠧᡬ"),
  bstack1lll1_opy_ (u"ࠩࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࠲ࠨᡭ"),
  bstack1lll1_opy_ (u"ࠪࡇ࡚࡙ࡔࡐࡏࡢࡘࡆࡍ࡟࠴ࠩᡮ"),
  bstack1lll1_opy_ (u"ࠫࡈ࡛ࡓࡕࡑࡐࡣ࡙ࡇࡇࡠ࠶ࠪᡯ"),
  bstack1lll1_opy_ (u"ࠬࡉࡕࡔࡖࡒࡑࡤ࡚ࡁࡈࡡ࠸ࠫᡰ"),
  bstack1lll1_opy_ (u"࠭ࡃࡖࡕࡗࡓࡒࡥࡔࡂࡉࡢ࠺ࠬᡱ"),
  bstack1lll1_opy_ (u"ࠧࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࡣ࠼࠭ᡲ"),
  bstack1lll1_opy_ (u"ࠨࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤ࠾ࠧᡳ"),
  bstack1lll1_opy_ (u"ࠩࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࠹ࠨᡴ"),
  bstack1lll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩᡵ"),
  bstack1lll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᡶ"),
  bstack1lll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡇࡦࡶࡴࡶࡴࡨࡑࡴࡪࡥࠨᡷ"),
  bstack1lll1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁࡶࡶࡲࡇࡦࡶࡴࡶࡴࡨࡐࡴ࡭ࡳࠨᡸ"),
  bstack1lll1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ᡹"),
  bstack1lll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࡔࡶࡴࡪࡱࡱࡷࠬ᡺"),
  bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࡕࡰࡵ࡫ࡲࡲࡸ࠭᡻")
]
bstack11l1ll11lll_opy_ = [
  bstack1lll1_opy_ (u"ࠪࡹࡵࡲ࡯ࡢࡦࡐࡩࡩ࡯ࡡࠨ᡼"),
  bstack1lll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭᡽"),
  bstack1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ᡾"),
  bstack1lll1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ᡿"),
  bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡕࡸࡩࡰࡴ࡬ࡸࡾ࠭ᢀ"),
  bstack1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫᢁ"),
  bstack1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡕࡣࡪࠫᢂ"),
  bstack1lll1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᢃ"),
  bstack1lll1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᢄ"),
  bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪᢅ"),
  bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᢆ"),
  bstack1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭ᢇ"),
  bstack1lll1_opy_ (u"ࠨࡱࡶࠫᢈ"),
  bstack1lll1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬᢉ"),
  bstack1lll1_opy_ (u"ࠪ࡬ࡴࡹࡴࡴࠩᢊ"),
  bstack1lll1_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ᢋ"),
  bstack1lll1_opy_ (u"ࠬࡸࡥࡨ࡫ࡲࡲࠬᢌ"),
  bstack1lll1_opy_ (u"࠭ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨᢍ"),
  bstack1lll1_opy_ (u"ࠧ࡮ࡣࡦ࡬࡮ࡴࡥࠨᢎ"),
  bstack1lll1_opy_ (u"ࠨࡴࡨࡷࡴࡲࡵࡵ࡫ࡲࡲࠬᢏ"),
  bstack1lll1_opy_ (u"ࠩ࡬ࡨࡱ࡫ࡔࡪ࡯ࡨࡳࡺࡺࠧᢐ"),
  bstack1lll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡒࡶ࡮࡫࡮ࡵࡣࡷ࡭ࡴࡴࠧᢑ"),
  bstack1lll1_opy_ (u"ࠫࡻ࡯ࡤࡦࡱࠪᢒ"),
  bstack1lll1_opy_ (u"ࠬࡴ࡯ࡑࡣࡪࡩࡑࡵࡡࡥࡖ࡬ࡱࡪࡵࡵࡵࠩᢓ"),
  bstack1lll1_opy_ (u"࠭ࡢࡧࡥࡤࡧ࡭࡫ࠧᢔ"),
  bstack1lll1_opy_ (u"ࠧࡥࡧࡥࡹ࡬࠭ᢕ"),
  bstack1lll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡔࡥࡵࡩࡪࡴࡳࡩࡱࡷࡷࠬᢖ"),
  bstack1lll1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡕࡨࡲࡩࡑࡥࡺࡵࠪᢗ"),
  bstack1lll1_opy_ (u"ࠪࡶࡪࡧ࡬ࡎࡱࡥ࡭ࡱ࡫ࠧᢘ"),
  bstack1lll1_opy_ (u"ࠫࡳࡵࡐࡪࡲࡨࡰ࡮ࡴࡥࠨᢙ"),
  bstack1lll1_opy_ (u"ࠬࡩࡨࡦࡥ࡮࡙ࡗࡒࠧᢚ"),
  bstack1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᢛ"),
  bstack1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡃࡰࡱ࡮࡭ࡪࡹࠧᢜ"),
  bstack1lll1_opy_ (u"ࠨࡥࡤࡴࡹࡻࡲࡦࡅࡵࡥࡸ࡮ࠧᢝ"),
  bstack1lll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭ᢞ"),
  bstack1lll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪᢟ"),
  bstack1lll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᢠ"),
  bstack1lll1_opy_ (u"ࠬࡴ࡯ࡃ࡮ࡤࡲࡰࡖ࡯࡭࡮࡬ࡲ࡬࠭ᢡ"),
  bstack1lll1_opy_ (u"࠭࡭ࡢࡵ࡮ࡗࡪࡴࡤࡌࡧࡼࡷࠬᢢ"),
  bstack1lll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡌࡰࡩࡶࠫᢣ"),
  bstack1lll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡊࡦࠪᢤ"),
  bstack1lll1_opy_ (u"ࠩࡧࡩࡩ࡯ࡣࡢࡶࡨࡨࡉ࡫ࡶࡪࡥࡨࠫᢥ"),
  bstack1lll1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡓࡥࡷࡧ࡭ࡴࠩᢦ"),
  bstack1lll1_opy_ (u"ࠫࡵ࡮࡯࡯ࡧࡑࡹࡲࡨࡥࡳࠩᢧ"),
  bstack1lll1_opy_ (u"ࠬࡴࡥࡵࡹࡲࡶࡰࡒ࡯ࡨࡵࠪᢨ"),
  bstack1lll1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡌࡰࡩࡶࡓࡵࡺࡩࡰࡰࡶᢩࠫ"),
  bstack1lll1_opy_ (u"ࠧࡤࡱࡱࡷࡴࡲࡥࡍࡱࡪࡷࠬᢪ"),
  bstack1lll1_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨ᢫"),
  bstack1lll1_opy_ (u"ࠩࡤࡴࡵ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭᢬"),
  bstack1lll1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡅ࡭ࡴࡳࡥࡵࡴ࡬ࡧࠬ᢭"),
  bstack1lll1_opy_ (u"ࠫࡻ࡯ࡤࡦࡱ࡙࠶ࠬ᢮"),
  bstack1lll1_opy_ (u"ࠬࡳࡩࡥࡕࡨࡷࡸ࡯࡯࡯ࡋࡱࡷࡹࡧ࡬࡭ࡃࡳࡴࡸ࠭᢯"),
  bstack1lll1_opy_ (u"࠭ࡥࡴࡲࡵࡩࡸࡹ࡯ࡔࡧࡵࡺࡪࡸࠧᢰ"),
  bstack1lll1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭ᢱ"),
  bstack1lll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࡆࡨࡵ࠭ᢲ"),
  bstack1lll1_opy_ (u"ࠩࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩᢳ"),
  bstack1lll1_opy_ (u"ࠪࡷࡾࡴࡣࡕ࡫ࡰࡩ࡜࡯ࡴࡩࡐࡗࡔࠬᢴ"),
  bstack1lll1_opy_ (u"ࠫ࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩᢵ"),
  bstack1lll1_opy_ (u"ࠬ࡭ࡰࡴࡎࡲࡧࡦࡺࡩࡰࡰࠪᢶ"),
  bstack1lll1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡐࡳࡱࡩ࡭ࡱ࡫ࠧᢷ"),
  bstack1lll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡎࡦࡶࡺࡳࡷࡱࠧᢸ"),
  bstack1lll1_opy_ (u"ࠨࡨࡲࡶࡨ࡫ࡃࡩࡣࡱ࡫ࡪࡐࡡࡳࠩᢹ"),
  bstack1lll1_opy_ (u"ࠩࡻࡱࡸࡐࡡࡳࠩᢺ"),
  bstack1lll1_opy_ (u"ࠪࡼࡲࡾࡊࡢࡴࠪᢻ"),
  bstack1lll1_opy_ (u"ࠫࡲࡧࡳ࡬ࡅࡲࡱࡲࡧ࡮ࡥࡵࠪᢼ"),
  bstack1lll1_opy_ (u"ࠬࡳࡡࡴ࡭ࡅࡥࡸ࡯ࡣࡂࡷࡷ࡬ࠬᢽ"),
  bstack1lll1_opy_ (u"࠭ࡷࡴࡎࡲࡧࡦࡲࡓࡶࡲࡳࡳࡷࡺࠧᢾ"),
  bstack1lll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡄࡱࡵࡷࡗ࡫ࡳࡵࡴ࡬ࡧࡹ࡯࡯࡯ࡵࠪᢿ"),
  bstack1lll1_opy_ (u"ࠨࡣࡳࡴ࡛࡫ࡲࡴ࡫ࡲࡲࠬᣀ"),
  bstack1lll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡰࡵࡋࡱࡷࡪࡩࡵࡳࡧࡆࡩࡷࡺࡳࠨᣁ"),
  bstack1lll1_opy_ (u"ࠪࡶࡪࡹࡩࡨࡰࡄࡴࡵ࠭ᣂ"),
  bstack1lll1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡴࡩ࡮ࡣࡷ࡭ࡴࡴࡳࠨᣃ"),
  bstack1lll1_opy_ (u"ࠬࡩࡡ࡯ࡣࡵࡽࠬᣄ"),
  bstack1lll1_opy_ (u"࠭ࡦࡪࡴࡨࡪࡴࡾࠧᣅ"),
  bstack1lll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧᣆ"),
  bstack1lll1_opy_ (u"ࠨ࡫ࡨࠫᣇ"),
  bstack1lll1_opy_ (u"ࠩࡨࡨ࡬࡫ࠧᣈ"),
  bstack1lll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪᣉ"),
  bstack1lll1_opy_ (u"ࠫࡶࡻࡥࡶࡧࠪᣊ"),
  bstack1lll1_opy_ (u"ࠬ࡯࡮ࡵࡧࡵࡲࡦࡲࠧᣋ"),
  bstack1lll1_opy_ (u"࠭ࡡࡱࡲࡖࡸࡴࡸࡥࡄࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠧᣌ"),
  bstack1lll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡃࡢ࡯ࡨࡶࡦࡏ࡭ࡢࡩࡨࡍࡳࡰࡥࡤࡶ࡬ࡳࡳ࠭ᣍ"),
  bstack1lll1_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸࡋࡸࡤ࡮ࡸࡨࡪࡎ࡯ࡴࡶࡶࠫᣎ"),
  bstack1lll1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࡉ࡯ࡥ࡯ࡹࡩ࡫ࡈࡰࡵࡷࡷࠬᣏ"),
  bstack1lll1_opy_ (u"ࠪࡹࡵࡪࡡࡵࡧࡄࡴࡵ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠧᣐ"),
  bstack1lll1_opy_ (u"ࠫࡷ࡫ࡳࡦࡴࡹࡩࡉ࡫ࡶࡪࡥࡨࠫᣑ"),
  bstack1lll1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬᣒ"),
  bstack1lll1_opy_ (u"࠭ࡳࡦࡰࡧࡏࡪࡿࡳࠨᣓ"),
  bstack1lll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡐࡢࡵࡶࡧࡴࡪࡥࠨᣔ"),
  bstack1lll1_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡊࡱࡶࡈࡪࡼࡩࡤࡧࡖࡩࡹࡺࡩ࡯ࡩࡶࠫᣕ"),
  bstack1lll1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡃࡸࡨ࡮ࡵࡉ࡯࡬ࡨࡧࡹ࡯࡯࡯ࠩᣖ"),
  bstack1lll1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡄࡴࡵࡲࡥࡑࡣࡼࠫᣗ"),
  bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬᣘ"),
  bstack1lll1_opy_ (u"ࠬࡽࡤࡪࡱࡖࡩࡷࡼࡩࡤࡧࠪᣙ"),
  bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨᣚ"),
  bstack1lll1_opy_ (u"ࠧࡱࡴࡨࡺࡪࡴࡴࡄࡴࡲࡷࡸ࡙ࡩࡵࡧࡗࡶࡦࡩ࡫ࡪࡰࡪࠫᣛ"),
  bstack1lll1_opy_ (u"ࠨࡪ࡬࡫࡭ࡉ࡯࡯ࡶࡵࡥࡸࡺࠧᣜ"),
  bstack1lll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡒࡵࡩ࡫࡫ࡲࡦࡰࡦࡩࡸ࠭ᣝ"),
  bstack1lll1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡖ࡭ࡲ࠭ᣞ"),
  bstack1lll1_opy_ (u"ࠫࡸ࡯࡭ࡐࡲࡷ࡭ࡴࡴࡳࠨᣟ"),
  bstack1lll1_opy_ (u"ࠬࡸࡥ࡮ࡱࡹࡩࡎࡕࡓࡂࡲࡳࡗࡪࡺࡴࡪࡰࡪࡷࡑࡵࡣࡢ࡮࡬ࡾࡦࡺࡩࡰࡰࠪᣠ"),
  bstack1lll1_opy_ (u"࠭ࡨࡰࡵࡷࡒࡦࡳࡥࠨᣡ"),
  bstack1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩᣢ"),
  bstack1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᣣ"),
  bstack1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠨᣤ"),
  bstack1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬᣥ"),
  bstack1lll1_opy_ (u"ࠫࡵࡧࡧࡦࡎࡲࡥࡩ࡙ࡴࡳࡣࡷࡩ࡬ࡿࠧᣦ"),
  bstack1lll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫᣧ"),
  bstack1lll1_opy_ (u"࠭ࡴࡪ࡯ࡨࡳࡺࡺࡳࠨᣨ"),
  bstack1lll1_opy_ (u"ࠧࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡓࡶࡴࡳࡰࡵࡄࡨ࡬ࡦࡼࡩࡰࡴࠪᣩ")
]
bstack1l11ll11_opy_ = {
  bstack1lll1_opy_ (u"ࠨࡸࠪᣪ"): bstack1lll1_opy_ (u"ࠩࡹࠫᣫ"),
  bstack1lll1_opy_ (u"ࠪࡪࠬᣬ"): bstack1lll1_opy_ (u"ࠫ࡫࠭ᣭ"),
  bstack1lll1_opy_ (u"ࠬ࡬࡯ࡳࡥࡨࠫᣮ"): bstack1lll1_opy_ (u"࠭ࡦࡰࡴࡦࡩࠬᣯ"),
  bstack1lll1_opy_ (u"ࠧࡰࡰ࡯ࡽࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ᣰ"): bstack1lll1_opy_ (u"ࠨࡱࡱࡰࡾࡇࡵࡵࡱࡰࡥࡹ࡫ࠧᣱ"),
  bstack1lll1_opy_ (u"ࠩࡩࡳࡷࡩࡥ࡭ࡱࡦࡥࡱ࠭ᣲ"): bstack1lll1_opy_ (u"ࠪࡪࡴࡸࡣࡦ࡮ࡲࡧࡦࡲࠧᣳ"),
  bstack1lll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻ࡫ࡳࡸࡺࠧᣴ"): bstack1lll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡌࡴࡹࡴࠨᣵ"),
  bstack1lll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡵࡵࡲࡵࠩ᣶"): bstack1lll1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖ࡯ࡳࡶࠪ᣷"),
  bstack1lll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡵࡴࡧࡵࠫ᣸"): bstack1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬ᣹"),
  bstack1lll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡲࡤࡷࡸ࠭᣺"): bstack1lll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡥࡸࡹࠧ᣻"),
  bstack1lll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡪࡲࡷࡹ࠭᣼"): bstack1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡋࡳࡸࡺࠧ᣽"),
  bstack1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡴࡴࡸࡴࠨ᣾"): bstack1lll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡵࡲࡵࠩ᣿"),
  bstack1lll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡱࡴࡲࡼࡾࡻࡳࡦࡴࠪᤀ"): bstack1lll1_opy_ (u"ࠪ࠱ࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡖࡵࡨࡶࠬᤁ"),
  bstack1lll1_opy_ (u"ࠫ࠲ࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡷࡶࡩࡷ࠭ᤂ"): bstack1lll1_opy_ (u"ࠬ࠳࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡘࡷࡪࡸࠧᤃ"),
  bstack1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡵࡸ࡯ࡹࡻࡳࡥࡸࡹࠧᤄ"): bstack1lll1_opy_ (u"ࠧ࠮࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡧࡳࡴࠩᤅ"),
  bstack1lll1_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡱࡴࡲࡼࡾࡶࡡࡴࡵࠪᤆ"): bstack1lll1_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡒࡵࡳࡽࡿࡐࡢࡵࡶࠫᤇ"),
  bstack1lll1_opy_ (u"ࠪࡦ࡮ࡴࡡࡳࡻࡳࡥࡹ࡮ࠧᤈ"): bstack1lll1_opy_ (u"ࠫࡧ࡯࡮ࡢࡴࡼࡴࡦࡺࡨࠨᤉ"),
  bstack1lll1_opy_ (u"ࠬࡶࡡࡤࡨ࡬ࡰࡪ࠭ᤊ"): bstack1lll1_opy_ (u"࠭࠭ࡱࡣࡦ࠱࡫࡯࡬ࡦࠩᤋ"),
  bstack1lll1_opy_ (u"ࠧࡱࡣࡦ࠱࡫࡯࡬ࡦࠩᤌ"): bstack1lll1_opy_ (u"ࠨ࠯ࡳࡥࡨ࠳ࡦࡪ࡮ࡨࠫᤍ"),
  bstack1lll1_opy_ (u"ࠩ࠰ࡴࡦࡩ࠭ࡧ࡫࡯ࡩࠬᤎ"): bstack1lll1_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭ᤏ"),
  bstack1lll1_opy_ (u"ࠫࡱࡵࡧࡧ࡫࡯ࡩࠬᤐ"): bstack1lll1_opy_ (u"ࠬࡲ࡯ࡨࡨ࡬ࡰࡪ࠭ᤑ"),
  bstack1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᤒ"): bstack1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩᤓ"),
  bstack1lll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭࠮ࡴࡨࡴࡪࡧࡴࡦࡴࠪᤔ"): bstack1lll1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡔࡨࡴࡪࡧࡴࡦࡴࠪᤕ")
}
bstack11l1l1l11ll_opy_ = bstack1lll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳࡬࡯ࡴࡩࡷࡥ࠲ࡨࡵ࡭࠰ࡲࡨࡶࡨࡿ࠯ࡤ࡮࡬࠳ࡷ࡫࡬ࡦࡣࡶࡩࡸ࠵࡬ࡢࡶࡨࡷࡹ࠵ࡤࡰࡹࡱࡰࡴࡧࡤࠣᤖ")
bstack11l1ll11ll1_opy_ = bstack1lll1_opy_ (u"ࠦ࠴ࡶࡥࡳࡥࡼ࠳࡭࡫ࡡ࡭ࡶ࡫ࡧ࡭࡫ࡣ࡬ࠤᤗ")
bstack1l1lll1lll_opy_ = bstack1lll1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡥࡥࡵ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡳࡦࡰࡧࡣࡸࡪ࡫ࡠࡧࡹࡩࡳࡺࡳࠣᤘ")
bstack1lllll11l_opy_ = bstack1lll1_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡸࡦ࠲࡬ࡺࡨࠧᤙ")
bstack11ll11l1ll_opy_ = bstack1lll1_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠪᤚ")
bstack1l11l11ll_opy_ = bstack1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱࡫ࡹࡧ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡱࡩࡽࡺ࡟ࡩࡷࡥࡷࠬᤛ")
bstack11l1l1lll1l_opy_ = {
  bstack1lll1_opy_ (u"ࠩࡦࡶ࡮ࡺࡩࡤࡣ࡯ࠫᤜ"): 50,
  bstack1lll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᤝ"): 40,
  bstack1lll1_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬᤞ"): 30,
  bstack1lll1_opy_ (u"ࠬ࡯࡮ࡧࡱࠪ᤟"): 20,
  bstack1lll1_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬᤠ"): 10
}
bstack1ll1l1lll_opy_ = bstack11l1l1lll1l_opy_[bstack1lll1_opy_ (u"ࠧࡪࡰࡩࡳࠬᤡ")]
bstack1l1111llll_opy_ = bstack1lll1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧᤢ")
bstack11ll11l1_opy_ = bstack1lll1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧᤣ")
bstack11llllll1l_opy_ = bstack1lll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧ࠰ࡴࡾࡺࡨࡰࡰࡤ࡫ࡪࡴࡴ࠰ࠩᤤ")
bstack1l111l11l_opy_ = bstack1lll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡵࡿࡴࡩࡱࡱࡥ࡬࡫࡮ࡵ࠱ࠪᤥ")
bstack1l11111l_opy_ = bstack1lll1_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰࡺࡶࡨࡷࡹࠦࡡ࡯ࡦࠣࡴࡾࡺࡥࡴࡶ࠰ࡷࡪࡲࡥ࡯࡫ࡸࡱࠥࡶࡡࡤ࡭ࡤ࡫ࡪࡹ࠮ࠡࡢࡳ࡭ࡵࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡱࡻࡷࡩࡸࡺࠠࡱࡻࡷࡩࡸࡺ࠭ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡢࠪᤦ")
bstack11l1l1l1ll1_opy_ = [bstack1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧᤧ"), bstack1lll1_opy_ (u"࡚ࠧࡑࡘࡖࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧᤨ")]
bstack11l1l1ll111_opy_ = [bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫᤩ"), bstack1lll1_opy_ (u"ࠩ࡜ࡓ࡚ࡘ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫᤪ")]
bstack11111l1l_opy_ = re.compile(bstack1lll1_opy_ (u"ࠪࡢࡠࡢ࡜ࡸ࠯ࡠ࠯࠿࠴ࠪࠥࠩᤫ"))
bstack11ll1lllll_opy_ = [
  bstack1lll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡏࡣࡰࡩࠬ᤬"),
  bstack1lll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧ᤭"),
  bstack1lll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪ᤮"),
  bstack1lll1_opy_ (u"ࠧ࡯ࡧࡺࡇࡴࡳ࡭ࡢࡰࡧࡘ࡮ࡳࡥࡰࡷࡷࠫ᤯"),
  bstack1lll1_opy_ (u"ࠨࡣࡳࡴࠬᤰ"),
  bstack1lll1_opy_ (u"ࠩࡸࡨ࡮ࡪࠧᤱ"),
  bstack1lll1_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩࠬᤲ"),
  bstack1lll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡨࠫᤳ"),
  bstack1lll1_opy_ (u"ࠬࡵࡲࡪࡧࡱࡸࡦࡺࡩࡰࡰࠪᤴ"),
  bstack1lll1_opy_ (u"࠭ࡡࡶࡶࡲ࡛ࡪࡨࡶࡪࡧࡺࠫᤵ"),
  bstack1lll1_opy_ (u"ࠧ࡯ࡱࡕࡩࡸ࡫ࡴࠨᤶ"), bstack1lll1_opy_ (u"ࠨࡨࡸࡰࡱࡘࡥࡴࡧࡷࠫᤷ"),
  bstack1lll1_opy_ (u"ࠩࡦࡰࡪࡧࡲࡔࡻࡶࡸࡪࡳࡆࡪ࡮ࡨࡷࠬᤸ"),
  bstack1lll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡖ࡬ࡱ࡮ࡴࡧࡴ᤹ࠩ"),
  bstack1lll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡔࡪࡸࡦࡰࡴࡰࡥࡳࡩࡥࡍࡱࡪ࡫࡮ࡴࡧࠨ᤺"),
  bstack1lll1_opy_ (u"ࠬࡵࡴࡩࡧࡵࡅࡵࡶࡳࠨ᤻"),
  bstack1lll1_opy_ (u"࠭ࡰࡳ࡫ࡱࡸࡕࡧࡧࡦࡕࡲࡹࡷࡩࡥࡐࡰࡉ࡭ࡳࡪࡆࡢ࡫࡯ࡹࡷ࡫ࠧ᤼"),
  bstack1lll1_opy_ (u"ࠧࡢࡲࡳࡅࡨࡺࡩࡷ࡫ࡷࡽࠬ᤽"), bstack1lll1_opy_ (u"ࠨࡣࡳࡴࡕࡧࡣ࡬ࡣࡪࡩࠬ᤾"), bstack1lll1_opy_ (u"ࠩࡤࡴࡵ࡝ࡡࡪࡶࡄࡧࡹ࡯ࡶࡪࡶࡼࠫ᤿"), bstack1lll1_opy_ (u"ࠪࡥࡵࡶࡗࡢ࡫ࡷࡔࡦࡩ࡫ࡢࡩࡨࠫ᥀"), bstack1lll1_opy_ (u"ࠫࡦࡶࡰࡘࡣ࡬ࡸࡉࡻࡲࡢࡶ࡬ࡳࡳ࠭᥁"),
  bstack1lll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡗ࡫ࡡࡥࡻࡗ࡭ࡲ࡫࡯ࡶࡶࠪ᥂"),
  bstack1lll1_opy_ (u"࠭ࡡ࡭࡮ࡲࡻ࡙࡫ࡳࡵࡒࡤࡧࡰࡧࡧࡦࡵࠪ᥃"),
  bstack1lll1_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡄࡱࡹࡩࡷࡧࡧࡦࠩ᥄"), bstack1lll1_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡅࡲࡺࡪࡸࡡࡨࡧࡈࡲࡩࡏ࡮ࡵࡧࡱࡸࠬ᥅"),
  bstack1lll1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡇࡩࡻ࡯ࡣࡦࡔࡨࡥࡩࡿࡔࡪ࡯ࡨࡳࡺࡺࠧ᥆"),
  bstack1lll1_opy_ (u"ࠪࡥࡩࡨࡐࡰࡴࡷࠫ᥇"),
  bstack1lll1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡉ࡫ࡶࡪࡥࡨࡗࡴࡩ࡫ࡦࡶࠪ᥈"),
  bstack1lll1_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡏ࡮ࡴࡶࡤࡰࡱ࡚ࡩ࡮ࡧࡲࡹࡹ࠭᥉"),
  bstack1lll1_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡉ࡯ࡵࡷࡥࡱࡲࡐࡢࡶ࡫ࠫ᥊"),
  bstack1lll1_opy_ (u"ࠧࡢࡸࡧࠫ᥋"), bstack1lll1_opy_ (u"ࠨࡣࡹࡨࡑࡧࡵ࡯ࡥ࡫ࡘ࡮ࡳࡥࡰࡷࡷࠫ᥌"), bstack1lll1_opy_ (u"ࠩࡤࡺࡩࡘࡥࡢࡦࡼࡘ࡮ࡳࡥࡰࡷࡷࠫ᥍"), bstack1lll1_opy_ (u"ࠪࡥࡻࡪࡁࡳࡩࡶࠫ᥎"),
  bstack1lll1_opy_ (u"ࠫࡺࡹࡥࡌࡧࡼࡷࡹࡵࡲࡦࠩ᥏"), bstack1lll1_opy_ (u"ࠬࡱࡥࡺࡵࡷࡳࡷ࡫ࡐࡢࡶ࡫ࠫᥐ"), bstack1lll1_opy_ (u"࠭࡫ࡦࡻࡶࡸࡴࡸࡥࡑࡣࡶࡷࡼࡵࡲࡥࠩᥑ"),
  bstack1lll1_opy_ (u"ࠧ࡬ࡧࡼࡅࡱ࡯ࡡࡴࠩᥒ"), bstack1lll1_opy_ (u"ࠨ࡭ࡨࡽࡕࡧࡳࡴࡹࡲࡶࡩ࠭ᥓ"),
  bstack1lll1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡆࡺࡨࡧࡺࡺࡡࡣ࡮ࡨࠫᥔ"), bstack1lll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡃࡵ࡫ࡸ࠭ᥕ"), bstack1lll1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡈࡼࡪࡩࡵࡵࡣࡥࡰࡪࡊࡩࡳࠩᥖ"), bstack1lll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡇ࡭ࡸ࡯࡮ࡧࡐࡥࡵࡶࡩ࡯ࡩࡉ࡭ࡱ࡫ࠧᥗ"), bstack1lll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶ࡚ࡹࡥࡔࡻࡶࡸࡪࡳࡅࡹࡧࡦࡹࡹࡧࡢ࡭ࡧࠪᥘ"),
  bstack1lll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡖ࡯ࡳࡶࠪᥙ"), bstack1lll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡐࡰࡴࡷࡷࠬᥚ"),
  bstack1lll1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡅ࡫ࡶࡥࡧࡲࡥࡃࡷ࡬ࡰࡩࡉࡨࡦࡥ࡮ࠫᥛ"),
  bstack1lll1_opy_ (u"ࠪࡥࡺࡺ࡯ࡘࡧࡥࡺ࡮࡫ࡷࡕ࡫ࡰࡩࡴࡻࡴࠨᥜ"),
  bstack1lll1_opy_ (u"ࠫ࡮ࡴࡴࡦࡰࡷࡅࡨࡺࡩࡰࡰࠪᥝ"), bstack1lll1_opy_ (u"ࠬ࡯࡮ࡵࡧࡱࡸࡈࡧࡴࡦࡩࡲࡶࡾ࠭ᥞ"), bstack1lll1_opy_ (u"࠭ࡩ࡯ࡶࡨࡲࡹࡌ࡬ࡢࡩࡶࠫᥟ"), bstack1lll1_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡡ࡭ࡋࡱࡸࡪࡴࡴࡂࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᥠ"),
  bstack1lll1_opy_ (u"ࠨࡦࡲࡲࡹ࡙ࡴࡰࡲࡄࡴࡵࡕ࡮ࡓࡧࡶࡩࡹ࠭ᥡ"),
  bstack1lll1_opy_ (u"ࠩࡸࡲ࡮ࡩ࡯ࡥࡧࡎࡩࡾࡨ࡯ࡢࡴࡧࠫᥢ"), bstack1lll1_opy_ (u"ࠪࡶࡪࡹࡥࡵࡍࡨࡽࡧࡵࡡࡳࡦࠪᥣ"),
  bstack1lll1_opy_ (u"ࠫࡳࡵࡓࡪࡩࡱࠫᥤ"),
  bstack1lll1_opy_ (u"ࠬ࡯ࡧ࡯ࡱࡵࡩ࡚ࡴࡩ࡮ࡲࡲࡶࡹࡧ࡮ࡵࡘ࡬ࡩࡼࡹࠧᥥ"),
  bstack1lll1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁ࡯ࡦࡵࡳ࡮ࡪࡗࡢࡶࡦ࡬ࡪࡸࡳࠨᥦ"),
  bstack1lll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᥧ"),
  bstack1lll1_opy_ (u"ࠨࡴࡨࡧࡷ࡫ࡡࡵࡧࡆ࡬ࡷࡵ࡭ࡦࡆࡵ࡭ࡻ࡫ࡲࡔࡧࡶࡷ࡮ࡵ࡮ࡴࠩᥨ"),
  bstack1lll1_opy_ (u"ࠩࡱࡥࡹ࡯ࡶࡦ࡙ࡨࡦࡘࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠨᥩ"),
  bstack1lll1_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡗࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡐࡢࡶ࡫ࠫᥪ"),
  bstack1lll1_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡘࡶࡥࡦࡦࠪᥫ"),
  bstack1lll1_opy_ (u"ࠬ࡭ࡰࡴࡇࡱࡥࡧࡲࡥࡥࠩᥬ"),
  bstack1lll1_opy_ (u"࠭ࡩࡴࡊࡨࡥࡩࡲࡥࡴࡵࠪᥭ"),
  bstack1lll1_opy_ (u"ࠧࡢࡦࡥࡉࡽ࡫ࡣࡕ࡫ࡰࡩࡴࡻࡴࠨ᥮"),
  bstack1lll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡥࡔࡥࡵ࡭ࡵࡺࠧ᥯"),
  bstack1lll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡄࡦࡸ࡬ࡧࡪࡏ࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡢࡶ࡬ࡳࡳ࠭ᥰ"),
  bstack1lll1_opy_ (u"ࠪࡥࡺࡺ࡯ࡈࡴࡤࡲࡹࡖࡥࡳ࡯࡬ࡷࡸ࡯࡯࡯ࡵࠪᥱ"),
  bstack1lll1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡓࡧࡴࡶࡴࡤࡰࡔࡸࡩࡦࡰࡷࡥࡹ࡯࡯࡯ࠩᥲ"),
  bstack1lll1_opy_ (u"ࠬࡹࡹࡴࡶࡨࡱࡕࡵࡲࡵࠩᥳ"),
  bstack1lll1_opy_ (u"࠭ࡲࡦ࡯ࡲࡸࡪࡇࡤࡣࡊࡲࡷࡹ࠭ᥴ"),
  bstack1lll1_opy_ (u"ࠧࡴ࡭࡬ࡴ࡚ࡴ࡬ࡰࡥ࡮ࠫ᥵"), bstack1lll1_opy_ (u"ࠨࡷࡱࡰࡴࡩ࡫ࡕࡻࡳࡩࠬ᥶"), bstack1lll1_opy_ (u"ࠩࡸࡲࡱࡵࡣ࡬ࡍࡨࡽࠬ᥷"),
  bstack1lll1_opy_ (u"ࠪࡥࡺࡺ࡯ࡍࡣࡸࡲࡨ࡮ࠧ᥸"),
  bstack1lll1_opy_ (u"ࠫࡸࡱࡩࡱࡎࡲ࡫ࡨࡧࡴࡄࡣࡳࡸࡺࡸࡥࠨ᥹"),
  bstack1lll1_opy_ (u"ࠬࡻ࡮ࡪࡰࡶࡸࡦࡲ࡬ࡐࡶ࡫ࡩࡷࡖࡡࡤ࡭ࡤ࡫ࡪࡹࠧ᥺"),
  bstack1lll1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡗࡪࡰࡧࡳࡼࡇ࡮ࡪ࡯ࡤࡸ࡮ࡵ࡮ࠨ᥻"),
  bstack1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩ࡚࡯ࡰ࡮ࡶ࡚ࡪࡸࡳࡪࡱࡱࠫ᥼"),
  bstack1lll1_opy_ (u"ࠨࡧࡱࡪࡴࡸࡣࡦࡃࡳࡴࡎࡴࡳࡵࡣ࡯ࡰࠬ᥽"),
  bstack1lll1_opy_ (u"ࠩࡨࡲࡸࡻࡲࡦ࡙ࡨࡦࡻ࡯ࡥࡸࡵࡋࡥࡻ࡫ࡐࡢࡩࡨࡷࠬ᥾"), bstack1lll1_opy_ (u"ࠪࡻࡪࡨࡶࡪࡧࡺࡈࡪࡼࡴࡰࡱ࡯ࡷࡕࡵࡲࡵࠩ᥿"), bstack1lll1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨ࡛ࡪࡨࡶࡪࡧࡺࡈࡪࡺࡡࡪ࡮ࡶࡇࡴࡲ࡬ࡦࡥࡷ࡭ࡴࡴࠧᦀ"),
  bstack1lll1_opy_ (u"ࠬࡸࡥ࡮ࡱࡷࡩࡆࡶࡰࡴࡅࡤࡧ࡭࡫ࡌࡪ࡯࡬ࡸࠬᦁ"),
  bstack1lll1_opy_ (u"࠭ࡣࡢ࡮ࡨࡲࡩࡧࡲࡇࡱࡵࡱࡦࡺࠧᦂ"),
  bstack1lll1_opy_ (u"ࠧࡣࡷࡱࡨࡱ࡫ࡉࡥࠩᦃ"),
  bstack1lll1_opy_ (u"ࠨ࡮ࡤࡹࡳࡩࡨࡕ࡫ࡰࡩࡴࡻࡴࠨᦄ"),
  bstack1lll1_opy_ (u"ࠩ࡯ࡳࡨࡧࡴࡪࡱࡱࡗࡪࡸࡶࡪࡥࡨࡷࡊࡴࡡࡣ࡮ࡨࡨࠬᦅ"), bstack1lll1_opy_ (u"ࠪࡰࡴࡩࡡࡵ࡫ࡲࡲࡘ࡫ࡲࡷ࡫ࡦࡩࡸࡇࡵࡵࡪࡲࡶ࡮ࢀࡥࡥࠩᦆ"),
  bstack1lll1_opy_ (u"ࠫࡦࡻࡴࡰࡃࡦࡧࡪࡶࡴࡂ࡮ࡨࡶࡹࡹࠧᦇ"), bstack1lll1_opy_ (u"ࠬࡧࡵࡵࡱࡇ࡭ࡸࡳࡩࡴࡵࡄࡰࡪࡸࡴࡴࠩᦈ"),
  bstack1lll1_opy_ (u"࠭࡮ࡢࡶ࡬ࡺࡪࡏ࡮ࡴࡶࡵࡹࡲ࡫࡮ࡵࡵࡏ࡭ࡧ࠭ᦉ"),
  bstack1lll1_opy_ (u"ࠧ࡯ࡣࡷ࡭ࡻ࡫ࡗࡦࡤࡗࡥࡵ࠭ᦊ"),
  bstack1lll1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࡊࡰ࡬ࡸ࡮ࡧ࡬ࡖࡴ࡯ࠫᦋ"), bstack1lll1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡃ࡯ࡰࡴࡽࡐࡰࡲࡸࡴࡸ࠭ᦌ"), bstack1lll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࡌ࡫ࡳࡵࡲࡦࡈࡵࡥࡺࡪࡗࡢࡴࡱ࡭ࡳ࡭ࠧᦍ"), bstack1lll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࡓࡵ࡫࡮ࡍ࡫ࡱ࡯ࡸࡏ࡮ࡃࡣࡦ࡯࡬ࡸ࡯ࡶࡰࡧࠫᦎ"),
  bstack1lll1_opy_ (u"ࠬࡱࡥࡦࡲࡎࡩࡾࡉࡨࡢ࡫ࡱࡷࠬᦏ"),
  bstack1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰ࡮ࢀࡡࡣ࡮ࡨࡗࡹࡸࡩ࡯ࡩࡶࡈ࡮ࡸࠧᦐ"),
  bstack1lll1_opy_ (u"ࠧࡱࡴࡲࡧࡪࡹࡳࡂࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᦑ"),
  bstack1lll1_opy_ (u"ࠨ࡫ࡱࡸࡪࡸࡋࡦࡻࡇࡩࡱࡧࡹࠨᦒ"),
  bstack1lll1_opy_ (u"ࠩࡶ࡬ࡴࡽࡉࡐࡕࡏࡳ࡬࠭ᦓ"),
  bstack1lll1_opy_ (u"ࠪࡷࡪࡴࡤࡌࡧࡼࡗࡹࡸࡡࡵࡧࡪࡽࠬᦔ"),
  bstack1lll1_opy_ (u"ࠫࡼ࡫ࡢ࡬࡫ࡷࡖࡪࡹࡰࡰࡰࡶࡩ࡙࡯࡭ࡦࡱࡸࡸࠬᦕ"), bstack1lll1_opy_ (u"ࠬࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵ࡙ࡤ࡭ࡹ࡚ࡩ࡮ࡧࡲࡹࡹ࠭ᦖ"),
  bstack1lll1_opy_ (u"࠭ࡲࡦ࡯ࡲࡸࡪࡊࡥࡣࡷࡪࡔࡷࡵࡸࡺࠩᦗ"),
  bstack1lll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡁࡴࡻࡱࡧࡊࡾࡥࡤࡷࡷࡩࡋࡸ࡯࡮ࡊࡷࡸࡵࡹࠧᦘ"),
  bstack1lll1_opy_ (u"ࠨࡵ࡮࡭ࡵࡒ࡯ࡨࡅࡤࡴࡹࡻࡲࡦࠩᦙ"),
  bstack1lll1_opy_ (u"ࠩࡺࡩࡧࡱࡩࡵࡆࡨࡦࡺ࡭ࡐࡳࡱࡻࡽࡕࡵࡲࡵࠩᦚ"),
  bstack1lll1_opy_ (u"ࠪࡪࡺࡲ࡬ࡄࡱࡱࡸࡪࡾࡴࡍ࡫ࡶࡸࠬᦛ"),
  bstack1lll1_opy_ (u"ࠫࡼࡧࡩࡵࡈࡲࡶࡆࡶࡰࡔࡥࡵ࡭ࡵࡺࠧᦜ"),
  bstack1lll1_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼࡉ࡯࡯ࡰࡨࡧࡹࡘࡥࡵࡴ࡬ࡩࡸ࠭ᦝ"),
  bstack1lll1_opy_ (u"࠭ࡡࡱࡲࡑࡥࡲ࡫ࠧᦞ"),
  bstack1lll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡓࡔࡎࡆࡩࡷࡺࠧᦟ"),
  bstack1lll1_opy_ (u"ࠨࡶࡤࡴ࡜࡯ࡴࡩࡕ࡫ࡳࡷࡺࡐࡳࡧࡶࡷࡉࡻࡲࡢࡶ࡬ࡳࡳ࠭ᦠ"),
  bstack1lll1_opy_ (u"ࠩࡶࡧࡦࡲࡥࡇࡣࡦࡸࡴࡸࠧᦡ"),
  bstack1lll1_opy_ (u"ࠪࡻࡩࡧࡌࡰࡥࡤࡰࡕࡵࡲࡵࠩᦢ"),
  bstack1lll1_opy_ (u"ࠫࡸ࡮࡯ࡸ࡚ࡦࡳࡩ࡫ࡌࡰࡩࠪᦣ"),
  bstack1lll1_opy_ (u"ࠬ࡯࡯ࡴࡋࡱࡷࡹࡧ࡬࡭ࡒࡤࡹࡸ࡫ࠧᦤ"),
  bstack1lll1_opy_ (u"࠭ࡸࡤࡱࡧࡩࡈࡵ࡮ࡧ࡫ࡪࡊ࡮ࡲࡥࠨᦥ"),
  bstack1lll1_opy_ (u"ࠧ࡬ࡧࡼࡧ࡭ࡧࡩ࡯ࡒࡤࡷࡸࡽ࡯ࡳࡦࠪᦦ"),
  bstack1lll1_opy_ (u"ࠨࡷࡶࡩࡕࡸࡥࡣࡷ࡬ࡰࡹ࡝ࡄࡂࠩᦧ"),
  bstack1lll1_opy_ (u"ࠩࡳࡶࡪࡼࡥ࡯ࡶ࡚ࡈࡆࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠪᦨ"),
  bstack1lll1_opy_ (u"ࠪࡻࡪࡨࡄࡳ࡫ࡹࡩࡷࡇࡧࡦࡰࡷ࡙ࡷࡲࠧᦩ"),
  bstack1lll1_opy_ (u"ࠫࡰ࡫ࡹࡤࡪࡤ࡭ࡳࡖࡡࡵࡪࠪᦪ"),
  bstack1lll1_opy_ (u"ࠬࡻࡳࡦࡐࡨࡻ࡜ࡊࡁࠨᦫ"),
  bstack1lll1_opy_ (u"࠭ࡷࡥࡣࡏࡥࡺࡴࡣࡩࡖ࡬ࡱࡪࡵࡵࡵࠩ᦬"), bstack1lll1_opy_ (u"ࠧࡸࡦࡤࡇࡴࡴ࡮ࡦࡥࡷ࡭ࡴࡴࡔࡪ࡯ࡨࡳࡺࡺࠧ᦭"),
  bstack1lll1_opy_ (u"ࠨࡺࡦࡳࡩ࡫ࡏࡳࡩࡌࡨࠬ᦮"), bstack1lll1_opy_ (u"ࠩࡻࡧࡴࡪࡥࡔ࡫ࡪࡲ࡮ࡴࡧࡊࡦࠪ᦯"),
  bstack1lll1_opy_ (u"ࠪࡹࡵࡪࡡࡵࡧࡧ࡛ࡉࡇࡂࡶࡰࡧࡰࡪࡏࡤࠨᦰ"),
  bstack1lll1_opy_ (u"ࠫࡷ࡫ࡳࡦࡶࡒࡲࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡳࡶࡒࡲࡱࡿࠧᦱ"),
  bstack1lll1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩ࡚ࡩ࡮ࡧࡲࡹࡹࡹࠧᦲ"),
  bstack1lll1_opy_ (u"࠭ࡷࡥࡣࡖࡸࡦࡸࡴࡶࡲࡕࡩࡹࡸࡩࡦࡵࠪᦳ"), bstack1lll1_opy_ (u"ࠧࡸࡦࡤࡗࡹࡧࡲࡵࡷࡳࡖࡪࡺࡲࡺࡋࡱࡸࡪࡸࡶࡢ࡮ࠪᦴ"),
  bstack1lll1_opy_ (u"ࠨࡥࡲࡲࡳ࡫ࡣࡵࡊࡤࡶࡩࡽࡡࡳࡧࡎࡩࡾࡨ࡯ࡢࡴࡧࠫᦵ"),
  bstack1lll1_opy_ (u"ࠩࡰࡥࡽ࡚ࡹࡱ࡫ࡱ࡫ࡋࡸࡥࡲࡷࡨࡲࡨࡿࠧᦶ"),
  bstack1lll1_opy_ (u"ࠪࡷ࡮ࡳࡰ࡭ࡧࡌࡷ࡛࡯ࡳࡪࡤ࡯ࡩࡈ࡮ࡥࡤ࡭ࠪᦷ"),
  bstack1lll1_opy_ (u"ࠫࡺࡹࡥࡄࡣࡵࡸ࡭ࡧࡧࡦࡕࡶࡰࠬᦸ"),
  bstack1lll1_opy_ (u"ࠬࡹࡨࡰࡷ࡯ࡨ࡚ࡹࡥࡔ࡫ࡱ࡫ࡱ࡫ࡴࡰࡰࡗࡩࡸࡺࡍࡢࡰࡤ࡫ࡪࡸࠧᦹ"),
  bstack1lll1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡎ࡝ࡄࡑࠩᦺ"),
  bstack1lll1_opy_ (u"ࠧࡢ࡮࡯ࡳࡼ࡚࡯ࡶࡥ࡫ࡍࡩࡋ࡮ࡳࡱ࡯ࡰࠬᦻ"),
  bstack1lll1_opy_ (u"ࠨ࡫ࡪࡲࡴࡸࡥࡉ࡫ࡧࡨࡪࡴࡁࡱ࡫ࡓࡳࡱ࡯ࡣࡺࡇࡵࡶࡴࡸࠧᦼ"),
  bstack1lll1_opy_ (u"ࠩࡰࡳࡨࡱࡌࡰࡥࡤࡸ࡮ࡵ࡮ࡂࡲࡳࠫᦽ"),
  bstack1lll1_opy_ (u"ࠪࡰࡴ࡭ࡣࡢࡶࡉࡳࡷࡳࡡࡵࠩᦾ"), bstack1lll1_opy_ (u"ࠫࡱࡵࡧࡤࡣࡷࡊ࡮ࡲࡴࡦࡴࡖࡴࡪࡩࡳࠨᦿ"),
  bstack1lll1_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡈࡪࡲࡡࡺࡃࡧࡦࠬᧀ"),
  bstack1lll1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡉࡥࡎࡲࡧࡦࡺ࡯ࡳࡃࡸࡸࡴࡩ࡯࡮ࡲ࡯ࡩࡹ࡯࡯࡯ࠩᧁ")
]
bstack11l1l1llll_opy_ = bstack1lll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠲ࡩ࡬ࡰࡷࡧ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡵࡱ࡮ࡲࡥࡩ࠭ᧂ")
bstack1ll111ll1l_opy_ = [bstack1lll1_opy_ (u"ࠨ࠰ࡤࡴࡰ࠭ᧃ"), bstack1lll1_opy_ (u"ࠩ࠱ࡥࡦࡨࠧᧄ"), bstack1lll1_opy_ (u"ࠪ࠲࡮ࡶࡡࠨᧅ")]
bstack1ll11lllll_opy_ = [bstack1lll1_opy_ (u"ࠫ࡮ࡪࠧᧆ"), bstack1lll1_opy_ (u"ࠬࡶࡡࡵࡪࠪᧇ"), bstack1lll1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡥࡩࡥࠩᧈ"), bstack1lll1_opy_ (u"ࠧࡴࡪࡤࡶࡪࡧࡢ࡭ࡧࡢ࡭ࡩ࠭ᧉ")]
bstack1llll1l1_opy_ = {
  bstack1lll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ᧊"): bstack1lll1_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᧋"),
  bstack1lll1_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫ᧌"): bstack1lll1_opy_ (u"ࠫࡲࡵࡺ࠻ࡨ࡬ࡶࡪ࡬࡯ࡹࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᧍"),
  bstack1lll1_opy_ (u"ࠬ࡫ࡤࡨࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ᧎"): bstack1lll1_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᧏"),
  bstack1lll1_opy_ (u"ࠧࡪࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ᧐"): bstack1lll1_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᧑"),
  bstack1lll1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᧒"): bstack1lll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫࠱ࡳࡵࡺࡩࡰࡰࡶࠫ᧓")
}
bstack1ll1ll1lll_opy_ = [
  bstack1lll1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᧔"),
  bstack1lll1_opy_ (u"ࠬࡳ࡯ࡻ࠼ࡩ࡭ࡷ࡫ࡦࡰࡺࡒࡴࡹ࡯࡯࡯ࡵࠪ᧕"),
  bstack1lll1_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᧖"),
  bstack1lll1_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᧗"),
  bstack1lll1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ᧘"),
]
bstack1lll11l1ll_opy_ = bstack11lllll11_opy_ + bstack11l1ll11lll_opy_ + bstack11ll1lllll_opy_
bstack1llll1l11_opy_ = [
  bstack1lll1_opy_ (u"ࠩࡡࡰࡴࡩࡡ࡭ࡪࡲࡷࡹࠪࠧ᧙"),
  bstack1lll1_opy_ (u"ࠪࡢࡧࡹ࠭࡭ࡱࡦࡥࡱ࠴ࡣࡰ࡯ࠧࠫ᧚"),
  bstack1lll1_opy_ (u"ࠫࡣ࠷࠲࠸࠰ࠪ᧛"),
  bstack1lll1_opy_ (u"ࠬࡤ࠱࠱࠰ࠪ᧜"),
  bstack1lll1_opy_ (u"࠭࡞࠲࠹࠵࠲࠶ࡡ࠶࠮࠻ࡠ࠲ࠬ᧝"),
  bstack1lll1_opy_ (u"ࠧ࡟࠳࠺࠶࠳࠸࡛࠱࠯࠼ࡡ࠳࠭᧞"),
  bstack1lll1_opy_ (u"ࠨࡠ࠴࠻࠷࠴࠳࡜࠲࠰࠵ࡢ࠴ࠧ᧟"),
  bstack1lll1_opy_ (u"ࠩࡡ࠵࠾࠸࠮࠲࠸࠻࠲ࠬ᧠")
]
bstack11ll111ll11_opy_ = bstack1lll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡶࡩ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫ᧡")
bstack1l1ll11lll_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠰ࡸ࠴࠳ࡪࡼࡥ࡯ࡶࠪ᧢")
bstack1l11llllll_opy_ = [ bstack1lll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ᧣") ]
bstack11lll1l11_opy_ = [ bstack1lll1_opy_ (u"࠭ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ᧤") ]
bstack1ll1l11lll_opy_ = [bstack1lll1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ᧥")]
bstack1l111ll1l1_opy_ = [ bstack1lll1_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ᧦") ]
bstack11111l11_opy_ = bstack1lll1_opy_ (u"ࠩࡖࡈࡐ࡙ࡥࡵࡷࡳࠫ᧧")
bstack1ll111lll1_opy_ = bstack1lll1_opy_ (u"ࠪࡗࡉࡑࡔࡦࡵࡷࡅࡹࡺࡥ࡮ࡲࡷࡩࡩ࠭᧨")
bstack1l1111l11_opy_ = bstack1lll1_opy_ (u"ࠫࡘࡊࡋࡕࡧࡶࡸࡘࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬ࠨ᧩")
bstack1lll1l1ll1_opy_ = bstack1lll1_opy_ (u"ࠬ࠺࠮࠱࠰࠳ࠫ᧪")
bstack1l1111l1l_opy_ = [
  bstack1lll1_opy_ (u"࠭ࡅࡓࡔࡢࡊࡆࡏࡌࡆࡆࠪ᧫"),
  bstack1lll1_opy_ (u"ࠧࡆࡔࡕࡣ࡙ࡏࡍࡆࡆࡢࡓ࡚࡚ࠧ᧬"),
  bstack1lll1_opy_ (u"ࠨࡇࡕࡖࡤࡈࡌࡐࡅࡎࡉࡉࡥࡂ࡚ࡡࡆࡐࡎࡋࡎࡕࠩ᧭"),
  bstack1lll1_opy_ (u"ࠩࡈࡖࡗࡥࡎࡆࡖ࡚ࡓࡗࡑ࡟ࡄࡊࡄࡒࡌࡋࡄࠨ᧮"),
  bstack1lll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡔࡑࡆࡏࡊ࡚࡟ࡏࡑࡗࡣࡈࡕࡎࡏࡇࡆࡘࡊࡊࠧ᧯"),
  bstack1lll1_opy_ (u"ࠫࡊࡘࡒࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡉࡌࡐࡕࡈࡈࠬ᧰"),
  bstack1lll1_opy_ (u"ࠬࡋࡒࡓࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡒࡆࡕࡈࡘࠬ᧱"),
  bstack1lll1_opy_ (u"࠭ࡅࡓࡔࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡓࡇࡉ࡙ࡘࡋࡄࠨ᧲"),
  bstack1lll1_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡃࡅࡓࡗ࡚ࡅࡅࠩ᧳"),
  bstack1lll1_opy_ (u"ࠨࡇࡕࡖࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩ᧴"),
  bstack1lll1_opy_ (u"ࠩࡈࡖࡗࡥࡎࡂࡏࡈࡣࡓࡕࡔࡠࡔࡈࡗࡔࡒࡖࡆࡆࠪ᧵"),
  bstack1lll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡂࡆࡇࡖࡊ࡙ࡓࡠࡋࡑ࡚ࡆࡒࡉࡅࠩ᧶"),
  bstack1lll1_opy_ (u"ࠫࡊࡘࡒࡠࡃࡇࡈࡗࡋࡓࡔࡡࡘࡒࡗࡋࡁࡄࡊࡄࡆࡑࡋࠧ᧷"),
  bstack1lll1_opy_ (u"ࠬࡋࡒࡓࡡࡗ࡙ࡓࡔࡅࡍࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡆࡂࡋࡏࡉࡉ࠭᧸"),
  bstack1lll1_opy_ (u"࠭ࡅࡓࡔࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡕࡋࡐࡉࡉࡥࡏࡖࡖࠪ᧹"),
  bstack1lll1_opy_ (u"ࠧࡆࡔࡕࡣࡘࡕࡃࡌࡕࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡇࡃࡌࡐࡊࡊࠧ᧺"),
  bstack1lll1_opy_ (u"ࠨࡇࡕࡖࡤ࡙ࡏࡄࡍࡖࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡊࡒࡗ࡙ࡥࡕࡏࡔࡈࡅࡈࡎࡁࡃࡎࡈࠫ᧻"),
  bstack1lll1_opy_ (u"ࠩࡈࡖࡗࡥࡐࡓࡑ࡛࡝ࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩ᧼"),
  bstack1lll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡏࡃࡐࡉࡤࡔࡏࡕࡡࡕࡉࡘࡕࡌࡗࡇࡇࠫ᧽"),
  bstack1lll1_opy_ (u"ࠫࡊࡘࡒࡠࡐࡄࡑࡊࡥࡒࡆࡕࡒࡐ࡚࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪ᧾"),
  bstack1lll1_opy_ (u"ࠬࡋࡒࡓࡡࡐࡅࡓࡊࡁࡕࡑࡕ࡝ࡤࡖࡒࡐ࡚࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣࡋࡇࡉࡍࡇࡇࠫ᧿"),
]
bstack1l1l111ll1_opy_ = bstack1lll1_opy_ (u"࠭࠮࠰ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠭ࡢࡴࡷ࡭࡫ࡧࡣࡵࡵ࠲ࠫᨀ")
bstack11lll11111_opy_ = os.path.join(os.path.expanduser(bstack1lll1_opy_ (u"ࠧࡿࠩᨁ")), bstack1lll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᨂ"), bstack1lll1_opy_ (u"ࠩ࠱ࡦࡸࡺࡡࡤ࡭࠰ࡧࡴࡴࡦࡪࡩ࠱࡮ࡸࡵ࡮ࠨᨃ"))
bstack11ll1ll11l1_opy_ = bstack1lll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡢࡲ࡬ࠫᨄ")
bstack11l1l1l1l11_opy_ = [ bstack1lll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᨅ"), bstack1lll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫᨆ"), bstack1lll1_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬᨇ"), bstack1lll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧᨈ")]
bstack11llll1l11_opy_ = [ bstack1lll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨᨉ"), bstack1lll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨᨊ"), bstack1lll1_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩᨋ"), bstack1lll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫᨌ") ]
bstack11l11llll_opy_ = [ bstack1lll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫᨍ") ]
bstack11l1l1lll11_opy_ = [ bstack1lll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ᨎ") ]
bstack11l111lll_opy_ = 360
bstack11ll111l1l1_opy_ = bstack1lll1_opy_ (u"ࠢࡢࡲࡳ࠱ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠢᨏ")
bstack11l1l1ll1ll_opy_ = bstack1lll1_opy_ (u"ࠣࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡥࡵ࡯࠯ࡷ࠳࠲࡭ࡸࡹࡵࡦࡵࠥᨐ")
bstack11l1l1lllll_opy_ = bstack1lll1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶࡨ࠳ࡦࡶࡩ࠰ࡸ࠴࠳࡮ࡹࡳࡶࡧࡶ࠱ࡸࡻ࡭࡮ࡣࡵࡽࠧᨑ")
bstack11ll11l1l1l_opy_ = bstack1lll1_opy_ (u"ࠥࡅࡵࡶࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡹ࡫ࡳࡵࡵࠣࡥࡷ࡫ࠠࡴࡷࡳࡴࡴࡸࡴࡦࡦࠣࡳࡳࠦࡏࡔࠢࡹࡩࡷࡹࡩࡰࡰࠣࠩࡸࠦࡡ࡯ࡦࠣࡥࡧࡵࡶࡦࠢࡩࡳࡷࠦࡁ࡯ࡦࡵࡳ࡮ࡪࠠࡥࡧࡹ࡭ࡨ࡫ࡳ࠯ࠤᨒ")
bstack11ll11l1ll1_opy_ = bstack1lll1_opy_ (u"ࠦ࠶࠷࠮࠱ࠤᨓ")
bstack111l11lll1_opy_ = {
  bstack1lll1_opy_ (u"ࠬࡖࡁࡔࡕࠪᨔ"): bstack1lll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ᨕ"),
  bstack1lll1_opy_ (u"ࠧࡇࡃࡌࡐࠬᨖ"): bstack1lll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᨗ"),
  bstack1lll1_opy_ (u"ࠩࡖࡏࡎࡖᨘࠧ"): bstack1lll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫᨙ")
}
bstack11111111l_opy_ = [
  bstack1lll1_opy_ (u"ࠦ࡬࡫ࡴࠣᨚ"),
  bstack1lll1_opy_ (u"ࠧ࡭࡯ࡃࡣࡦ࡯ࠧᨛ"),
  bstack1lll1_opy_ (u"ࠨࡧࡰࡈࡲࡶࡼࡧࡲࡥࠤ᨜"),
  bstack1lll1_opy_ (u"ࠢࡳࡧࡩࡶࡪࡹࡨࠣ᨝"),
  bstack1lll1_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࡅ࡭ࡧࡰࡩࡳࡺࠢ᨞"),
  bstack1lll1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨ᨟"),
  bstack1lll1_opy_ (u"ࠥࡷࡺࡨ࡭ࡪࡶࡈࡰࡪࡳࡥ࡯ࡶࠥᨠ"),
  bstack1lll1_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡆ࡮ࡨࡱࡪࡴࡴࠣᨡ"),
  bstack1lll1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࡔࡰࡃࡦࡸ࡮ࡼࡥࡆ࡮ࡨࡱࡪࡴࡴࠣᨢ"),
  bstack1lll1_opy_ (u"ࠨࡣ࡭ࡧࡤࡶࡊࡲࡥ࡮ࡧࡱࡸࠧᨣ"),
  bstack1lll1_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࡳࠣᨤ"),
  bstack1lll1_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࡕࡦࡶ࡮ࡶࡴࠣᨥ"),
  bstack1lll1_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࡄࡷࡾࡴࡣࡔࡥࡵ࡭ࡵࡺࠢᨦ"),
  bstack1lll1_opy_ (u"ࠥࡧࡱࡵࡳࡦࠤᨧ"),
  bstack1lll1_opy_ (u"ࠦࡶࡻࡩࡵࠤᨨ"),
  bstack1lll1_opy_ (u"ࠧࡶࡥࡳࡨࡲࡶࡲ࡚࡯ࡶࡥ࡫ࡅࡨࡺࡩࡰࡰࠥᨩ"),
  bstack1lll1_opy_ (u"ࠨࡰࡦࡴࡩࡳࡷࡳࡍࡶ࡮ࡷ࡭࡙ࡵࡵࡤࡪࠥᨪ"),
  bstack1lll1_opy_ (u"ࠢࡴࡪࡤ࡯ࡪࠨᨫ"),
  bstack1lll1_opy_ (u"ࠣࡥ࡯ࡳࡸ࡫ࡁࡱࡲࠥᨬ")
]
bstack11l1ll1l1l1_opy_ = [
  bstack1lll1_opy_ (u"ࠤࡦࡰ࡮ࡩ࡫ࠣᨭ"),
  bstack1lll1_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢᨮ"),
  bstack1lll1_opy_ (u"ࠦࡦࡻࡴࡰࠤᨯ"),
  bstack1lll1_opy_ (u"ࠧࡳࡡ࡯ࡷࡤࡰࠧᨰ"),
  bstack1lll1_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣᨱ")
]
bstack11ll1ll1l_opy_ = {
  bstack1lll1_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࠨᨲ"): [bstack1lll1_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࡅ࡭ࡧࡰࡩࡳࡺࠢᨳ")],
  bstack1lll1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨᨴ"): [bstack1lll1_opy_ (u"ࠥࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠢᨵ")],
  bstack1lll1_opy_ (u"ࠦࡦࡻࡴࡰࠤᨶ"): [bstack1lll1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࡔࡰࡇ࡯ࡩࡲ࡫࡮ࡵࠤᨷ"), bstack1lll1_opy_ (u"ࠨࡳࡦࡰࡧࡏࡪࡿࡳࡕࡱࡄࡧࡹ࡯ࡶࡦࡇ࡯ࡩࡲ࡫࡮ࡵࠤᨸ"), bstack1lll1_opy_ (u"ࠢࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠦᨹ"), bstack1lll1_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࡅ࡭ࡧࡰࡩࡳࡺࠢᨺ")],
  bstack1lll1_opy_ (u"ࠤࡰࡥࡳࡻࡡ࡭ࠤᨻ"): [bstack1lll1_opy_ (u"ࠥࡱࡦࡴࡵࡢ࡮ࠥᨼ")],
  bstack1lll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡥࡤࡷࡪࠨᨽ"): [bstack1lll1_opy_ (u"ࠧࡺࡥࡴࡶࡦࡥࡸ࡫ࠢᨾ")],
}
bstack11l1ll1l1ll_opy_ = {
  bstack1lll1_opy_ (u"ࠨࡣ࡭࡫ࡦ࡯ࡊࡲࡥ࡮ࡧࡱࡸࠧᨿ"): bstack1lll1_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࠨᩀ"),
  bstack1lll1_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧᩁ"): bstack1lll1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨᩂ"),
  bstack1lll1_opy_ (u"ࠥࡷࡪࡴࡤࡌࡧࡼࡷ࡙ࡵࡅ࡭ࡧࡰࡩࡳࡺࠢᩃ"): bstack1lll1_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸࠨᩄ"),
  bstack1lll1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࡔࡰࡃࡦࡸ࡮ࡼࡥࡆ࡮ࡨࡱࡪࡴࡴࠣᩅ"): bstack1lll1_opy_ (u"ࠨࡳࡦࡰࡧࡏࡪࡿࡳࠣᩆ"),
  bstack1lll1_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤᩇ"): bstack1lll1_opy_ (u"ࠣࡶࡨࡷࡹࡩࡡࡴࡧࠥᩈ")
}
bstack1111ll1ll1_opy_ = {
  bstack1lll1_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡄࡐࡑ࠭ᩉ"): bstack1lll1_opy_ (u"ࠪࡗࡺ࡯ࡴࡦࠢࡖࡩࡹࡻࡰࠨᩊ"),
  bstack1lll1_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡅࡑࡒࠧᩋ"): bstack1lll1_opy_ (u"࡙ࠬࡵࡪࡶࡨࠤ࡙࡫ࡡࡳࡦࡲࡻࡳ࠭ᩌ"),
  bstack1lll1_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫᩍ"): bstack1lll1_opy_ (u"ࠧࡕࡧࡶࡸ࡙ࠥࡥࡵࡷࡳࠫᩎ"),
  bstack1lll1_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡆࡃࡆࡌࠬᩏ"): bstack1lll1_opy_ (u"ࠩࡗࡩࡸࡺࠠࡕࡧࡤࡶࡩࡵࡷ࡯ࠩᩐ")
}
bstack11l1ll1llll_opy_ = 65536
bstack11l1l1ll11l_opy_ = bstack1lll1_opy_ (u"ࠪ࠲࠳࠴࡛ࡕࡔࡘࡒࡈࡇࡔࡆࡆࡠࠫᩑ")
bstack11l1lll11l1_opy_ = [
      bstack1lll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᩒ"), bstack1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᩓ"), bstack1lll1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩᩔ"), bstack1lll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫᩕ"), bstack1lll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡗࡣࡵ࡭ࡦࡨ࡬ࡦࡵࠪᩖ"),
      bstack1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬᩗ"), bstack1lll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡤࡷࡸ࠭ᩘ"), bstack1lll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡖࡵࡨࡶࠬᩙ"), bstack1lll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡔࡷࡵࡸࡺࡒࡤࡷࡸ࠭ᩚ"),
      bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᩛ"), bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᩜ"), bstack1lll1_opy_ (u"ࠨࡣࡸࡸ࡭࡚࡯࡬ࡧࡱࠫᩝ")
    ]
bstack11l1l1l1lll_opy_= {
  bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ᩞ"): bstack1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ᩟"),
  bstack1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨ᩠"): bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩᩡ"),
  bstack1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬᩢ"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫᩣ"),
  bstack1lll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᩤ"): bstack1lll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩᩥ"),
  bstack1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᩦ"): bstack1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᩧ"),
  bstack1lll1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧᩨ"): bstack1lll1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨᩩ"),
  bstack1lll1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪᩪ"): bstack1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫᩫ"),
  bstack1lll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭ᩬ"): bstack1lll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧᩭ"),
  bstack1lll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧᩮ"): bstack1lll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᩯ"),
  bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠫᩰ"): bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬᩱ"),
  bstack1lll1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬᩲ"): bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ᩳ"),
  bstack1lll1_opy_ (u"ࠪࡸࡪࡹࡴࡓࡧࡳࡳࡷࡺࡩ࡯ࡩࠪᩴ"): bstack1lll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡔࡨࡴࡴࡸࡴࡪࡰࡪࠫ᩵"),
  bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᩶"): bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ᩷"),
  bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࡏࡱࡶ࡬ࡳࡳࡹࠧ᩸"): bstack1lll1_opy_ (u"ࠨࡶࡨࡷࡹࡘࡥࡱࡱࡵࡸ࡮ࡴࡧࡐࡲࡷ࡭ࡴࡴࡳࠨ᩹"),
  bstack1lll1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠫ᩺"): bstack1lll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯࡙ࡥࡷ࡯ࡡࡣ࡮ࡨࡷࠬ᩻"),
  bstack1lll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᩼"): bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ᩽"),
  bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᩾"): bstack1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯᩿ࠩ"),
  bstack1lll1_opy_ (u"ࠨࡴࡨࡶࡺࡴࡔࡦࡵࡷࡷࠬ᪀"): bstack1lll1_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡕࡧࡶࡸࡸ࠭᪁"),
  bstack1lll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ᪂"): bstack1lll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪ᪃"),
  bstack1lll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡓࡵࡺࡩࡰࡰࡶࠫ᪄"): bstack1lll1_opy_ (u"࠭ࡰࡦࡴࡦࡽࡔࡶࡴࡪࡱࡱࡷࠬ᪅"),
  bstack1lll1_opy_ (u"ࠧࡱࡧࡵࡧࡾࡉࡡࡱࡶࡸࡶࡪࡓ࡯ࡥࡧࠪ᪆"): bstack1lll1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡃࡢࡲࡷࡹࡷ࡫ࡍࡰࡦࡨࠫ᪇"),
  bstack1lll1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫ᪈"): bstack1lll1_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡺࡺ࡯ࡄࡣࡳࡸࡺࡸࡥࡍࡱࡪࡷࠬ᪉"),
  bstack1lll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ᪊"): bstack1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ᪋"),
  bstack1lll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭᪌"): bstack1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧ᪍"),
  bstack1lll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ᪎"): bstack1lll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭᪏"),
  bstack1lll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᪐"): bstack1lll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ᪑"),
  bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᪒"): bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪ᪓"),
  bstack1lll1_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠧ᪔"): bstack1lll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠨ᪕")
}
bstack11l1lll11ll_opy_ = [bstack1lll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ᪖"), bstack1lll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ᪗")]
bstack1l1l11l111_opy_ = (bstack1lll1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦ᪘"),)
bstack11l1l1l1l1l_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠱ࡹ࠵࠴ࡻࡰࡥࡣࡷࡩࡤࡩ࡬ࡪࠩ᪙")
bstack11l1111l_opy_ = bstack1lll1_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࡢࡲ࡬࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡢࡷࡷࡳࡲࡧࡴࡦ࠯ࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠵ࡶ࠲࠱ࡪࡶ࡮ࡪࡳ࠰ࠤ᪚")
bstack11l1111lll_opy_ = bstack1lll1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࡩࡵ࡭ࡩ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡥࡸ࡮ࡢࡰࡣࡵࡨ࠴ࡨࡵࡪ࡮ࡧࡷ࠴ࠨ᪛")
bstack1lll1ll11_opy_ = bstack1lll1_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡴ࡮࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠱ࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥ࠰ࡸ࠴࠳ࡧࡻࡩ࡭ࡦࡶ࠲࡯ࡹ࡯࡯ࠤ᪜")
class EVENTS(Enum):
  bstack11l1ll11l1l_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀ࡯࠲࠳ࡼ࠾ࡵࡸࡩ࡯ࡶ࠰ࡦࡺ࡯࡬ࡥ࡮࡬ࡲࡰ࠭᪝")
  bstack11l1l1l11_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡤ࡮ࡨࡥࡳࡻࡰࠨ᪞") # final bstack11l1lll1111_opy_
  bstack11l1ll1ll11_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡵࡨࡲࡩࡲ࡯ࡨࡵࠪ᪟")
  bstack1l11l1llll_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪࡀࡰࡳ࡫ࡱࡸ࠲ࡨࡵࡪ࡮ࡧࡰ࡮ࡴ࡫ࠨ᪠") #shift post bstack11l1ll1lll1_opy_
  bstack1111l1l11_opy_ = bstack1lll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠿ࡶࡲࡪࡰࡷ࠱ࡧࡻࡩ࡭ࡦ࡯࡭ࡳࡱࠧ᪡") #shift post bstack11l1ll1lll1_opy_
  bstack11l1ll111ll_opy_ = bstack1lll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡹ࡫ࡳࡵࡪࡸࡦࠬ᪢") #shift
  bstack11l1ll1l11l_opy_ = bstack1lll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡶࡥࡳࡥࡼ࠾ࡩࡵࡷ࡯࡮ࡲࡥࡩ࠭᪣") #shift
  bstack1l1lll1l11_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧ࠽࡬ࡺࡨ࠭࡮ࡣࡱࡥ࡬࡫࡭ࡦࡰࡷࠫ᪤")
  bstack1ll111lll1l_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡢ࠳࠴ࡽ࠿ࡹࡡࡷࡧ࠰ࡶࡪࡹࡵ࡭ࡶࡶࠫ᪥")
  bstack11lllll1l_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡣ࠴࠵ࡾࡀࡤࡳ࡫ࡹࡩࡷ࠳ࡰࡦࡴࡩࡳࡷࡳࡳࡤࡣࡱࠫ᪦")
  bstack1ll1l1l1ll_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠾ࡱࡵࡣࡢ࡮ࠪᪧ") #shift
  bstack1llll1l1ll_opy_ = bstack1lll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦ࠼ࡤࡴࡵ࠳ࡵࡱ࡮ࡲࡥࡩ࠭᪨") #shift
  bstack1l11111l11_opy_ = bstack1lll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸࡪࡀࡣࡪ࠯ࡤࡶࡹ࡯ࡦࡢࡥࡷࡷࠬ᪩")
  bstack1lll1111l_opy_ = bstack1lll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧ࠱࠲ࡻ࠽࡫ࡪࡺ࠭ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࠭ࡳࡧࡶࡹࡱࡺࡳ࠮ࡵࡸࡱࡲࡧࡲࡺࠩ᪪") #shift
  bstack1ll1l1111l_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀࡡ࠲࠳ࡼ࠾࡬࡫ࡴ࠮ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹ࠮ࡴࡨࡷࡺࡲࡴࡴࠩ᪫") #shift
  bstack11l1llll111_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡱࡧࡵࡧࡾ࠭᪬") #shift
  bstack1l1l11ll111_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡲࡨࡶࡨࡿ࠺ࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠫ᪭")
  bstack1111111l1_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠾ࡸ࡫ࡳࡴ࡫ࡲࡲ࠲ࡹࡴࡢࡶࡸࡷࠬ᪮") #shift
  bstack1lll1ll11l_opy_ = bstack1lll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠿࡮ࡵࡣ࠯ࡰࡥࡳࡧࡧࡦ࡯ࡨࡲࡹ࠭᪯")
  bstack11l1lll1ll1_opy_ = bstack1lll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡵࡸ࡯ࡹࡻ࠰ࡷࡪࡺࡵࡱࠩ᪰") #shift
  bstack1l1l1l1l11_opy_ = bstack1lll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡹࡥࡵࡷࡳࠫ᪱")
  bstack11l1ll11l11_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀࡰࡦࡴࡦࡽ࠿ࡹ࡮ࡢࡲࡶ࡬ࡴࡺࠧ᪲") # not bstack11l1llll11l_opy_ in python
  bstack11l1111l1_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡥࡴ࡬ࡺࡪࡸ࠺ࡲࡷ࡬ࡸࠬ᪳") # used in bstack11l1lll1lll_opy_
  bstack1ll11llll_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡦࡵ࡭ࡻ࡫ࡲ࠻ࡩࡨࡸࠬ᪴") # used in bstack11l1lll1lll_opy_
  bstack111l1l11_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠼࡫ࡳࡴࡱ᪵ࠧ")
  bstack1ll1llll_opy_ = bstack1lll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠿ࡹࡥࡴࡵ࡬ࡳࡳ࠳࡮ࡢ࡯ࡨ᪶ࠫ")
  bstack11l1ll1l11_opy_ = bstack1lll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸࡪࡀࡳࡦࡵࡶ࡭ࡴࡴ࠭ࡢࡰࡱࡳࡹࡧࡴࡪࡱࡱ᪷ࠫ") #
  bstack1l1111l1_opy_ = bstack1lll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡵ࠱࠲ࡻ࠽ࡨࡷ࡯ࡶࡦࡴ࠰ࡸࡦࡱࡥࡔࡥࡵࡩࡪࡴࡓࡩࡱࡷ᪸ࠫ")
  bstack1l11l111l1_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀࡰࡦࡴࡦࡽ࠿ࡧࡵࡵࡱ࠰ࡧࡦࡶࡴࡶࡴࡨ᪹ࠫ")
  bstack1lllll11l1_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡱࡴࡨ࠱ࡹ࡫ࡳࡵ᪺ࠩ")
  bstack1lll111ll_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡲࡲࡷࡹ࠳ࡴࡦࡵࡷࠫ᪻")
  bstack11llll1ll_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡧࡶ࡮ࡼࡥࡳ࠼ࡳࡶࡪ࠳ࡩ࡯࡫ࡷ࡭ࡦࡲࡩࡻࡣࡷ࡭ࡴࡴࠧ᪼") #shift
  bstack1ll1llllll_opy_ = bstack1lll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡨࡷ࡯ࡶࡦࡴ࠽ࡴࡴࡹࡴ࠮࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡥࡹ࡯࡯࡯᪽ࠩ") #shift
  bstack11l1ll111l1_opy_ = bstack1lll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࠯ࡦࡥࡵࡺࡵࡳࡧࠪ᪾")
  bstack11l1lll1l11_opy_ = bstack1lll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱࡰࡥࡹ࡫࠺ࡪࡦ࡯ࡩ࠲ࡺࡩ࡮ࡧࡲࡹࡹᪿ࠭")
  bstack1llll11l1ll_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀࡣ࡭࡫࠽ࡷࡹࡧࡲࡵᫀࠩ")
  bstack11l1ll11111_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡤ࡮࡬࠾ࡩࡵࡷ࡯࡮ࡲࡥࡩ࠭᫁")
  bstack11l1l1llll1_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡥ࡯࡭࠿ࡩࡨࡦࡥ࡮࠱ࡺࡶࡤࡢࡶࡨࠫ᫂")
  bstack1lll111l111_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡦࡰ࡮ࡀ࡯࡯࠯ࡥࡳࡴࡺࡳࡵࡴࡤࡴ᫃ࠬ")
  bstack1lll11l1l11_opy_ = bstack1lll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡧࡱ࡯࠺ࡰࡰ࠰ࡧࡴࡴ࡮ࡦࡥࡷ᫄ࠫ")
  bstack1lll1lll1ll_opy_ = bstack1lll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡨࡲࡩ࠻ࡱࡱ࠱ࡸࡺ࡯ࡱࠩ᫅")
  bstack1ll1lllll11_opy_ = bstack1lll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡹࡴࡢࡴࡷࡆ࡮ࡴࡓࡦࡵࡶ࡭ࡴࡴࠧ᫆")
  bstack1ll1lll111l_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀࡣࡰࡰࡱࡩࡨࡺࡂࡪࡰࡖࡩࡸࡹࡩࡰࡰࠪ᫇")
  bstack11l1lll1l1l_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡥࡴ࡬ࡺࡪࡸࡉ࡯࡫ࡷࠫ᫈")
  bstack11l1l1l11l1_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡨ࡬ࡲࡩࡔࡥࡢࡴࡨࡷࡹࡎࡵࡣࠩ᫉")
  bstack1l11l1ll1l1_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡊࡰ࡬ࡸ᫊ࠬ")
  bstack1l11ll1ll1l_opy_ = bstack1lll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࡕࡷࡥࡷࡺࠧ᫋")
  bstack1ll11l1ll11_opy_ = bstack1lll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡇࡴࡴࡦࡪࡩࠪᫌ")
  bstack11l1ll1ll1l_opy_ = bstack1lll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࡈࡵ࡮ࡧ࡫ࡪࠫᫍ")
  bstack1l1lllll1ll_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀࡡࡪࡕࡨࡰ࡫ࡎࡥࡢ࡮ࡖࡸࡪࡶࠧᫎ")
  bstack1l1lllll111_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡩࡱ࠺ࡢ࡫ࡖࡩࡱ࡬ࡈࡦࡣ࡯ࡋࡪࡺࡒࡦࡵࡸࡰࡹ࠭᫏")
  bstack1l1l1ll11ll_opy_ = bstack1lll1_opy_ (u"ࠫࡸࡪ࡫࠻ࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡆࡸࡨࡲࡹ࠭᫐")
  bstack1l1lll11lll_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠼ࡷࡩࡸࡺࡓࡦࡵࡶ࡭ࡴࡴࡅࡷࡧࡱࡸࠬ᫑")
  bstack1l1ll1l11ll_opy_ = bstack1lll1_opy_ (u"࠭ࡳࡥ࡭࠽ࡧࡱ࡯࠺࡭ࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࡉࡻ࡫࡮ࡵࠩ᫒")
  bstack11l1lll111l_opy_ = bstack1lll1_opy_ (u"ࠧࡴࡦ࡮࠾ࡨࡲࡩ࠻ࡧࡱࡵࡺ࡫ࡵࡦࡖࡨࡷࡹࡋࡶࡦࡰࡷࠫ᫓")
  bstack1l11l1lll1l_opy_ = bstack1lll1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡗࡹࡵࡰࠨ᫔")
  bstack1lll1lll111_opy_ = bstack1lll1_opy_ (u"ࠩࡶࡨࡰࡀ࡯࡯ࡕࡷࡳࡵ࠭᫕")
class STAGE(Enum):
  bstack1l111l111_opy_ = bstack1lll1_opy_ (u"ࠪࡷࡹࡧࡲࡵࠩ᫖")
  END = bstack1lll1_opy_ (u"ࠫࡪࡴࡤࠨ᫗")
  bstack11ll11ll1l_opy_ = bstack1lll1_opy_ (u"ࠬࡹࡩ࡯ࡩ࡯ࡩࠬ᫘")
bstack11lll1l11l_opy_ = {
  bstack1lll1_opy_ (u"࠭ࡐ࡚ࡖࡈࡗ࡙࠭᫙"): bstack1lll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ᫚"),
  bstack1lll1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔ࠮ࡄࡇࡈࠬ᫛"): bstack1lll1_opy_ (u"ࠩࡓࡽࡹ࡫ࡳࡵ࠯ࡦࡹࡨࡻ࡭ࡣࡧࡵࠫ᫜")
}
PLAYWRIGHT_HUB_URL = bstack1lll1_opy_ (u"ࠥࡻࡸࡹ࠺࠰࠱ࡦࡨࡵ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡅࡣࡢࡲࡶࡁࠧ᫝")
bstack1ll111llll1_opy_ = 98
bstack1ll1111ll11_opy_ = 100
bstack111111l1l1_opy_ = {
  bstack1lll1_opy_ (u"ࠫࡷ࡫ࡲࡶࡰࠪ᫞"): bstack1lll1_opy_ (u"ࠬ࠳࠭ࡳࡧࡵࡹࡳࡹࠧ᫟"),
  bstack1lll1_opy_ (u"࠭ࡤࡦ࡮ࡤࡽࠬ᫠"): bstack1lll1_opy_ (u"ࠧ࠮࠯ࡵࡩࡷࡻ࡮ࡴ࠯ࡧࡩࡱࡧࡹࠨ᫡"),
  bstack1lll1_opy_ (u"ࠨࡴࡨࡶࡺࡴ࠭ࡥࡧ࡯ࡥࡾ࠭᫢"): 0
}
bstack11l1ll1l111_opy_ = bstack1lll1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡧࡴࡲ࡬ࡦࡥࡷࡳࡷ࠳࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠤ᫣")
bstack11l1l1ll1l1_opy_ = bstack1lll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡺࡶ࡬ࡰࡣࡧ࠱ࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠢ᫤")
bstack1l1lll111_opy_ = bstack1lll1_opy_ (u"࡙ࠦࡋࡓࡕࠢࡕࡉࡕࡕࡒࡕࡋࡑࡋࠥࡇࡎࡅࠢࡄࡒࡆࡒ࡙ࡕࡋࡆࡗࠧ᫥")