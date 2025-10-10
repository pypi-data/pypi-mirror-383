import logging

from .credential import replace_credential
from oocana import Mainframe, Context, StoreKey, BlockInfo, BinValueDict, VarValueDict, InputHandleDef, is_bin_value, is_var_value
from typing import Dict
from .secret import replace_secret
import os.path
from .logger import ContextHandler
from .data import EXECUTOR_NAME

logger = logging.getLogger(EXECUTOR_NAME)

def createContext(
    mainframe: Mainframe, session_id: str, job_id: str, store, output, session_dir: str, tmp_dir: str, package_name: str, pkg_dir: str
) -> Context:

    node_props = mainframe.notify_block_ready(session_id, job_id)

    inputs_def: Dict[str, Dict] | None = node_props.get("inputs_def")
    inputs = node_props.get("inputs")

    if inputs_def is not None and inputs is not None:

        inputs_def_handles: Dict[str, InputHandleDef] = {}
        for k, v in inputs_def.items():
            inputs_def_handles[k] = InputHandleDef(**v)

        inputs = replace_secret(inputs, inputs_def_handles, node_props.get("inputs_def_patch"))
        inputs = replace_credential(inputs, inputs_def_handles)

        for k, v in inputs.items():
            input_def = inputs_def_handles.get(k)
            if input_def is None:
                continue
            if is_var_value(v):
                wrap_var: VarValueDict = v
                try:
                    ref = StoreKey(**wrap_var["value"])
                except:  # noqa: E722
                    logger.warning(f"not valid object ref: {wrap_var}")
                    continue
                if ref in store:
                    inputs[k] = store.get(ref)
                elif input_def.is_serializable_var() and isinstance(wrap_var["serialize_path"], str):
                    # if the var is serializable, try to load it from the serialize path
                    serialize_path = wrap_var["serialize_path"]
                    if os.path.exists(serialize_path):
                        try:
                            import pandas as pd  # type: ignore
                            try:
                                inputs[k] = pd.read_pickle(serialize_path)
                            except Exception as e:
                                logger.error(f"Failed to load DataFrame from {serialize_path}: {e}")
                                continue
                            logger.info(f"Loaded DataFrame from {serialize_path}")
                        except ImportError:
                            logger.error("To use DataFrame serialization, please install pandas with `poetry install pandas`.")
                            continue
                    else:
                        logger.error(f"serialize path {serialize_path} for oomol/var is not found")
                else:
                    logger.error(f"object {ref} not found in store")
            elif is_bin_value(v):
                wrap_bin: BinValueDict = v
                path = wrap_bin["value"]
                if isinstance(path, str):
                    # check file path v is exist
                    if not os.path.exists(path):
                        logger.error(f"file {path} for oomol/bin is not found")
                        continue

                    with open(path, "rb") as f:
                        inputs[k] = f.read()
                else:
                    logger.error(f"not valid bin handle: {v}")

    if inputs is None:
        inputs = {}
    
    blockInfo = BlockInfo(**node_props)

    ctx = Context(
        inputs=inputs,
        inputs_def=inputs_def,
        blockInfo=blockInfo,
        mainframe=mainframe,
        store=store,
        outputs_def=output,
        session_dir=session_dir,
        tmp_dir=tmp_dir,
        package_name=package_name,
        pkg_dir=pkg_dir
    )
    # 跟 executor 日志分开，避免有的库在 logger 里面使用 print，导致 hook 出现递归调用。
    block_logger = logging.getLogger(f"block {job_id}")
    ctx_handler = ContextHandler(ctx)
    block_logger.addHandler(ctx_handler)
    ctx._logger = logger
    return ctx