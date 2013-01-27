#!/usr/bin/env python
# encoding: utf-8
import os
import elementary as elm
import ecore
import evas
import time
import commands
#~ import urllib2
import mimetypes, pwd, PAM, getpass


"""eDeb

A deb package installer built on Python-EFL's.
By: AntCer (bodhidocs@gmail.com)

Started: January 17, 2013
"""

#M.V.P.
def buttons_main(obj, item=None):

#----Common
    def run_command(bnt, window, command):
        cmd = ecore.Exe(command)

    def destroy(obj):
        elm.exit()

    def popup_close(btn, popup):
        popup.delete()

    def iw_close(bt, iw):
        iw.delete()

#----Package Information
    def pkg_information(fs, bt, win):
        file = fs.selected_get()
        #~ pkg_info = commands.getoutput("dpkg -f %s" %file)
        pkg_name = commands.getoutput("dpkg -f %s | awk '/Package:/'" %file)
        pkg_ver  = commands.getoutput("dpkg -f %s | awk '/Version:/'" %file)
        pkg_sec  = commands.getoutput("dpkg -f %s | awk '/Section:/'" %file)
        pkg_pri  = commands.getoutput("dpkg -f %s | awk '/Priority:/'" %file)
        pkg_arch = commands.getoutput("dpkg -f %s | awk '/Architecture:/'" %file)
        pkg_dep  = commands.getoutput("dpkg -f %s | awk '/Depends:/'" %file)
        pkg_size = commands.getoutput("dpkg -f %s | awk '/Installed-Size:/'" %file)
        pkg_auth = commands.getoutput("dpkg -f %s | awk '/Maintainer:/'" %file)
        pkg_desc = commands.getoutput("dpkg -f %s | awk '/Description:/'" %file)

        pkgbox = elm.Box(win)
        pkgbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)

        pkgfr = elm.Frame(win)
        pkgfr.text_set("Package Information:")
        pkgfr.autocollapse_set(True)
        pkgbox.pack_end(pkgfr)

        pkg_info_en = elm.Entry(win)
        pkg_info_en.line_wrap_set(2)
        pkg_info_en.input_panel_return_key_disabled = False
        pkg_info_en.size_hint_align_set(evas.EVAS_HINT_FILL, -1.0)
        pkg_info_en.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        pkg_info_en.editable_set(False)
        pkg_info_en.scrollable_set(True)
        pkg_info_en.entry_set("%s<ps><ps>%s<ps>%s<ps>%s<ps>%s<ps><ps>%s<ps><ps>%s<ps>%s<ps><ps>%s<ps>" %(pkg_name, pkg_auth, pkg_ver, pkg_arch, pkg_size, pkg_sec, pkg_pri, pkg_dep, pkg_desc))
        #~ pkg_info_en.entry_set("%s<ps>" %pkg_info)
        pkgbox.pack_end(pkg_info_en)
        pkg_info_en.show()

        pkgbox.show()
        pkgfr.show()
        iw = elm.InnerWindow(win)
        iw.content_set(pkgbox)
        iw.show()

        bt = elm.Button(win)
        bt.text_set("OK")
        bt.callback_clicked_add(iw_close, iw)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        pkgbox.pack_end(bt)
        bt.show()

#----Dependency Grab
    #~ def dependency_grab(bt, en):
        #~ try:
            #~ con = urllib2.urlopen("http://www.google.com/")
            #~ str = en.entry_get()
            #~ print("Starting Dependency Grab:")
            #~ run_command(False, False, "echo %s | sudo -S apt-get -f install" %(str))
            #~ time.sleep(15)
            #~ print("Installation Fully Completed.")
            #~ iw.delete()
            #~ finished_popup(bt, win)
        #~ except:
            #~ print("No network activity detected")
            #~ print(" ")
            #~ print("Please try again with an established Internet Connection.")

#----Progress Bar
    my_progressbar_run = False
    my_progressbar_timer = None

    def my_progressbar_value_set(pb):
        progress = pb.value_get()
        if progress < 1.0:
            progress += 0.0123
        else:
            progress = 0.0
        pb.value_set(progress)
        if progress < 1.0:
            return ecore.ECORE_CALLBACK_RENEW
        global my_progressbar_run
        my_progressbar_run = False
        return ecore.ECORE_CALLBACK_CANCEL

    def my_progressbar_test_start(obj, *args, **kwargs):
        (pb) = args
        global my_progressbar_run
        global my_progressbar_timer
        if not my_progressbar_run:
            my_progressbar_timer = ecore.timer_add(0.1, my_progressbar_value_set,
                                                *args)
            my_progressbar_run = True


#----Popups
    def nofile_error_popup(bt, win):
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>No File Selected</><br><br>Please select an appropriate file candidate for installation."
        popup.timeout = 3.0
        popup.show()

    def file_error_popup(bt, win):
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Invalid File Format</><br><br>That is <em>not</> a .deb file!"
        popup.timeout = 3.0
        popup.show()

    def pw_error_popup(bt, win):#STILL DOES NOT DISPLAY
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Error</><br><br>Incorrect Password!<br>Please try again."
        popup.timeout = 3.0
        popup.show()

    #~ def install_progress_popup(bt, win):
        #~ popup1 = elm.Popup(win)
        #~ popup1.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        #~ popup1.text = "<b>Installation Progress</>"
        #~ popup.timeout = 10.0
        #~ pb = elm.Progressbar(win)
        #~ pb.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        #~ pb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        #~ pb.show()
        #~ popup1.part_content_set("progress", pb)
        #~ popup1.show()

    def finished_popup(bt, win):
        popup = elm.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Installation Finished!</>"
        bt = elm.Button(win)
        bt.text = "Close"
        bt.callback_clicked_add(popup_close, popup)
        popup.part_content_set("button1", bt)
        popup.show()

    #~ def dependency_popup(bt, win):
        #~ popup = elm.Popup(win)
        #~ popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        #~ popup.text = "<b>Urgent:</><br>Installation Semi-Finished.<br>All dependencies were not met.<br>Click <b>Grab</> to attempt to install all dependencies."
        #~ bt = elm.Button(win)
        #~ bt.text = "Grab"
        #~ bt.callback_clicked_add(dependency_grab, popup)
        #~ popup.part_content_set("button1", bt)
        #~ popup.show()

