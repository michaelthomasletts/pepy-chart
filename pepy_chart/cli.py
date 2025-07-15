#!/usr/bin/python3

from click import command, option

from .core import PepyStats


@command()
@option(
    "-p",
    "--package",
    type=str,
    help="The name of the Python package",
    required=True,
)
@option(
    "-a",
    "--apikey",
    type=str,
    help="The PePy API key",
    required=True,
)
@option(
    "-c",
    "--createimage",
    is_flag=bool,
    help="Whether to create chart or not",
)
@option(
    "-op",
    "--outputpath",
    type=str,
    help="Where to save the image",
)
@option(
    "-rw",
    "--rollingwindow",
    type=int,
    help="The size of the rolling window",
    default=7,
)
@option(
    "-o",
    "--openimage",
    is_flag=True,
    help="Whether to open the image after it's created",
)
@option(
    "-c", "--color", type=str, help="The prevailing color", default="#FF0000FF"
)
@option("-f", "--fontsize", type=int, default=14)
def create(
    package,
    apikey,
    createimage,
    outputpath,
    rollingwindow,
    openimage,
    color,
    fontsize,
):
    ps = PepyStats(
        package=package,
        api_key=apikey,
        create_image=createimage,
        output_path=outputpath,
        rolling_window=rollingwindow,
        automatically_open_img=openimage,
        color=color,
        title_fontsize=fontsize,
    )


if __name__ == "__main__":
    create()
