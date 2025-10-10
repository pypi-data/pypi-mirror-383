# -*- coding: utf-8 -*-
"""Adaptive GPU Allocator(AGA) library.

This module is the entry point of the AGA library detecting GPU usage and automatically calls the AGA API.
It is assumed to be used as follows.
  python -m adaptive_gpu_allocator.pytorch_automatic_main app.py
"""

import os
import sys
import logging
from runpy import run_path
from typing import Callable, Any
from .pytorch_automatic import PyTorchAutomaticAGA
from .noop_pytorch_automatic import NoopPyTorchAutomaticAGA
from .env import STATUS_JOB_START, get_config_without_aga

logger = logging.getLogger(__name__)

AutomaticAGA: type[NoopPyTorchAutomaticAGA | PyTorchAutomaticAGA]

if get_config_without_aga():
    AutomaticAGA = NoopPyTorchAutomaticAGA
else:
    AutomaticAGA = PyTorchAutomaticAGA


def notify_start_to_agarun() -> None:
    # Notify the start of this process
    logger.debug("send 'process started'")
    os.write(AutomaticAGA.aga.pipeno, STATUS_JOB_START.encode())


def run_with_auto_aga(func: Callable[[], Any]) -> None:
    AutomaticAGA.init()
    AutomaticAGA.set_signal_handler()
    notify_start_to_agarun()

    with AutomaticAGA.hook():  # type: ignore[no-untyped-call]
        func()

    AutomaticAGA.unset_signal_handler()
    AutomaticAGA.finalize()


def run_args() -> None:
    sys.argv = sys.argv[1:]

    # Modify the current directory to the parent directory of the user script
    sys.path[0] = os.path.abspath(os.path.dirname(sys.argv[0]))

    # Execute the user script
    run_path(sys.argv[0], run_name="__main__")


if __name__ == "__main__":
    run_with_auto_aga(run_args)
