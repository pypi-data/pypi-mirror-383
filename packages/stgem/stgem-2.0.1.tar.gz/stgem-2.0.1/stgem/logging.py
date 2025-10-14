"""
Log messages
Multiprocessing does not support Python's logging module as concurrent
handling of log file writes is complex. Thus, we need our own logger. We use
a very simple approach without continuous logging to files.
"""

import inspect

import alive_progress

NOTSET = 0
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

level = INFO


def basicConfig(new_level):
    global level
    level = new_level


def debug(msg):
    if level > DEBUG:
        return
    stack = inspect.stack()
    if len(stack) >= 1:
        parent_frame = stack[1][0]
        module_name = inspect.getmodule(parent_frame).__name__
    else:
        module_name = ""
    print(f"{module_name}: {msg}")


def info(msg):
    if level > INFO:
        return
    print(msg)


def info_bar(*args, **kwargs):
    if level > INFO:
        # Return a dummy context manager when logging level is above INFO
        class DummyBar:
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
            
            def __call__(self, *args, **kwargs):
                # Allow calling the bar object (for incrementing)
                pass
            
            def __setattr__(self, name, value):
                # Allow setting attributes like bar.text = "something"
                pass
                
        return DummyBar()
    
    return alive_progress.alive_bar(*args, **kwargs)
