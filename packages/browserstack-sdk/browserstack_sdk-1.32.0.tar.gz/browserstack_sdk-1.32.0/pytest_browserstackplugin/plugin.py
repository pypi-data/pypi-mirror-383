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
import atexit
import datetime
import inspect
import logging
import signal
import threading
from uuid import uuid4
from bstack_utils.measure import bstack1l1ll11l11_opy_
from bstack_utils.percy_sdk import PercySDK
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack11ll11111l_opy_, bstack1111111ll_opy_, update, bstack1lllll1l11_opy_,
                                       bstack1ll111llll_opy_, bstack11l11l1ll1_opy_, bstack1l111l11_opy_, bstack11llll11_opy_,
                                       bstack11l1l1ll11_opy_, bstack1l1l11111l_opy_, bstack11l111ll_opy_,
                                       bstack11l1llll1l_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack11lll1ll1_opy_)
from browserstack_sdk.bstack111ll1l1_opy_ import bstack11ll1l111_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack11lll11l_opy_
from bstack_utils.capture import bstack111l1lll1l_opy_
from bstack_utils.config import Config
from bstack_utils.percy import *
from bstack_utils.constants import bstack1ll1l1lll_opy_, bstack1lll1l1ll1_opy_, bstack1l1111l1l_opy_, \
    bstack1l111l11l_opy_
from bstack_utils.helper import bstack1ll1l1l1l1_opy_, bstack11l11ll1111_opy_, bstack111l111111_opy_, bstack1l1llllll1_opy_, bstack1l1l1ll11l1_opy_, bstack1111l11l_opy_, \
    bstack11l11ll1lll_opy_, \
    bstack11l1111llll_opy_, bstack11llll111l_opy_, bstack11ll1ll1l1_opy_, bstack111llll1lll_opy_, bstack11lllll111_opy_, Notset, \
    bstack1lllll1l1l_opy_, bstack111lllll11l_opy_, bstack11l111ll1l1_opy_, Result, bstack11l11l11ll1_opy_, bstack11l11111ll1_opy_, error_handler, \
    bstack1llllll11l_opy_, bstack1111l1ll1_opy_, bstack1llll1ll_opy_, bstack111lll1l1l1_opy_
from bstack_utils.bstack111l1llll11_opy_ import bstack111ll111lll_opy_
from bstack_utils.messages import bstack111l11ll_opy_, bstack1111l1111_opy_, bstack1lllllll1_opy_, bstack11111111_opy_, bstack1l11111l_opy_, \
    bstack1l1111111_opy_, bstack11l111l1ll_opy_, bstack1l1l1ll1ll_opy_, bstack11111lll1_opy_, bstack1ll111l11l_opy_, \
    bstack1l1l1llll_opy_, bstack11lll11lll_opy_, bstack11111l111_opy_
from bstack_utils.proxy import bstack11l11lllll_opy_, bstack11llll111_opy_
from bstack_utils.bstack11llll11ll_opy_ import bstack1llllll11l11_opy_, bstack1llllll1ll1l_opy_, bstack1llllll1l1ll_opy_, bstack1llllll1l11l_opy_, \
    bstack1llllll1l111_opy_, bstack1lllllll1111_opy_, bstack1llllll1lll1_opy_, bstack1l1l1ll1l1_opy_, bstack1llllll11l1l_opy_
from bstack_utils.bstack1l111l11l1_opy_ import bstack1lll11llll_opy_
from bstack_utils.bstack1lll1llll1_opy_ import bstack11ll1l1l_opy_, bstack1l111lll1l_opy_, bstack11lll1lll_opy_, \
    bstack11l1111111_opy_, bstack1ll1lll1_opy_
