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
class bstack1lll11llll_opy_:
    def __init__(self, handler):
        self._1lllll11l1ll_opy_ = None
        self.handler = handler
        self._1lllll11lll1_opy_ = self.bstack1lllll11ll11_opy_()
        self.patch()
    def patch(self):
        self._1lllll11l1ll_opy_ = self._1lllll11lll1_opy_.execute
        self._1lllll11lll1_opy_.execute = self.bstack1lllll11ll1l_opy_()
    def bstack1lllll11ll1l_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack1lll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࠧ…"), driver_command, None, this, args)
            response = self._1lllll11l1ll_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack1lll1_opy_ (u"ࠨࡡࡧࡶࡨࡶࠧ‧"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1lllll11lll1_opy_.execute = self._1lllll11l1ll_opy_
    @staticmethod
    def bstack1lllll11ll11_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver