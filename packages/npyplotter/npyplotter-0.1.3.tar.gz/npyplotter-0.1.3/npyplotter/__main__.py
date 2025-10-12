import argparse
from npyplotter.plot_npy import plot


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('img_file_paths', nargs='+')
    parser.add_argument(
        '--no-index',
        dest='no_index',
        action='store_true',
        default=False
    )
    parser.add_argument('--limits', action='store_true', default=False)
    parser.add_argument('--stats', action='store_true', default=False)
    parser.add_argument('--sort', action='store_true', default=False)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--default-titles', action='store_true', default=False)
    args = parser.parse_args()
    plot(
        args.img_file_paths,
        limits=args.limits,
        stats=args.stats,
        offset=args.offset,
        enable_index=not args.no_index,
        default_titles=args.default_titles,
    )
