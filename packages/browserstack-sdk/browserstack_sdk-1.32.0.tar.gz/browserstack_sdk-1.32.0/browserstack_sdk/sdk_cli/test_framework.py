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
from enum import Enum
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack111111111l_opy_ import bstack1llllllll1l_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import bstack1llll1ll1l1_opy_, bstack1lllll1ll11_opy_
class bstack1ll1llll1ll_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack1lll1_opy_ (u"࡚ࠧࡥࡴࡶࡋࡳࡴࡱࡓࡵࡣࡷࡩ࠳ࢁࡽࠣᗉ").format(self.name)
class bstack1lll1l11111_opy_(Enum):
    NONE = 0
    BEFORE_ALL = 1
    LOG = 2
    SETUP_FIXTURE = 3
    INIT_TEST = 4
    BEFORE_EACH = 5
    AFTER_EACH = 6
    TEST = 7
    STEP = 8
    LOG_REPORT = 9
    AFTER_ALL = 10
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack1lll1_opy_ (u"ࠨࡔࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡢࡶࡨ࠲ࢀࢃࠢᗊ").format(self.name)
class bstack1lll11l11l1_opy_(bstack1llll1ll1l1_opy_):
    bstack1ll11l11111_opy_: List[str]
    bstack1l1111llll1_opy_: Dict[str, str]
    state: bstack1lll1l11111_opy_
    bstack1lllll1lll1_opy_: datetime
    bstack1lllllll111_opy_: datetime
    def __init__(
        self,
        context: bstack1lllll1ll11_opy_,
        bstack1ll11l11111_opy_: List[str],
        bstack1l1111llll1_opy_: Dict[str, str],
        state=bstack1lll1l11111_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1ll11l11111_opy_ = bstack1ll11l11111_opy_
        self.bstack1l1111llll1_opy_ = bstack1l1111llll1_opy_
        self.state = state
        self.bstack1lllll1lll1_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1lllllll111_opy_ = datetime.now(tz=timezone.utc)
    def bstack1llll1ll111_opy_(self, bstack1llllll1ll1_opy_: bstack1lll1l11111_opy_):
        bstack1llll1l1ll1_opy_ = bstack1lll1l11111_opy_(bstack1llllll1ll1_opy_).name
        if not bstack1llll1l1ll1_opy_:
            return False
        if bstack1llllll1ll1_opy_ == self.state:
            return False
        self.state = bstack1llllll1ll1_opy_
        self.bstack1lllllll111_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack11llllll11l_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1ll1lllll1l_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
    fileName: str = None
    bstack1l1l1l1l1ll_opy_: int = None
    bstack1l1l1ll1l11_opy_: str = None
    bstack111111l_opy_: str = None
    bstack1ll1111111_opy_: str = None
    bstack1l1l1lllll1_opy_: str = None
    bstack11llllll1ll_opy_: str = None
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1ll11ll1l1l_opy_ = bstack1lll1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡻࡵࡪࡦࠥᗋ")
    bstack11llll1ll11_opy_ = bstack1lll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡩࡥࠤᗌ")
    bstack1ll11l1ll1l_opy_ = bstack1lll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟࡯ࡣࡰࡩࠧᗍ")
    bstack11lllllll1l_opy_ = bstack1lll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡰࡪࡥࡰࡢࡶ࡫ࠦᗎ")
    bstack1l111l1llll_opy_ = bstack1lll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡷࡥ࡬ࡹࠢᗏ")
    bstack1l1l1111111_opy_ = bstack1lll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡶࡪࡹࡵ࡭ࡶࠥᗐ")
    bstack1l1ll11lll1_opy_ = bstack1lll1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷ࡫ࡳࡶ࡮ࡷࡣࡦࡺࠢᗑ")
    bstack1l1ll111lll_opy_ = bstack1lll1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠤᗒ")
    bstack1l1ll1111l1_opy_ = bstack1lll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡥ࡯ࡦࡨࡨࡤࡧࡴࠣᗓ")
    bstack1l11111l11l_opy_ = bstack1lll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤᗔ")
    bstack1ll1111llll_opy_ = bstack1lll1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࠤᗕ")
    bstack1l1lll11ll1_opy_ = bstack1lll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳࠨᗖ")
    bstack1l11111ll1l_opy_ = bstack1lll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡧࡴࡪࡥࠣᗗ")
    bstack1l1l11ll1ll_opy_ = bstack1lll1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡷ࡫ࡲࡶࡰࡢࡲࡦࡳࡥࠣᗘ")
    bstack1ll11111ll1_opy_ = bstack1lll1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࠣᗙ")
    bstack1l11lll1lll_opy_ = bstack1lll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡢ࡫࡯ࡹࡷ࡫ࠢᗚ")
    bstack1l111lll11l_opy_ = bstack1lll1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪࠨᗛ")
    bstack11lllll1lll_opy_ = bstack1lll1_opy_ (u"ࠥࡸࡪࡹࡴࡠ࡮ࡲ࡫ࡸࠨᗜ")
    bstack1l11111l1ll_opy_ = bstack1lll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡰࡩࡹࡧࠢᗝ")
    bstack11llll1l1ll_opy_ = bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡷࡨࡵࡰࡦࡵࠪᗞ")
    bstack1l11l11l11l_opy_ = bstack1lll1_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡥࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡱࡥࡲ࡫ࠢᗟ")
    bstack1l111l1lll1_opy_ = bstack1lll1_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥᗠ")
    bstack1l111llll11_opy_ = bstack1lll1_opy_ (u"ࠣࡧࡹࡩࡳࡺ࡟ࡦࡰࡧࡩࡩࡥࡡࡵࠤᗡ")
    bstack1l111l111ll_opy_ = bstack1lll1_opy_ (u"ࠤ࡫ࡳࡴࡱ࡟ࡪࡦࠥᗢ")
    bstack1l111l11lll_opy_ = bstack1lll1_opy_ (u"ࠥ࡬ࡴࡵ࡫ࡠࡴࡨࡷࡺࡲࡴࠣᗣ")
    bstack11llll1ll1l_opy_ = bstack1lll1_opy_ (u"ࠦ࡭ࡵ࡯࡬ࡡ࡯ࡳ࡬ࡹࠢᗤ")
    bstack1l11111l1l1_opy_ = bstack1lll1_opy_ (u"ࠧ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠣᗥ")
    bstack1l111ll11l1_opy_ = bstack1lll1_opy_ (u"ࠨ࡬ࡰࡩࡶࠦᗦ")
    bstack11lllllll11_opy_ = bstack1lll1_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࡟࡮ࡧࡷࡥࡩࡧࡴࡢࠤᗧ")
    bstack1l1111l111l_opy_ = bstack1lll1_opy_ (u"ࠣࡲࡨࡲࡩ࡯࡮ࡨࠤᗨ")
    bstack1l1111l11ll_opy_ = bstack1lll1_opy_ (u"ࠤࡳࡩࡳࡪࡩ࡯ࡩࠥᗩ")
    bstack1l1ll11ll11_opy_ = bstack1lll1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࠧᗪ")
    bstack1l1l1l11l1l_opy_ = bstack1lll1_opy_ (u"࡙ࠦࡋࡓࡕࡡࡏࡓࡌࠨᗫ")
    bstack1l1l1l1llll_opy_ = bstack1lll1_opy_ (u"࡚ࠧࡅࡔࡖࡢࡅ࡙࡚ࡁࡄࡊࡐࡉࡓ࡚ࠢᗬ")
    bstack1lllll1l11l_opy_: Dict[str, bstack1lll11l11l1_opy_] = dict()
    bstack11llll111l1_opy_: Dict[str, List[Callable]] = dict()
    bstack1ll11l11111_opy_: List[str]
    bstack1l1111llll1_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1ll11l11111_opy_: List[str],
        bstack1l1111llll1_opy_: Dict[str, str],
        bstack111111111l_opy_: bstack1llllllll1l_opy_
    ):
        self.bstack1ll11l11111_opy_ = bstack1ll11l11111_opy_
        self.bstack1l1111llll1_opy_ = bstack1l1111llll1_opy_
        self.bstack111111111l_opy_ = bstack111111111l_opy_
    def track_event(
        self,
        context: bstack11llllll11l_opy_,
        test_framework_state: bstack1lll1l11111_opy_,
        test_hook_state: bstack1ll1llll1ll_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack1lll1_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࡂࢁࡽࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࢂࠦࡡࡳࡩࡶࡁࢀࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࡼࡿࠥᗭ").format(test_framework_state,test_hook_state,args,kwargs))
    def bstack1l1111ll11l_opy_(
        self,
        instance: bstack1lll11l11l1_opy_,
        bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11l1111l1_opy_ = TestFramework.bstack1l111lllll1_opy_(bstack1lllll1l111_opy_)
        if not bstack1l11l1111l1_opy_ in TestFramework.bstack11llll111l1_opy_:
            return
        self.logger.debug(bstack1lll1_opy_ (u"ࠢࡪࡰࡹࡳࡰ࡯࡮ࡨࠢࡾࢁࠥࡩࡡ࡭࡮ࡥࡥࡨࡱࡳࠣᗮ").format(len(TestFramework.bstack11llll111l1_opy_[bstack1l11l1111l1_opy_])))
        for callback in TestFramework.bstack11llll111l1_opy_[bstack1l11l1111l1_opy_]:
            try:
                callback(self, instance, bstack1lllll1l111_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack1lll1_opy_ (u"ࠣࡧࡵࡶࡴࡸࠠࡪࡰࡹࡳࡰ࡯࡮ࡨࠢࡦࡥࡱࡲࡢࡢࡥ࡮࠾ࠥࢁࡽࠣᗯ").format(e))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1l1l1ll1lll_opy_(self):
        return
    @abc.abstractmethod
    def bstack1l1ll1ll11l_opy_(self, instance, bstack1lllll1l111_opy_):
        return
    @abc.abstractmethod
    def bstack1l1l1lll111_opy_(self, instance, bstack1lllll1l111_opy_):
        return
    @staticmethod
    def bstack1llll1l111l_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack1llll1ll1l1_opy_.create_context(target)
        instance = TestFramework.bstack1lllll1l11l_opy_.get(ctx.id, None)
        if instance and instance.bstack1llllll1l1l_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1l1l1l11l_opy_(reverse=True) -> List[bstack1lll11l11l1_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1lllll1l11l_opy_.values(),
            ),
            key=lambda t: t.bstack1lllll1lll1_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1lllll11111_opy_(ctx: bstack1lllll1ll11_opy_, reverse=True) -> List[bstack1lll11l11l1_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1lllll1l11l_opy_.values(),
            ),
            key=lambda t: t.bstack1lllll1lll1_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1llll1l1111_opy_(instance: bstack1lll11l11l1_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1llll1ll1ll_opy_(instance: bstack1lll11l11l1_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1llll1ll111_opy_(instance: bstack1lll11l11l1_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack1lll1_opy_ (u"ࠤࡶࡩࡹࡥࡳࡵࡣࡷࡩ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽࢀࠤࡰ࡫ࡹ࠾ࡽࢀࠤࡻࡧ࡬ࡶࡧࡀࡿࢂࠨᗰ").format(instance.ref(),key,value))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l111lll111_opy_(instance: bstack1lll11l11l1_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack1lll1_opy_ (u"ࠥࡷࡪࡺ࡟ࡴࡶࡤࡸࡪࡥࡥ࡯ࡶࡵ࡭ࡪࡹ࠺ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿࢂࠦࡥ࡯ࡶࡵ࡭ࡪࡹ࠽ࡼࡿࠥᗱ").format(instance.ref(),entries,))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack11lll1ll1ll_opy_(instance: bstack1lll1l11111_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack1lll1_opy_ (u"ࠦࡺࡶࡤࡢࡶࡨࡣࡸࡺࡡࡵࡧ࠽ࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࡻࡾࠢ࡮ࡩࡾࡃࡻࡾࠢࡹࡥࡱࡻࡥ࠾ࡽࢀࠦᗲ").format(instance.ref(),key,value))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack1llll1l111l_opy_(target, strict)
        return TestFramework.bstack1llll1ll1ll_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack1llll1l111l_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l111l1l1ll_opy_(instance: bstack1lll11l11l1_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack1l111ll111l_opy_(instance: bstack1lll11l11l1_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1l111lllll1_opy_(bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_]):
        return bstack1lll1_opy_ (u"ࠧࡀࠢᗳ").join((bstack1lll1l11111_opy_(bstack1lllll1l111_opy_[0]).name, bstack1ll1llll1ll_opy_(bstack1lllll1l111_opy_[1]).name))
    @staticmethod
    def bstack1ll11lllll1_opy_(bstack1lllll1l111_opy_: Tuple[bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_], callback: Callable):
        bstack1l11l1111l1_opy_ = TestFramework.bstack1l111lllll1_opy_(bstack1lllll1l111_opy_)
        TestFramework.logger.debug(bstack1lll1_opy_ (u"ࠨࡳࡦࡶࡢ࡬ࡴࡵ࡫ࡠࡥࡤࡰࡱࡨࡡࡤ࡭࠽ࠤ࡭ࡵ࡯࡬ࡡࡵࡩ࡬࡯ࡳࡵࡴࡼࡣࡰ࡫ࡹ࠾ࡽࢀࠦᗴ").format(bstack1l11l1111l1_opy_))
        if not bstack1l11l1111l1_opy_ in TestFramework.bstack11llll111l1_opy_:
            TestFramework.bstack11llll111l1_opy_[bstack1l11l1111l1_opy_] = []
        TestFramework.bstack11llll111l1_opy_[bstack1l11l1111l1_opy_].append(callback)
    @staticmethod
    def bstack1l1l1llll11_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack1lll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡹ࡯࡮ࡴࠤᗵ"):
            return klass.__qualname__
        return module + bstack1lll1_opy_ (u"ࠣ࠰ࠥᗶ") + klass.__qualname__
    @staticmethod
    def bstack1l1ll1l1lll_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}