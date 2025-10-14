import os
import logging
import struct
from numpy import pi

cor_logger = logging.getLogger(f'NTSim.read_corsika')

def process_corsika_file(full_path, desired_EAS=0):
    """ Function to read particles info from the given CORSIKA
    
    Each Corsika file is expected to have particles (e.g. muons, electrons) from several EAS'es, born by primary particle
	(e.g. proton, helium). After chosing file, EAS index should be given to let the generator know, from which particular EAS
	particles should be read

    Parameters
    ----------
    full_path: str 
       Path to Corsika file
	desired_EAS: int
	   Index of EAS to read particles from, set to 0 by default.

    """
    with open(full_path, 'rb') as infile:
        line_number = 0
        StartLine = 0
        Nsh = -1
        column = 1     
        count = 0

        begin_of_event_check = False
        end_code = False
    
        particle_data = {
                        'primary':{'Z_A_angles':[], 'energy':0},
                        'id':[],
                        'x':[], 'y':[],
                        'px':[], 'py':[], 'pz':[],
                        'time':[]
                        }
        colums_dict = {1: 'id', 2: 'px', 3: 'py', 4: 'pz', 5: 'x', 6: 'y', 7: 'time'}
        buffer_count_arr = []

        cor_logger.info("**Processing CORSIKA file %s **", full_path)
        
        while True:
            # Read 4 bytes (float)
            bytes_data = infile.read(4)
            if not bytes_data:
                break

            float_number = struct.unpack('f', bytes_data)[0]

            if float_number == 3.2134576383896705E-41:
                continue

            line_number += 1
            count += 1

            # Detect Event Header (EVTH)
            if float_number == 217433.078125 and not begin_of_event_check:
                Nsh += 1
                if (Nsh == desired_EAS):
                    count = 1
                    buffer_count_arr = []
                    column = 1
                    begin_of_event_check = True

                    StartLine = line_number + 273   #list of particles start 273 lines after event header
                continue
            
            if begin_of_event_check and (line_number < StartLine):
                buffer_count_arr.append(float_number)
                if count == 12:
                    energy = buffer_count_arr[2]                 # Reading the total energy
                    zenith = (180 / pi) * buffer_count_arr[9]   # Reading zenith angle
                    azimuth = (180 / pi) * buffer_count_arr[10]  # Reading azimuth angle
                    if azimuth < 0:
                        azimuth = 360 + azimuth
                    
                    particle_data['primary']['Z_A_angles'] += [zenith, azimuth]
                    particle_data['primary']['energy'] = energy

                continue
            
            # Detect Event End
            if (float_number == 3397.391845703125) and (line_number >= StartLine):
                if begin_of_event_check: 
                    break
                else:
                    continue

            # Read particle columns
            if begin_of_event_check and (line_number >= StartLine):
                if (line_number == StartLine) or (column > 7):
                    column = 1
                if (float_number == 0.0): 
                    break  
                particle_data[colums_dict[column]].append(float_number)

                column += 1

        cor_logger.info("Done processing %s ", full_path)
        infile.close()

        return particle_data

if __name__ == '__main__':
    # Example usage
    data = process_corsika_file('./DAT000001', desired_EAS = 1)
