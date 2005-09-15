#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
#
Summary:	Capability Override LSM
Summary(pl):	Modu³ LSM Capability Override
Name:		CapOver
Version:	0.9.3
%define rel	0.1
Release:	%{rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://files.randombit.net/cap_over/%{name}-%{version}.tgz
# Source0-md5:	971e50c1abaa97ee4a9958e92dd88300
URL:		http://www.randombit.net/projects/cap_over/
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.0}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Capability Override LSM, is a kernel module which gives
the ability to specify that certain users/groups/programs are
to gain access to one or more extra capabilities. This means
this LSM is a permissive module, rather than a restrictive one
(which is more typical of LSMs).

%description -l pl
Capability Override LSM to modu³ j±dra daj±cy mo¿liwo¶æ okre¶lenia
pewnych u¿ytkowników/grup/programów mog±cych mieæ dostêp do jednego
lub wiêkszej liczby uprawnieñ (capabilities). Oznacza to, ¿e ten LSM
jest modu³em zezwalaj±cym, a nie restrykcyjnym (co jest bardziej
typowe dla LSM).

%package -n kernel-misc-cap_over
Summary:	cap_over kernel module
Summary(pl):	Modu³ j±dra cap_over
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires:	CapOver

%description -n kernel-misc-cap_over
cap_over kernel module.

%description -n kernel-misc-cap_over -l pl
Modu³ j±dra cap_over.

%package -n kernel-smp-misc-cap_over
Summary:	cap_over SMP kernel module
Summary(pl):	Modu³ SMP j±dra cap_over
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Requires:	CapOver

%description -n kernel-smp-misc-cap_over
cap_over SMP kernel module.

%description -n kernel-smp-misc-cap_over -l pl
Modu³ SMP j±dra cap_over.

%prep
%setup -q

%build
%if %{with kernel}
%configure
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	mkdir -p modules/$cfg
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	chmod 000 modules
	install -d include/{linux,config}
	%{__make} -C %{_kernelsrcdir} clean \
		SUBDIRS=$PWD \
		O=$PWD \
		%{?with_verbose:V=1}
	install -d include/config
	chmod 700 modules
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-${cfg}.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} modules \
		SUBDIRS=$PWD \
		O=$PWD \
		%{?with_verbose:V=1}
	mv *.ko modules/$cfg/
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
install modules/%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/*.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
%if %{with smp} && %{with dist_kernel}
install modules/smp/*.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
%endif
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT/sbin
install policy.pl $RPM_BUILD_ROOT/sbin
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-misc-cap_over
%depmod %{_kernel_ver}

%postun	-n kernel-misc-cap_over
%depmod %{_kernel_ver}

%post	-n kernel-smp-misc-cap_over
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-misc-cap_over
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc readme.txt doc/[e-t]*
%attr(755,root,root) /sbin/policy.pl
%endif

%if %{with kernel}
%files -n kernel-misc-cap_over
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-misc-cap_over
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*
%endif
%endif
