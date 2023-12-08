import pydicom

class MetadataDicom():
    
    dicom=None
    #ds=None
    
    def __init__(self, p_dicom):
        self.dicom=p_dicom
        
        
    def setMetadata(self, p_patient_name=None):
        ds=self.dicom.getDS()
        if p_patient_name is not  None:
            ds.PatientName=p_patient_name
        self.dicom.setDS(ds)    