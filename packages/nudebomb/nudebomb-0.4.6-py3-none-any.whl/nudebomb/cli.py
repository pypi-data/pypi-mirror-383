"""Command line interface for nudebomb."""

from argparse import Action, ArgumentParser, Namespace, RawDescriptionHelpFormatter

from termcolor import colored
from typing_extensions import override

from nudebomb.config import NudebombConfig
from nudebomb.version import VERSION
from nudebomb.walk import Walk


class CommaListAction(Action):
    """Split arguments by commas into a list."""

    DELINEATOR: str = ","

    @override
    def __call__(self, _, namespace, values, _option_string=None):
        """Split by delineator and assign to dest variable."""
        items = values.strip().split(self.DELINEATOR)
        setattr(namespace, self.dest, items)


COLOR_KEY = (
    ("MKV ignored/skipped", "dark_grey", []),
    ("MKV skipped because timestamp unchanged", "light_green", ["dark", "bold"]),
    ("MKV already stripped", "green", []),
    ("MKV stripped tracks", "white", []),
    ("MKV not remuxed on dry run", "dark_grey", ["bold"]),
    ("WARNING", "light_yellow", []),
    ("ERROR", "light_red", []),
)


def get_dot_color_key():
    """Create dot color key."""
    epilogue = "Dot color key:\n"
    for text, color, attrs in COLOR_KEY:
        epilogue += "\t" + colored(text, color=color, attrs=attrs) + "\n"
    return epilogue


def get_arguments(params=None):
    """Command line interface."""
    description = "Strips unnecessary tracks from MKV files."
    epilog = get_dot_color_key()
    parser = ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Enable mkvmerge dry run for testing.",
    )
    parser.add_argument(
        "-b",
        "--mkvmerge-bin",
        action="store",
        help="The path to the MKVMerge executable.",
    )
    parser.add_argument(
        "-l",
        "--languages",
        action=CommaListAction,
        help=(
            "Comma-separated list of audio and subtitle languages to retain. "
            "e.g. eng,fre."
        ),
    )
    parser.add_argument(
        "-U",
        "--strip-und-language",
        action="store_true",
        help=(
            "Strip the 'und' undetermined or untagged language tracks. "
            "By default nudebomb does not strip these tracks."
        ),
    )
    parser.add_argument(
        "-s",
        "--sub-languages",
        action=CommaListAction,
        required=False,
        help=(
            "Comma-separated list of subtitle specific languages to retain. "
            "Supersedes --languages."
        ),
    )
    parser.add_argument(
        "-S",
        "--no-subtitles",
        action="store_false",
        dest="subtitles",
        help=(
            "If no subtitles match the languages to retain, strip all subtitles. "
            "By default nudebomb keeps all subtitles if no subtitles match specified "
            "languages."
        ),
    )
    parser.add_argument(
        "-i",
        "--ignore",
        action=CommaListAction,
        dest="ignore",
        help="List of globs to ignore.",
    )
    parser.add_argument(
        "-L",
        "--no-symlinks",
        action="store_false",
        dest="symlinks",
        help="Do not follow symlinks for files and directories",
    )
    parser.add_argument(
        "-T",
        "--no-title",
        action="store_false",
        dest="title",
        help="Do not rewrite the metadata title with the filename stem when remuxing.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        help="Verbose output. Can be used multiple times for noisier output.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        dest="verbose",
        const=0,
        help="Display little to no output.",
    )
    parser.add_argument(
        "-r",
        "--recurse",
        action="store_true",
        help="Recurse through all paths on the command line.",
    )
    parser.add_argument(
        "-t",
        "--timestamps",
        action="store_true",
        help=(
            "Read and write timestamps to strip only files that have been "
            "modified since the last run."
        ),
    )
    parser.add_argument(
        "-C",
        "--timestamps-no-check-config",
        dest="timestamps_check_config",
        action="store_false",
        default=True,
        help="Do not compare program config options with loaded timestamps.",
    )
    parser.add_argument(
        "-c", "--config", action="store", help="Alternate config file path"
    )
    parser.add_argument(
        "-A",
        "--after",
        action="store",
        dest="after",
        help=(
            "Only strip mkvs after the specified timestamp. "
            "Supersedes recorded timestamp files. Can be an epoch number or "
            "datetime string."
        ),
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {VERSION}"
    )
    parser.add_argument(
        "paths",
        metavar="path",
        type=str,
        nargs="+",
        help="Where your MKV files are stored. Can be a directories or files.",
    )

    # Parse the list of given arguments
    if params is not None:
        params = params[1:]
    nns = parser.parse_args(params)

    # increment verbose
    if nns.verbose is None:
        nns.verbose = 1
    elif nns.verbose > 0:
        nns.verbose += 1

    return Namespace(nudebomb=nns)


def main(args: tuple[str, ...] | None = None):
    """Process command line arguments, config and walk inputs."""
    arguments = get_arguments(args)
    config = NudebombConfig().get_config(arguments)
    # Iterate over all found mkv files
    walker = Walk(config)
    walker.run()


if __name__ == "__main__":
    main()
