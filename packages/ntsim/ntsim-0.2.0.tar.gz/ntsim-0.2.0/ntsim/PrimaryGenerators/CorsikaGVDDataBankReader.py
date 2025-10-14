import struct, os, sys
# p.add('--corsika_GVD_DB_reader_full_records',default=False,help='Save records with all data (not only energies)')

class CorsikaGVDDataBankReader:
    header_enum = [
        'format_version',
        'corsika_package',
        'run_number',
        'number_of_events',
        'primary_kind',  # 14 = protons, 402 = He, 1608 = Oxygen, 5626 = Fe
        'slope_of_the_spectrum',
        'e_min',
        'e_max',
        'the_min',
        'the_max',
        'phi_min',
        'phi_max',
        'atm_kind',
        'obs_level',
        'a_magnet1',
        'a_magnet2',
        'hmodel',
        'e_cut_for_hadrons',
        'e_cut_for_muons',
        'e_cut_for_electrons',
        'e_cut_for_photons'
    ]

    event_record_enum = [
        'nrec_event',
        'nprim_part',
        'energy_of_primary_particle',
        'zprim_first',  # [m]
        'the_prim',  # [deg]
        'phi_prim',  # [deg]
        'Nmu'
    ]

    event_record_cycle_enum = [
        'x_mu',  # [m]
        'y_mu',  # [m]
        'theta_mu',  # [deg]
        'phi_mu',  # [deg]
        'time_mu',  # [s]
        'energy_mu',  # [GeV]
        None
    ]

    shift_record_enum = len(event_record_enum)*4
    shift_record_cycle_enum = len(event_record_cycle_enum)*4
    event_record_enum_Nmu_index = event_record_enum.index('Nmu')
    event_record_cycle_enum_energy_mu_index = event_record_cycle_enum.index('energy_mu')

    def __init__(self):
        self.module_type = 'generator'
        self.max_records = 0
        self.header_readed_n_bytes = 0
        self.readed_record_n_bytes = 0
        self.readed_records = 0
        self.input_file = None
        self.logger.info("initialized")


    def configure(self, opts):
        if opts.corsika_GVD_DB_reader_max_records:
            self.max_records = int(opts.corsika_GVD_DB_reader_max_records)
        # self.only_energies = not opts.corsika_GVD_DB_reader_full_records
        self.input = opts.corsika_GVD_DB_reader_input
        # open DataBank file for processing
        if os.path.exists(self.input):
            self.input_file = open(self.input, 'rb') # readonly binary file
        else:
            self.logger.warning(f"The file {self.input} is not found. Check the path. I am trying to ")
            self.logger.warning(f"search in ntsim distribution.")
            import importlib
            path = importlib.util.find_spec('ntsim').submodule_search_locations[0]
            if os.path.exists(path+'/data/'+self.input):
                self.input_file = open(path+'/data/'+self.input, 'rb')
                self.logger.warning(f"Well. The file {path+'/data/'+self.input} is found.")
                self.logger.warning(f"You should be more careful to provide the path.")
            else:
                # alas no idea where to search for it
                self.logger.error(f"No file '{self.input}'")
                sys.exit()
        self.file_size = os.path.getsize(os.path.realpath(self.input_file.name))
        self.__read_header()
        self.logger.info("configured")


    def __del__(self):
        if self.input_file:
            self.input_file.close()


    def __read_header(self):
        header = {}
        n_bytes_to_read = int((int.from_bytes(self.input_file.read(4), byteorder='little')))
        mis = self.input_file.read(4) # todo Check this
        bytes_to_read = self.input_file.read(n_bytes_to_read)
        for i, header_key in enumerate(self.header_enum):
            header[header_key] = struct.unpack(
                'f', bytes_to_read[i*4:i*4+4])[0]
        self.header_readed_n_bytes = 8+n_bytes_to_read
        self.header = header
        self.logger.debug('Readed {} bytes of header'.format(self.header_readed_n_bytes))
        self.logger.debug('Header: {}'.format(self.header))


    def __read_event_record(self):
        # FIXME for nrec_event=1 corrupted data or wrong parser
        if self.max_records:
            if self.readed_records >= self.max_records:
                self.logger.debug("Limit of records read reached")
                return None
        if (self.header_readed_n_bytes + self.readed_record_n_bytes) >= self.file_size:
            self.logger.warning("Readed all records")
            return None
        tmp = self.input_file.read(8)
        if tmp == b'':
            return None
        n_bytes_to_read = int((int.from_bytes(tmp[0:3], byteorder='little')))
        bytes_to_read = self.input_file.read(n_bytes_to_read)
        self.readed_record_n_bytes += 8 + n_bytes_to_read
        self.readed_records += 1
        return bytes_to_read

    def parse_event_record(self, bytes_to_read):
        if bytes_to_read is None:
            return None
        event_record = {'event': []}
        for i, record_key in enumerate(self.event_record_enum):
            event_record[record_key] = struct.unpack(
                'f', bytes_to_read[int(i*4):int(i*4+4)])[0]
        # if self.only_energies:
        #     event_record_cycle = {}
        #     i_2 = self.event_record_cycle_enum_energy_mu_index
        #     for i in range(int(event_record['Nmu'])):
        #         shift1 = self.shift_record_enum + i*self.shift_record_cycle_enum
        #         if (bytes_to_read[shift1 + i_2*4:shift1 + i_2*4+4]) == b'':
        #             self.logger.warning("Skipping corrupted record key at 'nrec_event': {}".format(event_record['nrec_event']))
        #             continue
        #         tmp = struct.unpack('f',
        #             bytes_to_read[shift1 + i_2*4:shift1 + i_2*4+4])[0]
        #         event_record_cycle[self.event_record_cycle_enum[
        #             self.event_record_cycle_enum_energy_mu_index]] = tmp
        #     event_record['event'].append(event_record_cycle)
        #     return event_record
        for i in range(int(event_record['Nmu'])):
            event_record_cycle = {}
            shift1 = self.shift_record_enum + i*self.shift_record_cycle_enum
            for i_2, record_cycle_key in enumerate(self.event_record_cycle_enum[:-1]):
                if (bytes_to_read[shift1 + i_2*4:shift1 + i_2*4+4]) == b'':
                    self.logger.warning("Skipping corrupted record key at 'nrec_event': {}".format(event_record['nrec_event']))
                    continue
                tmp = struct.unpack('f',
                    bytes_to_read[shift1 + i_2*4:shift1 + i_2*4+4])[0]
                event_record_cycle[record_cycle_key] = tmp
            event_record['event'].append(event_record_cycle)
        return event_record

    def next_record_bytes(self,n=1):
        if n == 1:
            return(self.__read_event_record())
        toReturn = []
        for i in range(n):
            toReturn.append(self.__read_event_record())
        return toReturn

    def next(self):
        if self.max_records:
            if self.readed_records >= self.max_records:
                self.logger.debug("Limit of records read reached")
                return None
        tmp = self.__read_event_record()
        if tmp == None:
            self.logger.warning("Record corrupted or all records readed")
            return None
        return self.parse_event_record(tmp)
