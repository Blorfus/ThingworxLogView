# Thingworx Log Viewer

Why use a precious web browser tab when you can use a command line?
This utility script is an alternative to the built in log viewer that comes with Thingworx. The goal was to provide a more real time and color-coded view of what is going on in a ThingWorx Server. At this time only the Application and Script logs are supported as they are the most important things IMHO.

Since this is written in Python you can run it just about anywhere that has python and a network connection to your Thingworx Instance. You will need an Application Key from ThingWorx and it should be tied to your username which should have sufficient permissions to view the log files. Typically Admin level is preferable.

When starting up the script will load the config.yaml file and then immediately query the configured server for the last 30 minutes of logs or 500 entries, whichever is lower. After that initial query it will run in an interval (20s by default) and query the logs since the last interval. Each time a query is completed the results will be printed out to the screen

## Installing prerequesites:

'pip install argparse'
'pip install pyyaml'

## Configuration:

The script looks for a config.yaml file in the same directory. The format allows for extra server information to be setup and accessed with a single moniker. See config.yaml.example.


## Running the Log viewer:

'python TWXLogView.py <LogType> <Server>'

<LogType> Can be 'application' OR 'script', if not specified the Script log will be the default
<Server> is the name of the server configuration to load from your config.yaml file. If not specified the script will attempt to load the settings in the 'default' section of your config.yaml file.
