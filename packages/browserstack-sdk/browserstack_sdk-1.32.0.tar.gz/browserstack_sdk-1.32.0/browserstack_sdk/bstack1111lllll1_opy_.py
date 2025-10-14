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
class RobotHandler():
    def __init__(self, args, logger, bstack1111l111l1_opy_, bstack11111l1l11_opy_):
        self.args = args
        self.logger = logger
        self.bstack1111l111l1_opy_ = bstack1111l111l1_opy_
        self.bstack11111l1l11_opy_ = bstack11111l1l11_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack111l11l11l_opy_(bstack11111111ll_opy_):
        bstack1111111l1l_opy_ = []
        if bstack11111111ll_opy_:
            tokens = str(os.path.basename(bstack11111111ll_opy_)).split(bstack1lll1_opy_ (u"ࠤࡢࠦႛ"))
            camelcase_name = bstack1lll1_opy_ (u"ࠥࠤࠧႜ").join(t.title() for t in tokens)
            suite_name, bstack1111111l11_opy_ = os.path.splitext(camelcase_name)
            bstack1111111l1l_opy_.append(suite_name)
        return bstack1111111l1l_opy_
    @staticmethod
    def bstack1111111ll1_opy_(typename):
        if bstack1lll1_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࠢႝ") in typename:
            return bstack1lll1_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨ႞")
        return bstack1lll1_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢ႟")