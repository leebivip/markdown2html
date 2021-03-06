#!/usr/bin/env python3

# Copyright 2016 Panagiotis Ktistakis <panktist@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Usage: markdown2html.py [options] <file>

Convert a GitHub Flavored Markdown file to HTML, using
markdown, pygments and the latest github-markdown.css from
https://github.com/sindresorhus/github-markdown-css

Options:
  -o, --out <file>  Write output to <file>
  -f, --force       Overwrite existing CSS file
  -p, --preview     Open generated HTML file in browser
  -q, --quiet       Show less information
  -h, --help        Show this help message and exit
"""

import logging
import os
import sys
import urllib.request
import webbrowser

import markdown

TEMPLATE = """\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>%s</title>
    <link rel="stylesheet" href="%s">
    <style>
      .markdown-body {
        border: 1px solid #ddd;
        border-radius: 3px;
        max-width: 980px;
        margin: 64px auto 48px;
        padding: 45px 45px 29px;
      }
    </style>
  </head>
  <body>
    <article class="markdown-body">
      %s
    </article>
  </body>
</html>
"""


def download_css(path):
    """Get latest github-markdown.css and store it at `path`."""
    url = ('https://raw.githubusercontent.com/sindresorhus/'
           'github-markdown-css/gh-pages/github-markdown.css')
    try:
        with urllib.request.urlopen(url) as r, open(path, 'wb') as f:
            f.write(r.read())
    except urllib.error.URLError:
        logging.warning("Unable to download CSS file")


def render(text, title, csspath):
    """Convert a Markdown string to an HTML page.

    The following Markdown extensions are used to support most GFM features:
    codehilite, fenced_code, sane_lists, tables.
    """
    body = markdown.markdown(
        text,
        extensions=[
            'markdown.extensions.codehilite',
            'markdown.extensions.fenced_code',
            'markdown.extensions.sane_lists',
            'markdown.extensions.tables',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'guess_lang': False,
                'noclasses': True,
                'pygments_style': 'tango',
            }
        }
    )
    # Don't use the line-height style from pygments
    body = body.replace(' style="line-height: 125%"', '')
    html = TEMPLATE % (title, csspath, body)
    return html


def run(mdpath, out=None, force=False, preview=False):
    """Generate an HTML file from a Markdown one."""
    if not os.path.isfile(mdpath):
        logging.error("No such file: %s", mdpath)
        sys.exit(1)
    mdfilename = os.path.basename(mdpath)
    htmlpath = out or '/tmp/%s.html' % os.path.splitext(mdfilename)[0]
    csspath = '%s/.cache/github-markdown.css' % os.environ['HOME']

    if force or not os.path.isfile(csspath):
        logging.info("Downloading github-markdown.css...")
        download_css(csspath)

    logging.info("Converting %s to HTML...", mdfilename)
    with open(mdpath) as f:
        text = f.read()
    html = render(text, title=mdfilename, csspath=csspath)
    with open(htmlpath, 'w') as f:
        f.write(html)

    if preview:
        browser = webbrowser.get().name
        logging.info("Opening %s in %s...", htmlpath, browser)
        webbrowser.open(htmlpath)


def main():
    """Parse arguments and run."""
    from docopt import docopt
    args = docopt(__doc__)

    logging.basicConfig(format='%(message)s')
    if args['--quiet']:
        logging.root.setLevel(logging.WARNING)
    else:
        logging.root.setLevel(logging.INFO)

    run(
        args['<file>'],
        args['--out'],
        args['--force'],
        args['--preview']
    )


if __name__ == '__main__':
    main()
