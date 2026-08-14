from __future__ import annotations

import argparse
import sys

from aula_f99 import protocol
from aula_f99.controller import AulaF99


def main() -> int:
    parser = argparse.ArgumentParser(prog="aula-f99")
    parser.add_argument(
        "--wired", action="store_true", help="use wired USB mode instead of the wireless dongle"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    color = sub.add_parser("color", help="set a solid RGB color")
    color.add_argument("r", type=int)
    color.add_argument("g", type=int)
    color.add_argument("b", type=int)

    sub.add_parser("model", help="query and print the connected model")
    sub.add_parser("tui", help="launch the interactive TUI")

    args = parser.parse_args()

    if args.command == "tui":
        from aula_f99.tui.app import main as tui_main

        tui_main()
        return 0

    if args.command == "color":
        try:
            protocol.validate_rgb(args.r, args.g, args.b)
        except ValueError as exc:
            # Caught here, separately from the device I/O below: an
            # out-of-range value is a user-input mistake, not a device
            # failure, and it should never even reach for the device to
            # find that out.
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    try:
        with AulaF99(wired=args.wired) as kb:
            if args.command == "color":
                kb.set_solid_color(args.r, args.g, args.b)
                print(f"Set solid color to ({args.r}, {args.g}, {args.b})")
            elif args.command == "model":
                model_id = kb.query_model()
                if model_id is None:
                    print("No response from keyboard")
                    return 1
                name = protocol.MODEL_IDS.get(model_id, f"unknown (0x{model_id:02x})")
                print(f"Model: {name}")
    except (RuntimeError, OSError) as exc:
        # RuntimeError: no matching HID interface found (device.py's own check).
        # OSError: hidapi's open/write/read failure -- permission denied, the
        # interface vanished mid-command, etc. Either way, fail with the
        # reason instead of a raw traceback.
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
