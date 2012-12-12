from distutils.core import setup
import py2exe

options = {"py2exe":
                    {"compressed": 1,
                     "optimize": 2,
                     "bundle_files": 1}
           }
setup(
	version = "1.0.0",  
    options = options,
    zipfile=None,
    name = "DMCluster",
    description = "this is a py2exe test",   
    windows=[{"script":"auiframe.py", "icon_resources": [(1, "icon6.ico")]}]
	#data_files=[("txt",["Aggregation.txt"])]
    )