#!/usr/bin/env python
'''
find icon，在源图查找图标。
'''

VER = r'''
fico version: 2025.8.1.1.0
'''

INFO = r'''
find icon，在源图查找图标。
依赖库
pip install opencv-python PyQt5 numpy
'''

HELP = r'''
+-------------------------------------------+
|        show pythonPkg mirror link         |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi ryto mir [option]

Options:
    -H, --help   Show help / 显示帮助
    -I, --info   Show info / 显示信息
    -V, --version   Show version / 显示版本
    -r, --run   run window / 启动图形窗口
'''

##############################

import os
import sys
import argparse
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QGroupBox, QMessageBox, 
                             QSlider, QCheckBox, QScrollArea, QSizePolicy, QLineEdit,
                             QGridLayout, QSpinBox, QComboBox, QTextEdit, QDialog)
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint, QSize, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QMouseEvent, QWheelEvent, QKeyEvent

##############################

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用帮助")
        self.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setText("""
        🎯 图标选择与查找工具使用指南
        
        📁 基本操作：
        - 打开图片：选择要处理的图像文件
        - 选择查找图标：选择要查找的目标图标
        - 保存选中图标：将选框内的区域保存为图标
        
        🎯 选框控制：
        - 固定大小模式：启用后点击图片创建固定大小的选框
        - 坐标控制：精确设置选框的位置和大小
        - 移动按钮：微调选框位置
        - 大小按钮：调整选框尺寸
        
        🔍 查找功能：
        - 匹配阈值：设置匹配的敏感度（0-1）
        - 查找区域：指定查找范围（全图、四分图、九宫图）
        - 多种查找方式：灰度、彩色、各颜色通道
        
        📐 区域代码说明：
        - 全图：f0 (整个图像)
        - 四分图：
          f1: 左上角 | f2: 右上角
          f3: 左下角 | f4: 右下角
        - 九宫图：
          n1: 左上 | n2: 中上 | n3: 右上
          n4: 左中 | n5: 中心 | n6: 右中
          n7: 左下 | n8: 中下 | n9: 右下
        
        🖱️ 视图控制：
        - 缩放：放大、缩小、适应窗口、原始大小
        - 拖动：Alt+左键 或 中键拖动图片
        - 删除选框：Delete 或 Backspace 键
        
        💡 提示：
        - 使用 WSAD 代表上下左右键微调选框位置
        - Ctrl+方向键：移动5像素
        - Shift+方向键：移动10像素
        - 固定大小模式适合批量提取相同尺寸的图标
        """)
        
        layout.addWidget(help_text)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class ScrollableImageLabel(QLabel):
    rectChanged = pyqtSignal(QRect)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.rect = QRect()
        self.dragging = False
        self.panning = False
        self.panStartPos = QPoint()
        self.startPos = None
        self.currentPos = None
        self.setMinimumSize(400, 300)
        self.setAlignment(Qt.AlignCenter)
        self.setText("请打开图片")
        self.originalPixmap = None
        self.displayPixmap = None
        self.scaleFactor = 1.0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.imageOffset = QPoint(0, 0)
        self.drawingNewRect = False
        self.fixedSizeMode = False
        self.fixedSize = QSize(100, 100)
        
    def setPixmap(self, pixmap):
        self.originalPixmap = pixmap
        if pixmap:
            # 计算初始缩放比例，使图片适应窗口
            self.calculateInitialScale()
        else:
            self.scaleFactor = 1.0
        self.imageOffset = QPoint(0, 0)
        self.updateDisplay()
        
    def calculateInitialScale(self):
        """计算初始缩放比例，使图片适应窗口"""
        if not self.originalPixmap:
            return
            
        # 获取Label的可用大小（减去边距）
        labelWidth = self.width() - 20
        labelHeight = self.height() - 20
        
        if labelWidth <= 0 or labelHeight <= 0:
            return
    
        # 计算缩放比例
        widthRatio = labelWidth / self.originalPixmap.width()
        heightRatio = labelHeight / self.originalPixmap.height()
        self.scaleFactor = min(widthRatio, heightRatio, 1.0)  # 不超过原图大小
        
    def updateDisplay(self):
        """更新显示图像"""
        if self.originalPixmap:
            scaledSize = self.originalPixmap.size() * self.scaleFactor
            self.displayPixmap = self.originalPixmap.scaled(
                scaledSize, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        else:
            self.displayPixmap = None
        self.update()
        
    def getOriginalRectPrecise(self):
        """获取在原始图像中的矩形位置（高精度）"""
        if self.rect.isNull() or self.scaleFactor == 0:
            return QRectF()
        
        # 使用浮点数计算保持精度
        originalX = self.rect.x() / self.scaleFactor
        originalY = self.rect.y() / self.scaleFactor
        originalWidth = self.rect.width() / self.scaleFactor
        originalHeight = self.rect.height() / self.scaleFactor
        
        return QRectF(originalX, originalY, originalWidth, originalHeight)

    def setRectFromOriginalPrecise(self, originalRectF):
        """根据原始图像坐标设置矩形（高精度）"""
        if originalRectF.isNull():
            self.rect = QRect()
        else:
            # 使用浮点数计算保持精度
            displayX = originalRectF.x() * self.scaleFactor
            displayY = originalRectF.y() * self.scaleFactor
            displayWidth = originalRectF.width() * self.scaleFactor
            displayHeight = originalRectF.height() * self.scaleFactor
            
            # 只在最后创建矩形时转换为整数
            self.rect = QRect(
                round(displayX),      # 使用 round() 而不是 int() 减少误差
                round(displayY),
                round(displayWidth),
                round(displayHeight)
            )
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        if self.originalPixmap:
            # 保存当前的原始矩形坐标
            originalRect = self.getOriginalRect()
            
            # 缩放控制
            degrees = event.angleDelta().y() / 8
            steps = degrees / 15
            
            # 计算缩放前的图像坐标（用于保持缩放中心）
            oldPos = self._getImagePos(event.pos())
            
            # 更新缩放因子
            oldScale = self.scaleFactor
            self.scaleFactor *= 1.1 ** steps
            self.scaleFactor = max(0.1, min(10.0, self.scaleFactor))
            
            # 调整偏移量以保持缩放中心
            scaleRatio = self.scaleFactor / oldScale
            mousePos = event.pos()
            self.imageOffset = mousePos - (mousePos - self.imageOffset) * scaleRatio
            
            # 更新矩形位置和大小（无论是否固定大小都使用原始坐标重新计算）
            if not originalRect.isNull():
                self.rect = QRect(
                    int(originalRect.x() * self.scaleFactor),
                    int(originalRect.y() * self.scaleFactor),
                    int(originalRect.width() * self.scaleFactor),
                    int(originalRect.height() * self.scaleFactor)
                )
            
            self.updateDisplay()
        
    def mousePressEvent(self, event: QMouseEvent):
        if self.originalPixmap is None:
            return
        
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier):
            # 开始拖动图片
            self.panning = True
            self.panStartPos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

        elif event.button() == Qt.LeftButton:
            imgPos = self._getImagePos(event.pos())
            
            if self.panning:
                self.panStartPos = event.pos()
                return
                
            # 开始绘制新矩形
            if self.fixedSizeMode:
                # 固定大小模式：以点击点为中心创建固定大小的矩形
                center = imgPos
                halfWidth = self.fixedSize.width() // 2
                halfHeight = self.fixedSize.height() // 2
                self.rect = QRect(center.x() - halfWidth, center.y() - halfHeight, 
                                 self.fixedSize.width(), self.fixedSize.height())
                self.rectChanged.emit(self.getOriginalRect())
                self.update()  # 立即更新显示

            else:
                # 自由绘制模式
                self.rect = QRect(imgPos, imgPos)
                self.dragging = True
                self.drawingNewRect = True
                self.startPos = imgPos
                self.rectChanged.emit(self.getOriginalRect())
        
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.originalPixmap is None:
            return
            
        if self.panning:
            # 拖动图片
            delta = event.pos() - self.panStartPos
            self.imageOffset += delta
            self.panStartPos = event.pos()
            self.update()
            return
            
        if self.dragging and self.drawingNewRect and not self.fixedSizeMode:
            # 绘制新矩形
            imgPos = self._getImagePos(event.pos())
            self.rect = QRect(self.startPos, imgPos).normalized()
            
            # 确保矩形不超出图像边界
            img_width = self.displayPixmap.width() if self.displayPixmap else 0
            img_height = self.displayPixmap.height() if self.displayPixmap else 0
            self.rect.setLeft(max(0, self.rect.left()))
            self.rect.setTop(max(0, self.rect.top()))
            self.rect.setRight(min(img_width, self.rect.right()))
            self.rect.setBottom(min(img_height, self.rect.bottom()))
            
            self.rectChanged.emit(self.getOriginalRect())
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.drawingNewRect = False
            
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier):
            self.panning = False
            self.setCursor(Qt.ArrowCursor)
    
    def paintEvent(self, event):
        if self.displayPixmap is None:
            super().paintEvent(event)
            return
            
        # 创建绘制器
        painter = QPainter(self)
        
        # 计算绘制位置（考虑偏移量）
        xOffset = (self.width() - self.displayPixmap.width()) / 2 + self.imageOffset.x()
        yOffset = (self.height() - self.displayPixmap.height()) / 2 + self.imageOffset.y()
        
        # 绘制图像
        painter.drawPixmap(int(xOffset), int(yOffset), self.displayPixmap)
        
        # 绘制矩形（如果存在）- 使用虚线
        if not self.rect.isNull():
            # 创建虚线笔
            pen = QPen(Qt.red, 2, Qt.DashLine)
            painter.setPen(pen)
            
            # 调整矩形位置（考虑偏移量）
            adjustedRect = QRect(
                self.rect.x() + int(xOffset),
                self.rect.y() + int(yOffset),
                self.rect.width(),
                self.rect.height()
            )
            painter.drawRect(adjustedRect)
    
    def _getImagePos(self, labelPos):
        if self.displayPixmap is None:
            return QPoint(0, 0)
        
        # 计算图像在Label中的位置（考虑偏移量）
        xOffset = (self.width() - self.displayPixmap.width()) / 2 + self.imageOffset.x()
        yOffset = (self.height() - self.displayPixmap.height()) / 2 + self.imageOffset.y()
        
        # 计算在显示图像中的位置
        x = int(labelPos.x() - xOffset)
        y = int(labelPos.y() - yOffset)
        
        # 确保位置在图像范围内
        x = max(0, min(x, self.displayPixmap.width() - 1))
        y = max(0, min(y, self.displayPixmap.height() - 1))
        
        return QPoint(x, y)
    
    def getOriginalRect(self):
        """获取在原始图像中的矩形位置"""
        if self.rect.isNull() or self.scaleFactor == 0:
            return QRect()
        
        # 将显示坐标转换回原始图像坐标
        originalX = int(self.rect.x() / self.scaleFactor)
        originalY = int(self.rect.y() / self.scaleFactor)
        originalWidth = int(self.rect.width() / self.scaleFactor)
        originalHeight = int(self.rect.height() / self.scaleFactor)
        
        return QRect(originalX, originalY, originalWidth, originalHeight)
    
    def setRectFromOriginal(self, originalRect):
        """根据原始图像坐标设置矩形"""
        if originalRect.isNull():
            self.rect = QRect()
        else:
            self.rect = QRect(
                int(originalRect.x() * self.scaleFactor),
                int(originalRect.y() * self.scaleFactor),
                int(originalRect.width() * self.scaleFactor),
                int(originalRect.height() * self.scaleFactor)
            )
        self.update()
    
    def moveRect(self, dx, dy):
        """移动矩形"""
        if not self.rect.isNull():
            img_width = self.displayPixmap.width() if self.displayPixmap else 0
            img_height = self.displayPixmap.height() if self.displayPixmap else 0
            
            newX = max(0, min(self.rect.x() + dx, img_width - self.rect.width()))
            newY = max(0, min(self.rect.y() + dy, img_height - self.rect.height()))
            
            self.rect.moveTo(newX, newY)
            self.rectChanged.emit(self.getOriginalRect())
            self.update()
    
    def resizeRect(self, dw, dh):
        """调整矩形大小"""
        if not self.rect.isNull():
            img_width = self.displayPixmap.width() if self.displayPixmap else 0
            img_height = self.displayPixmap.height() if self.displayPixmap else 0
            
            newWidth = max(10, min(self.rect.width() + dw, img_width - self.rect.x()))
            newHeight = max(10, min(self.rect.height() + dh, img_height - self.rect.y()))
            
            self.rect.setSize(QSize(newWidth, newHeight))
            self.rectChanged.emit(self.getOriginalRect())
            self.update()
    
    def setRectPosition(self, x, y):
        """设置矩形位置"""
        if not self.rect.isNull():
            img_width = self.displayPixmap.width() if self.displayPixmap else 0
            img_height = self.displayPixmap.height() if self.displayPixmap else 0
            
            newX = max(0, min(x, img_width - self.rect.width()))
            newY = max(0, min(y, img_height - self.rect.height()))
            
            self.rect.moveTo(newX, newY)
            self.rectChanged.emit(self.getOriginalRect())
            self.update()
    
    def setRectSize(self, width, height):
        """设置矩形大小"""
        if not self.rect.isNull():
            img_width = self.displayPixmap.width() if self.displayPixmap else 0
            img_height = self.displayPixmap.height() if self.displayPixmap else 0
            
            newWidth = max(10, min(width, img_width - self.rect.x()))
            newHeight = max(10, min(height, img_height - self.rect.y()))
            
            self.rect.setSize(QSize(newWidth, newHeight))
            self.rectChanged.emit(self.getOriginalRect())
            self.update()
    
    def clearRect(self):
        """清除选框"""
        self.rect = QRect()
        self.rectChanged.emit(self.rect)
        self.update()
    
    def resizeEvent(self, event):
        """窗口大小改变时重新计算缩放"""
        super().resizeEvent(event)
        if self.originalPixmap:
            oldScale = self.scaleFactor
            self.calculateInitialScale()
            self.updateDisplay()
            
            # 更新矩形位置和大小
            if not self.rect.isNull():
                scaleRatio = self.scaleFactor / oldScale
                self.rect = QRect(
                    int(self.rect.x() * scaleRatio),
                    int(self.rect.y() * scaleRatio),
                    int(self.rect.width() * scaleRatio),
                    int(self.rect.height() * scaleRatio)
                )

