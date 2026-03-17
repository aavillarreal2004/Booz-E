import csv
import os
import sys
from enum import Enum, auto
from pathlib import Path

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qt_material import apply_stylesheet


# ===== Constants =====
SPLASH_DURATION = 1300          # ms before fade starts
FADE_DURATION = 900             # ms for fade animation
SWITCH_DELAY = 2500              # ms after splash to switch screen
BUTTON_SIZE = QSize(200, 300)
ICON_SIZE = QSize(160, 160)
DISPENSE_BUTTON_SIZE = QSize(200, 60)
MAX_COLS = 4
SCROLL_ICON_SIZE = QSize(480, 280)   # drink selection icons


# ===== Enums =====
class DispenseStatus(Enum):
    """Status of each drink slot."""
    NO_DRINK = auto()           # 0
    SELECTED = auto()            # 1
    DISPENSING = auto()          # 2
    DONE = auto()                 # 3


# ===== Data Class =====
class DrinkData:
    """Holds information for one drink."""
    def __init__(self, name, description, ingredient_list):
        self.name = name
        self.description = description
        self.ingredients = ingredient_list   # list of ints
        self.button = None                    # will be set later
        self.selection_count = 0


# ===== CSV Loader =====
def load_drinks_from_csv(filename):
    """
    Reads a CSV file with drink data.
    Expected columns: drink_name, description, space-separated ingredient IDs.
    Returns a dict mapping drink name -> DrinkData object.
    """
    drinks = {}
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row:
                continue
            name = row[0].strip()
            description = row[1].strip() if len(row) > 1 else ""
            ingredient_str = row[2].strip() if len(row) > 2 else ""
            ingredients = [int(x) for x in ingredient_str.split()] if ingredient_str else []
            drinks[name] = DrinkData(name, description, ingredients)
    return drinks


# ===== Splash Screen Widget =====
class SplashScreen(QLabel):
    """Full‑screen splash with fade‑out animation."""
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
    """Screen showing four drink slots and a dispense button."""
    slot_clicked = pyqtSignal(int)          # emitted when a slot button is tapped
    dispense_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.slot_buttons = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Top spacer
        main_layout.addSpacerItem(QSpacerItem(0, 100, QSizePolicy.Policy.Minimum,
                                              QSizePolicy.Policy.Expanding))

        # Four buttons layout
        button_row = QHBoxLayout()
        for i in range(4):
            btn = QPushButton()
            btn.setFixedSize(BUTTON_SIZE)
            btn.setIconSize(ICON_SIZE)
            btn.clicked.connect(lambda checked, idx=i: self.slot_clicked.emit(idx))
            # Default inactive icon
            btn.setIcon(QIcon("ui_images/logo_transparent_gray.png"))
            button_row.addWidget(btn)
            self.slot_buttons.append(btn)
        main_layout.addLayout(button_row)

        # Dispense button (centered)
        dispense_row = QHBoxLayout()
        dispense_row.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                                               QSizePolicy.Policy.Minimum))
        dispense_btn = QPushButton("Dispense")
        dispense_btn.setFixedSize(DISPENSE_BUTTON_SIZE)
        dispense_btn.clicked.connect(self.dispense_clicked.emit)
        dispense_row.addWidget(dispense_btn)
        dispense_row.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                                               QSizePolicy.Policy.Minimum))
        main_layout.addLayout(dispense_row)

        # Bottom spacer
        main_layout.addSpacerItem(QSpacerItem(0, 100, QSizePolicy.Policy.Minimum,
                                              QSizePolicy.Policy.Expanding))

    def set_slot_icon(self, slot_index, icon_path):
        """Change the icon of a slot button."""
        self.slot_buttons[slot_index].setIcon(QIcon(icon_path))

    def set_slot_enabled(self, slot_index, enabled):
        """Enable or disable a slot button."""
        self.slot_buttons[slot_index].setEnabled(enabled)


