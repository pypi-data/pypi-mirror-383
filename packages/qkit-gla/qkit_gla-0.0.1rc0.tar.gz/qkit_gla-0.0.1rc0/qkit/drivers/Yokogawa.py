# Yokogawa.py driver for Yokogawa GS820 multi channel source measure unit
# Hannes Rotzinger, hannes.rotzinger@kit.edu 2010
# Micha Wildermuth, micha.wildermuth@kit.edu 2017
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import time
from distutils.version import LooseVersion

import numpy as np

from qkit import visa
from qkit.core.instrument_base import Instrument


class Yokogawa(Instrument):
    """
    This is the driver for the Yokogawa GS820 multi channel source measure unit.
    """

    def __init__(self, name, address, reset=False):
        """
        Initializes VISA communication with the instrument Yokogawa GS820.

        Parameters
        ----------
        name: string
            Name of the instrument (driver).
        address: string
            GPIB address for the communication with the instrument.
        reset: bool, optional
            Resets the instrument to default conditions. Default is False.

        Returns
        -------
        None

        Examples
        --------
        >>> import qkit
        QKIT configuration initialized -> available as qkit.cfg[...]

        >>> qkit.start()
        Starting QKIT framework ... -> qkit.core.startup
        Loading module ... S10_logging.py
        Loading module ... S12_lockfile.py
        Loading module ... S14_setup_directories.py
        Loading module ... S20_check_for_updates.py
        Loading module ... S25_info_service.py
        Loading module ... S30_qkit_start.py
        Loading module ... S65_load_RI_service.py
        Loading module ... S70_load_visa.py
        Loading module ... S80_load_file_service.py
        Loading module ... S85_init_measurement.py
        Loading module ... S98_started.py
        Loading module ... S99_init_user.py

        >>> IVD = qkit.instruments.create('IVD', 'Yokogawa', address='TCPIP0::00.00.000.00::INSTR', reset=True)
        Initialized the file info database (qkit.fid) in 0.000 seconds.
        """
        self.__name__ = __name__
        # Start VISA communication
        logging.info(__name__ + ": Initializing instrument Yokogawa_GS820")
        Instrument.__init__(self, name, tags=["physical"])
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        # Set termination characters (necessary for Ethernet communication)
        if LooseVersion(visa.__version__) < LooseVersion("1.5.0"):  # pyvisa 1.4
            self._visainstrument.term_chars = ""
        else:  # pyvisa 1.5
            self._visainstrument.read_termination = ""
            self._visainstrument.write_termination = ""
        # initial variables
        self._sweep_mode = 1  # IV-mode
        self._sweep_channels = (1,)
        self._measurement_modes = {0: "2-wire", 1: "4-wire"}
        self._IV_modes = {0: "curr", 1: "volt"}
        self._IV_units = {0: "A", 1: "V"}
        # dict of defaults values: defaults[<sweep_mode>][<channel>][<parameter>][<value>]
        self._defaults = {
            0: [
                {
                    self.set_measurement_mode: 0,
                    self.set_bias_mode: 1,
                    self.set_sense_mode: 1,
                    self.set_bias_range: -1,
                    self.set_sense_range: -1,
                    self.set_bias_delay: 200e-6,
                    self.set_sense_delay: 15e-6,
                    self.set_sense_nplc: 1,
                    self.set_sense_average: 1,
                    self.set_sense_autozero: 0,
                },
                {
                    self.set_measurement_mode: 0,
                    self.set_bias_mode: 0,
                    self.set_sense_mode: 1,
                    self.set_bias_range: -1,
                    self.set_sense_range: -1,
                    self.set_bias_delay: 200e-6,
                    self.set_sense_delay: 15e-6,
                    self.set_sense_nplc: 1,
                    self.set_sense_average: 1,
                    self.set_sense_autozero: 0,
                },
            ],
            1: [
                {
                    self.set_measurement_mode: 1,
                    self.set_bias_mode: 0,
                    self.set_sense_mode: 1,
                    self.set_bias_trigger: """str('sens')""",
                    self.set_sense_trigger: """str('sour')""",
                    self.set_bias_range: -1,
                    self.set_sense_range: -1,
                    self.set_bias_delay: 200e-6,
                    self.set_sense_delay: 15e-6,
                    self.set_sense_nplc: 1,
                    self.set_sense_average: 1,
                    self.set_sense_autozero: 0,
                }
            ],
            2: [
                {
                    self.set_measurement_mode: 1,
                    self.set_bias_mode: 1,
                    self.set_sense_mode: 0,
                    self.set_bias_trigger: """str('sens')""",
                    self.set_sense_trigger: """str('sour')""",
                    self.set_bias_range: -1,
                    self.set_sense_range: -1,
                    self.set_bias_delay: 200e-6,
                    self.set_sense_delay: 15e-6,
                    self.set_sense_nplc: 1,
                    self.set_sense_average: 1,
                    self.set_sense_autozero: 0,
                }
            ],
        }
        self._default_str = "default parameters"
        self.__set_defaults_docstring()
        # condition code registers
        self.bias_ccr = [
            ("EOS1", "CH1 End of Sweep"),
            ("RDY1", "CH1 Ready for Sweep"),
            ("LL01", "CH1 Low Limiting"),
            ("LHI1", "CH1 High Limiting"),
            ("TRP1", "CH1 Tripped"),
            ("EMR1", "CH1 Emergency (Temperature/Current over)"),
            ("", ""),
            ("", ""),
            ("EOS2", "CH2 End of Sweep"),
            ("RDY2", "CH2 Ready for Sweep"),
            ("LL02", "CH2 Low Limiting"),
            ("LHI2", "CH2 High Limiting"),
            ("TRP2", "CH2 Tripped"),
            ("EMR2", "CH2 Emergency (Temperature/Current over)"),
            ("ILC", "Inter Locking"),
            ("SSB", "Start Sampling Error"),
        ]
        self.sense_ccr = [
            ("EOM1", "CH1 End of Measure"),
            ("", ""),
            ("CLO1", "CH1 Compare result is Low"),
            ("CHI1", "CH1 Compare result is High"),
            ("", ""),
            ("OVR1", "CH1 Over Range"),
            ("", ""),
            ("", ""),
            ("EOM2", "CH2 End of Measure"),
            ("", ""),
            ("CLO2", "CH2 Compare result is Low"),
            ("CHI2", "CH1 Compare result is High"),
            ("", ""),
            ("OVR2", "CH2 Over Range"),
            ("EOT", "End of Trace"),
            ("TSE", "Trigger Sampling Error"),
        ]
        # error messages
        self.err_msg = {
            -101: """Invalid_character: Check whether invalid characters such as $ or & are used in the command header or parameters.""",
            -102: """Syntax_error: Check that the syntax is correct.""",
            -103: """Invalid separator: Check the use of the separator (comma).""",
            -106: """Parameter not allowed: Check the command and the number of parameters.""",
            -107: """Missing parameter: Check the command and the number of parameters.""",
            -112: """Program mnemonic too long: Check the command mnemonic.""",
            -113: """Undefined header: Check the command mnemonic.""",
            -121: """Invalid character in number: Check that the notation of the numeric parameter is correct (for example, binary notation should not contain characters other than 0 and 1)""",
            -122: """Header suffix out of range: Check whether the numeric suffix of the command header is correct.""",
            -123: """Exponent too large: Check whether the exponent is within the range of -127 to 127.""",
            -124: """Too many digits: Check that the number of digits in the value does not exceed 255.""",
            -128: """Numeric data not allowed: Check the parameter format.""",
            -131: """Invalid suffix: Check the unit that can be used for the parameter.""",
            -138: """Suffix not allowed: Check the parameter format.""",
            -141: """Invalid character data: Check the character data that can be used for the parameter.""",
            -148: """Character data not allowed: Check the command and parameter format.""",
            -150: """String data error: Check that the closing quotation mark (" or ') for a string is available.""",
            -151: """Invalid string data: Check that the string parameter is in the correct format.""",
            -158: """String data not allowed: Check the command and parameter format.""",
            -161: """Invalid block data: Check that the block data is in the correct format.""",
            -168: """Block data not allowed: Check the command and parameter format.""",
            -178: """Expression data not allowed: Check the command and parameter format.""",
            -222: """Data out of range: Check the selectable range of the parameter. If the command can use MINimum and MAXimum as its parameter, the range can also be queried.""",
            -256: """Filename not found: Check that the file exists. You can also use the CATalog? command to query the list of files.""",
            -285: """Program syntax error: Check that the sweep pattern file is in the correct format.""",
            -350: """Queue overflow: Read the error using :SYSTem:ERRor? or clear the error queue using *CLS.""",
            -361: """Parity error: Check that the communication settings on the GS820 and PC match. If the settings are correct, check the cable, and lower the baud rate.""",
            -362: """Framing error: Check that the communication settings on the GS820 and PC match. If the settings are correct, check the cable, and lower the baud rate.""",
            -363: """Input buffer overrun: Set the handshaking to a setting other than OFF. Lower the baud rate.""",
            -410: """Query INTERRUPTED: Check transmission/reception procedure.""",
            -420: """Query UNTERMINATED: Check transmission/reception procedure.""",
            -430: """Query DEADLOCK: Keep the length of a program message less than or equal to 64 KB.""",
            +101: """Too complex expression: Keep the total number of constants, variables, and operators in a MATH definition less than or equal to 256.""",
            +102: """Math file syntax error: Check that the syntax of the MATH definition file is correct.""",
            +103: """Too large file error: Keep MATH definition files less than 4 KB in size.""",
            +104: """Illegal file error: Download the file for updating the system firmware again.""",
            +105: """No slave SMU found: Check that the connection between the master and slave units is correct.""",
            +200: """Sweep stopped because of the setting change: Stop the sweep operation before changing the settings.""",
            +202: """Interlocking: Release the interlock, and then turn the output ON.""",
            +203: """Cannot relay on in hardware abnormal: Check whether the temperature inside the case is okay.""",
            +204: """Hardware input abnormal error: Connect a load within the specifications.""",
            +205: """Analog busy: Change the settings after the calibration or self-test is completed.""",
            +206: """Low battery: Request to have the battery replaced, because the time stamp when creating files will not be correct.""",
            +207: """Power line frequency measure failure: Directly set the line frequency.""",
            +304: """Cannot change setting in auto measure function: If you want to change the measurement function, select a measurement mode other than auto function.""",
        }
        # reset
        if reset:
            self.reset()
        else:
            self.get_all()
        return

    def _write(self, cmd):
        """
        Sends a visa command <cmd>, waits until "operation complete" and raises eventual errors of the Device.

        Parameters
        ----------
        cmd: str
            Command that is send to the instrument via pyvisa and NI-VISA backend.

        Returns
        -------
        None
        """
        self._visainstrument.write(cmd)
        while not bool(int(self._visainstrument.query("*OPC?"))):
            time.sleep(1e-6)
        self._raise_error()
        return

    def _ask(self, cmd):
        """
        Sends a visa command <cmd>, waits until "operation complete", raises eventual errors of the Device and returns the read answer <ans>.

        Parameters
        ----------
        cmd: str
            Command that is send to the instrument via pyvisa and NI-VISA backend.

        Returns
        -------
        answer: str
            Answer that is returned at query after the sent <cmd>.
        """
        if "?" in cmd:
            ans = self._visainstrument.query(cmd).rstrip()
        else:
            ans = self._visainstrument.query(f"{cmd:s}?").rstrip()
        while not bool(int(self._visainstrument.query("*OPC?"))):
            time.sleep(1e-6)
        self._raise_error()
        return ans

    def set_measurement_mode(self, mode, channel=1):
        """
        Sets measurement mode (wiring system) of channel <channel> to <mode>.

        Parameters
        ----------
        mode: int
            State of the measurement sense mode. Must be 0 (2-wire) or 1 (4-wire).
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        None
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:REMote 1|0|ON|OFF
        try:
            logging.debug(
                f"{__name__!s}: Set measurement mode of channel {channel:d} to {mode:d}"
            )
            self._write(f":chan{channel:d}:sens:rem {mode:d}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set measurement mode of channel {channel!s} to {mode!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set measurement mode of channel {channel!s} to {mode!s}\n{e!s}"
            )
        return

    def get_measurement_mode(self, channel=1):
        """
        Gets measurement mode (wiring system) <mode> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        mode: int
            State of the measurement sense mode. Meanings are 0 (2-wire) and 1 (4-wire).
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:REMote 1|0|ON|OFF
        try:
            logging.debug(
                f"{__name__!s}: Get measurement mode of channel {channel:d}"
            )
            return int(self._ask(f":chan{channel:d}:sens:rem"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get measurement mode of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get measurement mode of channel {channel!s}\n{e!s}"
            )

    def set_sync(self, val):
        """
        Sets the interchannel synchronization to <val>. The first channel is always the "master", the second the "slave".

        Parameters
        ----------
        val: bool
                        Inter-channel synchronization mode specifies whether two channels are to be operated in sync.

        Returns
        -------
        None
        """
        # Corresponding Command: :SYNChronize:CHANnel 1|0|ON|OFF
        try:
            logging.debug(
                f"{__name__!s}: Set interchannel synchronization to {val!r}"
            )
            self._write(f":sync:chan {val:d}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set interchannel synchronization to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set interchannel synchronization to {val!s}\n{e!s}"
            )
        return

    def get_sync(self):
        """
        Gets the interchannel synchronization.

        Parameters
        ----------
        None

        Returns
        -------
        val: bool
                        Inter-channel synchronization mode specifies whether two channels are to be operated in sync.
        """
        # Corresponding Command: :SYNChronize:CHANnel 1|0|ON|OFF
        try:
            logging.debug(f"{__name__!s}: Get interchannel synchronization")
            return bool(int(self._ask(":sync:chan")))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get interchannel synchronization"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get interchannel synchronization\n{e!s}"
            )

    def set_bias_mode(self, mode, channel=1):
        """
        Sets bias mode of channel <channel> to mode <mode>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.
        mode: int
            Bias mode. Must be 0 (current) or 1 (voltage).

        Returns
        -------
        None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce:FUNCtion VOLTage|CURRent
        try:
            logging.debug(
                f"{__name__!s}: Set bias mode of channel {channel:d} to {mode:d}"
            )
            self._write(
                f":chan{channel:d}:sour:func {self._IV_modes[mode]:s}"
            )
            self.set_bias_range(val=-1, channel=channel)
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set bias mode of channel {channel!s} to {mode!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set bias mode of channel {channel!s} to {mode!s}\n{e!s}"
            )
        return

    def get_bias_mode(self, channel=1):
        """
        Gets bias mode <mode> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        mode: int
            Bias mode. Meanings are 0 (current) and 1 (voltage).
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce:FUNCtion VOLTage|CURRent
        try:
            logging.debug(
                f"{__name__!s}: Get bias mode of channel {channel:d}"
            )
            return int(
                list(self._IV_modes.keys())[
                    list(self._IV_modes.values()).index(
                        self._ask(f":chan{channel:d}:sour:func").lower()
                    )
                ]
            )
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get bias mode of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get bias mode of channel {channel!s}\n{e!s}"
            )

    def set_sense_mode(self, mode, channel=1):
        """
        Sets sense mode of channel <channel> to mode <mode>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.
        mode: int
            Sense mode. Must be 0 (current) or 1 (voltage).

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:FUNCtion VOLTage|CURRent
        try:
            logging.debug(
                f"{__name__!s}: Set sense mode of channel {channel:d} to {mode:d}"
            )
            self._write(
                f":chan{channel:d}:sens:func {self._IV_modes[mode]:s}"
            )
            self.set_sense_range(val=-1, channel=channel)
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sense mode of channel {channel!s} to {mode!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sense mode of channel {channel!s} to {mode!s}\n{e!s}"
            )
        return

    def get_sense_mode(self, channel=1):
        """
        Gets sense mode <mode> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        mode: int
            Sense mode. Meanings are 0 (current) and 1 (voltage).
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:FUNCtion VOLTage|CURRent
        try:
            logging.debug(
                f"{__name__!s}: Get sense mode of channel {channel:d}"
            )
            return int(
                list(self._IV_modes.keys())[
                    list(self._IV_modes.values()).index(
                        self._ask(f":chan{channel:d}:sens:func").lower()
                    )
                ]
            )
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sense mode of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sense mode of channel {channel!s}\n{e!s}"
            )

    def set_bias_range(self, val, channel=1):
        """
        Sets bias range of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Bias range. Possible values are -1 (auto), for currents 200nA, 2uA, 20uA, 200uA, 2mA, 20mA, 200mA, 1 A, 3A and for voltages 200mV, 2V, 7V, 18V.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:RANGe <voltage>|MINimum|MAXimum|UP|DOWN
        # Corresponding Command: [:CHANnel<n>]:SOURce[:CURRent]:RANGe <current>|MINimum|MAXimum|UP|DOWN
        try:
            logging.debug(
                f"{__name__!s}: Set bias range of channel {channel:d} to {val:f}"
            )
            if val == -1:
                self._write(f":chan{channel:d}:sour:rang:auto 1")
            else:
                self._write(f":chan{channel:d}:sour:rang {val:f}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set bias range of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set bias range of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def get_bias_range(self, channel=1):
        """
        Gets bias mode <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Bias range.
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:RANGe <voltage>|MINimum|MAXimum|UP|DOWN
        # Corresponding Command: [:CHANnel<n>]:SOURce[:CURRent]:RANGe <current>|MINimum|MAXimum|UP|DOWN
        try:
            logging.debug(
                f"{__name__!s}: Get bias range of channel {channel:d}"
            )
            return float(self._ask(f":chan{channel:d}:sour:rang"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get bias range of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get bias range of channel {channel!s}\n{e!s}"
            )

    def set_sense_range(self, val, channel=1):
        """
        Sets sense range of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Sense range. Possible values are -1 (auto), for currents 200nA, 2uA, 20uA, 200uA, 2mA, 20mA, 200mA, 1 A, 3A and for voltages 200mV, 2V, 7V, 18V.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe[:VOLTage]:RANGe <voltage>|MINimum|MAXimum|UP|DOWN
        # Corresponding Command: [:CHANnel<n>]:SENSe[:CURRent]:RANGe <current>|MINimum|MAXimum|UP|DOWN
        try:
            logging.debug(
                f"{__name__!s}: Set sense range of channel {channel:d} to {val:f}"
            )
            if val == -1:
                self._write(f":chan{channel:d}:sens:rang:auto 1")
            else:
                self._write(f":chan{channel:d}:sens:rang {val:f}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sense range of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sense range of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def get_sense_range(self, channel=1):
        """
        Gets sense mode <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Sense range.
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe[:VOLTage]:RANGe <voltage>|MINimum|MAXimum|UP|DOWN
        # Corresponding Command: [:CHANnel<n>]:SENSe[:CURRent]:RANGe <current>|MINimum|MAXimum|UP|DOWN
        try:
            logging.debug(
                f"{__name__!s}: Get sense range of channel {channel:d}"
            )
            return float(self._ask(f":chan{channel:d}:sens:rang"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sense range of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sense range of channel {channel!s}\n{e!s}"
            )

    def set_bias_trigger(self, mode, channel=1, **val):
        """
        Sets bias trigger mode of channel <channel> to <mode> and optional value <val>.

        Parameters
        ----------
        mode: str
                        Bias trigger mode. Must be 'ext' (external), 'aux' (auxiliary), 'tim1' (timer1), 'tim2' (timer2) or 'sens' (sense).
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.
        time: float, optional
                        Time trigger period if <mode> is 'timer'. Must be in [100µs, 3600s].
                pol: int, optional
                        Polarity of auxiliary trigger if <mode> is 'aux'. Must be 0 (falling edge) or 1 (rising edge).

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce:TRIGger EXTernal|AUXiliary|TIMer1|TIMer2|SENSe
        # Corresponding Command: [:CHANnel<n>]:SOURce:TRIGger:AUXiliary:POLarity NORMal|INVerted
        # Corresponding Command: :TRIGger:TIMer1 <time>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set bias trigger of channel {channel:d} to {mode:s}"
            )
            self._write(f":chan{channel:d}:sour:trig {mode:s}")
            if "pol" in val:
                cmd = {0: "norm", 1: "inv"}
                self._write(
                    ":chan{:d}:sour:trig:aux:pol {:s}".format(
                        channel, cmd[val.get("pol", 0)]
                    )
                )
            if "time" in val:
                self._write(":trig:{:s} {:f}".format(mode, val.get("time", 50e-3)))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set bias trigger of channel {channel!s} to {mode!s}{val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set bias trigger of channel {channel!s} to {mode!s}{val!s}\n{e!s}"
            )
        return

    def get_bias_trigger(self, channel=1):
        """
        Gets bias trigger of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        mode: str
                        Bias trigger mode. Meanings are 'ext' (external), 'aux' (auxiliary), 'tim1' (timer1), 'tim2' (timer2) and 'sens' (sense).
        time: float, optional
                        Time trigger period if <mode> is 'timer'.
                pol: int, optional
                        Polarity of auxiliary trigger if <mode> is 'aux'. Meanings are 0 (falling edge) and 1 (rising edge).
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce:TRIGger EXTernal|AUXiliary|TIMer1|TIMer2|SENSe
        # Corresponding Command: [:CHANnel<n>]:SOURce:TRIGger:AUXiliary:POLarity NORMal|INVerted
        # Corresponding Command: :TRIGger:TIMer1 <time>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get bias trigger of channel {channel:d}"
            )
            mode = str(self._ask(f":chan{channel:d}:sour:trig").lower())
            if mode[:3] == "tim":
                val = float(self._ask(f":trig:{mode:s}"))
                return mode, val
            elif mode == "aux":
                val = int(
                    float(self._ask(f":chan{channel:d}:sour:trig:aux:pol"))
                )
                return mode, val
            else:
                return mode
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get bias trigger of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get bias trigger of channel {channel!s}\n{e!s}"
            )

    def set_sense_trigger(self, mode, channel=1, **val):
        """
        Sets sense trigger mode of channel <channel> to <mode> and optional value <val>. If <mode> is 'timer' it can be set to <time>

        Parameters
        ----------
        mode: str
                        Sense trigger mode. Must be 'sour' (source), 'swe' (sweep), 'aux' (auxiliary), 'tim1' (timer1), 'tim2' (timer2) or 'imm' (immediate).
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.
        time: float, optional
                        Time trigger period. Must be in [100µs, 3600s].
                pol: int, optional
                        Polarity of auxiliary trigger if <mode> is 'aux'. Must be 0 (falling edge) or 1 (rising edge).

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:TRIGger SOURce|SWEep|AUXiliary|TIMer1|TIMer2|IMMediate
        # Corresponding Command: [:CHANnel<n>]:SENSe:TRIGger:AUXiliary:POLarity NORMal|INVerted
        # Corresponding Command: :TRIGger:TIMer1 <time>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set sense trigger of channel {channel:d} to {mode:s}"
            )
            self._write(f":chan{channel:d}:sens:trig {mode:s}")
            if "time" in val:
                self._write(":trig:{:s} {:f}".format(mode, val.get("time", 50e-3)))
            elif "pol" in val:
                cmd = {0: "norm", 1: "inv"}
                self._write(
                    ":chan{:d}:sens:trig:aux:pol {:s}".format(
                        channel, cmd[val.get("pol", 0)]
                    )
                )
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sense trigger of channel {channel!s} to {mode!s}{val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sense trigger of channel {channel!s} to {mode!s}{val!s}\n{e!s}"
            )
        return

    def get_sense_trigger(self, channel=1):
        """
        Gets sense trigger of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        mode: str
                        Sense trigger mode. Meanings are 'sour' (source), 'swe' (sweep), 'aux' (auxiliary), 'tim1' (timer1), 'tim2' (timer2) or 'imm' (immediate).
        time: float, optional
                        Time trigger period.
                pol: int, optional
                        Polarity of auxiliary trigger if <mode> is 'aux'. Meanings are 0 (falling edge) and 1 (rising edge).
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:TRIGger SOURce|SWEep|AUXiliary|TIMer1|TIMer2|IMMediate
        # Corresponding Command: [:CHANnel<n>]:SENSe:TRIGger:AUXiliary:POLarity NORMal|INVerted
        # Corresponding Command: :TRIGger:TIMer1 <time>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get sense trigger of channel {channel:d}"
            )
            mode = str(self._ask(f":chan{channel:d}:sens:trig").lower())
            if mode[:3] == "tim":
                val = float(self._ask(f":trig:{mode:s}"))
                return mode, val
            elif mode == "aux":
                val = int(
                    float(self._ask(f":chan{channel:d}:sens:trig:aux:pol"))
                )
                return mode, val
            else:
                return mode
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sense trigger of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sense trigger of channel {channel!s}\n{e!s}"
            )

    def set_bias_delay(self, val, channel=1):
        """
        Sets bias delay of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Bias delay with respect to the bias trigger. Must be are in [15µs, 3600s].
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce:DELay <time>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set bias delay of channel {channel:d} to {val:f}"
            )
            self._write(f":chan{channel:d}:sour:del {val:f}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set bias delay of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set bias delay of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def get_bias_delay(self, channel=1):
        """
        Gets bias delay <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Bias delay with respect to the bias trigger.
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce:DELay <time>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get bias delay of channel {channel:d}"
            )
            return float(self._ask(f":chan{channel:d}:sour:del"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get bias delay of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get bias delay of channel {channel!s}\n{e!s}"
            )

    def set_sense_delay(self, val, channel=1, **kwargs):
        """
        Sets sense delay of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Sense delay with respect to the sense trigger. Must be are in [15µs, 3600s].
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce:DELay <time>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set sense delay of channel {channel:d} to {val:f}"
            )
            self._write(f":chan{channel:d}:sens:del {val:f}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sense delay of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sense delay of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def get_sense_delay(self, channel=1):
        """
        Gets sense delay <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Sense delay with respect to the sense trigger.
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:DELay <time>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get sense delay of channel {channel:d}"
            )
            return float(self._ask(f":chan{channel:d}:sens:del"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sense delay of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sense delay of channel {channel!s}\n{e!s}"
            )

    def set_sense_average(self, val, channel=1, **kwargs):
        """
        Sets sense average of channel <channel> to <val>.
        If <val> is less than 1 average status is turned off, but the set value remains.

        Parameters
        ----------
        val: int
            Number of measured readings that are required to yield one filtered measurement. Must be in [1, 100].
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:AVERage[:STATe] 1|0|ON|OFF
        # Corresponding Command: [:CHANnel<n>]:SENSe:AVERage:COUNt <integer>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set sense average of channel {channel:d} to {val:d}"
            )
            status = not (
                0.5 * (1 - np.sign(val - 1))
            )  # equals Heaviside(1-<val>) --> turns on for <val> >= 2
            self._write(f":chan{channel:d}:sens:aver:stat {status:d}")
            if status:
                self._write(f":chan{channel:d}:sens:aver:coun {val:d}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sense average of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sense average of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def get_sense_average(self, channel=1):
        """
        Gets sense average status <status> and value <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        status: bool
            Status if the measurement filter is enabled.
        val: int
            Number of measured readings that are required to yield one filtered measurement.
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:AVERage[:STATe] 1|0|ON|OFF
        # Corresponding Command: [:CHANnel<n>]:SENSe:AVERage:COUNt <integer>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get sense average of channel {channel:d}"
            )
            status = bool(int(self._ask(f":chan{channel:d}:sens:aver:stat")))
            val = int(self._ask(f":chan{channel:d}:sens:aver:coun"))
            return status, val
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sense average of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sense average of channel {channel!s}\n{e!s}"
            )

    def set_plc(self, plc):
        """
        Sets power line cycle (PLC) to <val>.

        Parameters
        ----------
        plc: int
            Power line frequency setting used for NPLC calculations. Possible values are -1 (auto) | 50 | 60.

        Returns
        -------
                None
        """
        # Corresponding Command: :SYSTem:LFRequency 50|60
        # Corresponding Command: :SYSTem:LFRequency:AUTO 1|0|ON|OFF
        try:
            logging.debug(f"{__name__!s}: Set PLC to {plc!s}")
            cmd = {-1: ":auto 1", 50: " 50", 60: " 60"}
            self._write(f"syst:lfr{cmd.get(int(plc), cmd[-1]):s}")
        except Exception as e:
            logging.error(f"{__name__!s}: Cannot set PLC to {plc!s}")
            raise type(e)(f"{__name__!s}: Cannot set PLC to {plc!s}\n{e!s}")
        return

    def get_plc(self):
        """
        Gets power line cycle (PLC) <val>.

        Parameters
        ----------
                None

        Returns
        -------
        plc: int
            Power line frequency setting used for NPLC calculations.
        """
        # Corresponding Command: :SYSTem:LFRequency 50|60
        # Corresponding Command: :SYSTem:LFRequency:AUTO 1|0|ON|OFF
        try:
            logging.debug(f"{__name__!s}: Get PLC")
            return int(self._ask("syst:lfr"))
        except Exception as e:
            logging.error(f"{__name__!s}: Cannot get PLC")
            raise type(e)(f"{__name__!s}: Cannot get PLC\n{e!s}")

    def set_sense_nplc(self, val, channel=1):
        """
        Sets sense nplc (number of power line cycle) of channel <channel> with the <val>-fold of one power line cycle.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.
        val: float
            Integration aperture for measurements. Must be in [1, 25].

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:NPLC <real number>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set sense nplc of channel {channel:d} to {val:2.0f} PLC"
            )
            self._write(f":chan{channel:d}:sens:nplc {val:2.0f}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sense nplc of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sense nplc of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def get_sense_nplc(self, channel=1):
        """
        Gets sense nplc (number of power line cycle) <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Integration aperture for measurements.
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:NPLC <real number>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get sense nplc of channel {channel:d}"
            )
            return float(self._ask(f":chan{channel:d}:sens:nplc"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sense nplc of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sense nplc of channel {channel!s}\n{e!s}"
            )

    def set_sense_autozero(self, val, channel=1):
        """
        Sets autozero of channel <channel> to <val>. Note that "on" means that the internal zero point is measured for each measurement, wherefore the measurement takes approximately twice as long as when the auto zero function is "off"

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.
        val: int
            Status of the internal reference measurements (autozero) of the source-measure unit. Possible values are 0 (off), 1 (on) or 2 (once).

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:ZERo:AUTO 1|0|ON|OFF (at each measurement)
        # Corresponding Command: [:CHANnel<n>]:SENSe:ZERo:EXECute (once)
        try:
            logging.debug(
                f"{__name__!s}: Set sense autozero of channel {channel:d} to {val:d}"
            )
            if val == 2:
                self._visainstrument.write(f":chan{channel:d}:sens:zero:exec")
                time.sleep(2.0)  # tests yield random value t > 1.65 to be necessary
                self._wait_for_OPC()
                self._raise_error()
            else:
                self._write(f":chan{channel:d}:sens:zero:auto {val:d}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sense autozero of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sense autozero of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def get_sense_autozero(self, channel=1):
        """
        Gets sense autozero <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: int
            Status of the internal reference measurements (autozero) of the source-measure unit. Meanings are 0 (off) and 1 (on).
        """
        # Corresponding Command: [:CHANnel<n>]:SENSe:ZERo:AUTO 1|0|ON|OFF
        try:
            logging.debug(
                f"{__name__!s}: Get sense autozero of channel {channel:d}"
            )
            return bool(self._ask(f":chan{channel:d}:sens:zero:auto"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sense autozero of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sense autozero of channel {channel!s}\n{e!s}"
            )

    def set_status(self, status, channel=1):
        """
        Sets output status of channel <channel> to <status>.

        Parameters
        ----------
        status: int
            Output status. Possible values are 0 (off) or 1 (on).
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:OUTput:STATus 1|0|ON|OFF
        try:
            logging.debug(
                f"{__name__!s}: Set output status of channel {channel:d} to {status!r}"
            )
            self._write(f":chan{channel:d}:outp:stat {status:d}")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set output status of channel {channel!s} to {status!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set output status of channel {channel!s} to {status!s}\n{e!s}"
            )
        return

    def get_status(self, channel=1):
        """
        Gets output status <status> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        status: int
            Output status. Meanings are 0 (off) and 1 (on).
        """
        # Corresponding Command: [:CHANnel<n>]:OUTput:STATus 1|0|ON|OFF
        try:
            logging.debug(
                f"{__name__!s}: Get output status of channel {channel:d}"
            )
            return bool(int(self._ask(f":chan{channel:d}:outp:stat")))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get output status of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get output status of channel {channel!s}\n{e!s}"
            )

    def set_bias_value(self, val, channel=1):
        """
        Sets bias value of channel <channel> to value <val>.

        Parameters
        ----------
        val: float
            Bias value.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:LEVel <voltage>|MINimum|MAXimum
        # Corresponding Command: [:CHANnel<n>]:SOURce[:CURRent]:LEVel <current>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set bias value of channel {channel:d} to {val:f}"
            )
            self._write(
                f":chan{channel:d}:sour:lev {val:g}"
            )  # necessary to cast as scientific float! (otherwise only >= 1e-6 possible)
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set bias value of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set bias value of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def get_bias_value(self, channel=1):
        """
        Gets bias value <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Bias value.
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:LEVel <voltage>|MINimum|MAXimum
        # Corresponding Command: [:CHANnel<n>]:SOURce[:CURRent]:LEVel <current>|MINimum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get bias value of channel {channel:d}"
            )
            return float(self._ask(f":chan{channel:d}:sour:lev"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get bias value of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get bias value of channel {channel!s}\n{e!s}"
            )

    def get_sense_value(self, channel=1):
        """
        Gets sense value of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Sense value.
        """
        # Corresponding Command: [:CHANnel<n>]:MEASure?
        try:
            logging.debug(
                f"{__name__!s}: Get sense value of channel {channel:d}"
            )
            return float(self._ask(f":chan{channel:d}:meas"))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sense value of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sense value of channel {channel!s}\n{e!s}"
            )

    def set_voltage(self, val, channel=1):
        """
        Sets voltage value of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Bias voltage value.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        if self.get_bias_mode(channel):  # 1 (voltage bias)
            return self.set_bias_value(val, channel)
        elif not self.get_bias_mode(channel):  # 0 (current bias)
            logging.error(
                f"{__name__!s}: Cannot set voltage value of channel {channel!s} in the current bias"
            )
            raise SystemError(
                f"{__name__!s}: Cannot set voltage value of channel {channel!s} in the current bias"
            )
        return

    def get_voltage(self, channel=1, **kwargs):
        """
        Gets voltage value <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Sense voltage value.
        """
        if self.get_bias_mode(channel):  # 1 (voltage bias)
            return self.get_bias_value(channel)
        elif self.get_sense_mode(channel):  # 1 (voltage sense)
            return self.get_sense_value(channel)
        else:
            logging.error(
                f"{__name__!s}: Cannot get voltage value of channel {channel!s}: neither bias nor sense in voltage mode"
            )
            raise SystemError(
                f"{__name__!s}: Cannot get voltage value of channel {channel!s}: neither bias nor sense in voltage mode"
            )

    def set_current(self, val, channel=1):
        """
        Sets current value of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Bias current value.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        if not self.get_bias_mode(channel):  # 0 (current bias)
            return self.set_bias_value(val, channel)
        elif self.get_bias_mode(channel):  # 1 (voltage bias)
            logging.error(
                f"{__name__!s}: Cannot set current value of channel {channel!s} in the voltage bias"
            )
            raise SystemError(
                f"{__name__!s}: Cannot set current value of channel {channel!s} in the voltage bias"
            )
        return

    def get_current(self, channel=1):
        """
        Gets current value <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Sense current value.
        """
        if not self.get_bias_mode(channel):  # 0 (current bias)
            return self.get_bias_value(channel)
        elif not self.get_sense_mode(channel):  # 0 (current sense)
            return self.get_sense_value(channel)
        else:
            logging.error(
                f"{__name__!s}: Cannot get current value of channel {channel!s}: neither bias nor sense in current mode"
            )
            raise SystemError(
                f"{__name__!s}: Cannot get current value of channel {channel!s}: neither bias nor sense in current mode"
            )

    def get_IV(self, channel=1):
        """
        Gets both current value <I_val> and voltage value <V_val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        I_val: float
            Sense current value.
        V_val: float
            Sense voltage value.
        """
        return self.get_current(channel=channel), self.get_voltage(channel=channel)

    def ramp_bias(self, stop, step, step_time=0.1, channel=1):
        """
        Ramps bias value of channel <channel> from recent value to stop value <stop> with step size <step> and step time <step_time>.

        Parameters
        ----------
        stop: float
            Stop value
        step: float
            Step size.
        step_time: float
            Sleep time between staircase ramp.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1. (default)

        Returns
        -------
                None
        """
        start = self.get_bias_value(channel=channel)
        if stop < start:
            step = -step
        for val in np.arange(start, stop, step) + step:
            self.set_bias_value(val, channel=channel)
            print(
                f"{val:f}{self._IV_units[self.get_bias_mode()]:s}", end="\r"
            )
            time.sleep(step_time)
        return

    def ramp_voltage(self, stop, step, step_time=0.1, channel=1):
        """
        Ramps voltage of channel <channel> from recent value to stop value <stop> with step size <step> and step time <step_time> according to bias_mode.

        Parameters
        ----------
        stop: float
            Stop voltage value
        step: float
            Step voltage size.
        step_time: float
            Sleep time between voltage staircase ramp.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1. (default)

        Returns
        -------
                None
        """
        if self.get_bias_mode(channel=channel):  # 1 (voltage bias)
            return self.ramp_bias(
                stop=stop, step=step, step_time=step_time, channel=channel
            )
        elif not self.get_bias_mode(channel=channel):  # 0 (current bias)
            logging.error(
                __name__
                + f": Cannot set voltage value of channel {channel!s}: in the current bias"
            )
            return

    def ramp_current(self, stop, step, step_time=0.1, channel=1):
        """
        Ramps current of channel <channel> from recent value to stop value <stop> with step size <step> and step time <step_time> according to bias_mode.

        Parameters
        ----------
        stop: float
            Stop current value
        step: float
            Step current size.
        step_time: float
            Sleep time between current staircase ramp.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1. (default)

        Returns
        -------
                None
        """
        if not self.get_bias_mode(channel=channel):  # 0 (current bias)
            return self.ramp_bias(
                stop=stop, step=step, step_time=step_time, channel=channel
            )
        elif self.get_bias_mode(channel=channel):  # 1 (voltage bias)
            logging.error(
                __name__
                + f": Cannot ramp current value of channel {channel!s}: in the voltage bias"
            )
            return

    def set_sweep_mode(self, mode=1, *channels):
        """
        Sets an variable to decide weather
         * voltage is both applied and measured (VV-mode),
         * current is applied and voltage is measured (IV-mode) or
         * voltage is applied and current is measured (VI-mode)
        and channels <channels> that are used during sweeps.

        Parameters
        ----------
        mode: int
            Sweep mode denoting bias and sense modes. Possible values are 0 (VV-mode), 1 (IV-mode) or 2 (VI-mode). Default is 1
        channels: int or tuple(int)
            Number of channel of usage. Must be 1 or 2 for IV-mode and VI-mode or a tuple containing both channels for VV-mode (1st argument as bias channel and 2nd argument as sense channel).


        Returns
        -------
                None
        """
        default_channels = {0: (1, 2), 1: (1,), 2: (1,)}
        if mode in [0, 1, 2]:
            if len(channels) == int(not mode) + 1:
                logging.debug(
                    f"{__name__!s}: Set sweep channels to {channels!s}"
                )
                self._sweep_channels = channels
            elif len(channels) == 0:
                logging.debug(
                    f"{__name__!s}: Set sweep channels to {default_channels[mode]!s}"
                )
                self._sweep_channels = default_channels[mode]
            else:
                logging.error(
                    f"{__name__!s}: Cannot set sweep channels to {channels!s}"
                )
                raise ValueError(
                    f"{__name__!s}: Cannot set sweep channels to {channels!s}"
                )
            logging.debug(f"{__name__!s}: Set sweep mode to {mode:d}")
            self._sweep_mode = mode
            self.__set_defaults_docstring()
        else:
            logging.error(f"{__name__!s}: Cannot set sweep mode to {mode!s}")
            raise ValueError(
                f"{__name__!s}: Cannot set sweep mode to {mode!s}"
            )
        return

    def get_sweep_mode(self):
        """
        Gets an internal variable <mode> to decide weather
         * voltage is both applied and measured (VV-mode),
         * current is applied and voltage is measured (IV-mode) or
         * voltage is applied and current is measured (VI-mode).

        Parameters
        ----------
        None

        Returns
        -------
        mode: int
            Sweep mode denoting bias and sense modes. Meanings are 0 (VV-mode), 1 (IV-mode) or 2 (VI-mode).
        """
        return self._sweep_mode

    def get_sweep_channels(self):
        """
        Gets channels <channels> that are used during sweeps. In the IV and VI sweep mode one channel requires for biasing and sensing, whereas two channels are returned in the VV sweep mode (1st as bias and 2nd as sense channel).

        Parameters
        ----------
                None

        Returns
        -------
        channels: int or tuple(int)
            Number of channel of usage. Meanings are 1 or 2 for IV-mode and VI-mode or a tuple containing both channels for VV-mode (1st argument as bias channel and 2nd argument as sense channel).
        """
        return self._sweep_channels

    def get_sweep_bias(self):
        """
        Calls get_bias_mode of channel <channel>. This method is needed for qkit.measure.transport.transport.py in case of no virtual tunnel electronic.

        Parameters
        ----------
                None

        Returns
        -------
        mode: int
            Bias mode. Meanings are 0 (current) and 1 (voltage).
        """
        return self.get_bias_mode(self._sweep_channels[0])

    def _set_sweep_start(self, val, channel=1):
        """
        Sets sweep start value of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Start value of sweep.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:SWEep:STARt <voltage>|MINiumum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set sweep start of channel {channel:d} to {val:f}"
            )
            # self._write(':chan{:d}:sour:swe:star {:f}'.format(channel, val))
            self._write(
                f":chan{channel:d}:sour:{self._IV_modes[self.get_bias_mode(channel)]:s}:swe:star {val:f}"
            )
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sweep start of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sweep start of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def _get_sweep_start(self, channel=1):
        """
        Gets sweep start value of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Start value of sweep.
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:SWEep:STARt <voltage>|MINiumum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get sweep start of channel {channel:d}"
            )
            # return float(self._ask(':chan{:d}:sour:swe:star'.format(channel)))
            return float(
                self._ask(
                    f":chan{channel:d}:sour:{self._IV_modes[self.get_bias_mode(channel)]:s}:swe:star"
                )
            )
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sweep start of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sweep start of channel {channel!s}\n{e!s}"
            )

    def _set_sweep_stop(self, val, channel=1):
        """
        Sets sweep stop value of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Stop value of sweep.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:SWEep:STARt <voltage>|MINiumum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set sweep stop of channel {channel:d} to {val:f}"
            )
            # self._write(':chan{:d}:sour:swe:stop {:f}'.format(channel, val))
            self._write(
                f":chan{channel:d}:sour:{self._IV_modes[self.get_bias_mode(channel)]:s}:swe:stop {val:f}"
            )
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sweep stop of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sweep stop of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def _get_sweep_stop(self, channel=1):
        """
        Gets sweep stop value of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: float
            Stop value of sweep.
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:SWEep:STARt <voltage>|MINiumum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get sweep stop of channel {channel:d}"
            )
            # return float(self._ask(':chan{:d}:sour:swe:stop'.format(channel)))
            return float(
                self._ask(
                    f":chan{channel:d}:sour:{self._IV_modes[self.get_bias_mode(channel)]:s}:swe:stop"
                )
            )
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sweep stop of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sweep stop of channel {channel!s}\n{e!s}"
            )

    def _set_sweep_step(self, val, channel=1):
        """
        Sets sweep step value of channel <channel> to <val>.

        Parameters
        ----------
        val: float
            Step value of sweep.
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:SWEep:STARt <voltage>|MINiumum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Set sweep step of channel {channel:d} to {val:f}"
            )
            self._write(
                f":chan{channel:d}:sour:{self._IV_modes[self.get_bias_mode(channel)]:s}:swe:step {val:f}"
            )
            # self._write(':chan{:d}:sour:swe:step {:f}'.format(channel, val))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sweep step of channel {channel!s} to {val!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sweep step of channel {channel!s} to {val!s}\n{e!s}"
            )
        return

    def _get_sweep_step(self, channel=1):
        """
        Gets sweep step value of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val:
            Step value of sweep.
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce[:VOLTage]:SWEep:STARt <voltage>|MINiumum|MAXimum
        try:
            logging.debug(
                f"{__name__!s}: Get sweep step of channel {channel:d}"
            )
            return float(
                self._ask(
                    f":chan{channel:d}:sour:{self._IV_modes[self.get_bias_mode(channel)]:s}:swe:step"
                )
            )
            # return float(self._ask(':chan{:d}:sour:swe:step'.format(channel)))
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sweep step of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sweep step of channel {channel!s}\n{e!s}"
            )

    def _get_sweep_nop(self, channel=1):
        """
        Gets sweeps number of points (nop) of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val:
            Number of points of sweep.
        """
        try:
            logging.debug(
                f"{__name__!s}: Get sweep nop of channel {channel:d}"
            )
            return int(
                (
                    self._get_sweep_stop(channel=channel)
                    - self._get_sweep_start(channel=channel)
                )
                / self._get_sweep_step(channel=channel)
                + 1
            )
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot get sweep nop of channel {channel!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot get sweep nop of channel {channel!s}\n{e!s}"
            )

    def set_sweep_parameters(self, sweep):
        """
        Sets sweep parameters <sweep> and prepares instrument for the set sweep mode.

        Parameters
        ----------
        sweep: array_likes of floats
            Sweep range containing start, stop and step size (e.g. sweep object using qkit.measure.transport.transport.sweep class)

        Returns
        -------
                None
        """
        # Corresponding Command: [:CHANnel<n>]:SOURce:MODE FIXed|SWEep|LIST|SINGle
        # Corresponding Command: [:CHANnel<n>]:SWEep:TRIGger EXTernal|AUXiliary|TIMer1|TIMer2|SENSe
        # Corresponding Command: :TRACe:POINts <integer>|MINimum|MAXimum
        # Corresponding Command: :TRACe:CHANnel<n>:DATA:FORMat ASCii|BINary
        # Corresponding Command: :TRACe:BINary:REPLy BINary|ASCii
        # Corresponding Command: :TRACe[:STATe] 1|0|ON|OFF
        if not self._sweep_mode:  # 0 (VV-mode)
            channel_bias, channel_sense = self._sweep_channels
            self.set_sync(val=True)
        elif self._sweep_mode in [1, 2]:  # 1 (IV-mode) | 2 (VI-mode)
            channel_bias, channel_sense = self._sweep_channels * 2
        try:
            logging.debug(
                f"{__name__!s}: Set sweep parameters of channel {channel_bias:d} and {channel_sense:d} to {sweep!s}"
            )
            self._set_sweep_start(val=float(sweep[0]), channel=channel_bias)
            self._set_sweep_stop(val=float(sweep[1]), channel=channel_bias)
            self._set_sweep_step(val=np.abs(float(sweep[2])), channel=channel_bias)
            self.set_bias_trigger(mode="sens", channel=channel_bias)
            self.set_sense_trigger(mode="sour", channel=channel_sense)
            self.set_bias_value(
                val=self._get_sweep_start(channel=channel_bias), channel=channel_bias
            )
            self._write(f":chan{channel_bias:d}:sour:mode swe")
            self._write(f":chan{channel_bias:d}:swe:trig ext")
            self._write(
                ":trac:poin max"
            )  # alternative: self._write(':trac:poin {:d}'.format(self._get_sweep_nop(channel=channel_bias)))
            self._write(f":trac:chan{channel_sense:d}:data:form asc")
            self._write(":trac:bin:repl asc")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot set sweep parameters of channel {channel_bias:d} and {channel_sense:d} to {sweep!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot set sweep parameters of channel {channel_bias:d} and {channel_sense:d} to {sweep!s}\n{e!s}"
            )
        return

    def get_tracedata(self):
        """
        Starts bias sweep with already set parameters and gets trace data of bias <bias_values> and sense <sense_values> in the set sweep mode.

        Parameters
        ----------
                None

        Returns
        -------
        bias_values: numpy.array(float)
            Measured bias values.
        sense_values: numpy.array(float)
            Measured sense values.
        """
        # Corresponding Command: [:CHANnel<n>]:INITiate [DUAL]
        # Corresponding Command: :STARt
        # Corresponding Command: :TRACe[:STATe] 1|0|ON|OFF
        # Corresponding Command: :TRACe:CHANnel<n>:DATA:READ? [TM|DO|DI|SF|SL|MF|ML|LC|HC|CP]
        if not self._sweep_mode:  # 0 (VV-mode)
            channel_bias, channel_sense = self._sweep_channels
        elif self._sweep_mode in [1, 2]:  # 1 (IV-mode) | 2 (VI-mode)
            channel_bias, channel_sense = self._sweep_channels * 2
        try:
            logging.debug(
                f"{__name__!s}: Take sweep data of channel {channel_bias:d} and {channel_sense:d}"
            )
            self._write(f":chan{channel_bias:d}:init")
            self._wait_for_ready_for_sweep(channel=channel_bias)
            self._write(":trac:stat 1")
            self._wait_for_OPC()
            time.sleep(100e-6)
            self._write(":star")
            self._wait_for_end_of_sweep(channel=channel_bias)
            time.sleep(self.get_sense_delay(channel=channel_sense))
            self._wait_for_end_of_measure(channel=channel_sense)
            self._write(":trac:stat 0")
            bias_values = np.fromstring(
                string=self._ask(f"trac:chan{channel_bias:d}:data:read? sl"),
                dtype=float,
                sep=",",
            )
            sense_values = np.fromstring(
                string=self._ask(f"trac:chan{channel_bias:d}:data:read? ml"),
                dtype=float,
                sep=",",
            )
            return bias_values, sense_values
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot take sweep data of channel {channel_bias!s} and {channel_sense!s}"
            )
            raise type(e)(
                f"{__name__!s}: Cannot take sweep data of channel {channel_bias!s} and {channel_sense!s}\n{e!s}"
            )

    def take_IV(self, sweep):
        """
        Takes IV curve with sweep parameters <sweep> in set sweep mode.

        Parameters
        ----------
        sweep: array_likes of floats
            Sweep range containing start, stop and step size (e.g. sweep object using qkit.measure.transport.transport.sweep class)

        Returns
        -------
        bias_values: numpy.array(float)
            Measured bias values.
        sense_values: numpy.array(float)
            Measured sense values.
        """
        self.set_sweep_parameters(sweep=sweep)
        return self.get_tracedata()

    def get_bias_ccr(self):
        """
        Gets the entire bias condition code register (ccr)

        Parameters
        ----------
        None

        Returns
        -------
        ccr: list of booleans
            Condition code register of bias. Entries are
            0:  CH1 End of Sweep
            1:  CH1 Ready for Sweep
            2:  CH1 Low Limiting
            3:  CH1 High Limiting
            4:  CH1 Tripped
            5:  CH1 Emergency (Temperature/Current over)
            6:  ---
            7:  ---
            8:  CH2 End of Sweep
            9:  CH2 Ready for Sweep
            10: CH2 Low Limiting
            11: CH2 High Limiting
            12: CH2 Tripped
            13: CH2 Emergency (Temperature/Current over)
            14: Inter Locking
            15: Start Sampling Error
        """
        # Corresponding Command: :STATus:SOURce:CONDition?
        try:
            logging.debug(f"{__name__!s}: Get bias ccr")
            ccr = int(self._ask(":stat:sour:cond"))
            ans = []
            for i in range(16):
                ans.append(bool((ccr >> i) % 2))
            return ans
        except Exception as e:
            logging.error(f"{__name__!s}: Cannot get bias ccr")
            raise type(e)(f"{__name__!s}: Cannot get bias ccr\n{e!s}")

    def print_bias_ccr(self):
        """
        Prints the entire bias condition code register (ccr) including explanation.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        ccr = self.get_bias_ccr()
        msg = [
            (f"\n\t{sb[0]:s}:\t{ccr[i]!r}\t({sb[1]:s})")
            for i, sb in enumerate(self.bias_ccr)
            if sb != ("", "")
        ]
        print("Bias ccr :{:s}".format("".join(msg)))
        return

    def get_sense_ccr(self):
        """
        Gets the entire sense condition code register (ccr)

        Parameters
        ----------
        None

        Returns
        -------
        ccr: list of booleans
            Condition code register of sense. Entries are
                0:  CH1 End of Measure
                1:  ---
                2:  CH1 Compare result is Low
                3:  CH1 Compare result is High
                4:  ---
                5:  CH1 Over Range
                6:  ---
                7:  ---
                8:  CH2 End of Measure
                9:  ---
                10: CH2 Compare result is Low
                11: CH2 Compare result is High
                12: ---
                13: CH2 Over Range
                14: End of Trace
                15: Trigger Sampling Error
        """
        # Corresponding Command: :STATus:SENSe:CONDition?
        try:
            logging.debug(f"{__name__!s}: Get sense ccr")
            ccr = int(self._ask(":stat:sens:cond"))
            ans = []
            for i in range(16):
                ans.append(bool((ccr >> i) % 2))
            return ans
        except Exception as e:
            logging.error(f"{__name__!s}: Cannot get sense ccr")
            raise type(e)(f"{__name__!s}: Cannot get sense ccr\n{e!s}")

    def print_sense_ccr(self):
        """
        Prints the entire bias condition code register (ccr) including explanation.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        ssr = self.get_sense_ccr()
        msg = [
            (f"\n\t{sb[0]:s}:\t{ssr[i]!r}\t({sb[1]:s})")
            for i, sb in enumerate(self.sense_ccr)
            if sb != ("", "")
        ]
        print("Sense ccr:{:s}".format("".join(msg)))
        return

    def get_end_of_sweep(self, channel=1):
        """
        Gets event of bias condition code register (ccr) entry "End for Sweep" <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: bool
            End of sweep entry of bias condition code register.
        """
        # Corresponding Command: :STATus:SOURce:EVENt?
        try:
            logging.debug(
                f"""{__name__!s}: Get bias ccr event "End of Sweep" of channel {channel:d}"""
            )
            return bool(
                (int(self._ask(":stat:sour:even")) >> (0 + 8 * (channel - 1))) % 2
            )
        except Exception as e:
            logging.error(
                f'{__name__!s}: Cannot get bias ccr event "End of Sweep" of channel {channel!s}'
            )
            raise type(e)(
                f'{__name__!s}: Cannot get bias ccr event "End of Sweep" of channel {channel!s}\n{e!s}'
            )

    def _wait_for_end_of_sweep(self, channel=1):
        """
        Waits until the event of bias condition code register (ccr) entry "End for Sweep" of channel <channel> occurs.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        None
        """
        while not (self.get_end_of_sweep(channel=channel)):
            time.sleep(100e-3)
        return

    def get_ready_for_sweep(self, channel=1):
        """
        Gets condition of bias condition code register (ccr) entry "Ready for Sweep" <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: bool
            End of sweep entry of bias condition code register.
        """
        # Corresponding Command: :STATus:SOURce:CONDition?
        try:
            logging.debug(
                f"""{__name__!s}: Get bias ccr event "Ready of Sweep" of channel {channel:d}"""
            )
            return bool(
                (int(self._ask(":stat:sour:cond")) >> (1 + 8 * (channel - 1))) % 2
            )
        except Exception as e:
            logging.error(
                f'{__name__!s}: Cannot get bias ccr condition "Ready for Sweep" of channel {channel!s}'
            )
            raise type(e)(
                f'{__name__!s}: Cannot get bias ccr condition "Ready for Sweep" of channel {channel!s}\n{e!s}'
            )

    def _wait_for_ready_for_sweep(self, channel=1):
        """
        Waits until the condition of bias condition code register (ccr) entry "Ready for Sweep" of channel <channel> is fullfilled.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        None
        """
        while not (self.get_ready_for_sweep(channel=channel)):
            time.sleep(100e-3)
        return

    def get_end_of_measure(self, channel=1):
        """
        Gets condition of sense condition code register (ccr) entry "End of Measure" <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: bool
            End of sweep entry of bias condition code register.
        """
        # Corresponding Command: :STATus:SENSe:CONDition?
        try:
            logging.debug(
                f"""{__name__!s}: Get sense ccr event "End of Measure" of channel {channel:d}"""
            )
            return bool(
                (int(self._ask(":stat:sens:cond")) >> (0 + 8 * (channel - 1))) % 2
            )
        except Exception as e:
            logging.error(
                f'{__name__!s}: Cannot get sense ccr event "End of Measure" of channel {channel!s}'
            )
            raise type(e)(
                f'{__name__!s}: Cannot get sense ccr event "End of Measure" of channel {channel!s}\n{e!s}'
            )

    def _wait_for_end_of_measure(self, channel=1):
        """
        Waits until the condition of sense condition code register (ccr) entry "End for Measure" of channel <channel> is fullfilled.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        None
        """
        while not (self.get_end_of_measure(channel=channel)):
            time.sleep(100e-3)
        return

    def get_end_of_trace(self, channel=1):
        """
        Gets condition of sense condition code register (ccr) entry "End of Trace" <val> of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        val: bool
            End of sweep entry of bias condition code register.
        """
        # Corresponding Command: :STATus:SENSe:CONDition?
        try:
            logging.debug(
                f"""{__name__!s}: Get sense ccr event "End of Trace" of channel {channel:d}"""
            )
            return bool((int(self._ask(":stat:sens:cond")) >> 14) % 2)
        except Exception as e:
            logging.error(
                f'{__name__!s}: Cannot get sense ccr event "End of Trace"  of channel {channel!s}'
            )
            raise type(e)(
                f'{__name__!s}: Cannot get sense ccr event "End of Trace"  of channel {channel!s}\n{e!s}'
            )

    def _wait_for_end_of_trace(self, channel=1):
        """
        Waits until the condition of sense condition code register (ccr) entry "End for Trace" of channel <channel> is fullfilled.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
        None
        """
        while not (self.get_end_of_trace(channel=channel)):
            time.sleep(100e-3)
        return

    def get_OPC(self):
        """
        Waits until the condition of standard event register entry "Operation complete" is fulfilled.

        Parameters
        ----------
                None

        Returns
        -------
                None
        """
        # Corresponding Command: *OPC
        try:
            logging.debug(
                f'''{__name__!s}: Get ccr event "Operation complete"'''
            )
            return bool(int(self._ask("*OPC")))
        except Exception as e:
            logging.error(
                f'{__name__!s}: Cannot get ccr condition "Operation complete"'
            )
            raise type(e)(
                f'{__name__!s}: Cannot get ccr condition "Operation complete"\n{e!s}'
            )

    def _wait_for_OPC(self):
        """
        Waits until the condition of standard event register entry "Operation complete" is fulfilled.

        Parameters
        ----------
                None

        Returns
        -------
                None
        """
        while not (self.get_OPC()):
            time.sleep(1e-3)
        return

    def set_defaults(self, sweep_mode=None):
        """
        Sets default settings. Actual settings are:
        default parameters

        Parameters
        ----------
        mode: int
            Sweep mode denoting bias and sense modes. Possible values are 0 (VV-mode), 1 (IV-mode) or 2 (VI-mode). Default is 1

        Returns
        -------
                None
        """
        self.reset()
        # beeper off
        self._write(":syst:beep 0")
        # distiguish different sweep modes
        if sweep_mode is not None:
            self.set_sweep_mode(sweep_mode)
        # set values
        for i, channel in enumerate(self._sweep_channels):
            for func, param in self._defaults[self._sweep_mode][i].items():
                func(param, channel=channel)
        return

    def __set_defaults_docstring(self):
        """
        Sets docstring of "set_defaults" method with actual default settings.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        new = f"sweep mode: {self._sweep_mode:d}:\n" + "".join(
            [
                f"\t    channel: {channel:d}\n"
                + "".join(
                    [
                        f"\t\t{key_parameter:s}: {val_parameter!s}\n"
                        for key_parameter, val_parameter in self._defaults[
                            self._sweep_mode
                        ][i].items()
                    ]
                )
                for i, channel in enumerate(self._sweep_channels)
            ]
        )
        self.set_defaults.__func__.__doc__ = self.set_defaults.__func__.__doc__.replace(
            self._default_str, new
        )
        self._default_str = new
        return

    def get_all(self, channel=1):
        """
        Prints all settings of channel <channel>.

        Parameters
        ----------
        channel: int
            Number of channel of interest. Must be 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        logging.debug(f"{__name__:s}: Get all")
        print(f"synchronization    = {self.get_sync()!r}")
        print(
            f"measurement mode   = {self._measurement_modes[self.get_measurement_mode(channel=channel)]:s}"
        )
        print(
            f"bias mode          = {self._IV_modes[self.get_bias_mode(channel=channel)]:s}"
        )
        print(
            f"sense mode         = {self._IV_modes[self.get_sense_mode(channel=channel)]:s}"
        )
        print(
            f"bias range         = {self.get_bias_range(channel=channel):1.0e}{self._IV_units[self.get_bias_mode(channel=channel)]:s}"
        )
        print(
            f"sense range        = {self.get_sense_range(channel=channel):1.0e}{self._IV_units[self.get_sense_mode(channel=channel)]:s}"
        )
        print(
            f"bias delay         = {self.get_bias_delay(channel=channel):1.3e}s"
        )
        print(
            f"sense delay        = {self.get_sense_delay(channel=channel):1.3e}s"
        )
        print(
            f"sense average      = {self.get_sense_average(channel=channel)[1]:d}"
        )
        print(f"plc                = {self.get_plc():f}Hz")
        print(f"sense nplc         = {self.get_sense_nplc(channel=channel):f}")
        print(
            f"sense autozero     = {self.get_sense_autozero(channel=channel)!r}"
        )
        print(f"status             = {self.get_status(channel=channel)!r}")
        if self.get_status(channel=channel):
            print(
                f"bias value         = {self.get_bias_value(channel=channel):f}{self._IV_units[self.get_bias_mode(channel=channel)]:s}"
            )
            print(
                f"sense value        = {self.get_sense_value(channel=channel):f}{self._IV_units[self.get_sense_mode(channel=channel)]:s}"
            )
        print(
            f"sweep start        = {self._get_sweep_start(channel=channel):f}{self._IV_units[self.get_bias_mode(channel=channel)]:s}"
        )
        print(
            f"sweep stop         = {self._get_sweep_stop(channel=channel):f}{self._IV_units[self.get_bias_mode(channel=channel)]:s}"
        )
        print(
            f"sweep step         = {self._get_sweep_step(channel=channel):f}{self._IV_units[self.get_bias_mode(channel=channel)]:s}"
        )
        print(f"sweep nop          = {self._get_sweep_nop(channel=channel):d}")
        for err in self.get_error():
            print(f"error              = {err[0]:d}\t{err[1]:s}")
        self.print_bias_ccr()
        self.print_sense_ccr()
        return

    def reset(self):
        """
        Resets the instrument or a single channel to default conditions.

        Parameters
        ----------
        channel: int
            Number of channel to be set. Must be None, 1 or 2. Default is 1.

        Returns
        -------
                None
        """
        # Corresponding Command: *RST
        try:
            logging.debug(f"{__name__!s}: Reset instrument to factory settings")
            self._write("*RST")
        except Exception as e:
            logging.error(
                f"{__name__!s}: Cannot reset instrument to factory settings"
            )
            raise type(e)(
                f"{__name__!s}: Cannot reset instrument to factory settings\n{e!s}"
            )
        return

    def get_error(self):
        """
        Gets errors of instrument and removes them from the error queue.

        Parameters
        ----------
                None

        Returns
        -------
        err: array of str
            Entries from the error queue
        """
        # Corresponding Command: :SYSTem:ERRor?
        try:
            logging.debug(f"{__name__!s}: Get errors of instrument")
            err = [self._visainstrument.query(":syst:err?").rstrip().split(",", 1)]
            while err[-1] != ["0", '"No error"']:
                err.append(
                    self._visainstrument.query(":syst:err?").rstrip().split(",", 1)
                )
            if len(err) > 1:
                err = err[:-1]
            err = [[int(e[0]), str(e[1][1:-1])] for e in err]
            return err
        except Exception as e:
            logging.error(f"{__name__!s}: Cannot get errors of instrument")
            raise type(e)(
                f"{__name__!s}: Cannot get errors of instrument\n{e!s}"
            )

    def _raise_error(self):
        """
        Gets errors of instrument and as the case may be raises a python error.

        Parameters
        ----------
                None

        Returns
        -------
                None
        """
        errors = self.get_error()
        if len(errors) == 1 and errors[0][0] == 0:  # no error
            return
        else:
            msg = __name__ + " raises the following errors:"
            for err in errors:
                msg += f"\n{self.err_msg[err[0]]:s} ({err[1]:s})"
            raise ValueError(msg)

    def clear_error(self):
        """
        Clears error of instrument.

        Parameters
        ----------
                None

        Returns
        -------
                None
        """
        # Corresponding Command: *CLS
        try:
            logging.debug(f"{__name__!s}: Clears error of instrument")
            self._write("*CLS")
        except Exception as e:
            logging.error(f"{__name__!s}: Cannot clears error of instrument")
            raise type(e)(
                f"{__name__!s}: Cannot clears error of instrument\n{e!s}"
            )
        return

    def close(self):
        """
        Closes the VISA-instrument to disconnect the instrument.

        Parameters
        ----------
                None

        Returns
        -------
                None
        """
        try:
            logging.debug(f"{__name__!s}: Close VISA-instrument")
            self._visainstrument.close()
        except Exception as e:
            logging.error(f"{__name__!s}: Cannot close VISA-instrument")
            raise type(e)(
                f"{__name__!s}: Cannot close VISA-instrument\n{e!s}"
            )
        return

    def get_parameters(self):
        """
        Gets a parameter list <parlist> of measurement specific setting parameters.
        Needed for .set-file in 'write_additional_files', if qt parameters are not used.

        Parameters
        ----------
                None

        Returns
        -------
        parlist: dict
            Parameter names as keys, corresponding channels of interest as values.
        """
        parlist = {
            "measurement_mode": [1, 2],
            "sync": {"channels": [None]},
            "bias_mode": {"channels": [1, 2]},
            "sense_mode": {"channels": [1, 2]},
            "bias_range": {"channels": [1, 2]},
            "sense_range": {"channels": [1, 2]},
            "bias_trigger": {"channels": [1, 2]},
            "sense_trigger": {"channels": [1, 2]},
            "bias_delay": {"channels": [1, 2]},
            "sense_delay": {"channels": [1, 2]},
            "sense_average": {"channels": [1, 2]},
            "bias_value": {"channels": [1, 2]},
            "plc": {"channels": [None]},
            "sense_nplc": {"channels": [1, 2]},
            "sense_autozero": {"channels": [1, 2]},
            "status": {"channels": [1, 2]},
        }
        return parlist

    def get(self, param, **kwargs):
        """
        Gets the current parameter <param> by evaluation 'get_'+<param> and corresponding channel if needed
        In combination with <self.get_parameters> above.

        Parameters
        ----------
        param: str
            Parameter of interest.
        channels: array_likes
            Number of channels of interest. Must be in {1, 2} for channel specific parameters or None for channel independant (global) parameters.

        Returns
        -------
        parlist: dict
            Parameter names as keys, values of corresponding channels as values.
        """
        channels = kwargs.get("channels").get("channels")
        if channels == [None]:
            return getattr(self, f"get_{param!s}")()
        else:
            return tuple(
                [
                    getattr(self, f"get_{param!s}")(channel=channel)
                    for channel in channels
                ]
            )
