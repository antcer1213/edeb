import os
import logging
import mimetypes
import evas, esudo
import elementary as elm
import debfile as debianfile
import getpass, urllib2, commands
from apt_inst import debExtractControl
logging.basicConfig(level=logging.DEBUG)


#----Common
def popup_close(btn, popup):
    popup.delete()

def iw_close(bt, iw):
    iw.delete()

#----Popups
def nofile_error_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    popup.text = "<b>No File Selected</><br><br>Please select an appropriate file candidate for installation."
    popup.timeout = 3.0
    popup.show()

def file_error_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    popup.text = "<b>Invalid File Format</><br><br>That is <em>not</> a .deb file!"
    popup.timeout = 3.0
    popup.show()

def no_net_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    popup.text = "<b>Error</><br><br>No internet access.<br>Please try again when connected to internet."
    bt = elm.Button(win)
    bt.text = "OK"
    bt.callback_clicked_add(popup_close, popup)
    popup.part_content_set("button1", bt)
    popup.show()

def finished_dep_install_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    popup.text = "<b>Successful!</b><br><br>Missing dependencies successfully installed."
    bt = elm.Button(win)
    bt.text = "OK"
    bt.callback_clicked_add(popup_close, popup)
    popup.part_content_set("button1", bt)
    popup.show()

def not_installable_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    popup.text = "<b>Error</b><br><br>This file has failed initial check. It cannot be installed.<br><br>This is most often caused by a previously broken installation. Click <b>Fix</b> to attempt to repair broken packages, then try again.<br><br>If this occurs again, then the file may be of the wrong architecture."
    bt = elm.Button(win)
    bt.text = "Fix"
    bt.callback_clicked_add(dependency_comp, popup, win)
    popup.part_content_set("button1", bt)
    bt = elm.Button(win)
    bt.text = "Close"
    bt.callback_clicked_add(popup_close, popup)
    popup.part_content_set("button2", bt)
    popup.show()

def dependency_popup(win):
    print "SHIT"
    popup = elm.Popup(win)
    popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    popup.text = "<b>Urgent</b><br><br>Installation Semi-Finished. All dependencies were not met.<ps><ps>Click <b>Grab</> to attempt to grab the missing dependencies and complete the installation."
    bt = elm.Button(win)
    bt.text = "Grab"
    bt.callback_clicked_add(dependency_comp, win)
    popup.part_content_set("button1", bt)
    popup.show()

def finished_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    popup.text = "<b>Installation Finished!</b><br><br>The installation was successful."
    bt = elm.Button(self.win)
    bt.text = "OK"
    bt.callback_clicked_add(popup_close, popup)
    popup.part_content_set("button1", bt)
    popup.show()

#----Dependency Completion
def dependency_comp(bt, popup, win):
    print "hey"
    popup.delete()
    try:
        con = urllib2.urlopen("http://www.google.com/")
    except:
        logging.exception("No network activity detected")
        logging.exception("Please try again with an established Internet Connection.")
        no_net_popup(win)
    else:
        logging.info("Starting attempt to fulfill dependencies:")
        dep_comp = "apt-get -f install -y"
        esudo.eSudo(dep_comp, win, end_callback=dep_cb)

#---End Callbacks
def dep_grab_cb(exit_code):
    if exit_code == 0:
        logging.info("Successfully Grabbed Dependencies.")
        finished_dep_install_popup(win)
    else:
        logging.info("Something went wrong while installing dependencies.")
def main_cb(exit_code):
    if exit_code == 0:
        logging.info("Installation Completed!")
        finished_popup(win)
    else:
        logging.info("Something went wrong. Likely, dependencies that weren't met before attempting installation.")
        print "damn"
        dependency_popup(win)
        print "yo"
def dep_cb(exit_code):
    if exit_code == 0:
        logging.info("Successfully Grabbed Dependencies & Completed Installation.")
        #~ chk = Checks(file, win, end_callback=False)
        finished_popup(win)
    else:
        logging.info("Something went wrong while attempting to complete installation.")





class Checks(object):
    def __init__(self, command=False, window=False, end_callback=False ):
        self.win = window
        self.file = command
        self.end_cb = end_callback if callable(end_callback) else None