# ===== Drink Selection Screen (scrollable grid) =====
class DrinkSelectionScreen(QWidget):
    """Scrollable grid of all available drinks."""
    drink_selected = pyqtSignal(str)        # emits drink name
    cancel_clicked = pyqtSignal()

    def __init__(self, drinks_dict, images_folder):
        super().__init__()
        self.drinks = drinks_dict
        self.images_folder = Path(images_folder)
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

        # Container for the grid inside the scroll area
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(10)

        # Cancel button (top right)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_clicked.emit)
        grid.addWidget(cancel_btn, 0, MAX_COLS - 1)

        # Drink buttons
        for idx, (name, drink_data) in enumerate(self.drinks.items()):
            btn = QPushButton()
            btn.setFixedSize(BUTTON_SIZE)
            btn.setIconSize(SCROLL_ICON_SIZE)
            btn.setStyleSheet("border: 0px solid #ff3eb5;")   # no border
            btn.clicked.connect(lambda checked, n=name: self.drink_selected.emit(n))

            # Load image (fallback to placeholder if missing)
            image_path = self.images_folder / f"{name}.jpeg"
            if image_path.exists():
                btn.setIcon(QIcon(str(image_path)))
            else:
                btn.setIcon(QIcon("ui_images/logo_transparent_gray.png"))

            grid.addWidget(btn, (idx // MAX_COLS) + 1, idx % MAX_COLS)
            drink_data.button = btn   # store reference for later use

        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)


# ===== Main Window =====
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)

        # Load drink data
        self.drinks = load_drinks_from_csv("drinks.csv")

        # Status for the four slots: (status, drink_name)
        self.slot_status = {i: (DispenseStatus.NO_DRINK, None) for i in range(4)}
        self.current_slot = 0   # which slot is being configured

        # Stacked layout
        self.stacked = QStackedLayout()
        self._create_pages()
        self._setup_central_widget()

        # Start splash timer
        self._start_splash()

    def _create_pages(self):
        # Page 0: splash
        self.splash = SplashScreen("logo_pink.png", 300)
        self.stacked.addWidget(self.splash)

        # Page 1: main drink screen
        self.main_screen = MainDrinkScreen()
        self.main_screen.slot_clicked.connect(self.on_slot_clicked)
        self.main_screen.dispense_clicked.connect(self.on_dispense_clicked)
        self.stacked.addWidget(self.main_screen)

        # Page 2: drink selection screen
        self.selection_screen = DrinkSelectionScreen(self.drinks, "drink_images")
        self.selection_screen.drink_selected.connect(self.on_drink_selected)
        self.selection_screen.cancel_clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        self.stacked.addWidget(self.selection_screen)

        self.stacked.setCurrentIndex(0)   # start with splash

    def _setup_central_widget(self):
        central = QWidget()
        central.setLayout(self.stacked)
        self.setCentralWidget(central)

    def _start_splash(self):
        QTimer.singleShot(SPLASH_DURATION, self._fade_splash)
        QTimer.singleShot(SWITCH_DELAY, lambda: self.stacked.setCurrentIndex(1))

    def _fade_splash(self):
        self.splash.fade_out(FADE_DURATION)

    # === Slots ===
    def on_slot_clicked(self, slot_index):
        """User tapped one of the four main screen slots."""
        self.current_slot = slot_index
        self.stacked.setCurrentIndex(2)   # go to drink selection

    def on_drink_selected(self, drink_name):
        """User selected a drink from the scrollable grid."""
        # Update slot button icon
        image_path = f"drink_images/{drink_name}.jpeg"
        self.main_screen.set_slot_icon(self.current_slot, image_path)

        # Update status
        self.slot_status[self.current_slot] = (DispenseStatus.SELECTED, drink_name)

        # Go back to main screen
        self.stacked.setCurrentIndex(1)

    def on_dispense_clicked(self):
        """User pressed the dispense button."""
        for slot, (status, drink_name) in self.slot_status.items():
            if status == DispenseStatus.SELECTED:
                # Disable the slot that is about to dispense
                self.main_screen.set_slot_enabled(slot, False)
                self.slot_status[slot] = (DispenseStatus.DISPENSING, drink_name)
                self.drinks[drink_name].ingredients
            else:
                # Re‑enable any slots that are not selected (original logic)
                self.main_screen.set_slot_enabled(slot, True)
                self.slot_status[slot] = (DispenseStatus.NO_DRINK, None)


# ===== Application Entry Point =====
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply custom theme if available
    theme_file = "booze-theme.xml"
    if os.path.exists(theme_file):
        apply_stylesheet(app, theme=theme_file)

    window = MainWindow()
    window.show()
    # window.showFullScreen()   # uncomment for fullscreen on target device

    sys.exit(app.exec())
