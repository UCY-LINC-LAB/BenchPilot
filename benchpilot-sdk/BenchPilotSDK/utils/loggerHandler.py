import logging, os

class LoggerHandler:
    def __init__(self, name: str = 'BenchPilot'):
        # create logger
        self.logger = logging.getLogger(name)
        
        # assign debug mode if needed
        if "BENCHPILOT_DEBUG" in os.environ and '1' in os.environ["BENCHPILOT_DEBUG"]:
            self.logger.setLevel(logging.DEBUG)
            
        if not "LOGGER" in os.environ or '0' in os.environ["LOGGER"]:
            # create console handler and set level to debug
            ch = logging.StreamHandler()

            # add formatter to ch
            ch.setFormatter(CustomFormatter())

            # add ch to logger
            self.logger.addHandler(ch)
            os.environ["LOGGER"] = '1'
    
    @staticmethod
    def coloredPrint(msg: str = '', color_level: str = "default"):
        if "secondary" in color_level:
            print('\033[32m' + msg + '\033[0m')
        elif "blue" in color_level:
            print('\033[94m' + msg + '\033[0m')
        elif "green" in color_level:
            print('\033[92m' + msg + '\033[0m')
        elif "yellow" in color_level:
            print('\033[93m' + msg + '\033[0m')
        else:
            print('\033[96m' + msg + '\033[0m')


        

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    FORMATS = {
        logging.DEBUG: grey + '\n' + format + '\n' + reset,
        logging.INFO: grey + '\n' + format + '\n' + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)