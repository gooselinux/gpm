Summary: A mouse server for the Linux console
Name: gpm
Version: 1.20.6
Release: 11%{?dist}
License: GPLv2+
Group: System Environment/Daemons
URL: http://www.nico.schottelius.org/software/gpm/
Source: http://www.nico.schottelius.org/software/gpm/archives/%{name}-%{version}.tar.lzma
Source1: gpm.init
Source2: inputattach.c
Source3: inputattach.1.gz
Patch1: gpm-1.20.6-multilib.patch
Patch2: gpm-1.20.1-lib-silent.patch
Patch3: gpm-1.20.3-gcc4.3.patch
Patch4: gpm-1.20.5-close-fds.patch
Patch5: gpm-1.20.1-weak-wgetch.patch
Patch6: gpm-1.20.6-libtool.patch
#Patch7: gpm-1.20.6-capability.patch
Requires(post): /sbin/chkconfig /sbin/install-info /sbin/ldconfig
Requires(preun): /sbin/chkconfig /sbin/install-info
Requires(postun): /sbin/ldconfig
Requires: %{name}-libs = %{version}-%{release}
# this defines the library version that this package builds.
%define LIBVER 2.1.0
BuildRoot: %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildRequires: sed gawk texinfo bison ncurses-devel autoconf automake libtool libcap-ng-devel

%description
Gpm provides mouse support to text-based Linux applications like the
Emacs editor and the Midnight Commander file management system.  Gpm
also provides console cut-and-paste operations using the mouse and
includes a program to allow pop-up menus to appear at the click of a
mouse button.

%package libs
Summary: Dynamic library for for the gpm
Group: System Environment/Libraries

%description libs
This package contains the libgpm.so dynamic library which contains
the gpm system calls and library functions.

%package devel
Requires: %{name}-libs = %{version}-%{release}
Summary: Development files for the gpm library
Group: Development/Libraries

%description devel
The gpm-devel package includes header files and libraries necessary
for developing programs which use the gpm library. The gpm provides
mouse support to text-based Linux applications.

%package static
Requires: %{name} = %{version}-%{release}
Summary: Static development files for the gpm library
Group: Development/Libraries

%description static
The gpm-static package includes static libraries of gpm. The gpm provides
mouse support to text-based Linux applications.


%prep
%setup -q
%patch1 -p1 -b .multilib
%patch2 -p1 -b .lib-silent
%patch3 -p1 -b .gcc4.3
%patch4 -p1 -b .close-fds
%patch5 -p1 -b .weak-wgetch
%patch6 -p1 -b .libtool
#%patch7 -p1 -b .capability

iconv -f iso-8859-1 -t utf-8 -o TODO.utf8 TODO
touch -c -r TODO TODO.utf8
mv -f TODO.utf8 TODO

autoreconf

%build
%configure
make %{?_smp_mflags}
%__cc $RPM_OPT_FLAGS -o inputattach %{SOURCE2}


%install
rm -rf %{buildroot}

%makeinstall

chmod 0755 %{buildroot}/%{_libdir}/libgpm.so.%{LIBVER}
ln -sf libgpm.so.%{LIBVER} %{buildroot}/%{_libdir}/libgpm.so

install -m 644 %{SOURCE3} %{buildroot}%{_mandir}/man1/inputattach.1.gz

%ifnarch s390 s390x
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d  
install -m 755 inputattach %{buildroot}%{_sbindir}
install -m 644 conf/gpm-* %{buildroot}%{_sysconfdir}
install -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/gpm
%else
# we're shipping only libraries in s390[x], so
# remove stuff from the buildroot that we aren't shipping
rm -rf %{buildroot}%{_sbindir}
rm -rf %{buildroot}%{_bindir}
rm -rf %{buildroot}%{_mandir}
%endif

%clean
rm -rf %{buildroot}

%post
%ifnarch s390 s390x
/sbin/chkconfig --add gpm
%endif
if [ -e %{_infodir}/gpm.info.gz ]; then
  /sbin/install-info %{_infodir}/gpm.info.gz %{_infodir}/dir || :
fi
/sbin/ldconfig

