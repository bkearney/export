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
import json
import time
from katello.swexport.config import Config
from katello.swexport.csv_reader import CSVReader
from collections import defaultdict
from okaara.cli import Command
import xmlrpclib


class ExportBaseCommand(Command):

    def __init__(self, name, description ):
        Command.__init__(self, name, description, self.export)

        self.create_option('--server', 'Satellite server to extract from', aliases=['-s'], required=False, default=Config.values.satellite.url)
        self.create_option('--username', 'Username to access the satellite ', aliases=['-u'], required=False, default=Config.values.satellite.username)
        self.create_option('--password', 'Password for the user', aliases=['-p'], required=False, default=Config.values.satellite.password)
        self.create_option('--directory', 'Where to store output files. If not provided, go to std out', aliases=['-d'], required=False, default=Config.values.export.directory)
        self.create_option('--format', 'Output format (csv or json)', aliases=['-f'], required=False, default=Config.values.export.outputformat)
        self.create_option('--org-mapping-file', 'file which provides a mpping between a satellite org id and an org name', \
            required=False, default=Config.values.mapping.orgs)

    def export(self, **kwargs):
        self.options = kwargs
        self.stats = defaultdict(int)
        self.errors = []
        self.notes = []

        start = time.clock()
        self.setup_org_mappings()
        self.pre_export()
        self.setup_output()

        try:
            self.client = xmlrpclib.Server(self.options['server'], verbose=0)
            self.key = self.client.auth.login(self.options['username'], self.options['password'])
        except Exception, e:
            self.add_error("Can not connect to to the Satellite Server")
            self.dump_stats()
            sys.exit(-1)

        data = self.get_data()
        headers = self.get_headers()
        self.post_export()
        self.add_stat("time (secs)", (time.clock()-start))

        self.dump_data(data, headers)
        self.dump_stats()

    def setup_org_mappings(self):
        self.translate_orgs = False
        self.org_mappings = {}
        if os.path.exists(self.options['org-mapping-file']):
            self.translate_orgs= True
            org_file = CSVReader(self.options['org-mapping-file'])
            for row in org_file:
                if len(row) == 3:
                    self.org_mappings[row['id']] = (row['name'],row['label'])
                else:
                    self.add_error("Skipping row in org mapping file: %s" % str(row))

    def pre_export(self):
        pass

    def post_export(self):
        pass

    def translate_org_label(self, org_id):
        new_org = org_id
        if self.translate_orgs:
            if str(org_id) in self.org_mappings.keys():
                new_org = self.org_mappings[str(org_id)][1]
            else:
                self.add_note("No Mapping for Org with id %s" % (org_id))
        return new_org

    def translate_org_name(self, org_id):
        new_org = org_id
        if self.translate_orgs:
            if str(org_id) in self.org_mappings.keys():
                new_org = self.org_mappings[str(org_id)][0]
            else:
                self.add_note("No Name Mapping for Org with id %s" % (org_id))
        return new_org

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
        if self.options['format'] == 'csv':
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
        else:
            json.dump(data_list, self.output_file)
            self.output_file.write("\n")

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

def is_true(item):
    return str(item) in ['T', 't', 'True', 'TRUE', 'true', '1', 'Y', \
        'y', 'YES', 'yes', 'on']

