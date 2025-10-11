from PyQt5 import QtWidgets, uic
from os import path
#import modul_a
try:
    from . import modul_a
except ImportError:
    import modul_a


class MyWindow(QtWidgets.QWidget):
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
    }

    def __init__(self):
        super().__init__()
        
        ui_file = path.join(path.dirname(__file__), "..", "assets", "my_design.ui")
        print(ui_file)
        
        uic.loadUi(ui_file, self)
        self.ergebnis = None
        self.berechne_btn.clicked.connect(self.on_berechne)

        self.show()

    def _fwd_decl(self):
        self.berechne_btn: QtWidgets.QPushButton
        self.zahl1_spin: QtWidgets.QSpinBox
        self.zahl2_spin: QtWidgets.QSpinBox
        self.operation_cbx: QtWidgets.QComboBox
        self.ergebnis_lbl: QtWidgets.QLabel

    def on_berechne(self):
        zahl1 = self.zahl1_spin.value()
        zahl2 = self.zahl2_spin.value()
        operation = self.operation_cbx.currentText()

        self.ergebnis = self.ops[operation](zahl1, zahl2)

        self.ergebnis_lbl.setText(f"Ergebnis: {self.ergebnis}")


def my_gui():
    modul_a.func()
    app = QtWidgets.QApplication([])
    window = MyWindow()
    app.exec()

if __name__ == "__main__":
    my_gui()
