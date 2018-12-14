from __future__ import print_function, absolute_import, unicode_literals

import re
import sys
from prettytable import PrettyTable
from colorama import init, Fore, Back, Style
COLOR = False
CLI_COLOR_MAP = {
    "info": "white",
    "warning": "yellow",
    "error"  : "red"
}

COLOR_MATCHER = re.compile(r"(\w+)(\W+on\W+\w+)?")
init()
COLORS = {
    'none' : "",
    'default' : Style.RESET_ALL,
    'black'   : Fore.BLACK,
    'red'     : Fore.RED,
    'green'   : Fore.GREEN,
    'yellow'  : Fore.YELLOW,
    'blue'    : Fore.BLUE,
    'magenta' : Fore.MAGENTA,
    'cyan'    : Fore.CYAN,
    'white'   : Fore.WHITE,

    'on_black'   : Back.BLACK,
    'on_red'     : Back.RED,
    'on_green'   : Back.GREEN,
    'on_yellow'  : Back.YELLOW,
    'on_blue'    : Back.BLUE,
    'on_magenta' : Back.MAGENTA,
    'on_cyan'    : Back.CYAN,
    'on_white'   : Back.WHITE,
}
def colorstring_to_escapecode(color_string):
    match = re.match(COLOR_MATCHER, color_string)
    if match:
        return COLORS[match.group(1)] + \
            (COLORS[match.group(2).strip().replace(" ", "_")]
             if match.group(2) else "")
    else:
        return COLORS['default']

def print_string(msg, level=None):
    if not level:
        level = "info"
    string_color = CLI_COLOR_MAP.get(level)
    if string_color != "white":
        sys.stdout.write(colorstring_to_escapecode(string_color))
        sys.stdout.flush()
    sys.stdout.write("[embARC] {} \n".format(msg))
    if string_color != "white":
        sys.stdout.write(colorstring_to_escapecode('default'))
    sys.stdout.flush()

def print_table(msg, level=None):
    if not level:
        level = "info"
    if type(msg) is list:
        if len(msg) > 1:
            table_head = msg[0]
            table_content = msg[1]
            string_color = CLI_COLOR_MAP[level]
            sys.stdout.write(colorstring_to_escapecode(string_color))
            sys.stdout.flush()
            pretty_table = PrettyTable(table_head)
            pretty_table.align = "l"
            for content in table_content:
                if len(content) > 0:
                    pretty_table.add_row(content)
            print(pretty_table)
            sys.stdout.write(colorstring_to_escapecode('default'))
            sys.stdout.flush()


class TerminalNotifier():

    def __init__(self, color=True):
        self.event = self._get_event_template()
        self.color = color
        self.messages = []
        if self.color:
            init()
            self.COLORS = {
                'none' : "",
                'default' : Style.RESET_ALL,
                'black'   : Fore.BLACK,
                'red'     : Fore.RED,
                'green'   : Fore.GREEN,
                'yellow'  : Fore.YELLOW,
                'blue'    : Fore.BLUE,
                'magenta' : Fore.MAGENTA,
                'cyan'    : Fore.CYAN,
                'white'   : Fore.WHITE,

                'on_black'   : Back.BLACK,
                'on_red'     : Back.RED,
                'on_green'   : Back.GREEN,
                'on_yellow'  : Back.YELLOW,
                'on_blue'    : Back.BLUE,
                'on_magenta' : Back.MAGENTA,
                'on_cyan'    : Back.CYAN,
                'on_white'   : Back.WHITE,
            }

    def _get_event_template(self):
        event = {
            "type": "info",
            "format": "string",
            "message": ""
        }
        return event

    def collect_message(self, message):
        msg = "[embARC] %s\n" % message
        self.messages.append(msg)

    def notify(self, event):
        if event["format"] =="string":
            self.print_string(event)
            return True
        elif event["format"] =="table":
            self.print_table(event)
            return True
        else:
            msg = "Can not display this message"
            event = dict()
            event["message"] = msg
            event["type"] = "warning"
            event["format"] = "string"
            self.print_string(event)
            return False

    def print_string(self, event):
        msgtype = event.get("type", "info")
        current_color = self.COLORS[CLI_COLOR_MAP[msgtype]]
        print(current_color + "[embARC] {}".format(event["message"]), end="")
        print(self.COLORS['default'])
        sys.stdout.flush()
        self.event["type"] = "info"

    def print_table(self, event):
        if type(event["message"]) is list:
            if len(event["message"]) > 1:
                table_head = event["message"][0]
                table_content = event["message"][1]
                if event.get("type", None) in CLI_COLOR_MAP: #sys.stdout.isatty() and
                    sys.stdout.write(self.colorstring_to_escapecode(
                        CLI_COLOR_MAP[event["type"]]))
                    sys.stdout.flush()
                    pretty_table = PrettyTable(table_head)
                    pretty_table.align = "l"
                    for content in table_content:
                        if len(content) > 0:
                            pretty_table.add_row(content)
                    print(pretty_table)
                    sys.stdout.write(self.colorstring_to_escapecode('default'))
                    sys.stdout.flush()

        else:
            msg = "Can not display this message"
            event = dict()
            event["message"] = msg
            event["type"] = "warning"
            event["format"] = "string"
            self.print_string(event)
        self.event["format"] = "string"
        self.event["type"] = "info"

    COLOR_MATCHER = re.compile(r"(\w+)(\W+on\W+\w+)?")


    def colorstring_to_escapecode(self, color_string):
        match = re.match(self.COLOR_MATCHER, color_string)
        if match:
            return self.COLORS[match.group(1)] + \
                (self.COLORS[match.group(2).strip().replace(" ", "_")]
                 if match.group(2) else "")
        else:
            return self.COLORS['default']




