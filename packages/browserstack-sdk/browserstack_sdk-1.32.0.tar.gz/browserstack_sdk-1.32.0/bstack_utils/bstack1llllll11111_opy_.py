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
import threading
import logging
logger = logging.getLogger(__name__)
bstack1lllll1ll11l_opy_ = 1000
bstack1lllll1lll11_opy_ = 2
class bstack1lllll1ll1l1_opy_:
    def __init__(self, handler, bstack1llllll111ll_opy_=bstack1lllll1ll11l_opy_, bstack1llllll111l1_opy_=bstack1lllll1lll11_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1llllll111ll_opy_ = bstack1llllll111ll_opy_
        self.bstack1llllll111l1_opy_ = bstack1llllll111l1_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack1111111111_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack1lllll1lllll_opy_()
    def bstack1lllll1lllll_opy_(self):
        self.bstack1111111111_opy_ = threading.Event()
        def bstack1lllll1lll1l_opy_():
            self.bstack1111111111_opy_.wait(self.bstack1llllll111l1_opy_)
            if not self.bstack1111111111_opy_.is_set():
                self.bstack1llllll1111l_opy_()
        self.timer = threading.Thread(target=bstack1lllll1lll1l_opy_, daemon=True)
        self.timer.start()
    def bstack1lllll1llll1_opy_(self):
        try:
            if self.bstack1111111111_opy_ and not self.bstack1111111111_opy_.is_set():
                self.bstack1111111111_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack1lll1_opy_ (u"ࠩ࡞ࡷࡹࡵࡰࡠࡶ࡬ࡱࡪࡸ࡝ࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱ࠾ࠥ࠭ῖ") + (str(e) or bstack1lll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡣࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡥࡩࠥࡩ࡯࡯ࡸࡨࡶࡹ࡫ࡤࠡࡶࡲࠤࡸࡺࡲࡪࡰࡪࠦῗ")))
        finally:
            self.timer = None
    def bstack1lllll1ll1ll_opy_(self):
        if self.timer:
            self.bstack1lllll1llll1_opy_()
        self.bstack1lllll1lllll_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1llllll111ll_opy_:
                threading.Thread(target=self.bstack1llllll1111l_opy_).start()
    def bstack1llllll1111l_opy_(self, source = bstack1lll1_opy_ (u"ࠫࠬῘ")):
        with self.lock:
            if not self.queue:
                self.bstack1lllll1ll1ll_opy_()
                return
            data = self.queue[:self.bstack1llllll111ll_opy_]
            del self.queue[:self.bstack1llllll111ll_opy_]
        self.handler(data)
        if source != bstack1lll1_opy_ (u"ࠬࡹࡨࡶࡶࡧࡳࡼࡴࠧῙ"):
            self.bstack1lllll1ll1ll_opy_()
    def shutdown(self):
        self.bstack1lllll1llll1_opy_()
        while self.queue:
            self.bstack1llllll1111l_opy_(source=bstack1lll1_opy_ (u"࠭ࡳࡩࡷࡷࡨࡴࡽ࡮ࠨῚ"))