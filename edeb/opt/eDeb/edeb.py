#!/usr/bin/env python
# encoding: utf-8
import os
import elementary as elm
import apt.debfile as debianfile
import ecore
import evas
import esudo

import urllib2
import mimetypes
import getpass, commands


"""eDeb

A deb package installer built on Python-EFL's.
By: AntCer (bodhidocs@gmail.com)

Started: January 17, 2013
"""




def buttons_main(obj, item=None):

#----Common
    def destroy(obj):
        elm.exit()

    def popup_close(btn, popup):
        popup.delete()

    def iw_close(bt, iw):
        iw.delete()

    def dep_grab_cb(exit_code):
        if exit_code == 0:
            print("Successfully Grabbed Dependencies.")
            finished_dep_install_popup(win)
        else:
            print("Something went wrong while installing dependencies.")
    def main_cb(exit_code):
        if exit_code == 0:
            print("Installation Completed!")
            finished_popup(win)
        else:
            print("Something went wrong. Likely, dependencies that weren't met before attempting installation.")
            dependency_popup(win)
    def dep_cb(exit_code):
        if exit_code == 0:
            print("Successfully Grabbed Dependencies & Completed Installation.")
            finished_popup(win)
        else:
            print("Something went wrong while attempting to complete installation.")

#----Dependency Completion
    def dependency_comp(bt, win, iw):
        iw.delete()
        try:
            con = urllib2.urlopen("http://www.google.com/")
        except:
            print("No network activity detected")
            print(" ")
            print("Please try again with an established Internet Connection.")
            no_net_popup(win)
        else:
            print("Starting attempt to fulfill dependencies:")
            dep_comp = "apt-get -f install -y"
            esudo.eSudo(dep_comp, win, end_callback=dep_cb)

