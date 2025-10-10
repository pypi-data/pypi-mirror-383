""" 
Author: Darren
Date: 11/01/2022

Look for .env files, read variables from it,
and store as environment variables.

It looks for .env file in the current working directory where the script is being run from,
then checks up to three parent directories.

Then we check for env vars that have been loaded, e.g.

get_envs_from_file() # read env variables from a .env file, if we can find one
it not os.getenv('SOME_VAR'):
    os.environ['SOME_VAR'] = getpass('Enter your sensitive var: ')
"""
import logging

from dotenv import load_dotenv

logger = logging.getLogger("__name__")
logger.setLevel(logging.DEBUG)

def get_envs_from_file() -> bool:
    """ Look for .env files, read variables from it, and store as environment variables """
    # load_dotenv searches for .env in the current directory and its parents
    # It returns True if a .env file was found and loaded, False otherwise.
    loaded = load_dotenv(override=True, verbose=True)
    if loaded:
        logger.info(".env file found and loaded.")
    else:
        logger.warning("No .env file found.")
    return loaded