#----Checks
    def file_selected(fs, bt, win):
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

    def file_selected2(bt, win):
        username = getpass.getuser()
        file = fs.selected_get()
        deb = file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        if mimetype == "application/x-debian-package":
            print(file)
            esudo(None)
        elif file == "/home/%s" %username or file == "/home/%s/" %username:
            nofile_error_popup(bt, win)
            return
        else:
            print("Invalid file!")
            file_error_popup(bt, win)
            return
            
    def file_selected3(bt, win):
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

#----eSudo
    def esudo(win1):

#--------Password Checker
        def password_check(bt, en):

#------------Sets Password
            def pam_conv(auth, query_list, userData):
                str = en.entry_get()
                resp = []
                for i in range(len(query_list)):
                    query, type = query_list[i]
                    if type == PAM.PAM_PROMPT_ECHO_ON or type == PAM.PAM_PROMPT_ECHO_OFF:
                        val = str
                        resp.append((val, 0))
                    elif type == PAM.PAM_PROMPT_ERROR_MSG or type == PAM.PAM_PROMPT_TEXT_INFO:
                        resp.append(('', 0))
                    else:
                        return None
                return resp

#------------Username & Service To Use
            username = getpass.getuser()
            user = username
            service = 'passwd'

#------------Start Password Test
            auth = PAM.pam()
            auth.start(service)
            if user == username:
                auth.set_item(PAM.PAM_USER, user)
            auth.set_item(PAM.PAM_CONV, pam_conv)
            try:
                auth.authenticate()
                auth.acct_mgmt()
            except PAM.error, resp:
                pw_error_popup(bt, win)
                en.entry_set("")
                print("Invalid password! Please try again.")
                return
            except:
                print("Internal error! File bug report.")
            else:
                esudo_ok(bt, en)

#--------eSudo Cancel Button
        def esudo_cancel(bt, en):
            en.entry_set("")
            iw.delete()

#--------eSudo OK Button
        def esudo_ok(bt, en):
            #~ install_progress_popup(bt, win)
            file = fs.selected_get()
            str = en.entry_get()
            print("Starting installation:")
            run_command(False, False, "echo %s | sudo -S dpkg -i %s" %(str, file))
            time.sleep(20)
            print("Installation Finished.")
            iw.delete()
            finished_popup(bt, win)

#--------eSudo Window
        bz = elm.Box(win)
        bz.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)

        fr = elm.Frame(win)
        fr.text_set("eSudo")
        bz.pack_end(fr)

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        bz.pack_end(sep)
        sep.show()

        bz1 = elm.Box(win)
        bz.pack_end(bz1)
        bz1.show()

        lb = elm.Label(win)
        lb.text = "<b>Password:</b>"
        lb.size_hint_align = (0.0, 0.5)
        bz1.pack_end(lb)
        lb.show()

        en = elm.Entry(win)
        en.single_line = True
        en.line_wrap_set(False)
        en.input_panel_return_key_disabled = False
        en.password = True
        en.size_hint_weight_set(0.5, 0.5)
        en.size_hint_align_set(0.5, 0.5)
        bz1.pack_end(en)
        en.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        bz.pack_end(sep)
        sep.show()

        bz.show()
        fr.show()

        bx2 = elm.Box(win)
        bx2.horizontal_set(True)
        bx2.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bx2.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        bt = elm.Button(win)
        bt.text_set("Cancel")
        bt.callback_clicked_add(esudo_cancel, en)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bx2.pack_end(bt)
        bt.show()

        bt = elm.Button(win)
        bt.text_set("OK")
        bt.callback_clicked_add(password_check, en)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bx2.pack_end(bt)
        bt.show()

        bz.pack_end(bx2)
        bx2.show()

        en.focus_set(True)
        iw = elm.InnerWindow(win)
        iw.content_set(bz)
        iw.show()
        iw.activate()

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
    #~ fsbox.horizontal_set(True)
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
    fs.callback_file_chosen_add(file_selected, win)
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
    bt.callback_clicked_add(file_selected2, win)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    btbox.pack_end(bt)
    bt.show()

    bt = elm.Button(win)
    bt.text_set("Package Info")
    bt.callback_clicked_add(file_selected3, win)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    btbox.pack_end(bt)
    bt.show()

    sep = elm.Separator(win)
    sep.horizontal_set(True)
    vbox.pack_end(sep)
    sep.show()

    win.resize_object_add(vbox)
    win.resize(450, 150)
    win.show()

#----- Main -{{{-
if __name__ == "__main__":
    elm.init()

    buttons_main(None)

    elm.run()
    elm.shutdown()
# }}}
# vim:foldmethod=marker
