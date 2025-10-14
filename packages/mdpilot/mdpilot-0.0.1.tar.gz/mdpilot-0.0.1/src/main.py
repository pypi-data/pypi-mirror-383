from . import __version__


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(prog="mdp", description="MDPilot — Molecular Dynamics Processing Informatics Library Operations & Tools")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    args = p.parse_args()
    if args.version:
        print(__version__)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
