"""Advent of Code {YEAR}, Day: {DAY}
Link: https://adventofcode.com/{YEAR}/day/{DAY}"""

from pathlib import Path

from aoc_mod.utilities import (AocMod, AocModError, get_year_and_day,
                               parse_input)


def part_one(parsed_input: list[str]) -> dict[str, int]:
    """create the part one solution here

    :param parsed_input: list of strings from parsed input
    :type parsed_input: list[str]
    :return: a dictionary containing the result and a boolean
        where True will submit the part two result
    :rtype: dict[str, int]
    """
    print("Part One")
    output = dict(result=0, submit=False)

    return output


def part_two(parsed_input: list[str]) -> dict[str, int]:
    """create the part two solution here

    :param parsed_input: list of strings from parsed input
    :type parsed_input: list[str]
    :return: a dictionary containing the result and a boolean
        where True will submit the part two result
    :rtype: dict[str, int]
    """
    print("Part Two")
    output = dict(result=0, submit=False)

    return output


def main():
    """main driver function"""
    # set up aoc_mod
    try:
        aoc_mod = AocMod()
    except AocModError as err:
        print(f"Error occurred while initializing AocMod: {err}")
        exit(1)

    # get current path to file
    current_path_to_file = Path(__file__).absolute().parent

    # get the current year and day and then the input filepath
    year, day = get_year_and_day(current_path_to_file)
    if not year and not day:
        exit(1)

    input_path = current_path_to_file.joinpath(f"input_day{day}.txt")

    print(f"{year}:Day{day}")

    # get the answer for part one
    answer_one = part_one(parse_input(input_path))

    # submit part one, if ready
    if answer_one["submit"]:
        result = aoc_mod.submit_answer(year, day, 1, answer_one["result"])

        # if we get the correct answer for part one, we'll retrieve the instructions for part two
        if "That's the right answer" in result:
            aoc_mod.get_puzzle_instructions(year, day)

    # get the answer for part two
    answer_two = part_two(parse_input(input_path))

    # submit part two, if ready
    if answer_two["submit"]:
        result = aoc_mod.submit_answer(year, day, 2, answer_two["result"])

        # if we get the correct answer for part two, we'll retrieve the rest of the instructions
        if "That's the right answer" in result:
            aoc_mod.get_puzzle_instructions(year, day)


if __name__ == "__main__":
    main()
    main()
    main()
    main()
    main()
    main()
