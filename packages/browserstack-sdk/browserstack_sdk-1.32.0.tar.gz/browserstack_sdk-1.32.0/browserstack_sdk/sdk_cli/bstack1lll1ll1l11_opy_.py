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
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import bstack1lll111l11l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll11lll_opy_ import (
    bstack1lllll11ll1_opy_,
    bstack1llllll1l11_opy_,
    bstack1llllll111l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll11l111l_opy_ import bstack1ll1ll11ll1_opy_
from typing import Tuple, Callable, Any
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll1llllll_opy_ import bstack1lll111l11l_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import traceback
import os
import time
class bstack1lll1l1111l_opy_(bstack1lll111l11l_opy_):
    bstack1ll11lll1l1_opy_ = False
    def __init__(self):
        super().__init__()
        bstack1ll1ll11ll1_opy_.bstack1ll11lllll1_opy_((bstack1lllll11ll1_opy_.bstack1lllllll1ll_opy_, bstack1llllll1l11_opy_.PRE), self.bstack1l1llllll11_opy_)
    def is_enabled(self) -> bool:
        return True
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
        hub_url = f.hub_url(driver)
        if f.bstack1ll11111111_opy_(hub_url):
            if not bstack1lll1l1111l_opy_.bstack1ll11lll1l1_opy_:
                self.logger.warning(bstack1lll1_opy_ (u"ࠦࡱࡵࡣࡢ࡮ࠣࡷࡪࡲࡦ࠮ࡪࡨࡥࡱࠦࡦ࡭ࡱࡺࠤࡩ࡯ࡳࡢࡤ࡯ࡩࡩࠦࡦࡰࡴࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢ࡬ࡲ࡫ࡸࡡࠡࡵࡨࡷࡸ࡯࡯࡯ࡵࠣ࡬ࡺࡨ࡟ࡶࡴ࡯ࡁࠧሺ") + str(hub_url) + bstack1lll1_opy_ (u"ࠧࠨሻ"))
                bstack1lll1l1111l_opy_.bstack1ll11lll1l1_opy_ = True
            return
        command_name = f.bstack1ll1111ll1l_opy_(*args)
        bstack1l1lllll1l1_opy_ = f.bstack1l1llllllll_opy_(*args)
        if command_name and command_name.lower() == bstack1lll1_opy_ (u"ࠨࡦࡪࡰࡧࡩࡱ࡫࡭ࡦࡰࡷࠦሼ") and bstack1l1lllll1l1_opy_:
            framework_session_id = f.session_id(driver)
            locator_type, locator_value = bstack1l1lllll1l1_opy_.get(bstack1lll1_opy_ (u"ࠢࡶࡵ࡬ࡲ࡬ࠨሽ"), None), bstack1l1lllll1l1_opy_.get(bstack1lll1_opy_ (u"ࠣࡸࡤࡰࡺ࡫ࠢሾ"), None)
            if not framework_session_id or not locator_type or not locator_value:
                self.logger.warning(bstack1lll1_opy_ (u"ࠤࡾࡧࡴࡳ࡭ࡢࡰࡧࡣࡳࡧ࡭ࡦࡿ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠥࡵࡲࠡࡣࡵ࡫ࡸ࠴ࡵࡴ࡫ࡱ࡫ࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࢂࠦ࡯ࡳࠢࡤࡶ࡬ࡹ࠮ࡷࡣ࡯ࡹࡪࡃࠢሿ") + str(locator_value) + bstack1lll1_opy_ (u"ࠥࠦቀ"))
                return
            def bstack1llllll1111_opy_(driver, bstack1ll111111l1_opy_, *args, **kwargs):
                from selenium.common.exceptions import NoSuchElementException
                try:
                    result = bstack1ll111111l1_opy_(driver, *args, **kwargs)
                    response = self.bstack1l1lllllll1_opy_(
                        framework_session_id=framework_session_id,
                        is_success=True,
                        locator_type=locator_type,
                        locator_value=locator_value,
                    )
                    if response and response.execute_script:
                        driver.execute_script(response.execute_script)
                        self.logger.info(bstack1lll1_opy_ (u"ࠦࡸࡻࡣࡤࡧࡶࡷ࠲ࡹࡣࡳ࡫ࡳࡸ࠿ࠦ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࢂࠦ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࡃࠢቁ") + str(locator_value) + bstack1lll1_opy_ (u"ࠧࠨቂ"))
                    else:
                        self.logger.warning(bstack1lll1_opy_ (u"ࠨࡳࡶࡥࡦࡩࡸࡹ࠭࡯ࡱ࠰ࡷࡨࡸࡩࡱࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࢂࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠾ࠤቃ") + str(response) + bstack1lll1_opy_ (u"ࠢࠣቄ"))
                    return result
                except NoSuchElementException as e:
                    locator = (locator_type, locator_value)
                    return self.__1ll1111111l_opy_(
                        driver, bstack1ll111111l1_opy_, e, framework_session_id, locator, *args, **kwargs
                    )
            bstack1llllll1111_opy_.__name__ = command_name
            return bstack1llllll1111_opy_
    def __1ll1111111l_opy_(
        self,
        driver,
        bstack1ll111111l1_opy_: Callable,
        exception,
        framework_session_id: str,
        locator: Tuple[str, str],
        *args,
        **kwargs,
    ):
        try:
            locator_type, locator_value = locator
            response = self.bstack1l1lllllll1_opy_(
                framework_session_id=framework_session_id,
                is_success=False,
                locator_type=locator_type,
                locator_value=locator_value,
            )
            if response and response.execute_script:
                driver.execute_script(response.execute_script)
                self.logger.info(bstack1lll1_opy_ (u"ࠣࡨࡤ࡭ࡱࡻࡲࡦ࠯࡫ࡩࡦࡲࡩ࡯ࡩ࠰ࡸࡷ࡯ࡧࡨࡧࡵࡩࡩࡀࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫࠽ࠣቅ") + str(locator_value) + bstack1lll1_opy_ (u"ࠤࠥቆ"))
                bstack1l1lllll11l_opy_ = self.bstack1l1llllll1l_opy_(
                    framework_session_id=framework_session_id,
                    locator_type=locator_type,
                )
                self.logger.info(bstack1lll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡶࡴࡨ࠱࡭࡫ࡡ࡭࡫ࡱ࡫࠲ࡸࡥࡴࡷ࡯ࡸ࠿ࠦ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࡂࢁ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡵࡻࡳࡩࢂࠦ࡬ࡰࡥࡤࡸࡴࡸ࡟ࡷࡣ࡯ࡹࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫ࡽࠡࡪࡨࡥࡱ࡯࡮ࡨࡡࡵࡩࡸࡻ࡬ࡵ࠿ࠥቇ") + str(bstack1l1lllll11l_opy_) + bstack1lll1_opy_ (u"ࠦࠧቈ"))
                if bstack1l1lllll11l_opy_.success and args and len(args) > 1:
                    args[1].update(
                        {
                            bstack1lll1_opy_ (u"ࠧࡻࡳࡪࡰࡪࠦ቉"): bstack1l1lllll11l_opy_.locator_type,
                            bstack1lll1_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧቊ"): bstack1l1lllll11l_opy_.locator_value,
                        }
                    )
                    return bstack1ll111111l1_opy_(driver, *args, **kwargs)
                elif os.environ.get(bstack1lll1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡊࡡࡇࡉࡇ࡛ࡇࠣቋ"), False):
                    self.logger.info(bstack1111l1l1ll_opy_ (u"ࠣࡨࡤ࡭ࡱࡻࡲࡦ࠯࡫ࡩࡦࡲࡩ࡯ࡩ࠰ࡶࡪࡹࡵ࡭ࡶ࠰ࡱ࡮ࡹࡳࡪࡰࡪ࠾ࠥࡹ࡬ࡦࡧࡳࠬ࠸࠶ࠩࠡ࡮ࡨࡸࡹ࡯࡮ࡨࠢࡼࡳࡺࠦࡩ࡯ࡵࡳࡩࡨࡺࠠࡵࡪࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࠥ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࠡ࡮ࡲ࡫ࡸࠨቌ"))
                    time.sleep(300)
            else:
                self.logger.warning(bstack1lll1_opy_ (u"ࠤࡩࡥ࡮ࡲࡵࡳࡧ࠰ࡲࡴ࠳ࡳࡤࡴ࡬ࡴࡹࡀࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࡃࡻ࡭ࡱࡦࡥࡹࡵࡲࡠࡶࡼࡴࡪࢃࠠ࡭ࡱࡦࡥࡹࡵࡲࡠࡸࡤࡰࡺ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥࡾࠢࡵࡩࡸࡶ࡯࡯ࡵࡨࡁࠧቍ") + str(response) + bstack1lll1_opy_ (u"ࠥࠦ቎"))
        except Exception as err:
            self.logger.warning(bstack1lll1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡷࡵࡩ࠲࡮ࡥࡢ࡮࡬ࡲ࡬࠳ࡲࡦࡵࡸࡰࡹࡀࠠࡦࡴࡵࡳࡷࡀࠠࠣ቏") + str(err) + bstack1lll1_opy_ (u"ࠧࠨቐ"))
        raise exception
    @measure(event_name=EVENTS.bstack1l1lllll1ll_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def bstack1l1lllllll1_opy_(
        self,
        framework_session_id: str,
        is_success: bool,
        locator_type: str,
        locator_value: str,
        platform_index=bstack1lll1_opy_ (u"ࠨ࠰ࠣቑ"),
    ):
        self.bstack1ll11l11ll1_opy_()
        req = structs.AISelfHealStepRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.is_success = is_success
        req.test_name = bstack1lll1_opy_ (u"ࠢࠣቒ")
        req.locator_type = locator_type
        req.locator_value = locator_value
        try:
            r = self.bstack1ll1ll1l1l1_opy_.AISelfHealStep(req)
            self.logger.info(bstack1lll1_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࠥቓ") + str(r) + bstack1lll1_opy_ (u"ࠤࠥቔ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣቕ") + str(e) + bstack1lll1_opy_ (u"ࠦࠧቖ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1lllll111_opy_, stage=STAGE.bstack11ll11ll1l_opy_)
    def bstack1l1llllll1l_opy_(self, framework_session_id: str, locator_type: str, platform_index=bstack1lll1_opy_ (u"ࠧ࠶ࠢ቗")):
        self.bstack1ll11l11ll1_opy_()
        req = structs.AISelfHealGetRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.locator_type = locator_type
        try:
            r = self.bstack1ll1ll1l1l1_opy_.AISelfHealGetResult(req)
            self.logger.info(bstack1lll1_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣቘ") + str(r) + bstack1lll1_opy_ (u"ࠢࠣ቙"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1lll1_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨቚ") + str(e) + bstack1lll1_opy_ (u"ࠤࠥቛ"))
            traceback.print_exc()
            raise e