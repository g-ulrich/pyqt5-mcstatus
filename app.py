from main import Ui_MainWindow
import sys
from mcstatus import MinecraftServer
# from config_app_actions import AppActions
from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime
import json
import requests
from os.path import exists
import pyqtgraph as pg
pg.setConfigOption('foreground', 'w')


def current_time():
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[1]
    am_pm = "pm" if 12 < int(t[:2]) < 23 else "am"
    return f"{t}{am_pm}"


def time_now(floater=False):
    x = datetime.now().strftime("%H.%M")
    return float(x) if floater else x


class StartUtility(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.utility = Window()
        self.utility.show()


class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        Window.initialize(self)

    def css_discord(self, message):
        try:
            Message = {
                "content": f"```CSS\n{message}\n```"
            }
            webhook = self.ui.edit_discord_webhook.text()
            requests.post(webhook, data=Message)
            return True, 'success'
        except Exception as e:
            return False, str(e)

    def log(self, msg):
        list = self.ui.log
        log_count = list.count()
        if log_count > 200:
            self.ui.log.clear()
            self.log(f"Log cleared {log_count} items.")
        list.addItem(msg)
        list.scrollToBottom()
        c = self.ui.log.count()
        self.ui.label_log.setText(f"Count {c}")
        self.ui.label_timestamp.setText(current_time())
        if "[INFO]" in msg and self.ui.check_send_logs.isChecked():
            success, resp = self.css_discord(msg)
            if not success:
                self.log(f"[ERROR] {resp}")

    def write_json(self):
        dictionary = {
            "server": self.ui.edit_server_address.text(),
            "webhook": self.ui.edit_discord_webhook.text(),
            "log": self.ui.check_send_logs.isChecked(),
            "overworld_x": self.ui.line_overworld_x.value(),
            "overworld_y": self.ui.line_overworld_z.value(),
            "nether_x": self.ui.line_nether_x.value(),
            "nether_y": self.ui.line_nether_z.value()
        }
        json_object = json.dumps(dictionary, indent=4)
        with open(self.ui.json_file_name, "w") as outfile:
            outfile.write(json_object)

    def read_json(self):
        with open(self.ui.json_file_name, "r") as openfile:
            json_object = json.load(openfile)
        return json_object

    def json_check(self):
        if not exists(self.ui.json_file_name):
            self.write_json()
        else:
            form = self.read_json()
            self.ui.edit_server_address.setText(form['server'])
            self.ui.edit_discord_webhook.setText(form['webhook'])

    def calculate_overworld_portal(self):
        """
        get overworld axis and input nether
        """
        neth_x, neth_z = self.ui.line_nether_x.value(), self.ui.line_nether_z.value()
        self.ui.line_overworld_x.setValue(neth_x * 8)
        self.ui.line_overworld_z.setValue(neth_z * 8)

    def calculate_nether_portal(self):
        """
        get netrher axis and input overworld
        """
        over_x, over_z = self.ui.line_overworld_x.value(), self.ui.line_overworld_z.value()
        self.ui.line_nether_x.setValue(over_x / 8)
        self.ui.line_nether_z.setValue(over_z / 8)

    def player_count_graph(self):
        form = self.read_json()
        pw = self.ui.frame_graph
        pw.setStyleSheet('color: #fff;')
        pw.setBackground(None)
        if len(self.ui.player_count_array) > 0:
            pw.clear()
        if form['server'] != "":
            try:
                server = MinecraftServer.lookup(form['server'])
                status = server.status()
                players = status.players.online
                player_obj = {"players": players, "time": time_now()}
                self.ui.player_count_array.append(player_obj)
                if len(self.ui.player_count_array) > 6:
                    self.ui.player_count_array = self.ui.player_count_array[-5:-1]
                players_array = [i['players'] for i in self.ui.player_count_array]
                times_array = [i['time'] for i in self.ui.player_count_array]
                pw.plot(y=players_array,
                        illLevel=min(players_array),
                        brush="#fff",
                        symbol=None,
                        pen=pg.mkPen({'color': "#fff", 'width': 2})
                        )
                xax = pw.getAxis('bottom')
                ticks = [list(zip(range(len(times_array)), tuple(times_array)))]
                xax.setTicks(ticks)
                self.ui.label_users.setText(f"Players: {players}")
                self.ui.label_timestamp_users.setText(current_time())
                if players > 0:
                    self.log(f"[INFO] {players} player(s) active on {form['server']}. - {current_time()} ")
            except:
                pass
        else:
            self.ui.label_users.setText(f"No Data.")
            self.log("Enter server address.")

    def submit_form(self):
        self.write_json()
        self.log("-----Updated------")
        form = self.read_json()
        for items in form.items():
            key, val = items[0], items[1]
            if val == '':
                self.log(f"Enter {key.capitalize()}.")
        self.log(f"Analyzing {form['server']}!") if form['server'] != "" else ""
        self.log(
            f"Sending logs to {form['webhook'][0:15]}...{form['webhook'][-5:-1]}!") if self.ui.check_send_logs.isChecked() and \
                                                                                       form['webhook'] != "" else ""
        if form['server'] != "":
            server = MinecraftServer.lookup(form['server'])
            status = server.status()
            players = status.players.online
            if players == 0:
                self.log(f"Currently there are {players} player(s) online!")
        self.player_count_graph()

    def initialize(self):
        self.setWindowIcon(QtGui.QIcon('images/heart.png'))
        self.setFixedWidth(745)
        self.setFixedHeight(611)
        self.ui.json_file_name = "pyqt5-mcstatus.json"
        self.ui.player_count_array = []
        self.log("Welcome!")
        self.json_check()
        self.ui.line_overworld_x.valueChanged.connect(self.calculate_nether_portal)
        self.ui.line_overworld_z.valueChanged.connect(self.calculate_nether_portal)
        self.ui.line_nether_x.valueChanged.connect(self.calculate_overworld_portal)
        self.ui.line_nether_z.valueChanged.connect(self.calculate_overworld_portal)
        self.ui.btn_submit.clicked.connect(self.submit_form)
        form = self.read_json()
        self.log(f"Analyzing {form['server']}!") if form['server'] != "" else ""
        self.log(f"Sending logs to {form['webhook'][0:15]}...{form['webhook'][-5:-1]}!") if self.ui.check_send_logs.isChecked() and form['webhook'] != "" else ""
        self.player_count_graph()
        if form['server'] != "":
            server = MinecraftServer.lookup(form['server'])
            status = server.status()
            players = status.players.online
            if players == 0:
                self.log(f"Currently there are {players} player(s) online!")
        # timer for graph data
        self.ui.t = QtCore.QTimer()
        self.ui.t.timeout.connect(self.player_count_graph)
        self.ui.t.start(60000 * 5)

    # def time_and_internet(self):
    #     AppActions.check_internet_connection_and_set_time(self)
    #     self.ui.time_and_internet = QtCore.QTimer()
    #     self.ui.time_and_internet.timeout.connect(
    #         lambda: AppActions.check_internet_connection_and_set_time(self))
    #     self.ui.time_and_internet.start(2000)
    #
    # def buttons(self):
    #     self.ui.btn_side_menu_live_trade.clicked.connect(lambda: AppActions.go_to_livetrade(self))
    #     self.ui.btn_side_menu_settings.clicked.connect(lambda: AppActions.go_to_settings(self))
    #     self.ui.check_side_menu_dark_mode.stateChanged.connect(lambda: AppActions.change_stylesheet(self))
    #     self.ui.btn_side_menu_home.clicked.connect(lambda: AppActions.go_to_dashboard(self))
    #     self.ui.btn_side_menu_backtest.clicked.connect(lambda: AppActions.go_to_backtest(self))
    #     self.ui.btn_side_menu_quote.clicked.connect(lambda: AppActions.go_to_quote(self))

    # def minimum_height_and_width(self):
    #     self.setMinimumWidth(900)
    #     self.setMinimumHeight(900)
    #
    # def initialize(self):
    #     self.ui.database_file_path = 'assets/userData/user.db'
    #     self.ui.database_connection = sql.connect(self.ui.database_file_path, check_same_thread=False)
    #     self.ui.algorithm_is_livetrading = False
    #     self.ui.dark_mode_is_on = True
    #     User.initialize(self) # sets user data
    #     self.ui.get_market_hours = []
    #     Window.time_and_internet(self)
    #     Window.minimum_height_and_width(self)
    #     Window.buttons(self)
    #     EquityLivetrade.initialize(self)
    #     Dashboard.initialize(self)
    #     Backtest.initialize(self)
    #     Quote.initialize(self)
    #     self.ui.table_quote_backtest_history.cellClicked.connect(self.quote_history_table_row_data)
    #     self.ui.table_backtest_history.cellClicked.connect(self.backtest_history_table_row_data)
    #     self.ui.table_backtest_recent_history.cellClicked.connect(self.backtest_recent_table_row_data)
    #
    # def backtest_recent_table_row_data(self, row, col):
    #     row_items = []
    #     for i in range(self.ui.table_backtest_recent_history.columnCount()):
    #         # check if cell is widget or not
    #         row_items.append(self.ui.table_backtest_recent_history.item(row, i).text() if i != 0 else "")
    #     Backtest.insert_backtest_results(self, row_items)
    #
    # def backtest_history_table_row_data(self, row, col):
    #     row_items = []
    #     for i in range(self.ui.table_backtest_history.columnCount()):
    #         # check if cell is widget or not
    #         row_items.append(self.ui.table_backtest_history.item(row, i).text() if i != 0 and i != 2 else "")
    #     Backtest.insert_backtest_results(self, row_items)
    #
    # def quote_history_table_row_data(self, row, col):
    #     row_items = []
    #     for i in range(self.ui.table_quote_backtest_history.columnCount()):
    #         # check if cell is widget or not
    #         row_items.append(self.ui.table_quote_backtest_history.item(row, i).text() if i != 0 and i != 2 else "")
    #     Quote.insert_backtest_results(self, row_items)

    # def mousePressEvent(self, event):
    #     self.dragPos = event.globalPos()
    #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() == QtCore.Qt.LeftButton:
    #         self.move(self.pos() + event.globalPos() - self.dragPos)
    #         self.dragPos = event.globalPos()
    #         event.accept()


if __name__ == "__main__":
    app = StartUtility(sys.argv)
    sys.exit(app.exec_())
