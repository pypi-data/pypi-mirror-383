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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1l1ll1l1_opy_, bstack11l1l1lll1l_opy_, bstack11l1lll11l1_opy_
import tempfile
import json
bstack111l1l11l1l_opy_ = os.getenv(bstack1lll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡋࡤࡌࡉࡍࡇࠥᶻ"), None) or os.path.join(tempfile.gettempdir(), bstack1lll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠧᶼ"))
bstack111l1ll1l1l_opy_ = os.path.join(bstack1lll1_opy_ (u"ࠦࡱࡵࡧࠣᶽ"), bstack1lll1_opy_ (u"ࠬࡹࡤ࡬࠯ࡦࡰ࡮࠳ࡤࡦࡤࡸ࡫࠳ࡲ࡯ࡨࠩᶾ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack1lll1_opy_ (u"࠭ࠥࠩࡣࡶࡧࡹ࡯࡭ࡦࠫࡶࠤࡠࠫࠨ࡯ࡣࡰࡩ࠮ࡹ࡝࡜ࠧࠫࡰࡪࡼࡥ࡭ࡰࡤࡱࡪ࠯ࡳ࡞ࠢ࠰ࠤࠪ࠮࡭ࡦࡵࡶࡥ࡬࡫ࠩࡴࠩᶿ"),
      datefmt=bstack1lll1_opy_ (u"࡛ࠧࠦ࠰ࠩࡲ࠳ࠥࡥࡖࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࡞ࠬ᷀"),
      stream=sys.stdout
    )
  return logger
def bstack1ll1l1l111l_opy_():
  bstack111l1ll11l1_opy_ = os.environ.get(bstack1lll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡅࡇࡅ࡙ࡌࠨ᷁"), bstack1lll1_opy_ (u"ࠤࡩࡥࡱࡹࡥ᷂ࠣ"))
  return logging.DEBUG if bstack111l1ll11l1_opy_.lower() == bstack1lll1_opy_ (u"ࠥࡸࡷࡻࡥࠣ᷃") else logging.INFO
def bstack1l1l1lll111_opy_():
  global bstack111l1l11l1l_opy_
  if os.path.exists(bstack111l1l11l1l_opy_):
    os.remove(bstack111l1l11l1l_opy_)
  if os.path.exists(bstack111l1ll1l1l_opy_):
    os.remove(bstack111l1ll1l1l_opy_)
def bstack1l1llll1l_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l1l1l111_opy_ = log_level
  if bstack1lll1_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭᷄") in config and config[bstack1lll1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧ᷅")] in bstack11l1l1lll1l_opy_:
    bstack111l1l1l111_opy_ = bstack11l1l1lll1l_opy_[config[bstack1lll1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨ᷆")]]
  if config.get(bstack1lll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩ᷇"), False):
    logging.getLogger().setLevel(bstack111l1l1l111_opy_)
    return bstack111l1l1l111_opy_
  global bstack111l1l11l1l_opy_
  bstack1l1llll1l_opy_()
  bstack111l1l111l1_opy_ = logging.Formatter(
    fmt=bstack1lll1_opy_ (u"ࠨࠧࠫࡥࡸࡩࡴࡪ࡯ࡨ࠭ࡸ࡛ࠦࠦࠪࡱࡥࡲ࡫ࠩࡴ࡟࡞ࠩ࠭ࡲࡥࡷࡧ࡯ࡲࡦࡳࡥࠪࡵࡠࠤ࠲ࠦࠥࠩ࡯ࡨࡷࡸࡧࡧࡦࠫࡶࠫ᷈"),
    datefmt=bstack1lll1_opy_ (u"ࠩࠨ࡝࠲ࠫ࡭࠮ࠧࡧࡘࠪࡎ࠺ࠦࡏ࠽ࠩࡘࡠࠧ᷉"),
  )
  bstack111l1l11111_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l1l11l1l_opy_)
  file_handler.setFormatter(bstack111l1l111l1_opy_)
  bstack111l1l11111_opy_.setFormatter(bstack111l1l111l1_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l1l11111_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack1lll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࠳ࡽࡥࡣࡦࡵ࡭ࡻ࡫ࡲ࠯ࡴࡨࡱࡴࡺࡥ࠯ࡴࡨࡱࡴࡺࡥࡠࡥࡲࡲࡳ࡫ࡣࡵ࡫ࡲࡲ᷊ࠬ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l1l11111_opy_.setLevel(bstack111l1l1l111_opy_)
  logging.getLogger().addHandler(bstack111l1l11111_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l1l1l111_opy_
def bstack111l1ll1111_opy_(config):
  try:
    bstack111l1l1ll1l_opy_ = set(bstack11l1lll11l1_opy_)
    bstack111l1ll111l_opy_ = bstack1lll1_opy_ (u"ࠫࠬ᷋")
    with open(bstack1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨ᷌")) as bstack111l1l11l11_opy_:
      bstack111l1l1llll_opy_ = bstack111l1l11l11_opy_.read()
      bstack111l1ll111l_opy_ = re.sub(bstack1lll1_opy_ (u"ࡸࠧ࡟ࠪ࡟ࡷ࠰࠯࠿ࠤ࠰࠭ࠨࡡࡴࠧ᷍"), bstack1lll1_opy_ (u"ࠧࠨ᷎"), bstack111l1l1llll_opy_, flags=re.M)
      bstack111l1ll111l_opy_ = re.sub(
        bstack1lll1_opy_ (u"ࡳࠩࡡࠬࡡࡹࠫࠪࡁ᷏ࠫࠫ") + bstack1lll1_opy_ (u"ࠩࡿ᷐ࠫ").join(bstack111l1l1ll1l_opy_) + bstack1lll1_opy_ (u"ࠪ࠭࠳࠰ࠤࠨ᷑"),
        bstack1lll1_opy_ (u"ࡶࠬࡢ࠲࠻ࠢ࡞ࡖࡊࡊࡁࡄࡖࡈࡈࡢ࠭᷒"),
        bstack111l1ll111l_opy_, flags=re.M | re.I
      )
    def bstack111l1ll1l11_opy_(dic):
      bstack111l1l1ll11_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l1l1ll1l_opy_:
          bstack111l1l1ll11_opy_[key] = bstack1lll1_opy_ (u"ࠬࡡࡒࡆࡆࡄࡇ࡙ࡋࡄ࡞ࠩᷓ")
        else:
          if isinstance(value, dict):
            bstack111l1l1ll11_opy_[key] = bstack111l1ll1l11_opy_(value)
          else:
            bstack111l1l1ll11_opy_[key] = value
      return bstack111l1l1ll11_opy_
    bstack111l1l1ll11_opy_ = bstack111l1ll1l11_opy_(config)
    return {
      bstack1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩᷔ"): bstack111l1ll111l_opy_,
      bstack1lll1_opy_ (u"ࠧࡧ࡫ࡱࡥࡱࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪᷕ"): json.dumps(bstack111l1l1ll11_opy_)
    }
  except Exception as e:
    return {}
def bstack111l1ll11ll_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack1lll1_opy_ (u"ࠨ࡮ࡲ࡫ࠬᷖ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l1l11ll1_opy_ = os.path.join(log_dir, bstack1lll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡦࡳࡳ࡬ࡩࡨࡵࠪᷗ"))
  if not os.path.exists(bstack111l1l11ll1_opy_):
    bstack111l1l1l1l1_opy_ = {
      bstack1lll1_opy_ (u"ࠥ࡭ࡳ࡯ࡰࡢࡶ࡫ࠦᷘ"): str(inipath),
      bstack1lll1_opy_ (u"ࠦࡷࡵ࡯ࡵࡲࡤࡸ࡭ࠨᷙ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack1lll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡩ࡯࡯ࡨ࡬࡫ࡸ࠴ࡪࡴࡱࡱࠫᷚ")), bstack1lll1_opy_ (u"࠭ࡷࠨᷛ")) as bstack111l1l1l11l_opy_:
      bstack111l1l1l11l_opy_.write(json.dumps(bstack111l1l1l1l1_opy_))
def bstack111l1ll1ll1_opy_():
  try:
    bstack111l1l11ll1_opy_ = os.path.join(os.getcwd(), bstack1lll1_opy_ (u"ࠧ࡭ࡱࡪࠫᷜ"), bstack1lll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧᷝ"))
    if os.path.exists(bstack111l1l11ll1_opy_):
      with open(bstack111l1l11ll1_opy_, bstack1lll1_opy_ (u"ࠩࡵࠫᷞ")) as bstack111l1l1l11l_opy_:
        bstack111l1ll1lll_opy_ = json.load(bstack111l1l1l11l_opy_)
      return bstack111l1ll1lll_opy_.get(bstack1lll1_opy_ (u"ࠪ࡭ࡳ࡯ࡰࡢࡶ࡫ࠫᷟ"), bstack1lll1_opy_ (u"ࠫࠬᷠ")), bstack111l1ll1lll_opy_.get(bstack1lll1_opy_ (u"ࠬࡸ࡯ࡰࡶࡳࡥࡹ࡮ࠧᷡ"), bstack1lll1_opy_ (u"࠭ࠧᷢ"))
  except:
    pass
  return None, None
def bstack111l1l1111l_opy_():
  try:
    bstack111l1l11ll1_opy_ = os.path.join(os.getcwd(), bstack1lll1_opy_ (u"ࠧ࡭ࡱࡪࠫᷣ"), bstack1lll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧᷤ"))
    if os.path.exists(bstack111l1l11ll1_opy_):
      os.remove(bstack111l1l11ll1_opy_)
  except:
    pass
def bstack11l11111ll_opy_(config):
  try:
    from bstack_utils.helper import bstack1l1111ll1_opy_, bstack1l1ll111ll_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l1l11l1l_opy_
    if config.get(bstack1lll1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫᷥ"), False):
      return
    uuid = os.getenv(bstack1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᷦ")) if os.getenv(bstack1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᷧ")) else bstack1l1111ll1_opy_.get_property(bstack1lll1_opy_ (u"ࠧࡹࡤ࡬ࡔࡸࡲࡎࡪࠢᷨ"))
    if not uuid or uuid == bstack1lll1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫᷩ"):
      return
    bstack111l1l111ll_opy_ = [bstack1lll1_opy_ (u"ࠧࡳࡧࡴࡹ࡮ࡸࡥ࡮ࡧࡱࡸࡸ࠴ࡴࡹࡶࠪᷪ"), bstack1lll1_opy_ (u"ࠨࡒ࡬ࡴ࡫࡯࡬ࡦࠩᷫ"), bstack1lll1_opy_ (u"ࠩࡳࡽࡵࡸ࡯࡫ࡧࡦࡸ࠳ࡺ࡯࡮࡮ࠪᷬ"), bstack111l1l11l1l_opy_, bstack111l1ll1l1l_opy_]
    bstack111l1l11lll_opy_, root_path = bstack111l1ll1ll1_opy_()
    if bstack111l1l11lll_opy_ != None:
      bstack111l1l111ll_opy_.append(bstack111l1l11lll_opy_)
    if root_path != None:
      bstack111l1l111ll_opy_.append(os.path.join(root_path, bstack1lll1_opy_ (u"ࠪࡧࡴࡴࡦࡵࡧࡶࡸ࠳ࡶࡹࠨᷭ")))
    bstack1l1llll1l_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack1lll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠱ࡱࡵࡧࡴ࠯ࠪᷮ") + uuid + bstack1lll1_opy_ (u"ࠬ࠴ࡴࡢࡴ࠱࡫ࡿ࠭ᷯ"))
    with tarfile.open(output_file, bstack1lll1_opy_ (u"ࠨࡷ࠻ࡩࡽࠦᷰ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l1l111ll_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l1ll1111_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l1l1lll1_opy_ = data.encode()
        tarinfo.size = len(bstack111l1l1lll1_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l1l1lll1_opy_))
    bstack11ll1111l_opy_ = MultipartEncoder(
      fields= {
        bstack1lll1_opy_ (u"ࠧࡥࡣࡷࡥࠬᷱ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack1lll1_opy_ (u"ࠨࡴࡥࠫᷲ")), bstack1lll1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯ࡹ࠯ࡪࡾ࡮ࡶࠧᷳ")),
        bstack1lll1_opy_ (u"ࠪࡧࡱ࡯ࡥ࡯ࡶࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᷴ"): uuid
      }
    )
    bstack111l1l1l1ll_opy_ = bstack1l1ll111ll_opy_(cli.config, [bstack1lll1_opy_ (u"ࠦࡦࡶࡩࡴࠤ᷵"), bstack1lll1_opy_ (u"ࠧࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠧ᷶"), bstack1lll1_opy_ (u"ࠨࡵࡱ࡮ࡲࡥࡩࠨ᷷")], bstack11l1l1ll1l1_opy_)
    response = requests.post(
      bstack1lll1_opy_ (u"ࠢࡼࡿ࠲ࡧࡱ࡯ࡥ࡯ࡶ࠰ࡰࡴ࡭ࡳ࠰ࡷࡳࡰࡴࡧࡤ᷸ࠣ").format(bstack111l1l1l1ll_opy_),
      data=bstack11ll1111l_opy_,
      headers={bstack1lll1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫᷹ࠧ"): bstack11ll1111l_opy_.content_type},
      auth=(config[bstack1lll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨ᷺ࠫ")], config[bstack1lll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭᷻")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack1lll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡲ࡯ࡢࡦࠣࡰࡴ࡭ࡳ࠻ࠢࠪ᷼") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack1lll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫࡮ࡥ࡫ࡱ࡫ࠥࡲ࡯ࡨࡵ࠽᷽ࠫ") + str(e))
  finally:
    try:
      bstack1l1l1lll111_opy_()
      bstack111l1l1111l_opy_()
    except:
      pass