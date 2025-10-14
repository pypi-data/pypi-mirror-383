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
logger = logging.getLogger(__name__)
class BrowserStackSdk:
    def get_current_platform():
        bstack1lll1l11ll_opy_ = {}
        bstack111lll1l11_opy_ = os.environ.get(bstack1lll1_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨ༑"), bstack1lll1_opy_ (u"ࠨࠩ༒"))
        if not bstack111lll1l11_opy_:
            return bstack1lll1l11ll_opy_
        try:
            bstack111lll1l1l_opy_ = json.loads(bstack111lll1l11_opy_)
            if bstack1lll1_opy_ (u"ࠤࡲࡷࠧ༓") in bstack111lll1l1l_opy_:
                bstack1lll1l11ll_opy_[bstack1lll1_opy_ (u"ࠥࡳࡸࠨ༔")] = bstack111lll1l1l_opy_[bstack1lll1_opy_ (u"ࠦࡴࡹࠢ༕")]
            if bstack1lll1_opy_ (u"ࠧࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ༖") in bstack111lll1l1l_opy_ or bstack1lll1_opy_ (u"ࠨ࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠤ༗") in bstack111lll1l1l_opy_:
                bstack1lll1l11ll_opy_[bstack1lll1_opy_ (u"ࠢࡰࡵ࡙ࡩࡷࡹࡩࡰࡰ༘ࠥ")] = bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠣࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲ༙ࠧ"), bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠤࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༚")))
            if bstack1lll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࠦ༛") in bstack111lll1l1l_opy_ or bstack1lll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠤ༜") in bstack111lll1l1l_opy_:
                bstack1lll1l11ll_opy_[bstack1lll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠥ༝")] = bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࠢ༞"), bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠧ༟")))
            if bstack1lll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠥ༠") in bstack111lll1l1l_opy_ or bstack1lll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠥ༡") in bstack111lll1l1l_opy_:
                bstack1lll1l11ll_opy_[bstack1lll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠦ༢")] = bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ༣"), bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳࠨ༤")))
            if bstack1lll1_opy_ (u"ࠨࡤࡦࡸ࡬ࡧࡪࠨ༥") in bstack111lll1l1l_opy_ or bstack1lll1_opy_ (u"ࠢࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠦ༦") in bstack111lll1l1l_opy_:
                bstack1lll1l11ll_opy_[bstack1lll1_opy_ (u"ࠣࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠧ༧")] = bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠤࡧࡩࡻ࡯ࡣࡦࠤ༨"), bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠥࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠢ༩")))
            if bstack1lll1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࠨ༪") in bstack111lll1l1l_opy_ or bstack1lll1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦ༫") in bstack111lll1l1l_opy_:
                bstack1lll1l11ll_opy_[bstack1lll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧ༬")] = bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠤ༭"), bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠢ༮")))
            if bstack1lll1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧ༯") in bstack111lll1l1l_opy_ or bstack1lll1_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༰") in bstack111lll1l1l_opy_:
                bstack1lll1l11ll_opy_[bstack1lll1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳࠨ༱")] = bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣ༲"), bstack111lll1l1l_opy_.get(bstack1lll1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣ༳")))
            if bstack1lll1_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡖࡢࡴ࡬ࡥࡧࡲࡥࡴࠤ༴") in bstack111lll1l1l_opy_:
                bstack1lll1l11ll_opy_[bstack1lll1_opy_ (u"ࠣࡥࡸࡷࡹࡵ࡭ࡗࡣࡵ࡭ࡦࡨ࡬ࡦࡵ༵ࠥ")] = bstack111lll1l1l_opy_[bstack1lll1_opy_ (u"ࠤࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠦ༶")]
        except Exception as error:
            logger.error(bstack1lll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡣࡶࡴࡵࡩࡳࡺࠠࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠢࡧࡥࡹࡧ࠺ࠡࠤ༷") +  str(error))
        return bstack1lll1l11ll_opy_