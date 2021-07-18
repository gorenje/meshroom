from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc

import os

class NotificationSignal(desc.CommandLineNode):

    commandLine = '{signalPathValue} send {phonenumberValue} -m {messageValue}'

    category = 'Utils'
    documentation = '''
Send a notification to Signal when the node is executed. It can be used multiple times in a pipeline to send updates on how the pipeline is progressing.

This requires the installation of the signal-cli from https://github.com/AsamK/signal-cli

signal-cli will also need to be linked to your account as new device.
'''

    inputs = [
        desc.File(
            name='trigger',
            label='Trigger',
            description='Trigger Input that causes notification to be sent',
            value="",
            uid=[0],
        ),
        desc.File(
            name="signalPath",
            label="Signal-cli Path",
            description="Path to signal-cli",
            value=os.environ.get('SIGNAL_CLI_PATH', "/mnt/software/signal-cli-0.8.4.1/bin/signal-cli"),
            uid=[],
            group=""
        ),
        desc.StringParam(
            name="phonenumber",
            label="Phonenumber",
            description="Phone to whom the message should be sent",
            value="",
            uid=[0],
        ),
        desc.StringParam(
            name="message",
            label="Message",
            description="Message to Send",
            value="Step has completed",
            uid=[0],
        ),
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='''verbosity level (critical, error, warning, info, debug).''',
            value='info',
            values=['critical', 'error', 'warning', 'info', 'debug'],
            exclusive=True,
            uid=[],
        ),
    ]
