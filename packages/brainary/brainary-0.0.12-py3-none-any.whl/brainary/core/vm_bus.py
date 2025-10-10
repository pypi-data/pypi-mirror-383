# core/vm_bus.py
import logging
from typing import Optional
from threading import Lock  # Added for thread-safety

from brainary.core.ops.base_op import BaseOp

class VMBus:
    _vm = None
    _lock = Lock()  # For thread-safety

    @classmethod
    def set_vm(cls, vm):
        with cls._lock:
            cls._vm = vm

    @classmethod
    def dispatch(cls, op: BaseOp, **kwargs):
        with cls._lock:
            if cls._vm is None:
                raise RuntimeError("No VM installed. Use install_vm() first.")
            try:
                return cls._vm.accept_op(op, **kwargs)
            except Exception as e:
                logging.error(f"Dispatch failed for op {op}: {e}")
                raise