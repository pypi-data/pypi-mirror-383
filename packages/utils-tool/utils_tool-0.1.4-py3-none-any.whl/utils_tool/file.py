
""" 文件工具 """
import importlib
import yaml
from .log import Log
logger = Log.logger


def load_inpackage_file(package_name: str, file_name: str, file_type="yaml"):
    """load config"""
    with importlib.resources.open_text(package_name, file_name) as f:
        if file_type == "yaml":
            return yaml.safe_load(f)
        else:
            return f.read()

def super_log(s, target: str = "target",log_ = logger.debug):
    COLOR_RED = "\033[91m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_BLUE = "\033[94m"
    COLOR_RESET = "\033[0m" # 重置颜色

    log_("\n"+f"{COLOR_BLUE}=={COLOR_RESET}" * 21 + target + f"{COLOR_BLUE}=={COLOR_RESET}" * 21)
    log_("\n       "+"--" * 40)
    log_(type(s))
    log_("\n       "+f"{COLOR_RED}--{COLOR_RESET}" * 40)
    log_(s)
    log_("\n"+f"{COLOR_GREEN}=={COLOR_RESET}" * 21 + target + "  end!"+f"{COLOR_GREEN}=={COLOR_RESET}" * 21)