#----Package Info
    def pkg_information(fs, bt, win):
        file = fs.selected_get()
        deb = debianfile.DebPackage(file, cache=None)
        pkg_name = commands.getoutput("dpkg -f %s | awk '/Package:/'" %file)
        pkg_ver  = commands.getoutput("dpkg -f %s | awk '/Version:/'" %file)
        pkg_sec  = commands.getoutput("dpkg -f %s | awk '/Section:/'" %file)
        pkg_pri  = commands.getoutput("dpkg -f %s | awk '/Priority:/'" %file)
        pkg_dep  = commands.getoutput("dpkg -f %s | sed 's/<</less than/' | awk '/Depends:/' | sed 's/Depends:/ /' | sed 's/Pre-/ /'" %file)
        pkg_arch = commands.getoutput("dpkg -f %s | awk '/Architecture:/'" %file)
        pkg_size = commands.getoutput("dpkg -f %s | awk '/Installed-Size:/'" %file)
        pkg_auth = commands.getoutput("dpkg -f %s | awk '/Maintainer:/'" %file)
        pkg_desc = commands.getoutput("dpkg -f %s | awk '/Description:/'" %file)
        pkg_recc = commands.getoutput("dpkg -f %s | awk '/Recommends:/'" %file)
        pkg_conf = commands.getoutput("dpkg -f %s | awk '/Conflicts:/'" %file)
        pkg_repl = commands.getoutput("dpkg -f %s | awk '/Replaces:/'" %file)
        pkg_prov = commands.getoutput("dpkg -f %s | awk '/Provides:/'" %file)
        pkg_hp   = commands.getoutput("dpkg -f %s | awk '/Homepage:/'" %file)

        def dependency_grab(bt, win):
            try:
                con = urllib2.urlopen("http://www.google.com/")
            except:
                print("No network activity detected")
                print(" ")
                print("Please try again with an established Internet Connection.")
                iw.delete()
                no_net_popup(win)
            else:
                missingdep = deb.missing_deps
                separator_string = " "
                missdep = separator_string.join(missingdep)
                print("Starting Dependency Grab:")
                dep_grab = "apt-get --no-install-recommends install -y %s" %(missdep)
                esudo.eSudo(dep_grab, win, end_callback=dep_grab_cb)

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
            missingdep = deb.missing_deps
            separator_string = " , "
            missdep = separator_string.join(missingdep)
            pkg_info_en.entry_set("<b>Dependencies:</> %s<ps><ps><b>Missing Dependencies:</> " %pkg_dep)
            if missingdep == []:
                pkg_info_en.entry_append("None<ps>")
            else:
                bt.disabled_set(True)
                pkg_info_en.entry_append("%s<ps>" %missdep)
                bt = elm.Button(win)
                bt.text_set("Attempt to Install Missing Dependencies")
                bt.callback_clicked_add(dependency_grab, win)
                bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
                bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
                pkgbox.pack_end(bt)
                bt.show()

        def info(btn, pkg_info_en):
            pkg_info_en.entry_set("%s<ps>%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps>%s<ps><ps>%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps>%s" \
                            %(pkg_name, pkg_auth, pkg_ver, pkg_arch, pkg_size, pkg_sec, pkg_pri, pkg_desc, pkg_recc, pkg_conf, pkg_repl, pkg_prov, pkg_hp))

        def files(btn, pkg_info_en):
            filestosort = deb.filelist
            separator_string = " , "
            filesinlist = separator_string.join(filestosort)
            pkg_info_en.entry_set("%s<ps>" %filesinlist)

        if deb.check() ==  False:
            not_installable_popup(win)
        else:
            pkgbox = elm.Box(win)
            pkgbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)

            pkgfr = elm.Frame(win)
            pkgfr.text_set("Package Information:")
            pkgbox.pack_end(pkgfr)

            pkg_info_en = elm.Entry(win)
            pkg_info_en.line_wrap_set(2)
            pkg_info_en.input_panel_return_key_disabled = False
            pkg_info_en.size_hint_align_set(evas.EVAS_HINT_FILL, -1.0)
            pkg_info_en.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            pkg_info_en.editable_set(False)
            pkg_info_en.scrollable_set(True)
            pkg_info_en.entry_set("%s<ps>%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps>%s<ps><ps>%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps>%s" \
                                %(pkg_name, pkg_auth, pkg_ver, pkg_arch, pkg_size, pkg_sec, pkg_pri, pkg_desc, pkg_recc, pkg_conf, pkg_repl, pkg_prov, pkg_hp))

            pkgbox.pack_end(pkg_info_en)
            pkg_info_en.show()

            pkgbox.show()
            pkgfr.show()

            iw = elm.InnerWindow(win)
            iw.content_set(pkgbox)
            iw.show()
            iw.activate()

            btnbox = elm.Box(win)
            btnbox.horizontal = True
            btnbox.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
            pkgbox.pack_end(btnbox)
            btnbox.show()

            bt = elm.Button(win)
            bt.text = "Info"
            bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
            bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
            bt.callback_clicked_add(info, pkg_info_en)
            btnbox.pack_end(bt)
            bt.show()

            bt = elm.Button(win)
            bt.text = "Checks"
            bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
            bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
            bt.callback_clicked_add(checks, pkg_info_en)
            btnbox.pack_end(bt)
            bt.show()

            bt = elm.Button(win)
            bt.text = "Depends"
            bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
            bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
            bt.callback_clicked_add(depends, pkg_info_en, bt)
            btnbox.pack_end(bt)
            bt.show()

            bt = elm.Button(win)
            bt.text = "Files"
            bt.size_hint_align = (evas.EVAS_HINT_FILL, 0.0)
            bt.size_hint_weight = (evas.EVAS_HINT_EXPAND, 0.0)
            bt.callback_clicked_add(files, pkg_info_en)
            btnbox.pack_end(bt)
            bt.show()

            bt = elm.Button(win)
            bt.text_set("OK")
            bt.callback_clicked_add(iw_close, iw)
            bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
            bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
            pkgbox.pack_end(bt)
            bt.show()

#----Popups
    def no_net_popup(win):
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Error</><br><br>No internet access.<br>Please try again when connected to internet."
        popup.timeout = 2.0
        popup.show()

    def nofile_error_popup(bt, win):
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>No File Selected</><br><br>Please select an appropriate file candidate for installation."
        popup.timeout = 2.0
        popup.show()

    def file_error_popup(bt, win):
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Invalid File Format</><br><br>That is <em>not</> a .deb file!"
        popup.timeout = 2.0
        popup.show()

    def finished_dep_install_popup(win):
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Successful!</b><br><br>Missing dependencies successfully installed."
        popup.timeout = 2.0
        popup.show()

    def not_installable_popup(win):
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Error</b><br><br>This file has failed initial check. It cannot be installed.<br>This can be caused by a previously broken installation. Try running 'sudo apt-get install -f' in a terminal."
        popup.timeout = 2.0
        popup.show()

    def dependency_popup(win):
        pkgbox = elm.Box(win)
        pkgbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)

        pkgfr = elm.Frame(win)
        pkgfr.text_set("Urgent!")
        pkgbox.pack_end(pkgfr)

        lb = elm.Label(win)
        lb.line_wrap_set(2)
        lb.wrap_width_set(280)
        lb.text = "Installation Semi-Finished. All dependencies were not met.<ps><ps>Click <b>Grab</> to attempt to grab the missing dependencies and complete the installation."
        lb.size_hint_align = (0.0, 0.5)
        lb.show()
        pkgfr.content = lb

        pkgbox.show()
        pkgfr.show()

        iw = elm.InnerWindow(win)
        iw.content_set(pkgbox)
        iw.show()
        iw.activate()

        bt = elm.Button(win)
        bt.text = ("Grab")
        bt.callback_clicked_add(dependency_comp, win, iw)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        pkgbox.pack_end(bt)
        bt.show()

    def finished_popup(win):
        pkgbox = elm.Box(win)
        pkgbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)

        pkgfr = elm.Frame(win)
        pkgfr.text_set("Installation Finished!")
        pkgbox.pack_end(pkgfr)

        lb = elm.Label(win)
        lb.line_wrap_set(2)
        lb.wrap_width_set(280)
        lb.text = "The installation was successful."
        lb.size_hint_align = (0.0, 0.5)
        lb.show()
        pkgfr.content = lb

        pkgbox.show()
        pkgfr.show()

        iw = elm.InnerWindow(win)
        iw.content_set(pkgbox)
        iw.show()
        iw.activate()

        bt = elm.Button(win)
        bt.text_set("OK")
        bt.callback_clicked_add(iw_close, iw)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        pkgbox.pack_end(bt)
        bt.show()

        pkgbox.pack_end(pkgbox2)

