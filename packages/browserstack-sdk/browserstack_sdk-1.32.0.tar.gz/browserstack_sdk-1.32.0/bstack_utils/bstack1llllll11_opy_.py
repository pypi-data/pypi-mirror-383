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
from collections import deque
from bstack_utils.constants import *
class bstack11ll1l111l_opy_:
    def __init__(self):
        self._1111111lll1_opy_ = deque()
        self._11111111l11_opy_ = {}
        self._1111111l1l1_opy_ = False
        self._lock = threading.RLock()
    def bstack1111111llll_opy_(self, test_name, bstack111111111ll_opy_):
        with self._lock:
            bstack1111111l111_opy_ = self._11111111l11_opy_.get(test_name, {})
            return bstack1111111l111_opy_.get(bstack111111111ll_opy_, 0)
    def bstack1111111l1ll_opy_(self, test_name, bstack111111111ll_opy_):
        with self._lock:
            bstack11111111ll1_opy_ = self.bstack1111111llll_opy_(test_name, bstack111111111ll_opy_)
            self.bstack1111111ll1l_opy_(test_name, bstack111111111ll_opy_)
            return bstack11111111ll1_opy_
    def bstack1111111ll1l_opy_(self, test_name, bstack111111111ll_opy_):
        with self._lock:
            if test_name not in self._11111111l11_opy_:
                self._11111111l11_opy_[test_name] = {}
            bstack1111111l111_opy_ = self._11111111l11_opy_[test_name]
            bstack11111111ll1_opy_ = bstack1111111l111_opy_.get(bstack111111111ll_opy_, 0)
            bstack1111111l111_opy_[bstack111111111ll_opy_] = bstack11111111ll1_opy_ + 1
    def bstack11lll1l111_opy_(self, bstack1111111l11l_opy_, bstack1111111ll11_opy_):
        bstack11111111lll_opy_ = self.bstack1111111l1ll_opy_(bstack1111111l11l_opy_, bstack1111111ll11_opy_)
        event_name = bstack11l1ll1l1ll_opy_[bstack1111111ll11_opy_]
        bstack1l1l11ll1l1_opy_ = bstack1lll1_opy_ (u"ࠨࡻࡾ࠯ࡾࢁ࠲ࢁࡽࠣὣ").format(bstack1111111l11l_opy_, event_name, bstack11111111lll_opy_)
        with self._lock:
            self._1111111lll1_opy_.append(bstack1l1l11ll1l1_opy_)
    def bstack1ll1lll111_opy_(self):
        with self._lock:
            return len(self._1111111lll1_opy_) == 0
    def bstack1l1lll11l1_opy_(self):
        with self._lock:
            if self._1111111lll1_opy_:
                bstack11111111l1l_opy_ = self._1111111lll1_opy_.popleft()
                return bstack11111111l1l_opy_
            return None
    def capturing(self):
        with self._lock:
            return self._1111111l1l1_opy_
    def bstack11111lll_opy_(self):
        with self._lock:
            self._1111111l1l1_opy_ = True
    def bstack1l11llll11_opy_(self):
        with self._lock:
            self._1111111l1l1_opy_ = False