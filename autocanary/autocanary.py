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
from PyQt4 import QtCore, QtGui
from gnupg import GnuPG
from settings import Settings
from output_dialog import OutputDialog
import common
import feedparser

class AutoCanaryGui(QtGui.QWidget):

    def __init__(self, app, gpg):
        super(AutoCanaryGui, self).__init__()
        self.app = app
        self.gpg = gpg
        self.settings = Settings()
        self.setWindowTitle('AutoCanary')
        self.setWindowIcon(QtGui.QIcon(common.get_image_path('icon.png')))

        # frequency, year
        self.date_col1_layout = QtGui.QVBoxLayout()

        self.frequency_layout = QtGui.QHBoxLayout()
        self.frequency_label = QtGui.QLabel('Frequency')
        self.frequency = QtGui.QComboBox()
        frequency_options = ["Weekly", "Monthly", "Quarterly", "Semiannually"]
        for option in frequency_options:
            self.frequency.addItem(option)
        option = self.settings.get_frequency()
        if option in frequency_options:
            self.frequency.setCurrentIndex(frequency_options.index(option))
        self.frequency_layout.addWidget(self.frequency_label)
        self.frequency_layout.addWidget(self.frequency)
        self.frequency.activated.connect(self.update_date)

        self.year_layout = QtGui.QHBoxLayout()
        self.year_label = QtGui.QLabel('Year')
        self.year = QtGui.QComboBox()
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
        self.weekly_layout = QtGui.QHBoxLayout()
        self.weekly_label = QtGui.QLabel('Week')
        self.weekly_dropdown = QtGui.QComboBox()
        self.weekly_layout.addWidget(self.weekly_label)
        self.weekly_layout.addWidget(self.weekly_dropdown)

        # monthly dropdown
        self.monthly_layout = QtGui.QHBoxLayout()
        self.monthly_label = QtGui.QLabel('Month')
        self.monthly_dropdown = QtGui.QComboBox()
        monthly_options = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        for option in monthly_options:
            self.monthly_dropdown.addItem(option)
        self.monthly_layout.addWidget(self.monthly_label)
        self.monthly_layout.addWidget(self.monthly_dropdown)

        # quarterly radio buttons
        self.quarterly_layout = QtGui.QHBoxLayout()
        self.quarterly_label = QtGui.QLabel('Quarter')
        self.quarterly_q1 = QtGui.QRadioButton("")
        self.quarterly_q2 = QtGui.QRadioButton("")
        self.quarterly_q3 = QtGui.QRadioButton("")
        self.quarterly_q4 = QtGui.QRadioButton("")
        self.quarterly_layout.addWidget(self.quarterly_label)
        self.quarterly_layout.addWidget(self.quarterly_q1)
        self.quarterly_layout.addWidget(self.quarterly_q2)
        self.quarterly_layout.addWidget(self.quarterly_q3)
        self.quarterly_layout.addWidget(self.quarterly_q4)

        # semiannual radio buttons
        self.semiannually_layout = QtGui.QHBoxLayout()
        self.semiannually_label = QtGui.QLabel('Semester')
        self.semiannually_q12 = QtGui.QRadioButton("")
        self.semiannually_q34 = QtGui.QRadioButton("")
        self.semiannually_layout.addWidget(self.semiannually_label)
        self.semiannually_layout.addWidget(self.semiannually_q12)
        self.semiannually_layout.addWidget(self.semiannually_q34)

        # date layout
        self.date_layout = QtGui.QVBoxLayout()
        self.date_layout.addLayout(self.frequency_layout)
        self.date_layout.addLayout(self.year_layout)
        self.date_layout.addLayout(self.weekly_layout)
        self.date_layout.addLayout(self.monthly_layout)
        self.date_layout.addLayout(self.quarterly_layout)
        self.date_layout.addLayout(self.semiannually_layout)

        self.update_date()

        # status
        self.status_layout = QtGui.QHBoxLayout()
        self.status_label = QtGui.QLabel('Status')
        self.status = QtGui.QComboBox()
        status_options = ["All good", "It's complicated"]
        for option in status_options:
            self.status.addItem(option)
        option = self.settings.get_status()
        if option in status_options:
            self.status.setCurrentIndex(status_options.index(option))
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status)

        # canary text box
        self.textbox = QtGui.QTextEdit()
        self.textbox.setText(self.settings.get_text())


        # add headlines
        self.add_headlines_button = QtGui.QPushButton('Add Recent News Headlines')
        self.add_headlines_button.clicked.connect(self.add_headlines)

        # key selection
        seckeys = gpg.seckeys_list()
        self.key_selection = QtGui.QComboBox()
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

        # bottom buttons
        self.buttons_layout = QtGui.QHBoxLayout()
        self.sign_save_button = QtGui.QPushButton('Save and Sign')
        self.sign_save_button.clicked.connect(self.sign_save_clicked)
        self.sign_once = QtGui.QPushButton('One-Time Sign')
        self.sign_once.clicked.connect(self.sign_once_clicked)
        self.buttons_layout.addWidget(self.sign_save_button)
        self.buttons_layout.addWidget(self.sign_once)

        # layout
        self.layout = QtGui.QVBoxLayout()
        self.layout.addLayout(self.date_layout)
        self.layout.addLayout(self.status_layout)
        self.layout.addWidget(self.textbox)
        self.layout.addWidget(self.add_headlines_button)
        self.layout.addWidget(self.key_selection)
        self.layout.addLayout(self.buttons_layout)
        self.setLayout(self.layout)
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
        self.quarterly_q1.setText('Q1 {}'.format(year));
        self.quarterly_q2.setText('Q2 {}'.format(year));
        self.quarterly_q3.setText('Q3 {}'.format(year));
        self.quarterly_q4.setText('Q4 {}'.format(year));
        self.semiannually_q12.setText('Q1 and Q2 {}'.format(year))
        self.semiannually_q34.setText('Q3 and Q4 {}'.format(year))

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
        text = self.textbox.toPlainText()

        # add headers
        period_date = year_period
        if frequency == 'Quarterly':
            if year_period == 'Q1':
                period_date = 'January 1 to March 31'
            elif year_period == 'Q2':
                period_date = 'April 1 to June 30'
            elif year_period == 'Q3':
                period_date = 'July 1 to September 30'
            elif year_period == 'Q4':
                period_date = 'October 1 to December 31'
        elif frequency == 'Semiannually':
            if year_period == 'Q12':
                period_date = 'January 1 to June 30'
            elif year_period == 'Q34':
                period_date = 'July 1 to December 31'
        message = 'Status: {}\nPeriod: {}, {}\n\n{}'.format(status, period_date, year, text)

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
    def add_headlines(self):
        feed = feedparser.parse('https://en.wikinews.org/w/index.php?title=Special:NewsFeed&feed=rss&categories=Published&notcategories=No%20publish|Archived|AutoArchived|disputed&namespace=0&count=5&ordermethod=categoryadd&stablepages=only')
        self.textbox.append('\nRECENT HEADLINES:\n')
        for entry in feed.entries:
            self.textbox.append("- " + entry.title)

def main():
    # start the app
    app = QtGui.QApplication(sys.argv)

    # initialize and check for gpg and a secret key
    gpg = GnuPG()

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
            common.alert('GPG doesn\'t seem to be installed. Install <a href="http://gpg4win.org/">Gpg4win</a>, generate a key, and run AutoCanary again.')
            sys.exit(0)

        seckeys = gpg.seckeys_list()
        if len(seckeys) == 0:
            common.alert('You need an encryption key to use AutoCanary. Run the Kleopatra program, generate a new personal OpenPGP key pair, and run AutoCanary again.')
            sys.exit(0)

    # start the gui
    gui = AutoCanaryGui(app, gpg)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
