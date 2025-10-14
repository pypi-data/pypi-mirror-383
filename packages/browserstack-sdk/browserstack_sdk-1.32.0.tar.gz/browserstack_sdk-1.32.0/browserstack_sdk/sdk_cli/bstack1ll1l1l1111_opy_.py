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
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import bstack1lll111l11l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1lllll11ll1_opy_,
    bstack1llllll1l11_opy_,
    bstack1llllll111l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll11l111l_opy_ import bstack1ll1ll11ll1_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1lllllll1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack1l1ll11l11_opy_ import bstack1ll1l1lll1l_opy_
class bstack1llll11111l_opy_(bstack1lll111l11l_opy_):
    bstack1l11ll11lll_opy_ = bstack1lll1_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠ࡫ࡱ࡭ࡹࠨ፾")
    bstack1l11l1ll111_opy_ = bstack1lll1_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡦࡸࡴࠣ፿")
    bstack1l11ll111ll_opy_ = bstack1lll1_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢࡷࡹࡵࡰࠣᎀ")
    def __init__(self, bstack1ll1ll1lll1_opy_):
        super().__init__()
        bstack1ll1ll11ll1_opy_.bstack1ll11lllll1_opy_((bstack1lllll11ll1_opy_.bstack1llll1l11l1_opy_, bstack1llllll1l11_opy_.PRE), self.bstack1l11l1lll11_opy_)
        bstack1ll1ll11ll1_opy_.bstack1ll11lllll1_opy_((bstack1lllll11ll1_opy_.bstack1lllllll1ll_opy_, bstack1llllll1l11_opy_.PRE), self.bstack1l1llllll11_opy_)
        bstack1ll1ll11ll1_opy_.bstack1ll11lllll1_opy_((bstack1lllll11ll1_opy_.bstack1lllllll1ll_opy_, bstack1llllll1l11_opy_.POST), self.bstack1l11ll11l1l_opy_)
        bstack1ll1ll11ll1_opy_.bstack1ll11lllll1_opy_((bstack1lllll11ll1_opy_.bstack1lllllll1ll_opy_, bstack1llllll1l11_opy_.POST), self.bstack1l11ll1llll_opy_)
        bstack1ll1ll11ll1_opy_.bstack1ll11lllll1_opy_((bstack1lllll11ll1_opy_.QUIT, bstack1llllll1l11_opy_.POST), self.bstack1l11ll1l111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l1lll11_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        driver: object,
        exec: Tuple[bstack1llllll111l_opy_, str],
        bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1lll1_opy_ (u"ࠤࡢࡣ࡮ࡴࡩࡵࡡࡢࠦᎁ"):
            return
        def wrapped(driver, init, *args, **kwargs):
            url = None
            try:
                if isinstance(kwargs.get(bstack1lll1_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᎂ")), str):
                    url = kwargs.get(bstack1lll1_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᎃ"))
                elif hasattr(kwargs.get(bstack1lll1_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᎄ")), bstack1lll1_opy_ (u"࠭࡟ࡤ࡮࡬ࡩࡳࡺ࡟ࡤࡱࡱࡪ࡮࡭ࠧᎅ")):
                    url = kwargs.get(bstack1lll1_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡠࡧࡻࡩࡨࡻࡴࡰࡴࠥᎆ"))._client_config.remote_server_addr
                else:
                    url = kwargs.get(bstack1lll1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᎇ"))._url
            except Exception as e:
                url = bstack1lll1_opy_ (u"ࠩࠪᎈ")
                self.logger.error(bstack1lll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡸࡶࡱࠦࡦࡳࡱࡰࠤࡩࡸࡩࡷࡧࡵ࠾ࠥࢁࡽࠣᎉ").format(e))
            self.logger.info(bstack1lll1_opy_ (u"ࠦࡗ࡫࡭ࡰࡶࡨࠤࡘ࡫ࡲࡷࡧࡵࠤࡆࡪࡤࡳࡧࡶࡷࠥࡨࡥࡪࡰࡪࠤࡵࡧࡳࡴࡧࡧࠤࡦࡹࠠ࠻ࠢࡾࢁࠧᎊ").format(str(url)))
            self.bstack1l11ll1lll1_opy_(instance, url, f, kwargs)
            self.logger.info(bstack1lll1_opy_ (u"ࠧࡪࡲࡪࡸࡨࡶ࠳ࢁ࡭ࡦࡶ࡫ࡳࡩࡥ࡮ࡢ࡯ࡨࢁࠥࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࡻࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࡾ࠼ࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥᎋ").format(method_name=method_name, platform_index=f.platform_index, args=args, kwargs=kwargs))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
    def bstack1l1llllll11_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        driver: object,
        exec: Tuple[bstack1llllll111l_opy_, str],
        bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if f.bstack1llll1ll1ll_opy_(instance, bstack1llll11111l_opy_.bstack1l11ll11lll_opy_, False):
            return
        if not f.bstack1llll1l1111_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1ll11111ll1_opy_):
            return
        platform_index = f.bstack1llll1ll1ll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1ll11111ll1_opy_)
        if f.bstack1ll11l1lll1_opy_(method_name, *args) and len(args) > 1:
            bstack1l111111l1_opy_ = datetime.now()
            hub_url = bstack1ll1ll11ll1_opy_.hub_url(driver)
            self.logger.warning(bstack1lll1_opy_ (u"ࠨࡨࡶࡤࡢࡹࡷࡲ࠽ࠣᎌ") + str(hub_url) + bstack1lll1_opy_ (u"ࠢࠣᎍ"))
            bstack1l11l1l1ll1_opy_ = args[1][bstack1lll1_opy_ (u"ࠣࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢᎎ")] if isinstance(args[1], dict) and bstack1lll1_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᎏ") in args[1] else None
            bstack1l11l1l1l1l_opy_ = bstack1lll1_opy_ (u"ࠥࡥࡱࡽࡡࡺࡵࡐࡥࡹࡩࡨࠣ᎐")
            if isinstance(bstack1l11l1l1ll1_opy_, dict):
                bstack1l111111l1_opy_ = datetime.now()
                r = self.bstack1l11ll11111_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack1lll1lll11_opy_(bstack1lll1_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡵࡩ࡬࡯ࡳࡵࡧࡵࡣ࡮ࡴࡩࡵࠤ᎑"), datetime.now() - bstack1l111111l1_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack1lll1_opy_ (u"ࠧࡹ࡯࡮ࡧࡷ࡬࡮ࡴࡧࠡࡹࡨࡲࡹࠦࡷࡳࡱࡱ࡫࠿ࠦࠢ᎒") + str(r) + bstack1lll1_opy_ (u"ࠨࠢ᎓"))
                        return
                    if r.hub_url:
                        f.bstack1l11ll11ll1_opy_(instance, driver, r.hub_url)
                        f.bstack1llll1ll111_opy_(instance, bstack1llll11111l_opy_.bstack1l11ll11lll_opy_, True)
                except Exception as e:
                    self.logger.error(bstack1lll1_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨ᎔"), e)
    def bstack1l11ll11l1l_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        driver: object,
        exec: Tuple[bstack1llllll111l_opy_, str],
        bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1ll1ll11ll1_opy_.session_id(driver)
            if session_id:
                bstack1l11ll11l11_opy_ = bstack1lll1_opy_ (u"ࠣࡽࢀ࠾ࡸࡺࡡࡳࡶࠥ᎕").format(session_id)
                bstack1ll1l1lll1l_opy_.mark(bstack1l11ll11l11_opy_)
    def bstack1l11ll1llll_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        driver: object,
        exec: Tuple[bstack1llllll111l_opy_, str],
        bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if f.bstack1llll1ll1ll_opy_(instance, bstack1llll11111l_opy_.bstack1l11l1ll111_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1ll1ll11ll1_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack1lll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤ࡭ࡻࡢࡠࡷࡵࡰࡂࠨ᎖") + str(hub_url) + bstack1lll1_opy_ (u"ࠥࠦ᎗"))
            return
        framework_session_id = bstack1ll1ll11ll1_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack1lll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡱࡣࡵࡷࡪࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࡃࠢ᎘") + str(framework_session_id) + bstack1lll1_opy_ (u"ࠧࠨ᎙"))
            return
        if bstack1ll1ll11ll1_opy_.bstack1l11l1l1lll_opy_(*args) == bstack1ll1ll11ll1_opy_.bstack1l11lll1111_opy_:
            bstack1l11ll1ll11_opy_ = bstack1lll1_opy_ (u"ࠨࡻࡾ࠼ࡨࡲࡩࠨ᎚").format(framework_session_id)
            bstack1l11ll11l11_opy_ = bstack1lll1_opy_ (u"ࠢࡼࡿ࠽ࡷࡹࡧࡲࡵࠤ᎛").format(framework_session_id)
            bstack1ll1l1lll1l_opy_.end(
                label=bstack1lll1_opy_ (u"ࠣࡵࡧ࡯࠿ࡪࡲࡪࡸࡨࡶ࠿ࡶ࡯ࡴࡶ࠰࡭ࡳ࡯ࡴࡪࡣ࡯࡭ࡿࡧࡴࡪࡱࡱࠦ᎜"),
                start=bstack1l11ll11l11_opy_,
                end=bstack1l11ll1ll11_opy_,
                status=True,
                failure=None
            )
            bstack1l111111l1_opy_ = datetime.now()
            r = self.bstack1l11ll111l1_opy_(
                ref,
                f.bstack1llll1ll1ll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1ll11111ll1_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack1lll1lll11_opy_(bstack1lll1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡦࡸࡴࠣ᎝"), datetime.now() - bstack1l111111l1_opy_)
            f.bstack1llll1ll111_opy_(instance, bstack1llll11111l_opy_.bstack1l11l1ll111_opy_, r.success)
    def bstack1l11ll1l111_opy_(
        self,
        f: bstack1ll1ll11ll1_opy_,
        driver: object,
        exec: Tuple[bstack1llllll111l_opy_, str],
        bstack1lllll1l111_opy_: Tuple[bstack1lllll11ll1_opy_, bstack1llllll1l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if f.bstack1llll1ll1ll_opy_(instance, bstack1llll11111l_opy_.bstack1l11ll111ll_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1ll1ll11ll1_opy_.session_id(driver)
        hub_url = bstack1ll1ll11ll1_opy_.hub_url(driver)
        bstack1l111111l1_opy_ = datetime.now()
        r = self.bstack1l11l1ll1ll_opy_(
            ref,
            f.bstack1llll1ll1ll_opy_(instance, bstack1ll1ll11ll1_opy_.bstack1ll11111ll1_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack1lll1lll11_opy_(bstack1lll1_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡴࡨ࡫࡮ࡹࡴࡦࡴࡢࡷࡹࡵࡰࠣ᎞"), datetime.now() - bstack1l111111l1_opy_)
        f.bstack1llll1ll111_opy_(instance, bstack1llll11111l_opy_.bstack1l11ll111ll_opy_, r.success)
    @measure(event_name=EVENTS.bstack1ll11llll_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def bstack1l1l111l1ll_opy_(self, platform_index: int, url: str, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        req.hub_url = url
        self.logger.debug(bstack1lll1_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡷࡦࡤࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲ࡮ࡺ࠺ࠡࠤ᎟") + str(req) + bstack1lll1_opy_ (u"ࠧࠨᎠ"))
        try:
            r = self.bstack1ll1ll1l1l1_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1lll1_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࡴࡷࡦࡧࡪࡹࡳ࠾ࠤᎡ") + str(r.success) + bstack1lll1_opy_ (u"ࠢࠣᎢ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᎣ") + str(e) + bstack1lll1_opy_ (u"ࠤࠥᎤ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1ll1l1_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def bstack1l11ll11111_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1ll11l11ll1_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack1lll1_opy_ (u"ࠥࡶࡪ࡭ࡩࡴࡶࡨࡶࡤ࡯࡮ࡪࡶ࠽ࠤࠧᎥ") + str(req) + bstack1lll1_opy_ (u"ࠦࠧᎦ"))
        try:
            r = self.bstack1ll1ll1l1l1_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack1lll1_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࡳࡶࡥࡦࡩࡸࡹ࠽ࠣᎧ") + str(r.success) + bstack1lll1_opy_ (u"ࠨࠢᎨ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧᎩ") + str(e) + bstack1lll1_opy_ (u"ࠣࠤᎪ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11ll1ll1l_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def bstack1l11ll111l1_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll11l11ll1_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1lll1_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡸࡺࡡࡳࡶ࠽ࠤࠧᎫ") + str(req) + bstack1lll1_opy_ (u"ࠥࠦᎬ"))
        try:
            r = self.bstack1ll1ll1l1l1_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack1lll1_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨᎭ") + str(r) + bstack1lll1_opy_ (u"ࠧࠨᎮ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᎯ") + str(e) + bstack1lll1_opy_ (u"ࠢࠣᎰ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1lll1l_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def bstack1l11l1ll1ll_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll11l11ll1_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1lll1_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢࡷࡹࡵࡰ࠻ࠢࠥᎱ") + str(req) + bstack1lll1_opy_ (u"ࠤࠥᎲ"))
        try:
            r = self.bstack1ll1ll1l1l1_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack1lll1_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࠧᎳ") + str(r) + bstack1lll1_opy_ (u"ࠦࠧᎴ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᎵ") + str(e) + bstack1lll1_opy_ (u"ࠨࠢᎶ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack11llll1ll_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def bstack1l11ll1lll1_opy_(self, instance: bstack1llllll111l_opy_, url: str, f: bstack1ll1ll11ll1_opy_, kwargs):
        bstack1l11ll1l1l1_opy_ = version.parse(f.framework_version)
        bstack1l11l1lllll_opy_ = kwargs.get(bstack1lll1_opy_ (u"ࠢࡰࡲࡷ࡭ࡴࡴࡳࠣᎷ"))
        bstack1l11l1ll11l_opy_ = kwargs.get(bstack1lll1_opy_ (u"ࠣࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᎸ"))
        bstack1l1l11111ll_opy_ = {}
        bstack1l11l1llll1_opy_ = {}
        bstack1l11ll1l11l_opy_ = None
        bstack1l11ll1111l_opy_ = {}
        if bstack1l11l1ll11l_opy_ is not None or bstack1l11l1lllll_opy_ is not None: # check top level caps
            if bstack1l11l1ll11l_opy_ is not None:
                bstack1l11ll1111l_opy_[bstack1lll1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᎹ")] = bstack1l11l1ll11l_opy_
            if bstack1l11l1lllll_opy_ is not None and callable(getattr(bstack1l11l1lllll_opy_, bstack1lll1_opy_ (u"ࠥࡸࡴࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᎺ"))):
                bstack1l11ll1111l_opy_[bstack1lll1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࡤࡧࡳࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᎻ")] = bstack1l11l1lllll_opy_.to_capabilities()
        response = self.bstack1l1l111l1ll_opy_(f.platform_index, url, instance.ref(), json.dumps(bstack1l11ll1111l_opy_).encode(bstack1lll1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᎼ")))
        if response is not None and response.capabilities:
            bstack1l1l11111ll_opy_ = json.loads(response.capabilities.decode(bstack1lll1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᎽ")))
            if not bstack1l1l11111ll_opy_: # empty caps bstack1l1l11l111l_opy_ bstack1l1l11l11ll_opy_ bstack1l1l111l1l1_opy_ bstack1lll1111111_opy_ or error in processing
                return
            bstack1l11ll1l11l_opy_ = f.bstack1lll1l1l1ll_opy_[bstack1lll1_opy_ (u"ࠢࡤࡴࡨࡥࡹ࡫࡟ࡰࡲࡷ࡭ࡴࡴࡳࡠࡨࡵࡳࡲࡥࡣࡢࡲࡶࠦᎾ")](bstack1l1l11111ll_opy_)
        if bstack1l11l1lllll_opy_ is not None and bstack1l11ll1l1l1_opy_ >= version.parse(bstack1lll1_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧᎿ")):
            bstack1l11l1llll1_opy_ = None
        if (
                not bstack1l11l1lllll_opy_ and not bstack1l11l1ll11l_opy_
        ) or (
                bstack1l11ll1l1l1_opy_ < version.parse(bstack1lll1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨᏀ"))
        ):
            bstack1l11l1llll1_opy_ = {}
            bstack1l11l1llll1_opy_.update(bstack1l1l11111ll_opy_)
        self.logger.info(bstack1lllllll1_opy_)
        if os.environ.get(bstack1lll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓࠨᏁ")).lower().__eq__(bstack1lll1_opy_ (u"ࠦࡹࡸࡵࡦࠤᏂ")):
            kwargs.update(
                {
                    bstack1lll1_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᏃ"): f.bstack1l11ll1l1ll_opy_,
                }
            )
        if bstack1l11ll1l1l1_opy_ >= version.parse(bstack1lll1_opy_ (u"࠭࠴࠯࠳࠳࠲࠵࠭Ꮔ")):
            if bstack1l11l1ll11l_opy_ is not None:
                del kwargs[bstack1lll1_opy_ (u"ࠢࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢᏅ")]
            kwargs.update(
                {
                    bstack1lll1_opy_ (u"ࠣࡱࡳࡸ࡮ࡵ࡮ࡴࠤᏆ"): bstack1l11ll1l11l_opy_,
                    bstack1lll1_opy_ (u"ࠤ࡮ࡩࡪࡶ࡟ࡢ࡮࡬ࡺࡪࠨᏇ"): True,
                    bstack1lll1_opy_ (u"ࠥࡪ࡮ࡲࡥࡠࡦࡨࡸࡪࡩࡴࡰࡴࠥᏈ"): None,
                }
            )
        elif bstack1l11ll1l1l1_opy_ >= version.parse(bstack1lll1_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪᏉ")):
            kwargs.update(
                {
                    bstack1lll1_opy_ (u"ࠧࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᏊ"): bstack1l11l1llll1_opy_,
                    bstack1lll1_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡳࡳࡹࠢᏋ"): bstack1l11ll1l11l_opy_,
                    bstack1lll1_opy_ (u"ࠢ࡬ࡧࡨࡴࡤࡧ࡬ࡪࡸࡨࠦᏌ"): True,
                    bstack1lll1_opy_ (u"ࠣࡨ࡬ࡰࡪࡥࡤࡦࡶࡨࡧࡹࡵࡲࠣᏍ"): None,
                }
            )
        elif bstack1l11ll1l1l1_opy_ >= version.parse(bstack1lll1_opy_ (u"ࠩ࠵࠲࠺࠹࠮࠱ࠩᏎ")):
            kwargs.update(
                {
                    bstack1lll1_opy_ (u"ࠥࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᏏ"): bstack1l11l1llll1_opy_,
                    bstack1lll1_opy_ (u"ࠦࡰ࡫ࡥࡱࡡࡤࡰ࡮ࡼࡥࠣᏐ"): True,
                    bstack1lll1_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡢࡨࡪࡺࡥࡤࡶࡲࡶࠧᏑ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack1lll1_opy_ (u"ࠨࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᏒ"): bstack1l11l1llll1_opy_,
                    bstack1lll1_opy_ (u"ࠢ࡬ࡧࡨࡴࡤࡧ࡬ࡪࡸࡨࠦᏓ"): True,
                    bstack1lll1_opy_ (u"ࠣࡨ࡬ࡰࡪࡥࡤࡦࡶࡨࡧࡹࡵࡲࠣᏔ"): None,
                }
            )