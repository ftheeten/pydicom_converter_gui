import pydicom
import numpy
import uuid
import os


from windialog import *

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import pydicom.encoders.gdcm
import pydicom.encoders.pylibjpeg
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


app=None
window=None

def convert_to_dicom(p_file):
    print("wait...")
    base = os.path.splitext(p_file)[0]
    target_name= base + ".dcm"
    
    img = Image.open(p_file)
    width, height = img.size
    if img.mode == 'RGBA' or img.mode == 'RGB':
        np_frame = numpy.array(img.getdata(), dtype=numpy.uint8)
        #np_frame=pydicom.pixel_data_handlers.convert_color_space(np_frame,'RGB', "YBR_FULL_422", True)
    else:
        np_frame=numpy.array(img.getdata(), dtype=numpy.uint8)
    
    ds = Dataset()
    ds.file_meta = Dataset()
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    ds.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.1.1'
    ds.file_meta.MediaStorageSOPInstanceUID = "1.2.3"
    ds.file_meta.ImplementationClassUID = "1.2.3.4"
    ds.Rows = img.height
    ds.Columns = img.width
    #ds.PhotometricInterpretation = "YBR_FULL_422"
    ds.PhotometricInterpretation = "RGB"
    if np_frame.shape[1] == 3:
        print("3")
        ds.SamplesPerPixel = 3
    else:
        ds.SamplesPerPixel = 1
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
    
    ds.PixelData = np_frame

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