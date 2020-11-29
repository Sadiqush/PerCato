import argparse
from pathlib import Path

import textutil

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='yo ez')
    ap.add_argument('batch', type=int, help='batch count')
    ap.add_argument('length', type=int, nargs='?', help='length of words', default=3)
    ap.add_argument('-p', '--path', help='path to save json and images', default=str(Path(__file__).parent.absolute()))
    ap.add_argument('-z', '--zip', action='store_true', help='images will be saved into a zip')
    ap.add_argument('-u', '--ugly', action='store_true', help='will generate ugly data')
    ap.add_argument('-m', '--meaningful', action='store_true', help='will generate only meaninful data')
    args = ap.parse_args()
    path = Path(args.path)
    if not path.is_dir():
        raise NotADirectoryError('Given path is not a directoy', str(path))
    path = str(path)
    print(f'images will {"be" if args.zip else "NOT be"} saved into a zip')
    textutil.batch = args.batch
    textutil.length = args.length
    textutil.is_meaningful = args.meaningful
    # TODO: implement zipping option
    if args.zip:
        raise NotImplementedError("zip option is not implemented yet")
    textutil.ugly_mode = args.ugly
    assert not (textutil.is_meaningful and textutil.ugly_mode), \
        "You can't have ugly and meaninful at the same time retard."
    textutil.image_path = f"{path}{'/'}images/"
    textutil.json_path = f"{path}{'/'}final.json"
    print(f'saving {args.batch} images in "{path}"')
    textutil.main()
