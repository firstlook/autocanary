"""
AutoCanary | https://firstlook.org/code/autocanary
Copyright (c) 2015 First Look Media

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys, datetime, platform
from PyQt5 import QtCore, QtWidgets

from .gnupg import GnuPG
from .headlines import Headlines
from .settings import Settings
from .output_dialog import OutputDialog

from . import common

class AutoCanaryGui(QtWidgets.QMainWindow):

    def __init__(self, app, gpg, headlines):
        super(AutoCanaryGui, self).__init__()

        self.app = app
        self.gpg = gpg
        self.headlines = headlines
        self.settings = Settings()
        self.setWindowTitle('AutoCanary')
        self.setWindowIcon(common.get_icon())

        # frequency, year
        self.date_col1_layout = QtWidgets.QVBoxLayout()

        self.frequency_layout = QtWidgets.QHBoxLayout()
        self.frequency_label = QtWidgets.QLabel('Frequency')
        self.frequency = QtWidgets.QComboBox()
        frequency_options = ["Weekly", "Monthly", "Quarterly", "Semiannually"]
        for option in frequency_options:
            self.frequency.addItem(option)
        option = self.settings.get_frequency()
        if option in frequency_options:
            self.frequency.setCurrentIndex(frequency_options.index(option))
        self.frequency_layout.addWidget(self.frequency_label)
        self.frequency_layout.addWidget(self.frequency)
        self.frequency.activated.connect(self.update_date)

        self.year_layout = QtWidgets.QHBoxLayout()
        self.year_label = QtWidgets.QLabel('Year')
        self.year = QtWidgets.QComboBox()
        y = datetime.date.today().year
        year_options = [str(y-1), str(y), str(y+1)]
        for option in year_options:
            self.year.addItem(option)
        option = self.settings.get_year()
        if option in year_options:
            self.year.setCurrentIndex(year_options.index(option))
        self.year_layout.addWidget(self.year_label)
        self.year_layout.addWidget(self.year)
        self.year.activated.connect(self.update_date)

        # weekly dropdown
        self.weekly_layout = QtWidgets.QHBoxLayout()
        self.weekly_label = QtWidgets.QLabel('Week')
        self.weekly_dropdown = QtWidgets.QComboBox()
        self.weekly_layout.addWidget(self.weekly_label)
        self.weekly_layout.addWidget(self.weekly_dropdown)

        # monthly dropdown
        self.monthly_layout = QtWidgets.QHBoxLayout()
        self.monthly_label = QtWidgets.QLabel('Month')
        self.monthly_dropdown = QtWidgets.QComboBox()
        monthly_options = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        for option in monthly_options:
            self.monthly_dropdown.addItem(option)
        self.monthly_layout.addWidget(self.monthly_label)
        self.monthly_layout.addWidget(self.monthly_dropdown)

        # quarterly radio buttons
        self.quarterly_layout = QtWidgets.QHBoxLayout()
        self.quarterly_label = QtWidgets.QLabel('Quarter')
        self.quarterly_q1 = QtWidgets.QRadioButton("")
        self.quarterly_q2 = QtWidgets.QRadioButton("")
        self.quarterly_q3 = QtWidgets.QRadioButton("")
        self.quarterly_q4 = QtWidgets.QRadioButton("")
        self.quarterly_layout.addWidget(self.quarterly_label)
        self.quarterly_layout.addWidget(self.quarterly_q1)
        self.quarterly_layout.addWidget(self.quarterly_q2)
        self.quarterly_layout.addWidget(self.quarterly_q3)
        self.quarterly_layout.addWidget(self.quarterly_q4)

        # semiannual radio buttons
        self.semiannually_layout = QtWidgets.QHBoxLayout()
        self.semiannually_label = QtWidgets.QLabel('Semester')
        self.semiannually_q12 = QtWidgets.QRadioButton("")
        self.semiannually_q34 = QtWidgets.QRadioButton("")
        self.semiannually_layout.addWidget(self.semiannually_label)
        self.semiannually_layout.addWidget(self.semiannually_q12)
        self.semiannually_layout.addWidget(self.semiannually_q34)

        # date layout
        self.date_layout = QtWidgets.QVBoxLayout()
        self.date_layout.addLayout(self.frequency_layout)
        self.date_layout.addLayout(self.year_layout)
        self.date_layout.addLayout(self.weekly_layout)
        self.date_layout.addLayout(self.monthly_layout)
        self.date_layout.addLayout(self.quarterly_layout)
        self.date_layout.addLayout(self.semiannually_layout)

        # status
        self.status_layout = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel('Status')
        self.status = QtWidgets.QComboBox()
        status_options = ["All good", "It's complicated"]
        for option in status_options:
            self.status.addItem(option)
        option = self.settings.get_status()
        if option in status_options:
            self.status.setCurrentIndex(status_options.index(option))
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status)

        # canary text box
        self.textbox = QtWidgets.QTextEdit()
        self.textbox.setText(self.settings.get_text())

        # headlines controls: [checkbox, button, button].
        self.headlines_controls = self.get_headlines_controls()

        # key selection
        seckeys = gpg.seckeys_list()
        self.key_selection = QtWidgets.QComboBox()
        for seckey in seckeys:
            uid = seckey['uid']
            if len(uid) >= 53:
                uid = '{0}...'.format(uid[:50])
            fp = seckey['fp'][-8:]
            text = '{0} [{1}]'.format(uid, fp)
            self.key_selection.addItem(text)
        fp = self.settings.get_fp()
        if fp:
            key_i = 0
            for i, seckey in enumerate(seckeys):
                if seckey['fp'] == fp:
                    key_i = i
            self.key_selection.setCurrentIndex(key_i)

        # buttons
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.sign_save_button = QtWidgets.QPushButton('Save and Sign')
        self.sign_save_button.clicked.connect(self.sign_save_clicked)
        self.sign_once = QtWidgets.QPushButton('One-Time Sign')
        self.sign_once.clicked.connect(self.sign_once_clicked)
        self.buttons_layout.addWidget(self.sign_save_button)
        self.buttons_layout.addWidget(self.sign_once)

        # headlines controls.
        self.headline_controls_layout = QtWidgets.QHBoxLayout()
        for hl_control in self.headlines_controls:
            self.headline_controls_layout.addWidget(hl_control)

        # layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.date_layout)
        layout.addLayout(self.status_layout)
        layout.addWidget(self.textbox)
        layout.addLayout(self.headline_controls_layout)
        layout.addWidget(self.key_selection)
        layout.addLayout(self.buttons_layout)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.update_date()
        self.show()

    def update_date(self):
        frequency = self.frequency.currentText()
        year = self.year.currentText()

        if frequency == 'Weekly':
            self.weekly_label.show()
            self.weekly_dropdown.show()

            # regenerate the weekly dropdown options based on the current year
            self.weekly_dropdown.clear()

            one_week = datetime.timedelta(7)
            cur_date = datetime.datetime(int(year), 1, 1)

            def get_monday_of_week(d):
                days_past = d.isoweekday() - 1
                d = d - datetime.timedelta(days_past)
                return d

            def get_sunday_of_week(d):
                days_future = 7 - d.isoweekday()
                d = d + datetime.timedelta(days_future)
                return d

            while cur_date.year == int(year):
                date_str = ''

                # figure out the start and end dates of the week
                monday_date = get_monday_of_week(cur_date)
                sunday_date = get_sunday_of_week(cur_date)

                if sunday_date.year != int(year):
                    break

                date_str += '{0} to {1}'.format(
                    monday_date.strftime('%b %d'),
                    sunday_date.strftime('%b %d')
                )
                self.weekly_dropdown.addItem(date_str)

                cur_date += one_week

        else:
            self.weekly_label.hide()
            self.weekly_dropdown.hide()

        if frequency == 'Monthly':
            self.monthly_label.show()
            self.monthly_dropdown.show()
        else:
            self.monthly_label.hide()
            self.monthly_dropdown.hide()

        if frequency == 'Quarterly':
            self.quarterly_label.show()
            self.quarterly_q1.show()
            self.quarterly_q2.show()
            self.quarterly_q3.show()
            self.quarterly_q4.show()

            # make sure a quarterly radio button is checked
            if not self.quarterly_q1.isChecked() and not self.quarterly_q2.isChecked() and not self.quarterly_q3.isChecked() and not self.quarterly_q4.isChecked():
                self.quarterly_q1.setChecked(True)
        else:
            self.quarterly_label.hide()
            self.quarterly_q1.hide()
            self.quarterly_q2.hide()
            self.quarterly_q3.hide()
            self.quarterly_q4.hide()

        if frequency == 'Semiannually':
            self.semiannually_label.show()
            self.semiannually_q12.show()
            self.semiannually_q34.show()

            # make sure a semiannually radio button is checked
            if not self.semiannually_q12.isChecked() and not self.semiannually_q34.isChecked():
                self.semiannually_q12.setChecked(True)
        else:
            self.semiannually_label.hide()
            self.semiannually_q12.hide()
            self.semiannually_q34.hide()

        # update freqency text

        # the QString objects which represent the widget state are unicode
        # strings, hence the u'...'
        self.quarterly_q1.setText(u'Q1 {}'.format(year))
        self.quarterly_q2.setText(u'Q2 {}'.format(year))
        self.quarterly_q3.setText(u'Q3 {}'.format(year))
        self.quarterly_q4.setText(u'Q4 {}'.format(year))
        self.semiannually_q12.setText(u'Q1 and Q2 {}'.format(year))
        self.semiannually_q34.setText(u'Q3 and Q4 {}'.format(year))

    def get_year_period(self):
        frequency = self.frequency.currentText()

        if frequency == 'Weekly':
            year_period = self.weekly_dropdown.currentText()

        elif frequency == 'Monthly':
            year_period = self.monthly_dropdown.currentText()

        elif frequency == 'Quarterly':
            if self.quarterly_q1.isChecked():
                year_period = 'Q1'
            if self.quarterly_q2.isChecked():
                year_period = 'Q2'
            if self.quarterly_q3.isChecked():
                year_period = 'Q3'
            if self.quarterly_q4.isChecked():
                year_period = 'Q4'

        elif frequency == 'Semiannually':
            if self.semiannually_q12.isChecked():
                year_period = 'Q12'
            if self.semiannually_q34.isChecked():
                year_period = 'Q34'

        return year_period

    def sign_save_clicked(self):
        self.save()
        self.sign()

    def sign_once_clicked(self):
        self.sign()

    def save(self):
        frequency = self.frequency.currentText()
        year = self.year.currentText()
        year_period = self.get_year_period()
        status = str(self.status.currentText())
        text = self.textbox.toPlainText()

        self.settings.set_frequency(frequency)
        self.settings.set_year(year)
        self.settings.set_status(status)
        self.settings.set_text(text)

        key_i = self.key_selection.currentIndex()
        fp = self.gpg.seckeys_list()[key_i]['fp']
        self.settings.set_fp(fp)

        self.settings.save()

    def sign(self):
        frequency = self.frequency.currentText()
        year = self.year.currentText()
        year_period = self.get_year_period()
        status = str(self.status.currentText())
        text = str(self.textbox.toPlainText())

        if self.headlines.enabled and self.headlines.have_headlines:
            text = '\n\n'.join([text, self.headlines.headlines_str, ''])

        # add headers
        period_date = year_period
        if frequency == 'Quarterly':
            quarterly_headers = {
                'Q1': 'January 1 to March 31',
                'Q2': 'April 1 to June 30',
                'Q3': 'July 1 to September 30',
                'Q4': 'October 1 to December 31'
            }
            period_date = quarterly_headers[year_period]
        elif frequency == 'Semiannually':
            semiannually_headers = {
                'Q12': 'January 1 to June 30',
                'Q34': 'July 1 to December 31'
            }
            period_date = semiannually_headers[year_period]

        # the QString objects which represent the widget state are unicode
        # strings, hence the u'...'
        message = u'Status: {}\nPeriod: {}, {}\n\n{}'.format(status, period_date, year, text)

        # sign the file
        key_i = self.key_selection.currentIndex()
        fp = self.gpg.seckeys_list()[key_i]['fp']
        signed_message = self.gpg.sign(message, fp)

        if signed_message:
            # display signed message
            dialog = OutputDialog(self.app, signed_message)
            dialog.exec_()
        else:
            common.alert('Failed to sign message.')

    def get_headlines_controls(self):
        checkbox = QtWidgets.QCheckBox('Add Recent News Headlines')
        button_fetch = QtWidgets.QPushButton('Fetch Headlines')
        button_fetch.setDisabled(True)
        button_preview = QtWidgets.QPushButton('Preview Headlines')
        button_preview.setDisabled(True)
        def fetch_headlines():
            # synchronous.
            self.headlines.fetch_headlines()
            button_fetch.setDisabled(False)
            self.setCursor(QtCore.Qt.ArrowCursor)
            if self.headlines.have_headlines:
                button_preview.setDisabled(False)
        def cb_clicked():
            if checkbox.isChecked():
                button_fetch.setDisabled(False)
                self.headlines.enabled = True
                if self.headlines.have_headlines:
                    button_preview.setDisabled(False)
                else:
                    button_preview.setDisabled(True)
            else:
                self.headlines.enabled = False
                button_fetch.setDisabled(True)
                button_preview.setDisabled(True)
        def fetch_clicked():
            self.setCursor(QtCore.Qt.WaitCursor)
            button_fetch.setDisabled(True)
            # allow the widgets a chance to refresh (disabled/wait).
            QtCore.QTimer().singleShot(1, fetch_headlines)
        def preview_clicked():
            dialog = QtWidgets.QDialog()
            dialog.setModal(True)
            dialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
            layout = QtWidgets.QVBoxLayout()
            text = QtWidgets.QTextEdit()
            text.setText(self.headlines.headlines_str)
            button_close = QtWidgets.QPushButton('Close')
            button_close.clicked.connect(dialog.close)
            layout.addWidget(text)
            layout.addWidget(button_close)
            dialog.setLayout(layout)
            dialog.exec_()
        button_fetch.clicked.connect(fetch_clicked)
        button_preview.clicked.connect(preview_clicked)
        checkbox.clicked.connect(cb_clicked)
        return [checkbox, button_fetch, button_preview]


def main():
    # start the app
    app = QtWidgets.QApplication(sys.argv)

    # initialize and check for gpg and a secret key
    gpg = GnuPG()

    # initialize the module which handles the daily headlines feature.
    headlines = Headlines()

    system = platform.system()
    if system == 'Darwin':
        if not gpg.is_gpg_available():
            common.alert('GPG doesn\'t seem to be installed. Install <a href="https://gpgtools.org/">GPGTools</a>, generate a key, and run AutoCanary again.')
            sys.exit(0)

        seckeys = gpg.seckeys_list()
        if len(seckeys) == 0:
            common.alert('You need an encryption key to use AutoCanary. Run the GPG Keychain program, generate a key, and run AutoCanary again.')
            sys.exit(0)

    elif system == 'Linux':
        seckeys = gpg.seckeys_list()
        if len(seckeys) == 0:
            common.alert('You need an encryption key to use AutoCanary. Generate a key, and run AutoCanary again.')
            sys.exit(0)

    elif system == 'Windows':
        if not gpg.is_gpg_available():
            common.alert('GPG doesn\'t seem to be installed. Install <a href="https://gpg4win.org/">Gpg4win</a>, generate a key, and run AutoCanary again.')
            sys.exit(0)

        seckeys = gpg.seckeys_list()
        if len(seckeys) == 0:
            common.alert('You need an encryption key to use AutoCanary. Run the Kleopatra program, generate a new personal OpenPGP key pair, and run AutoCanary again.')
            sys.exit(0)

    # start the gui
    gui = AutoCanaryGui(app, gpg, headlines)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
