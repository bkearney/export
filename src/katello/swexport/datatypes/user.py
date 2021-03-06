#!/usr/bin/python
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import random
import string
import os
from katello.swexport.base_command import ExportBaseCommand
from katello.swexport.csv_reader import CSVReader
from katello.swexport.config import Config

class User(ExportBaseCommand):

    def __init__(self):
        ExportBaseCommand.__init__(self, "users", "export users")

        self.create_option('--role-mapping-file', 'file which provides a mpping between a satellite role and a collection of katello roles', \
            aliases=['-r'], required=False, \
            default=Config.values.mapping.roles)

    def pre_export(self):
        self.translate_roles = False
        self.role_mappings = {}
        if os.path.exists(self.options['role-mapping-file']):
            self.translate_roles = True
            role_file = CSVReader(self.options['role-mapping-file'])
            for row in role_file:
                if len(row) == 2:
                    self.role_mappings [row['satellite_role']] = row['katello_role']
                else:
                    self.add_error("Skipping row in mapping file: %s" % str(row))

    def get_data(self):
        user_list = self.client.user.listUsers(self.key)
        data_list=[]
        for user in user_list:
            data = {}
            login = user.get('login')
            detail = self.client.user.getDetails(self.key, login)
            data['username']= login
            data['disabled']= not user.get('enabled')
            data['email']= detail.get('email')
            data['password'] = self.pass_generator()
            data['org_name']= self.translate_org_name(detail.get('org_id'))
            data['roles'] = self.clean_roles(self.client.user.listRoles(self.key, login), login)
            data_list.append(data)
            self.add_stat('users exported')
        return data_list

    def clean_roles(self, roles, login):
        new_roles = roles
        if self.translate_roles:
            new_roles = []
            for role in roles:
                if role in self.role_mappings.keys():
                    new_roles.append(self.role_mappings[role])
                else:
                    self.add_note("Removing role %s from user %s" % (role, login))

        return new_roles


    def pass_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))


    def get_headers(self):
        return ['username', 'disabled','email', 'password', 'org_name', 'roles']

    def output_filename(self):
        return "users"




