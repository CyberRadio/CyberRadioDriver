#!/usr/bin/env python
###############################################################
# \file setup.py
#
# \brief Distutils setup script for cyberradiodriver-apps
#
# \author DA
#
# \copyright Copyright (c) 2019-2022 CyberRadio Solutions, Inc.  
#    All rights reserved.
#
# \note On RedHat-based systems, our "makerpm" script can build an
#    RPM package from the instructions here.  Alternatively, you can
#    execute this script as "python setup.py bdist_rpm" to use Python's
#    native RPM packaging capability. 
# \note On Debian-based systems, our "makedeb" script can build a
#    Debian installation package from the instructions here, if there 
#    is a "debian" subdirectory. 
# \note On Windows-based systems, you can execute this script as 
#    "python setup.py bdist_msi" to create an MSI installation package.
#    Alternatively, for Python projects that create an executable 
#    program, you can use py2exe to create a standalone executable.  
#    To do this, execute this script as "python setup.py py2exe".
#
###############################################################

from __future__ import print_function
from distutils.core import setup
from distutils.sysconfig import get_python_lib
import sys, os, glob
# Artifically make the libjsoncommand source directory the first
# entry in the module import path.  This allows us to peg this
# module's version to the current libjsoncommand version without
# them being co-located.
cyberradiodriverSourceDir = os.path.abspath(
        os.path.join(os.getcwd(), "..", "cyberradiodriver")
    )
sys.path.insert(0, cyberradiodriverSourceDir)
import CyberRadioDriver

# Configuration information for this application.  This should be consistent 
# across platforms, though there may be exceptions.
# VERSION: Version string for this application
VERSION=CyberRadioDriver.version
# NAME: Name of the application
NAME=CyberRadioDriver.name + "-apps"
# DESCRIPTION: Description of the application
DESCRIPTION=CyberRadioDriver.description + "-- Applications"
# AUTHOR: Author of the application
AUTHOR='CyberRadio Solutions, Inc.'
# EMAIL: E-mail address for the maintainer of the application
EMAIL='sales@cyberradiosolutions.com'
# MODULE_LIST: List of Python modules to install
MODULE_LIST=[]
# PACKAGE_LIST: List of Python packages to install
PACKAGE_LIST=[]
# SCRIPT_LIST: List of script files to install
SCRIPT_LIST=['ndr_dataport_config']
# CONF_FILE_LIST: List of configuration files to install 
CONF_FILE_LIST=[]
# INIT_SCRIPT_LIST: List of system initialization scripts to install.
# If a script has the extension ".init", the extension is stripped
# upon installation. 
INIT_SCRIPT_LIST=[]
# DOXY_FILE_LIST: List of Doxygen files to process for automatic 
# generation of documentation.
DOXY_FILE_LIST=[]
# EXTERNALS_INFO: Describes external C/C++ programs that need to be 
# built and installed as part of the installation procedure.
# 
# This is a nested dictionary.  The keys are executable names, 
# and the values are dictionaries with the following key-value pairs:
# * "sources": List of source files
# * "include_dirs": List of include file directories
# * "library_dirs": List of link library directories
# * "libraries": List of libraries to link against (each minus any 
#   "lib" prefix)
# * "compiler_options": List of extra options to add to the compiler
#   command line 
# * "linker_options": List of extra options to add to the linker
#   command line 
EXTERNALS_INFO={}
# PACKAGE_DIR_LIST: Package directory information dictionary.  This is
# a dictionary where the keys are package names and the values are 
# relative directory names where the package files are found.
PACKAGE_DIR_LIST={}
# PACKAGE_DATA_LIST: Package data information dictionary.  This is
# a dictionary where the keys are package names and the values are 
# lists of file specifications indicating which files should be 
# installed as package data.
PACKAGE_DATA_LIST={}
# DATA_FILE_LIST: Data file information.  This is a list of 2-tuples:
# (install directory, list of data files).
DATA_FILE_LIST=[]
# DOC_PROJECT_NAME: If DOXY_FILE_LIST has Doxyfile entries in it, 
# then this specifies what the project name should be in the 
# generated docs.  The default is to use the name of the package;
# set DOC_PROJECT_NAME to None to use the default. 
DOC_PROJECT_NAME=None
# DOC_INSTALL_DIR: If DOXY_FILE_LIST has Doxyfile entries in it, then 
# this specifies which directory to install the doc files in.
DOC_INSTALL_DIR=None
# DOC_FILE_DIR: If DOXY_FILE_LIST has Doxyfile entries in it, then 
# this is a directory containing the doc files.
DOC_FILE_DIR=None
# The following parameters have meaning only under Windows
README_LIST=[]
WINDOWS_ZIPPKG_LIST=[]
WINDOWS_WXPYTHON_SUPPORT=False
WINDOWS_PYWIN32_SUPPORT=False
WINDOWS_MATPLOTLIB_SUPPORT=False
# -- WINDOWS_UPGRADE_CODE: This is the string representation of a Windows
#    GUID (that is, a Python UUID surrounded by braces).  An upgrade code 
#    allows MSI installers to detect if there is a previous version 
#    installed and uninstall it automatically.  If this is None, the MSI 
#    installer will not do upgrade tracking (not recommended).
WINDOWS_UPGRADE_CODE="{39f75c95-3e8b-4994-95d4-c19f5870bcd5}"

