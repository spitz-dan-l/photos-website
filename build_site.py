import argparse
from pathlib import Path
import subprocess
import shutil

import exifread # pip install exifread
from tqdm import tqdm # pip install tqdm


def sh(cmd, *, shell=True, stdout=subprocess.DEVNULL, check=True, **kwds):
    """
    Wrapper around subprocess.run to make the call more concise.
    """
    return subprocess.run(cmd, shell=shell, stdout=stdout, check=check, **kwds)

def try_convert(p: Path, output_dir: Path) -> Path:
    """
    Reimplement this depending on the conversion tool(s) you've got in your environment.

    I am on ubuntu 20.04 and I installed heif-convert with
        sudo apt install libheif-examples
    based on a random website tutorial.

    Takes a file and output directory as input. If it can be converted to jpg, does it and returns the output file. Else returns None.
    """
    if p.is_dir():
        return None
    
    output = output_dir / f'{p.stem}.jpg'
    if output.exists():
        return output

    if p.suffix.upper() in ('.HEIC', '.HEIF'):    
        sh(f"heif-convert {p} -q 70 {output}")
    elif p.suffix.upper() in ('JPG', 'JPEG'):
        shutil.copyfile(p, output)
    else:
        return None
    return output
    
def resize(p: Path, output_dir: Path) -> str:
    """
    Reimplement this depending on the resizing tool you've got in your environment.

    I am on ubuntu 20.04 and I installed imagemagick with
        sudo apt install imagemagick
    based on a random website tutorial.

    Takes a .jpg file and output directory as input, resizes it, returns the output path
    """
    output = output_dir / f'{p.stem}_small.jpg'
    if not output.exists():
        sh(f"convert {p} -resize 500 {output}")
    return output

def get_image_datetime(image: Path):
    """Given an image file, read its EXIF tags for the datetime of the image and return it as a string.
    
    If the Image DateTime tag isn't set this returns the empty string.
    """
    with open(image, 'rb') as f:
        tags = exifread.process_file(f)
    if 'Image DateTime' in tags:
        return tags['Image DateTime'].values
    return ''

def build_redbean(output_dir: Path):
    """
    Build a redbean web server archive of a given directory
    """
    output = output_dir.parent / f"{output_dir.name}.com"
    if output.exists():
        print(f"Redbean archive {output} already exists. Skipping.")
        return output
    print('Downloading Redbean binary')
    sh(f'curl https://redbean.dev/redbean-latest.com >{output} && chmod +x {output}')
    print('Adding site assets to redbean')
    sh(f'zip -r ../{output.name} *', cwd=output_dir)
    return output

def handle_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--photos', type=Path, default=Path.cwd(), help="Photos directory to process")
    parser.add_argument('--site', type=Path, default=Path.cwd() / 'website', help='Output directory')
    parser.add_argument('--skip_redbean', action='store_true', help='Do not create a redbean archive at the end. Useful during development.')

    return parser.parse_args()

def main():
    args = handle_cli()
    
    input_dir: Path = args.photos
    output_dir: Path = args.site

    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f'Photos directory {input_dir} does not exist or not a directory.')
    
    output_dir.mkdir(exist_ok=True, parents=True)

    script_dir = Path(__file__).parent
    print('copying over styles')
    shutil.copyfile(script_dir / 'style.css', output_dir / 'style.css')

    print('converting, resizing, generating index page')
    jpg_dir = output_dir / 'jpg'
    jpg_dir.mkdir(exist_ok=True)

    small_dir = jpg_dir / 'small'
    small_dir.mkdir(exist_ok=True)

    converted = []
    for raw_image in tqdm(list(input_dir.iterdir())):
        jpg = try_convert(raw_image, jpg_dir)
        if jpg is not None:
            converted.append(jpg)

    with open(output_dir / 'index.html', 'wt') as f:
        f.write('''
            <html>
            <head><link href="style.css" rel="stylesheet" type="text/css" /></head>
            <body>
                <h1>Dan's Berlin Trip 2022-06</h1>
        ''')
        for jpg in tqdm(sorted(converted, key=get_image_datetime)):
            jpg_small = resize(jpg, small_dir)
            
            f.write(f'''
                <div class="photo">
                    <a href="{jpg.relative_to(output_dir)}">
                        <img src="{jpg_small.relative_to(output_dir)}" loading="lazy" />
                    </a>
                </div>
            ''')
        f.write('''
            </body>
            </html>
        ''')
    
    if not args.skip_redbean:
        build_redbean(output_dir)
        

if __name__ == '__main__':
    main()
