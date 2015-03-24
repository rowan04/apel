'''
   Copyright 2014 The Science and Technology Facilities Council

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   @author: Pavel Demin
'''


import logging

from apel.db.records.event import EventRecord
from apel.parsers import Parser


log = logging.getLogger(__name__)


class HTCondorParser(Parser):
    '''
    First implementation of the APEL parser for HTCondor
    '''
    def __init__(self, site, machine_name, mpi):
        Parser.__init__(self, site, machine_name, mpi)
        log.info('Site: %s; batch system: %s' % (self.site_name, self.machine_name))

    def parse(self, line):
        '''
        Parses single line from accounting log file.
        '''
        # condor_history -constraint "JobStartDate > 0" -format "%d|" ClusterId -format "%s|" Owner -format "%d|" RemoteWallClockTime -format "%d|" RemoteUserCpu -format "%d|" RemoteSysCpu -format "%d|" JobStartDate -format "%d|" EnteredCurrentStatus -format "%d|" ResidentSetSize_RAW -format "%d|" ImageSize_RAW -format "%d\n" RequestCpus
        # 1234567|opssgm|19|18|8|1412688273|1412708199|712944|2075028|1

        values = line.strip().split('|')

        mapping = {'Site'            : lambda x: self.site_name,
                   'MachineName'     : lambda x: self.machine_name,
                   'Infrastructure'  : lambda x: "APEL-CREAM-HTCONDOR",
                   'JobName'         : lambda x: x[0],
                   'LocalUserID'     : lambda x: x[1],
                   'LocalUserGroup'  : lambda x: x[10],
                   'WallDuration'    : lambda x: int(x[2]),
                   'CpuDuration'     : lambda x: int(x[3])+int(x[4]),
                   'StartTime'       : lambda x: x[5],
                   'StopTime'        : lambda x: x[6],
                   'MemoryReal'      : lambda x: int(x[7]),
                   'MemoryVirtual'   : lambda x: int(x[8]),
                   'Processors'      : lambda x: int(x[9]),
                   'NodeCount'       : lambda x: 0
                  }

        rc = {}

        for key in mapping:
            rc[key] = mapping[key](values)

        record = EventRecord()
        record.set_all(rc)
        return record
