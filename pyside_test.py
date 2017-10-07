import sys
from PySide.QtCore import *
from PySide.QtGui import *

class Form(QDialog):
    def __init__(self,parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("My Form")


if __name__ == '__main__':
    app= QApplication(sys.argv)
    form = Form()
    form.show()
    sys.exit(app.exec_())
    


