# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Interface

from typing import Any

from cocotb.handle import HierarchyObject

parameters = [
    "CLASSIFICATION",
    "VERSION",
    "TDATA_WIDTH",
    "TID_WIDTH",
    "TDEST_WIDTH",
    "TUSER_WIDTH",
    "Tready_Signal",
    "Tstrb_Signal",
    "Tkeep_Signal",
    "Tlast_Signal",
    "Wakeup_Signal",
    "TSTRB_WIDTH",
    "TKEEP_WIDTH",
]

class Interface:
    def __init__(self, hdl : HierarchyObject) -> None:
        """
        Create an interface
        Work around simulator specific issues with accessing signals inside generates.
        """
        # Parameters
        for p in parameters:
            # Parameters not exposed by list() in some simulators - look up explicitly
            v = getattr(hdl, p)
            if isinstance(v.value, bytes):
                setattr(self, p, str(v.value.decode("utf-8")))
            else:
                setattr(self, p, int(v.value))

        # Signals
        for child in list(hdl):
            # Signals start with a lowercase letter
            if not child._name[0].isupper():
                setattr(self, child._name, child)

        if self.CLASSIFICATION != "AXI-STREAM":
            raise TypeError(f"Expected AXI-STREAM classification, got {self.CLASSIFICATION}")

        if self.VERSION not in [4, 5]:
            raise ValueError(f"Unsupported AXI-STREAM version: {self.VERSION}")

        # Remove un-configured signals
        if self.Tready_Signal == 0:
            delattr(self, "tready")

        if self.TDATA_WIDTH == 0:
            delattr(self, "tdata")

        if self.Tstrb_Signal == 0:
            delattr(self, "tstrb")

        if self.Tkeep_Signal == 0:
            delattr(self, "tkeep")

        if self.Tlast_Signal == 0:
            delattr(self, "tlast")

        if self.TID_WIDTH == 0:
            delattr(self, "tid")

        if self.TDEST_WIDTH == 0:
            delattr(self, "tdest")

        if self.TUSER_WIDTH == 0:
            delattr(self, "tuser")

        if self.VERSION < 5 or self.Wakeup_Signal == 0:
            delattr(self, "twakeup")

    def set(self, name : str, value : int) -> None:
        """
        Set the value of a signal (if signal exists)

        :param name: The name of the signal
        :type name: str
        :param value: The value to set
        :type value: int
        :return: None
        """
        signal = getattr(self, name, None)
        if signal is not None:
            signal.value = value

    def get(self, name : str, default : Any = None) -> int:
        """
        Get the value of a signal (if signal exists)

        :param name: The name of the signal
        :type name: str
        :param default: The default value to return if signal does not exist
        :type default: Any
        :return: The value of the signal or the default value
        :rtype: int
        """
        signal = getattr(self, name, None)
        if signal is not None:
            return signal.value
        return default

__all__ = ["Interface"]
