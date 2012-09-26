#!/usr/bin/python
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from base_command import ExportBaseCommand

class SystemGroup(ExportBaseCommand):

    def __init__(self):
        ExportBaseCommand.__init__(self, "system_group", "export system groups")

    def get_data(self):
        group_list = self.client.systemgroup.listAllGroups(self.key)
        data_list=[]
        for group in group_list:
            data = {}
            data['id']= group.get('id')
            data['name']= group.get('name')
            data['description']= group.get('description')
            data['org_id']= group.get('org_id')
            data_list.append(data)
            self.add_stat('groups exported')
        return data_list

    def get_headers(self):
        return ['id', 'name','description', 'org_id']

    def output_filename(self):
        return "system_group"




