Thingworx Log Viewer

Why use a webbrowser when you can use a command line?

Installing prerequesites:

pip install argparse
pip install pyyaml

Configuration:

The script looks for a config.yaml file in the same directory. The format allows for extra server information to be setup and accessed with a single moniker. See config.yaml.example.


Running the Log viewer:

python TWXLogView.py <LogType> <Server>

<LogType> Can be 'application' OR 'script', if not specified the Application log will be the default
<Server> is the name of the server configuration to load from your config.yaml file. If not specified the script will attempt to load the settings in the 'default' section of your config.yaml file.
