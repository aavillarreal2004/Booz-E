import sys, csv
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import *
import gpiozero
from qt_material import apply_stylesheet
import os


def read_csv(filename):
    drink_dict = {}
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            drink_dict[row[0]] = row[1:]
        for key in drink_dict:
            drink_dict[key][1] = [int(i) for i in drink_dict[key][1].split(" ")]
    return drink_dict


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)

        self.layout = QStackedLayout()
        screen_size = (600 - 2, 1024 - 2)
        self.layout.setGeometry(QRect(0, 0, *screen_size))

        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        # Splash screen
        self.splash_pixmap = QPixmap("logo_pink.png")
        self.splash_size = 300
        self.scaled_splash_picture = self.splash_pixmap.scaled(self.splash_size, self.splash_size)
        self.splash_label = QLabel(self)
        self.splash_label.setPixmap(self.scaled_splash_picture)
        self.splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main four-drink screen
        #       Adding layouts
        self.main_drink_screen = QWidget()
        self.main_drink_widget = QWidget(self.main_drink_screen)
        self.main_drink_layout = QVBoxLayout(self.main_drink_widget)
        self.four_button_layout = QHBoxLayout()
        self.dispense_button_layout = QHBoxLayout()

        #       Adding items to layouts
        self.drink_selection_buttons = []
        self.drink_slot_number = 0
        for drink_selection_button_number in range(4):
            drink_selection_button = QPushButton()
            drink_selection_button.clicked.connect(
                lambda checked, i=drink_selection_button_number: self.drink_selection_button_tapped(i))
            button_inactive_icon_path = "ui_images\\logo_transparent_gray.png"
            drink_selection_button_inactive_icon = QIcon(button_inactive_icon_path)
            drink_selection_button.setIcon(drink_selection_button_inactive_icon)
            drink_selection_button.setIconSize(QSize(160, 160))
            drink_selection_button.setFixedSize(QSize(200, 300))
            size_policy.setHeightForWidth(drink_selection_button.sizePolicy().hasHeightForWidth())
            self.four_button_layout.addWidget(drink_selection_button)
            self.drink_selection_buttons.append(drink_selection_button)

        self.dispense_button = QPushButton("Dispense")
        self.dispense_button.setFixedSize(200, 60)
        self.dispense_button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.dispense_button_layout.addWidget(self.dispense_button)
        self.dispense_button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        #       Arranging biggest layouts
        self.main_drink_layout.addItem(QSpacerItem(0, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.main_drink_layout.addLayout(self.four_button_layout)
        self.main_drink_layout.addLayout(self.dispense_button_layout)
        self.main_drink_layout.addItem(QSpacerItem(0, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Drink selection screen
        self.drink_selection_screen = QWidget()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scroll_area.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        QScroller.grabGesture(self.scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        self.scroll_layout = QGridLayout(self.scroll_area)
        self.drink_selection_screen.setLayout(self.scroll_layout)

        self.drink_dict = read_csv("drinks.csv")
        index = -1
        for drink in self.drink_dict:
            index += 1
            drink_image_path = os.path.join("drink_images", drink + ".jpeg")
            drink_button = QPushButton()
            drink_button.setStyleSheet("border: 0px solid #ff3eb5;")
            drink_button.clicked.connect(lambda checked, i=drink: self.select_drink(i))
            drink_icon = QIcon(drink_image_path)
            drink_button.setIcon(drink_icon)
            drink_button.setIconSize(QSize(500 - 20, 300 - 20))
            drink_button.setFixedSize(QSize(200, 300))
            self.scroll_layout.addWidget(drink_button, index // 4, index % 4)
            self.drink_dict[drink].append(drink_button)
            self.drink_dict[drink].append(0)
        #
        # self.dispense_button = QPushButton("Dispense")
        # self.dispense_button.setStyleSheet("font-size: 30px;")
        # self.dispense_button.setFixedSize(QSize(200, 80))
        # self.dispense_button.clicked.connect(lambda: self.switch_to_dispensing_gui(self.selected_drink))
        # self.scroll_widget.setLayout(self.scroll_layout)
        # self.scroll_area.setWidget(self.scroll_widget)
        # self.gui_layout.addStretch()
        # self.gui_layout.addWidget(self.scroll_area)
        # self.gui_layout.addWidget(self.dispense_button, alignment=Qt.AlignmentFlag.AlignCenter)
        # self.gui_layout.addStretch()
        #
        # self.dispensing_widget = QWidget()
        # self.dispensing_layout = QVBoxLayout(self.dispensing_widget)
        # self.dispense_label = QLabel()
        # self.dispense_label.setStyleSheet("font-size: 36px")
        # self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.update_countdown)
        # self.timer_label = QLabel()
        # self.timer_label.setStyleSheet("font-size: 36px")
        #
        # self.dispensing_layout.addStretch()
        # self.dispensing_layout.addWidget(self.dispense_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # self.dispensing_layout.addWidget(self.timer_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # self.dispensing_layout.addStretch()

        self.layout.addWidget(self.splash_label)
        self.layout.addWidget(self.main_drink_screen)
        self.layout.addWidget(self.drink_selection_screen)
        self.layout.setCurrentIndex(0)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.splash_timer()

    def splash_timer(self):
        QTimer.singleShot(1300, self.splash_fadeout)
        QTimer.singleShot(2500, lambda page_index=1: self.switch_to_page_index(page_index))

    def splash_fadeout(self):
        self.opacity_effect = QGraphicsOpacityEffect(self.splash_label)
        self.splash_label.setGraphicsEffect(self.opacity_effect)
        self.splash_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.splash_animation.setDuration(900)
        self.splash_animation.setStartValue(1)
        self.splash_animation.setEndValue(0)
        self.splash_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.splash_animation.start()

    def switch_to_page_index(self, index):
        self.layout.setCurrentIndex(index)

    def drink_selection_button_tapped(self, drink_selection_button_number):
        self.drink_slot_number = drink_selection_button_number
        self.switch_to_page_index(2)

    def select_drink(self, drink_id):
        # Reset all buttons to unhighlighted
        for drink in self.drink_dict:
            drink_button = self.drink_dict[drink][2]
            drink_button.setStyleSheet("border: 0px solid #ff3eb5;")

        # Highlight button that user just pressed
        self.selected_drink = drink_id
        selected_drink_button = self.drink_dict[self.selected_drink][2]
        selected_drink_button.setStyleSheet("border: 20px solid #ff3eb5;")
        self.drink_selection_buttons[self.drink_slot_number].setIcon(
            QIcon(os.path.join("drink_images", drink_id + ".jpeg")))
        self.switch_to_page_index(1)

    def switch_to_dispensing_gui(self, drink_id):
        self.switch_to_page_index(2)
        self.dispense_label.setText(f"Now dispensing your {self.drink_dict[drink_id][0]}")
        self.timer_label.setText("Starting...")
        self.start_timer()

    def start_timer(self):
        self.time_left = 10
        self.timer.start()

    def update_countdown(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.setText(f"{self.time_left + 1}")
        else:
            self.timer.stop()
            self.timer_label.setText("Done!")
            QTimer.singleShot(1300, lambda page_index=1: self.switch_to_page_index(page_index))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="booze-theme.xml")
    window = MyWindow()

    window.show()
    # window.showFullScreen()

    sys.exit(app.exec())
