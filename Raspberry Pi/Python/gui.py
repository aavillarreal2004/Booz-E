import sys, csv
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import *
import gpiozero
from qt_material import apply_stylesheet
import os


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Booze Interface")
        screen_size = (600-2, 1024-2)
        self.setGeometry(0, 0, *screen_size)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        
        self.layout = QStackedLayout()
        
        # Splash screen
        self.splash_pixmap = QPixmap("logo_pink.png")
        self.splash_size = 300
        self.scaled_splash_picture = self.splash_pixmap.scaled(self.splash_size, self.splash_size)
        self.splash_label = QLabel(self)
        self.splash_label.setPixmap(self.scaled_splash_picture)
        self.splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
        self.gui_widget = QWidget()
        self.gui_layout = QVBoxLayout(self.gui_widget)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scroll_area.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        QScroller.grabGesture(self.scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        self.scroll_widget = QWidget()
        self.scroll_layout = QHBoxLayout()
        
        self.drink_dict = self.read_csv("drinks.csv")
        for drink in self.drink_dict:
            drink_image_path = os.path.join("drink_images", drink + ".jpeg")
            drink_button = QPushButton()
            drink_button.setStyleSheet("border: 0px solid #ff3eb5;")
            drink_button.clicked.connect(lambda checked, i=drink: self.highlight_drink(i))
            drink_icon = QIcon(drink_image_path)
            drink_button.setIcon(drink_icon)
            drink_button.setIconSize(QSize(500-20, 300-20))
            drink_button.setFixedSize(QSize(200, 300))
            self.scroll_layout.addWidget(drink_button)
            self.drink_dict[drink].append(drink_button)
            self.drink_dict[drink].append(0)
        
        self.dispense_button = QPushButton("Dispense")
        self.dispense_button.setStyleSheet("font-size: 30px;")
        self.dispense_button.setFixedSize(QSize(200, 80))
        self.dispense_button.clicked.connect(lambda: self.switch_to_dispensing_gui(self.selected_drink))
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.gui_layout.addStretch()
        self.gui_layout.addWidget(self.scroll_area)
        self.gui_layout.addWidget(self.dispense_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.gui_layout.addStretch()
        
        self.dispensing_widget = QWidget()
        self.dispensing_layout = QVBoxLayout(self.dispensing_widget)
        self.dispense_label = QLabel()
        self.dispense_label.setStyleSheet("font-size: 36px")
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_countdown)
        self.timer_label = QLabel()
        self.timer_label.setStyleSheet("font-size: 36px")
        
        self.dispensing_layout.addStretch()
        self.dispensing_layout.addWidget(self.dispense_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dispensing_layout.addWidget(self.timer_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dispensing_layout.addStretch()
        
        motor_pin = 16
        liquid_sensor_pin = 26
        
        self.motor_control = gpiozero.DigitalOutputDevice(motor_pin)
        self.liquid_sensor = gpiozero.DigitalInputDevice(liquid_sensor_pin)
        
        self.layout.addWidget(self.gui_widget)
        self.layout.addWidget(self.splash_label)
        self.layout.addWidget(self.dispensing_widget)
        self.layout.setCurrentIndex(1)
        
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        
        self.splash_timer()
    
    def splash_timer(self):
        QTimer.singleShot(1300, self.splash_fadeout)
        QTimer.singleShot(2500, self.switch_to_main_gui)
    
    def splash_fadeout(self):
        self.opacity_effect = QGraphicsOpacityEffect(self.splash_label)
        self.splash_label.setGraphicsEffect(self.opacity_effect)
        self.splash_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.splash_animation.setDuration(900)
        self.splash_animation.setStartValue(1)
        self.splash_animation.setEndValue(0)
        self.splash_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.splash_animation.start()
        
    def switch_to_main_gui(self):
        self.layout.setCurrentIndex(0)
            
    def highlight_drink(self, drink_id):
        # Reset all buttons to unhighlighted
        for drink in self.drink_dict:
            drink_button = self.drink_dict[drink][2]
            drink_button.setStyleSheet("border: 0px solid #ff3eb5;")
            
        # Highlight button that user just pressed
        self.selected_drink = drink_id
        selected_drink_button = self.drink_dict[self.selected_drink][2]
        selected_drink_button.setStyleSheet("border: 20px solid #ff3eb5;")
        
        
    def switch_to_dispensing_gui(self, drink_id):
        self.layout.setCurrentIndex(2)
        self.dispense_label.setText(f"Now dispensing your {self.drink_dict[drink_id][0]}")
        self.timer_label.setText("Starting...")
        self.start_timer()
        
    def start_timer(self):
        self.time_left = 10
        self.motor_control.on()
        self.timer.start()
        
    def update_countdown(self):
        print(self.liquid_sensor.is_active)
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.setText(f"{self.time_left+1}")
        else:
            self.timer.stop()
            self.motor_control.off()
            self.timer_label.setText("Done!")
            QTimer.singleShot(1300, self.switch_to_main_gui)
            
    def read_csv(self, filename):
        drink_dict = {}
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                drink_dict[row[0]] = row[1:]
            for key in drink_dict:
                drink_dict[key][1] = [int(i) for i in drink_dict[key][1].split(" ")]
        return drink_dict



if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="booze-theme.xml")
    window = MyWindow()

    window.show()
    window.showFullScreen()

    sys.exit(app.exec())
    

