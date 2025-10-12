from . import __version__


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(prog="mdsb", description="MDSB — Molecular Dynamics Simulations of Biomolecules (placeholder).")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    args = p.parse_args()
    if args.version:
        print(__version__)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