#####

class IconFinderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图标选择与查找工具")
        self.setGeometry(100, 100, 1400, 800)
        
        self.currentImage = None
        self.iconImage = None
        self.saveDirectory = ""
        self.currentViewState = None
        
        self.initUI()
        
    def initUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        mainLayout = QHBoxLayout(centralWidget)
        
        # 左侧控制面板
        controlPanel = QWidget()
        controlPanel.setFixedWidth(320)
        controlLayout = QVBoxLayout(controlPanel)
        
        # 选择图片区域
        selectGroup = QGroupBox("选择图片")
        selectLayout = QVBoxLayout(selectGroup)
        
        # 第一行：打开图片和帮助按钮
        fileLayout = QHBoxLayout()
        self.selectImageBtn = QPushButton("打开图片")
        self.selectImageBtn.clicked.connect(self.openImage)
        self.helpBtn = QPushButton("帮助")
        self.helpBtn.clicked.connect(self.showHelp)
        fileLayout.addWidget(self.selectImageBtn)
        fileLayout.addWidget(self.helpBtn)
        selectLayout.addLayout(fileLayout)
        
        # 缩放控制
        zoomLayout = QHBoxLayout()
        zoomLayout.addWidget(QLabel("缩放:"))
        self.zoomInBtn = QPushButton("放大")
        self.zoomInBtn.clicked.connect(self.zoomIn)
        self.zoomOutBtn = QPushButton("缩小")
        self.zoomOutBtn.clicked.connect(self.zoomOut)
        self.winZoomBtn = QPushButton("窗口")
        self.winZoomBtn.clicked.connect(self.winZoom)
        self.resetZoomBtn = QPushButton("原始")
        self.resetZoomBtn.clicked.connect(self.resetZoom)
        zoomLayout.addWidget(self.zoomInBtn)
        zoomLayout.addWidget(self.zoomOutBtn)
        zoomLayout.addWidget(self.winZoomBtn)
        zoomLayout.addWidget(self.resetZoomBtn)
        selectLayout.addLayout(zoomLayout)
        
        selectLayout.addWidget(QLabel("提示: 按住Alt+左键或按鼠标中键拖动图片"))
        controlLayout.addWidget(selectGroup)
        
        # 选框控制区域
        rectControlGroup = QGroupBox("选框控制")
        rectLayout = QVBoxLayout(rectControlGroup)
        
        # 固定大小模式
        fixedSizeLayout = QHBoxLayout()
        self.fixedSizeCheck = QCheckBox("固定大小")
        self.fixedSizeCheck.stateChanged.connect(self.toggleFixedSizeMode)
        fixedSizeLayout.addWidget(self.fixedSizeCheck)
        
        self.fixedWidthEdit = QSpinBox()
        self.fixedWidthEdit.setRange(10, 1000)
        self.fixedWidthEdit.setValue(100)
        self.fixedWidthEdit.valueChanged.connect(self.updateFixedSize)
        self.fixedHeightEdit = QSpinBox()
        self.fixedHeightEdit.setRange(10, 1000)
        self.fixedHeightEdit.setValue(100)
        self.fixedHeightEdit.valueChanged.connect(self.updateFixedSize)
        
        w_label = QLabel("W:")
        w_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 右对齐且垂直居中
        fixedSizeLayout.addWidget(w_label)
        fixedSizeLayout.addWidget(self.fixedWidthEdit)
        h_label = QLabel("H:")
        h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 右对齐且垂直居中
        fixedSizeLayout.addWidget(h_label)
        fixedSizeLayout.addWidget(self.fixedHeightEdit)
        rectLayout.addLayout(fixedSizeLayout)
        
        # 坐标控制
        coordLayout = QGridLayout()
        coordLayout.addWidget(QLabel("坐标:"), 0, 0, 1, 4)
        
        x_label = QLabel("X:")
        x_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        coordLayout.addWidget(x_label, 1, 0)
        self.xSpinBox = QSpinBox()
        self.xSpinBox.setRange(0, 10000)
        self.xSpinBox.valueChanged.connect(self.updateRectFromSpinBox)
        coordLayout.addWidget(self.xSpinBox, 1, 1)
        
        y_label = QLabel("Y:")
        y_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        coordLayout.addWidget(y_label, 1, 2)
        self.ySpinBox = QSpinBox()
        self.ySpinBox.setRange(0, 10000)
        self.ySpinBox.valueChanged.connect(self.updateRectFromSpinBox)
        coordLayout.addWidget(self.ySpinBox, 1, 3)
        
        w_label = QLabel("W:")
        w_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        coordLayout.addWidget(w_label, 1, 4)
        self.widthSpinBox = QSpinBox()
        self.widthSpinBox.setRange(10, 10000)
        self.widthSpinBox.valueChanged.connect(self.updateRectFromSpinBox)
        coordLayout.addWidget(self.widthSpinBox, 1, 5)
        
        h_label = QLabel("H:")
        h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        coordLayout.addWidget(h_label, 1, 6)
        self.heightSpinBox = QSpinBox()
        self.heightSpinBox.setRange(10, 10000)
        self.heightSpinBox.valueChanged.connect(self.updateRectFromSpinBox)
        coordLayout.addWidget(self.heightSpinBox, 1, 7)
        
        rectLayout.addLayout(coordLayout)
        
        # 移动控制
        moveLayout = QGridLayout()
        moveLayout.addWidget(QLabel("移动:"), 0, 0, 1, 3)
        
        self.moveUpBtn = QPushButton("↑")
        self.moveDownBtn = QPushButton("↓")
        self.moveLeftBtn = QPushButton("←")
        self.moveRightBtn = QPushButton("→")
        
        self.moveUpBtn.clicked.connect(lambda: self.moveRect(0, -1))
        self.moveDownBtn.clicked.connect(lambda: self.moveRect(0, 1))
        self.moveLeftBtn.clicked.connect(lambda: self.moveRect(-1, 0))
        self.moveRightBtn.clicked.connect(lambda: self.moveRect(1, 0))
        
        moveLayout.addWidget(self.moveUpBtn, 1, 0)
        moveLayout.addWidget(self.moveDownBtn, 1, 1)
        moveLayout.addWidget(self.moveLeftBtn, 1, 2)
        moveLayout.addWidget(self.moveRightBtn, 1, 3)
        
        rectLayout.addLayout(moveLayout)
        
        # 大小控制
        sizeLayout = QGridLayout()
        sizeLayout.addWidget(QLabel("大小:"), 0, 0, 1, 3)
        
        self.shorterBtn = QPushButton("↑")
        self.tallerBtn = QPushButton("↓")
        self.narrowerBtn = QPushButton("←")
        self.widerBtn = QPushButton("→")
        
        self.shorterBtn.clicked.connect(lambda: self.resizeRect(0, -1))
        self.tallerBtn.clicked.connect(lambda: self.resizeRect(0, 1))
        self.narrowerBtn.clicked.connect(lambda: self.resizeRect(-1, 0))
        self.widerBtn.clicked.connect(lambda: self.resizeRect(1, 0))
        
        sizeLayout.addWidget(self.shorterBtn, 1, 0)
        sizeLayout.addWidget(self.tallerBtn, 1, 1)
        sizeLayout.addWidget(self.narrowerBtn, 1, 2)
        sizeLayout.addWidget(self.widerBtn, 1, 3)
        
        rectLayout.addLayout(sizeLayout)
        
        # 删除选框
        self.clearRectBtn = QPushButton("删除选框")
        self.clearRectBtn.clicked.connect(self.clearRectangle)
        self.clearRectBtn.setEnabled(False)
        rectLayout.addWidget(self.clearRectBtn)
        
        controlLayout.addWidget(rectControlGroup)
        
        # 保存图标区域
        iconGroup = QGroupBox("保存图标")
        iconLayout = QVBoxLayout(iconGroup)
        
        # 图标名称输入
        nameLayout = QHBoxLayout()
        nameLayout.addWidget(QLabel("图标名称:"))
        self.iconNameEdit = QLineEdit("ico_")
        nameLayout.addWidget(self.iconNameEdit)
        iconLayout.addLayout(nameLayout)
        
        saveLayout = QGridLayout()
        self.selectSaveDirBtn = QPushButton("选择目录")
        self.selectSaveDirBtn.clicked.connect(self.selectSaveDirectory)
        saveLayout.addWidget(self.selectSaveDirBtn, 0, 0)
        
        self.saveIconBtn = QPushButton("开始保存")
        self.saveIconBtn.clicked.connect(self.saveIcon)
        self.saveIconBtn.setEnabled(False)
        saveLayout.addWidget(self.saveIconBtn, 0, 1)

        iconLayout.addLayout(saveLayout)
        controlLayout.addWidget(iconGroup)
        
        # 查找图标区域
        findGroup = QGroupBox("查找图标")
        findLayout = QVBoxLayout(findGroup)
        
        # 选择查找图标和区域选择
        iconSelectLayout = QHBoxLayout()
        self.selectIconBtn = QPushButton("选择查找图标")
        self.selectIconBtn.clicked.connect(self.selectIconImage)
        
        # 查找区域选择
        self.searchRegionCombo = QComboBox()
        self.searchRegionCombo.addItems([
            "全图 (f0)", "左上 (f1)", "右上 (f2)", "左下 (f3)", "右下 (f4)",
            "左上 (n1)", "中上 (n2)", "右上 (n3)", "左中 (n4)", "中心 (n5)",
            "右中 (n6)", "左下 (n7)", "中下 (n8)", "右下 (n9)"
        ])
        self.searchRegionCombo.setCurrentIndex(0)
        
        iconSelectLayout.addWidget(self.selectIconBtn)
        iconSelectLayout.addWidget(self.searchRegionCombo)
        findLayout.addLayout(iconSelectLayout)
        
        # 查找选项
        optionsLayout = QHBoxLayout()
        optionsLayout.addWidget(QLabel("匹配阈值:"))
        self.thresholdSlider = QSlider(Qt.Horizontal)
        self.thresholdSlider.setRange(0, 100)
        self.thresholdSlider.setValue(80)
        optionsLayout.addWidget(self.thresholdSlider)
        self.thresholdLabel = QLabel("0.8")
        optionsLayout.addWidget(self.thresholdLabel)
        findLayout.addLayout(optionsLayout)
        
        # 多种查找方式按钮
        findMethodsLayout = QGridLayout()
        findMethodsLayout.addWidget(QLabel("查找方式:"), 0, 0, 1, 3)
        
        self.grayFindBtn = QPushButton("灰度")
        self.colorFindBtn = QPushButton("彩色")
        self.redFindBtn = QPushButton("红色")
        self.greenFindBtn = QPushButton("绿色")
        self.blueFindBtn = QPushButton("蓝色")
        self.clearMarksBtn = QPushButton("清除标记")
        
        self.grayFindBtn.clicked.connect(lambda: self.findIcon("gray"))
        self.colorFindBtn.clicked.connect(lambda: self.findIcon("color"))
        self.redFindBtn.clicked.connect(lambda: self.findIcon("red"))
        self.greenFindBtn.clicked.connect(lambda: self.findIcon("green"))
        self.blueFindBtn.clicked.connect(lambda: self.findIcon("blue"))
        self.clearMarksBtn.clicked.connect(self.clearMarks)
        
        findMethodsLayout.addWidget(self.grayFindBtn, 1, 0)
        findMethodsLayout.addWidget(self.colorFindBtn, 1, 1)
        findMethodsLayout.addWidget(self.redFindBtn, 1, 2)
        findMethodsLayout.addWidget(self.greenFindBtn, 2, 0)
        findMethodsLayout.addWidget(self.blueFindBtn, 2, 1)
        findMethodsLayout.addWidget(self.clearMarksBtn, 2, 2)
        
        findLayout.addLayout(findMethodsLayout)
        
        controlLayout.addWidget(findGroup)
        
        # 结果显示区域
        resultGroup = QGroupBox("结果")
        resultLayout = QVBoxLayout(resultGroup)
        self.resultLabel = QLabel("等待操作...")
        resultLayout.addWidget(self.resultLabel)
        controlLayout.addWidget(resultGroup)
        
        controlLayout.addStretch()
        
        # 右侧图像显示区域
        self.imageLabel = ScrollableImageLabel()
        self.imageLabel.rectChanged.connect(self.onRectChanged)
        
        mainLayout.addWidget(controlPanel)
        mainLayout.addWidget(self.imageLabel, 1)
        
        # 连接信号
        self.thresholdSlider.valueChanged.connect(self.updateThresholdLabel)
        
        # 初始化按钮状态
        self.updateButtonStates()
    
    def updateButtonStates(self):
        """更新按钮状态"""
        hasRect = not self.imageLabel.rect.isNull() if self.imageLabel.originalPixmap else False
        hasIcon = self.iconImage is not None
        hasImage = self.currentImage is not None
        
        # 选框控制按钮
        for btn in [self.moveUpBtn, self.moveDownBtn, self.moveLeftBtn, self.moveRightBtn,
                   self.widerBtn, self.narrowerBtn,
                   self.tallerBtn, self.shorterBtn, self.clearRectBtn]:
            btn.setEnabled(hasRect)
        
        # 坐标输入框
        for spinBox in [self.xSpinBox, self.ySpinBox, self.widthSpinBox, self.heightSpinBox]:
            spinBox.setEnabled(hasRect)
        
        # 保存按钮
        self.saveIconBtn.setEnabled(hasRect)
        
        # 查找按钮
        for btn in [self.grayFindBtn, self.colorFindBtn, self.redFindBtn, 
                   self.greenFindBtn, self.blueFindBtn, self.clearMarksBtn]:
            btn.setEnabled(hasIcon and hasImage)
        
    def toggleFixedSizeMode(self, state):
        """切换固定大小模式"""
        self.imageLabel.fixedSizeMode = state == Qt.Checked
        if self.imageLabel.fixedSizeMode:
            self.imageLabel.fixedSize = QSize(
                self.fixedWidthEdit.value(),
                self.fixedHeightEdit.value()
            )
        
    def updateFixedSize(self):
        """更新固定大小"""
        if self.imageLabel.fixedSizeMode:
            self.imageLabel.fixedSize = QSize(
                self.fixedWidthEdit.value(),
                self.fixedHeightEdit.value()
            )
        
    def updateRectFromSpinBox(self):
        """从SpinBox更新矩形"""
        if not self.imageLabel.rect.isNull():
            x = self.xSpinBox.value()
            y = self.ySpinBox.value()
            width = self.widthSpinBox.value()
            height = self.heightSpinBox.value()
            
            # 转换为显示坐标
            displayX = int(x * self.imageLabel.scaleFactor)
            displayY = int(y * self.imageLabel.scaleFactor)
            displayWidth = int(width * self.imageLabel.scaleFactor)
            displayHeight = int(height * self.imageLabel.scaleFactor)
            
            self.imageLabel.setRectPosition(displayX, displayY)
            self.imageLabel.setRectSize(displayWidth, displayHeight)
        
    def zoomIn(self):
        try:
            if self.imageLabel.originalPixmap:
                # 保存当前视图状态
                self.saveViewState()
                
                # 保存当前的高精度原始矩形坐标
                originalRectF = self.imageLabel.getOriginalRectPrecise()
                
                oldScale = self.imageLabel.scaleFactor
                self.imageLabel.scaleFactor *= 1.1
                self.imageLabel.scaleFactor = min(10.0, self.imageLabel.scaleFactor)
                
                # 更新矩形位置和大小（使用高精度重新计算）
                if not originalRectF.isNull():
                    self.imageLabel.setRectFromOriginalPrecise(originalRectF)
                
                self.imageLabel.updateDisplay()
        except Exception as e:
            print(f"zoomIn error: {e}")

    def zoomOut(self):
        try:
            if self.imageLabel.originalPixmap:
                # 保存当前视图状态
                self.saveViewState()
                
                # 保存当前的高精度原始矩形坐标
                originalRectF = self.imageLabel.getOriginalRectPrecise()
                
                oldScale = self.imageLabel.scaleFactor
                self.imageLabel.scaleFactor /= 1.1
                self.imageLabel.scaleFactor = max(0.1, self.imageLabel.scaleFactor)
                
                # 更新矩形位置和大小（使用高精度重新计算）
                if not originalRectF.isNull():
                    self.imageLabel.setRectFromOriginalPrecise(originalRectF)
                
                self.imageLabel.updateDisplay()
        except Exception as e:
            print(f"zoomOut error: {e}")

    def winZoom(self):
        """将图片缩放到窗口大小"""
        try:
            if self.imageLabel.originalPixmap:
                # 保存当前视图状态
                self.saveViewState()
                
                # 保存当前的高精度原始矩形坐标
                originalRectF = self.imageLabel.getOriginalRectPrecise()
                
                # 计算适合窗口的缩放比例
                self.imageLabel.calculateInitialScale()
                
                # 更新矩形位置和大小（使用高精度重新计算）
                if not originalRectF.isNull():
                    self.imageLabel.setRectFromOriginalPrecise(originalRectF)
                
                # 重置偏移量
                self.imageLabel.imageOffset = QPoint(0, 0)
                
                # 更新显示
                self.imageLabel.updateDisplay()
                
                # 更新坐标显示
                self.updateCoordinateDisplay()
        except Exception as e:
            print(f"winZoom error: {e}")

    def resetZoom(self):
        try:
            if self.imageLabel.originalPixmap:
                # 保存当前视图状态
                self.saveViewState()
                
                # 保存当前的高精度原始矩形坐标
                originalRectF = self.imageLabel.getOriginalRectPrecise()
                
                oldScale = self.imageLabel.scaleFactor
                self.imageLabel.scaleFactor = 1.0
                self.imageLabel.imageOffset = QPoint(0, 0)
                
                # 更新矩形位置和大小（使用高精度重新计算）
                if not originalRectF.isNull():
                    self.imageLabel.setRectFromOriginalPrecise(originalRectF)
                
                self.imageLabel.updateDisplay()
        except Exception as e:
            print(f"resetZoom error: {e}")
    
    def updateCoordinateDisplay(self):
        """更新坐标SpinBox显示"""
        if not self.imageLabel.rect.isNull():
            originalRect = self.imageLabel.getOriginalRect()
            
            self.xSpinBox.blockSignals(True)
            self.ySpinBox.blockSignals(True)
            self.widthSpinBox.blockSignals(True)
            self.heightSpinBox.blockSignals(True)
            
            self.xSpinBox.setValue(originalRect.x())
            self.ySpinBox.setValue(originalRect.y())
            self.widthSpinBox.setValue(originalRect.width())
            self.heightSpinBox.setValue(originalRect.height())
            
            self.xSpinBox.blockSignals(False)
            self.ySpinBox.blockSignals(False)
            self.widthSpinBox.blockSignals(False)
            self.heightSpinBox.blockSignals(False)

    def saveViewState(self):
        """保存当前视图状态"""
        if self.imageLabel.originalPixmap:
            self.currentViewState = {
                'scaleFactor': self.imageLabel.scaleFactor,
                'imageOffset': self.imageLabel.imageOffset,
                'rect': self.imageLabel.rect
            }
    
    def restoreViewState(self):
        """恢复视图状态"""
        if self.currentViewState and self.imageLabel.originalPixmap:
            self.imageLabel.scaleFactor = self.currentViewState['scaleFactor']
            self.imageLabel.imageOffset = self.currentViewState['imageOffset']
            self.imageLabel.rect = self.currentViewState['rect']
            self.imageLabel.updateDisplay()
        
    def updateThresholdLabel(self, value):
        self.thresholdLabel.setText(f"{value/100:.2f}")
        
    def openImage(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "打开图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.tif)")
        if filePath:
            try:
                # 使用OpenCV读取图片
                self.currentImage = cv2.imread(filePath)
                if self.currentImage is not None:
                    # 转换颜色空间从BGR到RGB
                    height, width, channel = self.currentImage.shape
                    bytesPerLine = 3 * width
                    rgb_image = cv2.cvtColor(self.currentImage, cv2.COLOR_BGR2RGB)
                    qImg = QImage(rgb_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qImg)
                    self.imageLabel.setPixmap(pixmap)
                    self.imageLabel.clearRect()
                    self.resultLabel.setText("图片已加载")
                    self.updateButtonStates()
                else:
                    QMessageBox.warning(self, "错误", "无法加载图片")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载图片时发生错误: {str(e)}")
                
    def selectIconImage(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "选择查找图标", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.tif)")
        if filePath:
            try:
                iconImage = cv2.imread(filePath)
                if iconImage is not None:
                    self.iconImage = iconImage
                    self.resultLabel.setText(f"已选择查找图标: {os.path.basename(filePath)}")
                    self.updateButtonStates()
                else:
                    QMessageBox.warning(self, "错误", "无法加载图标图片")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载图标图片时发生错误: {str(e)}")
                
    def onRectChanged(self, rect):
        # 更新SpinBox显示
        if not rect.isNull():
            self.xSpinBox.blockSignals(True)
            self.ySpinBox.blockSignals(True)
            self.widthSpinBox.blockSignals(True)
            self.heightSpinBox.blockSignals(True)
            
            self.xSpinBox.setValue(rect.x())
            self.ySpinBox.setValue(rect.y())
            self.widthSpinBox.setValue(rect.width())
            self.heightSpinBox.setValue(rect.height())
            
            self.xSpinBox.blockSignals(False)
            self.ySpinBox.blockSignals(False)
            self.widthSpinBox.blockSignals(False)
            self.heightSpinBox.blockSignals(False)
        
        self.updateButtonStates()
        
    def moveRect(self, dx, dy):
        # 根据按键状态调整移动步长
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier:
            dx *= 5
            dy *= 5
        elif modifiers & Qt.ShiftModifier:
            dx *= 10
            dy *= 10
        
        self.imageLabel.moveRect(dx, dy)
        
    def resizeRect(self, dw, dh):
        # 根据按键状态调整大小步长
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier:
            dw *= 5
            dh *= 5
        elif modifiers & Qt.ShiftModifier:
            dw *= 10
            dh *= 10
        
        self.imageLabel.resizeRect(dw, dh)
        
    def clearRectangle(self):
        self.imageLabel.clearRect()
        
    def clearMarks(self):
        """清除查找标记"""
        if self.currentImage is not None:
            # 恢复原始图像显示
            height, width, channel = self.currentImage.shape
            bytesPerLine = 3 * width
            rgb_image = cv2.cvtColor(self.currentImage, cv2.COLOR_BGR2RGB)
            qImg = QImage(rgb_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            
            # 恢复之前的视图状态
            self.imageLabel.originalPixmap = pixmap
            self.restoreViewState()
            
            self.resultLabel.setText("已清除查找标记")
        
    def selectSaveDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if directory:
            self.saveDirectory = directory
            self.resultLabel.setText(f"保存目录: {directory}")
            
    def saveIcon(self):
        if self.currentImage is None or self.imageLabel.rect.isNull():
            return
            
        if not self.saveDirectory:
            QMessageBox.warning(self, "警告", "请先选择保存目录")
            return
            
        # 获取在原始图像坐标中的矩形
        rect = self.imageLabel.getOriginalRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        
        # 确保矩形在图像范围内
        imgHeight, imgWidth = self.currentImage.shape[:2]
        x = max(0, min(x, imgWidth - 1))
        y = max(0, min(y, imgHeight - 1))
        w = min(w, imgWidth - x)
        h = min(h, imgHeight - y)
        
        if w <= 0 or h <= 0:
            QMessageBox.warning(self, "错误", "选择的区域无效")
            return
            
        # 保存图标
        icon = self.currentImage[y:y+h, x:x+w]
        
        # 获取图标名称
        iconName = self.iconNameEdit.text().strip()
        if not iconName:
            iconName = "icon"
        
        # 生成保存文件名
        extension = ".png"
        counter = 1
        savePath = os.path.join(self.saveDirectory, f"{iconName}{extension}")
        
        # 如果文件已存在，添加数字后缀
        while os.path.exists(savePath):
            savePath = os.path.join(self.saveDirectory, f"{iconName}{counter}{extension}")
            counter += 1
            
        success = cv2.imwrite(savePath, icon)
        
        if success:
            self.iconImage = icon
            self.resultLabel.setText(f"图标已保存: {savePath}\n尺寸: {w}x{h} 像素")
            self.updateButtonStates()
        else:
            QMessageBox.warning(self, "错误", "保存图标失败")
        
    def showHelp(self):
        """显示帮助信息"""
        dialog = HelpDialog(self)
        dialog.exec_()
    
    def getSearchRegion(self):
        """获取选择的查找区域"""
        region_text = self.searchRegionCombo.currentText()
        
        if region_text == "全图 (f0)":
            return None  # 全图
        
        # 解析区域代码
        if "f1" in region_text: return "f1"  # 左上
        if "f2" in region_text: return "f2"  # 右上
        if "f3" in region_text: return "f3"  # 左下
        if "f4" in region_text: return "f4"  # 右下
        if "n1" in region_text: return "n1"  # 左上
        if "n2" in region_text: return "n2"  # 中上
        if "n3" in region_text: return "n3"  # 右上
        if "n4" in region_text: return "n4"  # 左中
        if "n5" in region_text: return "n5"  # 中心
        if "n6" in region_text: return "n6"  # 右中
        if "n7" in region_text: return "n7"  # 左下
        if "n8" in region_text: return "n8"  # 中下
        if "n9" in region_text: return "n9"  # 右下
        
        return None  # 默认全图
    
    def getRegionRect(self, region_code, image_shape):
        """根据区域代码获取对应的图像区域"""
        if not region_code or region_code == "f0":
            return None  # 全图
        
        height, width = image_shape[:2]
        
        if region_code.startswith('f'):  # 四分图
            if region_code == "f1":  # 左上
                return (0, 0, width//2, height//2)
            elif region_code == "f2":  # 右上
                return (width//2, 0, width//2, height//2)
            elif region_code == "f3":  # 左下
                return (0, height//2, width//2, height//2)
            elif region_code == "f4":  # 右下
                return (width//2, height//2, width//2, height//2)
        
        elif region_code.startswith('n'):  # 九宫图
            third_w = width // 3
            third_h = height // 3
            
            regions = {
                "n1": (0, 0, third_w, third_h),                    # 左上
                "n2": (third_w, 0, third_w, third_h),              # 中上
                "n3": (2*third_w, 0, third_w, third_h),            # 右上
                "n4": (0, third_h, third_w, third_h),              # 左中
                "n5": (third_w, third_h, third_w, third_h),        # 中心
                "n6": (2*third_w, third_h, third_w, third_h),      # 右中
                "n7": (0, 2*third_h, third_w, third_h),            # 左下
                "n8": (third_w, 2*third_h, third_w, third_h),      # 中下
                "n9": (2*third_w, 2*third_h, third_w, third_h)     # 右下
            }
            
            return regions.get(region_code, None)
        
        return None

    def findIcon(self, mode="color"):
        if self.currentImage is None or self.iconImage is None:
            return
            
        # 保存当前视图状态
        self.saveViewState()
            
        # 获取匹配阈值
        threshold = self.thresholdSlider.value() / 100
        
        # 获取查找区域
        region_code = self.getSearchRegion()
        search_region = self.getRegionRect(region_code, self.currentImage.shape)
        
        try:
            # 根据模式选择查找方式
            if mode == "gray":
                source = cv2.cvtColor(self.currentImage, cv2.COLOR_BGR2GRAY)
                template = cv2.cvtColor(self.iconImage, cv2.COLOR_BGR2GRAY)
            elif mode == "color":
                source = self.currentImage
                template = self.iconImage
            elif mode == "red":
                source_red = self.currentImage[:, :, 2]
                template_red = self.iconImage[:, :, 2]
                result = cv2.matchTemplate(source_red, template_red, cv2.TM_CCOEFF_NORMED)
            elif mode == "green":
                source_green = self.currentImage[:, :, 1]
                template_green = self.iconImage[:, :, 1]
                result = cv2.matchTemplate(source_green, template_green, cv2.TM_CCOEFF_NORMED)
            elif mode == "blue":
                source_blue = self.currentImage[:, :, 0]
                template_blue = self.iconImage[:, :, 0]
                result = cv2.matchTemplate(source_blue, template_blue, cv2.TM_CCOEFF_NORMED)
            
            # 如果不是颜色通道模式，执行模板匹配
            if not mode.startswith(('red', 'green', 'blue')):
                result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
            
            # 如果指定了查找区域，只在该区域内查找
            if search_region:
                x, y, w, h = search_region
                # 创建区域掩码
                region_mask = np.zeros_like(result)
                region_mask[y:y+h, x:x+w] = 1
                # 只在该区域内查找匹配
                result = result * region_mask
            
            locations = np.where(result >= threshold)
            
            # 绘制匹配结果
            output = self.currentImage.copy()
            h, w = self.iconImage.shape[:2]
            
            # 使用非极大值抑制来避免重叠的矩形
            points = list(zip(*locations[::-1]))
            picked_points = self.non_max_suppression(points, w, h, 0.3)
            
            for pt in picked_points:
                cv2.rectangle(output, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
            
            # 如果指定了查找区域，绘制区域边界
            if search_region:
                x, y, w, h = search_region
                cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(output, f"Search Region: {region_code}", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            # 显示结果（保持当前视图状态）
            height, width, channel = output.shape
            bytesPerLine = 3 * width
            rgb_image = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
            qImg = QImage(rgb_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            
            # 更新图像但保持视图状态
            self.imageLabel.originalPixmap = pixmap
            self.restoreViewState()
            
            mode_names = {
                "gray": "灰度", "color": "彩色", 
                "red": "红色通道", "green": "绿色通道", "blue": "蓝色通道"
            }
            
            region_name = "全图" if not region_code else f"区域 {region_code}"
            self.resultLabel.setText(f"{mode_names[mode]}查找 ({region_name}): 找到 {len(picked_points)} 个匹配位置")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查找图标时发生错误: {str(e)}")

    def non_max_suppression(self, points, w, h, overlapThresh):
        if len(points) == 0:
            return []
            
        # 将点转换为矩形
        rects = [[x, y, x + w, y + h] for (x, y) in points]
        rects = np.array(rects, dtype=np.float32)
        
        # 执行非极大值抑制
        pick = []
        x1 = rects[:, 0]
        y1 = rects[:, 1]
        x2 = rects[:, 2]
        y2 = rects[:, 3]
        
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)
        
        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])
            
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)
            
            overlap = (w * h) / area[idxs[:last]]
            
            idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))
            
        return [points[i] for i in pick]
    
    def keyPressEvent(self, event: QKeyEvent):
        """键盘事件处理"""
        if self.imageLabel.originalPixmap is None:
            return
            
        # 方向键移动选框
        if not self.imageLabel.rect.isNull():
            if event.key() == Qt.Key_A:
                self.moveRect(-1, 0)
            elif event.key() == Qt.Key_D:
                self.moveRect(1, 0)
            elif event.key() == Qt.Key_W:
                self.moveRect(0, -1)
            elif event.key() == Qt.Key_S:
                self.moveRect(0, 1)
                
        # 删除选框
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            self.clearRectangle()

def run_win(run):
    '''
    启动图形窗口。
    '''
    if run:
        app = QApplication(sys.argv)
        window = IconFinderApp()
        window.show()
        sys.exit(app.exec_())
    else:
        if sys.platform == "win32":
            pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
            script_path = Path(__file__).resolve()
            cmd = f'start "" "{pythonw_path}" "{script_path}" -r --win'
            subprocess.Popen(cmd, shell=True, start_new_session=True)
        else:
            # Linux/macOS
            script_path = Path(__file__).resolve()
            cmd = [sys.executable, str(script_path), "-r", "--win"]
            subprocess.Popen(cmd, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("\nGUI 已在后台启动，当前命令行可安全关闭。")
        sys.exit(0)

def main(args=None):
    '''
    入口主函数。
    返回: void
    参数列表：
        args (str): 参数列表，通过命令行传入或调用者传入。
    '''

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-H', '--help', action='store_true')
    parser.add_argument('-I', '--info', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument('-r', '--run', action='store_true')
    parser.add_argument('--win', action='store_true')

    args = parser.parse_args(args)

    if args.version:
        print(VER)
    elif args.info:
        print(INFO)
    elif args.run:
        run_win(args.win)
    else:
        print(HELP)

if __name__ == '__main__':
    main()