"""  Copyright (c) 2005-2010 Canonical
  Author: Michael Vogt <michael.vogt@ubuntu.com>

  eDeb Revisions: Anthony "AntCer" Cervantes <bodhidocs@gmail.com>"""

import apt
import apt_inst
import apt_pkg
from elementary import exit as elmexit



class DebPackage(object):
    """A Debian Package (.deb file)."""
    (VERSION_NONE,
     VERSION_OUTDATED,
     VERSION_SAME,
     VERSION_NEWER) = range(4)

    debug = 0

    def __init__(self, filename=None, cache=None):
        if cache is None:
            cache = apt.Cache()
        self.cache = cache
        self.multiarch = None
        if filename:
            self.open(filename)

    def open(self, filename):
        """ open given debfile """
        self.need_pkgs = []
        self.installed_conflicts = set()
        self.filename = filename
        try:
            self.debfile = apt_inst.DebFile(filename)
        except:
            print("eDeb Critical Error: Invalid archive signature. Either permissions issue or file is corrupted.\nExiting...")
            elmexit()
            quit()
        control = self.debfile.control.extractdata("control")
        self.sections = apt_pkg.TagSection(control)
        self.pkgname = self.sections["Package"]
        self.check_was_run = False

    def __getitem__(self, key):
        return self.sections[key]

    @property
    def filelist(self):
        """return the list of files in the deb."""
        files = []
        try:
            self.debfile.data.go(lambda item, data: files.append(item.name))
        except SystemError:
            return False
            #~ [_("List of files for '%s' could not be read") % self.filename]
        return files

    # helper that will return a pkgname with a multiarch suffix if needed
    def maybe_append_multiarch_suffix(self, pkgname, in_conflict_checking=False):
        # trivial cases
        if not self.multiarch:
            return pkgname
        elif self.cache.is_virtual_package(pkgname):
            return pkgname
        elif (pkgname in self.cache and self.cache[pkgname].candidate.architecture == "all"):
            return pkgname
        # now do the real multiarch checking
        multiarch_pkgname = "%s:%s" % (pkgname, self.multiarch)
        # the upper layers will handle this
        if not multiarch_pkgname in self.cache:
            return multiarch_pkgname
        # now check the multiarch state
        cand = self.cache[multiarch_pkgname].candidate._cand
        # the default is to add the suffix, unless its a pkg that can satify
        # foreign dependencies
        if cand.multi_arch & cand.MULTI_ARCH_FOREIGN:
            return pkgname
        # for conflicts we need a special case here, any not multiarch enabled package has a implicit conflict
        if (in_conflict_checking and not (cand.multi_arch & cand.MULTI_ARCH_SAME)):
            return pkgname
        return multiarch_pkgname

    def is_or_group_satisfied(self, or_group):
        """Return True if at least one dependency of the or-group is satisfied.

        This method gets an 'or_group' and analyzes if at least one dependency
        of this group is already satisfied.
        """

        for dep in or_group:
            depname = dep[0]
            ver = dep[1]
            oper = dep[2]

            # multiarch
            depname = self.maybe_append_multiarch_suffix(depname)

            # check for virtual pkgs
            if not depname in self.cache:
                if self.cache.is_virtual_package(depname):
                    for pkg in self.cache.get_providing_packages(depname):
                        if pkg.is_installed:
                            return True
                continue
            # check real dependency
            inst = self.cache[depname].installed
            if inst is not None and apt_pkg.check_dep(inst.version, oper, ver):
                return True

            # if no real dependency is installed, check if there is
            # a package installed that provides this dependency
            # (e.g. scrollkeeper dependecies are provided by rarian-compat)
            # but only do that if there is no version required in the
            # dependency (we do not supprot versionized dependencies)
            if not oper:
                for ppkg in self.cache.get_providing_packages(depname, include_nonvirtual=True):
                    if ppkg.is_installed:
                        return True
        return False

    def satisfy_or_group(self, or_group):
        """Try to satisfy the or_group."""
        for dep in or_group:
            depname, ver, oper = dep

            # multiarch
            depname = self.maybe_append_multiarch_suffix(depname)

            # if we don't have it in the cache, it may be virtual
            if not depname in self.cache:
                if not self.cache.is_virtual_package(depname):
                    continue
                providers = self.cache.get_providing_packages(depname)
                # if a package just has a single virtual provider, we
                # just pick that (just like apt)
                if len(providers) != 1:
                    continue
                depname = providers[0].name

            # now check if we can satisfy the deps with the candidate(s)
            # in the cache
            pkg = self.cache[depname]
            cand = self.cache._depcache.get_candidate_ver(pkg._pkg)
            if not cand:
                continue
            if not apt_pkg.check_dep(cand.ver_str, oper, ver):
                continue

            # check if we need to install it
            if not depname in " ".join(self.need_pkgs):
                self.need_pkgs.append(depname)
            return True

        # if we reach this point, we failed
        or_str = ""
        for dep in or_group:
            or_str += dep[0]
            if ver and oper:
                or_str += " (%s %s)" % (dep[2], dep[1])
            if dep != or_group[len(or_group)-1]:
                or_str += "|"
        #~ self.failure_string += _("Dependency is not satisfiable: %s\n") % or_str
        return False

    def check_single_pkg_conflict(self, pkgname, ver, oper):
        """Return True if a pkg conflicts with a real installed/marked pkg."""
        # FIXME: deal with conflicts against its own provides
        #        (e.g. Provides: ftp-server, Conflicts: ftp-server)
        pkg = self.cache[pkgname]
        if pkg.is_installed:
            pkgver = pkg.installed.version
        elif pkg.marked_install:
            pkgver = pkg.candidate.version
        else:
            return False

        if (apt_pkg.check_dep(pkgver, oper, ver) and not
            self.replaces_real_pkg(pkgname, oper, ver)):
            #~ self.failure_string += _("Conflicts with the installed package "
                                      #~ "'%s'") % pkg.name
            return True
        return False

    def check_conflicts_or_group(self, or_group):
        """Check the or-group for conflicts with installed pkgs."""
        for dep in or_group:
            depname = dep[0]
            ver = dep[1]
            oper = dep[2]

            # FIXME: is this good enough? i.e. will apt always populate
            #        the cache with conflicting pkgnames for our arch?
            depname = self.maybe_append_multiarch_suffix(
                depname, in_conflict_checking=True)

            # check conflicts with virtual pkgs
            if not depname in self.cache:
                # FIXME: we have to check for virtual replaces here as
                #        well (to pass tests/gdebi-test8.deb)
                if self.cache.is_virtual_package(depname):
                    for pkg in self.cache.get_providing_packages(depname):
                        # P/C/R on virtal pkg, e.g. ftpd
                        if self.pkgname == pkg.name:
                            continue
                        if self.check_single_pkg_conflict(pkg.name, ver,
                                                           oper):
                            self.installed_conflicts.add(pkg.name)
                continue
            if self.check_single_pkg_conflict(depname, ver, oper):
                self.installed_conflicts.add(depname)
        return bool(self.installed_conflicts)

    @property
    def conflicts(self):
        """List of package names conflicting with this package."""
        key = "Conflicts"
        try:
            return apt_pkg.parse_depends(self.sections[key])
        except KeyError:
            return []

    @property
    def depends(self):
        """List of package names on which this package depends on."""
        depends = []
        # find depends
        for key in "Depends", "Pre-Depends":
            try:
                depends.extend(apt_pkg.parse_depends(self.sections[key]))
            except KeyError:
                pass
        return depends

    @property
    def provides(self):
        """List of virtual packages which are provided by this package."""
        key = "Provides"
        try:
            return apt_pkg.parse_depends(self.sections[key])
        except KeyError:
            return []

    @property
    def replaces(self):
        """List of packages which are replaced by this package."""
        key = "Replaces"
        try:
            return apt_pkg.parse_depends(self.sections[key])
        except KeyError:
            return []

    def check_conflicts(self):
        """Check if there are conflicts with existing or selected packages.

        Check if the package conflicts with a existing or to be installed
        package. Return True if the pkg is OK.
        """
        res = True
        for or_group in self.conflicts:
            if self.check_conflicts_or_group(or_group):
                #print "Conflicts with a exisiting pkg!"
                #self.failure_string = "Conflicts with a exisiting pkg!"
                res = False
        return res

    def check_breaks_existing_packages(self):
        """
        check if installing the package would break exsisting
        package on the system, e.g. system has:
        smc depends on smc-data (= 1.4)
        and user tries to installs smc-data 1.6
        """
        # show progress information as this step may take some time
        debver = self.sections["Version"]
        debarch = self.sections["Architecture"]
        # store what we provide so that we can later check against that
        provides = [ x[0][0] for x in self.provides]
        for (i, pkg) in enumerate(self.cache):
            if not pkg.is_installed:
                continue
            # check if the exising dependencies are still satisfied with the package
            ver = pkg._pkg.current_ver
            for dep_or in pkg.installed.dependencies:
                for dep in dep_or.or_dependencies:
                    if dep.name == self.pkgname:
                        if not apt_pkg.check_dep(debver, dep.relation, dep.version):
                            failure_string = "Breaks existing package <b>%(pkgname)s</b> with dependency:<br>     <b>%(depname)s</b> (%(deprelation)s%(depversion)s)" % {
                                'pkgname' : pkg.name,
                                'depname' : dep.name,
                                'deprelation' : dep.relation,
                                'depversion' : dep.version}
                            return failure_string
            # now check if there are conflicts against this package on the existing system
            if "Conflicts" in ver.depends_list:
                for conflicts_ver_list in ver.depends_list["Conflicts"]:
                    for c_or in conflicts_ver_list:
                        if c_or.target_pkg.name == self.pkgname and c_or.target_pkg.architecture == debarch:
                            if apt_pkg.check_dep(debver, c_or.comp_type, c_or.target_ver):
                                failure_string = "Breaks existing package <b>%(pkgname)s</b> conflict:<br>     <b>%(targetpkg)s</b> (%(comptype)s%(targetver)s)" % {
                                    'pkgname' : pkg.name,
                                    'targetpkg' : c_or.target_pkg.name,
                                    'comptype' : c_or.comp_type,
                                    'targetver' : c_or.target_ver }
                                return failure_string
                        if (c_or.target_pkg.name in provides and self.pkgname != pkg.name):
                            failure_string = "Breaks existing package <b>%(pkgname)s</b> that conflict:<br>     <b>%(targetpkg)s</b><br><br>But the <b>%(debfile)s</b> provides it via:<br>     <b>%(provides)s</b>" % {
                                'provides' : ",".join(provides),
                                'debfile'  : self.filename,
                                'targetpkg' : c_or.target_pkg.name,
                                'pkgname' : pkg.name }
                            return failure_string
        return True

    def compare_to_version_in_cache(self, use_installed=True):
        """Compare the package to the version available in the cache.

        Checks if the package is already installed or availabe in the cache
        and if so in what version, returns one of (VERSION_NONE,
        VERSION_OUTDATED, VERSION_SAME, VERSION_NEWER).
        """
        pkgname = self.sections["Package"]
        debver = self.sections["Version"]
        if pkgname in self.cache:
            if use_installed and self.cache[pkgname].installed:
                cachever = self.cache[pkgname].installed.version
            elif not use_installed and self.cache[pkgname].candidate:
                cachever = self.cache[pkgname].candidate.version
            else:
                return self.VERSION_NONE
            if cachever is not None:
                cmp = apt_pkg.version_compare(cachever, debver)
                if cmp == 0:
                    return self.VERSION_SAME
                elif cmp < 0:
                    return self.VERSION_NEWER
                elif cmp > 0:
                    return self.VERSION_OUTDATED
        return self.VERSION_NONE

    def depends_check(self, clear=False):
        """Check package dependencies."""

        self.check_was_run = True

        if not self.satisfy_depends(self.depends, clear):
            return False


    def check(self):
        """Check if the package is installable."""

        self.check_was_run = True

        if not "Architecture" in self.sections:
            print("eDeb Package Error: No Architecture field in the package")
            return "Package was created poorly. No Architecture field in the package"
        arch = self.sections["Architecture"]
        if  arch != "all" and arch != apt_pkg.config.find("APT::Architecture"):
            if arch in apt_pkg.get_architectures():
                self.multiarch = arch
                self.pkgname = "%s:%s" % (self.pkgname, self.multiarch)
            else:
                print("eDeb Package Error: Wrong architecture, %s" %arch)
                return "Package is not eligible for installation because of wrong architecture: <b>%s</b>" %arch

        if self.cache._depcache.broken_count > 0:
            print("eDeb Package Error: Failed to satisfy dependencies. Broken cache. Now clearing..")
            self.cache.clear()
            print("eDeb Notification: Cache cleared.")
            return "Broken dependencies from previous installation (broken cache). Cache has been cleared.<ps><ps>If the issue persists, please select Fix to attempt to complete the broken installation."
        return True

    def satisfy_depends(self, depends, clear=False):
        """Satisfy the dependencies."""
        if clear:
            self.cache = apt.Cache()
            self.need_pkgs = []

        # turn off MarkAndSweep via a action group (if available)
        try:
            _actiongroup = apt_pkg.ActionGroup(self.cache._depcache)
        except AttributeError:
            pass
        # check depends
        for or_group in depends:
            #~ print "or_group: %s" % or_group
            #~ print "or_group satified: %s" % self.is_or_group_satisfied(or_group)
            if not self.is_or_group_satisfied(or_group):
                if not self.satisfy_or_group(or_group):
                    return False
        # now try it out in the cache
        for pkg in self.need_pkgs:
            try:
                self.cache[pkg].mark_install(from_user=False)
            except SystemError:
                #~ self.failure_string = _("Cannot install '%s'") % pkg
                self.cache.clear()
                return False
        return True

    @property
    def missing_deps(self):
        """Return missing dependencies."""
        if not self.check_was_run:
            raise AttributeError("property only available after depends_check() is ran")
        return self.need_pkgs
