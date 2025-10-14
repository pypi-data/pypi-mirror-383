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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack111111111l_opy_ import bstack1llllllll1l_opy_
class bstack1lll111l11l_opy_(abc.ABC):
    bin_session_id: str
    bstack111111111l_opy_: bstack1llllllll1l_opy_
    def __init__(self):
        self.bstack1ll1ll1l1l1_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack111111111l_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1lll1l1l111_opy_(self):
        return (self.bstack1ll1ll1l1l1_opy_ != None and self.bin_session_id != None and self.bstack111111111l_opy_ != None)
    def configure(self, bstack1ll1ll1l1l1_opy_, config, bin_session_id: str, bstack111111111l_opy_: bstack1llllllll1l_opy_):
        self.bstack1ll1ll1l1l1_opy_ = bstack1ll1ll1l1l1_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack111111111l_opy_ = bstack111111111l_opy_
        if self.bin_session_id:
            self.logger.debug(bstack1lll1_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡩࡩࠦ࡭ࡰࡦࡸࡰࡪࠦࡻࡴࡧ࡯ࡪ࠳ࡥ࡟ࡤ࡮ࡤࡷࡸࡥ࡟࠯ࡡࡢࡲࡦࡳࡥࡠࡡࢀ࠾ࠥࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࡃࠢቜ") + str(self.bin_session_id) + bstack1lll1_opy_ (u"ࠦࠧቝ"))
    def bstack1ll11l11ll1_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack1lll1_opy_ (u"ࠧࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࠦࡣࡢࡰࡱࡳࡹࠦࡢࡦࠢࡑࡳࡳ࡫ࠢ቞"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False