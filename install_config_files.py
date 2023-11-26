from __future__ import print_function
import sys
from PYME import config
import os
import sys
from distutils.dir_util import copy_tree

# this seems needed so that we can actually see the copying messages from copy_tree
# see also: https://stackoverflow.com/questions/17712722/dir-util-copy-tree-wont-print-the-files-that-it-copies
import logging
logging.basicConfig(level=logging.INFO)

def stderrprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def update_config_file(rootdir,mode):
    initpath =  os.path.abspath(os.path.join(rootdir,'init_scripts'))
    logging_config_path = os.path.abspath(os.path.join(rootdir,'logging/pymeacquire-logging.yaml'))
    splitter_data_path = os.path.abspath(os.path.join(rootdir,'dyeRatios/dyeRatios.json'))
    
    from string import Template
    t = Template('''
adding the following lines to the "$mode" config.yaml file:

    PYMEAcquire-extra_init_dir: "$initpath"
    Acquire-logging_conf_file: "$logging_config_path"

''')
    print(t.substitute({ 'initpath': initpath,
                         'mode': mode,
                         'logging_config_path': logging_config_path}))

    config.update_config({'PYMEAcquire-extra_init_dir': initpath,
                          'SplitterRatioDatabase': splitter_data_path,
                          'Acquire-logging_conf_file': logging_config_path},
                         config=mode, create_backup=True)
#    for dir in config.config_dirs:
#        print(dir)
    
def main():
    this_dir = os.path.dirname(__file__)

    try:
        if sys.argv[1] == 'dist':
            installdir = config.dist_config_directory
            mode = 'dist'
        else:
            installdir = config.user_config_dir
            mode = 'user'
    except IndexError:  # no argument provided, default to user config directory
        installdir = config.user_config_dir
        mode = 'user'

    stderrprint("\nINSTALLING protocol and camera files\ninstalling files into %s...\n" % installdir)
    copy_tree(os.path.join(this_dir, 'etc', 'PYME'), installdir, verbose=1)
    update_config_file(this_dir,mode)

if __name__ == '__main__':
    main()
