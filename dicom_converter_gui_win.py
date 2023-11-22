#https://pydicom.github.io/pydicom/dev/tutorials/pixel_data/compressing.html
#https://stackoverflow.com/questions/51667881/lossy-compression-of-numpy-array-image-uint8-in-memory
#https://tkinter-snippets.com/bytesio-get-length-of-binary-stream/
#https://stackoverflow.com/questions/58518357/how-to-create-jpeg-compressed-dicom-dataset-using-pydicom
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
from pydicom.encaps import encapsulate, encapsulate_extended
from pydicom.uid import JPEG2000Lossless, JPEGExtended
from pydicom.uid import RLELossless
import io

Image.MAX_IMAGE_PIXELS = None


app=None
window=None

def ensure_even(stream):
    # Very important for some viewers
    if len(stream) % 2:
        return stream + b"\x00"
    return stream
    
class BytesIOFR(io.BytesIO):
  
  def __len__(self):
    self.seek(0, io.SEEK_END)
    tmp=self.tell()
    print(tmp)
    return tmp
  
def convert_to_dicom(p_file):
    print("wait...")
    base = os.path.splitext(p_file)[0]
    target_name= base + ".dcm"
    
    img = Image.open(p_file)
    output =io.BytesIO()
    img.save(output, format='JPEG',quality=50)
    width, height = img.size
    if img.mode == 'RGBA' or img.mode == 'RGB':
        np_frame = numpy.array(img.getdata(), dtype=numpy.uint8)
        #np_frame=pydicom.pixel_data_handlers.convert_color_space(np_frame,'RGB', "YBR_FULL_422", True)
    else:
        np_frame=numpy.array(img.getdata(), dtype=numpy.uint8)
    
    ds = Dataset()
    ds.file_meta = Dataset()
    #ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
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
    #buffer = StringIO.StringIO()
    #im1.save(buffer, "JPEG", quality=10)
    #ds.PixelData = np_frame.tobytes()
    ds.file_meta.TransferSyntaxUID = JPEGExtended

    ds.PixelData=encapsulate([ensure_even(output.getvalue())])
    #ds.PixelData.is_undefined_length = True 
    
    ds.is_little_endian = True
    ds.is_implicit_VR = False    
    #GOOD
    #ds.compress(RLELossless)
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