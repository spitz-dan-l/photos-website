# Photo website generator

Code to turn a directory of photos into a single-file web server.

I went on vacation and I wanted to share all the photos I took with friends and family, but WITHOUT:

- Uploading the photos to social media
- Messing around with a complicated, depressing CMS like wordpress

I accomplished this using:
- Basic image processing tools [ImageMagick](https://imagemagick.org/index.php), [libheif](https://github.com/strukturag/libheif) and [EXIF.py](https://github.com/ianare/exif-py)
- [Redbean](https://redbean.dev/) single-file multi-OS web server
- Python to script the image processing and site generation
- [fly.io](fly.io) to deploy it for free
- Fly requires you to use [docker](https://www.docker.com/), so docker

# Installation

Clone this repo. Get your photos all together in a local directory. Install the following image processing tools and python packages:

```sh
sudo apt install libheif-examples
sudo apt install imagemagick
pip install exifread
pip install tqdm
```

If you would prefer to process or convert your images in a different way, then reimplement the functions `try_convert()` and `resize()` in `build_site.py`. Right now it only works for HEIF and JPEG formats. (These photos came off my iPhone.)

# Usage

It is basically a 2-step process:

1. Run `python build_site.py --photos path/to/photos --site path/to/site` to process the images, generate HTML for a static image-viewing site, and bundle it all together using Redbean. Produces `path/to/site` and `path/to/site.com` (the redbean executable server/zip).
2. Deploy the newly-created Redbean executable any way you want. (Like I mentioned I used fly.io, which required me to further bake the executable into a trivial docker image. Example in [deploy](deploy/Dockerfile).)

# What it does

First it converts all the images into JPEGs. Then it creates a smaller second copy of all the jpegs to render on the index page faster. (You can click any image to get to the big version.) It puts these files into `website/jpg/` and `website/jpg/small/` respectively.

It also generates a `website/index.html` page which displays all images in chronological order according to the EXIF tags of the images. It also copies in a `website/style.css`.

Note, if you passed in an argument for `--site my/path`, then it will use that instead of "website" above.

Finally, it takes the full contents of `website/` and adds it all to a Redbean executable web server archive. [Redbean](redbean.dev) is a crazy project, do check it out. The Redbean executable will be named `website.com` (or whatever you passed for `--site`).



