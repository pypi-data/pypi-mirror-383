import h5py
from pathlib import Path
from ntsim.IO.Base.WriterBase import WriterBase

class H5Writer(WriterBase):
    arg_dict = {
        'h5_output_file': {'type': str, 'default': 'events', 'help': 'output file name'},
        'h5_output_dir': {'type': str, 'default': 'h5_output', 'help': 'output directory name'},
        'h5_save_event': {'type': str, 'nargs': '+', 
                         'choices': ['tracks','particles','photons','hits'],
                         'default': ['tracks','particles','photons','hits'],
                         'help': 'Event data to record'},
        'h5_save_header': {'type': str, 'nargs': '+',
                          'choices': ['geometry','metadata'],
                          'default': ['geometry','metadata'],
                          'help': 'Header information to record'}
    }
    def __init__(self, *args, file_path=None):
        self.file_path = file_path
        super().__init__()
        
    def __post_configure__(self):
        #create file path
        self.file_path = Path(self.h5_output_dir)/self.h5_output_file
        #add suffix, if it's missing
        self.file_path = self.file_path.with_suffix('.h5')
       
    def write_data(self, path: str, label: str, data):
        self.logger.debug("Writing path=%s label=%s, data=%s", path, label, type(data))
        group = self._file.require_group(path)
        group.create_dataset(label, data=data)
        #write the metadata
        # for key,value in data.metadata.items():
            # dataset.attrs[key] = value

    def open(self):
        #create the base directories
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = h5py.File(self.file_path, "w")
        self.logger.info("Opened file %s for writing", self.file_path)
        return self

    def close(self):
        self._file.close()
        self.logger.info("Closed file %s", self.file_path)