# Package building code (platform-dependent)
if sys.platform == 'win32':
    # Under Win32, we can use the py2exe package to create a Windows executable from the
    # Python code.  To do this, specify "py2exe" as an argument to the script.
    windowsOpts = {}
    if "py2exe" in sys.argv:
        windowsOpts = {'py2exe': {'bundle_files': 1, \
                                 "dll_excludes": ["mswsock.dll", "MSWSOCK.dll"], \
                              }}
        if WINDOWS_WXPYTHON_SUPPORT:
            sys.path.append("C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT")
            DATA_FILE_LIST += [("Microsoft.VC90.CRT", glob.glob(r'C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
        if WINDOWS_PYWIN32_SUPPORT:
            pywin32path = os.path.join(get_python_lib(), "pythonwin")
            sys.path.append(pywin32path)
            DATA_FILE_LIST += [("Microsoft.VC90.MFC", glob.glob(os.path.join(pywin32path, "*.dll")))]
            DATA_FILE_LIST += [("Microsoft.VC90.MFC", glob.glob(os.path.join(pywin32path, "*.manifest")))]
        if WINDOWS_MATPLOTLIB_SUPPORT:
            from distutils.filelist import findall
            import matplotlib
            matplotlibdatadir = matplotlib.get_data_path()
            matplotlibdata = findall(matplotlibdatadir)
            for f in matplotlibdata:
                dirname = os.path.join('matplotlibdata', f[len(matplotlibdatadir)+1:])
                DATA_FILE_LIST.append((os.path.split(dirname)[0], [f]))
            windowsOpts['py2exe']['packages'] = ['matplotlib', 'numpy', 'pytz']
            #windowsOpts['py2exe']['includes'] = 'matplotlib.numerix.random_array'
            windowsOpts['py2exe']['excludes'] = ['_gtkagg', '_tkagg']
            windowsOpts['py2exe']['dll_excludes'].extend(['libgdk-win32-2.0-0.dll', \
                                                         'libgdk_pixbuf-2.0-0.dll', \
                                                         'libgobject-2.0-0.dll'])
        try:
            import py2exe
        except:
            raise RuntimeError("Cannot build executable using py2exe because the package is not installed")
    elif "bdist_msi" in sys.argv:
        windowsOpts = {'bdist_msi': {}}
        if WINDOWS_UPGRADE_CODE is not None:
            windowsOpts['bdist_msi']['upgrade_code'] = str(WINDOWS_UPGRADE_CODE).upper()
    setup(name=NAME, \
          version=VERSION, \
          description=DESCRIPTION, \
          author=AUTHOR, \
          author_email=EMAIL, \
          py_modules=MODULE_LIST, \
          packages=PACKAGE_LIST, \
          scripts=SCRIPT_LIST, \
          console=SCRIPT_LIST, \
          package_dir=PACKAGE_DIR_LIST, \
          package_data=PACKAGE_DATA_LIST, \
          data_files=DATA_FILE_LIST, \
          options=windowsOpts, \
          zipfile=None, \
         )
    # Automatically package the results as a version-tagged ZIP archive, if desired
    if len(WINDOWS_ZIPPKG_LIST) > 0:
        import zipfile, os, shutil
        ziptarget = os.path.join("dist", "%s-%s.zip" % (name, version))
        print("Packaging archive:", ziptarget)
        for fname in README_LIST:
            shutil.copy(fname, os.path.join("dist", fname))
        zfs = zipfile.ZipFile(ziptarget, "w", zipfile.ZIP_DEFLATED)
        for fname in WINDOWS_ZIPPKG_LIST:
            zfs.write(os.path.join("dist", fname), fname)
        zfs.close()
else:
    # Linux
    # Custom classes that handle "python setup.py install" command for us
    # -- Installs configuration files to /etc or ${prefix}/etc, depending
    #    on the "prefix" setting
    # -- Installs init scripts to /etc/init.d
    # -- Automatically generates documentation using Doxygen if Doxygen 
    #    configuration files are provided
    # -- Builds and installs example programs as described in the example
    #    information dictionary
    import distutils.dist
    import distutils.command.build_scripts
    import distutils.command.install
    import distutils.ccompiler
    import distutils.log
    
    class LinuxDistribution(distutils.dist.Distribution):
        
        # OVERRIDE
        # -- Exposes "conf_files", "init_files", "doxy_files", "externals_info",
        #    "doc_project_name", "doc_install_dir", and "doc_file_dir"
        def __init__ (self, attrs=None):
            self.conf_files = None
            self.init_files = None
            self.doxy_files = None
            self.externals_info = None
            self.doc_project_name = None
            self.doc_install_dir = None
            self.doc_file_dir = None
            distutils.dist.Distribution.__init__(self, attrs)
                        
            
    class LinuxBuildScripts(distutils.command.build_scripts.build_scripts):

        # OVERRIDE
        def initialize_options(self):
            distutils.command.build_scripts.build_scripts.initialize_options(self)
            self.externals_info = self.distribution.externals_info
            
        # OVERRIDE
        def finalize_options(self):
            distutils.command.build_scripts.build_scripts.finalize_options(self)
            
        # OVERRIDE
        def run (self):
            # Compile and link external executables, adding them to the list
            # of scripts.
            if self.externals_info != {}:
                comp = distutils.ccompiler.new_compiler()
                for external_name in self.externals_info:
                    external_info = self.externals_info[external_name]
                    external_srcs = external_info.get("sources", [])
                    external_incdirs = external_info.get("include_dirs", [])
                    external_libdirs = external_info.get("library_dirs", [])
                    external_libs = external_info.get("libraries", [])
                    external_compopts = external_info.get("compiler_options", [])
                    external_linkopts = external_info.get("linker_options", [])
                    distutils.log.info("building external program %s", external_name)
                    external_objs = comp.compile(sources=external_srcs, 
                                                include_dirs=external_incdirs,
                                                extra_preargs=external_compopts)
                    comp.link_executable(objects=external_objs, 
                                         output_progname=external_name, 
                                         libraries=external_libs,
                                         library_dirs=external_libdirs,
                                         extra_preargs=external_linkopts)
                    self.scripts.append(external_name)
            # Execute base-class version to handle all "scripts"
            distutils.command.build_scripts.build_scripts.run(self)
    
    
    class LinuxInstall(distutils.command.install.install):
        
        # OVERRIDE
        def initialize_options(self):
            distutils.command.install.install.initialize_options(self)
            self.conf_prefix = ''
            self.init_prefix = '/etc/init.d'

        # OVERRIDE
        def finalize_options(self):
            distutils.command.install.install.finalize_options(self)
            if self.prefix == '/usr':
                self.conf_prefix = '/etc'
            else:
                self.conf_prefix = os.path.join(self.prefix, 'etc')
            
        # EXTENSION
        def ensurePathToFileExists(self, filename):
            dirname = os.path.dirname(os.path.normpath(filename))
            if not os.access(dirname, os.F_OK):
                self.distribution.announce("creating %s" % dirname)
                os.makedirs(dirname)
            
        # EXTENSION
        def executeDoxygen(self, doxy_file):
            # (1) Update the configuration file with the correct application name
            #     and version number
            self.distribution.announce("updating Doxygen file %s with name and version" % doxy_file)
            ifs = open(doxy_file, "r")
            lines = ifs.readlines()
            ifs.close()
            docProjectName = self.distribution.get_name()
            if self.distribution.doc_project_name is not None:
                docProjectName = self.distribution.doc_project_name
            for i in range(0, len(lines), 1):
                if "PROJECT_name = " in lines[i]:
                    lines[i] = "PROJECT_name = " + docProjectName + "\n"
                if "PROJECT_NUMBER = " in lines[i]:
                    lines[i] = "PROJECT_NUMBER = " + self.distribution.get_version() + "\n"
            ofs = open(doxy_file, "w")
            ofs.writelines(lines)
            ofs.close()
            # (2) Execute Doxygen to generate the docs.
            self.distribution.announce("executing Doxygen on file %s" % doxy_file)
            self.spawn(["doxygen", doxy_file])
            # (3) Add the generated docs files to the distribution's data files list
            if self.distribution.data_files is None:
                self.distribution.data_files = []
            # -- Generate a data file map.  The keys of the map are relative
            #    path names (relative to the doc file directory), and the values
            #    are lists of files (unpathed).
            dfMap = dict(
                    [
                        (
                            os.path.relpath(q[0], self.distribution.doc_file_dir), 
                            q[2]
                        ) for q in os.walk(self.distribution.doc_file_dir) \
                        if len(q[2]) > 0
                    ]
                )
            # -- Generate the data file tuples for each directory in the data
            #    file map.  Note that we need to add paths back in, so we use
            #    normpath() to eliminate any path weirdness.
            for dfDir in dfMap:
                self.distribution.data_files.append(
                        (
                            os.path.normpath(
                                    os.path.join(self.distribution.doc_install_dir, 
                                    dfDir)
                                ), 
                            [
                                os.path.normpath(
                                        os.path.join(self.distribution.doc_file_dir, 
                                        dfDir, q)
                                    ) for q in dfMap[dfDir]
                            ]
                        )
                    )
        
        # OVERRIDE
        def run(self):
            # Execute Doxygen if we have doxyfiles to process
            # (do this first because it modifies the data file
            # list)
            for doxy_file in self.distribution.doxy_files:
                if os.access(doxy_file, os.F_OK):
                    # Execute Doxygen
                    self.executeDoxygen(doxy_file)
            # Run base-class installation procedure
            distutils.command.install.install.run(self)
            # Install configuration files
            for conf_file in self.distribution.conf_files:
                if os.access(conf_file, os.F_OK):
                    # os.path.join() drops the root path if the conf_prefix contains
                    # a leading slash
                    dstComponents = []
                    dstComponents.append("/" if self.root is None \
                                         else self.root)
                    dstComponents.append(self.conf_prefix[1:] if \
                                         self.conf_prefix.startswith("/") \
                                         else self.conf_prefix)
                    dstComponents.append(os.path.basename(conf_file))
                    dst = os.path.join(*dstComponents)
                    self.ensurePathToFileExists(dst)
                    self.copy_file(conf_file, dst)
            # Install init scripts
            for init_file in self.distribution.init_files:
                if os.access(init_file, os.F_OK):
                    # If init file name ends with ".init", then strip this 
                    # ending off of the filename
                    tmp = init_file.replace(".init", "")
                    # os.path.join() drops the root path if the init_prefix contains
                    # a leading slash
                    dstComponents = []
                    dstComponents.append("/" if self.root is None \
                                         else self.root)
                    dstComponents.append(self.init_prefix[1:] if \
                                         self.init_prefix.startswith("/") \
                                         else self.init_prefix)
                    dstComponents.append(os.path.basename(tmp))
                    dst = os.path.join(*dstComponents)
                    self.ensurePathToFileExists(dst)
                    self.copy_file(init_file, dst)
                    # Make the destination file executable
                    self.distribution.announce("changing mode of %s to 755" % dst)
                    os.chmod(dst, 0o755)
        
    # Under Linux, use the script argument to determine how to package it (tarball 
    # using "bdist_dumb" or RPM using "bdist_rpm").  Debian (Ubuntu) machines can
    # leverage setup.py to produce DEB installers using native packaging tools.
    setup(
            distclass = LinuxDistribution, \
            cmdclass = {
                    'build_scripts': LinuxBuildScripts,
                    'install': LinuxInstall,
                },
            name=NAME,
            version=VERSION,
            description=DESCRIPTION,
            author=AUTHOR,
            author_email=EMAIL,
            py_modules=MODULE_LIST,
            packages=PACKAGE_LIST,
            scripts=SCRIPT_LIST,
            package_dir=PACKAGE_DIR_LIST,
            package_data=PACKAGE_DATA_LIST,
            data_files=DATA_FILE_LIST,
            conf_files=CONF_FILE_LIST,
            init_files=INIT_SCRIPT_LIST,
            doxy_files=DOXY_FILE_LIST,
            externals_info=EXTERNALS_INFO,
            doc_project_name=DOC_PROJECT_NAME,
            doc_install_dir=DOC_INSTALL_DIR,
            doc_file_dir=DOC_FILE_DIR,
        )
    

