import pydicom
import numpy
import uuid
import os
import io


from windialog import *

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import pydicom.encoders.gdcm
import pydicom.encoders.pylibjpeg
from pydicom.encaps import encapsulate, encapsulate_extended
from pydicom.uid import JPEG2000Lossless, JPEGExtended
from PIL import Image


Image.MAX_IMAGE_PIXELS = None


app=None
window=None

def convert_to_dicom(p_file):
    base = os.path.splitext(p_file)[0]
    target_name= base + ".dcm"
    img = Image.open(p_file)
    output = io.BytesIO()
    img.save(output, format="JPEG")
    ds = Dataset()
    ds.file_meta=Dataset()
    
    
    ds.file_meta = Dataset()

    ds.Rows = img.height
    ds.Columns = img.width
    


    ds.SamplesPerPixel = 3
    
    
    ds.BitsStored = 8
    ds.BitsAllocated = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PlanarConfiguration = 0
    ds.NumberOfFrames = 1

    ds.SOPClassUID = generate_uid()
    ds.SOPInstanceUID = generate_uid()
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    
    ds.PixelData = encapsulate([output.getvalue()])
    # Need to set this flag to indicate the Pixel Data is compressed
    ds['PixelData'].is_undefined_length = True  # Only needed for < v1.4
    ds.PhotometricInterpretation = "YBR_FULL_422"
    
    ds.file_meta.TransferSyntaxUID = JPEGExtended
    
    ds.is_little_endian = True
    ds.is_implicit_VR = False  
    
    ds.save_as(target_name, write_like_original=False)
    print("conversion done...")


    

def start():
    filenames=getfile(multi = True)
    print(filenames)
    for f in filenames:
        print(f)
        convert_to_dicom(f)

if __name__ == '__main__':
    start()
