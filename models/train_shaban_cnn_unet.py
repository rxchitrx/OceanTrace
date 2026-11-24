"""Train the Shaban-style two-stage CNN gate + U-Net comparison on original SOS PALSAR."""

from baseline_runner import run_cli


def main():
    run_cli('shaban', __doc__)


if __name__ == '__main__':
    main()