#----Package Info
    def pkg_information(self, win):
        deb = debianfile.DebPackage(self.file, cache=None)
        #~ control = debExtractControl(open(self.file))
        #~ filing = u'%s' %control
        pkg_name = commands.getoutput("dpkg -f %s | awk '/Package:/'" %self.file)
        pkg_ver  = commands.getoutput("dpkg -f %s | awk '/Version:/'" %self.file)
        pkg_sec  = commands.getoutput("dpkg -f %s | awk '/Section:/'" %self.file)
        pkg_pri  = commands.getoutput("dpkg -f %s | awk '/Priority:/'" %self.file)
        pkg_dep  = commands.getoutput("dpkg -f %s | sed 's/<</less than/' | awk '/Depends:/' | sed 's/Depends:/ /' | sed 's/Pre-/ /'" %self.file)
        pkg_arch = commands.getoutput("dpkg -f %s | awk '/Architecture:/'" %self.file)
        pkg_size = commands.getoutput("dpkg -f %s | awk '/Installed-Size:/'" %self.file)
        pkg_auth = commands.getoutput("dpkg -f %s | awk '/Maintainer:/'" %self.file)
        pkg_desc = commands.getoutput("dpkg -f %s | awk '/Description:/'" %self.file)
        pkg_recc = commands.getoutput("dpkg -f %s | awk '/Recommends:/'" %self.file)
        pkg_conf = commands.getoutput("dpkg -f %s | awk '/Conflicts:/'" %self.file)
        pkg_repl = commands.getoutput("dpkg -f %s | awk '/Replaces:/'" %self.file)
        pkg_prov = commands.getoutput("dpkg -f %s | awk '/Provides:/'" %self.file)
        pkg_hp   = commands.getoutput("dpkg -f %s | awk '/Homepage:/'" %self.file)

        def dependency_grab(bt, win):
            try:
                con = urllib2.urlopen("http://www.google.com/")
            except:
                logging.exception("No network activity detected")
                logging.exception("Please try again with an established Internet Connection.")
                iw.delete()
                no_net_popup(win)
            else:
                missingdep = deb.missing_deps
                separator_string = " "
                missdep = separator_string.join(missingdep)
                logging.info("Starting Dependency Grab:")
                dep_grab = "apt-get --no-install-recommends install -y %s" %(missdep)
                esudo.eSudo(dep_grab, win, end_callback=dep_grab_cb)

        def compare(btn, pkg_info_en):
            debcompare = deb.compare_to_version_in_cache(use_installed=True)
            debcomparerepo = deb.compare_to_version_in_cache(use_installed=False)
            if debcompare == 1:
                pkg_info_en.entry_set("<b>Outdated:</> This version is lower than the version currently installed.")
            elif debcompare == 2:
                pkg_info_en.entry_set("<b>Same:</> The same version is already installed.")
            elif debcompare == 3:
                pkg_info_en.entry_set("<b>Newer:</> This version is higher than the version currently installed.")
            elif debcompare == 0:
                pkg_info_en.entry_set("<b>None:</> This application has not been installed.")
            else:
                pkg_info_en.entry_set("<b>Not found:</> A version installed or in the repository cannot be located for comparison.")

            if debcomparerepo == 1:
                pkg_info_en.entry_append("<ps><ps><b>Outdated:</> This version is lower than the version available in the repository.")
            elif debcomparerepo == 2:
                pkg_info_en.entry_append("<ps><ps><b>Same:</> This version is the same as the version available in the repository.")
            elif debcomparerepo == 3:
                pkg_info_en.entry_append("<ps><ps><b>Newer:</> This version is higher than the version available in the repository.")
            elif debcomparerepo == 0:
                pkg_info_en.entry_append("<ps><ps><b>None:</> This application cannot be located in the repository.")
            else:
                pkg_info_en.entry_set("<b>Not found:</> A version installed or in the repository cannot be located for comparison.")

        def checks(btn, pkg_info_en):
            if deb.check_breaks_existing_packages() == False:
                pkg_info_en.entry_set("<b>WARNING:</> Installing this package will <b>BREAK</> certain existing packages.")
            elif deb.check_conflicts() == False:
                pkg_info_en.entry_set("<b>WARNING:</> There are conflicting packages!")
                conflicting = deb.conflicts
                pkg_info_en.entry_append("<ps> %s" %conflicting)
            else:
                pkg_info_en.entry_set("<b>CLEAR:</> You are cleared to go. The selected file has passed ALL checks.")

        def depends(btn, pkg_info_en, bt):
            deb.depends_check()
            missingdep = deb.missing_deps
            separator_string = " , "
            missdep = separator_string.join(missingdep)
            pkg_info_en.entry_set("<b>Dependencies:</> %s<ps><ps><b>Missing Dependencies:</> " %pkg_dep)
            if missingdep == []:
                pkg_info_en.entry_append("None<ps>")
            else:
                bt.disabled_set(True)
                pkg_info_en.entry_append("%s<ps>" %missdep)
                bt = elm.Button(self.win)
                bt.text_set("Attempt to Install Missing Dependencies")
                bt.callback_clicked_add(dependency_grab, self.win)
                bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
                bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
                pkgbox.pack_end(bt)
                bt.show()

        def info(btn, pkg_info_en):
            pkg_info_en.entry_set("%s<ps>%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps>%s<ps><ps>%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps>%s" \
                            %(pkg_name, pkg_auth, pkg_ver, pkg_arch, pkg_size, pkg_sec, pkg_pri, pkg_desc, pkg_recc, pkg_conf, pkg_repl, pkg_prov, pkg_hp))
            #~ pkg_info_en.entry_set("%s<ps>" \
                            #~ %(filing))

        def files(btn, pkg_info_en):
            filestosort = deb.filelist
            separator_string = " , "
            filesinlist = separator_string.join(filestosort)
            pkg_info_en.entry_set("%s<ps>" %filesinlist)


        pkgbox = elm.Box(self.win)
        pkgbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)

        pkgfr = elm.Frame(self.win)
        pkgfr.text_set("Package Information:")
        pkgbox.pack_end(pkgfr)

        pkg_info_en = elm.Entry(self.win)
        pkg_info_en.line_wrap_set(2)
        pkg_info_en.input_panel_return_key_disabled = False
        pkg_info_en.size_hint_align_set(evas.EVAS_HINT_FILL, -1.0)
        pkg_info_en.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        pkg_info_en.editable_set(False)
        pkg_info_en.scrollable_set(True)
        pkg_info_en.entry_set("%s<ps>%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps>%s<ps><ps>%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps>%s" \
                            %(pkg_name, pkg_auth, pkg_ver, pkg_arch, pkg_size, pkg_sec, pkg_pri, pkg_desc, pkg_recc, pkg_conf, pkg_repl, pkg_prov, pkg_hp))
        #~ pkg_info_en.entry_set("%s<ps>" \
                            #~ %(filing))

        pkgbox.pack_end(pkg_info_en)
        pkg_info_en.show()

        pkgbox.show()
        pkgfr.show()

        iw = elm.InnerWindow(self.win)
        iw.content_set(pkgbox)
        iw.show()
        iw.activate()

        btnbox = elm.Box(self.win)
        btnbox.horizontal = True
        btnbox.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
        pkgbox.pack_end(btnbox)
        btnbox.show()

        bt = elm.Button(self.win)
        bt.text = "Info"
        bt.tooltip_text_set("View general information")
        bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
        bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
        bt.callback_clicked_add(info, pkg_info_en)
        btnbox.pack_end(bt)
        bt.show()

        bt = elm.Button(self.win)
        bt.text = "Compare"
        bt.tooltip_text_set("Compare version with the repo/installed versions")
        bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
        bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
        bt.callback_clicked_add(compare, pkg_info_en)
        btnbox.pack_end(bt)
        bt.show()

        bt = elm.Button(self.win)
        bt.text = "Checks"
        bt.tooltip_text_set("Check for conflicts/breaks if installed")
        bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
        bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
        bt.callback_clicked_add(checks, pkg_info_en)
        btnbox.pack_end(bt)
        bt.show()

        bt = elm.Button(self.win)
        bt.text = "Depends"
        bt.tooltip_text_set("Display dependencies and missing dependencies")
        bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
        bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
        bt.callback_clicked_add(depends, pkg_info_en, bt)
        btnbox.pack_end(bt)
        bt.show()

        bt = elm.Button(self.win)
        bt.text = "Files"
        bt.tooltip_text_set("View the file-listing")
        bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
        bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
        bt.callback_clicked_add(files, pkg_info_en)
        btnbox.pack_end(bt)
        bt.show()

        bt = elm.Button(self.win)
        bt.text_set("OK")
        bt.callback_clicked_add(iw_close, iw)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        pkgbox.pack_end(bt)
        bt.show()


#----Checks
    def check_file(self, fs, win):
        username = getpass.getuser()
        deb = self.file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        if mimetype == "application/x-debian-package":
            self.pkg_information(self)
            return
        elif self.file == "/home/%s" %username or self.file == "/home/%s/" %username:
            nofile_error_popup(win)
            return
        else:
            logging.info("Invalid file!")
            file_error_popup(win)
            return

    def check_file_install(self, bt, win):
        username = getpass.getuser()
        deb = self.file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        if mimetype == "application/x-debian-package":
            logging.info(self.file)
            install_deb = 'dpkg -i %s'%self.file
            esudo.eSudo(install_deb, win, end_callback=main_cb)
        elif self.file == "/home/%s" %username or self.file == "/home/%s/" %username:
            nofile_error_popup(win)
            return
        else:
            logging.info("Invalid file!")
            file_error_popup(win)
            return
