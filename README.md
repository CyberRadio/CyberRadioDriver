# CyberRadio Driver

### Description

The CyberRadio Driver is a Python library that allows client applications 
to communicate with NDR-class radios.

On any system where the CyberRadio Driver package is installed, you can 
find the documentation at `/usr/share/doc/CyberRadioDriver/html`.

## Dependencies

- python[3]-serial
- python[3]-numpy
- python[3]-requests

### Building the Package
    
    # Setup in the local python2
    python setup.py install # install local
    # Setup system wide python2
    sudo -H python setup.py install #install system
    # Virtual Env
    python3 -m venv ./venv && source ./venv/bin/activate
    python setup.py install
    # System wide python3
    sudo -H python3 setup.py install
