"""Train the Shaban-style two-stage CNN gate + U-Net on all positive oil crops (dropping the 40-60% filter)."""

import sys
from baseline_runner import run_cli


def main():
    if '--min-oil' not in sys.argv:
        sys.argv.extend(['--min-oil', '0.01'])
    if '--run-name' not in sys.argv:
        sys.argv.extend(['--run-name', 'run-shaban-full'])
    run_cli('shaban', __doc__)


if __name__ == '__main__':
    main()
