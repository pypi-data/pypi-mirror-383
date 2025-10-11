"""
BK1902B programmable power supply control:
- Open/close serial port
- Set voltage/current
- Enable/disable output
- Read front-panel display
CLI included at bottom.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from types import TracebackType
from typing import Callable, Optional, Tuple, Union, cast

import serial

Number = Union[int, float]


class BK1902B:
    """Control a BK1902B programmable power supply over a serial port."""

    VOLT_MIN: float = 1.0
    VOLT_MAX: float = 60.0
    CURR_MIN: float = 0.0
    CURR_MAX: float = 16.0  # per manual

    def __init__(self, port: str, baud: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None

    def __enter__(self) -> "BK1902B":
        """Open the serial port on context entry."""
        self.open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def open(self) -> None:
        """Open the serial port."""
        try:
            self.ser = serial.Serial(
                self.port, baudrate=self.baud, timeout=self.timeout
            )
        except serial.SerialException as err:
            raise RuntimeError(f"Serial port {self.port} unavailable") from err

    def close(self) -> None:
        """Close the serial port if open."""
        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.close()
            finally:
                self.ser = None

    @staticmethod
    def _clamp(val: Number, minimum: Number, maximum: Number) -> Number:
        if minimum > maximum:
            raise ValueError("Minimum must be less than or equal to maximum")
        if val < minimum:
            return minimum
        if val > maximum:
            return maximum
        return val

    @staticmethod
    def _to_bk_str(val: Number) -> str:
        """
        BK format is tenths with no decimal, zero-padded to 3 digits.
        Example: 12.3 -> "123", 60.0 -> "600".
        """
        return str(int(round(float(val) * 10))).zfill(3)

    def _require_open(self) -> None:
        if self.ser is None or not self.ser.is_open:
            raise RuntimeError("Serial port is not open. Call open() first.")

    # -------------------------
    # Low-level I/O helpers
    # -------------------------

    def _read_line_cr(self, max_len: int = 32) -> bytes:
        """Read one CR-terminated line, up to max_len bytes including CR."""
        if self.ser is None:
            raise RuntimeError("Serial port is not open. Call open() first.")
        buf = bytearray()
        deadline = time.time() + self.timeout
        while time.time() < deadline and len(buf) < max_len:
            b = self.ser.read(1)
            if not b:
                continue
            buf += b
            if b == b"\r":
                break
        return bytes(buf)

    def _read_ok_line(self) -> None:
        ok = self._read_line_cr()
        if ok != b"OK\r":
            raise RuntimeError(f"Expected OK\\r, got {ok!r}")

    def _send_cmd(self, cmd: str, expect_ok: bool = True) -> None:
        """Send a command and optionally verify an 'OK\\r' reply."""
        self._require_open()
        if self.ser is None:
            raise RuntimeError("Serial port is not open. Call open() first.")

        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.write(cmd.encode("utf-8"))
        self.ser.flush()

        if expect_ok:
            self._read_ok_line()

    # -------------------------
    # Public API
    # -------------------------

    def set_voltage(self, voltage: float) -> float:
        """Set output voltage in the range [1.0, 60.0] V. Returns the applied (clamped) value."""
        original = float(voltage)
        valid_voltage = float(self._clamp(original, self.VOLT_MIN, self.VOLT_MAX))
        self._send_cmd(f"VOLT{self._to_bk_str(valid_voltage)}\r")
        return valid_voltage

    def set_current(self, current: float) -> float:
        """Set output current in the range [0.0, 16.0] A. Returns the applied (clamped) value."""
        original = float(current)
        valid_current = float(self._clamp(original, self.CURR_MIN, self.CURR_MAX))
        self._send_cmd(f"CURR{self._to_bk_str(valid_current)}\r")
        return valid_current

    def enable_output(self) -> None:
        """Enable output."""
        self._send_cmd("SOUT0\r")

    def disable_output(self) -> None:
        """Disable output."""
        self._send_cmd("SOUT1\r")

    def get_display(self) -> Tuple[float, float, bool]:
        """
        Read voltage, current and CV/CC from the front display.
        Returns (voltage_V, current_A, is_constant_voltage).

        Manual shows GETD returns two lines:
          1) VVVV AAAA S [CR]  (no spaces in actual bytes; V and A are 4 digits each;
             S is '0' for CV, '1' for CC)
          2) OK[CR]
        """
        self._require_open()
        if self.ser is None:
            raise RuntimeError("Serial port is not open. Call open() first.")

        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.write(b"GETD\r")

        # First line: measurements
        payload = self._read_line_cr(max_len=16)
        if len(payload) < 2 or payload[-1:] != b"\r":
            raise RuntimeError(f"Bad GETD reply length or terminator: {payload!r}")
        data = payload[:-1]  # strip CR
        if len(data) < 9:
            raise RuntimeError(f"Incomplete GETD payload: {payload!r}")

        v_raw = data[0:4]
        a_raw = data[4:8]
        mode_byte = data[8:9]

        if not (v_raw.isdigit() and a_raw.isdigit() and mode_byte in (b"0", b"1")):
            raise RuntimeError(f"Malformed GETD fields: {payload!r}")

        voltage = int(v_raw) / 100.0
        current = int(a_raw) / 100.0
        is_constant_voltage = mode_byte == b"0"

        # Second line: OK
        self._read_ok_line()

        return voltage, current, is_constant_voltage


# -------------------------
# CLI
# -------------------------


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--port", required=True, help="Serial port, for example COM3 or /dev/ttyUSB0"
    )
    p.add_argument("--baud", type=int, default=9600, help="Baud rate")
    p.add_argument(
        "--timeout", type=float, default=1.0, help="Serial read timeout in seconds"
    )


def _cmd_set_voltage(args: argparse.Namespace) -> int:
    try:
        with BK1902B(args.port, baud=args.baud, timeout=args.timeout) as psu:
            applied = psu.set_voltage(args.voltage)
            if abs(applied - args.voltage) > 1e-6:
                print(f"Voltage clamped to {applied:.1f} V")
            print(f"Voltage set to {applied:.1f} V")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def _cmd_set_current(args: argparse.Namespace) -> int:
    try:
        with BK1902B(args.port, baud=args.baud, timeout=args.timeout) as psu:
            applied = psu.set_current(args.current)
            if abs(applied - args.current) > 1e-6:
                print(f"Current clamped to {applied:.1f} A")
            print(f"Current set to {applied:.1f} A")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def _cmd_output(args: argparse.Namespace) -> int:
    try:
        with BK1902B(args.port, baud=args.baud, timeout=args.timeout) as psu:
            if args.state == "on":
                psu.enable_output()
                print("Output enabled")
            else:
                psu.disable_output()
                print("Output disabled")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def _cmd_read_display(args: argparse.Namespace) -> int:
    try:
        with BK1902B(args.port, baud=args.baud, timeout=args.timeout) as psu:
            v, a, is_cv = psu.get_display()
            if args.json:
                print(
                    json.dumps(
                        {
                            "voltage_V": v,
                            "current_A": a,
                            "mode": "CV" if is_cv else "CC",
                        }
                    )
                )
            else:
                mode = "CV" if is_cv else "CC"
                print(f"{v:.2f} V, {a:.2f} A, mode {mode}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BK1902B command line control")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_v = sub.add_parser("set-voltage", help="Set output voltage in volts")
    _add_common_args(p_v)
    p_v.add_argument("voltage", type=float, help="Voltage in volts, 1.0 to 60.0")
    p_v.set_defaults(func=_cmd_set_voltage)

    p_c = sub.add_parser("set-current", help="Set output current in amps")
    _add_common_args(p_c)
    p_c.add_argument("current", type=float, help="Current in amps, 0.0 to 16.0")
    p_c.set_defaults(func=_cmd_set_current)

    p_o = sub.add_parser("output", help="Turn output on or off")
    _add_common_args(p_o)
    p_o.add_argument("state", choices=["on", "off"], help="Desired output state")
    p_o.set_defaults(func=_cmd_output)

    p_r = sub.add_parser(
        "read-display", help="Read voltage, current, and mode from the front display"
    )
    _add_common_args(p_r)
    p_r.add_argument("--json", action="store_true", help="Print as JSON")
    p_r.set_defaults(func=_cmd_read_display)

    return parser


CommandFunc = Callable[[argparse.Namespace], int]


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    func = cast(CommandFunc, args.func)
    return func(args)


if __name__ == "__main__":
    sys.exit(main())
