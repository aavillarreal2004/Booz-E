import csv
import os
import sys
from enum import Enum, auto
from pathlib import Path
import gpiozero

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qt_material import apply_stylesheet

os.environ["GPIOZERO_PIN_FACTORY"] = "mock"
# os.chdir("/boot/firmware/pc_upload")

# ===== Constants =====

# Pins and gpio for sending dispense data from Raspberry Pi to Arduino
# First 3 pins are for drink info, second 2 are for which nozzle
OUTPUT_STROBE_PIN = 14
OUTPUT_DATA_PINS = [15, 18, 23, 24, 25]
DRINK_OUTPUT_PINS = [OUTPUT_STROBE_PIN] + OUTPUT_DATA_PINS
gpio_output_bus = []
for pin_number in DRINK_OUTPUT_PINS:
    gpio_output_bus.append(gpiozero.OutputDevice(pin_number))

# Receives status of dispensation from Arduino
INPUT_STROBE_PIN = 13
INPUT_DATA_PINS = [19, 26]
FEEDBACK_PINS = [INPUT_STROBE_PIN] + INPUT_DATA_PINS
gpio_input_bus = []
for PIN_NUMBER in FEEDBACK_PINS:
    gpio_input_bus.append(gpiozero.InputDevice(PIN_NUMBER))

TEST_DISPENSE_DURATION = 4000
SPLASH_DURATION = 1300
FADE_DURATION = 900
SWITCH_DELAY = 2500
BUTTON_SIZE = QSize(200, 300)
ICON_SIZE = QSize(160, 160)
DISPENSE_BUTTON_SIZE = QSize(200, 60)
MAX_COLS = 4
SCROLL_ICON_SIZE = QSize(480, 280)
DISPENSE_TIMEOUT_MS = 30000      # 30 seconds max to wait for feedback
FEEDBACK_POLL_INTERVAL_MS = 100  # check pin every 100 ms


# ===== Enums =====
class DispenseStatus(Enum):
    NO_DRINK = auto()
    SELECTED = auto()
    DISPENSING = auto()
    DONE = auto()


# ===== Data Class =====
class DrinkData:
    def __init__(self, name, description, ingredient_list, index):
        self.name = name
        self.description = description
        self.ingredients = ingredient_list
        self.index = index
        self.button = None
        self.selection_count = 0


# ===== CSV Loader =====
def load_drinks_from_csv(filename):
    drinks = {}
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for index, row in enumerate(reader):
            if not row:
                continue
            name = row[0].strip()
            description = row[1].strip() if len(row) > 1 else ""
            ingredient_str = row[2].strip() if len(row) > 2 else ""
            ingredients = [int(x) for x in ingredient_str.split()] if ingredient_str else []
            drinks[name] = DrinkData(name, description, ingredients, index + 1)
    return drinks


def set_output_bus(drink_id, nozzle_id):
    zero_based_drink = drink_id - 1

    # Combine: (drink << 2) | nozzle
    value = (zero_based_drink << 2) | nozzle_id

    # Write data to output pins
    for i in range(5):
        bit = (value >> i) & 1
        pin_index = i + 1  # data pins start at index 1
        if bit:
            gpio_output_bus[pin_index].on()
        else:
            gpio_output_bus[pin_index].off()

    # Set strobe HIGH (first pin)
    gpio_output_bus[0].on()


def clear_output_bus():
    # Turns off all output pins.
    for pin in gpio_output_bus:
        pin.off()


def read_feedback_bus():
    # Check strobe pin (index 0)
    if not gpio_input_bus[0].is_active:
        return -1  # no valid data

    value = 0
    if gpio_input_bus[1].is_active:
        value += 2
    if gpio_input_bus[2].is_active:
        value += 1
    return value


# ===== Splash Screen Widget =====
class SplashScreen(QLabel):
    def __init__(self, image_path, size=300):
        super().__init__()
        self.opacity_effect = None
        self.animation = None
        pixmap = QPixmap(image_path)
        scaled = pixmap.scaled(size, size,
                               Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def fade_out(self, duration):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.start()


# ===== Main Screen (4 slots + Dispense) =====
class MainDrinkScreen(QWidget):
    slot_clicked = pyqtSignal(int)
    dispense_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.slot_buttons = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.addSpacerItem(QSpacerItem(0, 100, QSizePolicy.Policy.Minimum,
                                              QSizePolicy.Policy.Expanding))

        button_row = QHBoxLayout()
        for i in range(4):
            button = QPushButton()
            button.setFixedSize(BUTTON_SIZE)
            button.setIconSize(ICON_SIZE)
            button.clicked.connect(lambda checked, index=i: self.slot_clicked.emit(index))
            button.setIcon(QIcon("ui_images/logo_transparent_gray.png"))
            button_row.addWidget(button)
            self.slot_buttons.append(button)
        main_layout.addLayout(button_row)

        dispense_row = QHBoxLayout()
        dispense_row.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                                               QSizePolicy.Policy.Minimum))
        self.dispense_button = QPushButton("Dispense")
        self.dispense_button.setFixedSize(DISPENSE_BUTTON_SIZE)
        self.dispense_button.clicked.connect(self.dispense_clicked.emit)
        dispense_row.addWidget(self.dispense_button)
        dispense_row.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                                               QSizePolicy.Policy.Minimum))
        main_layout.addLayout(dispense_row)

        main_layout.addSpacerItem(QSpacerItem(0, 100, QSizePolicy.Policy.Minimum,
                                              QSizePolicy.Policy.Expanding))

    def set_slot_icon(self, slot_index, icon_path):
        self.slot_buttons[slot_index].setIcon(QIcon(icon_path))

    def set_slot_enabled(self, slot_index, enabled):
        self.slot_buttons[slot_index].setEnabled(enabled)

    def set_dispense_enabled(self, enabled):
        self.dispense_button.setEnabled(enabled)


