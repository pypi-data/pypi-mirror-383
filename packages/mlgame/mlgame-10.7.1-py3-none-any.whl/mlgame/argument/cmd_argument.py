import os
import sys
from argparse import ArgumentParser, REMAINDER

import pydantic

from mlgame.argument.model import MLGameArgument
from mlgame.utils.logger import logger
from mlgame.version import version


def create_cli_args_parser():
    """
    Generate an ArgumentParser for parse the arguments in the command line
    """
    usage_str = "python -m mlgame [options] <game_folder> [game_params]"
    description_str = ("A platform for applying machine learning algorithm "
                       "to play pixel games. "
                       "In default, the game runs in the machine learning mode. ")

    parser = ArgumentParser(usage=usage_str, description=description_str,
                            add_help=False)

    parser.add_argument("game_folder",
                        type=os.path.abspath,
                        nargs="?",
                        help="the name of the game to be started")
    parser.add_argument("game_params", nargs=REMAINDER, default=None,
                        help="[optional] the additional settings for the game. "
                             "Note that all arguments after <game> will be collected to 'game_params'.")

    group = parser.add_argument_group(title="functional options")
    group.add_argument("-v", "--version", action="version", version=version)
    group.add_argument("-h", "--help", action="help",
                       help="show this help message and exit. "
                            "If this flag is specified after the <game>, "
                            "show the help message of the game instead.")

    group.add_argument("-f", "--fps", type=int, default=30,
                       help="the updating frequency of the game process [default: %(default)s]")

    group.add_argument("-1", "--one-shot", action="store_true",
                       dest="one_shot_mode",
                       help="quit the game when the game is passed or is over. "
                            "Otherwise, the game will restart automatically. [default: %(default)s]")
    group.add_argument("--nd", "--no-display", action="store_true",
                       dest="no_display", default=False,
                       help="didn't display the game on screen. [default: %(default)s]")
    group.add_argument("--ws_url",
                       type=str,
                       dest="ws_url",
                       help="ws_url route")

    group.add_argument("-i", "--input-ai",
                       # type=validate_file,
                       type=str,
                       action="append",
                       dest="labeled_ai_orig",
                       default=None, metavar="SCRIPT",
                       help="specify user script(s) for the machine learning mode. "
                            "For multiple user scripts, use this flag multiple times. "
                            "The script path could be relative path or absolute path "
                       )
    group.add_argument("-o", "--output-folder",
                       # type=validate_file,
                       type=os.path.abspath,
                       dest="output_folder",
                       default=None, metavar="SCRIPT",
                       help="Save each frame of game progress into destination folder."
                            "This folder should be existed and it will create a timestamp folder."
                       )
    group.add_argument("-r", "--progress-folder","--record-folder",
                       # type=validate_file,
                       type=os.path.abspath,
                       dest="record_folder",
                       default=None, metavar="SCRIPT",
                       help="Save game process as a file into destination folder."
                            "This folder should be existed and it will create a timestamp folder."
                       )

    group.add_argument("-p", "--progress-frame-frequency", type=int, default=300,
                       help="the frequency of the game progress save [default: %(default)s]")
    group.add_argument("--ns", "--no-sound", action="store_false",
                       dest="is_sound_on", default=True,
                       help="didn't play music and sound. [default: %(default)s]")
    group.add_argument("--debug", action="store_true",
                       dest="is_debug", default=False,
                       help="show all debug info in console. [default: %(default)s]")

    # group.add_argument("--group_ai",default=None,
    #                    action="append",
    #                    dest="group_ai_orig",
    #                    help="set ai with team group, team should be one of ['A','B','C','D'] ,"
    #                         "player number should be ['1P','2P',...,'8P'] \n"
    #                         "!Important: this argument will overwrite input from --input-ai or -i \n"
    #                         "format: --group_ai A,1P,/path/to/ml_play.py,ai_label "
    #                    )
    group.add_argument("--az_upload_url",
                       type=str,
                       dest="az_upload_url",
                       help="Azure Blob Storage upload URL")

    return parser


def parse_cmd_and_get_arg_obj(arg_str: list) -> MLGameArgument:
    arg_parser = create_cli_args_parser()
    try:
        parsed_args = arg_parser.parse_args(arg_str)
    except pydantic.ValidationError as e:
        logger.exception(f"Error in parsing command : {e.__str__()}")
        arg_parser.print_help()
        sys.exit()

    arg_obj = MLGameArgument(**parsed_args.__dict__)
    # how to resolve if file or directory at path  does not exist
    return arg_obj
