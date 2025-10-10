""" 
Test for colored_logging.py.
Author: Darren
"""
import logging
import unittest
from io import StringIO

import dazbo_commons as dc


class TestColoredLogging(unittest.TestCase):
    """ Tests that logging is emitted based on logging threshold, 
    and that it contains the right prefix text. """
    
    def setUp(self):
        """ Retrieve the console logger, and also setup a StringIO log stream,
        so we can inspect the logging output that has been transformed by the ColouredFormatter. """
        
        self.script_name = "Test Logging"
        
        # Redirect to an in-memory stream, rather than console, for testing
        # Set it to use the same formatting as the ColouredFormatter of our logger
        self.log_stream = StringIO() 
        self.stream_handler = logging.StreamHandler(self.log_stream)
        self.stream_handler.setFormatter(dc.ColouredFormatter(
                fmt='%(asctime)s.%(msecs)03d:%(name)s - %(levelname)s: %(message)s',
                datefmt='%H:%M:%S'))
        
        # typical console logger definition
        self.logger = dc.retrieve_console_logger(self.script_name)
        self.logger.addHandler(self.stream_handler)

    def tearDown(self):
        """ Clean up by removing the custom handler after tests. """
        self.logger.removeHandler(self.stream_handler)
          
    def test_logger_creation(self):
        self.assertIsNotNone(self.logger)
        self.assertEqual(self.logger.name, self.script_name)
        self.assertIn(self.stream_handler, self.logger.handlers)
        
    def test_write_log(self):
        """ Write log messages with different logging levels.
        Test whether logs are emitted, based on threshold level. """
        
        msg = "This is a test message" 
        
        # Short lvl name, logging method to call, logging level threshold
        levels = {"DBG": (self.logger.debug, logging.INFO), # should NOT appear
                  "INF": (self.logger.info, logging.INFO), # should appear
                  "WRN": (self.logger.warning, logging.INFO), # should appear
                  "ERR": (self.logger.error, logging.INFO)} # should appear
        
        for short_lvl, (log_call, lvl) in levels.items():
            self.logger.setLevel(lvl)
            log_call(msg)

            # Go back to the beginning of the stream to read its contents
            self.log_stream.seek(0)
            log_contents = self.log_stream.read()
        
            if short_lvl == "DBG":
                # Assert that the DBG message is not visible
                self.assertEqual('', log_contents)
            else:
                # Assert that the formatted message is in the log contents
                self.assertIn(f"{short_lvl}: This is a test message", log_contents)
        
if __name__ == '__main__':
    unittest.main()
