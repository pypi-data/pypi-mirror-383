"""Script to initialize a new day for Advent of Code.
This script will basically grab the input and puzzle clue
from the Advent of Code website.

If user specifies a year and day, this script will create
the files pertaining to that day and year.

Note: This script is being provided as a courtesy and is simply
an example of using the AocMod class for a command-line utility.
While the functionality is correct here and the CLI can be utilized
in a user's local install, it is recommended to perform any
desired tweaks to ensure proper functionality.

Author: David Eyrich
"""

import argparse
import importlib.metadata
from pathlib import Path

from aoc_mod.utilities import AocMod, AocModError

LOCAL_PUZZLE_FILEPATH = "challenges/{YEAR}/day{DAY}"
DEFAULT_FILE_TEMPLATE = (
    Path(__file__).absolute().parent.joinpath("templates/solution_template.py")
)


def create_solution_file(filename_in: str, day_path: Path, year: int, day: int):
    """read in the template solution file and replace instances of "{YEAR}"
    and "{DAY}" with the corresponding year and day arguments

    :param filename_in: path to the input file
    :type filename_in: str
    :param day_path: path to the output directory
    :type filename_out: Path
    :param year: year that was entered
    :type year: int
    :param day: day that was entered
    :type day: int
    :raises AocModError: if an error occurs with file operations
    """

    temp_in = Path(filename_in)
    temp_out = day_path.joinpath(f"day{day}.{temp_in.suffix}")

    if temp_out.exists():
        raise AocModError(f"{year}, Day {day} solution file already exists")

    try:
        with temp_in.open("r", encoding="utf-8") as f_in:
            data = f_in.read()

        data_w_year = data.replace("{YEAR}", f"{year}")
        data_w_year_day = data_w_year.replace("{DAY}", f"{day}")

        with temp_out.open("w", encoding="utf-8") as f_out:
            f_out.write(data_w_year_day)
    except (OSError, TypeError) as err:
        raise AocModError("Failed to create solution file") from err


def setup_challenge_day_template(
    aoc_mod: AocMod,
    year: int,
    day: int,
    output_root_dir: str = "",
    template_path: str = "",
):
    """set up a template folder named "challenges/{year}/day{day}" that contains
    the puzzle input (.txt), instructions (.md) and a template solution file, if
    specified

    :param year: year of the AoC puzzle
    :type year: int
    :param day: day of the AoC puzzle
    :type day: int
    :param output_root_dir: path to be prepended to the template folder,
        defaults to the current directory
    :type output_root_dir: str, optional
    :param template_path: path to a template file to use for solution code,
        defaults to ""
    :type template_path: str, optional
    """

    # set output directory path (prepend root_dir, if specified)
    day_path = Path(output_root_dir).joinpath(
        LOCAL_PUZZLE_FILEPATH.format(YEAR=year, DAY=day)
    )

    # set individual file paths
    input_path = day_path.joinpath(f"input_day{day}.txt")
    instructions_path = day_path.joinpath(f"instructions_day{day}.md")

    # attempt to get puzzle input and instructions
    input_data = ""
    instructions = ""

    # get puzzle input data
    if not input_path.exists():
        try:
            input_data = aoc_mod.get_puzzle_input(year, day)
        except AocModError as err:
            print(f"Failed to get puzzle input for {year}, Day {day} ({err})")
    else:
        print(f"{year}, Day {day} input file already exists.")

    # get instruction input data
    if not instructions_path.exists():
        try:
            instructions = aoc_mod.get_puzzle_instructions(year, day)
        except AocModError as err:
            print(f"Failed to get puzzle instructions for {year}, Day {day} ({err})")
    else:
        print(f"{year}, Day {day} instruction file already exists.")

    # create the challenges directory structure if we have input/instruction data
    if input_data or instructions:
        day_path.mkdir(parents=True, exist_ok=True)

    if input_data:
        with input_path.open("w", encoding="utf-8") as f_out:
            f_out.write(input_data)
        print(f"{year}, Day {day} input file created: {input_path}")

    if instructions:
        with instructions_path.open("w", encoding="utf-8") as f_out:
            f_out.write(instructions)
        print(f"{year}, Day {day} instructions file created: {instructions_path}")

    try:
        create_solution_file(template_path, day_path, year, day)
        print(f"{year}, Day {day} solution file created.")
    except AocModError as err:
        print(err)


def file_exists(filepath: str) -> str:
    """verify that a file exists for argparse argument

    :param filepath: path to the file
    :type filepath: str
    :raises argparse.ArgumentTypeError: raise if file doesn't exist or
        filepath is not a file
    :return: filepath, once verified
    :rtype: str
    """
    path = Path(filepath)

    if not path.exists():
        raise argparse.ArgumentTypeError(f"Error: file '{filepath}' does not exist")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Error: '{filepath}' is not a file")
    return filepath


def parse_arguments() -> tuple[argparse.Namespace, list[str]]:
    """create an argument parser and parse user args

    :return: parser.parse_known_args() return value
    :rtype: tuple[Type[argparse.Namespace], list[str]]
    """

    ### define the basic parser object ###

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--version",
        action="version",
        version=f"aoc-mod version {importlib.metadata.version('aoc-mod')}",
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        help="year of the puzzle",
    )
    parser.add_argument(
        "-d",
        "--day",
        type=int,
        help="day of the puzzle",
    )
    parser.add_argument(
        "-s",
        "--session-id",
        type=str,
        help="session-id from an authenticated Advent of Code browser session",
    )

    subparsers = parser.add_subparsers(required=True)

    ### define setup arguments ###

    setup_parser = subparsers.add_parser(
        "setup", help="setup challenge files for AoC puzzle"
    )
    setup_parser.add_argument(
        "-t",
        "--template",
        type=file_exists,
        default=DEFAULT_FILE_TEMPLATE,
        help="path to a code template file",
    )
    setup_parser.add_argument(
        "-o",
        "--output-root-dir",
        type=str,
        default="",
        help="root path where the 'challenges' folder structure will be created",
    )

    ### define submission arguments ###

    submit_parser = subparsers.add_parser(
        "submit", help="submit answer for an AoC puzzle"
    )
    submit_parser.add_argument(
        "-a", "--answer", type=int, help="answer to submit", required=True
    )
    submit_parser.add_argument(
        "-p",
        "--part",
        choices=[1, 2],
        type=int,
        help="part A = 1; part B = 2",
        required=True,
    )

    return parser.parse_known_args()


def interactive():
    """Entry-point to the aoc-mod program"""

    known_opts, _ = parse_arguments()

    # create an AOCMod class instance
    try:
        aoc_mod = AocMod(session_id=known_opts.session_id)
    except AocModError as err:
        print(f"Error: could not initialize AocMod ({err})")
        exit(1)

    # parse the year and day
    if known_opts.year is not None and known_opts.day is not None:
        year = known_opts.year
        day = known_opts.day
    else:
        year = aoc_mod.curr_time.tm_year
        day = aoc_mod.curr_time.tm_mday

    print(f"Year: {year}\tDay: {day}")

    # if we are submitting, let's do it, otherwise we'll setup the template
    if "answer" in known_opts and "part" in known_opts:
        print(f"Answer: {known_opts.answer}\tLevel: {known_opts.part}")

        # attempt to submit the answer
        try:
            aoc_mod.submit_answer(year, day, known_opts.part, known_opts.answer)
        except AocModError as err:
            print(f"Failed to submit puzzle answer ({err})")

    else:
        setup_challenge_day_template(
            aoc_mod,
            year,
            day,
            output_root_dir=known_opts.output_root_dir,
            template_path=known_opts.template,
        )
