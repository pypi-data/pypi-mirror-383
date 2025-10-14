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
from bstack_utils.bstack11lll11l_opy_ import get_logger
logger = get_logger(__name__)
class bstack11ll11l1111_opy_(object):
  bstack1l1l1l11_opy_ = os.path.join(os.path.expanduser(bstack1lll1_opy_ (u"ࠪࢂࠬᝤ")), bstack1lll1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᝥ"))
  bstack11ll111lll1_opy_ = os.path.join(bstack1l1l1l11_opy_, bstack1lll1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹ࠮࡫ࡵࡲࡲࠬᝦ"))
  commands_to_wrap = None
  perform_scan = None
  bstack111lll11l_opy_ = None
  bstack1l1l1111l_opy_ = None
  bstack11ll1l1l11l_opy_ = None
  bstack11ll1ll1l11_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack1lll1_opy_ (u"࠭ࡩ࡯ࡵࡷࡥࡳࡩࡥࠨᝧ")):
      cls.instance = super(bstack11ll11l1111_opy_, cls).__new__(cls)
      cls.instance.bstack11ll11l111l_opy_()
    return cls.instance
  def bstack11ll11l111l_opy_(self):
    try:
      with open(self.bstack11ll111lll1_opy_, bstack1lll1_opy_ (u"ࠧࡳࠩᝨ")) as bstack11l1l1lll_opy_:
        bstack11ll11l11l1_opy_ = bstack11l1l1lll_opy_.read()
        data = json.loads(bstack11ll11l11l1_opy_)
        if bstack1lll1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࠪᝩ") in data:
          self.bstack11ll11l1l11_opy_(data[bstack1lll1_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶࠫᝪ")])
        if bstack1lll1_opy_ (u"ࠪࡷࡨࡸࡩࡱࡶࡶࠫᝫ") in data:
          self.bstack1111llll1_opy_(data[bstack1lll1_opy_ (u"ࠫࡸࡩࡲࡪࡲࡷࡷࠬᝬ")])
        if bstack1lll1_opy_ (u"ࠬࡴ࡯࡯ࡄࡖࡸࡦࡩ࡫ࡊࡰࡩࡶࡦࡇ࠱࠲ࡻࡆ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᝭") in data:
          self.bstack11ll111llll_opy_(data[bstack1lll1_opy_ (u"࠭࡮ࡰࡰࡅࡗࡹࡧࡣ࡬ࡋࡱࡪࡷࡧࡁ࠲࠳ࡼࡇ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᝮ")])
    except:
      pass
  def bstack11ll111llll_opy_(self, bstack11ll1ll1l11_opy_):
    if bstack11ll1ll1l11_opy_ != None:
      self.bstack11ll1ll1l11_opy_ = bstack11ll1ll1l11_opy_
  def bstack1111llll1_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts.get(bstack1lll1_opy_ (u"ࠧࡴࡥࡤࡲࠬᝯ"),bstack1lll1_opy_ (u"ࠨࠩᝰ"))
      self.bstack111lll11l_opy_ = scripts.get(bstack1lll1_opy_ (u"ࠩࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࠭᝱"),bstack1lll1_opy_ (u"ࠪࠫᝲ"))
      self.bstack1l1l1111l_opy_ = scripts.get(bstack1lll1_opy_ (u"ࠫ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠨᝳ"),bstack1lll1_opy_ (u"ࠬ࠭᝴"))
      self.bstack11ll1l1l11l_opy_ = scripts.get(bstack1lll1_opy_ (u"࠭ࡳࡢࡸࡨࡖࡪࡹࡵ࡭ࡶࡶࠫ᝵"),bstack1lll1_opy_ (u"ࠧࠨ᝶"))
  def bstack11ll11l1l11_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack11ll111lll1_opy_, bstack1lll1_opy_ (u"ࠨࡹࠪ᝷")) as file:
        json.dump({
          bstack1lll1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡶࠦ᝸"): self.commands_to_wrap,
          bstack1lll1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࡶࠦ᝹"): {
            bstack1lll1_opy_ (u"ࠦࡸࡩࡡ࡯ࠤ᝺"): self.perform_scan,
            bstack1lll1_opy_ (u"ࠧ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠤ᝻"): self.bstack111lll11l_opy_,
            bstack1lll1_opy_ (u"ࠨࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࡖࡹࡲࡳࡡࡳࡻࠥ᝼"): self.bstack1l1l1111l_opy_,
            bstack1lll1_opy_ (u"ࠢࡴࡣࡹࡩࡗ࡫ࡳࡶ࡮ࡷࡷࠧ᝽"): self.bstack11ll1l1l11l_opy_
          },
          bstack1lll1_opy_ (u"ࠣࡰࡲࡲࡇ࡙ࡴࡢࡥ࡮ࡍࡳ࡬ࡲࡢࡃ࠴࠵ࡾࡉࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠧ᝾"): self.bstack11ll1ll1l11_opy_
        }, file)
    except Exception as e:
      logger.error(bstack1lll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡶࡲࡶ࡮ࡴࡧࠡࡥࡲࡱࡲࡧ࡮ࡥࡵ࠽ࠤࢀࢃࠢ᝿").format(e))
      pass
  def bstack1lll1111l1_opy_(self, command_name):
    try:
      return any(command.get(bstack1lll1_opy_ (u"ࠪࡲࡦࡳࡥࠨក")) == command_name for command in self.commands_to_wrap)
    except:
      return False
bstack1111ll11l_opy_ = bstack11ll11l1111_opy_()