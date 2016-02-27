
from pacman.model.partitioned_graph.partitioned_vertex import PartitionedVertex
from pacman.model.resources.cpu_cycles_per_tick_resource import \
    CPUCyclesPerTickResource
from pacman.model.constraints.placer_constraints\
    .placer_chip_and_core_constraint import PlacerChipAndCoreConstraint
from pacman.model.resources.dtcm_resource import DTCMResource
from pacman.model.resources.resource_container import ResourceContainer
from pacman.model.resources.sdram_resource import SDRAMResource

from spynnaker_graph_front_end.abstract_partitioned_data_specable_vertex \
    import AbstractPartitionedDataSpecableVertex

from spinn_front_end_common.utilities import constants

from data_specification.data_specification_generator import \
    DataSpecificationGenerator

from enum import Enum

import logging

logger = logging.getLogger(__name__)

class BranchVertex(PartitionedVertex, AbstractPartitionedDataSpecableVertex):

    DATA_REGIONS = Enum(
        value="DATA_REGIONS",
        names=[('SYSTEM', 0),
               ('DATABASE', 1)])

    CORE_APP_IDENTIFIER = 0xBEEF

    def __init__(self, label, machine_time_step, time_scale_factor, placement,
                 constraints=None):

        x, y, p = placement

        resoruces = ResourceContainer(cpu=CPUCyclesPerTickResource(45),
                                      dtcm=DTCMResource(100),
                                      sdram=SDRAMResource(100))

        PartitionedVertex.__init__(
            self, label=label, resources_required=resoruces,
            constraints=constraints)
        AbstractPartitionedDataSpecableVertex.__init__(self)
        self._machine_time_step = machine_time_step
        self._time_scale_factor = time_scale_factor

        self._database_size = 7000000

        self.placement = None
        self.spec = None

        placement_constaint = PlacerChipAndCoreConstraint(x, y, p)
        self.add_constraint(placement_constaint)

    def get_binary_file_name(self):
        return "branch.aplx"

    def model_name(self):
        return "BranchVertex"

    def generate_data_spec(
            self, placement, sub_graph, routing_info, hostname, report_folder,
            ip_tags, reverse_ip_tags, write_text_specs,
            application_run_time_folder):
        """
        method to determine how to generate their data spec for a non neural
        application

        :param placement: the placement object for the dsg
        :param sub_graph: the partitioned graph object for this dsg
        :param routing_info: the routing info object for this dsg
        :param hostname: the machines hostname
        :param ip_tags: the collection of iptags generated by the tag allcoator
        :param reverse_ip_tags: the colelction of reverse iptags generated by
        the tag allcoator
        :param report_folder: the folder to write reports to
        :param write_text_specs: bool which says if test specs should be written
        :param application_run_time_folder: the folder where application files
         are written
        """
        self.placement = placement

        data_writer, report_writer = \
            self.get_data_spec_file_writers(
                placement.x, placement.y, placement.p, hostname, report_folder,
                write_text_specs, application_run_time_folder)

        spec = DataSpecificationGenerator(data_writer, report_writer)
        self.spec = spec

        # Setup words + 1 for flags + 1 for recording size
        setup_size = (constants.DATA_SPECABLE_BASIC_SETUP_INFO_N_WORDS + 3) * 4

        # Reserve SDRAM space for memory areas:

        # Create the data regions for hello world
        self._reserve_memory_regions(spec, setup_size)
        self._write_setup_info(spec, self.CORE_APP_IDENTIFIER,
                                     self.DATA_REGIONS.SYSTEM.value)

        # End-of-Spec:
        spec.end_specification()

        data_writer.close()

        return [data_writer.filename]

    def _reserve_memory_regions(self, spec, system_size):
        """
        *** Modified version of same routine in abstract_models.py These could
        be combined to form a common routine, perhaps by passing a list of
        entries. ***
        Reserve memory for the system, indices and spike data regions.
        The indices region will be copied to DTCM by the executable.
        :param spec:
        :param system_size:
        :return:
        """
        spec.reserve_memory_region(region=self.DATA_REGIONS.SYSTEM.value,
                                   size=system_size, label='systemInfo')
        spec.reserve_memory_region(region=self.DATA_REGIONS.DATABASE.value,
                                   size=self._database_size,
                                   label="inputs", empty=True)

    def _write_setup_info(self, spec, core_app_identifier, region_id):
        """
         Write this to the system region (to be picked up by the simulation):
        :param spec:
        :param core_app_identifier:
        :param region_id:
        :return:
        """
        self._write_basic_setup_info(spec, region_id)

    def append(self,data):
        self.spec.switch_write_focus(region=self.DATA_REGIONS.DATABASE.value)
        self.spec.write_value(data=data)

    def is_partitioned_data_specable(self):
        """
        helper method for isinstance
        :return:
        """
        return True