#----Chcks
    def check_file_initial(fs, bt, win):
        username = getpass.getuser()
        file = fs.selected_get()
        deb = file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        if mimetype == "application/x-debian-package":
            pkg_information(fs, bt, win)
            return
        elif file == "/home/%s" %username or file == "/home/%s/" %username:
            return
        else:
            print("Invalid file!")
            file_error_popup(bt, win)
            return

    def check_file_install(bt, win):
        username = getpass.getuser()
        file = fs.selected_get()
        debfile = debianfile.DebPackage(file, cache=None)
        deb = file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        if mimetype == "application/x-debian-package":
            if debfile.check() ==  False:
                not_installable_popup(win)
                return
            else:
                print(file)
                install_deb = 'dpkg -i %s'%file
                esudo.eSudo(install_deb, win, end_callback=main_cb)
        elif file == "/home/%s" %username or file == "/home/%s/" %username:
            nofile_error_popup(bt, win)
            return
        else:
            print("Invalid file!")
            file_error_popup(bt, win)
            return

    def check_file_pkginfo(bt, win):
        username = getpass.getuser()
        file = fs.selected_get()
        deb = file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        if mimetype == "application/x-debian-package":
            pkg_information(fs, bt, win)
            return
        elif file == "/home/%s" %username or file == "/home/%s/" %username:
            nofile_error_popup(bt, win)
            return
        else:
            print("Invalid file!")
            file_error_popup(bt, win)
            return

#----Main Window
    win = elm.StandardWindow("edeb", "eDeb")
    win.callback_delete_request_add(lambda o: elm.exit())

    vbox = elm.Box(win)
    vbox.padding_set(5, 20)
    vbox.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    vbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    vbox.show()

    sep = elm.Separator(win)
    sep.horizontal_set(True)
    vbox.pack_end(sep)
    sep.show()

    fsbox = elm.Box(win)
    fsbox.size_hint_align_set(evas.EVAS_HINT_FILL, 0.0)
    fsbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    vbox.pack_end(fsbox)
    fsbox.show()

    fs = elm.FileselectorEntry(win)
    fs.text_set("Select .deb file")
    fs.window_title_set("Select a .deb file:")
    fs.expandable_set(False)
    fs.inwin_mode_set(False)
    fs.path_set(os.getenv("HOME"))
    fs.callback_file_chosen_add(check_file_initial, win)
    fs.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fs.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fsbox.pack_end(fs)
    fs.show()

    sep = elm.Separator(win)
    sep.horizontal_set(True)
    vbox.pack_end(sep)
    sep.show()

    btbox = elm.Box(win)
    btbox.size_hint_align_set(evas.EVAS_HINT_FILL, -1.0)
    btbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    vbox.pack_end(btbox)
    btbox.show()

    bt = elm.Button(win)
    bt.text_set("Install")
    bt.callback_clicked_add(check_file_install, win)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    btbox.pack_end(bt)
    bt.show()

    bt = elm.Button(win)
    bt.text_set("Package Info")
    bt.callback_clicked_add(check_file_pkginfo, win)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    btbox.pack_end(bt)
    bt.show()

    sep = elm.Separator(win)
    sep.horizontal_set(True)
    vbox.pack_end(sep)
    sep.show()

    win.resize_object_add(vbox)
    win.resize(425, 200)
    win.show()

#----- Main -{{{-
if __name__ == "__main__":
    elm.init()

    buttons_main(None)

    elm.run()
    elm.shutdown()
# }}}
# vim:foldmethod=marker
