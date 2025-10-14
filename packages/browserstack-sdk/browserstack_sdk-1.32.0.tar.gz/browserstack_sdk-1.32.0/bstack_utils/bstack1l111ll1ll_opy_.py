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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack111l11ll111_opy_ import bstack111l11l1111_opy_
from bstack_utils.bstack1llll1ll11_opy_ import bstack111llll111_opy_
from bstack_utils.helper import bstack1llll1ll_opy_
import json
class bstack11lll1ll_opy_:
    _1ll1l1l1lll_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack111l11l1l1l_opy_ = bstack111l11l1111_opy_(self.config, logger)
        self.bstack1llll1ll11_opy_ = bstack111llll111_opy_.bstack1111l11l1_opy_(config=self.config)
        self.bstack111l111l1ll_opy_ = {}
        self.bstack1111l1l11l_opy_ = False
        self.bstack111l11l1ll1_opy_ = (
            self.__111l111ll1l_opy_()
            and self.bstack1llll1ll11_opy_ is not None
            and self.bstack1llll1ll11_opy_.bstack11lll11l11_opy_()
            and config.get(bstack1lll1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫṋ"), None) is not None
            and config.get(bstack1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪṌ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack1111l11l1_opy_(cls, config, logger):
        if cls._1ll1l1l1lll_opy_ is None and config is not None:
            cls._1ll1l1l1lll_opy_ = bstack11lll1ll_opy_(config, logger)
        return cls._1ll1l1l1lll_opy_
    def bstack11lll11l11_opy_(self):
        bstack1lll1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡊ࡯ࠡࡰࡲࡸࠥࡧࡰࡱ࡮ࡼࠤࡹ࡫ࡳࡵࠢࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡼ࡮ࡥ࡯࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡑ࠴࠵ࡾࠦࡩࡴࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡕࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡪࡵࠣࡲࡴࡺࠠࡦࡰࡤࡦࡱ࡫ࡤࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠤ࡮ࡹࠠࡏࡱࡱࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠦࡩࡴࠢࡑࡳࡳ࡫ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦṍ")
        return self.bstack111l11l1ll1_opy_ and self.bstack111l11l1l11_opy_()
    def bstack111l11l1l11_opy_(self):
        bstack111l11l11l1_opy_ = os.getenv(bstack1lll1_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪṎ"), self.config.get(bstack1lll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ṏ"), None))
        return bstack111l11l11l1_opy_ in bstack11l1l1lll11_opy_
    def __111l111ll1l_opy_(self):
        bstack11l1lllll11_opy_ = False
        for fw in bstack11l1l1l1l11_opy_:
            if fw in self.config.get(bstack1lll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧṐ"), bstack1lll1_opy_ (u"ࠬ࠭ṑ")):
                bstack11l1lllll11_opy_ = True
        return bstack1llll1ll_opy_(self.config.get(bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪṒ"), bstack11l1lllll11_opy_))
    def bstack111l11ll11l_opy_(self):
        return (not self.bstack11lll11l11_opy_() and
                self.bstack1llll1ll11_opy_ is not None and self.bstack1llll1ll11_opy_.bstack11lll11l11_opy_())
    def bstack111l11l111l_opy_(self):
        if not self.bstack111l11ll11l_opy_():
            return
        if self.config.get(bstack1lll1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬṓ"), None) is None or self.config.get(bstack1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫṔ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack1lll1_opy_ (u"ࠤࡗࡩࡸࡺࠠࡓࡧࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡨࡧ࡮ࠨࡶࠣࡻࡴࡸ࡫ࠡࡣࡶࠤࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠠࡰࡴࠣࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠡ࡫ࡶࠤࡳࡻ࡬࡭࠰ࠣࡔࡱ࡫ࡡࡴࡧࠣࡷࡪࡺࠠࡢࠢࡱࡳࡳ࠳࡮ࡶ࡮࡯ࠤࡻࡧ࡬ࡶࡧ࠱ࠦṕ"))
        if not self.__111l111ll1l_opy_():
            self.logger.info(bstack1lll1_opy_ (u"ࠥࡘࡪࡹࡴࠡࡔࡨࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡩࡡ࡯ࠩࡷࠤࡼࡵࡲ࡬ࠢࡤࡷࠥࡺࡥࡴࡶࡕࡩࡵࡵࡲࡵ࡫ࡱ࡫ࠥ࡯ࡳࠡࡦ࡬ࡷࡦࡨ࡬ࡦࡦ࠱ࠤࡕࡲࡥࡢࡵࡨࠤࡪࡴࡡࡣ࡮ࡨࠤ࡮ࡺࠠࡧࡴࡲࡱࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠡࡨ࡬ࡰࡪ࠴ࠢṖ"))
    def bstack111l111ll11_opy_(self):
        return self.bstack1111l1l11l_opy_
    def bstack11111ll1l1_opy_(self, bstack111l111lll1_opy_):
        self.bstack1111l1l11l_opy_ = bstack111l111lll1_opy_
        self.bstack1111l111ll_opy_(bstack1lll1_opy_ (u"ࠦࡦࡶࡰ࡭࡫ࡨࡨࠧṗ"), bstack111l111lll1_opy_)
    def bstack1111l11l1l_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack1lll1_opy_ (u"ࠧࡡࡲࡦࡱࡵࡨࡪࡸ࡟ࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࡡࠥࡔ࡯ࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡶࡲࡰࡸ࡬ࡨࡪࡪࠠࡧࡱࡵࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬࠴ࠢṘ"))
                return None
            orchestration_strategy = None
            bstack1ll1l1l1ll1_opy_ = self.bstack1llll1ll11_opy_.bstack111l111llll_opy_()
            if self.bstack1llll1ll11_opy_ is not None:
                orchestration_strategy = self.bstack1llll1ll11_opy_.bstack1ll1lll1ll_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack1lll1_opy_ (u"ࠨࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡵࡴࡤࡸࡪ࡭ࡹࠡ࡫ࡶࠤࡓࡵ࡮ࡦ࠰ࠣࡇࡦࡴ࡮ࡰࡶࠣࡴࡷࡵࡣࡦࡧࡧࠤࡼ࡯ࡴࡩࠢࡷࡩࡸࡺࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠯ࠤṙ"))
                return None
            self.logger.info(bstack1lll1_opy_ (u"ࠢࡓࡧࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡹ࡬ࡸ࡭ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡵࡴࡤࡸࡪ࡭ࡹ࠻ࠢࡾࢁࠧṚ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack1lll1_opy_ (u"ࠣࡗࡶ࡭ࡳ࡭ࠠࡄࡎࡌࠤ࡫ࡲ࡯ࡸࠢࡩࡳࡷࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦṛ"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy, json.dumps(bstack1ll1l1l1ll1_opy_))
            else:
                self.logger.debug(bstack1lll1_opy_ (u"ࠤࡘࡷ࡮ࡴࡧࠡࡵࡧ࡯ࠥ࡬࡬ࡰࡹࠣࡪࡴࡸࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧṜ"))
                self.bstack111l11l1l1l_opy_.bstack111l11l11ll_opy_(test_files, orchestration_strategy, bstack1ll1l1l1ll1_opy_)
                ordered_test_files = self.bstack111l11l1l1l_opy_.bstack111l11l1lll_opy_()
            if not ordered_test_files:
                return None
            self.bstack1111l111ll_opy_(bstack1lll1_opy_ (u"ࠥࡹࡵࡲ࡯ࡢࡦࡨࡨ࡙࡫ࡳࡵࡈ࡬ࡰࡪࡹࡃࡰࡷࡱࡸࠧṝ"), len(test_files))
            self.bstack1111l111ll_opy_(bstack1lll1_opy_ (u"ࠦࡳࡵࡤࡦࡋࡱࡨࡪࡾࠢṞ"), int(os.environ.get(bstack1lll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡓࡕࡄࡆࡡࡌࡒࡉࡋࡘࠣṟ")) or bstack1lll1_opy_ (u"ࠨ࠰ࠣṠ")))
            self.bstack1111l111ll_opy_(bstack1lll1_opy_ (u"ࠢࡵࡱࡷࡥࡱࡔ࡯ࡥࡧࡶࠦṡ"), int(os.environ.get(bstack1lll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡏࡑࡇࡉࡤࡉࡏࡖࡐࡗࠦṢ")) or bstack1lll1_opy_ (u"ࠤ࠴ࠦṣ")))
            self.bstack1111l111ll_opy_(bstack1lll1_opy_ (u"ࠥࡨࡴࡽ࡮࡭ࡱࡤࡨࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴࡅࡲࡹࡳࡺࠢṤ"), len(ordered_test_files))
            self.bstack1111l111ll_opy_(bstack1lll1_opy_ (u"ࠦࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳࡂࡒࡌࡇࡦࡲ࡬ࡄࡱࡸࡲࡹࠨṥ"), self.bstack111l11l1l1l_opy_.bstack111l11ll1l1_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack1lll1_opy_ (u"ࠧࡡࡲࡦࡱࡵࡨࡪࡸ࡟ࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࡡࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡤ࡮ࡤࡷࡸ࡫ࡳ࠻ࠢࡾࢁࠧṦ").format(e))
        return None
    def bstack1111l111ll_opy_(self, key, value):
        self.bstack111l111l1ll_opy_[key] = value
    def bstack111l11lll_opy_(self):
        return self.bstack111l111l1ll_opy_