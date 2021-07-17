from __future__ import print_function

__version__ = "1.2"

from meshroom.core import desc
import shutil
import glob
import os
import json

class NotificationSignal(desc.CommandLineNode):

    commandLine = '/mnt/software/signal-cli-0.8.4.1/bin/signal-cli send {phonenumberValue} -m {messageValue}'

    category = 'Utils'
    documentation = '''
Send a notification to Signal when this gets called.
'''

    inputs = [
        desc.File(
            name='trigger',
            label='Trigger',
            description='Trigger Input that causes notification to be sent',
            value=None,
            uid=[0],
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
            value="Step has completed {Step}",
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
