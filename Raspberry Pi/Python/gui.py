import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import *
from gpiozero import LED
import os


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Booze Interface")
        screen_size = (600-2, 1024-2)
        self.setGeometry(0, 0, *screen_size)
        
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
        self.scroll_layout = QHBoxLayout()
        
        for drink_image_filename in os.listdir("drink_images"):
            drink_image_path = os.path.join("drink_images", drink_image_filename)
            drink_button = QPushButton()
            drink_icon = QIcon(drink_image_path)
            drink_button.setIcon(drink_icon)
            drink_button.setIconSize(QSize(400-8, 300-8))
            drink_button.setFixedSize(QSize(200, 300))
            self.scroll_layout.addWidget(drink_button)
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.gui_layout.addWidget(self.scroll_widget)
        
        self.layout.addWidget(self.gui_widget)
        self.layout.addWidget(self.splash_label)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()

    window.show()
    window.showFullScreen()

    sys.exit(app.exec())