%preun
%ifnarch s390 s390x
if [ $1 = 0 ]; then
    /sbin/service gpm stop >/dev/null 2>&1
    /sbin/chkconfig --del gpm
fi
%endif
if [ $1 = 0 -a -e %{_infodir}/gpm.info.gz ]; then
  /sbin/install-info %{_infodir}/gpm.info.gz --delete %{_infodir}/dir || :
fi

%postun
%ifnarch s390 s390x
if [ $1 -ge 1 ]; then
    /sbin/service gpm condrestart >/dev/null 2>&1
fi
%endif
/sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc BUGS COPYING README TODO
%doc doc/README* doc/FAQ doc/Announce doc/changes/*
%{_infodir}/*
%ifnarch s390 s390x
%config(noreplace) %{_sysconfdir}/gpm-*
%attr(0755,root,root) %{_sysconfdir}/rc.d/init.d/gpm
%{_sbindir}/*
%{_bindir}/*
%{_mandir}/man?/*
%endif

%files libs
%defattr(-,root,root,-)
%{_libdir}/libgpm.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/libgpm.so

%files static
%defattr(-,root,root,-)
%{_libdir}/libgpm.a

%changelog
* Thu Jun 24 2010 Nikola Pajkovsky <npajkovs@redhat.com> - 1.20.6-11
- add manpages
- add Requires: gpm-libs = %{version}-%{release}
- Resolves: #605053 - RPMdiff run failed for package gpm-1.20.6-10.el6
[snip from email]
 npajkovs@redhat.com: I'd like to ask you what kind of license did you use for inputattach?
 steve@sk2.org: I didn't mention it in debian/copyright, but
 all the packaging (including the manpages) are licensed under the same
 terms as the packaged source, ie. GPL-2 or later.

* Tue Jan 5 2010 Nikola Pajkovsky <npajkovs@redhat.com> - 1.20.6-10
- fix Url and Source

* Thu Dec 10 2009 Nikola Pajkovsky <npajkovs@redhat.com> 1.20.6-9
- add try-restart into gpm.init to be more LSB-compilant

* Thu Nov 19 2009 Nikola Pajkovsky <npajkovs@redhat.com> 1.20.6-8
- drop patch7
- resolved #537724(does not work with capabilities)

* Wed Sep 30 2009 Nikola Pajkovsky <npajkovs@redhat.com> 1.20.6-7
- add BuildRequires: libcap-ng-devel
- fix patch .capability

* Thu Aug 20 2009 Zdenek Prikryl <zprikryl@redhat.com> 1.20.6-6
- Don't complain if installing with --excludedocs (#515927)
- Drop unnecessary capabilities in gpm (#517659)

* Wed Aug 12 2009 Ville Skyttä <ville.skytta@iki.fi> - 1.20.6-5
- Use lzma compressed upstream tarball.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.20.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Apr 14 2009 Zdenek Prikryl <zprikryl@redhat.com> 1.20.6-3
- created new subpackage gpm-libs (#495124)

* Tue Feb 24 2009 Zdenek Prikryl <zprikryl@redhat.com> - 1.20.6-2
- Fixed gpm.info.gz building

* Tue Feb 03 2009 Zdenek Prikryl <zprikryl@redhat.com> - 1.20.6-1
- Spec review (#225856)
- Updated to 1.20.6

* Wed Dec 02 2008 Zdenek Prikryl <zprikryl@redhat.com> - 1.20.5-2
- Fixed debug mode (#473422)
- Fixed description in init script (#474337)

* Thu Jul 17 2008 Zdenek Prikryl <zprikryl@redhat.com> - 1.20.5-1
- Updated to 1.20.5
- Removed doc patch
- Removed lisp stuff, it is part of emacs-common now 
- Spec clean up

* Thu Jun 04 2008 Zdenek Prikryl <zprikryl@redhat.com> - 1.20.3-2
- Enable gpm in runlevel 5

* Thu May 29 2008 Zdenek Prikryl <zprikryl@redhat.com> - 1.20.3-1
- Updated to 1.20.3
- Fixed init script to comply with LSB standard (#246937)
- Mass patch cleanup
- Fixed typo in doc (#446679)

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.20.1-90
- Autorebuild for GCC 4.3

* Fri Aug 24 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-89
- license tag update (and rebuild for BuildID, etc.)

* Wed Jul 25 2007 Jesse Keating <jkeating@redhat.com> - 1.20.1-88
- Rebuild for RH #249435

* Tue Jul 24 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-87
- replace OPEN_MAX with sysconf(_SC_OPEN_MAX), fixing build with 2.6.23 kernel

* Tue Jul 24 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-86
- don't install t-mouse.el, emacs-common contains a newer version,
  fixes #249362

* Fri Jun 29 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-85
- applied patch for #246219, fixing segfault with vsyslog on x86_64

* Wed May 23 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-84
- applied patch for #240389, fixing default handlers

* Thu May 03 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-83
- gpm-devel now requires version-release correctly, fixes #238785

* Mon Apr 02 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-82
- updated inputattach.c to 1.24 from cvs, fixes #231635

* Fri Mar 23 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-81
- the patch for #168076 caused a strange behaviour with ncurses, fixed it
  differently

* Mon Jan 22 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-80
- forgot to add the patch for #168076

* Mon Jan 22 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-79
- added disttag to release

* Mon Jan 22 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-78
- refuse connections while waiting for console, fixes #168076

* Mon Jan 22 2007 Tomas Janousek <tjanouse@redhat.com> - 1.20.1-77
- #223696: non-failsafe install-info use in scriptlets

* Tue Oct 10 2006 Petr Rockai <prockai@redhat.com> - 1.20-1-76
- align sleeps to tick boundary, should reduce cpu wakeups
  on laptops, fixes #205064 (patch by Arjan van de Ven)
- disable gpm altogether in runlevel 5, it is probably not
  worth the overhead considering it is barely used at all

* Fri Sep 22 2006 Petr Rockai <prockai@redhat.com> - 1.20.1-75
- fix a bug where gpm daemon kept stdin/out/err open after
  detaching from terminal, causing eg. pipes from initscript
  to hang for the lifetime of gpm

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.20.1-74.1
- rebuild

* Wed Jun  7 2006 Jeremy Katz <katzj@redhat.com> - 1.20.1-74
- rebuild for -devel deps

* Mon Feb 13 2006 Petr Rockai <prockai@redhat.com> - 1.20.1-73.3
- rebuild due to failure on x86-64 (possibly a glitch?)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.20.1-73.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.20.1-73.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Wed Jan 18 2006 Petr Rockai <prockai@redhat.com> 1.20.1-73
- do not ooops in gpm when console device cannot be found, print
  an error message instead and exit(1), as per BR 140025, 176178
- do not print messages in libgpm, unless envvar GPM_VERBOSE
  is set -- avoids unwanted clutter from libgpm in apps like dialog
  or mc when gpm is not available

* Thu Dec 22 2005 Jesse Keating <jkeating@redhat.com> 1.20.1-72
- rebuilt again

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt
- added autoconf as a BuildReq

* Fri Mar 04 2005 Petr Rockai <prockai@redhat.com>
- rebuilt

* Mon Feb 14 2005 Adrian Havill <havill@redhat.com>
- rebuilt

* Thu Oct 21 2004 Adrian Havill <havill@redhat.com> 1.20.1-66
- avoid spawning multiple copies of inputattach, and kill process
  when gpm shuts down (#135776)

* Wed Oct 20 2004 Bill Nottingham <notting@redhat.com> 1.20.1-65
- remove buildroot paths from gpm.info, fixing #135305

* Wed Oct 20 2004 Adrian Havill <havill@redhat.com> 1.20.1-64
- fixing multilib conflict (#135305):
  o remove buildsys check/conditional for gziping info pages (let rpm
    do it)
  o don't pre-byte-compile emacs code

* Thu Oct 14 2004 Bill Nottingham <notting@redhat.com> 1.20.1-62
- fix remaining sourcing of /etc/sysconfig/gpm (#135776)

* Wed Oct 13 2004 Adrian Havill <havill@redhat.com> 1.20.1-61
- remove unnecessary diagnostic and check of the consolename (#129962)
- remove /etc/sysconfig/gpm; set unset defaults in the init script instead
  after mousecfg is (or is not) read

* Wed Oct 13 2004 Florian La Roche <laroche@redhat.com>
- sysconfig/gpm should probably go away, that is more confusing than
  helping anyone
- read at least sysconfig/gpm first as it seems to have the default values
  and sysconfig/mouse is getting probed values and probably has better
  settings in it.

* Tue Oct 12 2004 Adrian Havill <havill@redhat.com> 1.20.1-57
- read both the sysconfig/mouse and sysconfig/gpm (preferrence to gpm
  settings), not just one of them, if both exist (#134389)

* Tue Oct 12 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- remove gzip of info pages within .spec file, #135305

* Sat Oct 09 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- initscript cleanup

* Thu Sep 23 2004 Adrian Havill <havill@redhat.com> 1.20.1-54
- change init so that MOUSECFG fallsback to /etc/sysconfig/gpm if
  /etc/sysconfig/mouse doesn't exist (#133141)
- fixed compile vs new kernheaders (#131783)

* Tue May 04 2004 Adrian Havill <havill@redhat.com> 1.20.1-49
- remove superfluous "i die" msg (#121845)

* Tue May 04 2004 Adrian Havill <havill@redhat.com> 1.20.1-48
- restore gpmopen() NULL check that was removed with the
  evdev superpatch (#118554)

* Fri Apr 16 2004 Adrian Havill <havill@redhat.com> 1.20.1-47
- make presence of t-mouse.el flexible (#120958)

* Wed Mar 31 2004 Adrian Havill <havill@redhat.com> 1.20.1-46
- revise nodebug patch as liblow reporting the VC to the console through
  stderr has re-appeared (#117676)

* Mon Mar 22 2004 Adrian Havill <havill@redhat.com> 1.20.1-45
- remove circular ncurses dep for prelink by restoring wgetch
  patch (#117150)

* Wed Mar 17 2004 Bill Nottingham <notting@redhat.com> 1.20.1-44
- include inputattach
- if configured mouse has IMOUSETYPE, use inputattach

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 26 2004 Adrian Havill <havill@redhat.com> 1.20.1-43
- add event device (for 2.6 kernel) superpatch-- includes all
  patches up to release 38; thanks to Dmitry Torokhov
- change default mouse device over to /dev/input/mice
- set mouse type to Intellimouse Explorer (exps2), which is what
  the 2.6 kernel exports by default

* Sat Feb 14 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- already add shared lib symlinks at install time
- fix subscript #114289

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Nov 18 2003 Adrian Havill <havill@redhat.com> 1.20.1-39
- re-add the $OPTIONS that gets pulled in from /etc/sysconfig/gpm
  to the init.d script (#110248)

* Wed Aug 07 2003 Adrian Havill <havill@redhat.com> 1.20.1-38
- Gpm_Open() NULL deref revisited (#101104). Patch by
  <leonardjo@hetnet.nl>
* Wed Jul 30 2003 Adrian Havill <havill@redhat.com> 1.20.1-37
- removed auto-add of repeat with -M (#84310)

* Tue Jul 29 2003 Adrian Havill <havill@redhat.com> 1.20.1-36
- fixed grammar typos in the init script (#89109)
- don't deref NULL string in Gpm_Open (#101104)

* Wed Jul 02 2003 Adrian Havill <havill@redhat.com> 1.20.1-35
- remove debug output from gpm_report() to prevent spurious
  debugging msgs even when not in debug mode (#98210)
  
* Thu Jun 26 2003 Adrian Havill <havill@redhat.com> 1.20.1-33
- reversed -t and -m params in init script, removed $OPTION
- add doc blurb regarding no auto-repeat with multiple mice

* Tue Jun 24 2003 Adrian Havill <havill@redhat.com> 1.20.1-32
- update version
- add -lm for ceil()
- add hltest, mouse-test for all but zSeries

* Mon Jun 16 2003 Jakub Jelinek <jakub@redhat.com>
- don't link against -lncurses, instead make wgetch and stdscr weak
  undefined symbols to break library dependency cycle

* Thu Jun 12 2003 Elliot Lee <sopwith@redhat.com>
- Remove pam requirement

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan 29 2003 Bill Nottingham <notting@redhat.com> 1.19.13-27
- ship libraries on s390/s390x

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Mon Jan 13 2003 Bill Nottingham <notting@redhat.com> 1.19.13-25
- don't automatically enable the repeater when '-M' is in use

* Fri Nov 22 2002 Tim Powers <timp@redhat.com>
- remove unpackaged files from the buildroot

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Apr  9 2002 Bernhard Rosenkraenzer <bero@redhat.com> 
- Revert to the version from 7.2 because later versions have some grave
  issues I can't {reproduce,debug} with my hardware, such as
  #62540 and #61691

* Thu Jul 19 2001 Preston Brown <pbrown@redhat.com>
- more documentation fixes for Netmouse type devices (#48885)

* Tue Jun 26 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- add link from library major version number

* Mon Jun 25 2001 Preston Brown <pbrown@redhat.com>
- small fixlet in init script (#36995)

* Tue Jun 19 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- add ExcludeArch: s390 s390x

* Fri Apr  6 2001 Preston Brown <pbrown@redhat.com>
- work better with unsupported devfs (#23500, #34883)

* Mon Feb 05 2001 Karsten Hopp <karsten@redhat.de>
- found another bug: tmpfile was never removed if
  gpm was already running

* Mon Feb 05 2001 Karsten Hopp <karsten@redhat.de>
- really fix tmpfile path

* Mon Feb 05 2001 Karsten Hopp <karsten@redhat.de>
- fix tmpfile path (bugzilla  #25967)

* Tue Jan 30 2001 Preston Brown <pbrown@redhat.com>
- don't make PID file world-writable.

* Mon Jan 29 2001 Preston Brown <pbrown@redhat.com>
- fix up devel dependency on main package

* Sun Jan 28 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Don't crash if we can't open /dev/console
  (Happens with some devfs enabled kernels)

* Tue Jan 23 2001 Trond Eivind Glomsr�d <teg@redhat.com>
- fix bug in i18n of initscript

* Tue Jan 23 2001 Preston Brown <pbrown@redhat.com>
- bash2 style of i18n for initscript

* Wed Jan 17 2001 Preston Brown <pbrown@redhat.com>
- i18n the initscript.

* Thu Jan 11 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Add hooks for extra options in /etc/sysconfig/gpm (#23547)

* Fri Jan 05 2001 Preston Brown <pbrown@redhat.com>
- patch added to abort if running on a serial console (#15784)

* Fri Jul 28 2000 Preston Brown <pbrown@redhat.com>
- cleaned up post section

* Wed Jul 26 2000 Preston Brown <pbrown@redhat.com>
- clarification: pam requirement added to fix permissions on /dev/gpmctl (#12849)

* Sat Jul 22 2000 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.19.3

* Sat Jul 15 2000 Bill Nottingham <notting@redhat.com>
- move initscript back

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Fri Jun 30 2000 Matt Wilson <msw@redhat.com>
- use sysconf(_SC_OPEN_MAX)

* Tue Jun 27 2000 Preston Brown <pbrown@redhat.com>
- don't prereq, only require initscripts

* Mon Jun 26 2000 Preston Brown <pbrown@redhat.com>
- fix up and move initscript
- prereq initscripts >= 5.20

* Sat Jun 17 2000 Bill Nottingham <notting@redhat.com>
- fix %%config tag for initscript

* Thu Jun 15 2000 Bill Nottingham <notting@redhat.com>
- move it back

* Thu Jun 15 2000 Preston Brown <pbrown@redhat.com>
- move init script

* Wed Jun 14 2000 Preston Brown <pbrown@redhat.com>
- security patch on socket descriptor from Chris Evans.  Thanks Chris.
- include limits.h for OPEN_MAX

* Mon Jun 12 2000 Preston Brown <pbrown@redhat.com>
- 1.19.2, fix up root (setuid) patch
- FHS paths

* Thu Apr  6 2000 Jakub Jelinek <jakub@redhat.com>
- 1.19.1
- call initgroups in gpm-root before spawning command as user
- make gpm-root work on big endian

* Sun Mar 26 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- call ldconfig directly in postun

* Wed Mar 22 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- rebuild with new libncurses

* Sat Mar 18 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.19.0
- fix build on systems that don't have emacs
  (configure built t-mouse* only if emacs was installed)

* Tue Feb 29 2000 Preston Brown <pbrown@redhat.com>
- important fix: improperly buildrooted for /usr/share/emacs/site-lisp, fixed.

* Tue Feb 15 2000 Jakub Jelinek <jakub@redhat.com>
- avoid cluttering of syslog with gpm No data messages

* Mon Feb 14 2000 Preston Brown <pbrown@redhat.com>
- disable-paste and mouse-test removed, they seem broken.

* Thu Feb 03 2000 Preston Brown <pbrown@redhat.com>
- updated gpm.init to have better shutdown and descriptive messages
- strip lib

* Wed Feb 02 2000 Cristian Gafton <gafton@redhat.com>
- fix description
- man pages are compressed

* Wed Jan 12 2000 Preston Brown <pbrown@redhat.com>
- 1.18.1.

* Tue Sep 28 1999 Preston Brown <pbrown@redhat.com>
- upgraded to 1.18, hopefully fixes sparc protocol issues

* Fri Sep 24 1999 Bill Nottingham <notting@redhat.com>
- install-info sucks, and then you die.

* Fri Sep 10 1999 Bill Nottingham <notting@redhat.com>
- chkconfig --del in %%preun, not %%postun

* Fri Aug 27 1999 Preston Brown <pbrown@redhat.com>
- upgrade to 1.17.9
- the maintainers are taking care of .so version now, removed patch

* Mon Aug 16 1999 Bill Nottingham <notting@redhat.com>
- initscript munging

* Wed Jun  2 1999 Jeff Johnson <jbj@redhat.com>
- disable-paste need not be setuid root in Red Hat 6.0 (#2654)

* Tue May 18 1999 Michael K. Johnson <johnsonm@redhat.com>
- gpm.init had wrong pidfile name in comments; confused linuxconf

* Mon Mar 22 1999 Preston Brown <pbrown@redhat.com>
- make sure all binaries are stripped, make init stuff more chkconfig style
- removed sparc-specific mouse stuff
- bumped libver to 1.17.5
- fixed texinfo source

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 2)

* Thu Mar  4 1999 Matt Wilson <msw@redhat.com>
- updated to 1.75.5

* Tue Feb 16 1999 Cristian Gafton <gafton@redhat.com>
- avoid using makedev for internal functions (it is a #define in the system
  headers)

* Wed Jan 13 1999 Preston Brown <pbrown@redhat.com>
- upgrade to 1.17.2.

* Wed Jan 06 1999 Cristian Gafton <gafton@redhat.com>
- enforce the use of -D_GNU_SOURCE so that it will compile on the ARM
- build against glibc 2.1

* Tue Aug 11 1998 Jeff Johnson <jbj@redhat.com>
- build root

* Thu May 07 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Wed Apr 22 1998 Michael K. Johnson <johnsonm@redhat.com>
- enhanced initscript

* Fri Apr 10 1998 Cristian Gafton <gafton@redhat.com>
- recompiled for manhattan

* Wed Apr 08 1998 Erik Troan <ewt@redhat.com>
- updated to 1.13

* Mon Nov 03 1997 Donnie Barnes <djb@redhat.com>
- added patch from Richard to get things to build on the SPARC

* Tue Oct 28 1997 Donnie Barnes <djb@redhat.com>
- fixed the emacs patch to install the emacs files in the right
  place (hopefully).

* Mon Oct 13 1997 Erik Troan <ewt@redhat.com>
- added chkconfig support
- added install-info

* Thu Sep 11 1997 Donald Barnes <djb@redhat.com>
- upgraded from 1.10 to 1.12
- added status/restart functionality to init script
- added define LIBVER 1.11

* Thu Jun 19 1997 Erik Troan <ewt@redhat.com>
- built against glibc
