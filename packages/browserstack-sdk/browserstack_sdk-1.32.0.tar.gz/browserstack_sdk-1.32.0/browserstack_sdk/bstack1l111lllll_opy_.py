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
import json
import multiprocessing
import os
from bstack_utils.config import Config
class bstack11l1111ll1_opy_():
  def __init__(self, args, logger, bstack1111l111l1_opy_, bstack11111l1l11_opy_, bstack1111111lll_opy_):
    self.args = args
    self.logger = logger
    self.bstack1111l111l1_opy_ = bstack1111l111l1_opy_
    self.bstack11111l1l11_opy_ = bstack11111l1l11_opy_
    self.bstack1111111lll_opy_ = bstack1111111lll_opy_
  def bstack1ll11l1ll_opy_(self, bstack11111l11ll_opy_, bstack11ll11l11l_opy_, bstack111111l111_opy_=False):
    bstack11llll1ll1_opy_ = []
    manager = multiprocessing.Manager()
    bstack1111l1111l_opy_ = manager.list()
    bstack1l1111ll1_opy_ = Config.bstack1111l11l1_opy_()
    if bstack111111l111_opy_:
      for index, platform in enumerate(self.bstack1111l111l1_opy_[bstack1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ႔")]):
        if index == 0:
          bstack11ll11l11l_opy_[bstack1lll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭႕")] = self.args
        bstack11llll1ll1_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack11111l11ll_opy_,
                                                    args=(bstack11ll11l11l_opy_, bstack1111l1111l_opy_)))
    else:
      for index, platform in enumerate(self.bstack1111l111l1_opy_[bstack1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ႖")]):
        bstack11llll1ll1_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack11111l11ll_opy_,
                                                    args=(bstack11ll11l11l_opy_, bstack1111l1111l_opy_)))
    i = 0
    for t in bstack11llll1ll1_opy_:
      try:
        if bstack1l1111ll1_opy_.get_property(bstack1lll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭႗")):
          os.environ[bstack1lll1_opy_ (u"࠭ࡃࡖࡔࡕࡉࡓ࡚࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡇࡅ࡙ࡇࠧ႘")] = json.dumps(self.bstack1111l111l1_opy_[bstack1lll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ႙")][i % self.bstack1111111lll_opy_])
      except Exception as e:
        self.logger.debug(bstack1lll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡳࡵࡱࡵ࡭ࡳ࡭ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡪࡺࡡࡪ࡮ࡶ࠾ࠥࢁࡽࠣႚ").format(str(e)))
      i += 1
      t.start()
    for t in bstack11llll1ll1_opy_:
      t.join()
    return list(bstack1111l1111l_opy_)