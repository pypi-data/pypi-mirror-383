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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111llll1ll1_opy_
from browserstack_sdk.bstack111ll1l1_opy_ import bstack11ll1l111_opy_
def _111ll1111ll_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111ll111lll_opy_:
    def __init__(self, handler):
        self._111ll111ll1_opy_ = {}
        self._111ll111l11_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack11ll1l111_opy_.version()
        if bstack111llll1ll1_opy_(pytest_version, bstack1lll1_opy_ (u"ࠣ࠺࠱࠵࠳࠷ࠢᶐ")) >= 0:
            self._111ll111ll1_opy_[bstack1lll1_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶑ")] = Module._register_setup_function_fixture
            self._111ll111ll1_opy_[bstack1lll1_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᶒ")] = Module._register_setup_module_fixture
            self._111ll111ll1_opy_[bstack1lll1_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᶓ")] = Class._register_setup_class_fixture
            self._111ll111ll1_opy_[bstack1lll1_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᶔ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111ll11111l_opy_(bstack1lll1_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᶕ"))
            Module._register_setup_module_fixture = self.bstack111ll11111l_opy_(bstack1lll1_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᶖ"))
            Class._register_setup_class_fixture = self.bstack111ll11111l_opy_(bstack1lll1_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᶗ"))
            Class._register_setup_method_fixture = self.bstack111ll11111l_opy_(bstack1lll1_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᶘ"))
        else:
            self._111ll111ll1_opy_[bstack1lll1_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᶙ")] = Module._inject_setup_function_fixture
            self._111ll111ll1_opy_[bstack1lll1_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶚ")] = Module._inject_setup_module_fixture
            self._111ll111ll1_opy_[bstack1lll1_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶛ")] = Class._inject_setup_class_fixture
            self._111ll111ll1_opy_[bstack1lll1_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᶜ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111ll11111l_opy_(bstack1lll1_opy_ (u"ࠧࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᶝ"))
            Module._inject_setup_module_fixture = self.bstack111ll11111l_opy_(bstack1lll1_opy_ (u"ࠨ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᶞ"))
            Class._inject_setup_class_fixture = self.bstack111ll11111l_opy_(bstack1lll1_opy_ (u"ࠩࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᶟ"))
            Class._inject_setup_method_fixture = self.bstack111ll11111l_opy_(bstack1lll1_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᶠ"))
    def bstack111l1lllll1_opy_(self, bstack111l1llllll_opy_, hook_type):
        bstack111ll111111_opy_ = id(bstack111l1llllll_opy_.__class__)
        if (bstack111ll111111_opy_, hook_type) in self._111ll111l11_opy_:
            return
        meth = getattr(bstack111l1llllll_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111ll111l11_opy_[(bstack111ll111111_opy_, hook_type)] = meth
            setattr(bstack111l1llllll_opy_, hook_type, self.bstack111l1lll111_opy_(hook_type, bstack111ll111111_opy_))
    def bstack111l1lll1ll_opy_(self, instance, bstack111ll111l1l_opy_):
        if bstack111ll111l1l_opy_ == bstack1lll1_opy_ (u"ࠦ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠢᶡ"):
            self.bstack111l1lllll1_opy_(instance.obj, bstack1lll1_opy_ (u"ࠧࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠨᶢ"))
            self.bstack111l1lllll1_opy_(instance.obj, bstack1lll1_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࠥᶣ"))
        if bstack111ll111l1l_opy_ == bstack1lll1_opy_ (u"ࠢ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠣᶤ"):
            self.bstack111l1lllll1_opy_(instance.obj, bstack1lll1_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟࡮ࡱࡧࡹࡱ࡫ࠢᶥ"))
            self.bstack111l1lllll1_opy_(instance.obj, bstack1lll1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲࡵࡤࡶ࡮ࡨࠦᶦ"))
        if bstack111ll111l1l_opy_ == bstack1lll1_opy_ (u"ࠥࡧࡱࡧࡳࡴࡡࡩ࡭ࡽࡺࡵࡳࡧࠥᶧ"):
            self.bstack111l1lllll1_opy_(instance.obj, bstack1lll1_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡧࡱࡧࡳࡴࠤᶨ"))
            self.bstack111l1lllll1_opy_(instance.obj, bstack1lll1_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡤ࡮ࡤࡷࡸࠨᶩ"))
        if bstack111ll111l1l_opy_ == bstack1lll1_opy_ (u"ࠨ࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠢᶪ"):
            self.bstack111l1lllll1_opy_(instance.obj, bstack1lll1_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩࠨᶫ"))
            self.bstack111l1lllll1_opy_(instance.obj, bstack1lll1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠥᶬ"))
    @staticmethod
    def bstack111l1lll11l_opy_(hook_type, func, args):
        if hook_type in [bstack1lll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠨᶭ"), bstack1lll1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳࡥࡵࡪࡲࡨࠬᶮ")]:
            _111ll1111ll_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111l1lll111_opy_(self, hook_type, bstack111ll111111_opy_):
        def bstack111ll1111l1_opy_(arg=None):
            self.handler(hook_type, bstack1lll1_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫᶯ"))
            result = None
            try:
                bstack1llll1l1lll_opy_ = self._111ll111l11_opy_[(bstack111ll111111_opy_, hook_type)]
                self.bstack111l1lll11l_opy_(hook_type, bstack1llll1l1lll_opy_, (arg,))
                result = Result(result=bstack1lll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᶰ"))
            except Exception as e:
                result = Result(result=bstack1lll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᶱ"), exception=e)
                self.handler(hook_type, bstack1lll1_opy_ (u"ࠧࡢࡨࡷࡩࡷ࠭ᶲ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1lll1_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧᶳ"), result)
        def bstack111l1llll1l_opy_(this, arg=None):
            self.handler(hook_type, bstack1lll1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩᶴ"))
            result = None
            exception = None
            try:
                self.bstack111l1lll11l_opy_(hook_type, self._111ll111l11_opy_[hook_type], (this, arg))
                result = Result(result=bstack1lll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᶵ"))
            except Exception as e:
                result = Result(result=bstack1lll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᶶ"), exception=e)
                self.handler(hook_type, bstack1lll1_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫᶷ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1lll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬᶸ"), result)
        if hook_type in [bstack1lll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭ᶹ"), bstack1lll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪᶺ")]:
            return bstack111l1llll1l_opy_
        return bstack111ll1111l1_opy_
    def bstack111ll11111l_opy_(self, bstack111ll111l1l_opy_):
        def bstack111l1lll1l1_opy_(this, *args, **kwargs):
            self.bstack111l1lll1ll_opy_(this, bstack111ll111l1l_opy_)
            self._111ll111ll1_opy_[bstack111ll111l1l_opy_](this, *args, **kwargs)
        return bstack111l1lll1l1_opy_