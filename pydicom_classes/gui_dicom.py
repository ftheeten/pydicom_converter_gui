from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QButtonGroup, QRadioButton, QLineEdit, QLabel, QCheckBox, QMessageBox, QComboBox, QSizePolicy
from PySide6.QtCore import Qt
#own class
from process_dicom import ProcessDicom
from metadata_dicom import MetadataDicom
import os


class DicomGui(QApplication):
    MODE_FOLDER=False
    window=None
    combobox_mode=None
    but_input_files=None
    
    layout=None
    
    filenames=[]
    folders=[]
    output_dicom_file_folder=None
    folders_output=None
    
    def __init__(self):
        super(DicomGui, self).__init__([])
        self.window = QWidget()
        self.init_gui()
        self.window.show()
        self.exec()
        
    def init_gui(self):
        self.layout = QVBoxLayout()
        
        labelMode=QLabel("Input mode :")
        self.layout.addWidget(labelMode)
        
        self.combobox_mode = QComboBox()
        self.combobox_mode.addItems(['files', 'folder'])
        self.layout.addWidget(self.combobox_mode)
        self.combobox_mode.currentIndexChanged.connect(self.input_mode_changed)
        
        self.but_input_files= QPushButton('Input files')
        self.layout.addWidget(self.but_input_files)
        self.but_input_files.clicked.connect(self.choose_input)
        
        self.but_output_files= QPushButton('Choose output')
        self.layout.addWidget(self.but_output_files)
        self.but_output_files.clicked.connect(self.choose_output)
        
        self.but_process= QPushButton('Process DICOM conversion')
        self.layout.addWidget(self.but_process)
        self.but_process.clicked.connect(self.process_input)
        
        self.window.setLayout(self.layout)
        self.window.setFixedSize(self.window.sizeHint())
        self.window.setMinimumWidth(700)
        
    def input_mode_changed(self, index):
        if index==0:
            self.MODE_FOLDER=False
        elif index==1:
            self.MODE_FOLDER=True
        print(self.MODE_FOLDER)
        
    def choose_input(self, x):
        if not self.MODE_FOLDER:
            print("MODE_FILE")
            file_name = QFileDialog()
            filter = "TIFF (*.TIF);;TIFF (*.TIFF);;tiff (*.tiff);;JPG (*.jpg);;JPEG (*.JPEG);;PNG (*.PNG)"
            self.filenames, _ = file_name.getOpenFileNames(self.window, "Open files", "", filter)
            print("FILES\n"+"\n".join(self.filenames))
        else:
            print("MODE_FOLDER")
            file= QFileDialog.getExistingDirectory(self.window, "Choose folder to add")
            if len(file)>0:
                self.folders.append(file)
            print("FILES\n"+"\n".join(self.folders))
    
    def choose_output(self):
        folder_object = QFileDialog()
        self.output_dicom_file_folder =folder_object.getExistingDirectory(self.window, "Choose folder for Dicom")
       
                    
    def process_input(self):
        print(self.output_dicom_file_folder)
        if self.MODE_FOLDER:
            i=0
            for folder in self.folders:
               filenames_tmp = [self.folders[i]+"/"+f for f in os.listdir(self.folders[i]) if f.lower().endswith('.tif') or  f.lower().endswith('.tiff') or  f.lower().endswith('.jpg') or  f.lower().endswith('.jpeg') or  f.lower().endswith('.png')]
               self.filenames=self.filenames + filenames_tmp
               i=i+1
        for f in self.filenames:
            print(f)
            base_parser= os.path.basename(f)
            name_base = base_parser.split(".")
            print(name_base)
            if len(name_base)>0:
                name_base=name_base[0 :-1]
                print(name_base)
                dicom_name= '.'.join(name_base) + ".dcm"
                full_dicom=self.output_dicom_file_folder+"/"+dicom_name
                print(full_dicom)
                if f.lower().endswith('.jpg') or  f.lower().endswith('.jpeg'):
                    print("is_jpeg")
                    dicom=ProcessDicom(f, full_dicom, "jpeg", "JPEGExtended")
                    
                elif f.lower().endswith('.png'):
                    print("is_png")
                    dicom=ProcessDicom(f, full_dicom, "jpeg", "JPEGExtended")
                    
                elif f.lower().endswith('.tiff') or f.lower().endswith('.tif'):
                    print("is_tiff")
                    dicom=ProcessDicom(f, full_dicom, "tif")
                # dependency injection for metadata update
                metadata=MetadataDicom(dicom)
                metadata.setMetadata(p_patient_name=full_dicom)
                #saving
                dicom.save_dicom()    
                 
            
        
app=DicomGui()