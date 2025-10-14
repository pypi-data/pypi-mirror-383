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
from browserstack_sdk.bstack111ll1l1_opy_ import bstack11ll1l111_opy_
from browserstack_sdk.bstack1111lllll1_opy_ import RobotHandler
def bstack1ll1l11ll_opy_(framework):
    if framework.lower() == bstack1lll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪᬎ"):
        return bstack11ll1l111_opy_.version()
    elif framework.lower() == bstack1lll1_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪᬏ"):
        return RobotHandler.version()
    elif framework.lower() == bstack1lll1_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬᬐ"):
        import behave
        return behave.__version__
    else:
        return bstack1lll1_opy_ (u"࠭ࡵ࡯࡭ࡱࡳࡼࡴࠧᬑ")
def bstack11l1ll11l_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack1lll1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩᬒ"))
        framework_version.append(importlib.metadata.version(bstack1lll1_opy_ (u"ࠣࡵࡨࡰࡪࡴࡩࡶ࡯ࠥᬓ")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack1lll1_opy_ (u"ࠩࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ᬔ"))
        framework_version.append(importlib.metadata.version(bstack1lll1_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᬕ")))
    except:
        pass
    return {
        bstack1lll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩᬖ"): bstack1lll1_opy_ (u"ࠬࡥࠧᬗ").join(framework_name),
        bstack1lll1_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧᬘ"): bstack1lll1_opy_ (u"ࠧࡠࠩᬙ").join(framework_version)
    }