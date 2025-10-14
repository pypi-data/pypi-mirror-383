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
import tempfile
import math
from bstack_utils import bstack11lll11l_opy_
from bstack_utils.constants import bstack1ll1l1lll_opy_, bstack11l1l1lll11_opy_
from bstack_utils.helper import bstack111llllll11_opy_, get_host_info
from bstack_utils.bstack11ll111l1ll_opy_ import bstack11ll11111ll_opy_
import json
import re
import sys
bstack111l111l111_opy_ = bstack1lll1_opy_ (u"ࠨࡲࡦࡶࡵࡽ࡙࡫ࡳࡵࡵࡒࡲࡋࡧࡩ࡭ࡷࡵࡩࠧṧ")
bstack1111ll1l1l1_opy_ = bstack1lll1_opy_ (u"ࠢࡢࡤࡲࡶࡹࡈࡵࡪ࡮ࡧࡓࡳࡌࡡࡪ࡮ࡸࡶࡪࠨṨ")
bstack1111llll1l1_opy_ = bstack1lll1_opy_ (u"ࠣࡴࡸࡲࡕࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡇࡣ࡬ࡰࡪࡪࡆࡪࡴࡶࡸࠧṩ")
bstack1111llllll1_opy_ = bstack1lll1_opy_ (u"ࠤࡵࡩࡷࡻ࡮ࡑࡴࡨࡺ࡮ࡵࡵࡴ࡮ࡼࡊࡦ࡯࡬ࡦࡦࠥṪ")
bstack1111l1ll1l1_opy_ = bstack1lll1_opy_ (u"ࠥࡷࡰ࡯ࡰࡇ࡮ࡤ࡯ࡾࡧ࡮ࡥࡈࡤ࡭ࡱ࡫ࡤࠣṫ")
bstack1111l1lll1l_opy_ = bstack1lll1_opy_ (u"ࠦࡷࡻ࡮ࡔ࡯ࡤࡶࡹ࡙ࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠣṬ")
bstack111l111l1l1_opy_ = {
    bstack111l111l111_opy_,
    bstack1111ll1l1l1_opy_,
    bstack1111llll1l1_opy_,
    bstack1111llllll1_opy_,
    bstack1111l1ll1l1_opy_,
    bstack1111l1lll1l_opy_
}
bstack111l1111l1l_opy_ = {bstack1lll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬṭ")}
logger = bstack11lll11l_opy_.get_logger(__name__, bstack1ll1l1lll_opy_)
class bstack1111l1l1lll_opy_:
    def __init__(self):
        self.enabled = False
        self.name = None
    def enable(self, name):
        self.enabled = True
        self.name = name
    def disable(self):
        self.enabled = False
        self.name = None
    def bstack1111ll1111l_opy_(self):
        return self.enabled
    def get_name(self):
        return self.name
class bstack111llll111_opy_:
    _1ll1l1l1lll_opy_ = None
    def __init__(self, config):
        self.bstack1111lll11l1_opy_ = False
        self.bstack1111ll1l11l_opy_ = False
        self.bstack1111lllllll_opy_ = False
        self.bstack1111ll1l1ll_opy_ = False
        self.bstack1111l1l1l1l_opy_ = None
        self.bstack1111ll1lll1_opy_ = bstack1111l1l1lll_opy_()
        self.bstack111l111l11l_opy_ = None
        opts = config.get(bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪṮ"), {})
        self.bstack1111lllll1l_opy_ = config.get(bstack1lll1_opy_ (u"ࠧࡴ࡯ࡤࡶࡹ࡙ࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࡇࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࡥࡴࡇࡑ࡚ࠬṯ"), bstack1lll1_opy_ (u"ࠣࠤṰ"))
        self.bstack1111lll1l11_opy_ = config.get(bstack1lll1_opy_ (u"ࠩࡶࡱࡦࡸࡴࡔࡧ࡯ࡩࡨࡺࡩࡰࡰࡉࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࡧࡶࡇࡑࡏࠧṱ"), bstack1lll1_opy_ (u"ࠥࠦṲ"))
        bstack1111ll1l111_opy_ = opts.get(bstack1111l1lll1l_opy_, {})
        bstack1111l1lll11_opy_ = None
        if bstack1lll1_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫṳ") in bstack1111ll1l111_opy_:
            bstack1111l1lll11_opy_ = bstack1111ll1l111_opy_[bstack1lll1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬṴ")]
            if bstack1111l1lll11_opy_ is None:
                bstack1111l1lll11_opy_ = []
        self.__1111lll111l_opy_(
            bstack1111ll1l111_opy_.get(bstack1lll1_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧṵ"), False),
            bstack1111ll1l111_opy_.get(bstack1lll1_opy_ (u"ࠧ࡮ࡱࡧࡩࠬṶ"), bstack1lll1_opy_ (u"ࠨࡴࡨࡰࡪࡼࡡ࡯ࡶࡉ࡭ࡷࡹࡴࠨṷ")),
            bstack1111l1lll11_opy_
        )
        self.__1111lllll11_opy_(opts.get(bstack1111llll1l1_opy_, False))
        self.__1111ll111l1_opy_(opts.get(bstack1111llllll1_opy_, False))
        self.__1111lll11ll_opy_(opts.get(bstack1111l1ll1l1_opy_, False))
    @classmethod
    def bstack1111l11l1_opy_(cls, config=None):
        if cls._1ll1l1l1lll_opy_ is None and config is not None:
            cls._1ll1l1l1lll_opy_ = bstack111llll111_opy_(config)
        return cls._1ll1l1l1lll_opy_
    @staticmethod
    def bstack1ll11l1ll1_opy_(config: dict) -> bool:
        bstack1111ll11l1l_opy_ = config.get(bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࡕࡰࡵ࡫ࡲࡲࡸ࠭Ṹ"), {}).get(bstack111l111l111_opy_, {})
        return bstack1111ll11l1l_opy_.get(bstack1lll1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫṹ"), False)
    @staticmethod
    def bstack1l11l111ll_opy_(config: dict) -> int:
        bstack1111ll11l1l_opy_ = config.get(bstack1lll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨṺ"), {}).get(bstack111l111l111_opy_, {})
        retries = 0
        if bstack111llll111_opy_.bstack1ll11l1ll1_opy_(config):
            retries = bstack1111ll11l1l_opy_.get(bstack1lll1_opy_ (u"ࠬࡳࡡࡹࡔࡨࡸࡷ࡯ࡥࡴࠩṻ"), 1)
        return retries
    @staticmethod
    def bstack11l1l11ll_opy_(config: dict) -> dict:
        bstack1111lll1l1l_opy_ = config.get(bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪṼ"), {})
        return {
            key: value for key, value in bstack1111lll1l1l_opy_.items() if key in bstack111l111l1l1_opy_
        }
    @staticmethod
    def bstack111l1111lll_opy_():
        bstack1lll1_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈ࡮ࡥࡤ࡭ࠣ࡭࡫ࠦࡴࡩࡧࠣࡥࡧࡵࡲࡵࠢࡥࡹ࡮ࡲࡤࠡࡨ࡬ࡰࡪࠦࡥࡹ࡫ࡶࡸࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦṽ")
        return os.path.exists(os.path.join(tempfile.gettempdir(), bstack1lll1_opy_ (u"ࠣࡣࡥࡳࡷࡺ࡟ࡣࡷ࡬ࡰࡩࡥࡻࡾࠤṾ").format(os.getenv(bstack1lll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢṿ")))))
    @staticmethod
    def bstack1111lll1lll_opy_(test_name: str):
        bstack1lll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡄࡪࡨࡧࡰࠦࡩࡧࠢࡷ࡬ࡪࠦࡡࡣࡱࡵࡸࠥࡨࡵࡪ࡮ࡧࠤ࡫࡯࡬ࡦࠢࡨࡼ࡮ࡹࡴࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢẀ")
        bstack1111ll1llll_opy_ = os.path.join(tempfile.gettempdir(), bstack1lll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࡣࡹ࡫ࡳࡵࡵࡢࡿࢂ࠴ࡴࡹࡶࠥẁ").format(os.getenv(bstack1lll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠥẂ"))))
        with open(bstack1111ll1llll_opy_, bstack1lll1_opy_ (u"࠭ࡡࠨẃ")) as file:
            file.write(bstack1lll1_opy_ (u"ࠢࡼࡿ࡟ࡲࠧẄ").format(test_name))
    @staticmethod
    def bstack111l1111l11_opy_(framework: str) -> bool:
       return framework.lower() in bstack111l1111l1l_opy_
    @staticmethod
    def bstack11l1l1l111l_opy_(config: dict) -> bool:
        bstack1111ll11l11_opy_ = config.get(bstack1lll1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬẅ"), {}).get(bstack1111ll1l1l1_opy_, {})
        return bstack1111ll11l11_opy_.get(bstack1lll1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪẆ"), False)
    @staticmethod
    def bstack11l1l111111_opy_(config: dict, bstack11l1l111ll1_opy_: int = 0) -> int:
        bstack1lll1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡈࡧࡷࠤࡹ࡮ࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡷ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨ࠱ࠦࡷࡩ࡫ࡦ࡬ࠥࡩࡡ࡯ࠢࡥࡩࠥࡧ࡮ࠡࡣࡥࡷࡴࡲࡵࡵࡧࠣࡲࡺࡳࡢࡦࡴࠣࡳࡷࠦࡡࠡࡲࡨࡶࡨ࡫࡮ࡵࡣࡪࡩ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡂࡴࡪࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡨࡵ࡮ࡧ࡫ࡪࠤ࠭ࡪࡩࡤࡶࠬ࠾࡚ࠥࡨࡦࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡥࡹ࡯࡯࡯ࠢࡧ࡭ࡨࡺࡩࡰࡰࡤࡶࡾ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡺ࡯ࡵࡣ࡯ࡣࡹ࡫ࡳࡵࡵࠣࠬ࡮ࡴࡴࠪ࠼ࠣࡘ࡭࡫ࠠࡵࡱࡷࡥࡱࠦ࡮ࡶ࡯ࡥࡩࡷࠦ࡯ࡧࠢࡷࡩࡸࡺࡳࠡࠪࡵࡩࡶࡻࡩࡳࡧࡧࠤ࡫ࡵࡲࠡࡲࡨࡶࡨ࡫࡮ࡵࡣࡪࡩ࠲ࡨࡡࡴࡧࡧࠤࡹ࡮ࡲࡦࡵ࡫ࡳࡱࡪࡳࠪ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡮ࡴࡴ࠻ࠢࡗ࡬ࡪࠦࡦࡢ࡫࡯ࡹࡷ࡫ࠠࡵࡪࡵࡩࡸ࡮࡯࡭ࡦ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣẇ")
        bstack1111ll11l11_opy_ = config.get(bstack1lll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨẈ"), {}).get(bstack1lll1_opy_ (u"ࠬࡧࡢࡰࡴࡷࡆࡺ࡯࡬ࡥࡑࡱࡊࡦ࡯࡬ࡶࡴࡨࠫẉ"), {})
        bstack1111ll1ll1l_opy_ = 0
        bstack111l1111111_opy_ = 0
        if bstack111llll111_opy_.bstack11l1l1l111l_opy_(config):
            bstack111l1111111_opy_ = bstack1111ll11l11_opy_.get(bstack1lll1_opy_ (u"࠭࡭ࡢࡺࡉࡥ࡮ࡲࡵࡳࡧࡶࠫẊ"), 5)
            if isinstance(bstack111l1111111_opy_, str) and bstack111l1111111_opy_.endswith(bstack1lll1_opy_ (u"ࠧࠦࠩẋ")):
                try:
                    percentage = int(bstack111l1111111_opy_.strip(bstack1lll1_opy_ (u"ࠨࠧࠪẌ")))
                    if bstack11l1l111ll1_opy_ > 0:
                        bstack1111ll1ll1l_opy_ = math.ceil((percentage * bstack11l1l111ll1_opy_) / 100)
                    else:
                        raise ValueError(bstack1lll1_opy_ (u"ࠤࡗࡳࡹࡧ࡬ࠡࡶࡨࡷࡹࡹࠠ࡮ࡷࡶࡸࠥࡨࡥࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡪࡴࡸࠠࡱࡧࡵࡧࡪࡴࡴࡢࡩࡨ࠱ࡧࡧࡳࡦࡦࠣࡸ࡭ࡸࡥࡴࡪࡲࡰࡩࡹ࠮ࠣẍ"))
                except ValueError as e:
                    raise ValueError(bstack1lll1_opy_ (u"ࠥࡍࡳࡼࡡ࡭࡫ࡧࠤࡵ࡫ࡲࡤࡧࡱࡸࡦ࡭ࡥࠡࡸࡤࡰࡺ࡫ࠠࡧࡱࡵࠤࡲࡧࡸࡇࡣ࡬ࡰࡺࡸࡥࡴ࠼ࠣࡿࢂࠨẎ").format(bstack111l1111111_opy_)) from e
            else:
                bstack1111ll1ll1l_opy_ = int(bstack111l1111111_opy_)
        logger.info(bstack1lll1_opy_ (u"ࠦࡒࡧࡸࠡࡨࡤ࡭ࡱࡻࡲࡦࡵࠣࡸ࡭ࡸࡥࡴࡪࡲࡰࡩࠦࡳࡦࡶࠣࡸࡴࡀࠠࡼࡿࠣࠬ࡫ࡸ࡯࡮ࠢࡦࡳࡳ࡬ࡩࡨ࠼ࠣࡿࢂ࠯ࠢẏ").format(bstack1111ll1ll1l_opy_, bstack111l1111111_opy_))
        return bstack1111ll1ll1l_opy_
    def bstack1111ll1ll11_opy_(self):
        return self.bstack1111ll1l1ll_opy_
    def bstack111l111111l_opy_(self):
        return self.bstack1111l1l1l1l_opy_
    def bstack1111l1l11ll_opy_(self):
        return self.bstack111l111l11l_opy_
    def __1111lll111l_opy_(self, enabled, mode, source=None):
        try:
            self.bstack1111ll1l1ll_opy_ = bool(enabled)
            if mode not in [bstack1lll1_opy_ (u"ࠬࡸࡥ࡭ࡧࡹࡥࡳࡺࡆࡪࡴࡶࡸࠬẐ"), bstack1lll1_opy_ (u"࠭ࡲࡦ࡮ࡨࡺࡦࡴࡴࡐࡰ࡯ࡽࠬẑ")]:
                logger.warning(bstack1lll1_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡵࡰࡥࡷࡺࠠࡴࡧ࡯ࡩࡨࡺࡩࡰࡰࠣࡱࡴࡪࡥࠡࠩࡾࢁࠬࠦࡰࡳࡱࡹ࡭ࡩ࡫ࡤ࠯ࠢࡇࡩ࡫ࡧࡵ࡭ࡶ࡬ࡲ࡬ࠦࡴࡰࠢࠪࡶࡪࡲࡥࡷࡣࡱࡸࡋ࡯ࡲࡴࡶࠪ࠲ࠧẒ").format(mode))
                mode = bstack1lll1_opy_ (u"ࠨࡴࡨࡰࡪࡼࡡ࡯ࡶࡉ࡭ࡷࡹࡴࠨẓ")
            self.bstack1111l1l1l1l_opy_ = mode
            if source is None:
                self.bstack111l111l11l_opy_ = None
            elif isinstance(source, list):
                self.bstack111l111l11l_opy_ = source
            elif isinstance(source, str) and source.endswith(bstack1lll1_opy_ (u"ࠩ࠱࡮ࡸࡵ࡮ࠨẔ")):
                self.bstack111l111l11l_opy_ = self._1111llll111_opy_(source)
            self.__111l11111ll_opy_()
        except Exception as e:
            logger.error(bstack1lll1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡷࡲࡧࡲࡵࠢࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠥࡩ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࠥ࠳ࠠࡦࡰࡤࡦࡱ࡫ࡤ࠻ࠢࡾࢁ࠱ࠦ࡭ࡰࡦࡨ࠾ࠥࢁࡽ࠭ࠢࡶࡳࡺࡸࡣࡦ࠼ࠣࡿࢂ࠴ࠠࡆࡴࡵࡳࡷࡀࠠࡼࡿࠥẕ").format(enabled, mode, source, e))
    def bstack1111l1lllll_opy_(self):
        return self.bstack1111lll11l1_opy_
    def __1111lllll11_opy_(self, value):
        self.bstack1111lll11l1_opy_ = bool(value)
        self.__111l11111ll_opy_()
    def bstack1111lll1111_opy_(self):
        return self.bstack1111ll1l11l_opy_
    def __1111ll111l1_opy_(self, value):
        self.bstack1111ll1l11l_opy_ = bool(value)
        self.__111l11111ll_opy_()
    def bstack1111ll111ll_opy_(self):
        return self.bstack1111lllllll_opy_
    def __1111lll11ll_opy_(self, value):
        self.bstack1111lllllll_opy_ = bool(value)
        self.__111l11111ll_opy_()
    def __111l11111ll_opy_(self):
        if self.bstack1111ll1l1ll_opy_:
            self.bstack1111lll11l1_opy_ = False
            self.bstack1111ll1l11l_opy_ = False
            self.bstack1111lllllll_opy_ = False
            self.bstack1111ll1lll1_opy_.enable(bstack1111l1lll1l_opy_)
        elif self.bstack1111lll11l1_opy_:
            self.bstack1111ll1l11l_opy_ = False
            self.bstack1111lllllll_opy_ = False
            self.bstack1111ll1l1ll_opy_ = False
            self.bstack1111ll1lll1_opy_.enable(bstack1111llll1l1_opy_)
        elif self.bstack1111ll1l11l_opy_:
            self.bstack1111lll11l1_opy_ = False
            self.bstack1111lllllll_opy_ = False
            self.bstack1111ll1l1ll_opy_ = False
            self.bstack1111ll1lll1_opy_.enable(bstack1111llllll1_opy_)
        elif self.bstack1111lllllll_opy_:
            self.bstack1111lll11l1_opy_ = False
            self.bstack1111ll1l11l_opy_ = False
            self.bstack1111ll1l1ll_opy_ = False
            self.bstack1111ll1lll1_opy_.enable(bstack1111l1ll1l1_opy_)
        else:
            self.bstack1111ll1lll1_opy_.disable()
    def bstack11lll11l11_opy_(self):
        return self.bstack1111ll1lll1_opy_.bstack1111ll1111l_opy_()
    def bstack1ll1lll1ll_opy_(self):
        if self.bstack1111ll1lll1_opy_.bstack1111ll1111l_opy_():
            return self.bstack1111ll1lll1_opy_.get_name()
        return None
    def _1111llll111_opy_(self, bstack1111l1l1ll1_opy_):
        bstack1lll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡒࡤࡶࡸ࡫ࠠࡋࡕࡒࡒࠥࡹ࡯ࡶࡴࡦࡩࠥࡩ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࠥ࡬ࡩ࡭ࡧࠣࡥࡳࡪࠠࡧࡱࡵࡱࡦࡺࠠࡪࡶࠣࡪࡴࡸࠠࡴ࡯ࡤࡶࡹࠦࡳࡦ࡮ࡨࡧࡹ࡯࡯࡯࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡵࡲࡹࡷࡩࡥࡠࡨ࡬ࡰࡪࡥࡰࡢࡶ࡫ࠤ࠭ࡹࡴࡳࠫ࠽ࠤࡕࡧࡴࡩࠢࡷࡳࠥࡺࡨࡦࠢࡍࡗࡔࡔࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠࡧ࡫࡯ࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࡬ࡪࡵࡷ࠾ࠥࡌ࡯ࡳ࡯ࡤࡸࡹ࡫ࡤࠡ࡮࡬ࡷࡹࠦ࡯ࡧࠢࡵࡩࡵࡵࡳࡪࡶࡲࡶࡾࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࡹࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦẖ")
        if not os.path.isfile(bstack1111l1l1ll1_opy_):
            logger.error(bstack1lll1_opy_ (u"࡙ࠧ࡯ࡶࡴࡦࡩࠥ࡬ࡩ࡭ࡧࠣࠫࢀࢃࠧࠡࡦࡲࡩࡸࠦ࡮ࡰࡶࠣࡩࡽ࡯ࡳࡵ࠰ࠥẗ").format(bstack1111l1l1ll1_opy_))
            return []
        data = None
        try:
            with open(bstack1111l1l1ll1_opy_, bstack1lll1_opy_ (u"ࠨࡲࠣẘ")) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(bstack1lll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡰࡢࡴࡶ࡭ࡳ࡭ࠠࡋࡕࡒࡒࠥ࡬ࡲࡰ࡯ࠣࡷࡴࡻࡲࡤࡧࠣࡪ࡮ࡲࡥࠡࠩࡾࢁࠬࡀࠠࡼࡿࠥẙ").format(bstack1111l1l1ll1_opy_, e))
            return []
        _1111l1ll111_opy_ = None
        _1111ll11lll_opy_ = None
        def _1111llll11l_opy_():
            bstack111l1111ll1_opy_ = {}
            bstack1111l1llll1_opy_ = {}
            try:
                if self.bstack1111lllll1l_opy_.startswith(bstack1lll1_opy_ (u"ࠨࡽࠪẚ")) and self.bstack1111lllll1l_opy_.endswith(bstack1lll1_opy_ (u"ࠩࢀࠫẛ")):
                    bstack111l1111ll1_opy_ = json.loads(self.bstack1111lllll1l_opy_)
                else:
                    bstack111l1111ll1_opy_ = dict(item.split(bstack1lll1_opy_ (u"ࠪ࠾ࠬẜ")) for item in self.bstack1111lllll1l_opy_.split(bstack1lll1_opy_ (u"ࠫ࠱࠭ẝ")) if bstack1lll1_opy_ (u"ࠬࡀࠧẞ") in item) if self.bstack1111lllll1l_opy_ else {}
                if self.bstack1111lll1l11_opy_.startswith(bstack1lll1_opy_ (u"࠭ࡻࠨẟ")) and self.bstack1111lll1l11_opy_.endswith(bstack1lll1_opy_ (u"ࠧࡾࠩẠ")):
                    bstack1111l1llll1_opy_ = json.loads(self.bstack1111lll1l11_opy_)
                else:
                    bstack1111l1llll1_opy_ = dict(item.split(bstack1lll1_opy_ (u"ࠨ࠼ࠪạ")) for item in self.bstack1111lll1l11_opy_.split(bstack1lll1_opy_ (u"ࠩ࠯ࠫẢ")) if bstack1lll1_opy_ (u"ࠪ࠾ࠬả") in item) if self.bstack1111lll1l11_opy_ else {}
            except json.JSONDecodeError as e:
                logger.error(bstack1lll1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡴࡦࡸࡳࡪࡰࡪࠤ࡫࡫ࡡࡵࡷࡵࡩࠥࡨࡲࡢࡰࡦ࡬ࠥࡳࡡࡱࡲ࡬ࡲ࡬ࡹ࠺ࠡࡽࢀࠦẤ").format(e))
            logger.debug(bstack1lll1_opy_ (u"ࠧࡌࡥࡢࡶࡸࡶࡪࠦࡢࡳࡣࡱࡧ࡭ࠦ࡭ࡢࡲࡳ࡭ࡳ࡭ࡳࠡࡨࡵࡳࡲࠦࡥ࡯ࡸ࠽ࠤࢀࢃࠬࠡࡅࡏࡍ࠿ࠦࡻࡾࠤấ").format(bstack111l1111ll1_opy_, bstack1111l1llll1_opy_))
            return bstack111l1111ll1_opy_, bstack1111l1llll1_opy_
        if _1111l1ll111_opy_ is None or _1111ll11lll_opy_ is None:
            _1111l1ll111_opy_, _1111ll11lll_opy_ = _1111llll11l_opy_()
        def bstack1111l1ll11l_opy_(name, bstack111l11111l1_opy_):
            if name in _1111ll11lll_opy_:
                return _1111ll11lll_opy_[name]
            if name in _1111l1ll111_opy_:
                return _1111l1ll111_opy_[name]
            if bstack111l11111l1_opy_.get(bstack1lll1_opy_ (u"࠭ࡦࡦࡣࡷࡹࡷ࡫ࡂࡳࡣࡱࡧ࡭࠭Ầ")):
                return bstack111l11111l1_opy_[bstack1lll1_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࠧầ")]
            return None
        if isinstance(data, dict):
            bstack1111ll11ll1_opy_ = []
            bstack1111l1l1l11_opy_ = re.compile(bstack1lll1_opy_ (u"ࡳࠩࡡ࡟ࡆ࠳࡚࠱࠯࠼ࡣࡢ࠱ࠤࠨẨ"))
            for name, bstack111l11111l1_opy_ in data.items():
                if not isinstance(bstack111l11111l1_opy_, dict):
                    continue
                if not bstack111l11111l1_opy_.get(bstack1lll1_opy_ (u"ࠩࡸࡶࡱ࠭ẩ")):
                    logger.warning(bstack1lll1_opy_ (u"ࠥࡖࡪࡶ࡯ࡴ࡫ࡷࡳࡷࡿࠠࡖࡔࡏࠤ࡮ࡹࠠ࡮࡫ࡶࡷ࡮ࡴࡧࠡࡨࡲࡶࠥࡹ࡯ࡶࡴࡦࡩࠥ࠭ࡻࡾࠩ࠽ࠤࢀࢃࠢẪ").format(name, bstack111l11111l1_opy_))
                    continue
                if not bstack1111l1l1l11_opy_.match(name):
                    logger.warning(bstack1lll1_opy_ (u"ࠦࡎࡴࡶࡢ࡮࡬ࡨࠥࡹ࡯ࡶࡴࡦࡩࠥ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠢࡩࡳࡷࡳࡡࡵࠢࡩࡳࡷࠦࠧࡼࡿࠪ࠾ࠥࢁࡽࠣẫ").format(name, bstack111l11111l1_opy_))
                    continue
                if len(name) > 30 or len(name) < 1:
                    logger.warning(bstack1lll1_opy_ (u"࡙ࠧ࡯ࡶࡴࡦࡩࠥ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠢࠪࡿࢂ࠭ࠠ࡮ࡷࡶࡸࠥ࡮ࡡࡷࡧࠣࡥࠥࡲࡥ࡯ࡩࡷ࡬ࠥࡨࡥࡵࡹࡨࡩࡳࠦ࠱ࠡࡣࡱࡨࠥ࠹࠰ࠡࡥ࡫ࡥࡷࡧࡣࡵࡧࡵࡷ࠳ࠨẬ").format(name))
                    continue
                bstack111l11111l1_opy_ = bstack111l11111l1_opy_.copy()
                bstack111l11111l1_opy_[bstack1lll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫậ")] = name
                bstack111l11111l1_opy_[bstack1lll1_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࠧẮ")] = bstack1111l1ll11l_opy_(name, bstack111l11111l1_opy_)
                if not bstack111l11111l1_opy_.get(bstack1lll1_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࠨắ")):
                    logger.warning(bstack1lll1_opy_ (u"ࠤࡉࡩࡦࡺࡵࡳࡧࠣࡦࡷࡧ࡮ࡤࡪࠣࡲࡴࡺࠠࡴࡲࡨࡧ࡮࡬ࡩࡦࡦࠣࡪࡴࡸࠠࡴࡱࡸࡶࡨ࡫ࠠࠨࡽࢀࠫ࠿ࠦࡻࡾࠤẰ").format(name, bstack111l11111l1_opy_))
                    continue
                if bstack111l11111l1_opy_.get(bstack1lll1_opy_ (u"ࠪࡦࡦࡹࡥࡃࡴࡤࡲࡨ࡮ࠧằ")) and bstack111l11111l1_opy_[bstack1lll1_opy_ (u"ࠫࡧࡧࡳࡦࡄࡵࡥࡳࡩࡨࠨẲ")] == bstack111l11111l1_opy_[bstack1lll1_opy_ (u"ࠬ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠬẳ")]:
                    logger.warning(bstack1lll1_opy_ (u"ࠨࡆࡦࡣࡷࡹࡷ࡫ࠠࡣࡴࡤࡲࡨ࡮ࠠࡢࡰࡧࠤࡧࡧࡳࡦࠢࡥࡶࡦࡴࡣࡩࠢࡦࡥࡳࡴ࡯ࡵࠢࡥࡩࠥࡺࡨࡦࠢࡶࡥࡲ࡫ࠠࡧࡱࡵࠤࡸࡵࡵࡳࡥࡨࠤࠬࢁࡽࠨ࠼ࠣࡿࢂࠨẴ").format(name, bstack111l11111l1_opy_))
                    continue
                bstack1111ll11ll1_opy_.append(bstack111l11111l1_opy_)
            return bstack1111ll11ll1_opy_
        return data
    def bstack111l111llll_opy_(self):
        data = {
            bstack1lll1_opy_ (u"ࠧࡳࡷࡱࡣࡸࡳࡡࡳࡶࡢࡷࡪࡲࡥࡤࡶ࡬ࡳࡳ࠭ẵ"): {
                bstack1lll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩẶ"): self.bstack1111ll1ll11_opy_(),
                bstack1lll1_opy_ (u"ࠩࡰࡳࡩ࡫ࠧặ"): self.bstack111l111111l_opy_(),
                bstack1lll1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪẸ"): self.bstack1111l1l11ll_opy_()
            }
        }
        return data
    def bstack1111l1ll1ll_opy_(self, config):
        bstack1111lll1ll1_opy_ = {}
        bstack1111lll1ll1_opy_[bstack1lll1_opy_ (u"ࠫࡷࡻ࡮ࡠࡵࡰࡥࡷࡺ࡟ࡴࡧ࡯ࡩࡨࡺࡩࡰࡰࠪẹ")] = {
            bstack1lll1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭Ẻ"): self.bstack1111ll1ll11_opy_(),
            bstack1lll1_opy_ (u"࠭࡭ࡰࡦࡨࠫẻ"): self.bstack111l111111l_opy_()
        }
        bstack1111lll1ll1_opy_[bstack1lll1_opy_ (u"ࠧࡳࡧࡵࡹࡳࡥࡰࡳࡧࡹ࡭ࡴࡻࡳ࡭ࡻࡢࡪࡦ࡯࡬ࡦࡦࠪẼ")] = {
            bstack1lll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩẽ"): self.bstack1111lll1111_opy_()
        }
        bstack1111lll1ll1_opy_[bstack1lll1_opy_ (u"ࠩࡵࡹࡳࡥࡰࡳࡧࡹ࡭ࡴࡻࡳ࡭ࡻࡢࡪࡦ࡯࡬ࡦࡦࡢࡪ࡮ࡸࡳࡵࠩẾ")] = {
            bstack1lll1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫế"): self.bstack1111l1lllll_opy_()
        }
        bstack1111lll1ll1_opy_[bstack1lll1_opy_ (u"ࠫࡸࡱࡩࡱࡡࡩࡥ࡮ࡲࡩ࡯ࡩࡢࡥࡳࡪ࡟ࡧ࡮ࡤ࡯ࡾ࠭Ề")] = {
            bstack1lll1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭ề"): self.bstack1111ll111ll_opy_()
        }
        if self.bstack1ll11l1ll1_opy_(config):
            bstack1111lll1ll1_opy_[bstack1lll1_opy_ (u"࠭ࡲࡦࡶࡵࡽࡤࡺࡥࡴࡶࡶࡣࡴࡴ࡟ࡧࡣ࡬ࡰࡺࡸࡥࠨỂ")] = {
                bstack1lll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨể"): True,
                bstack1lll1_opy_ (u"ࠨ࡯ࡤࡼࡤࡸࡥࡵࡴ࡬ࡩࡸ࠭Ễ"): self.bstack1l11l111ll_opy_(config)
            }
        if self.bstack11l1l1l111l_opy_(config):
            bstack1111lll1ll1_opy_[bstack1lll1_opy_ (u"ࠩࡤࡦࡴࡸࡴࡠࡤࡸ࡭ࡱࡪ࡟ࡰࡰࡢࡪࡦ࡯࡬ࡶࡴࡨࠫễ")] = {
                bstack1lll1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫỆ"): True,
                bstack1lll1_opy_ (u"ࠫࡲࡧࡸࡠࡨࡤ࡭ࡱࡻࡲࡦࡵࠪệ"): self.bstack11l1l111111_opy_(config)
            }
        return bstack1111lll1ll1_opy_
    def bstack1l1111l1ll_opy_(self, config):
        bstack1lll1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆࡳࡱࡲࡥࡤࡶࡶࠤࡧࡻࡩ࡭ࡦࠣࡨࡦࡺࡡࠡࡤࡼࠤࡲࡧ࡫ࡪࡰࡪࠤࡦࠦࡣࡢ࡮࡯ࠤࡹࡵࠠࡵࡪࡨࠤࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡨࡵࡪ࡮ࡧ࠱ࡩࡧࡴࡢࠢࡨࡲࡩࡶ࡯ࡪࡰࡷ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡦࡺ࡯࡬ࡥࡡࡸࡹ࡮ࡪࠠࠩࡵࡷࡶ࠮ࡀࠠࡕࡪࡨࠤ࡚࡛ࡉࡅࠢࡲࡪࠥࡺࡨࡦࠢࡥࡹ࡮ࡲࡤࠡࡶࡲࠤࡨࡵ࡬࡭ࡧࡦࡸࠥࡪࡡࡵࡣࠣࡪࡴࡸ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡧ࡭ࡨࡺ࠺ࠡࡔࡨࡷࡵࡵ࡮ࡴࡧࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡩࠥࡩ࡯࡭࡮ࡨࡧࡹ࠳ࡢࡶ࡫࡯ࡨ࠲ࡪࡡࡵࡣࠣࡩࡳࡪࡰࡰ࡫ࡱࡸ࠱ࠦ࡯ࡳࠢࡑࡳࡳ࡫ࠠࡪࡨࠣࡪࡦ࡯࡬ࡦࡦ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣỈ")
        if not (config.get(bstack1lll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩỉ"), None) in bstack11l1l1lll11_opy_ and self.bstack1111ll1ll11_opy_()):
            return None
        bstack1111llll1ll_opy_ = os.environ.get(bstack1lll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬỊ"), None)
        logger.debug(bstack1lll1_opy_ (u"ࠣ࡝ࡦࡳࡱࡲࡥࡤࡶࡅࡹ࡮ࡲࡤࡅࡣࡷࡥࡢࠦࡃࡰ࡮࡯ࡩࡨࡺࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦ࡙࡚ࠣࡏࡄ࠻ࠢࡾࢁࠧị").format(bstack1111llll1ll_opy_))
        try:
            bstack11ll111ll1l_opy_ = bstack1lll1_opy_ (u"ࠤࡷࡩࡸࡺ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠵ࡡࡱ࡫࠲ࡺ࠶࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾ࠱ࡦࡳࡱࡲࡥࡤࡶ࠰ࡦࡺ࡯࡬ࡥ࠯ࡧࡥࡹࡧࠢỌ").format(bstack1111llll1ll_opy_)
            payload = {
                bstack1lll1_opy_ (u"ࠥࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠣọ"): config.get(bstack1lll1_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩỎ"), bstack1lll1_opy_ (u"ࠬ࠭ỏ")),
                bstack1lll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠤỐ"): config.get(bstack1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪố"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack1lll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡒࡶࡰࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࠨỒ"): os.environ.get(bstack1lll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡓࡗࡑࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠣồ"), bstack1lll1_opy_ (u"ࠥࠦỔ")),
                bstack1lll1_opy_ (u"ࠦࡳࡵࡤࡦࡋࡱࡨࡪࡾࠢổ"): int(os.environ.get(bstack1lll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡓࡕࡄࡆࡡࡌࡒࡉࡋࡘࠣỖ")) or bstack1lll1_opy_ (u"ࠨ࠰ࠣỗ")),
                bstack1lll1_opy_ (u"ࠢࡵࡱࡷࡥࡱࡔ࡯ࡥࡧࡶࠦỘ"): int(os.environ.get(bstack1lll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡑࡗࡅࡑࡥࡎࡐࡆࡈࡣࡈࡕࡕࡏࡖࠥộ")) or bstack1lll1_opy_ (u"ࠤ࠴ࠦỚ")),
                bstack1lll1_opy_ (u"ࠥ࡬ࡴࡹࡴࡊࡰࡩࡳࠧớ"): get_host_info(),
            }
            logger.debug(bstack1lll1_opy_ (u"ࠦࡠࡩ࡯࡭࡮ࡨࡧࡹࡈࡵࡪ࡮ࡧࡈࡦࡺࡡ࡞ࠢࡖࡩࡳࡪࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡱࡣࡼࡰࡴࡧࡤ࠻ࠢࡾࢁࠧỜ").format(payload))
            response = bstack11ll11111ll_opy_.bstack1111ll11111_opy_(bstack11ll111ll1l_opy_, payload)
            if response:
                logger.debug(bstack1lll1_opy_ (u"ࠧࡡࡣࡰ࡮࡯ࡩࡨࡺࡂࡶ࡫࡯ࡨࡉࡧࡴࡢ࡟ࠣࡆࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡤࡱ࡯ࡰࡪࡩࡴࡪࡱࡱࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࡀࠠࡼࡿࠥờ").format(response))
                return response
            else:
                logger.error(bstack1lll1_opy_ (u"ࠨ࡛ࡤࡱ࡯ࡰࡪࡩࡴࡃࡷ࡬ࡰࡩࡊࡡࡵࡣࡠࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡤࡱ࡯ࡰࡪࡩࡴࠡࡤࡸ࡭ࡱࡪࠠࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡥࡹ࡮ࡲࡤࠡࡗࡘࡍࡉࡀࠠࡼࡿࠥỞ").format(bstack1111llll1ll_opy_))
                return None
        except Exception as e:
            logger.error(bstack1lll1_opy_ (u"ࠢ࡜ࡥࡲࡰࡱ࡫ࡣࡵࡄࡸ࡭ࡱࡪࡄࡢࡶࡤࡡࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡨࡵ࡬࡭ࡧࡦࡸ࡮ࡴࡧࠡࡤࡸ࡭ࡱࡪࠠࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡥࡹ࡮ࡲࡤࠡࡗࡘࡍࡉࠦࡻࡾ࠼ࠣࡿࢂࠨở").format(bstack1111llll1ll_opy_, e))
            return None