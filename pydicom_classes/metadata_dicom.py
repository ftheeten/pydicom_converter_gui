import pydicom

class MetadataDicom():
    
    dicom=None
    #ds=None
    
    def __init__(self, p_dicom):
        self.dicom=p_dicom
        
        
    def setMetadata(self):
        ds=self.dicom.getDS()
        #.....
        self.dicom.setDS(ds)
        
        
        pass