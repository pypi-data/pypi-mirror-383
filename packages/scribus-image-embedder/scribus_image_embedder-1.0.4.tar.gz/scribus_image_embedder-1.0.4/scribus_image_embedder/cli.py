import sys
import argparse
import os
from .embedder import embed_images_in_sla, log

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Embed linked images inline into a Scribus .sla file (images only)"
    )
    ap.add_argument("input_sla", help="Path to .sla")
    ap.add_argument("-o", "--output", help="Output .sla path")
    args = ap.parse_args()

    if not os.path.exists(args.input_sla):
        log(f"✗ Input not found: {args.input_sla}")
        sys.exit(1)

    res = embed_images_in_sla(args.input_sla, args.output)
    sys.exit(0 if res else 1)

if __name__ == "__main__":
    main()
