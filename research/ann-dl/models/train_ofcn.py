"""Train Bianchi-style OFCN(32) on the original SOS ALOS PALSAR split."""

from baseline_runner import run_cli


def main():
    run_cli('ofcn', __doc__)


if __name__ == '__main__':
    main()
