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
    #see https://www.dicomlibrary.com/dicom/transfer-syntax/ and https://pydicom.github.io/pydicom/stable/old/image_data_handlers.html
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
        
    def getDS(self):
        return self.ds
    
    def setDS(self, p_ds):
        self.ds=p_ds
        
    def process(self):
        if self.format.lower()=="jpeg":
            self.set_bytes_jpeg(self.input_file)
        elif self.format.lower()=="tif":
            self.set_bytes_tiff(self.input_file)
    
    #separate step to allow editing from the GUI
    def getDicomDataSet(self):
        return self.ds
        
    
        
    def set_bytes_jpeg(self, p_file):
        self.internal_image = Image.open(p_file)
        self.internal_output = io.BytesIO()
        self.internal_image.save(self.internal_output, format= self.format.upper(), subsampling=self.subsampling, quality=self.jpeg_quality)            
        self.init_ds_jpeg(self.internal_image, self.jpeg_type,  self.jpeg_color_space)
        
    def set_bytes_tiff(self, p_file):
        self.internal_image = Image.open(p_file) 
        
        self.init_ds_tiff(self.internal_image)
    
    
        
    def save_dicom(self):    
        self.ds.save_as(self.target_file, write_like_original=False)
        print("done : "+self.target_file)
    
    
    def init_ds_tiff(self, p_img):
        
        self.init_ds_common(p_img)
        self.ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
        print(p_img.mode)
        
        #https://pillow.readthedocs.io/en/stable/handbook/concepts.html
        #https://pydicom.github.io/pydicom/dev/reference/generated/pydicom.pixel_data_handlers.convert_color_space.html
        color_space='RGB'
        if p_img.mode == '1':
            np_frame = numpy.array(p_img.getdata(), dtype=numpy.bool)
            self.ds.SamplesPerPixel = 1
        elif p_img.mode == 'L' or  p_img.mode == 'P' :
            np_frame = numpy.array(p_img.getdata(), dtype=numpy.uint8)
            self.ds.SamplesPerPixel = 1
        elif p_img.mode == 'RGBA' or p_img.mode == 'RGB' :
            np_frame = numpy.array(p_img.getdata(), dtype=numpy.uint8)
            #np_frame=pydicom.pixel_data_handlers.convert_color_space(np_frame,'RGB', "YBR_FULL_422", True)
            self.ds.SamplesPerPixel = 3
        elif p_img.mode == 'YCbCr '  :
            np_frame = numpy.array(p_img.getdata(), dtype=numpy.uint8)
            #np_frame=pydicom.pixel_data_handlers.convert_color_space(np_frame,'YBR_FULL_422', "RGB", True)
            color_space='YBR_FULL_422'
            self.ds.SamplesPerPixel = 3
        else:
            raise Exception("UNSUPPORTED COLOR SPACE :"+ p_img.mode )
        print(np_frame.shape)
        self.ds.PhotometricInterpretation = color_space
        '''
        if np_frame.shape[1] == 3:
            print("3")
            ds.SamplesPerPixel = 3
        else:
            ds.SamplesPerPixel = 1
        '''
        self.ds.BitsStored = 8
        self.ds.BitsAllocated = 8
        self.ds.HighBit = 7
        self.ds.PixelRepresentation = 0
        self.ds.PlanarConfiguration = 0
        self.ds.NumberOfFrames = 1
        self.ds.PixelData = np_frame
        self.ds.is_little_endian = True
        self.ds.is_implicit_VR = False
    
    def init_ds_jpeg(self, p_img, p_jpeg_mode, p_color_space):
        self.init_ds_common(p_img)
        self.ds.file_meta.TransferSyntaxUID = p_jpeg_mode        
        self.ds.SamplesPerPixel = 3
        self.ds.BitsStored = 8
        self.ds.BitsAllocated = 8
        self.ds.HighBit = 7
        self.ds.PixelRepresentation = 0
        self.ds.PlanarConfiguration = 0
        self.ds.NumberOfFrames = 1            
        self.ds.PixelData = encapsulate([self.internal_output.getvalue()])
         # Need to set this flag to indicate the Pixel Data is compressed
        self.ds['PixelData'].is_undefined_length = True  # Only needed for < v1.4        
        self.ds.PhotometricInterpretation = p_color_space
        self.ds.is_little_endian = True
        self.ds.is_implicit_VR = False
       
        
    
    def init_ds_common(self, p_img):
        self.ds = Dataset()
        self.ds.file_meta=Dataset()
        self.ds.Rows = p_img.height
        self.ds.Columns  = p_img.width
        self.ds.SOPClassUID = generate_uid()
        self.ds.SOPInstanceUID = generate_uid()
        self.ds.StudyInstanceUID = generate_uid()
        self.ds.SeriesInstanceUID = generate_uid()  