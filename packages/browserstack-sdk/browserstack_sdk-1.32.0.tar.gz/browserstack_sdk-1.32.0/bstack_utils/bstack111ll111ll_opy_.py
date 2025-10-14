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
from uuid import uuid4
from bstack_utils.helper import bstack1111l11l_opy_, bstack111lllll11l_opy_
from bstack_utils.bstack11llll11ll_opy_ import bstack1llllll1llll_opy_
class bstack111l1l1l11_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1llll1llll1l_opy_=None, bstack1lllll111111_opy_=True, bstack1l1111l11l1_opy_=None, bstack11lll11l1_opy_=None, result=None, duration=None, bstack1111ll11l1_opy_=None, meta={}):
        self.bstack1111ll11l1_opy_ = bstack1111ll11l1_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1lllll111111_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1llll1llll1l_opy_ = bstack1llll1llll1l_opy_
        self.bstack1l1111l11l1_opy_ = bstack1l1111l11l1_opy_
        self.bstack11lll11l1_opy_ = bstack11lll11l1_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack1111l1ll1l_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111l1lll11_opy_(self, meta):
        self.meta = meta
    def bstack111l1lllll_opy_(self, hooks):
        self.hooks = hooks
    def bstack1llll1ll1ll1_opy_(self):
        bstack1lllll1111l1_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack1lll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭⁜"): bstack1lllll1111l1_opy_,
            bstack1lll1_opy_ (u"ࠫࡱࡵࡣࡢࡶ࡬ࡳࡳ࠭⁝"): bstack1lllll1111l1_opy_,
            bstack1lll1_opy_ (u"ࠬࡼࡣࡠࡨ࡬ࡰࡪࡶࡡࡵࡪࠪ⁞"): bstack1lllll1111l1_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack1lll1_opy_ (u"ࠨࡕ࡯ࡧࡻࡴࡪࡩࡴࡦࡦࠣࡥࡷ࡭ࡵ࡮ࡧࡱࡸ࠿ࠦࠢ ") + key)
            setattr(self, key, val)
    def bstack1lllll111ll1_opy_(self):
        return {
            bstack1lll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⁠"): self.name,
            bstack1lll1_opy_ (u"ࠨࡤࡲࡨࡾ࠭⁡"): {
                bstack1lll1_opy_ (u"ࠩ࡯ࡥࡳ࡭ࠧ⁢"): bstack1lll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ⁣"),
                bstack1lll1_opy_ (u"ࠫࡨࡵࡤࡦࠩ⁤"): self.code
            },
            bstack1lll1_opy_ (u"ࠬࡹࡣࡰࡲࡨࡷࠬ⁥"): self.scope,
            bstack1lll1_opy_ (u"࠭ࡴࡢࡩࡶࠫ⁦"): self.tags,
            bstack1lll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ⁧"): self.framework,
            bstack1lll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⁨"): self.started_at
        }
    def bstack1llll1lll11l_opy_(self):
        return {
         bstack1lll1_opy_ (u"ࠩࡰࡩࡹࡧࠧ⁩"): self.meta
        }
    def bstack1llll1lll1ll_opy_(self):
        return {
            bstack1lll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡕࡩࡷࡻ࡮ࡑࡣࡵࡥࡲ࠭⁪"): {
                bstack1lll1_opy_ (u"ࠫࡷ࡫ࡲࡶࡰࡢࡲࡦࡳࡥࠨ⁫"): self.bstack1llll1llll1l_opy_
            }
        }
    def bstack1lllll111l11_opy_(self, bstack1llll1lll111_opy_, details):
        step = next(filter(lambda st: st[bstack1lll1_opy_ (u"ࠬ࡯ࡤࠨ⁬")] == bstack1llll1lll111_opy_, self.meta[bstack1lll1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ⁭")]), None)
        step.update(details)
    def bstack1ll1l1l1_opy_(self, bstack1llll1lll111_opy_):
        step = next(filter(lambda st: st[bstack1lll1_opy_ (u"ࠧࡪࡦࠪ⁮")] == bstack1llll1lll111_opy_, self.meta[bstack1lll1_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ⁯")]), None)
        step.update({
            bstack1lll1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⁰"): bstack1111l11l_opy_()
        })
    def bstack111ll11l11_opy_(self, bstack1llll1lll111_opy_, result, duration=None):
        bstack1l1111l11l1_opy_ = bstack1111l11l_opy_()
        if bstack1llll1lll111_opy_ is not None and self.meta.get(bstack1lll1_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩⁱ")):
            step = next(filter(lambda st: st[bstack1lll1_opy_ (u"ࠫ࡮ࡪࠧ⁲")] == bstack1llll1lll111_opy_, self.meta[bstack1lll1_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫ⁳")]), None)
            step.update({
                bstack1lll1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⁴"): bstack1l1111l11l1_opy_,
                bstack1lll1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩ⁵"): duration if duration else bstack111lllll11l_opy_(step[bstack1lll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⁶")], bstack1l1111l11l1_opy_),
                bstack1lll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⁷"): result.result,
                bstack1lll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫ⁸"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1llll1llll11_opy_):
        if self.meta.get(bstack1lll1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ⁹")):
            self.meta[bstack1lll1_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫ⁺")].append(bstack1llll1llll11_opy_)
        else:
            self.meta[bstack1lll1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ⁻")] = [ bstack1llll1llll11_opy_ ]
    def bstack1llll1lllll1_opy_(self):
        return {
            bstack1lll1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⁼"): self.bstack1111l1ll1l_opy_(),
            **self.bstack1lllll111ll1_opy_(),
            **self.bstack1llll1ll1ll1_opy_(),
            **self.bstack1llll1lll11l_opy_()
        }
    def bstack1lllll1111ll_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack1lll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⁽"): self.bstack1l1111l11l1_opy_,
            bstack1lll1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ⁾"): self.duration,
            bstack1lll1_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪⁿ"): self.result.result
        }
        if data[bstack1lll1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ₀")] == bstack1lll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ₁"):
            data[bstack1lll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ₂")] = self.result.bstack1111111ll1_opy_()
            data[bstack1lll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨ₃")] = [{bstack1lll1_opy_ (u"ࠨࡤࡤࡧࡰࡺࡲࡢࡥࡨࠫ₄"): self.result.bstack11l111lllll_opy_()}]
        return data
    def bstack1lllll111l1l_opy_(self):
        return {
            bstack1lll1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ₅"): self.bstack1111l1ll1l_opy_(),
            **self.bstack1lllll111ll1_opy_(),
            **self.bstack1llll1ll1ll1_opy_(),
            **self.bstack1lllll1111ll_opy_(),
            **self.bstack1llll1lll11l_opy_()
        }
    def bstack1111ll1l11_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack1lll1_opy_ (u"ࠪࡗࡹࡧࡲࡵࡧࡧࠫ₆") in event:
            return self.bstack1llll1lllll1_opy_()
        elif bstack1lll1_opy_ (u"ࠫࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭₇") in event:
            return self.bstack1lllll111l1l_opy_()
    def bstack1111ll1lll_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1l1111l11l1_opy_ = time if time else bstack1111l11l_opy_()
        self.duration = duration if duration else bstack111lllll11l_opy_(self.started_at, self.bstack1l1111l11l1_opy_)
        if result:
            self.result = result
class bstack111ll1l111_opy_(bstack111l1l1l11_opy_):
    def __init__(self, hooks=[], bstack111lll11l1_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111lll11l1_opy_ = bstack111lll11l1_opy_
        super().__init__(*args, **kwargs, bstack11lll11l1_opy_=bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࠪ₈"))
    @classmethod
    def bstack1llll1lll1l1_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1lll1_opy_ (u"࠭ࡩࡥࠩ₉"): id(step),
                bstack1lll1_opy_ (u"ࠧࡵࡧࡻࡸࠬ₊"): step.name,
                bstack1lll1_opy_ (u"ࠨ࡭ࡨࡽࡼࡵࡲࡥࠩ₋"): step.keyword,
            })
        return bstack111ll1l111_opy_(
            **kwargs,
            meta={
                bstack1lll1_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࠪ₌"): {
                    bstack1lll1_opy_ (u"ࠪࡲࡦࡳࡥࠨ₍"): feature.name,
                    bstack1lll1_opy_ (u"ࠫࡵࡧࡴࡩࠩ₎"): feature.filename,
                    bstack1lll1_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪ₏"): feature.description
                },
                bstack1lll1_opy_ (u"࠭ࡳࡤࡧࡱࡥࡷ࡯࡯ࠨₐ"): {
                    bstack1lll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬₑ"): scenario.name
                },
                bstack1lll1_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧₒ"): steps,
                bstack1lll1_opy_ (u"ࠩࡨࡼࡦࡳࡰ࡭ࡧࡶࠫₓ"): bstack1llllll1llll_opy_(test)
            }
        )
    def bstack1llll1llllll_opy_(self):
        return {
            bstack1lll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩₔ"): self.hooks
        }
    def bstack1lllll11111l_opy_(self):
        if self.bstack111lll11l1_opy_:
            return {
                bstack1lll1_opy_ (u"ࠫ࡮ࡴࡴࡦࡩࡵࡥࡹ࡯࡯࡯ࡵࠪₕ"): self.bstack111lll11l1_opy_
            }
        return {}
    def bstack1lllll111l1l_opy_(self):
        return {
            **super().bstack1lllll111l1l_opy_(),
            **self.bstack1llll1llllll_opy_()
        }
    def bstack1llll1lllll1_opy_(self):
        return {
            **super().bstack1llll1lllll1_opy_(),
            **self.bstack1lllll11111l_opy_()
        }
    def bstack1111ll1lll_opy_(self):
        return bstack1lll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧₖ")
class bstack111lll111l_opy_(bstack111l1l1l11_opy_):
    def __init__(self, hook_type, *args,bstack111lll11l1_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1ll1111l11l_opy_ = None
        self.bstack111lll11l1_opy_ = bstack111lll11l1_opy_
        super().__init__(*args, **kwargs, bstack11lll11l1_opy_=bstack1lll1_opy_ (u"࠭ࡨࡰࡱ࡮ࠫₗ"))
    def bstack1111l1llll_opy_(self):
        return self.hook_type
    def bstack1llll1ll1lll_opy_(self):
        return {
            bstack1lll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪₘ"): self.hook_type
        }
    def bstack1lllll111l1l_opy_(self):
        return {
            **super().bstack1lllll111l1l_opy_(),
            **self.bstack1llll1ll1lll_opy_()
        }
    def bstack1llll1lllll1_opy_(self):
        return {
            **super().bstack1llll1lllll1_opy_(),
            bstack1lll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢ࡭ࡩ࠭ₙ"): self.bstack1ll1111l11l_opy_,
            **self.bstack1llll1ll1lll_opy_()
        }
    def bstack1111ll1lll_opy_(self):
        return bstack1lll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࠫₚ")
    def bstack111ll11111_opy_(self, bstack1ll1111l11l_opy_):
        self.bstack1ll1111l11l_opy_ = bstack1ll1111l11l_opy_