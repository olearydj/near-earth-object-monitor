from neo_monitor.cli import main


# This file supports `python -m neo_monitor`. The guard prevents main() from
# running when another module imports this file.
if __name__ == "__main__":
    main()
