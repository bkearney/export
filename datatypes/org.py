#!/usr/bin/python
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from base_command import ExportBaseCommand

class Org(ExportBaseCommand):

    def __init__(self):
        ExportBaseCommand.__init__(self, "orgs", "export orgs")

    def get_data(self):
        org_list = self.client.org.listOrgs(self.key)
        data_list=[]
        for org in org_list:
            data = {}
            data['name']= org.get('id')
            data['description']= org.get('name')
            data_list.append(data)
            self.add_stat('orgs exported')
        return data_list

    def get_headers(self):
        return ['name', 'description']

    def output_filename(self):
        return "org"




