#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
#
%define rel	1
Summary:	Capability Override LSM
Summary(pl.UTF-8):	Moduł LSM Capability Override
Name:		CapOver
Version:	0.9.3
Release:	%{rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://files.randombit.net/cap_over/%{name}-%{version}.tgz
# Source0-md5:	971e50c1abaa97ee4a9958e92dd88300
URL:		http://www.randombit.net/projects/cap_over/
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.0}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Capability Override LSM, is a kernel module which gives the
ability to specify that certain users/groups/programs are to gain
access to one or more extra capabilities. This means this LSM is a
permissive module, rather than a restrictive one (which is more
typical of LSMs).

%description -l pl.UTF-8
Capability Override LSM to moduł jądra dający możliwość określenia
pewnych użytkowników/grup/programów mogących mieć dostęp do jednego
lub większej liczby uprawnień (capabilities). Oznacza to, że ten LSM
jest modułem zezwalającym, a nie restrykcyjnym (co jest bardziej
typowe dla LSM).

%package -n kernel%{_alt_kernel}-misc-cap_over
Summary:	cap_over kernel module
Summary(pl.UTF-8):	Moduł jądra cap_over
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires:	CapOver

%description -n kernel%{_alt_kernel}-misc-cap_over
cap_over kernel module.

%description -n kernel%{_alt_kernel}-misc-cap_over -l pl.UTF-8
Moduł jądra cap_over.

%package -n kernel%{_alt_kernel}-smp-misc-cap_over
Summary:	cap_over SMP kernel module
Summary(pl.UTF-8):	Moduł SMP jądra cap_over
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Requires:	CapOver

%description -n kernel%{_alt_kernel}-smp-misc-cap_over
cap_over SMP kernel module.

%description -n kernel%{_alt_kernel}-smp-misc-cap_over -l pl.UTF-8
Moduł SMP jądra cap_over.

%prep
%setup -q

%build
%if %{with kernel}
%configure \
	--with-linux="%{_kernelsrcdir}"

for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-${cfg}.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	mv cap_over{,-$cfg}.ko
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
install cap_over-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/cap_over.ko
%if %{with smp} && %{with dist_kernel}
install cap_over-smp.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/cap_over.ko
%endif
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT/sbin
install policy.pl $RPM_BUILD_ROOT/sbin
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-misc-cap_over
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-misc-cap_over
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-misc-cap_over
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-misc-cap_over
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc readme.txt doc/[e-t]*
%attr(755,root,root) /sbin/policy.pl
%endif

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-misc-cap_over
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-misc-cap_over
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*
%endif
%endif
