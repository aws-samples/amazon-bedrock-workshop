import textwrap
from io import StringIO
import sys

def print_ww(*args, **kwargs):
    buffer = StringIO()
    try: 
        _stdout = sys.stdout
        sys.stdout = buffer
        width = 100
        if 'width' in kwargs:
            width = kwargs['width']
            del kwargs['width']
        print(*args, **kwargs)
        output = buffer.getvalue()    
    finally:
        sys.stdout = _stdout
    for line in output.splitlines():
        print("\n".join(textwrap.wrap(line, width=width)))


        
    
