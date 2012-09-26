#!/usr/bin/python
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import csv
import os
import sys
from collections import defaultdict
from okaara.cli import Command
from export_defaults import DEFAULT_SATELLITE_URL, DEFAULT_SATELLITE_LOGIN,\
    DEFAULT_SATELLITE_PASSWORD
import xmlrpclib


class ExportBaseCommand(Command):

    def __init__(self, name, description ):
        Command.__init__(self, name, description, self.export)

        self.create_option('--server', 'satellite server to extract from', aliases=['-s'], required=False, default=DEFAULT_SATELLITE_URL)
        self.create_option('--username', 'username to access the satellite ', aliases=['-u'], required=False, default=DEFAULT_SATELLITE_LOGIN)
        self.create_option('--password', 'password for the user', aliases=['-p'], required=False, default=DEFAULT_SATELLITE_PASSWORD)
        self.create_option('--directory', 'Where to store output files. If not provided, go to std out', aliases=['-d'], required=False)

    def export(self, **kwargs):
        self.options = kwargs
        self.stats = defaultdict(int)
        self.errors = []
        self.notes = []

        self.pre_export()
        self.client = xmlrpclib.Server(self.options['server'], verbose=0)
        self.key = self.client.auth.login(self.options['username'], self.options['password'])

        self.setup_output()

        data = self.get_data()
        headers = self.get_headers()
        self.post_export()

        self.dump_data(data, headers)
        self.dump_stats()

    def pre_export(self):
        pass

    def post_export(self):
        pass

    def setup_output(self):
        if self.options['directory']:
        # Create the output directory
            output_dir = self.options['directory']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.output_file = open(output_dir + "/" + self.output_filename(), 'w')
            self.stats_file = open(output_dir + "/" + self.output_filename() + "-stats", 'w')
        else:
            self.output_file = sys.stdout
            self.stats_file = sys.stdout


    def add_stat(self, stat_name, stat_count = 1):
        self.stats[stat_name] += 1

    def add_error(self, string):
        self.add_stat("errors")
        self.errors.append(string)

    def add_note(self, string):
        self.notes.append(string)

    def dump_data(self, data_list, keys):
        writer = csv.writer(self.output_file)
        writer.writerow(keys)
        for data in data_list:
            line_data = []
            for key in keys:
                value = data[key]
                if type(value) is list:
                    line_data.append(",".join(value))
                else:
                    line_data.append(value)
            writer.writerow(line_data)

    def dump_stats(self):
        self.stats_file.write("Stats\n")
        self.stats_file.write("-----\n")
        for stat in self.stats.keys():
            self.stats_file.write("%s -> %s\n" % (stat, self.stats[stat]))

        if len(self.errors) > 0:
            self.stats_file.write("\nErrors\n")
            self.stats_file.write("------\n")
            for err in self.errors:
                self.stats_file.write(err + "\n")

        if len(self.notes) > 0:
            self.stats_file.write("\nNotes\n")
            self.stats_file.write("-----\n")
            for note in self.notes:
                self.stats_file.write(note + "\n")
