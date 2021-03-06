#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#


include:
  - components.ha.iostack-ha.config.base
{% if salt["pillar.get"]('cluster:{0}:is_primary'.format(grains['id']), false) %}
  - components.ha.iostack-ha.config.post_install
  - components.ha.iostack-ha.config.config

start LDR-R1 HA cluster:
  cmd.run:
    - name: __slot__:salt:setup_conf.conf_cmd('/opt/seagate/cortx/iostack-ha/conf/setup.yaml', 'iostack-ha:init')

{% else %}
setup LDR-R1 HA config on non-primary node:
  test.show_notification:
    - text: "No changes needed on non-primary node."
{% endif %}