from bstack_utils.bstack111ll111ll_opy_ import bstack111ll1l111_opy_
from bstack_utils.bstack111lll11ll_opy_ import bstack1ll1ll1l1l_opy_
import bstack_utils.accessibility as bstack1l11llll1l_opy_
from bstack_utils.bstack111ll1ll11_opy_ import bstack1lll11l1l_opy_
from bstack_utils.bstack1111ll11l_opy_ import bstack1111ll11l_opy_
from bstack_utils.bstack1llll1ll11_opy_ import bstack111llll111_opy_
from browserstack_sdk.__init__ import bstack11l1ll1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1lll1l1ll11_opy_
from browserstack_sdk.sdk_cli.bstack1l1ll1l111_opy_ import bstack1l1ll1l111_opy_, bstack1l1ll1ll11_opy_, bstack1l11l11l1_opy_
from browserstack_sdk.sdk_cli.test_framework import bstack11llllll11l_opy_, bstack1lll1l11111_opy_, bstack1ll1llll1ll_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack1l1ll1l111_opy_ import bstack1l1ll1l111_opy_, bstack1l1ll1ll11_opy_, bstack1l11l11l1_opy_
bstack1ll1lllll_opy_ = None
bstack1l111lll1_opy_ = None
bstack1ll1l1111_opy_ = None
bstack1111l111l_opy_ = None
bstack1111ll1l_opy_ = None
bstack1ll111l11_opy_ = None
bstack1l1111111l_opy_ = None
bstack1ll11l1lll_opy_ = None
bstack1llllll111_opy_ = None
bstack11l11l11_opy_ = None
bstack1l1l1l1l1l_opy_ = None
bstack11ll1lll1_opy_ = None
bstack111ll1ll1_opy_ = None
bstack111ll1l1l_opy_ = bstack1lll1_opy_ (u"ࠧࠨ≊")
CONFIG = {}
bstack1lll1ll1l_opy_ = False
bstack1lll1lll_opy_ = bstack1lll1_opy_ (u"ࠨࠩ≋")
bstack1l1l11111_opy_ = bstack1lll1_opy_ (u"ࠩࠪ≌")
bstack1l11lllll1_opy_ = False
bstack111lllll1l_opy_ = []
bstack11ll1l11l_opy_ = bstack1ll1l1lll_opy_
bstack1lll1l1llll1_opy_ = bstack1lll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ≍")
bstack11l11lll1l_opy_ = {}
bstack1l11111l1_opy_ = None
bstack1111l1l1_opy_ = False
logger = bstack11lll11l_opy_.get_logger(__name__, bstack11ll1l11l_opy_)
store = {
    bstack1lll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ≎"): []
}
bstack1lll1lll1ll1_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_1111llllll_opy_ = {}
current_test_uuid = None
cli_context = bstack11llllll11l_opy_(
    test_framework_name=bstack11lll1l11l_opy_[bstack1lll1_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘ࠲ࡈࡄࡅࠩ≏")] if bstack11lllll111_opy_() else bstack11lll1l11l_opy_[bstack1lll1_opy_ (u"࠭ࡐ࡚ࡖࡈࡗ࡙࠭≐")],
    test_framework_version=pytest.__version__,
    platform_index=-1,
)
def bstack1l11l1l1ll_opy_(page, bstack11l11l1111_opy_):
    try:
        page.evaluate(bstack1lll1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ≑"),
                      bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠬ≒") + json.dumps(
                          bstack11l11l1111_opy_) + bstack1lll1_opy_ (u"ࠤࢀࢁࠧ≓"))
    except Exception as e:
        print(bstack1lll1_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥࢁࡽࠣ≔"), e)
def bstack1l1l11l1l_opy_(page, message, level):
    try:
        page.evaluate(bstack1lll1_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧ≕"), bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪ≖") + json.dumps(
            message) + bstack1lll1_opy_ (u"࠭ࠬࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠩ≗") + json.dumps(level) + bstack1lll1_opy_ (u"ࠧࡾࡿࠪ≘"))
    except Exception as e:
        print(bstack1lll1_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡦࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠡࡽࢀࠦ≙"), e)
def pytest_configure(config):
    global bstack1lll1lll_opy_
    global CONFIG
    bstack1l1111ll1_opy_ = Config.bstack1111l11l1_opy_()
    config.args = bstack1ll1ll1l1l_opy_.bstack1lll1llll1ll_opy_(config.args)
    bstack1l1111ll1_opy_.bstack11ll11l11_opy_(bstack1llll1ll_opy_(config.getoption(bstack1lll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸ࠭≚"))))
    try:
        bstack11lll11l_opy_.bstack111l1ll11ll_opy_(config.inipath, config.rootpath)
    except:
        pass
    if cli.is_running():
        bstack1l1ll1l111_opy_.invoke(bstack1l1ll1ll11_opy_.CONNECT, bstack1l11l11l1_opy_())
        cli_context.platform_index = int(os.environ.get(bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ≛"), bstack1lll1_opy_ (u"ࠫ࠵࠭≜")))
        config = json.loads(os.environ.get(bstack1lll1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡕࡎࡇࡋࡊࠦ≝"), bstack1lll1_opy_ (u"ࠨࡻࡾࠤ≞")))
        cli.bstack1llll11ll11_opy_(bstack11ll1ll1l1_opy_(bstack1lll1lll_opy_, CONFIG), cli_context.platform_index, bstack1lllll1l11_opy_)
    if cli.bstack1lll1l1ll1l_opy_(bstack1lll1l1ll11_opy_):
        cli.bstack1ll1ll1ll1l_opy_()
        logger.debug(bstack1lll1_opy_ (u"ࠢࡄࡎࡌࠤ࡮ࡹࠠࡢࡥࡷ࡭ࡻ࡫ࠠࡧࡱࡵࠤࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࡂࠨ≟") + str(cli_context.platform_index) + bstack1lll1_opy_ (u"ࠣࠤ≠"))
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.BEFORE_ALL, bstack1ll1llll1ll_opy_.PRE, config)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    when = getattr(call, bstack1lll1_opy_ (u"ࠤࡺ࡬ࡪࡴࠢ≡"), None)
    if cli.is_running() and when == bstack1lll1_opy_ (u"ࠥࡧࡦࡲ࡬ࠣ≢"):
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.LOG_REPORT, bstack1ll1llll1ll_opy_.PRE, item, call)
    outcome = yield
    if when == bstack1lll1_opy_ (u"ࠦࡨࡧ࡬࡭ࠤ≣"):
        report = outcome.get_result()
        passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1lll1_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢ≤")))
        if not passed:
            config = json.loads(os.environ.get(bstack1lll1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡉࡏࡏࡈࡌࡋࠧ≥"), bstack1lll1_opy_ (u"ࠢࡼࡿࠥ≦")))
            if bstack111llll111_opy_.bstack1ll11l1ll1_opy_(config):
                bstack1111l111111_opy_ = bstack111llll111_opy_.bstack1l11l111ll_opy_(config)
                if item.execution_count > bstack1111l111111_opy_:
                    print(bstack1lll1_opy_ (u"ࠨࡖࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࠦࡡࡧࡶࡨࡶࠥࡸࡥࡵࡴ࡬ࡩࡸࡀࠠࠨ≧"), report.nodeid, os.environ.get(bstack1lll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ≨")))
                    bstack111llll111_opy_.bstack1111lll1lll_opy_(report.nodeid)
            else:
                print(bstack1lll1_opy_ (u"ࠪࡘࡪࡹࡴࠡࡨࡤ࡭ࡱ࡫ࡤ࠻ࠢࠪ≩"), report.nodeid, os.environ.get(bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ≪")))
                bstack111llll111_opy_.bstack1111lll1lll_opy_(report.nodeid)
        else:
            print(bstack1lll1_opy_ (u"࡚ࠬࡥࡴࡶࠣࡴࡦࡹࡳࡦࡦ࠽ࠤࠬ≫"), report.nodeid, os.environ.get(bstack1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ≬")))
    if cli.is_running():
        if when == bstack1lll1_opy_ (u"ࠢࡴࡧࡷࡹࡵࠨ≭"):
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.BEFORE_EACH, bstack1ll1llll1ll_opy_.POST, item, call, outcome)
        elif when == bstack1lll1_opy_ (u"ࠣࡥࡤࡰࡱࠨ≮"):
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.LOG_REPORT, bstack1ll1llll1ll_opy_.POST, item, call, outcome)
        elif when == bstack1lll1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࠦ≯"):
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.AFTER_EACH, bstack1ll1llll1ll_opy_.POST, item, call, outcome)
        return # skip all existing operations
    skipSessionName = item.config.getoption(bstack1lll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ≰"))
    plugins = item.config.getoption(bstack1lll1_opy_ (u"ࠦࡵࡲࡵࡨ࡫ࡱࡷࠧ≱"))
    report = outcome.get_result()
    os.environ[bstack1lll1_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࡤ࡚ࡅࡔࡖࡢࡒࡆࡓࡅࠨ≲")] = report.nodeid
    bstack1lll1l1ll1l1_opy_(item, call, report)
    if bstack1lll1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡵࡲࡵࡨ࡫ࡱࠦ≳") not in plugins or bstack11lllll111_opy_():
        return
    summary = []
    driver = getattr(item, bstack1lll1_opy_ (u"ࠢࡠࡦࡵ࡭ࡻ࡫ࡲࠣ≴"), None)
    page = getattr(item, bstack1lll1_opy_ (u"ࠣࡡࡳࡥ࡬࡫ࠢ≵"), None)
    try:
        if (driver == None or driver.session_id == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None or cli.is_running()):
        bstack1lll1lll1l1l_opy_(item, report, summary, skipSessionName)
    if (page is not None):
        bstack1lll1l1lll1l_opy_(item, report, summary, skipSessionName)
def bstack1lll1lll1l1l_opy_(item, report, summary, skipSessionName):
    if report.when == bstack1lll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ≶") and report.skipped:
        bstack1llllll11l1l_opy_(report)
    if report.when in [bstack1lll1_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤ≷"), bstack1lll1_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨ≸")]:
        return
    if not bstack1l1l1ll11l1_opy_():
        return
    try:
        if ((str(skipSessionName).lower() != bstack1lll1_opy_ (u"ࠬࡺࡲࡶࡧࠪ≹")) and (not cli.is_running())) and item._driver.session_id:
            item._driver.execute_script(
                bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠣࠫ≺") + json.dumps(
                    report.nodeid) + bstack1lll1_opy_ (u"ࠧࡾࡿࠪ≻"))
        os.environ[bstack1lll1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫ≼")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack1lll1_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠ࡮ࡣࡵ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨ࠾ࠥࢁ࠰ࡾࠤ≽").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1lll1_opy_ (u"ࠥࡻࡦࡹࡸࡧࡣ࡬ࡰࠧ≾")))
    bstack1lll1l1ll_opy_ = bstack1lll1_opy_ (u"ࠦࠧ≿")
    bstack1llllll11l1l_opy_(report)
    if not passed:
        try:
            bstack1lll1l1ll_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1lll1_opy_ (u"ࠧ࡝ࡁࡓࡐࡌࡒࡌࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡨࡪࡺࡥࡳ࡯࡬ࡲࡪࠦࡦࡢ࡫࡯ࡹࡷ࡫ࠠࡳࡧࡤࡷࡴࡴ࠺ࠡࡽ࠳ࢁࠧ⊀").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack1lll1l1ll_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack1lll1_opy_ (u"ࠨࡷࡢࡵࡻࡪࡦ࡯࡬ࠣ⊁")))
        bstack1lll1l1ll_opy_ = bstack1lll1_opy_ (u"ࠢࠣ⊂")
        if not passed:
            try:
                bstack1lll1l1ll_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1lll1_opy_ (u"࡙ࠣࡄࡖࡓࡏࡎࡈ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡤࡦࡶࡨࡶࡲ࡯࡮ࡦࠢࡩࡥ࡮ࡲࡵࡳࡧࠣࡶࡪࡧࡳࡰࡰ࠽ࠤࢀ࠶ࡽࠣ⊃").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack1lll1l1ll_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡯࡮ࡧࡱࠥ࠰ࠥࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡪࡡࡵࡣࠥ࠾ࠥ࠭⊄")
                    + json.dumps(bstack1lll1_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠤࠦ⊅"))
                    + bstack1lll1_opy_ (u"ࠦࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃࠢ⊆")
                )
            else:
                item._driver.execute_script(
                    bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨ࡬ࡦࡸࡨࡰࠧࡀࠠࠣࡧࡵࡶࡴࡸࠢ࠭ࠢ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡧࡥࡹࡧࠢ࠻ࠢࠪ⊇")
                    + json.dumps(str(bstack1lll1l1ll_opy_))
                    + bstack1lll1_opy_ (u"ࠨ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾࠤ⊈")
                )
        except Exception as e:
            summary.append(bstack1lll1_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡧ࡮࡯ࡱࡷࡥࡹ࡫࠺ࠡࡽ࠳ࢁࠧ⊉").format(e))
def bstack1lll1ll1l11l_opy_(test_name, error_message):
    try:
        bstack1lll1l1lll11_opy_ = []
        bstack1ll11l111_opy_ = os.environ.get(bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨ⊊"), bstack1lll1_opy_ (u"ࠩ࠳ࠫ⊋"))
        bstack1llll1l111_opy_ = {bstack1lll1_opy_ (u"ࠪࡲࡦࡳࡥࠨ⊌"): test_name, bstack1lll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ⊍"): error_message, bstack1lll1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫ⊎"): bstack1ll11l111_opy_}
        bstack1lll1ll1lll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1lll1_opy_ (u"࠭ࡰࡸࡡࡳࡽࡹ࡫ࡳࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫ⊏"))
        if os.path.exists(bstack1lll1ll1lll1_opy_):
            with open(bstack1lll1ll1lll1_opy_) as f:
                bstack1lll1l1lll11_opy_ = json.load(f)
        bstack1lll1l1lll11_opy_.append(bstack1llll1l111_opy_)
        with open(bstack1lll1ll1lll1_opy_, bstack1lll1_opy_ (u"ࠧࡸࠩ⊐")) as f:
            json.dump(bstack1lll1l1lll11_opy_, f)
    except Exception as e:
        logger.debug(bstack1lll1_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡴࡪࡸࡳࡪࡵࡷ࡭ࡳ࡭ࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡵࡿࡴࡦࡵࡷࠤࡪࡸࡲࡰࡴࡶ࠾ࠥ࠭⊑") + str(e))
def bstack1lll1l1lll1l_opy_(item, report, summary, skipSessionName):
    if report.when in [bstack1lll1_opy_ (u"ࠤࡶࡩࡹࡻࡰࠣ⊒"), bstack1lll1_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧ⊓")]:
        return
    if (str(skipSessionName).lower() != bstack1lll1_opy_ (u"ࠫࡹࡸࡵࡦࠩ⊔")):
        bstack1l11l1l1ll_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1lll1_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢ⊕")))
    bstack1lll1l1ll_opy_ = bstack1lll1_opy_ (u"ࠨࠢ⊖")
    bstack1llllll11l1l_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack1lll1l1ll_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1lll1_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡵࡩࡦࡹ࡯࡯࠼ࠣࡿ࠵ࢃࠢ⊗").format(e)
                )
        try:
            if passed:
                bstack1ll1lll1_opy_(getattr(item, bstack1lll1_opy_ (u"ࠨࡡࡳࡥ࡬࡫ࠧ⊘"), None), bstack1lll1_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ⊙"))
            else:
                error_message = bstack1lll1_opy_ (u"ࠪࠫ⊚")
                if bstack1lll1l1ll_opy_:
                    bstack1l1l11l1l_opy_(item._page, str(bstack1lll1l1ll_opy_), bstack1lll1_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥ⊛"))
                    bstack1ll1lll1_opy_(getattr(item, bstack1lll1_opy_ (u"ࠬࡥࡰࡢࡩࡨࠫ⊜"), None), bstack1lll1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ⊝"), str(bstack1lll1l1ll_opy_))
                    error_message = str(bstack1lll1l1ll_opy_)
                else:
                    bstack1ll1lll1_opy_(getattr(item, bstack1lll1_opy_ (u"ࠧࡠࡲࡤ࡫ࡪ࠭⊞"), None), bstack1lll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ⊟"))
                bstack1lll1ll1l11l_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack1lll1_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡶࡲࡧࡥࡹ࡫ࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳ࠻ࠢࡾ࠴ࢂࠨ⊠").format(e))
def pytest_addoption(parser):
    parser.addoption(bstack1lll1_opy_ (u"ࠥ࠱࠲ࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ⊡"), default=bstack1lll1_opy_ (u"ࠦࡋࡧ࡬ࡴࡧࠥ⊢"), help=bstack1lll1_opy_ (u"ࠧࡇࡵࡵࡱࡰࡥࡹ࡯ࡣࠡࡵࡨࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨࠦ⊣"))
    parser.addoption(bstack1lll1_opy_ (u"ࠨ࠭࠮ࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ⊤"), default=bstack1lll1_opy_ (u"ࠢࡇࡣ࡯ࡷࡪࠨ⊥"), help=bstack1lll1_opy_ (u"ࠣࡃࡸࡸࡴࡳࡡࡵ࡫ࡦࠤࡸ࡫ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫ࠢ⊦"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack1lll1_opy_ (u"ࠤ࠰࠱ࡩࡸࡩࡷࡧࡵࠦ⊧"), action=bstack1lll1_opy_ (u"ࠥࡷࡹࡵࡲࡦࠤ⊨"), default=bstack1lll1_opy_ (u"ࠦࡨ࡮ࡲࡰ࡯ࡨࠦ⊩"),
                         help=bstack1lll1_opy_ (u"ࠧࡊࡲࡪࡸࡨࡶࠥࡺ࡯ࠡࡴࡸࡲࠥࡺࡥࡴࡶࡶࠦ⊪"))
def bstack111lll1111_opy_(log):
    if not (log[bstack1lll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ⊫")] and log[bstack1lll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⊬")].strip()):
        return
    active = bstack111l1ll1ll_opy_()
    log = {
        bstack1lll1_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ⊭"): log[bstack1lll1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ⊮")],
        bstack1lll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭⊯"): bstack111l111111_opy_().isoformat() + bstack1lll1_opy_ (u"ࠫ࡟࠭⊰"),
        bstack1lll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭⊱"): log[bstack1lll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ⊲")],
    }
    if active:
        if active[bstack1lll1_opy_ (u"ࠧࡵࡻࡳࡩࠬ⊳")] == bstack1lll1_opy_ (u"ࠨࡪࡲࡳࡰ࠭⊴"):
            log[bstack1lll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⊵")] = active[bstack1lll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⊶")]
        elif active[bstack1lll1_opy_ (u"ࠫࡹࡿࡰࡦࠩ⊷")] == bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࠪ⊸"):
            log[bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⊹")] = active[bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⊺")]
    bstack1lll11l1l_opy_.bstack11l11111ll_opy_([log])
def bstack111l1ll1ll_opy_():
    if len(store[bstack1lll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ⊻")]) > 0 and store[bstack1lll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⊼")][-1]:
        return {
            bstack1lll1_opy_ (u"ࠪࡸࡾࡶࡥࠨ⊽"): bstack1lll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ⊾"),
            bstack1lll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⊿"): store[bstack1lll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⋀")][-1]
        }
    if store.get(bstack1lll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⋁"), None):
        return {
            bstack1lll1_opy_ (u"ࠨࡶࡼࡴࡪ࠭⋂"): bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺࠧ⋃"),
            bstack1lll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⋄"): store[bstack1lll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ⋅")]
        }
    return None
def pytest_runtest_logstart(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.INIT_TEST, bstack1ll1llll1ll_opy_.PRE, nodeid, location)
def pytest_runtest_logfinish(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.INIT_TEST, bstack1ll1llll1ll_opy_.POST, nodeid, location)
def pytest_runtest_call(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.PRE, item)
        return
    try:
        global CONFIG
        item._1lll1ll11lll_opy_ = True
        bstack1l111ll111_opy_ = bstack1l11llll1l_opy_.bstack1l1l111ll_opy_(bstack11l1111llll_opy_(item.own_markers))
        if not cli.bstack1lll1l1ll1l_opy_(bstack1lll1l1ll11_opy_):
            item._a11y_test_case = bstack1l111ll111_opy_
            if bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ⋆"), None):
                driver = getattr(item, bstack1lll1_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ⋇"), None)
                item._a11y_started = bstack1l11llll1l_opy_.bstack1l1111ll_opy_(driver, bstack1l111ll111_opy_)
        if not bstack1lll11l1l_opy_.on() or bstack1lll1l1llll1_opy_ != bstack1lll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ⋈"):
            return
        global current_test_uuid #, bstack111ll11l1l_opy_
        bstack1111lll1ll_opy_ = {
            bstack1lll1_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⋉"): uuid4().__str__(),
            bstack1lll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⋊"): bstack111l111111_opy_().isoformat() + bstack1lll1_opy_ (u"ࠪ࡞ࠬ⋋")
        }
        current_test_uuid = bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠫࡺࡻࡩࡥࠩ⋌")]
        store[bstack1lll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ⋍")] = bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⋎")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _1111llllll_opy_[item.nodeid] = {**_1111llllll_opy_[item.nodeid], **bstack1111lll1ll_opy_}
        bstack1lll1lll1111_opy_(item, _1111llllll_opy_[item.nodeid], bstack1lll1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ⋏"))
    except Exception as err:
        print(bstack1lll1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡳࡷࡱࡸࡪࡹࡴࡠࡥࡤࡰࡱࡀࠠࡼࡿࠪ⋐"), str(err))
def pytest_runtest_setup(item):
    store[bstack1lll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⋑")] = item
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.BEFORE_EACH, bstack1ll1llll1ll_opy_.PRE, item, bstack1lll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩ⋒"))
    if bstack111llll111_opy_.bstack111l1111lll_opy_():
            bstack1lll1ll11111_opy_ = bstack1lll1_opy_ (u"ࠦࡘࡱࡩࡱࡲ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡦࡹࠠࡵࡪࡨࠤࡦࡨ࡯ࡳࡶࠣࡦࡺ࡯࡬ࡥࠢࡩ࡭ࡱ࡫ࠠࡦࡺ࡬ࡷࡹࡹ࠮ࠣ⋓")
            logger.error(bstack1lll1ll11111_opy_)
            bstack1111lll1ll_opy_ = {
                bstack1lll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ⋔"): uuid4().__str__(),
                bstack1lll1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⋕"): bstack111l111111_opy_().isoformat() + bstack1lll1_opy_ (u"࡛ࠧࠩ⋖"),
                bstack1lll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⋗"): bstack111l111111_opy_().isoformat() + bstack1lll1_opy_ (u"ࠩ࡝ࠫ⋘"),
                bstack1lll1_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⋙"): bstack1lll1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ⋚"),
                bstack1lll1_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬ⋛"): bstack1lll1ll11111_opy_,
                bstack1lll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⋜"): [],
                bstack1lll1_opy_ (u"ࠧࡧ࡫ࡻࡸࡺࡸࡥࡴࠩ⋝"): []
            }
            bstack1lll1lll1111_opy_(item, bstack1111lll1ll_opy_, bstack1lll1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕ࡮࡭ࡵࡶࡥࡥࠩ⋞"))
            pytest.skip(bstack1lll1ll11111_opy_)
            return # skip all existing operations
    global bstack1lll1lll1ll1_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack111llll1lll_opy_():
        atexit.register(bstack11lllllll_opy_)
        if not bstack1lll1lll1ll1_opy_:
            try:
                bstack1lll1ll1ll1l_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack111lll1l1l1_opy_():
                    bstack1lll1ll1ll1l_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack1lll1ll1ll1l_opy_:
                    signal.signal(s, bstack1lll1l1ll11l_opy_)
                bstack1lll1lll1ll1_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack1lll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡷ࡫ࡧࡪࡵࡷࡩࡷࠦࡳࡪࡩࡱࡥࡱࠦࡨࡢࡰࡧࡰࡪࡸࡳ࠻ࠢࠥ⋟") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack1llllll11l11_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack1lll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ⋠")
    try:
        if not bstack1lll11l1l_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack1111lll1ll_opy_ = {
            bstack1lll1_opy_ (u"ࠫࡺࡻࡩࡥࠩ⋡"): uuid,
            bstack1lll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⋢"): bstack111l111111_opy_().isoformat() + bstack1lll1_opy_ (u"࡚࠭ࠨ⋣"),
            bstack1lll1_opy_ (u"ࠧࡵࡻࡳࡩࠬ⋤"): bstack1lll1_opy_ (u"ࠨࡪࡲࡳࡰ࠭⋥"),
            bstack1lll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬ⋦"): bstack1lll1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨ⋧"),
            bstack1lll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧ⋨"): bstack1lll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ⋩")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack1lll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪ⋪")] = item
        store[bstack1lll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ⋫")] = [uuid]
        if not _1111llllll_opy_.get(item.nodeid, None):
            _1111llllll_opy_[item.nodeid] = {bstack1lll1_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⋬"): [], bstack1lll1_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⋭"): []}
        _1111llllll_opy_[item.nodeid][bstack1lll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⋮")].append(bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠫࡺࡻࡩࡥࠩ⋯")])
        _1111llllll_opy_[item.nodeid + bstack1lll1_opy_ (u"ࠬ࠳ࡳࡦࡶࡸࡴࠬ⋰")] = bstack1111lll1ll_opy_
        bstack1lll1lll1lll_opy_(item, bstack1111lll1ll_opy_, bstack1lll1_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ⋱"))
    except Exception as err:
        print(bstack1lll1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡲࡶࡰࡷࡩࡸࡺ࡟ࡴࡧࡷࡹࡵࡀࠠࡼࡿࠪ⋲"), str(err))
def pytest_runtest_teardown(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.POST, item)
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.AFTER_EACH, bstack1ll1llll1ll_opy_.PRE, item, bstack1lll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ⋳"))
        return # skip all existing operations
    try:
        global bstack11l11lll1l_opy_
        bstack1ll11l111_opy_ = 0
        if bstack1l11lllll1_opy_ is True:
            bstack1ll11l111_opy_ = int(os.environ.get(bstack1lll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩ⋴")))
        if bstack11l11111l1_opy_.bstack11l1111ll_opy_() == bstack1lll1_opy_ (u"ࠥࡸࡷࡻࡥࠣ⋵"):
            if bstack11l11111l1_opy_.bstack1l11l1ll11_opy_() == bstack1lll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡥࡤࡷࡪࠨ⋶"):
                bstack1lll1ll1l1ll_opy_ = bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ⋷"), None)
                bstack111l1111_opy_ = bstack1lll1ll1l1ll_opy_ + bstack1lll1_opy_ (u"ࠨ࠭ࡵࡧࡶࡸࡨࡧࡳࡦࠤ⋸")
                driver = getattr(item, bstack1lll1_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨ⋹"), None)
                bstack1llll11l11_opy_ = getattr(item, bstack1lll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭⋺"), None)
                bstack11ll111l_opy_ = getattr(item, bstack1lll1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⋻"), None)
                PercySDK.screenshot(driver, bstack111l1111_opy_, bstack1llll11l11_opy_=bstack1llll11l11_opy_, bstack11ll111l_opy_=bstack11ll111l_opy_, bstack1lll11111_opy_=bstack1ll11l111_opy_)
        if not cli.bstack1lll1l1ll1l_opy_(bstack1lll1l1ll11_opy_):
            if getattr(item, bstack1lll1_opy_ (u"ࠪࡣࡦ࠷࠱ࡺࡡࡶࡸࡦࡸࡴࡦࡦࠪ⋼"), False):
                bstack11ll1l111_opy_.bstack11lllll1_opy_(getattr(item, bstack1lll1_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬ⋽"), None), bstack11l11lll1l_opy_, logger, item)
        if not bstack1lll11l1l_opy_.on():
            return
        bstack1111lll1ll_opy_ = {
            bstack1lll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ⋾"): uuid4().__str__(),
            bstack1lll1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⋿"): bstack111l111111_opy_().isoformat() + bstack1lll1_opy_ (u"࡛ࠧࠩ⌀"),
            bstack1lll1_opy_ (u"ࠨࡶࡼࡴࡪ࠭⌁"): bstack1lll1_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ⌂"),
            bstack1lll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭⌃"): bstack1lll1_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠨ⌄"),
            bstack1lll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠨ⌅"): bstack1lll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨ⌆")
        }
        _1111llllll_opy_[item.nodeid + bstack1lll1_opy_ (u"ࠧ࠮ࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ⌇")] = bstack1111lll1ll_opy_
        bstack1lll1lll1lll_opy_(item, bstack1111lll1ll_opy_, bstack1lll1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⌈"))
    except Exception as err:
        print(bstack1lll1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡴࡸࡲࡹ࡫ࡳࡵࡡࡷࡩࡦࡸࡤࡰࡹࡱ࠾ࠥࢁࡽࠨ⌉"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if bstack1llllll1l11l_opy_(fixturedef.argname):
        store[bstack1lll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡲࡵࡤࡶ࡮ࡨࡣ࡮ࡺࡥ࡮ࠩ⌊")] = request.node
    elif bstack1llllll1l111_opy_(fixturedef.argname):
        store[bstack1lll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡩ࡬ࡢࡵࡶࡣ࡮ࡺࡥ࡮ࠩ⌋")] = request.node
    if not bstack1lll11l1l_opy_.on():
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.SETUP_FIXTURE, bstack1ll1llll1ll_opy_.PRE, fixturedef, request)
        outcome = yield
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.SETUP_FIXTURE, bstack1ll1llll1ll_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    start_time = datetime.datetime.now()
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.SETUP_FIXTURE, bstack1ll1llll1ll_opy_.PRE, fixturedef, request)
    outcome = yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.SETUP_FIXTURE, bstack1ll1llll1ll_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    try:
        fixture = {
            bstack1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⌌"): fixturedef.argname,
            bstack1lll1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⌍"): bstack11l11ll1lll_opy_(outcome),
            bstack1lll1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩ⌎"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack1lll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ⌏")]
        if not _1111llllll_opy_.get(current_test_item.nodeid, None):
            _1111llllll_opy_[current_test_item.nodeid] = {bstack1lll1_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⌐"): []}
        _1111llllll_opy_[current_test_item.nodeid][bstack1lll1_opy_ (u"ࠪࡪ࡮ࡾࡴࡶࡴࡨࡷࠬ⌑")].append(fixture)
    except Exception as err:
        logger.debug(bstack1lll1_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡸ࡫ࡴࡶࡲ࠽ࠤࢀࢃࠧ⌒"), str(err))
if bstack11lllll111_opy_() and bstack1lll11l1l_opy_.on():
    def pytest_bdd_before_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.STEP, bstack1ll1llll1ll_opy_.PRE, request, step)
            return
        try:
            _1111llllll_opy_[request.node.nodeid][bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ⌓")].bstack1ll1l1l1_opy_(id(step))
        except Exception as err:
            print(bstack1lll1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡨࡤࡥࡡࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶ࠺ࠡࡽࢀࠫ⌔"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.STEP, bstack1ll1llll1ll_opy_.POST, request, step, exception)
            return
        try:
            _1111llllll_opy_[request.node.nodeid][bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⌕")].bstack111ll11l11_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack1lll1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡣࡦࡧࡣࡸࡺࡥࡱࡡࡨࡶࡷࡵࡲ࠻ࠢࡾࢁࠬ⌖"), str(err))
    def pytest_bdd_after_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.STEP, bstack1ll1llll1ll_opy_.POST, request, step)
            return
        try:
            bstack111ll111ll_opy_: bstack111ll1l111_opy_ = _1111llllll_opy_[request.node.nodeid][bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⌗")]
            bstack111ll111ll_opy_.bstack111ll11l11_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack1lll1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡳࡵࡧࡳࡣࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠧ⌘"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack1lll1l1llll1_opy_
        try:
            if not bstack1lll11l1l_opy_.on() or bstack1lll1l1llll1_opy_ != bstack1lll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨ⌙"):
                return
            if cli.is_running():
                cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.TEST, bstack1ll1llll1ll_opy_.PRE, request, feature, scenario)
                return
            driver = bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫ⌚"), None)
            if not _1111llllll_opy_.get(request.node.nodeid, None):
                _1111llllll_opy_[request.node.nodeid] = {}
            bstack111ll111ll_opy_ = bstack111ll1l111_opy_.bstack1llll1lll1l1_opy_(
                scenario, feature, request.node,
                name=bstack1lllllll1111_opy_(request.node, scenario),
                started_at=bstack1111l11l_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack1lll1_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠳ࡣࡶࡥࡸࡱࡧ࡫ࡲࠨ⌛"),
                tags=bstack1llllll1lll1_opy_(feature, scenario),
                bstack111lll11l1_opy_=bstack1lll11l1l_opy_.bstack111ll1llll_opy_(driver) if driver and driver.session_id else {}
            )
            _1111llllll_opy_[request.node.nodeid][bstack1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⌜")] = bstack111ll111ll_opy_
            bstack1lll1ll1111l_opy_(bstack111ll111ll_opy_.uuid)
            bstack1lll11l1l_opy_.bstack111ll11lll_opy_(bstack1lll1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⌝"), bstack111ll111ll_opy_)
        except Exception as err:
            print(bstack1lll1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵ࠺ࠡࡽࢀࠫ⌞"), str(err))
def bstack1lll1ll1ll11_opy_(bstack111ll1l11l_opy_):
    if bstack111ll1l11l_opy_ in store[bstack1lll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⌟")]:
        store[bstack1lll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⌠")].remove(bstack111ll1l11l_opy_)
def bstack1lll1ll1111l_opy_(test_uuid):
    store[bstack1lll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ⌡")] = test_uuid
    threading.current_thread().current_test_uuid = test_uuid
@bstack1lll11l1l_opy_.bstack1llll111lll1_opy_
def bstack1lll1l1ll1l1_opy_(item, call, report):
    logger.debug(bstack1lll1_opy_ (u"࠭ࡨࡢࡰࡧࡰࡪࡥ࡯࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡶࡸࡦࡸࡴࠨ⌢"))
    global bstack1lll1l1llll1_opy_
    bstack11llllllll_opy_ = bstack1111l11l_opy_()
    if hasattr(report, bstack1lll1_opy_ (u"ࠧࡴࡶࡲࡴࠬ⌣")):
        bstack11llllllll_opy_ = bstack11l11l11ll1_opy_(report.stop)
    elif hasattr(report, bstack1lll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࠧ⌤")):
        bstack11llllllll_opy_ = bstack11l11l11ll1_opy_(report.start)
    try:
        if getattr(report, bstack1lll1_opy_ (u"ࠩࡺ࡬ࡪࡴࠧ⌥"), bstack1lll1_opy_ (u"ࠪࠫ⌦")) == bstack1lll1_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ⌧"):
            logger.debug(bstack1lll1_opy_ (u"ࠬ࡮ࡡ࡯ࡦ࡯ࡩࡤࡵ࠱࠲ࡻࡢࡸࡪࡹࡴࡠࡧࡹࡩࡳࡺ࠺ࠡࡵࡷࡥࡹ࡫ࠠ࠮ࠢࡾࢁ࠱ࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠢ࠰ࠤࢀࢃࠧ⌨").format(getattr(report, bstack1lll1_opy_ (u"࠭ࡷࡩࡧࡱࠫ〈"), bstack1lll1_opy_ (u"ࠧࠨ〉")).__str__(), bstack1lll1l1llll1_opy_))
            if bstack1lll1l1llll1_opy_ == bstack1lll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ⌫"):
                _1111llllll_opy_[item.nodeid][bstack1lll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⌬")] = bstack11llllllll_opy_
                bstack1lll1lll1111_opy_(item, _1111llllll_opy_[item.nodeid], bstack1lll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ⌭"), report, call)
                store[bstack1lll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ⌮")] = None
            elif bstack1lll1l1llll1_opy_ == bstack1lll1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤ⌯"):
                bstack111ll111ll_opy_ = _1111llllll_opy_[item.nodeid][bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⌰")]
                bstack111ll111ll_opy_.set(hooks=_1111llllll_opy_[item.nodeid].get(bstack1lll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⌱"), []))
                exception, bstack111ll1l1l1_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack111ll1l1l1_opy_ = [call.excinfo.exconly(), getattr(report, bstack1lll1_opy_ (u"ࠨ࡮ࡲࡲ࡬ࡸࡥࡱࡴࡷࡩࡽࡺࠧ⌲"), bstack1lll1_opy_ (u"ࠩࠪ⌳"))]
                bstack111ll111ll_opy_.stop(time=bstack11llllllll_opy_, result=Result(result=getattr(report, bstack1lll1_opy_ (u"ࠪࡳࡺࡺࡣࡰ࡯ࡨࠫ⌴"), bstack1lll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ⌵")), exception=exception, bstack111ll1l1l1_opy_=bstack111ll1l1l1_opy_))
                bstack1lll11l1l_opy_.bstack111ll11lll_opy_(bstack1lll1_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⌶"), _1111llllll_opy_[item.nodeid][bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⌷")])
        elif getattr(report, bstack1lll1_opy_ (u"ࠧࡸࡪࡨࡲࠬ⌸"), bstack1lll1_opy_ (u"ࠨࠩ⌹")) in [bstack1lll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⌺"), bstack1lll1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬ⌻")]:
            logger.debug(bstack1lll1_opy_ (u"ࠫ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡴࡶࡤࡸࡪࠦ࠭ࠡࡽࢀ࠰ࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࠯ࠣࡿࢂ࠭⌼").format(getattr(report, bstack1lll1_opy_ (u"ࠬࡽࡨࡦࡰࠪ⌽"), bstack1lll1_opy_ (u"࠭ࠧ⌾")).__str__(), bstack1lll1l1llll1_opy_))
            bstack111l1llll1_opy_ = item.nodeid + bstack1lll1_opy_ (u"ࠧ࠮ࠩ⌿") + getattr(report, bstack1lll1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⍀"), bstack1lll1_opy_ (u"ࠩࠪ⍁"))
            if getattr(report, bstack1lll1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫ⍂"), False):
                hook_type = bstack1lll1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩ⍃") if getattr(report, bstack1lll1_opy_ (u"ࠬࡽࡨࡦࡰࠪ⍄"), bstack1lll1_opy_ (u"࠭ࠧ⍅")) == bstack1lll1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭⍆") else bstack1lll1_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡆࡃࡆࡌࠬ⍇")
                _1111llllll_opy_[bstack111l1llll1_opy_] = {
                    bstack1lll1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⍈"): uuid4().__str__(),
                    bstack1lll1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ⍉"): bstack11llllllll_opy_,
                    bstack1lll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ⍊"): hook_type
                }
            _1111llllll_opy_[bstack111l1llll1_opy_][bstack1lll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⍋")] = bstack11llllllll_opy_
            bstack1lll1ll1ll11_opy_(_1111llllll_opy_[bstack111l1llll1_opy_][bstack1lll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⍌")])
            bstack1lll1lll1lll_opy_(item, _1111llllll_opy_[bstack111l1llll1_opy_], bstack1lll1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ⍍"), report, call)
            if getattr(report, bstack1lll1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⍎"), bstack1lll1_opy_ (u"ࠩࠪ⍏")) == bstack1lll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩ⍐"):
                if getattr(report, bstack1lll1_opy_ (u"ࠫࡴࡻࡴࡤࡱࡰࡩࠬ⍑"), bstack1lll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ⍒")) == bstack1lll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⍓"):
                    bstack1111lll1ll_opy_ = {
                        bstack1lll1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⍔"): uuid4().__str__(),
                        bstack1lll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⍕"): bstack1111l11l_opy_(),
                        bstack1lll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⍖"): bstack1111l11l_opy_()
                    }
                    _1111llllll_opy_[item.nodeid] = {**_1111llllll_opy_[item.nodeid], **bstack1111lll1ll_opy_}
                    bstack1lll1lll1111_opy_(item, _1111llllll_opy_[item.nodeid], bstack1lll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⍗"))
                    bstack1lll1lll1111_opy_(item, _1111llllll_opy_[item.nodeid], bstack1lll1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭⍘"), report, call)
    except Exception as err:
        print(bstack1lll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡼࡿࠪ⍙"), str(err))
def bstack1lll1ll11l1l_opy_(test, bstack1111lll1ll_opy_, result=None, call=None, bstack11lll11l1_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack111ll111ll_opy_ = {
        bstack1lll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⍚"): bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⍛")],
        bstack1lll1_opy_ (u"ࠨࡶࡼࡴࡪ࠭⍜"): bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺࠧ⍝"),
        bstack1lll1_opy_ (u"ࠪࡲࡦࡳࡥࠨ⍞"): test.name,
        bstack1lll1_opy_ (u"ࠫࡧࡵࡤࡺࠩ⍟"): {
            bstack1lll1_opy_ (u"ࠬࡲࡡ࡯ࡩࠪ⍠"): bstack1lll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭⍡"),
            bstack1lll1_opy_ (u"ࠧࡤࡱࡧࡩࠬ⍢"): inspect.getsource(test.obj)
        },
        bstack1lll1_opy_ (u"ࠨ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⍣"): test.name,
        bstack1lll1_opy_ (u"ࠩࡶࡧࡴࡶࡥࠨ⍤"): test.name,
        bstack1lll1_opy_ (u"ࠪࡷࡨࡵࡰࡦࡵࠪ⍥"): bstack1ll1ll1l1l_opy_.bstack111l11l11l_opy_(test),
        bstack1lll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ⍦"): file_path,
        bstack1lll1_opy_ (u"ࠬࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠧ⍧"): file_path,
        bstack1lll1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⍨"): bstack1lll1_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨ⍩"),
        bstack1lll1_opy_ (u"ࠨࡸࡦࡣ࡫࡯࡬ࡦࡲࡤࡸ࡭࠭⍪"): file_path,
        bstack1lll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⍫"): bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ⍬")],
        bstack1lll1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ⍭"): bstack1lll1_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸࠬ⍮"),
        bstack1lll1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡘࡥࡳࡷࡱࡔࡦࡸࡡ࡮ࠩ⍯"): {
            bstack1lll1_opy_ (u"ࠧࡳࡧࡵࡹࡳࡥ࡮ࡢ࡯ࡨࠫ⍰"): test.nodeid
        },
        bstack1lll1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭⍱"): bstack11l1111llll_opy_(test.own_markers)
    }
    if bstack11lll11l1_opy_ in [bstack1lll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪ⍲"), bstack1lll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ⍳")]:
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠫࡲ࡫ࡴࡢࠩ⍴")] = {
            bstack1lll1_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧ⍵"): bstack1111lll1ll_opy_.get(bstack1lll1_opy_ (u"࠭ࡦࡪࡺࡷࡹࡷ࡫ࡳࠨ⍶"), [])
        }
    if bstack11lll11l1_opy_ == bstack1lll1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔ࡭࡬ࡴࡵ࡫ࡤࠨ⍷"):
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⍸")] = bstack1lll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪ⍹")
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⍺")] = bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ⍻")]
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⍼")] = bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⍽")]
    if result:
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⍾")] = result.outcome
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩ⍿")] = result.duration * 1000
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⎀")] = bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⎁")]
        if result.failed:
            bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪ⎂")] = bstack1lll11l1l_opy_.bstack1111111ll1_opy_(call.excinfo.typename)
            bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭⎃")] = bstack1lll11l1l_opy_.bstack1llll11lll11_opy_(call.excinfo, result)
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⎄")] = bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⎅")]
    if outcome:
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⎆")] = bstack11l11ll1lll_opy_(outcome)
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ⎇")] = 0
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⎈")] = bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⎉")]
        if bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⎊")] == bstack1lll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⎋"):
            bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪ࠭⎌")] = bstack1lll1_opy_ (u"ࠨࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠩ⎍")  # bstack1lll1ll1l111_opy_
            bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࠪ⎎")] = [{bstack1lll1_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭⎏"): [bstack1lll1_opy_ (u"ࠫࡸࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠨ⎐")]}]
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⎑")] = bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⎒")]
    return bstack111ll111ll_opy_
def bstack1lll1ll111ll_opy_(test, bstack111l111l1l_opy_, bstack11lll11l1_opy_, result, call, outcome, bstack1lll1ll11l11_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack111l111l1l_opy_[bstack1lll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ⎓")]
    hook_name = bstack111l111l1l_opy_[bstack1lll1_opy_ (u"ࠨࡪࡲࡳࡰࡥ࡮ࡢ࡯ࡨࠫ⎔")]
    hook_data = {
        bstack1lll1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⎕"): bstack111l111l1l_opy_[bstack1lll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⎖")],
        bstack1lll1_opy_ (u"ࠫࡹࡿࡰࡦࠩ⎗"): bstack1lll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ⎘"),
        bstack1lll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ⎙"): bstack1lll1_opy_ (u"ࠧࡼࡿࠪ⎚").format(bstack1llllll1ll1l_opy_(hook_name)),
        bstack1lll1_opy_ (u"ࠨࡤࡲࡨࡾ࠭⎛"): {
            bstack1lll1_opy_ (u"ࠩ࡯ࡥࡳ࡭ࠧ⎜"): bstack1lll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ⎝"),
            bstack1lll1_opy_ (u"ࠫࡨࡵࡤࡦࠩ⎞"): None
        },
        bstack1lll1_opy_ (u"ࠬࡹࡣࡰࡲࡨࠫ⎟"): test.name,
        bstack1lll1_opy_ (u"࠭ࡳࡤࡱࡳࡩࡸ࠭⎠"): bstack1ll1ll1l1l_opy_.bstack111l11l11l_opy_(test, hook_name),
        bstack1lll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ⎡"): file_path,
        bstack1lll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࠪ⎢"): file_path,
        bstack1lll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⎣"): bstack1lll1_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ⎤"),
        bstack1lll1_opy_ (u"ࠫࡻࡩ࡟ࡧ࡫࡯ࡩࡵࡧࡴࡩࠩ⎥"): file_path,
        bstack1lll1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⎦"): bstack111l111l1l_opy_[bstack1lll1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⎧")],
        bstack1lll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ⎨"): bstack1lll1_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴ࠮ࡥࡸࡧࡺࡳࡢࡦࡴࠪ⎩") if bstack1lll1l1llll1_opy_ == bstack1lll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩ࠭⎪") else bstack1lll1_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶࠪ⎫"),
        bstack1lll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ⎬"): hook_type
    }
    bstack1ll1111l11l_opy_ = bstack1111ll1111_opy_(_1111llllll_opy_.get(test.nodeid, None))
    if bstack1ll1111l11l_opy_:
        hook_data[bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡪࡦࠪ⎭")] = bstack1ll1111l11l_opy_
    if result:
        hook_data[bstack1lll1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⎮")] = result.outcome
        hook_data[bstack1lll1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡤࡳࡳࠨ⎯")] = result.duration * 1000
        hook_data[bstack1lll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⎰")] = bstack111l111l1l_opy_[bstack1lll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⎱")]
        if result.failed:
            hook_data[bstack1lll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ⎲")] = bstack1lll11l1l_opy_.bstack1111111ll1_opy_(call.excinfo.typename)
            hook_data[bstack1lll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ⎳")] = bstack1lll11l1l_opy_.bstack1llll11lll11_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack1lll1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⎴")] = bstack11l11ll1lll_opy_(outcome)
        hook_data[bstack1lll1_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧ⎵")] = 100
        hook_data[bstack1lll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⎶")] = bstack111l111l1l_opy_[bstack1lll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⎷")]
        if hook_data[bstack1lll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⎸")] == bstack1lll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ⎹"):
            hook_data[bstack1lll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪ⎺")] = bstack1lll1_opy_ (u"࡛ࠬ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷ࠭⎻")  # bstack1lll1ll1l111_opy_
            hook_data[bstack1lll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧ⎼")] = [{bstack1lll1_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪ⎽"): [bstack1lll1_opy_ (u"ࠨࡵࡲࡱࡪࠦࡥࡳࡴࡲࡶࠬ⎾")]}]
    if bstack1lll1ll11l11_opy_:
        hook_data[bstack1lll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⎿")] = bstack1lll1ll11l11_opy_.result
        hook_data[bstack1lll1_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫ⏀")] = bstack111lllll11l_opy_(bstack111l111l1l_opy_[bstack1lll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⏁")], bstack111l111l1l_opy_[bstack1lll1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⏂")])
        hook_data[bstack1lll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⏃")] = bstack111l111l1l_opy_[bstack1lll1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ⏄")]
        if hook_data[bstack1lll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⏅")] == bstack1lll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⏆"):
            hook_data[bstack1lll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ⏇")] = bstack1lll11l1l_opy_.bstack1111111ll1_opy_(bstack1lll1ll11l11_opy_.exception_type)
            hook_data[bstack1lll1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ⏈")] = [{bstack1lll1_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨ⏉"): bstack11l111ll1l1_opy_(bstack1lll1ll11l11_opy_.exception)}]
    return hook_data
def bstack1lll1lll1111_opy_(test, bstack1111lll1ll_opy_, bstack11lll11l1_opy_, result=None, call=None, outcome=None):
    logger.debug(bstack1lll1_opy_ (u"࠭ࡳࡦࡰࡧࡣࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡥࡷࡧࡱࡸ࠿ࠦࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡶࡨࡷࡹࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠥ࠳ࠠࡼࡿࠪ⏊").format(bstack11lll11l1_opy_))
    bstack111ll111ll_opy_ = bstack1lll1ll11l1l_opy_(test, bstack1111lll1ll_opy_, result, call, bstack11lll11l1_opy_, outcome)
    driver = getattr(test, bstack1lll1_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨ⏋"), None)
    if bstack11lll11l1_opy_ == bstack1lll1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⏌") and driver:
        bstack111ll111ll_opy_[bstack1lll1_opy_ (u"ࠩ࡬ࡲࡹ࡫ࡧࡳࡣࡷ࡭ࡴࡴࡳࠨ⏍")] = bstack1lll11l1l_opy_.bstack111ll1llll_opy_(driver)
    if bstack11lll11l1_opy_ == bstack1lll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡰ࡯ࡰࡱࡧࡧࠫ⏎"):
        bstack11lll11l1_opy_ = bstack1lll1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭⏏")
    bstack111l1ll111_opy_ = {
        bstack1lll1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ⏐"): bstack11lll11l1_opy_,
        bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ⏑"): bstack111ll111ll_opy_
    }
    bstack1lll11l1l_opy_.bstack11l11l1l1l_opy_(bstack111l1ll111_opy_)
    if bstack11lll11l1_opy_ == bstack1lll1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ⏒"):
        threading.current_thread().bstackTestMeta = {bstack1lll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ⏓"): bstack1lll1_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ⏔")}
    elif bstack11lll11l1_opy_ == bstack1lll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ⏕"):
        threading.current_thread().bstackTestMeta = {bstack1lll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ⏖"): getattr(result, bstack1lll1_opy_ (u"ࠬࡵࡵࡵࡥࡲࡱࡪ࠭⏗"), bstack1lll1_opy_ (u"࠭ࠧ⏘"))}
def bstack1lll1lll1lll_opy_(test, bstack1111lll1ll_opy_, bstack11lll11l1_opy_, result=None, call=None, outcome=None, bstack1lll1ll11l11_opy_=None):
    logger.debug(bstack1lll1_opy_ (u"ࠧࡴࡧࡱࡨࡤ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡦࡸࡨࡲࡹࡀࠠࡂࡶࡷࡩࡲࡶࡴࡪࡰࡪࠤࡹࡵࠠࡨࡧࡱࡩࡷࡧࡴࡦࠢ࡫ࡳࡴࡱࠠࡥࡣࡷࡥ࠱ࠦࡥࡷࡧࡱࡸ࡙ࡿࡰࡦࠢ࠰ࠤࢀࢃࠧ⏙").format(bstack11lll11l1_opy_))
    hook_data = bstack1lll1ll111ll_opy_(test, bstack1111lll1ll_opy_, bstack11lll11l1_opy_, result, call, outcome, bstack1lll1ll11l11_opy_)
    bstack111l1ll111_opy_ = {
        bstack1lll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ⏚"): bstack11lll11l1_opy_,
        bstack1lll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࠫ⏛"): hook_data
    }
    bstack1lll11l1l_opy_.bstack11l11l1l1l_opy_(bstack111l1ll111_opy_)
def bstack1111ll1111_opy_(bstack1111lll1ll_opy_):
    if not bstack1111lll1ll_opy_:
        return None
    if bstack1111lll1ll_opy_.get(bstack1lll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭⏜"), None):
        return getattr(bstack1111lll1ll_opy_[bstack1lll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ⏝")], bstack1lll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ⏞"), None)
    return bstack1111lll1ll_opy_.get(bstack1lll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⏟"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.LOG, bstack1ll1llll1ll_opy_.PRE, request, caplog)
    yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_.LOG, bstack1ll1llll1ll_opy_.POST, request, caplog)
        return # skip all existing operations
    try:
        if not bstack1lll11l1l_opy_.on():
            return
        places = [bstack1lll1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭⏠"), bstack1lll1_opy_ (u"ࠨࡥࡤࡰࡱ࠭⏡"), bstack1lll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫ⏢")]
        logs = []
        for bstack1lll1l1lllll_opy_ in places:
            records = caplog.get_records(bstack1lll1l1lllll_opy_)
            bstack1lll1lll11ll_opy_ = bstack1lll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⏣") if bstack1lll1l1lllll_opy_ == bstack1lll1_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ⏤") else bstack1lll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⏥")
            bstack1lll1ll1l1l1_opy_ = request.node.nodeid + (bstack1lll1_opy_ (u"࠭ࠧ⏦") if bstack1lll1l1lllll_opy_ == bstack1lll1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ⏧") else bstack1lll1_opy_ (u"ࠨ࠯ࠪ⏨") + bstack1lll1l1lllll_opy_)
            test_uuid = bstack1111ll1111_opy_(_1111llllll_opy_.get(bstack1lll1ll1l1l1_opy_, None))
            if not test_uuid:
                continue
            for record in records:
                if bstack11l11111ll1_opy_(record.message):
                    continue
                logs.append({
                    bstack1lll1_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ⏩"): bstack11l11ll1111_opy_(record.created).isoformat() + bstack1lll1_opy_ (u"ࠪ࡞ࠬ⏪"),
                    bstack1lll1_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ⏫"): record.levelname,
                    bstack1lll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭⏬"): record.message,
                    bstack1lll1lll11ll_opy_: test_uuid
                })
        if len(logs) > 0:
            bstack1lll11l1l_opy_.bstack11l11111ll_opy_(logs)
    except Exception as err:
        print(bstack1lll1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡹࡥࡤࡱࡱࡨࡤ࡬ࡩࡹࡶࡸࡶࡪࡀࠠࡼࡿࠪ⏭"), str(err))
def bstack11l1lll111_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack1111l1l1_opy_
    bstack1111l1l1l_opy_ = bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ⏮"), None) and bstack1ll1l1l1l1_opy_(
            threading.current_thread(), bstack1lll1_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ⏯"), None)
    bstack1l11l1lll1_opy_ = getattr(driver, bstack1lll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ⏰"), None) != None and getattr(driver, bstack1lll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪ⏱"), None) == True
    if sequence == bstack1lll1_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫ⏲") and driver != None:
      if not bstack1111l1l1_opy_ and bstack1l1l1ll11l1_opy_() and bstack1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ⏳") in CONFIG and CONFIG[bstack1lll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭⏴")] == True and bstack1111ll11l_opy_.bstack1lll1111l1_opy_(driver_command) and (bstack1l11l1lll1_opy_ or bstack1111l1l1l_opy_) and not bstack11lll1ll1_opy_(args):
        try:
          bstack1111l1l1_opy_ = True
          logger.debug(bstack1lll1_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡩࡳࡷࠦࡻࡾࠩ⏵").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack1lll1_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵ࡫ࡲࡧࡱࡵࡱࠥࡹࡣࡢࡰࠣࡿࢂ࠭⏶").format(str(err)))
        bstack1111l1l1_opy_ = False
    if sequence == bstack1lll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨ⏷"):
        if driver_command == bstack1lll1_opy_ (u"ࠪࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠧ⏸"):
            bstack1lll11l1l_opy_.bstack1l111llll1_opy_({
                bstack1lll1_opy_ (u"ࠫ࡮ࡳࡡࡨࡧࠪ⏹"): response[bstack1lll1_opy_ (u"ࠬࡼࡡ࡭ࡷࡨࠫ⏺")],
                bstack1lll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⏻"): store[bstack1lll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⏼")]
            })
