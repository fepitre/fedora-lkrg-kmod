%if 0%{?fedora} || 0%{?rhel}
%global buildforkernels akmod
%global debug_package %{nil}
%endif

Name:           lkrg-kmod
Version:        0.9.1
Release:        1%{?dist}

Summary:        Kernel module for Linux Kernel Runtime Guard (LKRG)
License:        GPLv2
URL:            https://lkrg.org

Source0:        https://lkrg.org/download/lkrg-%{version}.tar.gz
Source1:        https://lkrg.org/download/lkrg-%{version}.tar.gz.sign
Source2:        lkrg-signing-key.asc

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  %{_bindir}/kmodtool
BuildRequires:  make
BuildRequires:  gnupg2

%global AkmodsBuildRequires xz time elfutils-libelf-devel gcc
BuildRequires:  %{AkmodsBuildRequires}

%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }


%description
LKRG performs runtime integrity checking of the Linux kernel and detection of
security vulnerability exploits against the kernel.

LKRG is a kernel module (not a kernel patch), so it can be built for and loaded
on top of a wide range of mainline and distros' kernels, without needing to
patch those.

That is only a dependency package to install the LKRG kernel module and also
some systemd service in order to help to manage loading/unloading the module at
system boot/shutdown.


%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'

# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T -a 0


for kernel_version in %{?kernel_versions} ; do
    cp -a lkrg-%{version} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    %make_build -C ${kernel_version##*___} M=${PWD}/_kmod_build_${kernel_version%%___*} V=1 modules
done


%install
rm -rf ${RPM_BUILD_ROOT}

for kernel_version in %{?kernel_versions}; do
    # upstream is providing only one kernel module
    install -D -m 755 _kmod_build_${kernel_version%%___*}/p_lkrg.ko  ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/p_lkrg.ko
done
%{?akmod_install}


%changelog
* Sat Dec 04 2021 Frédéric Pierret (fepitre) <frederic.pierret@qubes-os.org> - 0.9.1-1
- Initial RPM packaging.
