#!/usr/bin/python
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import sys

from config import Config
from print_config import PrintConfig
from okaara.prompt import Prompt, COLOR_LIGHT_CYAN, COLOR_LIGHT_BLUE
from okaara.cli import Cli, Section, Command, Option, Flag
from datatypes import org, system_group, user, activation_key


class ExportCli(Cli):
    def __init__(self):
        Config()
        Cli.__init__(self)

        self.add_command(activation_key.ActivationKey())
        self.add_command(org.Org())
        self.add_command(PrintConfig())
        self.add_command(system_group.SystemGroup())
        self.add_command(user.User())


    def map(self):
        self.print_cli_map(section_color=COLOR_LIGHT_BLUE, command_color=COLOR_LIGHT_CYAN)


if __name__ == '__main__':
    sys.exit(ExportCli().run(sys.argv[1:]))
