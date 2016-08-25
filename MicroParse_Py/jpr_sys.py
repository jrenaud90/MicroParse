import os
from datetime import datetime
import time

## Constants, Lists, Dicts that are used in other fuctions and classes. ##

# String to Bool Conversions
str2bool = {'y': True, '1': True, 'yes': True,
            'n': False, '0': False, 'no': False}



class Log_Class():
    ''' Log class used to create, update, save program logs. 
        Version 1.2 JPR 7-24-15
    '''


    def __init__(self, log_directory, prog_name, **kwargs):
        ''' Construction of Log class. Ensures that directory exists, gets opening timestamp, opens file obj, writes opening lines. '''

        # Ensure that directory exists
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # Time stamp
        self.start_time = time.time()
        if kwargs.get('timestamp'):
            _ini_ts = '_' + datetime.fromtimestamp(Start_Time).strftime('%Y%m%d_%H%M%S')
        else:
            _ini_ts = ''
        self.path = os.path.join(log_directory, 'Log_' + prog_name + _ini_ts + '.log')
        
        # Other Parameters
        if kwargs.get('auto_line', True):
            self.eol = '\n'
        else:
            self.eol = ''
        self.ts_lines = kwargs.get('ts_lines', True)
        
        # Create File
        with open(self.path, 'w') as fobj:
            fobj.write('~~~log start~~~')
        
        # Write opening lines
        _header = kwargs.get('header', False)
        if _header:
            with open(self.path, 'w') as fobj:
                fobj.write(_header)

    def __call__(self, input):
        ''' Write an input line(s) to the log file. Implemented as a function call. '''
        if ts_lines:
            txt = str(time.time() - self.start_time) + ' :: ' + input + self.eol
        else:
            txt = input + self.eol
        with open(self.path, 'a') as fobj:
            fobj.write(txt)

    def __str__(self):
        ''' Return string representing log file '''
        return 'log_class instance located at ' + self.path + '.'


def _input(disp_txt, **kwargs):
    '''
    Implements a new version of python's input that always outputs lower case strings.
        * Can also output booleans with a kwargs call.
    '''

    # Get Input
    out = input(disp_txt)
    # Preform Operations
    if kwargs.get('strip', True):
        out = out.strip()
    if kwargs.get('lower', True):
        out = out.lower()
    if kwargs.get('bool', False):
        out = str2bool[out]
    return out