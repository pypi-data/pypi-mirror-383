from ntsim.Base.BaseFactory import BaseFactory
from ntsim.SensitiveDetectors.Base.BaseSensitiveDetector import BaseSensitiveDetector

class SensitiveDetectorFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.SensitiveDetectors', base_class=BaseSensitiveDetector)

    def configure(self, opts):
        super().configure(opts, 'sensitive_detector_name')
