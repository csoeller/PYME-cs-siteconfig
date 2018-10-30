from __future__ import print_function
import sys
from PYME import config
import os
import sys
from distutils.dir_util import copy_tree

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def print_config_instructions(rootdir):
    initpath =  os.path.abspath(os.path.join(rootdir,'init_scripts'))

    from string import Template
    t = Template('''
*IMPORTANT*: to register these init scripts add the following line to a config.yaml file:

    PYMEAcquire-extra_init_dir: $initpath

config.yaml files will be read from the following directories:

''')
    print(t.substitute({ 'initpath': initpath }))
    for dir in config.config_dirs:
        print(dir)
    
def main():
    this_dir = os.path.dirname(__file__)

    try:
        if sys.argv[1] == 'dist':
            installdir = config.dist_config_directory
    except IndexError:  # no argument provided, default to user config directory
        installdir = config.user_config_dir

    eprint("\nINSTALLING protocol files\n\tinstalling protocol files into %s..." % installdir)
    copy_tree(os.path.join(this_dir, 'etc', 'PYME'), installdir, verbose=1)

    print_config_instructions(this_dir)
if __name__ == '__main__':
    main()
