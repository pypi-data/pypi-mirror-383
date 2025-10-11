import argparse
import time

from bk_precision_1900.bk1902b import BK1902B


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimal demo of BK1902B library usage"
    )
    parser.add_argument(
        "port",
        help="Serial port path (e.g., /dev/ttyUSB0 or COM3)",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=9600,
        help="Baud rate (default: 9600)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Serial timeout in seconds (default: 1.0)",
    )
    args = parser.parse_args()

    with BK1902B(args.port, baud=args.baud, timeout=args.timeout) as psu:
        print("Disabling output…")
        psu.disable_output()

        print("Setting initial current and voltage…")
        psu.set_current(0.1)
        psu.set_voltage(1.0)
        time.sleep(1.0)

        print("Enabling output…")
        psu.enable_output()

        for voltage in range(1, 40, 5):
            psu.set_voltage(float(voltage))
            time.sleep(0.5)  # brief settle time
            v, a, is_cv = psu.get_display()
            mode = "CV" if is_cv else "CC"
            print(f"Set {voltage:>2} V  →  Measured {v:.2f} V @ {a:.2f} A  [{mode}]")
            time.sleep(1.5)

        print("Disabling output…")
        psu.disable_output()


if __name__ == "__main__":
    main()
