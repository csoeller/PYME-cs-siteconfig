import PYME.config as config
import os
import inspect

def main():
    scriptfile = inspect.getfile(inspect.currentframe())
    parentdir = parentDir = os.path.abspath(os.path.join(os.path.dirname(scriptfile),os.pardir))
    initpath = os.path.join(parentdir,'init_scripts')

    from string import Template
    t = Template('''
to register these init scripts add the following line to a config.yaml file:

PYMEAcquire-extra_init_dir: $initpath

config.yaml files will be read from the following directories:

''')
    print(t.substitute({ 'initpath': initpath }))
    for dir in config.config_dirs:
        print(dir)

if __name__ == "__main__":
    main()
