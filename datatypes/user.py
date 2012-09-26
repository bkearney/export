#!/usr/bin/python
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from base_command import ExportBaseCommand
import csv

class User(ExportBaseCommand):

    def __init__(self):
        ExportBaseCommand.__init__(self, "user", "export system groups")

        self.create_option('--role-mapping-file', 'file which provides a mpping between a satellite role and a collection of katello roles', aliases=['-r'], required=False)

    def pre_export(self):
        self.translate_roles = False
        self.role_mappings = {}
        if self.options['role-mapping-file']:
            self.translate_roles = True
            print csv.Sniffer().sniff(open(self.options['role-mapping-file'], 'rb').read()).quotechar
            role_file = csv.reader(open(self.options['role-mapping-file'], 'rb'), quotechar='"', skipinitialspace=True)
            for row in role_file:
                if len(row) == 2:
                    self.role_mappings [row[0]] = row[1]
                else:
                    self.add_error("Skipping row in mapping file: %s" % str(row))
            self.role_mappings

    def get_data(self):
        user_list = self.client.user.listUsers(self.key)
        data_list=[]
        for user in user_list:
            data = {}
            login = user.get('login')
            detail = self.client.user.getDetails(self.key, login)
            data['username']= login
            data['enabled']= user.get('enabled')
            data['email']= detail.get('email')
            data['password'] = ""
            data['org_id']= detail.get('org_id')
            data['roles'] = self.clean_roles(self.client.user.listRoles(self.key, login), login)
            data_list.append(data)
            self.add_stat('users exported')
        return data_list

    def clean_roles(self, roles, login):
        new_roles = []
        for role in roles:
            if role in self.role_mappings.keys():
                new_roles.append(self.role_mappings[role])
            else:
                self.add_note("Removing role %s from user %s" % (role, login))
        return new_roles


    def get_headers(self):
        return ['username', 'enabled','email', 'password', 'org_id', 'roles']

    def output_filename(self):
        return "user"




