# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'show_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)
from . import resources_rc

class Ui_ShowDialog(object):
    def setupUi(self, ShowDialog):
        if not ShowDialog.objectName():
            ShowDialog.setObjectName(u"ShowDialog")
        ShowDialog.resize(679, 589)
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(50)
        font.setKerning(True)
        ShowDialog.setFont(font)
        icon = QIcon()
        icon.addFile(u":/images/window_icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ShowDialog.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(ShowDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.title_label = QLabel(ShowDialog)
        self.title_label.setObjectName(u"title_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.title_label.sizePolicy().hasHeightForWidth())
        self.title_label.setSizePolicy(sizePolicy)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.title_label)

        self.description_label = QLabel(ShowDialog)
        self.description_label.setObjectName(u"description_label")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(20)
        font1.setKerning(True)
        self.description_label.setFont(font1)

        self.verticalLayout.addWidget(self.description_label)

        self.timeout_h_layout = QHBoxLayout()
        self.timeout_h_layout.setObjectName(u"timeout_h_layout")
        self.timeout_progress_bar = QProgressBar(ShowDialog)
        self.timeout_progress_bar.setObjectName(u"timeout_progress_bar")
        self.timeout_progress_bar.setSizeIncrement(QSize(0, 0))
        self.timeout_progress_bar.setBaseSize(QSize(0, 0))
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(20)
        font2.setBold(False)
        font2.setKerning(True)
        self.timeout_progress_bar.setFont(font2)
        self.timeout_progress_bar.setValue(24)
        self.timeout_progress_bar.setTextVisible(True)

        self.timeout_h_layout.addWidget(self.timeout_progress_bar)

        self.timeout_increase_button = QPushButton(ShowDialog)
        self.timeout_increase_button.setObjectName(u"timeout_increase_button")
        self.timeout_increase_button.setMaximumSize(QSize(50, 50))
        font3 = QFont()
        font3.setFamilies([u"Arial"])
        font3.setPointSize(30)
        font3.setKerning(True)
        self.timeout_increase_button.setFont(font3)
        icon1 = QIcon()
        icon1.addFile(u":/images/plus_icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.timeout_increase_button.setIcon(icon1)

        self.timeout_h_layout.addWidget(self.timeout_increase_button)


        self.verticalLayout.addLayout(self.timeout_h_layout)

        self.buttons_h_layout = QHBoxLayout()
        self.buttons_h_layout.setObjectName(u"buttons_h_layout")
        self.fail_button = QPushButton(ShowDialog)
        self.fail_button.setObjectName(u"fail_button")
        self.fail_button.setMaximumSize(QSize(325, 100))
        icon2 = QIcon()
        icon2.addFile(u":/images/fail_icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.fail_button.setIcon(icon2)

        self.buttons_h_layout.addWidget(self.fail_button)

        self.pass_button = QPushButton(ShowDialog)
        self.pass_button.setObjectName(u"pass_button")
        self.pass_button.setMaximumSize(QSize(325, 100))
        icon3 = QIcon()
        icon3.addFile(u":/images/pass_icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pass_button.setIcon(icon3)

        self.buttons_h_layout.addWidget(self.pass_button)


        self.verticalLayout.addLayout(self.buttons_h_layout)


        self.retranslateUi(ShowDialog)

        QMetaObject.connectSlotsByName(ShowDialog)
    # setupUi

    def retranslateUi(self, ShowDialog):
        ShowDialog.setWindowTitle(QCoreApplication.translate("ShowDialog", u"Show Dialog", None))
        self.title_label.setText(QCoreApplication.translate("ShowDialog", u"Title", None))
        self.description_label.setText(QCoreApplication.translate("ShowDialog", u"Description\n"
"multiline", None))
        self.timeout_increase_button.setText("")
        self.fail_button.setText(QCoreApplication.translate("ShowDialog", u"Fail", None))
        self.pass_button.setText(QCoreApplication.translate("ShowDialog", u"Pass", None))
    # retranslateUi

