# Spec file template for package: cyberradiodriver-apps
#
# If using the makerpm script, use the following placeholders:
# * RPM_PKG_NAME: Name of the RPM package
# * RPM_PKG_VERSION: Version number of the RPM package
# * RPM_PKG_OS: Name of the OS that the RPM is built on
# * RPM_PKG_OS_VER: Version (major) of the OS
#
# Also, makerpm will build a source tarball with the version number in
# its name, so just use the %setup macro without arguments.
#
Summary: CRS NDR-series Radio Control Driver -- Applications
Name: RPM_PKG_NAME
Version: RPM_PKG_VERSION
Release: RPM_PKG_OSRPM_PKG_OS_VER
License: Proprietary
Group: Applications/Programming
Source: RPM_PKG_NAME-RPM_PKG_VERSION.tar.gz
URL: http://www.cyberradiosolutions.com
Vendor: CyberRadio Solutions, Inc.
Packager: CyberRadio Solutions, Inc. <sales@cyberradiosolutions.com>
%if "%{__python}" == "%{__python3}"
BuildRequires: python3
BuildRequires: doxygen
%else
BuildRequires: python
%endif

# Don't build a "debuginfo" package
%define debug_package %{nil}

%description
Applications using the NDR-series Radio Control Driver

%prep
# Use setup macro without arguments if using the makerpm script.
%setup

%build
# Uncomment the build steps necessary for the project you are building.
# -- Makefile project: Just the "%{__make}" step
# -- CMake project: Both the "%cmake" and "%{__make}" steps
# -- Autotools project: TBD
# -- Python project: None (the install step takes care of this)
#%cmake . -DPACKAGE_VERSION=RPM_PKG_VERSION
#%{__make} %{?_smp_mflags}

%install
# Uncomment the install steps necessary for the project you are building.
# -- Makefile project: The "make install" step
# -- CMake project: The "make install" step
# -- Autotools project: The "make install" step
# -- Python project: The "%{__python} setup.py install" step
# -- Projects with docs that are not installed via Makefile: The "mkdir" and "mv" steps
#make install DESTDIR=%{buildroot}
%{__python} setup.py install --root=%{buildroot}
#mkdir -p %{buildroot}/%{_docdir}/%{name}

%files
# Uncomment the entries necessary for the project you are building.
# -- Projects that generate system configuration files under /etc
#%{_sysconfdir}/*
# -- Projects that generate header files under /usr/include
#%{_includedir}/*
# -- Projects that generate executables under /usr/bin
%{_bindir}/*
# -- Projects that generate libraries under /usr/lib (/usr/lib64 on RedHat)
#%{_libdir}/*
# -- Projects that generate docs under /usr/share/docs
#%docdir %{_docdir}
#%{_docdir}/*
# -- Projects that generate Python libraries under /usr/lib/python[ver]
%{python_sitelib}/*
#%{python_sitearch}/*
# -- Projects that generate auxiliary files under /usr/share/<name>
#%{_datadir}/libtwistdaemon-doc/*
# -- Projects that generate app shortcuts under /usr/share/applications
#%{_datadir}/applications/*
# -- systemd service scripts
#/etc/systemd/system/*

%post
# Post-installation script

%preun
# Pre-uninstallation script