# ===== Drink Selection Screen (scrollable grid) =====
class DrinkSelectionScreen(QWidget):
    drink_selected = pyqtSignal(str)
    cancel_clicked = pyqtSignal()
    deselect_clicked = pyqtSignal()

    def __init__(self, drinks_dict, drink_images_folder, ui_images_folder):
        super().__init__()
        self.drinks = drinks_dict
        self.drink_images_folder_path = Path(drink_images_folder)
        self.ui_images_folder_path = Path(ui_images_folder)
        self._setup_ui()

    def _setup_ui(self):
        layout = QGridLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        QScroller.grabGesture(self.scroll.viewport(),
                              QScroller.ScrollerGestureType.LeftMouseButtonGesture)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(10)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_clicked.emit)
        grid.addWidget(cancel_button, 0, MAX_COLS - 1)

        deselect_button = QPushButton("Deselect")
        deselect_button.clicked.connect(self.deselect_clicked.emit)
        grid.addWidget(deselect_button, 0, MAX_COLS - 2)

        for idx, (drink_name, drink_data) in enumerate(self.drinks.items()):
            button = QPushButton()
            button.setFixedSize(BUTTON_SIZE)
            button.setIconSize(SCROLL_ICON_SIZE)
            button.setStyleSheet("border: 0px solid #ff3eb5;")
            button.clicked.connect(lambda checked, n=drink_name: self.drink_selected.emit(n))

            image_path = self.drink_images_folder_path / f"{drink_name}.jpeg"
            if not image_path.exists():
                image_path = self.ui_images_folder_path / "unknown.png"
            button.setIcon(QIcon(str(image_path)))

            grid.addWidget(button, (idx // MAX_COLS) + 1, idx % MAX_COLS)
            drink_data.button = button

        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)


# ===== Main Window =====
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)

        self.drinks = load_drinks_from_csv("drinks.csv")
        self.slot_status = {i: (DispenseStatus.NO_DRINK, None) for i in range(4)}
        self.current_slot = 0

        # Feedback monitoring
        self.dispense_timer = QTimer()
        self.dispense_timer.timeout.connect(self._check_feedback)
        self.current_dispensing_slot = -1   # -1 means none
        self.current_dispensing_drink = None

        self.dispense_burst_timer = QTimer()
        self.dispense_burst_timer.setInterval(500)
        self.dispense_burst_timer.timeout.connect(self._send_burst_code)
        self.burst_list = []
        self.nozzle_timeouts = {}  # nozzle -> QTimer

        self.stacked = QStackedLayout()
        self._create_pages()
        self._setup_central_widget()
        self._start_splash()

    def _create_pages(self):
        self.splash = SplashScreen("logo_pink.png", 300)
        self.stacked.addWidget(self.splash)

        self.main_screen = MainDrinkScreen()
        self.main_screen.slot_clicked.connect(self.on_slot_clicked)
        self.main_screen.dispense_clicked.connect(self.on_dispense_clicked)
        self.stacked.addWidget(self.main_screen)

        self.selection_screen = DrinkSelectionScreen(self.drinks, "drink_images", "ui_images")
        self.selection_screen.drink_selected.connect(self.on_drink_selected)
        self.selection_screen.cancel_clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        self.selection_screen.deselect_clicked.connect(self.on_deselect_clicked)
        self.stacked.addWidget(self.selection_screen)

        self.stacked.setCurrentIndex(0)

    def _setup_central_widget(self):
        central = QWidget()
        central.setLayout(self.stacked)
        self.setCentralWidget(central)

    def _start_splash(self):
        QTimer.singleShot(SPLASH_DURATION, self._fade_splash)
        QTimer.singleShot(SWITCH_DELAY, lambda: self.stacked.setCurrentIndex(1))

    def _fade_splash(self):
        self.splash.fade_out(FADE_DURATION)

    def on_slot_clicked(self, slot_index):
        self.current_slot = slot_index
        self.stacked.setCurrentIndex(2)

    def on_drink_selected(self, drink_name):
        drink_images_folder_path = Path("drink_images")
        image_path = drink_images_folder_path / f"{drink_name}.jpeg"
        self.main_screen.set_slot_icon(self.current_slot, str(image_path))
        self.slot_status[self.current_slot] = (DispenseStatus.SELECTED, drink_name)
        self.stacked.setCurrentIndex(1)
        self.main_screen.set_dispense_enabled(True)

    def on_dispense_clicked(self):
        # Collect all selected slots
        burst_items = []
        for nozzle, (status, drink_name) in self.slot_status.items():
            if status == DispenseStatus.SELECTED:
                burst_items.append((nozzle, drink_name))
                # Mark as DISPENSING immediately
                self.slot_status[nozzle] = (DispenseStatus.DISPENSING, drink_name)
                self.main_screen.set_slot_enabled(nozzle, False)

        if not burst_items:
            return

        # Add to burst list (these will be sent one by one)
        self.burst_list = burst_items
        # Start the burst timer – first code sent immediately, then every 500ms
        self._send_burst_code()  # send first one now
        self.dispense_burst_timer.start()  # subsequent ones every 500ms

    def _send_burst_code(self):
        if not self.burst_list:
            self.dispense_burst_timer.stop()
            self._start_feedback_monitoring()
            return

        nozzle, drink_name = self.burst_list.pop(0)

        drink_data = self.drinks.get(drink_name)
        drink_id = drink_data.index if drink_data else 0

        set_output_bus(drink_id, nozzle)

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda n=nozzle: self._on_nozzle_timeout(n))
        timer.start(DISPENSE_TIMEOUT_MS)
        self.nozzle_timeouts[nozzle] = timer

    def _on_nozzle_timeout(self, nozzle):
        """Called when one specific nozzle does not finish in time."""
        # Clean up timer
        if nozzle in self.nozzle_timeouts:
            self.nozzle_timeouts[nozzle].stop()
            del self.nozzle_timeouts[nozzle]

        # Only act if still marked as DISPENSING
        status, drink = self.slot_status.get(nozzle, (None, None))
        if status != DispenseStatus.DISPENSING:
            return

        # Mark as failed (DONE with error)
        self.slot_status[nozzle] = (DispenseStatus.DONE, None)
        self.main_screen.set_slot_enabled(nozzle, True)
        self.main_screen.set_slot_icon(nozzle, "ui_images/logo_transparent_gray.png")

        QMessageBox.warning(self, "Dispense Timeout",
                            f"Nozzle {nozzle + 1} did not finish in time.")

        # Check if all nozzles are done
        active = [n for n, (s, _) in self.slot_status.items() if s == DispenseStatus.DISPENSING]
        if not active:
            self._all_dispenses_complete()

    def on_deselect_clicked(self):
        image_path = "ui_images/logo_transparent_gray.png"
        self.slot_status[self.current_slot] = (DispenseStatus.NO_DRINK, None)
        self.main_screen.set_slot_icon(self.current_slot, image_path)
        self.stacked.setCurrentIndex(1)

    def _start_feedback_monitoring(self):
        clear_output_bus()
        self.dispense_timer.start(FEEDBACK_POLL_INTERVAL_MS)
        self.active_nozzles = [n for n, (s, _) in self.slot_status.items() if s == DispenseStatus.DISPENSING]

    def _check_feedback(self):
        finished_nozzle = read_feedback_bus()
        if finished_nozzle == -1:
            return

        status, drink = self.slot_status.get(finished_nozzle, (None, None))
        if status != DispenseStatus.DISPENSING:
            return

        # Cancel this nozzle's timeout timer
        if finished_nozzle in self.nozzle_timeouts:
            self.nozzle_timeouts[finished_nozzle].stop()
            del self.nozzle_timeouts[finished_nozzle]

        self.slot_status[finished_nozzle] = (DispenseStatus.DONE, drink)
        self.main_screen.set_slot_enabled(finished_nozzle, True)
        self.main_screen.set_slot_icon(finished_nozzle, "ui_images/logo_transparent_gray.png")

        active = [n for n, (s, _) in self.slot_status.items() if s == DispenseStatus.DISPENSING]
        if not active:
            self._all_dispenses_complete()

    def _all_dispenses_complete(self):
        self.dispense_timer.stop()
        for timer in self.nozzle_timeouts.values():
            timer.stop()
        self.nozzle_timeouts.clear()
        clear_output_bus()
        self.main_screen.set_dispense_enabled(True)
        self.current_dispensing_slot = -1
        self.current_dispensing_drink = None


# ===== Application Entry Point =====
if __name__ == "__main__":
    app = QApplication(sys.argv)

    theme_file = "booze-theme.xml"
    if os.path.exists(theme_file):
        apply_stylesheet(app, theme=theme_file)

    window = MainWindow()
    window.show()
    # window.showFullScreen()

    sys.exit(app.exec())