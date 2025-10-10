""" 
Author: Darren
Date: 11/01/2021

Create a new instance of "logger" in the client application
Set to your preferred logging level
And add the stream_handler from this module, if you want coloured output.

E.g.

logger_identifier = "my_app"
logger = dc.retrieve_console_logger(logger_identifier)
logger.setLevel(logging.INFO)
logger.info("Logger initialised.")
"""

import copy
import logging
from typing import ClassVar

from colorama import Fore

# Setup logging for dazbo-commons itself
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = None

class ColouredFormatter(logging.Formatter):
    """ Custom Formatter which adds colour to output, based on logging level """

    level_mapping: ClassVar[dict[str, tuple[str, str]]] = {
                     "DEBUG": (Fore.BLUE, "DBG"),
                     "INFO": (Fore.GREEN, "INF"),
                     "WARNING": (Fore.YELLOW, "WRN"),
                     "ERROR": (Fore.RED, "ERR"),
                     "CRITICAL": (Fore.MAGENTA, "CRT")
    }

    def __init__(self, *args, apply_colour=True, shorten_lvl=True, **kwargs) -> None:
        """ Args:
            apply_colour (bool, optional): Apply colouring to messages. Defaults to True.
            shorten_lvl (bool, optional): Shorten level names to 3 chars. Defaults to True.
        """
        super().__init__(*args, **kwargs)
        self._apply_colour = apply_colour
        self._shorten_lvl = shorten_lvl

    def format(self, record):
        if record.levelname in ColouredFormatter.level_mapping:
            new_rec = copy.copy(record)
            colour, new_level = ColouredFormatter.level_mapping[record.levelname]

            if self._shorten_lvl:
                new_rec.levelname = new_level

            if self._apply_colour:
                msg = colour + super().format(new_rec) + Fore.RESET
            else:
                msg = super().format(new_rec)

            return msg

        # If our logging message is not using one of these levels...
        return super().format(record)

# Add our ColouredFormatter as the default console logging
if not stream_handler:
    stream_handler = logging.StreamHandler()
    stream_fmt = ColouredFormatter(fmt='%(asctime)s.%(msecs)03d:%(name)s - %(levelname)s: %(message)s',
                                   datefmt='%H:%M:%S')
    stream_handler.setFormatter(stream_fmt)
    
if not logger.handlers:
    logger.addHandler(stream_handler)

def retrieve_console_logger(script_name):
    """ 
    Create and return a new logger, named after the script
    So, in your calling code, add a line like this:
    logger = ac.retrieve_console_logger(script_name)
    """
    a_logger = logging.getLogger(script_name)
    a_logger.addHandler(stream_handler) # type: ignore
    a_logger.propagate = False # Prevent the log messages from propagating to the root logger
    return a_logger
    
def top_and_tail(data, block_size=5, include_line_numbers=True, zero_indexed=False):
    """ Print a summary of a large amount of data 

    Args:
        data (_type_): The data to present in summary form.
        block_size (int, optional): How many rows to include in the top, and in the tail.
        include_line_numbers (bool, optional): Prefix with line number. Defaults to True.
        zero_indexed (bool, optional): Lines start at 0? Defaults to False.
    """
    if isinstance(data, list):
        # Get the number of digits of the last item for proper alignment
        num_digits_last_item = len(str(len(data)))

        # Format the string with line number
        def format_with_line_number(idx, line):
            start = 0 if zero_indexed else 1
            if include_line_numbers:
                return f"{idx + start:>{num_digits_last_item}}: {line}"
            else:
                return line

        # If there are less than 11 lines, just print them all
        if len(data) < 11:
            return "\n".join(format_with_line_number(i, line) for i, line in enumerate(data))
        else:
            top = [format_with_line_number(i, line) for i, line in enumerate(data[:block_size])]
            tail = [format_with_line_number(i, line) for i, line in enumerate(data[-block_size:], 
                            start=len(data)-block_size)]
            return "\n".join([*top, "...", *tail])
    else:
        return data

__all__ = ['ColouredFormatter', 'retrieve_console_logger', 'top_and_tail']
