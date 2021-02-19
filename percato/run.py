import argparse
from pathlib import Path

import main


def run():
    ap = argparse.ArgumentParser(description='...')
    ap.add_argument('batch', type=int, nargs='+', help='Batch count')
    ap.add_argument('length', type=int, nargs='?', help='Length of words (default = 3)', default=3)
    ap.add_argument('-p', '--path', nargs='?', help='Path to save json and images', default=str(Path(__file__).parent.absolute()))
    # TODO: implement zipping option
    ap.add_argument('-z', '--zip', nargs='?', action='store_true', help='Images will be saved into a zip')
    ap.add_argument('-u', '--ugly', nargs='?', action='store_true',
                    help='Will generate ugly words, uses random alphabets (default = False')
    ap.add_argument('-m', '--meaningful', nargs='?', action='store_true',
                    help='Will generate only meaningful words (default = False)')
    args = ap.parse_args()

    path = Path(args.path)
    if not path.is_dir():
        raise NotADirectoryError('Given path is not a directory', str(path))
    path = str(path)

    print(f'Images will {"be" if args.zip else "NOT be"} saved into a zip file')

    main.batch = args.batch
    main.length = args.length
    main.is_meaningful = args.meaningful

    if args.zip:
        raise NotImplementedError("zip option is not implemented yet")
    main.ugly_mode = args.ugly
    assert not (main.is_meaningful and main.ugly_mode), \
        "You can't have ugly and meaningful at the same time."
    main.image_path = f"{path}{'/'}images/"
    main.json_path = f"{path}{'/'}final.json"
    print(f'Saving {args.batch} images in "{path}"')
    main.main()


if __name__ == '__main__':
    run()
