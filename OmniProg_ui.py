# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'OmniProg.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QStatusBar, QTabWidget, QTextEdit,
    QToolButton, QWidget, QStyle)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(640, 694)
        MainWindow.setMinimumSize(QSize(640, 694))
        MainWindow.setMaximumSize(QSize(640, 694))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 622, 651))
        self.tabWidget.setMinimumSize(QSize(622, 651))
        self.tabWidget.setMaximumSize(QSize(622, 651))
        self.Program = QWidget()
        self.Program.setObjectName(u"Program")
        self.gridLayout_10 = QGridLayout(self.Program)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_3 = QLabel(self.Program)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(70, 15))
        self.label_3.setMaximumSize(QSize(70, 15))

        self.horizontalLayout_6.addWidget(self.label_3)

        self.line_Prog = QLineEdit(self.Program)
        self.line_Prog.setObjectName(u"line_Prog")
        self.line_Prog.setEnabled(False)
        self.line_Prog.setMinimumSize(QSize(430, 21))
        self.line_Prog.setMaximumSize(QSize(430, 21))

        self.horizontalLayout_6.addWidget(self.line_Prog)

        self.Button_Prog = QToolButton(self.Program)
        self.Button_Prog.setObjectName(u"Button_Prog")
        self.Button_Prog.setMinimumSize(QSize(27, 21))
        self.Button_Prog.setMaximumSize(QSize(27, 21))

        self.horizontalLayout_6.addWidget(self.Button_Prog)


        self.gridLayout_10.addLayout(self.horizontalLayout_6, 0, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_6 = QLabel(self.Program)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(70, 15))
        self.label_6.setMaximumSize(QSize(70, 15))

        self.horizontalLayout_7.addWidget(self.label_6)

        self.line_SQTP = QLineEdit(self.Program)
        self.line_SQTP.setObjectName(u"line_SQTP")
        self.line_SQTP.setEnabled(False)
        self.line_SQTP.setMinimumSize(QSize(430, 21))
        self.line_SQTP.setMaximumSize(QSize(430, 21))

        self.horizontalLayout_7.addWidget(self.line_SQTP)

        self.Button_SQTP = QToolButton(self.Program)
        self.Button_SQTP.setObjectName(u"Button_SQTP")
        self.Button_SQTP.setEnabled(False)
        self.Button_SQTP.setMinimumSize(QSize(27, 21))
        self.Button_SQTP.setMaximumSize(QSize(27, 21))

        self.horizontalLayout_7.addWidget(self.Button_SQTP)


        self.gridLayout_10.addLayout(self.horizontalLayout_7, 1, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_1 = QLabel(self.Program)
        self.label_1.setObjectName(u"label_1")
        self.label_1.setMinimumSize(QSize(70, 16))
        self.label_1.setMaximumSize(QSize(65, 16))

        self.horizontalLayout_8.addWidget(self.label_1)

        self.comboBoxPort = QComboBox(self.Program)
        self.comboBoxPort.setObjectName(u"comboBoxPort")
        self.comboBoxPort.setMinimumSize(QSize(430, 20))
        self.comboBoxPort.setMaximumSize(QSize(430, 20))

        self.horizontalLayout_8.addWidget(self.comboBoxPort)

        self.Button_rescan = QPushButton(self.Program)
        self.Button_rescan.setObjectName(u"Button_rescan")
        self.Button_rescan.setEnabled(True)
        self.Button_rescan.setMinimumSize(QSize(30, 24))
        self.Button_rescan.setMaximumSize(QSize(30, 24))
        # ➡️ Solución: Usar el icono de "recargar" nativo del sistema operativo
        icon_sistema = self.style().standardIcon(QStyle.SP_BrowserReload)
        self.Button_rescan.setIcon(icon_sistema)
        #icon = QIcon()
        #icon.addFile(u"Ico_refresh.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        #self.Button_rescan.setIcon(icon)

        self.horizontalLayout_8.addWidget(self.Button_rescan)

        self.gridLayout_10.addLayout(self.horizontalLayout_8, 2, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_5 = QLabel(self.Program)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(120, 10))
        self.label_5.setMaximumSize(QSize(120, 10))

        self.horizontalLayout_9.addWidget(self.label_5)

        self.check_SQTPMan = QCheckBox(self.Program)
        self.check_SQTPMan.setObjectName(u"check_SQTPMan")
        self.check_SQTPMan.setEnabled(False)
        self.check_SQTPMan.setMinimumSize(QSize(60, 20))
        self.check_SQTPMan.setMaximumSize(QSize(60, 20))

        self.horizontalLayout_9.addWidget(self.check_SQTPMan)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer)


        self.gridLayout_10.addLayout(self.horizontalLayout_9, 3, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.line_SQTPNumber = QLineEdit(self.Program)
        self.line_SQTPNumber.setObjectName(u"line_SQTPNumber")
        self.line_SQTPNumber.setEnabled(False)
        self.line_SQTPNumber.setMinimumSize(QSize(171, 40))
        self.line_SQTPNumber.setMaximumSize(QSize(171, 40))
        font = QFont()
        font.setPointSize(18)
        self.line_SQTPNumber.setFont(font)
        self.line_SQTPNumber.setLayoutDirection(Qt.RightToLeft)
        self.line_SQTPNumber.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.line_SQTPNumber)

        self.label_PASS = QLabel(self.Program)
        self.label_PASS.setObjectName(u"label_PASS")
        font1 = QFont()
        font1.setPointSize(22)
        self.label_PASS.setFont(font1)
        self.label_PASS.setLayoutDirection(Qt.LeftToRight)
        self.label_PASS.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.label_PASS)

        self.Button_program = QPushButton(self.Program)
        self.Button_program.setObjectName(u"Button_program")
        self.Button_program.setEnabled(False)
        self.Button_program.setMinimumSize(QSize(110, 50))
        self.Button_program.setMaximumSize(QSize(110, 50))

        self.horizontalLayout.addWidget(self.Button_program)


        self.gridLayout_10.addLayout(self.horizontalLayout, 4, 0, 1, 1)

        self.textEdit = QTextEdit(self.Program)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setEnabled(True)
        self.textEdit.setUndoRedoEnabled(False)
        self.textEdit.setReadOnly(True)

        self.gridLayout_10.addWidget(self.textEdit, 5, 0, 1, 1)

        self.tabWidget.addTab(self.Program, "")
        self.Tools = QWidget()
        self.Tools.setObjectName(u"Tools")
        self.gridLayout_6 = QGridLayout(self.Tools)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.groupBox_2 = QGroupBox(self.Tools)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_8 = QGridLayout(self.groupBox_2)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.line_Prog_2 = QLineEdit(self.groupBox_2)
        self.line_Prog_2.setObjectName(u"line_Prog_2")
        self.line_Prog_2.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.line_Prog_2)

        self.Button_Prog_2 = QToolButton(self.groupBox_2)
        self.Button_Prog_2.setObjectName(u"Button_Prog_2")
        self.Button_Prog_2.setEnabled(True)

        self.horizontalLayout_5.addWidget(self.Button_Prog_2)


        self.gridLayout_8.addLayout(self.horizontalLayout_5, 1, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.Button_Merge = QPushButton(self.groupBox_2)
        self.Button_Merge.setObjectName(u"Button_Merge")
        self.Button_Merge.setEnabled(True)

        self.horizontalLayout_2.addWidget(self.Button_Merge)

        self.Button_Compare = QPushButton(self.groupBox_2)
        self.Button_Compare.setObjectName(u"Button_Compare")
        self.Button_Compare.setEnabled(True)

        self.horizontalLayout_2.addWidget(self.Button_Compare)


        self.gridLayout_8.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.line_Prog_1 = QLineEdit(self.groupBox_2)
        self.line_Prog_1.setObjectName(u"line_Prog_1")
        self.line_Prog_1.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.line_Prog_1)

        self.Button_Prog_1 = QToolButton(self.groupBox_2)
        self.Button_Prog_1.setObjectName(u"Button_Prog_1")

        self.horizontalLayout_4.addWidget(self.Button_Prog_1)


        self.gridLayout_8.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.groupBox_3 = QGroupBox(self.Tools)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_9 = QGridLayout(self.groupBox_3)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.Button_C_Reset = QPushButton(self.groupBox_3)
        self.Button_C_Reset.setObjectName(u"Button_C_Reset")
        self.Button_C_Reset.setEnabled(True)

        self.gridLayout_9.addWidget(self.Button_C_Reset, 0, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_3, 2, 0, 1, 1)

        self.groupBox = QGroupBox(self.Tools)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_7 = QGridLayout(self.groupBox)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.line_Num_Ini = QLineEdit(self.groupBox)
        self.line_Num_Ini.setObjectName(u"line_Num_Ini")

        self.gridLayout.addWidget(self.line_Num_Ini, 0, 1, 1, 1)

        self.QSpin_Cantidad = QSpinBox(self.groupBox)
        self.QSpin_Cantidad.setObjectName(u"QSpin_Cantidad")
        self.QSpin_Cantidad.setMinimum(1)
        self.QSpin_Cantidad.setMaximum(9999)

        self.gridLayout.addWidget(self.QSpin_Cantidad, 0, 3, 1, 1)

        self.QSpin_SQTPLen1 = QSpinBox(self.groupBox)
        self.QSpin_SQTPLen1.setObjectName(u"QSpin_SQTPLen1")
        self.QSpin_SQTPLen1.setMinimum(1)
        self.QSpin_SQTPLen1.setMaximum(8)

        self.gridLayout.addWidget(self.QSpin_SQTPLen1, 0, 5, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 4, 1, 1)


        self.gridLayout_7.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.Button_Generar = QPushButton(self.groupBox)
        self.Button_Generar.setObjectName(u"Button_Generar")

        self.gridLayout_7.addWidget(self.Button_Generar, 1, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_4 = QGroupBox(self.Tools)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_11 = QGridLayout(self.groupBox_4)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_7 = QLabel(self.groupBox_4)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(120, 0))
        self.label_7.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_10.addWidget(self.label_7)

        self.line_Prog_hex1 = QLineEdit(self.groupBox_4)
        self.line_Prog_hex1.setObjectName(u"line_Prog_hex1")
        self.line_Prog_hex1.setEnabled(False)

        self.horizontalLayout_10.addWidget(self.line_Prog_hex1)

        self.Button_Prog_hex1 = QToolButton(self.groupBox_4)
        self.Button_Prog_hex1.setObjectName(u"Button_Prog_hex1")

        self.horizontalLayout_10.addWidget(self.Button_Prog_hex1)


        self.gridLayout_11.addLayout(self.horizontalLayout_10, 0, 0, 1, 1)

        self.Button_createpg = QPushButton(self.groupBox_4)
        self.Button_createpg.setObjectName(u"Button_createpg")
        self.Button_createpg.setEnabled(True)

        self.gridLayout_11.addWidget(self.Button_createpg, 5, 0, 1, 1)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_9 = QLabel(self.groupBox_4)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(120, 0))
        self.label_9.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_12.addWidget(self.label_9)

        self.comboBox_device = QComboBox(self.groupBox_4)
        self.comboBox_device.setObjectName(u"comboBox_device")

        self.horizontalLayout_12.addWidget(self.comboBox_device)


        self.gridLayout_11.addLayout(self.horizontalLayout_12, 2, 0, 1, 1)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_12 = QLabel(self.groupBox_4)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(120, 0))
        self.label_12.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_14.addWidget(self.label_12)

        self.line_params = QLineEdit(self.groupBox_4)
        self.line_params.setObjectName(u"line_params")
        self.line_params.setEnabled(True)

        self.horizontalLayout_14.addWidget(self.line_params)


        self.gridLayout_11.addLayout(self.horizontalLayout_14, 4, 0, 1, 1)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_10 = QLabel(self.groupBox_4)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(120, 0))
        self.label_10.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_13.addWidget(self.label_10)

        self.line_sqtp_dir = QLineEdit(self.groupBox_4)
        self.line_sqtp_dir.setObjectName(u"line_sqtp_dir")
        self.line_sqtp_dir.setEnabled(True)

        self.horizontalLayout_13.addWidget(self.line_sqtp_dir)

        self.label_11 = QLabel(self.groupBox_4)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(80, 0))
        self.label_11.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_13.addWidget(self.label_11)

        self.QSpin_SQTPLen2 = QSpinBox(self.groupBox_4)
        self.QSpin_SQTPLen2.setObjectName(u"QSpin_SQTPLen2")
        self.QSpin_SQTPLen2.setMinimum(1)
        self.QSpin_SQTPLen2.setMaximum(8)

        self.horizontalLayout_13.addWidget(self.QSpin_SQTPLen2)


        self.gridLayout_11.addLayout(self.horizontalLayout_13, 3, 0, 1, 1)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_8 = QLabel(self.groupBox_4)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(120, 0))
        self.label_8.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_11.addWidget(self.label_8)

        self.comboBox_driver = QComboBox(self.groupBox_4)
        self.comboBox_driver.setObjectName(u"comboBox_driver")

        self.horizontalLayout_11.addWidget(self.comboBox_driver)


        self.gridLayout_11.addLayout(self.horizontalLayout_11, 1, 0, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_4, 3, 0, 1, 1)

        self.tabWidget.addTab(self.Tools, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.tabWidget, self.line_Prog)
        QWidget.setTabOrder(self.line_Prog, self.Button_Prog)
        QWidget.setTabOrder(self.Button_Prog, self.line_SQTP)
        QWidget.setTabOrder(self.line_SQTP, self.Button_SQTP)
        QWidget.setTabOrder(self.Button_SQTP, self.comboBoxPort)
        QWidget.setTabOrder(self.comboBoxPort, self.Button_rescan)
        QWidget.setTabOrder(self.Button_rescan, self.check_SQTPMan)
        QWidget.setTabOrder(self.check_SQTPMan, self.line_SQTPNumber)
        QWidget.setTabOrder(self.line_SQTPNumber, self.Button_program)
        QWidget.setTabOrder(self.Button_program, self.textEdit)
        QWidget.setTabOrder(self.textEdit, self.line_Num_Ini)
        QWidget.setTabOrder(self.line_Num_Ini, self.QSpin_Cantidad)
        QWidget.setTabOrder(self.QSpin_Cantidad, self.QSpin_SQTPLen1)
        QWidget.setTabOrder(self.QSpin_SQTPLen1, self.Button_Generar)
        QWidget.setTabOrder(self.Button_Generar, self.line_Prog_1)
        QWidget.setTabOrder(self.line_Prog_1, self.Button_Prog_1)
        QWidget.setTabOrder(self.Button_Prog_1, self.line_Prog_2)
        QWidget.setTabOrder(self.line_Prog_2, self.Button_Prog_2)
        QWidget.setTabOrder(self.Button_Prog_2, self.Button_Merge)
        QWidget.setTabOrder(self.Button_Merge, self.Button_Compare)
        QWidget.setTabOrder(self.Button_Compare, self.Button_C_Reset)
        QWidget.setTabOrder(self.Button_C_Reset, self.line_Prog_hex1)
        QWidget.setTabOrder(self.line_Prog_hex1, self.Button_Prog_hex1)
        QWidget.setTabOrder(self.Button_Prog_hex1, self.comboBox_driver)
        QWidget.setTabOrder(self.comboBox_driver, self.comboBox_device)
        QWidget.setTabOrder(self.comboBox_device, self.line_sqtp_dir)
        QWidget.setTabOrder(self.line_sqtp_dir, self.line_params)
        QWidget.setTabOrder(self.line_params, self.Button_createpg)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"OmniProg", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"PG File:", None))
        self.line_Prog.setText("")
        self.Button_Prog.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"SQTP:", None))
        self.line_SQTP.setText("")
        self.Button_SQTP.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_1.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.Button_rescan.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"SQTP (hex.)", None))
        self.check_SQTPMan.setText(QCoreApplication.translate("MainWindow", u"Man.", None))
        self.line_SQTPNumber.setText("")
        self.label_PASS.setText("")
        self.Button_program.setText(QCoreApplication.translate("MainWindow", u"PRO&GRAM", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Program), QCoreApplication.translate("MainWindow", u"Program", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Hex_Tools", None))
        self.line_Prog_2.setText("")
        self.Button_Prog_2.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.Button_Merge.setText(QCoreApplication.translate("MainWindow", u"Merge", None))
        self.Button_Compare.setText(QCoreApplication.translate("MainWindow", u"Compare", None))
        self.line_Prog_1.setText("")
        self.Button_Prog_1.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Counter", None))
        self.Button_C_Reset.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"SQTP_Generate", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Quantity", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"First SQTP:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Length (Bytes)", None))
        self.Button_Generar.setText(QCoreApplication.translate("MainWindow", u"Generar", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Create PG File", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Program (hex)", None))
        self.line_Prog_hex1.setText("")
        self.Button_Prog_hex1.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.Button_createpg.setText(QCoreApplication.translate("MainWindow", u"Create PG File", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"device:", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"params", None))
        self.line_params.setText("")
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"sqtp_dir:", None))
        self.line_sqtp_dir.setText("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"sqtp_len:", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Driver:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Tools), QCoreApplication.translate("MainWindow", u"Tools", None))
    # retranslateUi

