# This file is part of OpenSnitch.
#
# Copyright(c) 2017 Simone Margaritelli
# evilsocket@gmail.com
# http://www.evilsocket.net
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 2 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from opensnitch.rule import Rule
from PyQt4 import QtCore, QtGui, uic
import sys, os

# TODO: Implement tray icon and menu.
# TODO: Implement rules editor.

RESOURCES_PATH = "%s/resources/" % os.path.dirname(sys.modules[__name__].__file__)
DIALOG_UI_PATH = "%s/dialog.ui" % RESOURCES_PATH

dialog_ui = uic.loadUiType(DIALOG_UI_PATH)[0]

class QtApp:
    def __init__(self):
        pass

    def run(self):
        self.app = QtGui.QApplication([])

    def prompt_user( self, connection ):
        dialog = OpenSnitchDialog( connection )
        dialog.show()
        self.app.exec_()
        return dialog.result

class OpenSnitchDialog( QtGui.QMainWindow, dialog_ui ):
    DEFAULT_RESULT = ( Rule.ONCE, Rule.ACCEPT, False )

    def __init__( self, connection, parent=None ):
        self.connection = connection
        QtGui.QMainWindow.__init__( self, parent )
        self.setupUi(self)
        self.init_widgets()
        self.start_listeners()
        self.setup_labels()
        self.setup_extra()
        self.result = OpenSnitchDialog.DEFAULT_RESULT

    def setup_labels(self):
        self.app_name_label.setText( self.connection.app.name )

        message = "%s (%s) wants to connect to %s on %s port %s%s" % ( \
                    self.connection.app.name,
                    self.connection.app_path,
                    self.connection.hostname,
                    self.connection.proto.upper(),
                    self.connection.dst_port,
                    " (%s)" % self.connection.service if self.connection.service is not None else '' )
        self.message_label.setText( message )

    def init_widgets(self):
        self.app_name_label = self.findChild( QtGui.QLabel, "appNameLabel" )
        self.message_label = self.findChild( QtGui.QLabel, "messageLabel" )
        self.action_combo_box = self.findChild( QtGui.QComboBox, "actionComboBox" )
        self.allow_button = self.findChild( QtGui.QPushButton, "allowButton" )
        self.deny_button = self.findChild( QtGui.QPushButton, "denyButton" )
        self.whitelist_button = self.findChild( QtGui.QPushButton, "whitelistButton" )
        self.block_button = self.findChild( QtGui.QPushButton, "blockButton" )
        self.logo_graphics_view = self.findChild( QtGui.QGraphicsView, "logoGraphicsView" )

    def start_listeners(self):
        self.allow_button.clicked.connect( self._allow_action )
        self.deny_button.clicked.connect( self._deny_action )
        self.whitelist_button.clicked.connect( self._whitelist_action )
        self.block_button.clicked.connect( self._block_action )
        self.action_combo_box.currentIndexChanged[str].connect ( self._action_changed )

    def setup_extra(self):
        self._action_changed()

    def _action_changed(self):
        s_option = self.action_combo_box.currentText()
        if s_option == "Until Quit" or s_option == "Forever":
          self.whitelist_button.show()
          self.block_button.show()
        elif s_option == "Once":
          self.whitelist_button.hide()
          self.block_button.hide()

    def _allow_action(self):
        self._action( Rule.ACCEPT, False )

    def _deny_action(self):
        self._action( Rule.DROP, False )

    def _whitelist_action(self):
        self._action( Rule.ACCEPT, True )

    def _block_action(self):
        self._action( Rule.DROP, True )

    def _action( self, verdict, apply_to_all=False ):
        s_option = self.action_combo_box.currentText()

        if s_option == "Once":
          option = Rule.ONCE
        elif s_option == "Until Quit":
          option = Rule.UNTIL_QUIT
        elif s_option == "Forever":
          option = Rule.FOREVER

        self.result = ( option, verdict, apply_to_all )
        self.close()
