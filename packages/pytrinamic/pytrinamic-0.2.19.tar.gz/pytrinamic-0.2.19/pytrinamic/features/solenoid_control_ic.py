################################################################################
# Copyright © 2019 TRINAMIC Motion Control GmbH & Co. KG
# (now owned by Analog Devices Inc.),
#
# Copyright © 2023 Analog Devices Inc. All Rights Reserved.
# This software is proprietary to Analog Devices, Inc. and its licensors.
################################################################################

from pytrinamic.features.solenoid_control import SolenoidControl

class SolenoidControlIC(SolenoidControl):
    """
    Solenoid control implementation for ICs
    """

    def __init__(self, eval_board, ic, axis):
        super().__init__(eval_board, axis)
        self._ic = ic

    def set_high(self):
        """
        Apply high voltage.
        This writes 1 to the corresponding CNTL channel field.
        """
        self._parent.write_axis_field(self._axis, self._ic.FIELD.CNTL, 1)

    def set_low(self):
        """
        Apply low voltage.
        This writes 0 to the corresponding CNTL channel field.
        """
        self._parent.write_axis_field(self._axis, self._ic.FIELD.CNTL, 0)