def bstack11lllllll_opy_():
    global bstack111lllll1l_opy_
    bstack11lll11l_opy_.bstack1l1llll1l_opy_()
    logging.shutdown()
    bstack1lll11l1l_opy_.bstack1111lll111_opy_()
    for driver in bstack111lllll1l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack1lll1l1ll11l_opy_(*args):
    global bstack111lllll1l_opy_
    bstack1lll11l1l_opy_.bstack1111lll111_opy_()
    for driver in bstack111lllll1l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1ll1llllll_opy_, stage=STAGE.bstack11ll11ll1l_opy_, bstack1ll1ll1l11_opy_=bstack1l11111l1_opy_)
def bstack1lll1ll1ll_opy_(self, *args, **kwargs):
    bstack1lll11111l_opy_ = bstack1ll1lllll_opy_(self, *args, **kwargs)
    bstack1l111lll11_opy_ = getattr(threading.current_thread(), bstack1lll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡕࡧࡶࡸࡒ࡫ࡴࡢࠩ⏽"), None)
    if bstack1l111lll11_opy_ and bstack1l111lll11_opy_.get(bstack1lll1_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ⏾"), bstack1lll1_opy_ (u"ࠪࠫ⏿")) == bstack1lll1_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬ␀"):
        bstack1lll11l1l_opy_.bstack1l1ll11l_opy_(self)
    return bstack1lll11111l_opy_
@measure(event_name=EVENTS.bstack1l1l1l1l11_opy_, stage=STAGE.bstack1l111l111_opy_, bstack1ll1ll1l11_opy_=bstack1l11111l1_opy_)
def bstack1ll11111l1_opy_(framework_name):
    from bstack_utils.config import Config
    bstack1l1111ll1_opy_ = Config.bstack1111l11l1_opy_()
    if bstack1l1111ll1_opy_.get_property(bstack1lll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡳ࡯ࡥࡡࡦࡥࡱࡲࡥࡥࠩ␁")):
        return
    bstack1l1111ll1_opy_.bstack1l11l1l1_opy_(bstack1lll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥ࡭ࡰࡦࡢࡧࡦࡲ࡬ࡦࡦࠪ␂"), True)
    global bstack111ll1l1l_opy_
    global bstack11l1llllll_opy_
    bstack111ll1l1l_opy_ = framework_name
    logger.info(bstack11lll11lll_opy_.format(bstack111ll1l1l_opy_.split(bstack1lll1_opy_ (u"ࠧ࠮ࠩ␃"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack1l1l1ll11l1_opy_():
            Service.start = bstack1l111l11_opy_
            Service.stop = bstack11llll11_opy_
            webdriver.Remote.get = bstack1lll1l1l1_opy_
            webdriver.Remote.__init__ = bstack111ll1lll_opy_
            if not isinstance(os.getenv(bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑ࡛ࡗࡉࡘ࡚࡟ࡑࡃࡕࡅࡑࡒࡅࡍࠩ␄")), str):
                return
            WebDriver.quit = bstack11ll11ll_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        elif bstack1lll11l1l_opy_.on():
            webdriver.Remote.__init__ = bstack1lll1ll1ll_opy_
        bstack11l1llllll_opy_ = True
    except Exception as e:
        pass
    if os.environ.get(bstack1lll1_opy_ (u"ࠩࡖࡉࡑࡋࡎࡊࡗࡐࡣࡔࡘ࡟ࡑࡎࡄ࡝࡜ࡘࡉࡈࡊࡗࡣࡎࡔࡓࡕࡃࡏࡐࡊࡊࠧ␅")):
        bstack11l1llllll_opy_ = eval(os.environ.get(bstack1lll1_opy_ (u"ࠪࡗࡊࡒࡅࡏࡋࡘࡑࡤࡕࡒࡠࡒࡏࡅ࡞࡝ࡒࡊࡉࡋࡘࡤࡏࡎࡔࡖࡄࡐࡑࡋࡄࠨ␆")))
    if not bstack11l1llllll_opy_:
        bstack1l1l11111l_opy_(bstack1lll1_opy_ (u"ࠦࡕࡧࡣ࡬ࡣࡪࡩࡸࠦ࡮ࡰࡶࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠨ␇"), bstack1l1l1llll_opy_)
    if bstack11ll1l11ll_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            if hasattr(RemoteConnection, bstack1lll1_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭␈")) and callable(getattr(RemoteConnection, bstack1lll1_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ␉"))):
                RemoteConnection._get_proxy_url = bstack1l1l11ll1l_opy_
            else:
                from selenium.webdriver.remote.client_config import ClientConfig
                ClientConfig.get_proxy_url = bstack1l1l11ll1l_opy_
        except Exception as e:
            logger.error(bstack1l1111111_opy_.format(str(e)))
    if bstack1lll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ␊") in str(framework_name).lower():
        if not bstack1l1l1ll11l1_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack1ll111llll_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack11l11l1ll1_opy_
            Config.getoption = bstack1ll1l1ll_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack1l1l1llll1_opy_
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack11l1111l1_opy_, stage=STAGE.bstack11ll11ll1l_opy_, bstack1ll1ll1l11_opy_=bstack1l11111l1_opy_)
def bstack11ll11ll_opy_(self):
    global bstack111ll1l1l_opy_
    global bstack1111ll111_opy_
    global bstack1l111lll1_opy_
    try:
        if bstack1lll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ␋") in bstack111ll1l1l_opy_ and self.session_id != None and bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"ࠩࡷࡩࡸࡺࡓࡵࡣࡷࡹࡸ࠭␌"), bstack1lll1_opy_ (u"ࠪࠫ␍")) != bstack1lll1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ␎"):
            bstack1ll11lll_opy_ = bstack1lll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ␏") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1lll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭␐")
            bstack1111l1ll1_opy_(logger, True)
            if os.environ.get(bstack1lll1_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࡟ࡕࡇࡖࡘࡤࡔࡁࡎࡇࠪ␑"), None):
                self.execute_script(
                    bstack1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭␒") + json.dumps(
                        os.environ.get(bstack1lll1_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ␓"))) + bstack1lll1_opy_ (u"ࠪࢁࢂ࠭␔"))
            if self != None:
                bstack11l1111111_opy_(self, bstack1ll11lll_opy_, bstack1lll1_opy_ (u"ࠫ࠱ࠦࠧ␕").join(threading.current_thread().bstackTestErrorMessages))
        if not cli.bstack1lll1l1ll1l_opy_(bstack1lll1l1ll11_opy_):
            item = store.get(bstack1lll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ␖"), None)
            if item is not None and bstack1ll1l1l1l1_opy_(threading.current_thread(), bstack1lll1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ␗"), None):
                bstack11ll1l111_opy_.bstack11lllll1_opy_(self, bstack11l11lll1l_opy_, logger, item)
        threading.current_thread().testStatus = bstack1lll1_opy_ (u"ࠧࠨ␘")
    except Exception as e:
        logger.debug(bstack1lll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࠤ␙") + str(e))
    bstack1l111lll1_opy_(self)
    self.session_id = None
@measure(event_name=EVENTS.bstack11llll1ll_opy_, stage=STAGE.bstack11ll11ll1l_opy_, bstack1ll1ll1l11_opy_=bstack1l11111l1_opy_)
def bstack111ll1lll_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack1111ll111_opy_
    global bstack1l11111l1_opy_
    global bstack1l11lllll1_opy_
    global bstack111ll1l1l_opy_
    global bstack1ll1lllll_opy_
    global bstack111lllll1l_opy_
    global bstack1lll1lll_opy_
    global bstack1l1l11111_opy_
    global bstack11l11lll1l_opy_
    CONFIG[bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ␚")] = str(bstack111ll1l1l_opy_) + str(__version__)
    command_executor = bstack11ll1ll1l1_opy_(bstack1lll1lll_opy_, CONFIG)
    logger.debug(bstack11111111_opy_.format(command_executor))
    proxy = bstack11l1llll1l_opy_(CONFIG, proxy)
    bstack1ll11l111_opy_ = 0
    try:
        if bstack1l11lllll1_opy_ is True:
            bstack1ll11l111_opy_ = int(os.environ.get(bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ␛")))
    except:
        bstack1ll11l111_opy_ = 0
    bstack11l11llll1_opy_ = bstack11ll11111l_opy_(CONFIG, bstack1ll11l111_opy_)
    logger.debug(bstack1l1l1ll1ll_opy_.format(str(bstack11l11llll1_opy_)))
    bstack11l11lll1l_opy_ = CONFIG.get(bstack1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ␜"))[bstack1ll11l111_opy_]
    if bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ␝") in CONFIG and CONFIG[bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ␞")]:
        bstack11lll1lll_opy_(bstack11l11llll1_opy_, bstack1l1l11111_opy_)
    if bstack1l11llll1l_opy_.bstack1lll111l_opy_(CONFIG, bstack1ll11l111_opy_) and bstack1l11llll1l_opy_.bstack1ll11l1l1l_opy_(bstack11l11llll1_opy_, options, desired_capabilities):
        threading.current_thread().a11yPlatform = True
        if not cli.bstack1lll1l1ll1l_opy_(bstack1lll1l1ll11_opy_):
            bstack1l11llll1l_opy_.set_capabilities(bstack11l11llll1_opy_, CONFIG)
    if desired_capabilities:
        bstack11lll1llll_opy_ = bstack1111111ll_opy_(desired_capabilities)
        bstack11lll1llll_opy_[bstack1lll1_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ␟")] = bstack1lllll1l1l_opy_(CONFIG)
        bstack111ll1111_opy_ = bstack11ll11111l_opy_(bstack11lll1llll_opy_)
        if bstack111ll1111_opy_:
            bstack11l11llll1_opy_ = update(bstack111ll1111_opy_, bstack11l11llll1_opy_)
        desired_capabilities = None
    if options:
        bstack11l1l1ll11_opy_(options, bstack11l11llll1_opy_)
    if not options:
        options = bstack1lllll1l11_opy_(bstack11l11llll1_opy_)
    if proxy and bstack11llll111l_opy_() >= version.parse(bstack1lll1_opy_ (u"ࠨ࠶࠱࠵࠵࠴࠰ࠨ␠")):
        options.proxy(proxy)
    if options and bstack11llll111l_opy_() >= version.parse(bstack1lll1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨ␡")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack11llll111l_opy_() < version.parse(bstack1lll1_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ␢")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack11l11llll1_opy_)
    logger.info(bstack1lllllll1_opy_)
    bstack1l1ll11l11_opy_.end(EVENTS.bstack1l1l1l1l11_opy_.value, EVENTS.bstack1l1l1l1l11_opy_.value + bstack1lll1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦ␣"),
                               EVENTS.bstack1l1l1l1l11_opy_.value + bstack1lll1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥ␤"), True, None)
    try:
        if bstack11llll111l_opy_() >= version.parse(bstack1lll1_opy_ (u"࠭࠴࠯࠳࠳࠲࠵࠭␥")):
            bstack1ll1lllll_opy_(self, command_executor=command_executor,
                      options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
        elif bstack11llll111l_opy_() >= version.parse(bstack1lll1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭␦")):
            bstack1ll1lllll_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities, options=options,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        elif bstack11llll111l_opy_() >= version.parse(bstack1lll1_opy_ (u"ࠨ࠴࠱࠹࠸࠴࠰ࠨ␧")):
            bstack1ll1lllll_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        else:
            bstack1ll1lllll_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive)
    except Exception as bstack1lll1lll1l_opy_:
        logger.error(bstack11111l111_opy_.format(bstack1lll1_opy_ (u"ࠩࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠨ␨"), str(bstack1lll1lll1l_opy_)))
        raise bstack1lll1lll1l_opy_
    try:
        bstack1l1llll11l_opy_ = bstack1lll1_opy_ (u"ࠪࠫ␩")
        if bstack11llll111l_opy_() >= version.parse(bstack1lll1_opy_ (u"ࠫ࠹࠴࠰࠯࠲ࡥ࠵ࠬ␪")):
            bstack1l1llll11l_opy_ = self.caps.get(bstack1lll1_opy_ (u"ࠧࡵࡰࡵ࡫ࡰࡥࡱࡎࡵࡣࡗࡵࡰࠧ␫"))
        else:
            bstack1l1llll11l_opy_ = self.capabilities.get(bstack1lll1_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡱࡦࡲࡈࡶࡤࡘࡶࡱࠨ␬"))
        if bstack1l1llll11l_opy_:
            bstack1llllll11l_opy_(bstack1l1llll11l_opy_)
            if bstack11llll111l_opy_() <= version.parse(bstack1lll1_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧ␭")):
                self.command_executor._url = bstack1lll1_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ␮") + bstack1lll1lll_opy_ + bstack1lll1_opy_ (u"ࠤ࠽࠼࠵࠵ࡷࡥ࠱࡫ࡹࡧࠨ␯")
            else:
                self.command_executor._url = bstack1lll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࠧ␰") + bstack1l1llll11l_opy_ + bstack1lll1_opy_ (u"ࠦ࠴ࡽࡤ࠰ࡪࡸࡦࠧ␱")
            logger.debug(bstack1111l1111_opy_.format(bstack1l1llll11l_opy_))
        else:
            logger.debug(bstack111l11ll_opy_.format(bstack1lll1_opy_ (u"ࠧࡕࡰࡵ࡫ࡰࡥࡱࠦࡈࡶࡤࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩࠨ␲")))
    except Exception as e:
        logger.debug(bstack111l11ll_opy_.format(e))
    bstack1111ll111_opy_ = self.session_id
    if bstack1lll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭␳") in bstack111ll1l1l_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack1lll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫ␴"), None)
        if item:
            bstack1lll1ll111l1_opy_ = getattr(item, bstack1lll1_opy_ (u"ࠨࡡࡷࡩࡸࡺ࡟ࡤࡣࡶࡩࡤࡹࡴࡢࡴࡷࡩࡩ࠭␵"), False)
            if not getattr(item, bstack1lll1_opy_ (u"ࠩࡢࡨࡷ࡯ࡶࡦࡴࠪ␶"), None) and bstack1lll1ll111l1_opy_:
                setattr(store[bstack1lll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡸࡪࡳࠧ␷")], bstack1lll1_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬ␸"), self)
        bstack1l111lll11_opy_ = getattr(threading.current_thread(), bstack1lll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࡙࡫ࡳࡵࡏࡨࡸࡦ࠭␹"), None)
        if bstack1l111lll11_opy_ and bstack1l111lll11_opy_.get(bstack1lll1_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭␺"), bstack1lll1_opy_ (u"ࠧࠨ␻")) == bstack1lll1_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩ␼"):
            bstack1lll11l1l_opy_.bstack1l1ll11l_opy_(self)
    bstack111lllll1l_opy_.append(self)
    if bstack1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ␽") in CONFIG and bstack1lll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ␾") in CONFIG[bstack1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ␿")][bstack1ll11l111_opy_]:
        bstack1l11111l1_opy_ = CONFIG[bstack1lll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ⑀")][bstack1ll11l111_opy_][bstack1lll1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ⑁")]
    logger.debug(bstack1ll111l11l_opy_.format(bstack1111ll111_opy_))
@measure(event_name=EVENTS.bstack1ll11llll_opy_, stage=STAGE.bstack11ll11ll1l_opy_, bstack1ll1ll1l11_opy_=bstack1l11111l1_opy_)
def bstack1lll1l1l1_opy_(self, url):
    global bstack1llllll111_opy_
    global CONFIG
    try:
        bstack1l111lll1l_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack11111lll1_opy_.format(str(err)))
    try:
        bstack1llllll111_opy_(self, url)
    except Exception as e:
        try:
            bstack1ll1lll11_opy_ = str(e)
            if any(err_msg in bstack1ll1lll11_opy_ for err_msg in bstack1l1111l1l_opy_):
                bstack1l111lll1l_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack11111lll1_opy_.format(str(err)))
        raise e
def bstack1l11ll11l_opy_(item, when):
    global bstack11ll1lll1_opy_
    try:
        bstack11ll1lll1_opy_(item, when)
    except Exception as e:
        pass
def bstack1l1l1llll1_opy_(item, call, rep):
    global bstack111ll1ll1_opy_
    global bstack111lllll1l_opy_
    name = bstack1lll1_opy_ (u"ࠧࠨ⑂")
    try:
        if rep.when == bstack1lll1_opy_ (u"ࠨࡥࡤࡰࡱ࠭⑃"):
            bstack1111ll111_opy_ = threading.current_thread().bstackSessionId
            skipSessionName = item.config.getoption(bstack1lll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ⑄"))
            try:
                if (str(skipSessionName).lower() != bstack1lll1_opy_ (u"ࠪࡸࡷࡻࡥࠨ⑅")):
                    name = str(rep.nodeid)
                    bstack1ll1ll111l_opy_ = bstack11ll1l1l_opy_(bstack1lll1_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ⑆"), name, bstack1lll1_opy_ (u"ࠬ࠭⑇"), bstack1lll1_opy_ (u"࠭ࠧ⑈"), bstack1lll1_opy_ (u"ࠧࠨ⑉"), bstack1lll1_opy_ (u"ࠨࠩ⑊"))
                    os.environ[bstack1lll1_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ⑋")] = name
                    for driver in bstack111lllll1l_opy_:
                        if bstack1111ll111_opy_ == driver.session_id:
                            driver.execute_script(bstack1ll1ll111l_opy_)
            except Exception as e:
                logger.debug(bstack1lll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪ⑌").format(str(e)))
            try:
                bstack1l1l1ll1l1_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack1lll1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ⑍"):
                    status = bstack1lll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ⑎") if rep.outcome.lower() == bstack1lll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⑏") else bstack1lll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ⑐")
                    reason = bstack1lll1_opy_ (u"ࠨࠩ⑑")
                    if status == bstack1lll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⑒"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack1lll1_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨ⑓") if status == bstack1lll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ⑔") else bstack1lll1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ⑕")
                    data = name + bstack1lll1_opy_ (u"࠭ࠠࡱࡣࡶࡷࡪࡪࠡࠨ⑖") if status == bstack1lll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ⑗") else name + bstack1lll1_opy_ (u"ࠨࠢࡩࡥ࡮ࡲࡥࡥࠣࠣࠫ⑘") + reason
                    bstack111l111ll_opy_ = bstack11ll1l1l_opy_(bstack1lll1_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫ⑙"), bstack1lll1_opy_ (u"ࠪࠫ⑚"), bstack1lll1_opy_ (u"ࠫࠬ⑛"), bstack1lll1_opy_ (u"ࠬ࠭⑜"), level, data)
                    for driver in bstack111lllll1l_opy_:
                        if bstack1111ll111_opy_ == driver.session_id:
                            driver.execute_script(bstack111l111ll_opy_)
            except Exception as e:
                logger.debug(bstack1lll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡴࡴࡴࡦࡺࡷࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪ⑝").format(str(e)))
    except Exception as e:
        logger.debug(bstack1lll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡷࡹࡧࡴࡦࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࡽࢀࠫ⑞").format(str(e)))
    bstack111ll1ll1_opy_(item, call, rep)
notset = Notset()
def bstack1ll1l1ll_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack1l1l1l1l1l_opy_
    if str(name).lower() == bstack1lll1_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࠨ⑟"):
        return bstack1lll1_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣ①")
    else:
        return bstack1l1l1l1l1l_opy_(self, name, default, skip)
def bstack1l1l11ll1l_opy_(self):
    global CONFIG
    global bstack1l1111111l_opy_
    try:
        proxy = bstack11l11lllll_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack1lll1_opy_ (u"ࠪ࠲ࡵࡧࡣࠨ②")):
                proxies = bstack11llll111_opy_(proxy, bstack11ll1ll1l1_opy_())
                if len(proxies) > 0:
                    protocol, bstack1l1ll11ll_opy_ = proxies.popitem()
                    if bstack1lll1_opy_ (u"ࠦ࠿࠵࠯ࠣ③") in bstack1l1ll11ll_opy_:
                        return bstack1l1ll11ll_opy_
                    else:
                        return bstack1lll1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨ④") + bstack1l1ll11ll_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack1lll1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡳࡶࡴࡾࡹࠡࡷࡵࡰࠥࡀࠠࡼࡿࠥ⑤").format(str(e)))
    return bstack1l1111111l_opy_(self)
def bstack11ll1l11ll_opy_():
    return (bstack1lll1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ⑥") in CONFIG or bstack1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ⑦") in CONFIG) and bstack1l1llllll1_opy_() and bstack11llll111l_opy_() >= version.parse(
        bstack1lll1l1ll1_opy_)
def bstack111ll1l11_opy_(self,
               executablePath=None,
               channel=None,
               args=None,
               ignoreDefaultArgs=None,
               handleSIGINT=None,
               handleSIGTERM=None,
               handleSIGHUP=None,
               timeout=None,
               env=None,
               headless=None,
               devtools=None,
               proxy=None,
               downloadsPath=None,
               slowMo=None,
               tracesDir=None,
               chromiumSandbox=None,
               firefoxUserPrefs=None
               ):
    global CONFIG
    global bstack1l11111l1_opy_
    global bstack1l11lllll1_opy_
    global bstack111ll1l1l_opy_
    CONFIG[bstack1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ⑧")] = str(bstack111ll1l1l_opy_) + str(__version__)
    bstack1ll11l111_opy_ = 0
    try:
        if bstack1l11lllll1_opy_ is True:
            bstack1ll11l111_opy_ = int(os.environ.get(bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ⑨")))
    except:
        bstack1ll11l111_opy_ = 0
    CONFIG[bstack1lll1_opy_ (u"ࠦ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ⑩")] = True
    bstack11l11llll1_opy_ = bstack11ll11111l_opy_(CONFIG, bstack1ll11l111_opy_)
    logger.debug(bstack1l1l1ll1ll_opy_.format(str(bstack11l11llll1_opy_)))
    if CONFIG.get(bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ⑪")):
        bstack11lll1lll_opy_(bstack11l11llll1_opy_, bstack1l1l11111_opy_)
    if bstack1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ⑫") in CONFIG and bstack1lll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ⑬") in CONFIG[bstack1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ⑭")][bstack1ll11l111_opy_]:
        bstack1l11111l1_opy_ = CONFIG[bstack1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ⑮")][bstack1ll11l111_opy_][bstack1lll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ⑯")]
    import urllib
    import json
    if bstack1lll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ⑰") in CONFIG and str(CONFIG[bstack1lll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ⑱")]).lower() != bstack1lll1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬ⑲"):
        bstack11llll1l1l_opy_ = bstack11l1ll1l1l_opy_()
        bstack1l1ll1lll1_opy_ = bstack11llll1l1l_opy_ + urllib.parse.quote(json.dumps(bstack11l11llll1_opy_))
    else:
        bstack1l1ll1lll1_opy_ = bstack1lll1_opy_ (u"ࠧࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠩ⑳") + urllib.parse.quote(json.dumps(bstack11l11llll1_opy_))
    browser = self.connect(bstack1l1ll1lll1_opy_)
    return browser
def bstack1l11ll1ll1_opy_():
    global bstack11l1llllll_opy_
    global bstack111ll1l1l_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1lll11ll_opy_
        if not bstack1l1l1ll11l1_opy_():
            global bstack11l1ll1l_opy_
            if not bstack11l1ll1l_opy_:
                from bstack_utils.helper import bstack1l11l1l11l_opy_, bstack111l11ll1_opy_
                bstack11l1ll1l_opy_ = bstack1l11l1l11l_opy_()
                bstack111l11ll1_opy_(bstack111ll1l1l_opy_)
            BrowserType.connect = bstack1lll11ll_opy_
            return
        BrowserType.launch = bstack111ll1l11_opy_
        bstack11l1llllll_opy_ = True
    except Exception as e:
        pass
def bstack1lll1ll11ll1_opy_():
    global CONFIG
    global bstack1lll1ll1l_opy_
    global bstack1lll1lll_opy_
    global bstack1l1l11111_opy_
    global bstack1l11lllll1_opy_
    global bstack11ll1l11l_opy_
    CONFIG = json.loads(os.environ.get(bstack1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍࠧ⑴")))
    bstack1lll1ll1l_opy_ = eval(os.environ.get(bstack1lll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪ⑵")))
    bstack1lll1lll_opy_ = os.environ.get(bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡋ࡙ࡇࡥࡕࡓࡎࠪ⑶"))
    bstack11l111ll_opy_(CONFIG, bstack1lll1ll1l_opy_)
    bstack11ll1l11l_opy_ = bstack11lll11l_opy_.configure_logger(CONFIG, bstack11ll1l11l_opy_)
    if cli.bstack1l11ll111_opy_():
        bstack1l1ll1l111_opy_.invoke(bstack1l1ll1ll11_opy_.CONNECT, bstack1l11l11l1_opy_())
        cli_context.platform_index = int(os.environ.get(bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫ⑷"), bstack1lll1_opy_ (u"ࠬ࠶ࠧ⑸")))
        cli.bstack1lll1ll1111_opy_(cli_context.platform_index)
        cli.bstack1llll11ll11_opy_(bstack11ll1ll1l1_opy_(bstack1lll1lll_opy_, CONFIG), cli_context.platform_index, bstack1lllll1l11_opy_)
        cli.bstack1ll1ll1ll1l_opy_()
        logger.debug(bstack1lll1_opy_ (u"ࠨࡃࡍࡋࠣ࡭ࡸࠦࡡࡤࡶ࡬ࡺࡪࠦࡦࡰࡴࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࠧ⑹") + str(cli_context.platform_index) + bstack1lll1_opy_ (u"ࠢࠣ⑺"))
        return # skip all existing operations
    global bstack1ll1lllll_opy_
    global bstack1l111lll1_opy_
    global bstack1ll1l1111_opy_
    global bstack1111l111l_opy_
    global bstack1111ll1l_opy_
    global bstack1ll111l11_opy_
    global bstack1ll11l1lll_opy_
    global bstack1llllll111_opy_
    global bstack1l1111111l_opy_
    global bstack1l1l1l1l1l_opy_
    global bstack11ll1lll1_opy_
    global bstack111ll1ll1_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack1ll1lllll_opy_ = webdriver.Remote.__init__
        bstack1l111lll1_opy_ = WebDriver.quit
        bstack1ll11l1lll_opy_ = WebDriver.close
        bstack1llllll111_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫ⑻") in CONFIG or bstack1lll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭⑼") in CONFIG) and bstack1l1llllll1_opy_():
        if bstack11llll111l_opy_() < version.parse(bstack1lll1l1ll1_opy_):
            logger.error(bstack11l111l1ll_opy_.format(bstack11llll111l_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                if hasattr(RemoteConnection, bstack1lll1_opy_ (u"ࠪࡣ࡬࡫ࡴࡠࡲࡵࡳࡽࡿ࡟ࡶࡴ࡯ࠫ⑽")) and callable(getattr(RemoteConnection, bstack1lll1_opy_ (u"ࠫࡤ࡭ࡥࡵࡡࡳࡶࡴࡾࡹࡠࡷࡵࡰࠬ⑾"))):
                    bstack1l1111111l_opy_ = RemoteConnection._get_proxy_url
                else:
                    from selenium.webdriver.remote.client_config import ClientConfig
                    bstack1l1111111l_opy_ = ClientConfig.get_proxy_url
            except Exception as e:
                logger.error(bstack1l1111111_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack1l1l1l1l1l_opy_ = Config.getoption
        from _pytest import runner
        bstack11ll1lll1_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warn(e, bstack1l11111l_opy_)
    try:
        from pytest_bdd import reporting
        bstack111ll1ll1_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack1lll1_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡴࠦࡲࡶࡰࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡵࡧࡶࡸࡸ࠭⑿"))
    bstack1l1l11111_opy_ = CONFIG.get(bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ⒀"), {}).get(bstack1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ⒁"))
    bstack1l11lllll1_opy_ = True
    bstack1ll11111l1_opy_(bstack1l111l11l_opy_)
if (bstack111llll1lll_opy_()):
    bstack1lll1ll11ll1_opy_()
@error_handler(class_method=False)
def bstack1lll1l1ll111_opy_(hook_name, event, bstack11llll1lll1_opy_=None):
    if hook_name not in [bstack1lll1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩ⒂"), bstack1lll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭⒃"), bstack1lll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠩ⒄"), bstack1lll1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭⒅"), bstack1lll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪ⒆"), bstack1lll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡥ࡯ࡥࡸࡹࠧ⒇"), bstack1lll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭⒈"), bstack1lll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪ⒉")]:
        return
    node = store[bstack1lll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⒊")]
    if hook_name in [bstack1lll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠩ⒋"), bstack1lll1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭⒌")]:
        node = store[bstack1lll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥ࡭ࡰࡦࡸࡰࡪࡥࡩࡵࡧࡰࠫ⒍")]
    elif hook_name in [bstack1lll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡩ࡬ࡢࡵࡶࠫ⒎"), bstack1lll1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡦࡰࡦࡹࡳࠨ⒏")]:
        node = store[bstack1lll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡦࡰࡦࡹࡳࡠ࡫ࡷࡩࡲ࠭⒐")]
    hook_type = bstack1llllll1l1ll_opy_(hook_name)
    if event == bstack1lll1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩ⒑"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_[hook_type], bstack1ll1llll1ll_opy_.PRE, node, hook_name)
            return
        uuid = uuid4().__str__()
        bstack111l111l1l_opy_ = {
            bstack1lll1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⒒"): uuid,
            bstack1lll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⒓"): bstack1111l11l_opy_(),
            bstack1lll1_opy_ (u"ࠬࡺࡹࡱࡧࠪ⒔"): bstack1lll1_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ⒕"),
            bstack1lll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ⒖"): hook_type,
            bstack1lll1_opy_ (u"ࠨࡪࡲࡳࡰࡥ࡮ࡢ࡯ࡨࠫ⒗"): hook_name
        }
        store[bstack1lll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⒘")].append(uuid)
        bstack1lll1l1ll1ll_opy_ = node.nodeid
        if hook_type == bstack1lll1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨ⒙"):
            if not _1111llllll_opy_.get(bstack1lll1l1ll1ll_opy_, None):
                _1111llllll_opy_[bstack1lll1l1ll1ll_opy_] = {bstack1lll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ⒚"): []}
            _1111llllll_opy_[bstack1lll1l1ll1ll_opy_][bstack1lll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⒛")].append(bstack111l111l1l_opy_[bstack1lll1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⒜")])
        _1111llllll_opy_[bstack1lll1l1ll1ll_opy_ + bstack1lll1_opy_ (u"ࠧ࠮ࠩ⒝") + hook_name] = bstack111l111l1l_opy_
        bstack1lll1lll1lll_opy_(node, bstack111l111l1l_opy_, bstack1lll1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⒞"))
    elif event == bstack1lll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨ⒟"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l11111_opy_[hook_type], bstack1ll1llll1ll_opy_.POST, node, None, bstack11llll1lll1_opy_)
            return
        bstack111l1llll1_opy_ = node.nodeid + bstack1lll1_opy_ (u"ࠪ࠱ࠬ⒠") + hook_name
        _1111llllll_opy_[bstack111l1llll1_opy_][bstack1lll1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⒡")] = bstack1111l11l_opy_()
        bstack1lll1ll1ll11_opy_(_1111llllll_opy_[bstack111l1llll1_opy_][bstack1lll1_opy_ (u"ࠬࡻࡵࡪࡦࠪ⒢")])
        bstack1lll1lll1lll_opy_(node, _1111llllll_opy_[bstack111l1llll1_opy_], bstack1lll1_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ⒣"), bstack1lll1ll11l11_opy_=bstack11llll1lll1_opy_)
def bstack1lll1lll11l1_opy_():
    global bstack1lll1l1llll1_opy_
    if bstack11lllll111_opy_():
        bstack1lll1l1llll1_opy_ = bstack1lll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠫ⒤")
    else:
        bstack1lll1l1llll1_opy_ = bstack1lll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ⒥")
def pytest_collection_modifyitems(session, config, items):
    bstack1lll1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡉ࡭ࡱࡺࡥࡳࡵࠣࡧࡴࡲ࡬ࡦࡥࡷࡩࡩࠦࡰࡺࡶࡨࡷࡹࠦࡩࡵࡧࡰࡷࠥࡨࡡࡴࡧࡧࠤࡴࡴࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷࡩࡩࠦࡳࡦ࡮ࡨࡧࡹࡵࡲࡴࠢࡩࡶࡴࡳࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡴࡧࡵࡺࡪࡸ࠮ࠋࠢࠣࠤࠥࠨࠢࠣ⒦")
    import os
    bstack1lll1lll1l11_opy_ = os.environ.get(bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡒࡖࡈࡎࡅࡔࡖࡕࡅ࡙ࡋࡄࡠࡕࡈࡐࡊࡉࡔࡐࡔࡖࠫ⒧"))
    if not bstack1lll1lll1l11_opy_:
        return
    try:
        bstack1lll1llll111_opy_ = json.loads(bstack1lll1lll1l11_opy_)
        if not isinstance(bstack1lll1llll111_opy_, (list, set)) or not bstack1lll1llll111_opy_:
            return
    except Exception as e:
        logger.debug(bstack1lll1_opy_ (u"ࠦࡈࡵࡵ࡭ࡦࠣࡲࡴࡺࠠࡱࡣࡵࡷࡪࠦࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡕࡒࡄࡊࡈࡗ࡙ࡘࡁࡕࡇࡇࡣࡘࡋࡌࡆࡅࡗࡓࡗ࡙࠺ࠡࠤ⒨") + str(e) + bstack1lll1_opy_ (u"ࠧࠨ⒩"))
        return
    selected = []
    deselected = []
    bstack1lll1ll1llll_opy_ = set()
    for selector in bstack1lll1llll111_opy_:
        if not selector or not isinstance(selector, str):
            continue
        bstack1lll1ll1llll_opy_.add(selector)
    for item in items:
        nodeid = getattr(item, bstack1lll1_opy_ (u"࠭࡮ࡰࡦࡨ࡭ࡩ࠭⒪"), None)
        if not nodeid:
            deselected.append(item)
            continue
        if (
            nodeid in bstack1lll1ll1llll_opy_ or
            any(sel in nodeid for sel in bstack1lll1ll1llll_opy_)
        ):
            selected.append(item)
        else:
            deselected.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
@bstack1lll11l1l_opy_.bstack1llll111lll1_opy_
def bstack1lll1lll111l_opy_():
    bstack1lll1lll11l1_opy_()
    if cli.is_running():
        try:
            bstack111ll111lll_opy_(bstack1lll1l1ll111_opy_)
        except Exception as e:
            logger.debug(bstack1lll1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࡷࠥࡶࡡࡵࡥ࡫࠾ࠥࢁࡽࠣ⒫").format(e))
        return
    if bstack1l1llllll1_opy_():
        bstack1l1111ll1_opy_ = Config.bstack1111l11l1_opy_()
        bstack1lll1_opy_ (u"ࠨࠩࠪࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡉࡳࡷࠦࡰࡱࡲࠣࡁࠥ࠷ࠬࠡ࡯ࡲࡨࡤ࡫ࡸࡦࡥࡸࡸࡪࠦࡧࡦࡶࡶࠤࡺࡹࡥࡥࠢࡩࡳࡷࠦࡡ࠲࠳ࡼࠤࡨࡵ࡭࡮ࡣࡱࡨࡸ࠳ࡷࡳࡣࡳࡴ࡮ࡴࡧࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡆࡰࡴࠣࡴࡵࡶࠠ࠿ࠢ࠴࠰ࠥࡳ࡯ࡥࡡࡨࡼࡪࡩࡵࡵࡧࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥࡸࡵ࡯ࠢࡥࡩࡨࡧࡵࡴࡧࠣ࡭ࡹࠦࡩࡴࠢࡳࡥࡹࡩࡨࡦࡦࠣ࡭ࡳࠦࡡࠡࡦ࡬ࡪ࡫࡫ࡲࡦࡰࡷࠤࡵࡸ࡯ࡤࡧࡶࡷࠥ࡯ࡤࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡔࡩࡷࡶࠤࡼ࡫ࠠ࡯ࡧࡨࡨࠥࡺ࡯ࠡࡷࡶࡩ࡙ࠥࡥ࡭ࡧࡱ࡭ࡺࡳࡐࡢࡶࡦ࡬࠭ࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࡟ࡩࡣࡱࡨࡱ࡫ࡲࠪࠢࡩࡳࡷࠦࡰࡱࡲࠣࡂࠥ࠷ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠩࠪࠫ⒬")
        if bstack1l1111ll1_opy_.get_property(bstack1lll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡰࡳࡩࡥࡣࡢ࡮࡯ࡩࡩ࠭⒭")):
            if CONFIG.get(bstack1lll1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ⒮")) is not None and int(CONFIG[bstack1lll1_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫ⒯")]) > 1:
                bstack1lll11llll_opy_(bstack11l1lll111_opy_)
            return
        bstack1lll11llll_opy_(bstack11l1lll111_opy_)
    try:
        bstack111ll111lll_opy_(bstack1lll1l1ll111_opy_)
    except Exception as e:
        logger.debug(bstack1lll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࡵࠣࡴࡦࡺࡣࡩ࠼ࠣࡿࢂࠨ⒰").format(e))
bstack1lll1lll111l_opy_()