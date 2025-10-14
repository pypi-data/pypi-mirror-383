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
from filelock import FileLock
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional
from bstack_utils.bstack11lll11l_opy_ import get_logger
logger = get_logger(__name__)
bstack1lllllllllll_opy_: Dict[str, float] = {}
bstack11111111111_opy_: List = []
bstack1lllllllll11_opy_ = 5
bstack1l111l1ll1_opy_ = os.path.join(os.getcwd(), bstack1lll1_opy_ (u"ࠧ࡭ࡱࡪࠫὤ"), bstack1lll1_opy_ (u"ࠨ࡭ࡨࡽ࠲ࡳࡥࡵࡴ࡬ࡧࡸ࠴ࡪࡴࡱࡱࠫὥ"))
logging.getLogger(bstack1lll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡬ࡰࡥ࡮ࠫὦ")).setLevel(logging.WARNING)
lock = FileLock(bstack1l111l1ll1_opy_+bstack1lll1_opy_ (u"ࠥ࠲ࡱࡵࡣ࡬ࠤὧ"))
class bstack1llllllll1l1_opy_:
    duration: float
    name: str
    startTime: float
    worker: int
    status: bool
    failure: str
    details: Optional[str]
    entryType: str
    platform: Optional[int]
    command: Optional[str]
    hookType: Optional[str]
    cli: Optional[bool]
    def __init__(self, duration: float, name: str, start_time: float, bstack1111111111l_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None, cli: Optional[bool] = False) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack1111111111l_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack1lll1_opy_ (u"ࠦࡲ࡫ࡡࡴࡷࡵࡩࠧὨ")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
        self.cli = cli
class bstack1ll1l1lll1l_opy_:
    global bstack1lllllllllll_opy_
    @staticmethod
    def bstack1ll11lll11l_opy_(key: str):
        bstack1ll11llll1l_opy_ = bstack1ll1l1lll1l_opy_.bstack11ll1l1111l_opy_(key)
        bstack1ll1l1lll1l_opy_.mark(bstack1ll11llll1l_opy_+bstack1lll1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧὩ"))
        return bstack1ll11llll1l_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack1lllllllllll_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack1lll1_opy_ (u"ࠨࡅࡳࡴࡲࡶ࠿ࠦࡻࡾࠤὪ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str] = None, hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack1ll1l1lll1l_opy_.mark(end)
            bstack1ll1l1lll1l_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack1lll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡩ࡯ࠢ࡮ࡩࡾࠦ࡭ࡦࡶࡵ࡭ࡨࡹ࠺ࠡࡽࢀࠦὫ").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack1lllllllllll_opy_ or end not in bstack1lllllllllll_opy_:
                logger.debug(bstack1lll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡪࡰࠣࡷࡹࡧࡲࡵࠢ࡮ࡩࡾࠦࡷࡪࡶ࡫ࠤࡻࡧ࡬ࡶࡧࠣࡿࢂࠦ࡯ࡳࠢࡨࡲࡩࠦ࡫ࡦࡻࠣࡻ࡮ࡺࡨࠡࡸࡤࡰࡺ࡫ࠠࡼࡿࠥὬ").format(start,end))
                return
            duration: float = bstack1lllllllllll_opy_[end] - bstack1lllllllllll_opy_[start]
            bstack1llllllllll1_opy_ = os.environ.get(bstack1lll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡌࡒࡆࡘ࡙ࡠࡋࡖࡣࡗ࡛ࡎࡏࡋࡑࡋࠧὭ"), bstack1lll1_opy_ (u"ࠥࡪࡦࡲࡳࡦࠤὮ")).lower() == bstack1lll1_opy_ (u"ࠦࡹࡸࡵࡦࠤὯ")
            bstack111111111l1_opy_: bstack1llllllll1l1_opy_ = bstack1llllllll1l1_opy_(duration, label, bstack1lllllllllll_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack1lll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠧὰ"), 0), command, test_name, hook_type, bstack1llllllllll1_opy_)
            del bstack1lllllllllll_opy_[start]
            del bstack1lllllllllll_opy_[end]
            bstack1ll1l1lll1l_opy_.bstack1llllllll11l_opy_(bstack111111111l1_opy_)
        except Exception as e:
            logger.debug(bstack1lll1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡲ࡫ࡡࡴࡷࡵ࡭ࡳ࡭ࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷ࠿ࠦࡻࡾࠤά").format(e))
    @staticmethod
    def bstack1llllllll11l_opy_(bstack111111111l1_opy_):
        os.makedirs(os.path.dirname(bstack1l111l1ll1_opy_)) if not os.path.exists(os.path.dirname(bstack1l111l1ll1_opy_)) else None
        bstack1ll1l1lll1l_opy_.bstack1lllllllll1l_opy_()
        try:
            with lock:
                with open(bstack1l111l1ll1_opy_, bstack1lll1_opy_ (u"ࠢࡳ࠭ࠥὲ"), encoding=bstack1lll1_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢέ")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack111111111l1_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError as bstack1llllllll1ll_opy_:
            logger.debug(bstack1lll1_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠ࡯ࡱࡷࠤ࡫ࡵࡵ࡯ࡦࠣࡿࢂࠨὴ").format(bstack1llllllll1ll_opy_))
            with lock:
                with open(bstack1l111l1ll1_opy_, bstack1lll1_opy_ (u"ࠥࡻࠧή"), encoding=bstack1lll1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥὶ")) as file:
                    data = [bstack111111111l1_opy_.__dict__]
                    json.dump(data, file, indent=4)
        except Exception as e:
            logger.debug(bstack1lll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷࠥࡧࡰࡱࡧࡱࡨࠥࢁࡽࠣί").format(str(e)))
        finally:
            if os.path.exists(bstack1l111l1ll1_opy_+bstack1lll1_opy_ (u"ࠨ࠮࡭ࡱࡦ࡯ࠧὸ")):
                os.remove(bstack1l111l1ll1_opy_+bstack1lll1_opy_ (u"ࠢ࠯࡮ࡲࡧࡰࠨό"))
    @staticmethod
    def bstack1lllllllll1l_opy_():
        attempt = 0
        while (attempt < bstack1lllllllll11_opy_):
            attempt += 1
            if os.path.exists(bstack1l111l1ll1_opy_+bstack1lll1_opy_ (u"ࠣ࠰࡯ࡳࡨࡱࠢὺ")):
                time.sleep(0.5)
            else:
                break
    @staticmethod
    def bstack11ll1l1111l_opy_(label: str) -> str:
        try:
            return bstack1lll1_opy_ (u"ࠤࡾࢁ࠿ࢁࡽࠣύ").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack1lll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨὼ").format(e))