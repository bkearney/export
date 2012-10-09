#!/usr/bin/python
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from base_command import ExportBaseCommand

class ActivationKey(ExportBaseCommand):

    def __init__(self):
        ExportBaseCommand.__init__(self, "activation_keys", "export activation keys")

        self.create_flag('--include-disabled', 'include disabled keys')

    def _add_data(self, key, data_list):
        data = {}
        data['name']= key.get('key')
        data['description']= key.get('description')
        data['usage_limit']= key.get('usage_limit')
        data['system_groups']= self._get_groups(key.get('server_group_ids'))
        data_list.append(data)
        self.add_stat('actitvation keys exported')


    def get_data(self):
        key_list = self.client.activationkey.listActivationKeys(self.key)
        data_list=[]
        for key in key_list:
            if (key.get('disabled')):
                if self.options['include-disabled']:
                    self._add_data(key, data_list)
                else:
                    self.add_stat('disabled actitvation keys skipped')
            else:
                self._add_data(key, data_list)

        return data_list

    def _get_groups(self, id_list):
        groups = []
        for group_id in id_list:
            groups.append(self.client.systemgroup.getDetails(self.key, group_id).get('name'))

        return groups

    def get_headers(self):
        return ['name', 'description','usage_limit', 'system_groups']

    def output_filename(self):
        return "activation_keys"




