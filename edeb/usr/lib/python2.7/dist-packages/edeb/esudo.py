"""eSudo - a GUI sudo tool in python and elementary

Base code by AntCer, polished by Jeff Hoogland
Something actually useful done by Kai Huuhko <kai.huuhko@gmail.com>
"""

import os
import getpass
import logging
logging.basicConfig(level=logging.DEBUG)

import PAM

import ecore
import evas
import elementary

#----Popups
def pw_error_popup(bt, win):
    popup = elementary.Popup(win)
    popup.size_hint_weight = evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND
    popup.text = "<b>Error</><br><br>Incorrect Password!<br>Please try again."
    popup.timeout = 3.0
    popup.show()

#----eSudo
class eSudo(object):
    def __init__( self, command=None, window=None, start_callback=None, end_callback=None, *args, **kwargs ):

        self.mainWindow = self.win = win = window
        self.Window = False

        self.cmd = command
        self.start_cb = start_callback if callable(start_callback) else None
        self.end_cb = end_callback if callable(end_callback) else None

        self.args = args
        self.kwargs = kwargs

#--------eSudo Window

        bz = elementary.Box(win)
        bz.size_hint_weight = evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND

        fr = elementary.Frame(win)
        bz.pack_end(fr)

        fr.text_set("Command:")
        self.cmdline = cmdline = elementary.Label(win)
        cmdline.line_wrap_set(2)
        cmdline.wrap_width_set(280)
        cmdline.text = "<i>%s</i>"%self.cmd
        cmdline.size_hint_align = (0.0, 0.5)

        cmdline.show()
        fr.content = cmdline

        sep = elementary.Separator(win)
        sep.horizontal = True
        bz.pack_end(sep)
        sep.show()

        bz1 = elementary.Box(win)
        bz.pack_end(bz1)
        bz1.show()

        lb = elementary.Label(win)
        lb.text = "<b>Password:</b>"
        lb.size_hint_align = 0.0, 0.5
        bz1.pack_end(lb)
        lb.show()

        en = elementary.Entry(win)
        en.elm_event_callback_add(self.pw_entry_event)
        en.single_line = True
        en.password = True
        en.size_hint_weight = 0.5, 0.5
        en.size_hint_align = 0.5, 0.5
        bz1.pack_end(en)
        en.show()

        sep = elementary.Separator(win)
        sep.horizontal = True
        bz.pack_end(sep)
        sep.show()

        bz.show()
        fr.show()

        bz2 = elementary.Box(win)
        bz2.horizontal = True
        bz2.size_hint_weight = evas.EVAS_HINT_EXPAND, 0.0
        bz2.size_hint_align = evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL

        bt = elementary.Button(win)
        bt.text = "Cancel"
        bt.callback_clicked_add(self.esudo_cancel, en)
        bt.size_hint_align = evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL
        bt.size_hint_weight = evas.EVAS_HINT_EXPAND, 0.0
        bz2.pack_end(bt)
        bt.show()

        bt = elementary.Button(win)
        bt.text = "OK"
        bt.callback_clicked_add(self.password_check, en)
        bt.size_hint_align = evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL
        bt.size_hint_weight = evas.EVAS_HINT_EXPAND, 0.0
        bz2.pack_end(bt)
        bt.show()

        bz.pack_end(bz2)
        bz2.show()

        en.focus = True
        self.iw = iw = elementary.InnerWindow(win)
        iw.content = bz
        iw.show()
        iw.activate()

    def pw_entry_event(self, obj, entry, event_type, event, *args):
        if event_type == evas.EVAS_CALLBACK_KEY_UP:
            if event.keyname == "Return":
                self.password_check(None, entry)
            elif event.keyname == "Escape":
                self.close()

        return True

#--------Password Checker
    def password_check(self, bt, en):

#------------Sets Password
        def pam_conv(auth, query_list, userData):
            password = en.entry
            resp = []
            for i in range(len(query_list)):
                query, type = query_list[i]
                if type == PAM.PAM_PROMPT_ECHO_ON or type == PAM.PAM_PROMPT_ECHO_OFF:
                    val = password
                    resp.append((val, 0))
                elif type == PAM.PAM_PROMPT_ERROR_MSG or type == PAM.PAM_PROMPT_TEXT_INFO:
                    resp.append(('', 0))
                else:
                    return None
            return resp

#------------Username & Service To Use
        username = getpass.getuser()
        service = 'sudo'

#------------Start Password Test
        auth = PAM.pam()
        auth.start(service)
        auth.set_item(PAM.PAM_USER, username)
        auth.set_item(PAM.PAM_CONV, pam_conv)
        try:
            auth.authenticate()
            auth.acct_mgmt()
        except PAM.error, resp:
            pw_error_popup(bt, self.mainWindow)
            en.entry = ""
            en.focus = True
            logging.info("Invalid password! Please try again.")
            return
        except:
            logging.exception("Internal error! File bug report.")
        else:
            self.esudo_ok(bt, en)

#--------eSudo Cancel Button
    def esudo_cancel(self, bt, en):
        logging.info("Command terminated before attempt was initiated.")
        en.entry = ""
        self.close()

    def close(self):
        self.iw.delete()

#--------eSudo OK Button
    def esudo_ok(self, bt, en):
        password = en.entry_get()
        logging.info("Starting %s" % self.cmd)
        self.run_command("sudo -S %s" % (self.cmd), password)

    def run_command(self, command, password):
        self.cmd_exe = cmd = ecore.Exe(command, ecore.ECORE_EXE_PIPE_READ|ecore.ECORE_EXE_PIPE_ERROR|ecore.ECORE_EXE_PIPE_WRITE)
        cmd.on_add_event_add(self.command_started)
        cmd.on_data_event_add(self.received_data, password)
        cmd.on_error_event_add(self.received_error, password)
        cmd.on_del_event_add(self.command_done)

    def command_started(self, cmd, event, *args, **kwargs):
        logging.debug("Command started")
        logging.debug(cmd)
        if self.start_cb:
            try:
                self.start_cb(self.iw, self.mainWindow, *self.args, **self.kwargs)
            except:
                logging.exception("Exception while running start_cb")

    def received_data(self, cmd, event, *args, **kwargs):
        logging.debug("Received data")
        logging.debug(event.data)

    def received_error(self, cmd, event, *args, **kwargs):
        logging.debug("Received error")
        logging.debug(event.data)

        password = args[0]
        cmd.send(str(password)+"\n")

    def command_done(self, cmd, event, *args, **kwargs):
        logging.debug("Command done")
        if self.end_cb:
            try:
                self.end_cb(event.exit_code, self.mainWindow, *self.args, **self.kwargs)
            except:
                logging.exception("Exception while running end_cb")
