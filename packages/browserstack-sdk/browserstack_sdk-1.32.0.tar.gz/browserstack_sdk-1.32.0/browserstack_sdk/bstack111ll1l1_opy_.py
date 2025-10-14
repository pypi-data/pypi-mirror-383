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
import multiprocessing
import os
import json
from time import sleep
import time
import bstack_utils.accessibility as bstack1l11llll1l_opy_
import subprocess
import re
from browserstack_sdk.bstack1ll11l11ll_opy_ import *
from bstack_utils.config import Config
from bstack_utils.messages import bstack1l11111l_opy_
from bstack_utils.bstack1llll1ll11_opy_ import bstack111llll111_opy_
from bstack_utils.constants import bstack111111l1l1_opy_
from bstack_utils.bstack1l111ll1ll_opy_ import bstack11lll1ll_opy_
class bstack11ll1l111_opy_:
    bstack11111l1lll_opy_ = bstack1lll1_opy_ (u"ࡳࠩ࠿ࡑࡴࡪࡵ࡭ࡧࠣࠬࡠࡤ࠾࡞࠭ࠬࡂࠬၔ")  # bstack11111ll11l_opy_ lines bstack111111_opy_ <Module path/to/bstack1111lll1l_opy_.py> in pytest --collect-bstack11111lllll_opy_ output
    def __init__(self, args, logger, bstack1111l111l1_opy_, bstack11111l1l11_opy_):
        self.args = args
        self.logger = logger
        self.bstack1111l111l1_opy_ = bstack1111l111l1_opy_
        self.bstack11111l1l11_opy_ = bstack11111l1l11_opy_
        self._prepareconfig = None
        self.Config = None
        self.runner = None
        self.bstack1l1l11lll_opy_ = []
        self.bstack11111lll11_opy_ = []
        self.bstack111llll1l_opy_ = []
        self.bstack111111l1ll_opy_ = self.bstack1l1l1l11l1_opy_()
        self.bstack1ll1l11l1l_opy_ = -1
    def bstack11ll11l11l_opy_(self, bstack1111l11ll1_opy_):
        self.parse_args()
        self.bstack111111l11l_opy_()
        self.bstack1111l11l11_opy_(bstack1111l11ll1_opy_)
        self.bstack111111llll_opy_()
    def bstack11lll1l1ll_opy_(self):
        bstack1l111ll1ll_opy_ = bstack11lll1ll_opy_.bstack1111l11l1_opy_(self.bstack1111l111l1_opy_, self.logger)
        if bstack1l111ll1ll_opy_ is None:
            self.logger.warn(bstack1lll1_opy_ (u"ࠤࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢ࡫ࡥࡳࡪ࡬ࡦࡴࠣ࡭ࡸࠦ࡮ࡰࡶࠣ࡭ࡳ࡯ࡴࡪࡣ࡯࡭ࡿ࡫ࡤ࠯ࠢࡖ࡯࡮ࡶࡰࡪࡰࡪࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧၕ"))
            return
        bstack1111l1l11l_opy_ = False
        bstack1l111ll1ll_opy_.bstack1111l111ll_opy_(bstack1lll1_opy_ (u"ࠥࡩࡳࡧࡢ࡭ࡧࡧࠦၖ"), bstack1l111ll1ll_opy_.bstack11lll11l11_opy_())
        start_time = time.time()
        if bstack1l111ll1ll_opy_.bstack11lll11l11_opy_():
            test_files = self.bstack1111l11lll_opy_()
            bstack1111l1l11l_opy_ = True
            bstack11111ll1ll_opy_ = bstack1l111ll1ll_opy_.bstack1111l11l1l_opy_(test_files)
            if bstack11111ll1ll_opy_:
                self.bstack1l1l11lll_opy_ = [os.path.normpath(item).replace(bstack1lll1_opy_ (u"ࠫࡡࡢࠧၗ"), bstack1lll1_opy_ (u"ࠬ࠵ࠧၘ")) for item in bstack11111ll1ll_opy_]
                self.__111111ll1l_opy_()
                bstack1l111ll1ll_opy_.bstack11111ll1l1_opy_(bstack1111l1l11l_opy_)
                self.logger.info(bstack1lll1_opy_ (u"ࠨࡔࡦࡵࡷࡷࠥࡸࡥࡰࡴࡧࡩࡷ࡫ࡤࠡࡷࡶ࡭ࡳ࡭ࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠦၙ").format(self.bstack1l1l11lll_opy_))
            else:
                self.logger.info(bstack1lll1_opy_ (u"ࠢࡏࡱࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹࠠࡸࡧࡵࡩࠥࡸࡥࡰࡴࡧࡩࡷ࡫ࡤࠡࡤࡼࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧၚ"))
        bstack1l111ll1ll_opy_.bstack1111l111ll_opy_(bstack1lll1_opy_ (u"ࠣࡶ࡬ࡱࡪ࡚ࡡ࡬ࡧࡱࡘࡴࡇࡰࡱ࡮ࡼࠦၛ"), int((time.time() - start_time) * 1000)) # bstack1111l11111_opy_ to bstack11111llll1_opy_
    def __111111ll1l_opy_(self):
        bstack1lll1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡆࡰࡴࠣࡩࡦࡩࡨࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࠤ࡮ࡴࠠࡴࡧ࡯ࡪ࠳ࡹࡰࡦࡥࡢࡪ࡮ࡲࡥࡴ࠮ࠣࡧࡴࡲ࡬ࡦࡥࡷࠤࡦࡲ࡬ࠡࡰࡲࡨࡪ࡯ࡤࡴࠢࡸࡷ࡮ࡴࡧࠡࡲࡼࡸࡪࡹࡴࠡ࠯࠰ࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡴࡴ࡬ࡺࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨၜ")
        bstack11111lll1l_opy_ = []
        for bstack1111lll1l_opy_ in self.bstack1l1l11lll_opy_:
            bstack11111l1l1l_opy_ = [bstack1lll1_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶࠥၝ"), bstack1111lll1l_opy_, bstack1lll1_opy_ (u"ࠦ࠲࠳ࡣࡰ࡮࡯ࡩࡨࡺ࠭ࡰࡰ࡯ࡽࠧၞ"), bstack1lll1_opy_ (u"ࠧ࠳ࡱࠣၟ")]
            result = subprocess.run(bstack11111l1l1l_opy_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.logger.error(bstack1111l1l1ll_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡮ࡨࠢࡱࡳࡩ࡫ࡩࡥࡵࠣࡪࡴࡸࠠࡼࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࢁ࠿ࠦࡻࡳࡧࡶࡹࡱࡺ࠮ࡴࡶࡧࡩࡷࡸࡽࠣၠ"))
                continue
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith(bstack1lll1_opy_ (u"ࠢ࠽ࠤၡ")) and bstack1lll1_opy_ (u"ࠣ࠼࠽ࠦၢ") in line:
                    bstack11111lll1l_opy_.append(line)
        os.environ[bstack1lll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡑࡕࡇࡍࡋࡓࡕࡔࡄࡘࡊࡊ࡟ࡔࡇࡏࡉࡈ࡚ࡏࡓࡕࠪၣ")] = json.dumps(bstack11111lll1l_opy_)
    @staticmethod
    def version():
        import pytest
        return pytest.__version__
    @staticmethod
    def bstack11111l1ll1_opy_():
        import importlib
        if getattr(importlib, bstack1lll1_opy_ (u"ࠪࡪ࡮ࡴࡤࡠ࡮ࡲࡥࡩ࡫ࡲࠨၤ"), False):
            bstack111111lll1_opy_ = importlib.find_loader(bstack1lll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭ၥ"))
        else:
            bstack111111lll1_opy_ = importlib.util.find_spec(bstack1lll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠧၦ"))
    def bstack11111ll111_opy_(self, arg):
        if arg in self.args:
            i = self.args.index(arg)
            self.args.pop(i + 1)
            self.args.pop(i)
    def parse_args(self):
        self.bstack1ll1l11l1l_opy_ = -1
        if self.bstack11111l1l11_opy_ and bstack1lll1_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ၧ") in self.bstack1111l111l1_opy_:
            self.bstack1ll1l11l1l_opy_ = int(self.bstack1111l111l1_opy_[bstack1lll1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧၨ")])
        try:
            bstack11111l111l_opy_ = [bstack1lll1_opy_ (u"ࠨ࠯࠰ࡨࡷ࡯ࡶࡦࡴࠪၩ"), bstack1lll1_opy_ (u"ࠩ࠰࠱ࡵࡲࡵࡨ࡫ࡱࡷࠬၪ"), bstack1lll1_opy_ (u"ࠪ࠱ࡵ࠭ၫ")]
            if self.bstack1ll1l11l1l_opy_ >= 0:
                bstack11111l111l_opy_.extend([bstack1lll1_opy_ (u"ࠫ࠲࠳࡮ࡶ࡯ࡳࡶࡴࡩࡥࡴࡵࡨࡷࠬၬ"), bstack1lll1_opy_ (u"ࠬ࠳࡮ࠨၭ")])
            for arg in bstack11111l111l_opy_:
                self.bstack11111ll111_opy_(arg)
        except Exception as exc:
            self.logger.error(str(exc))
    def get_args(self):
        return self.args
    def bstack111111l11l_opy_(self):
        bstack11111lll11_opy_ = [os.path.normpath(item) for item in self.args]
        self.bstack11111lll11_opy_ = bstack11111lll11_opy_
        return self.bstack11111lll11_opy_
    def bstack1l11ll1111_opy_(self):
        try:
            from _pytest.config import _prepareconfig
            from _pytest.config import Config
            from _pytest import runner
            self.bstack11111l1ll1_opy_()
            self._prepareconfig = _prepareconfig
            self.Config = Config
            self.runner = runner
        except Exception as e:
            self.logger.warn(e, bstack1l11111l_opy_)
    def bstack1111l11l11_opy_(self, bstack1111l11ll1_opy_):
        bstack1l1111ll1_opy_ = Config.bstack1111l11l1_opy_()
        if bstack1111l11ll1_opy_:
            self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"࠭࠭࠮ࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪၮ"))
            self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"ࠧࡕࡴࡸࡩࠬၯ"))
        if bstack1l1111ll1_opy_.bstack111111ll11_opy_():
            self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"ࠨ࠯࠰ࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧၰ"))
            self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"ࠩࡗࡶࡺ࡫ࠧၱ"))
        self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"ࠪ࠱ࡵ࠭ၲ"))
        self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡳࡰࡺ࡭ࡩ࡯ࠩၳ"))
        self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"ࠬ࠳࠭ࡥࡴ࡬ࡺࡪࡸࠧၴ"))
        self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ၵ"))
        if self.bstack1ll1l11l1l_opy_ > 1:
            self.bstack11111lll11_opy_.append(bstack1lll1_opy_ (u"ࠧ࠮ࡰࠪၶ"))
            self.bstack11111lll11_opy_.append(str(self.bstack1ll1l11l1l_opy_))
    def bstack111111llll_opy_(self):
        if bstack111llll111_opy_.bstack1ll11l1ll1_opy_(self.bstack1111l111l1_opy_):
             self.bstack11111lll11_opy_ += [
                bstack111111l1l1_opy_.get(bstack1lll1_opy_ (u"ࠨࡴࡨࡶࡺࡴࠧၷ")), str(bstack111llll111_opy_.bstack1l11l111ll_opy_(self.bstack1111l111l1_opy_)),
                bstack111111l1l1_opy_.get(bstack1lll1_opy_ (u"ࠩࡧࡩࡱࡧࡹࠨၸ")), str(bstack111111l1l1_opy_.get(bstack1lll1_opy_ (u"ࠪࡶࡪࡸࡵ࡯࠯ࡧࡩࡱࡧࡹࠨၹ")))
            ]
    def bstack11111l11l1_opy_(self):
        bstack111llll1l_opy_ = []
        for spec in self.bstack1l1l11lll_opy_:
            bstack1lll11ll1l_opy_ = [spec]
            bstack1lll11ll1l_opy_ += self.bstack11111lll11_opy_
            bstack111llll1l_opy_.append(bstack1lll11ll1l_opy_)
        self.bstack111llll1l_opy_ = bstack111llll1l_opy_
        return bstack111llll1l_opy_
    def bstack1l1l1l11l1_opy_(self):
        try:
            from pytest_bdd import reporting
            self.bstack111111l1ll_opy_ = True
            return True
        except Exception as e:
            self.bstack111111l1ll_opy_ = False
        return self.bstack111111l1ll_opy_
    def bstack1l11ll111l_opy_(self):
        bstack1lll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡍࡥࡵࠢࡷ࡬ࡪࠦࡣࡰࡷࡱࡸࠥࡵࡦࠡࡶࡨࡷࡹࡹࠠࡸ࡫ࡷ࡬ࡴࡻࡴࠡࡴࡸࡲࡳ࡯࡮ࡨࠢࡷ࡬ࡪࡳࠠࡶࡵ࡬ࡲ࡬ࠦࡰࡺࡶࡨࡷࡹ࠭ࡳࠡ࠯࠰ࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡴࡴ࡬ࡺࠢࡩࡰࡦ࡭࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡭ࡳࡺ࠺ࠡࡖ࡫ࡩࠥࡺ࡯ࡵࡣ࡯ࠤࡳࡻ࡭ࡣࡧࡵࠤࡴ࡬ࠠࡵࡧࡶࡸࡸࠦࡣࡰ࡮࡯ࡩࡨࡺࡥࡥ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢၺ")
        try:
            self.logger.info(bstack1lll1_opy_ (u"ࠧࡉ࡯࡭࡮ࡨࡧࡹ࡯࡮ࡨࠢࡷࡩࡸࡺࡳࠡࡷࡶ࡭ࡳ࡭ࠠࡱࡻࡷࡩࡸࡺࠠ࠮࠯ࡦࡳࡱࡲࡥࡤࡶ࠰ࡳࡳࡲࡹࠣၻ"))
            bstack11111l1l1l_opy_ = [bstack1lll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨၼ"), *self.bstack11111lll11_opy_, bstack1lll1_opy_ (u"ࠢ࠮࠯ࡦࡳࡱࡲࡥࡤࡶ࠰ࡳࡳࡲࡹࠣၽ")]
            result = subprocess.run(bstack11111l1l1l_opy_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.logger.error(bstack1lll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡣࡰ࡮࡯ࡩࡨࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࡴ࠼ࠣࡿࢂࠨၾ").format(result.stderr))
                return 0
            test_count = result.stdout.count(bstack1lll1_opy_ (u"ࠤ࠿ࡊࡺࡴࡣࡵ࡫ࡲࡲࠥࠨၿ"))
            self.logger.info(bstack1lll1_opy_ (u"ࠥࡘࡴࡺࡡ࡭ࠢࡷࡩࡸࡺࡳࠡࡥࡲࡰࡱ࡫ࡣࡵࡧࡧ࠾ࠥࢁࡽࠣႀ").format(test_count))
            return test_count
        except Exception as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡩ࡯ࡶࡰࡷ࠾ࠥࢁࡽࠣႁ").format(e))
            return 0
    def bstack1ll11l1ll_opy_(self, bstack11111l11ll_opy_, bstack11ll11l11l_opy_):
        bstack11ll11l11l_opy_[bstack1lll1_opy_ (u"ࠬࡉࡏࡏࡈࡌࡋࠬႂ")] = self.bstack1111l111l1_opy_
        multiprocessing.set_start_method(bstack1lll1_opy_ (u"࠭ࡳࡱࡣࡺࡲࠬႃ"))
        bstack11llll1ll1_opy_ = []
        manager = multiprocessing.Manager()
        bstack1111l1111l_opy_ = manager.list()
        if bstack1lll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪႄ") in self.bstack1111l111l1_opy_:
            for index, platform in enumerate(self.bstack1111l111l1_opy_[bstack1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫႅ")]):
                bstack11llll1ll1_opy_.append(multiprocessing.Process(name=str(index),
                                                            target=bstack11111l11ll_opy_,
                                                            args=(self.bstack11111lll11_opy_, bstack11ll11l11l_opy_, bstack1111l1111l_opy_)))
            bstack11111l1111_opy_ = len(self.bstack1111l111l1_opy_[bstack1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬႆ")])
        else:
            bstack11llll1ll1_opy_.append(multiprocessing.Process(name=str(0),
                                                        target=bstack11111l11ll_opy_,
                                                        args=(self.bstack11111lll11_opy_, bstack11ll11l11l_opy_, bstack1111l1111l_opy_)))
            bstack11111l1111_opy_ = 1
        i = 0
        for t in bstack11llll1ll1_opy_:
            os.environ[bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪႇ")] = str(i)
            if bstack1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧႈ") in self.bstack1111l111l1_opy_:
                os.environ[bstack1lll1_opy_ (u"ࠬࡉࡕࡓࡔࡈࡒ࡙ࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡆࡄࡘࡆ࠭ႉ")] = json.dumps(self.bstack1111l111l1_opy_[bstack1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩႊ")][i % bstack11111l1111_opy_])
            i += 1
            t.start()
        for t in bstack11llll1ll1_opy_:
            t.join()
        return list(bstack1111l1111l_opy_)
    @staticmethod
    def bstack11lllll1_opy_(driver, bstack1111l1l1l1_opy_, logger, item=None, wait=False):
        item = item or getattr(threading.current_thread(), bstack1lll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫႋ"), None)
        if item and getattr(item, bstack1lll1_opy_ (u"ࠨࡡࡤ࠵࠶ࡿ࡟ࡵࡧࡶࡸࡤࡩࡡࡴࡧࠪႌ"), None) and not getattr(item, bstack1lll1_opy_ (u"ࠩࡢࡥ࠶࠷ࡹࡠࡵࡷࡳࡵࡥࡤࡰࡰࡨႍࠫ"), False):
            logger.info(
                bstack1lll1_opy_ (u"ࠥࡅࡺࡺ࡯࡮ࡣࡷࡩࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥࠡࡧࡻࡩࡨࡻࡴࡪࡱࡱࠤ࡭ࡧࡳࠡࡧࡱࡨࡪࡪ࠮ࠡࡒࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡷࡩࡸࡺࡩ࡯ࡩࠣ࡭ࡸࠦࡵ࡯ࡦࡨࡶࡼࡧࡹ࠯ࠤႎ"))
            bstack1111l1l111_opy_ = item.cls.__name__ if not item.cls is None else None
            bstack1l11llll1l_opy_.bstack11l1l1l1_opy_(driver, item.name, item.path)
            item._a11y_stop_done = True
            if wait:
                sleep(2)
    def bstack1111l11lll_opy_(self):
        bstack1lll1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦ࡬ࡪࡵࡷࠤࡴ࡬ࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡹࡵࠠࡣࡧࠣࡩࡽ࡫ࡣࡶࡶࡨࡨࠥࡨࡹࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡷ࡬ࡪࠦ࡯ࡶࡶࡳࡹࡹࠦ࡯ࡧࠢࡳࡽࡹ࡫ࡳࡵࠢ࠰࠱ࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡵ࡮࡭ࡻ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡔ࡯ࡵࡧ࠽ࠤ࡙࡮ࡥࠡࡴࡨ࡫ࡪࡾࠠࡱࡣࡷࡸࡪࡸ࡮ࠡࡷࡶࡩࡩࠦࡨࡦࡴࡨࠤࡩ࡫ࡰࡦࡰࡧࡷࠥࡵ࡮ࠡࡲࡼࡸࡪࡹࡴࠨࡵࠣࡳࡺࡺࡰࡶࡶࠣࡪࡴࡸ࡭ࡢࡶࠣࡪࡴࡸࠠ࠽ࡏࡲࡨࡺࡲࡥࠡ࠰࠱࠲ࡃࠦ࡬ࡪࡰࡨࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥႏ")
        try:
            bstack11111l1l1l_opy_ = [bstack1lll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧ႐"), *self.bstack11111lll11_opy_, bstack1lll1_opy_ (u"ࠨ࠭࠮ࡥࡲࡰࡱ࡫ࡣࡵ࠯ࡲࡲࡱࡿࠢ႑")]
            result = subprocess.run(bstack11111l1l1l_opy_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.logger.error(bstack1lll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡮ࡨࠢࡷࡩࡸࡺࡳࠡࡨ࡬ࡰࡪࡀࠠࡼࡿࠥ႒").format(result.stderr))
                return []
            file_names = set(re.findall(self.bstack11111l1lll_opy_, result.stdout))
            file_names = sorted(file_names)
            return list(file_names)
        except Exception as e:
            self.logger.error(bstack1111l1l1ll_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡴࡲ࡬ࡦࡥࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶ࠾ࠥࢁࡥࡾࠤ႓"))
            return []