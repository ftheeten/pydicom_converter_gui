import pydicom
import numpy
import uuid
import os
import io

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import pydicom.encoders.gdcm
import pydicom.encoders.pylibjpeg
from pydicom.encaps import encapsulate, encapsulate_extended
from pydicom.uid import JPEG2000Lossless, JPEGExtended
from PIL import Image


class ProcessDicom():
    
    input_file=None
    output_folder=None
    target_file=None
    format=None
    jpeg_type=None
    ds=None
    internal_image=None
    internal_output=None
    subsampling=0
    jpeg_quality=None
    jpeg_color_space=None
    
    def __init__(self, p_file, p_target_file, p_format, p_jpeg_type="JPEGExtended", p_jpeg_quality=75, p_jpeg_color_space= "YBR_FULL_422"):
        self.input_file=p_file
        self.target_file=p_target_file
        self.format=p_format
        self.jpeg_type=p_jpeg_type
        if self.format.lower()=="jpeg":

            if self.jpeg_type.lower()=="jpegextended":
                self.jpeg_type=JPEGExtended
            elif self.jpeg_type.lower()=="jpeg2000lossless":
                self.jpeg_type=JPEG2000Lossless
            #default
            else:
                self.jpeg_type=JPEGExtended
            #avoid above 95 (PIL doc)
            self.jpeg_quality=p_jpeg_quality
            self.jpeg_color_space=p_jpeg_color_space
        self.process()
        
    def process(self):
        self.set_bytes_jpeg(self.input_file)
        
        
    
    #separate step to allow editing from the GUI
    def getDicomDataSet(self):
        return self.ds
        
    
        
    def set_bytes_jpeg(self, p_file):
        self.internal_image = Image.open(p_file)
        self.internal_output = io.BytesIO()
        self.internal_image.save(self.internal_output, format="JPEG", subsampling=self.subsampling, quality=self.jpeg_quality)            
        self.ds=self.init_ds_jpeg(self.internal_image, self.jpeg_type,  self.jpeg_color_space)
    
    def getDS(self):
        return self.ds
    
    def setDS(self, p_ds):
        self.ds=p_ds
        
    def save_dicom_jpeg(self):    
        self.ds.save_as(self.target_file, write_like_original=False)
    
    
    
    def init_ds_jpeg(self, p_img, p_jpeg_mode, p_color_space):
        ds = Dataset()
        ds.file_meta=Dataset()        
        ds.Rows = p_img.height
        ds.Columns  = p_img.width
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
        ds.PixelData = encapsulate([self.internal_output.getvalue()])
         # Need to set this flag to indicate the Pixel Data is compressed
        ds['PixelData'].is_undefined_length = True  # Only needed for < v1.4
        ds.file_meta.TransferSyntaxUID = p_jpeg_mode
        ds.PhotometricInterpretation = p_color_space
        ds.is_little_endian = True
        ds.is_implicit_VR = False
        return ds
    