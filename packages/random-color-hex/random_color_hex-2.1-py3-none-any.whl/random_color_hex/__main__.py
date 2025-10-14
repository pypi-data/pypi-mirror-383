# random_color_hex/__main__.py
import argparse
from . import main

def _parse():
    p = argparse.ArgumentParser(description="Print a random CSS hex color.")
    p.add_argument("--no-superlight", action="store_true",
                   help="Disallow very light/near-white colors.")
    p.add_argument("--distance", default="s", choices=["s","m","l","sl"],
                   help="Separation: s=small, m=medium, l=large, sl=super large")
    return p.parse_args()

def run():
    args=_parse()
    print(main(SuperLightColorsAllowed=not args.no_superlight,
               HowDifferentShouldColorsBe=args.distance))

if __name__ == "__main__":
    run()
