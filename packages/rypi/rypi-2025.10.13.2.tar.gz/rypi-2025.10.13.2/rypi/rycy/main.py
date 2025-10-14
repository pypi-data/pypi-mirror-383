#!/usr/bin/env python
'''
RyCy: 锐色，HSB 拾色器 14 彩。
'''

VER = r'''
RyCy Version: 2025.8.1.1.0
'''

INFO = r'''
锐色RyCy 是一款 HSB 拾色器，只有14种色相(彩度)，分别是：红色(Red)，橙色(Orange)，金色(Gold)，黄色(Yellow)，黄绿(Chartreuse)，春绿(Spring-Greens)，绿色(Green)，青绿(Viridity)，青色(Cyan)，天蓝(Skyblue)，蓝色(Blue)，蓝紫(Bluish-Violet)，紫色(Violet)，紫红(Magenta)。

每种色相只有5%、10%、20%三种浓度和亮度步长，只要确定一种颜色主题，就可以轻松选择需要的颜色，不像传统的拾色器那样密密麻麻的颜色布局导致选择颜色相对困难。

快捷键：

A(连按3次): 切换快捷键模式

1~7,Q~U: 色相

D/F/G: 步长5/10/20

B/N: S-/B+

C/V: 复制主色/辅色

X: 切换复制格式

H: 显示帮助

M: 最小化窗口(点击右上角同效)

Esc: 退出
'''

HELP = r'''
+-------------------------------------------+
|            RyCy: HSB Color 14             |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi rycy [option]

Options:
    -H, --help   Show help / 显示帮助
    -I, --info   Show info / 显示信息
    -V, --version   Show version / 显示版本
    -m, --module   Show module / 显示子模块
    -r, --run   run window / 启动图形窗口
'''

##############################

import os
import sys
import argparse
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea, QLabel, QVBoxLayout, QDialog, QFileDialog
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont, QColor, QRadialGradient, QLinearGradient, QPixmap, QImage
from PyQt5.QtCore import Qt, QRect, QTimer, QMargins

# 脚本运行模式的路径修复
pjt_root = None
if __name__ == '__main__' and __package__ is None:
    # 将项目根目录（pjt_rypi/）临时加入 sys.path
    pjt_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, pjt_root)
    # 手动设置包名（包目录: pjt_rypi/rypi/）
    __package__ = 'rypi.rycy'

# 导入依赖
try:  # 相对导入
    from . import conf as rycy_conf
    from .. import comm
except ImportError:
    try:  # 包名导入
        from rypi.rycy import conf as rycy_conf
        from rypi import comm
    except ImportError:  # 绝对导入
        import conf as rycy_conf
        import comm

##############################

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("帮助")
        self.setFixedSize(300, 400)
        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_label = QLabel()
        content_label.setTextFormat(Qt.PlainText)
        content_label.setWordWrap(True)
        content_label.setText(
            "锐色RyCy 是一款 HSB 拾色器，只有14种色相(彩度)，分别是：红色(Red)，橙色(Orange)，金色(Gold)，黄色(Yellow)，黄绿(Chartreuse)，春绿(Spring-Greens)，绿色(Green)，青绿(Viridity)，青色(Cyan)，天蓝(Skyblue)，蓝色(Blue)，蓝紫(Bluish-Violet)，紫色(Violet)，紫红(Magenta)。\n\n每种色相只有5%、10%、20%三种浓度和亮度步长，只要确定一种颜色主题，就可以轻松选择需要的颜色，不像传统的拾色器那样密密麻麻的颜色布局导致选择颜色相对困难。\n\n"
            "快捷键：\n"
            "A(连按3次): 切换快捷键模式\n"
            "1~7,Q~U: 色相\n"
            "D/F/G: 步长5/10/20\n"
            "B/N: S-/B+\n"
            "C/V: 复制主色/辅色\n"
            "X: 切换复制格式\n"
            "H: 显示帮助\n"
            "M: 最小化窗口(点击右上角同效)\n"
            "Esc: 退出"
        )
        content_label.setStyleSheet("padding: 10px; font-family: Verdana; font-size: 10pt;")
        scroll_area.setWidget(content_label)
        layout.addWidget(scroll_area)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #ddd;")


class RyCyColorPicker(QWidget):
    def __init__(self):
        super().__init__()
        # 窗口设置
        self.setFixedSize(260, 335)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # 初始状态
        self.hue = 0
        self.sat = 100
        self.bri = 100
        self.step = 10
        self.sl = 2  # 饱和度等级
        self.bl = 1  # 亮度等级
        self.cn = 0  # 复制格式索引
        self.cnl = ['all', 'hex', '#hex', 'rgb', 'rgba', 'hsv', 'hsb', 'cmyk', 'pan']
        self.mns = 0  # 是否显示菜单
        self.cps = 0  # 是否显示复制提示
        self.cpv = ""  # 复制内容
        self.cx = self.cy = 0  # 当前选中色块坐标（绘制游标用）

        # 色相按钮定义
        self.hue_buttons = [
            (0, "0"), (30, "30"), (45, "45"), (60, "60"), (75, "75"), (90, "90"),
            (120, "120"), (150, "150"), (180, "180"), (210, "210"), (240, "240"),
            (270, "270"), (300, "300"), (330, "330")
        ]

        # 主色、辅色
        self.mc = "#FF0000"
        self.ac = "#FF3232"

        # 启动定时器隐藏复制提示
        self.copy_timer = self.new_timer()

        self.help_dialog = HelpDialog(self)

        # 快捷键模式控制
        self.feature_mode = False  # 功能键模式（三连 A 激活）
        self.f_press_count = 0
        self.f_timer = QTimer()
        self.f_timer.setSingleShot(True)
        self.f_timer.timeout.connect(self.reset_f_count)

        # 窗口状态
        self.last_mouse_pos = None

        self.setWindowTitle("锐色RyCy HSB 14")
        self.show()

    def new_timer(self):
        timer = self.startTimer(3000)  # 3秒后触发
        return timer

    def timerEvent(self, event):
        if event.timerId() == self.copy_timer:
            self.killTimer(self.copy_timer)
            self.cps = 0
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.globalPos() - self.pos()

        # 点击右上角 20px 区域最小化
        pos = event.pos()
        if pos.x() >= self.width() - 20 and pos.y() <= 20:
            self.showMinimized()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'last_mouse_pos') and self.last_mouse_pos is not None:
            self.move(event.globalPos() - self.last_mouse_pos)

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'last_mouse_pos'):
            self.last_mouse_pos = None

    def keyPressEvent(self, event):
        # 处理三连 A 激活功能键模式
        if event.key() == Qt.Key_A:
            self.f_press_count += 1
            if self.f_press_count >= 3:
                self.feature_mode = not self.feature_mode
                self.f_press_count = 0
                self.update()
            else:
                self.f_timer.start(300)  # 300ms内再按有效
            return

        # 只有在功能键模式下才执行快捷键操作
        #if event.modifiers() & Qt.AltModifier:
        if self.feature_mode:
            self.handle_key_action(event)
        
    def reset_f_count(self):
        self.f_press_count = 0

    def handle_key_action(self, event):
        key_map = {
            Qt.Key_1: 0, Qt.Key_2: 30, Qt.Key_3: 45, Qt.Key_4: 60,
            Qt.Key_5: 75, Qt.Key_6: 90, Qt.Key_7: 120,
            Qt.Key_Q: 150, Qt.Key_W: 180, Qt.Key_E: 210,
            Qt.Key_R: 240, Qt.Key_T: 270, Qt.Key_Y: 300, Qt.Key_U: 330,
            Qt.Key_D: 5, Qt.Key_F: 10, Qt.Key_G: 20,
            Qt.Key_B: 'sl', Qt.Key_N: 'bl',
            Qt.Key_X: 'cpn', Qt.Key_C: 'mc', Qt.Key_V: 'ac',
            Qt.Key_H: 'help', Qt.Key_M: 'mini', Qt.Key_Escape: 'esc'
        }
        if event.key() in key_map:
            val = key_map[event.key()]
            if isinstance(val, int):
                if event.key() in [Qt.Key_D, Qt.Key_F, Qt.Key_G]:
                    self.step = val
                else:
                    self.hue = val
                self.update_colors()
            elif val == 'sl':
                self.sl = (self.sl + 1) % 6
                self.update_colors()
            elif val == 'bl':
                self.bl = (self.bl + 1) % 6
                self.update_colors()
            elif val == 'cpn':
                self.cn = (self.cn + 1) % len(self.cnl)
                self.update()
            elif val == 'mc':
                self.copy_color('mc')
            elif val == 'ac':
                self.copy_color('ac')
            elif val == 'help':
                self.toggle_help()
            elif val == 'mini':
                self.showMinimized()
            elif val == 'esc':
                self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景
        painter.fillRect(self.rect(), QBrush(QColor("#eee")))

        # 计算主色和辅色
        self.mc = self.hsv_to_rgb(self.hue, self.sat, self.bri)
        if self.sl != 0 or self.bl != 0:
            s = max(0, self.sat - self.step * self.sl)
            b = min(100, self.bri + self.step * self.bl)
            self.ac = self.hsv_to_rgb(self.hue, s, b)
        else:
            self.ac = self.mc

        # 计算文字颜色（根据亮度决定黑白）
        r = int(self.mc[1:3], 16)
        g = int(self.mc[3:5], 16)
        b = int(self.mc[5:7], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        fg_color = QColor("#fff") if brightness < 128 else QColor("#000")

        # 绘制色相按钮 (30x25)
        x, y = 0, 0
        for i, (h, label) in enumerate(self.hue_buttons):
            rect = QRect(x, y, 30, 25)
            color = self.hsv_to_rgb(h, 100, 100)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor("#ccc"), 0.5))
            painter.drawRect(rect)
            if h == self.hue:
                painter.setPen(QPen(QColor("#fff")))
            else:
                painter.setPen(QPen(QColor("#000")))
            painter.setFont(QFont("Verdana", 10))
            painter.drawText(rect, Qt.AlignCenter, label)
            x += 30
            if i == 6:
                x = 0
                y = 25

        # 右上角大方框使用方框径向渐变
        rect = QRect(210, 0, 50, 50)
        center_x = rect.center().x()
        center_y = rect.center().y()
        max_radius = max(rect.width(), rect.height()) * 0.7
        grad = QRadialGradient(center_x, center_y, max_radius, center_x, center_y)
        grad.setColorAt(0, QColor(self.ac))
        grad.setColorAt(1, QColor(self.mc))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#ccc"), 0.5))
        painter.drawRect(rect)

        # 绘制底部按钮
        btn_y = 50
        btn_w, btn_h = 25, 25
        steps = [5, 10, 20]
        for i, s in enumerate(steps):
            rect = QRect(i * btn_w, btn_y, btn_w, btn_h)
            if s == self.step:
                painter.setBrush(QBrush(QColor("#bbf")))
            else:
                painter.setBrush(QBrush(QColor("#ddf")))
            painter.setPen(QPen(QColor("#ccc"), 0.5))
            painter.drawRect(rect)
            painter.setPen(QPen(QColor("#000")))
            font_size = 8
            if self.step == 5:
                font_size = 7
            painter.setFont(QFont("Verdana", font_size))
            painter.drawText(rect, Qt.AlignCenter, str(s))

        # S-
        rect = QRect(75, btn_y, btn_w, btn_h)
        painter.setBrush(QBrush(QColor("#ddf")))
        painter.setPen(QPen(QColor("#ccc"), 0.5))
        painter.drawRect(rect)
        painter.setPen(QPen(QColor("#000")))
        painter.setFont(QFont("Verdana", font_size))
        painter.drawText(rect, Qt.AlignCenter, f"S-{self.sl}")

        # B+
        rect = QRect(100, btn_y, btn_w, btn_h)
        painter.setBrush(QBrush(QColor("#ddf")))
        painter.setPen(QPen(QColor("#ccc"), 0.5))
        painter.drawRect(rect)
        painter.setPen(QPen(QColor("#000")))
        painter.setFont(QFont("Verdana", font_size))
        painter.drawText(rect, Qt.AlignCenter, f"B+{self.bl}")

        # CP
        rect = QRect(125, btn_y, btn_w, btn_h)
        painter.setBrush(QBrush(QColor("#ddf")))
        painter.setPen(QPen(QColor("#ccc"), 0.5))
        painter.drawRect(rect)
        painter.setPen(QPen(QColor("#000")))
        painter.setFont(QFont("Verdana", font_size))
        painter.drawText(rect, Qt.AlignCenter, self.cnl[self.cn])

        # MC
        rect = QRect(150, btn_y, btn_w, btn_h)
        painter.setBrush(QBrush(QColor(self.mc)))
        painter.setPen(QPen(QColor("#ccc"), 0.5))
        painter.drawRect(rect)
        painter.setPen(fg_color)
        painter.setFont(QFont("Verdana", font_size))
        painter.drawText(rect, Qt.AlignCenter, "MC")

        # AC
        rect = QRect(175, btn_y, btn_w, btn_h)
        painter.setBrush(QBrush(QColor(self.ac)))
        painter.setPen(QPen(QColor("#ccc"), 0.5))
        painter.drawRect(rect)
        painter.setPen(fg_color)
        painter.setFont(QFont("Verdana", font_size))
        painter.drawText(rect, Qt.AlignCenter, "AC")

        # Help 按钮使用从左到右的线性渐变
        help_rect = QRect(200, btn_y, 60, btn_h)
        if self.mc != self.ac:
            grad = QLinearGradient(help_rect.left(), help_rect.center().y(),
                                   help_rect.right(), help_rect.center().y())
            grad.setColorAt(0, QColor(self.mc))
            grad.setColorAt(1, QColor(self.ac))
            painter.setBrush(QBrush(grad))
        else:
            painter.setBrush(QBrush(QColor(self.mc)))
        painter.setPen(QPen(QColor("#ccc"), 0.5))
        painter.drawRect(help_rect)
        painter.setPen(fg_color)
        painter.setFont(QFont("Verdana", font_size))
        painter.drawText(help_rect, Qt.AlignCenter, "Help")

        # 绘制色板
        start_x, start_y = 10, 85
        block_w = block_h = self.step * 4
        if self.step == 5:
            block_w = block_h = 10
            start_x, start_y = 30, 105
        elif self.step == 10:
            block_w = block_h = 20
            start_x, start_y = 30, 105
        else:
            block_w = block_h = 40
            start_x, start_y = 10, 85

        for i, v in enumerate(range(100, -1, -self.step)):
            for j, s in enumerate(range(0, 101, self.step)):
                x = start_x + j * block_w
                y = start_y + i * block_h
                color = self.hsv_to_rgb(self.hue, s, v)
                painter.setBrush(QBrush(QColor(color)))
                painter.setPen(QPen(QColor("#ccc"), 0.5))
                painter.drawRect(x, y, block_w, block_h)
                if s == self.sat and v == self.bri:
                    self.cx, self.cy = x, y

        # S/B 数值显示与色块大小一致，字体随步长调整
        if self.step <= 10:
            border_pen = QPen(QColor("#ccc"), 0.5)
            font_size_label = 7 if self.step == 5 else 8
            painter.setFont(QFont("Arial", font_size_label))

            # S/B 标识框
            label_rect = QRect(start_x - 20, start_y - 20, 20, 20)
            painter.setPen(border_pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(label_rect)
            painter.setPen(QPen(QColor("#000")))
            painter.drawText(label_rect, Qt.AlignCenter, "S/B")

            # 左侧 B 值（100 → 0）
            for i, v in enumerate(range(100, -1, -self.step)):
                y = start_y + i * block_h
                text_rect = QRect(start_x - 20, y, 20, block_h)
                painter.setPen(border_pen)
                painter.setBrush(QBrush(Qt.NoBrush))
                painter.drawRect(text_rect)
                painter.setPen(QPen(QColor("#000")))
                painter.drawText(text_rect, Qt.AlignCenter, str(v))

            # 顶部 S 值（0 → 100）
            for j, s in enumerate(range(0, 101, self.step)):
                x = start_x + j * block_w
                text_rect = QRect(x, start_y - 20, block_w, 20)
                painter.setPen(border_pen)
                painter.setBrush(QBrush(Qt.NoBrush))
                painter.drawRect(text_rect)
                painter.setPen(QPen(QColor("#000")))
                painter.drawText(text_rect, Qt.AlignCenter, str(s))

        # 画十字游标
        if self.cx and self.cy:
            painter.setPen(QPen(fg_color, 1))
            cx_center = self.cx + block_w // 2
            cy_center = self.cy + block_h // 2
            painter.drawLine(cx_center, self.cy, cx_center, self.cy + block_h)
            painter.drawLine(self.cx, cy_center, self.cx + block_w, cy_center)

        # 复制提示
        if self.cps:
            total_width = (100 // self.step) * block_w
            total_height = (100 // self.step + 1) * block_h
            text_rect = QRect(start_x, start_y, total_width, total_height)
            painter.setPen(QPen(QColor("#fff")))
            painter.setFont(QFont("Verdana", 10, QFont.Bold))
            painter.drawText(text_rect, Qt.AlignCenter, self.cpv)

        # 右下角绿色小方块（功能键模式指示）
        if self.feature_mode:
            painter.setBrush(QBrush(QColor("#080")))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.width() - 10, self.height() - 10, 10, 10)

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        x, y = pos.x(), pos.y()

        # 检查色相按钮
        for i, (h, label) in enumerate(self.hue_buttons):
            row = i // 7
            col = i % 7
            bx = col * 30
            by = row * 25
            if bx <= x < bx + 30 and by <= y < by + 25:
                self.hue = h
                self.update_colors()
                return

        # 检查底部按钮
        if 50 <= y < 75:
            if x < 75:
                step_idx = x // 25
                if step_idx < 3:
                    self.step = [5, 10, 20][step_idx]
                    self.update_colors()
            elif 75 <= x < 100:
                self.sl = (self.sl + 1) % 6
                self.update_colors()
            elif 100 <= x < 125:
                self.bl = (self.bl + 1) % 6
                self.update_colors()
            elif 125 <= x < 150:
                self.cn = (self.cn + 1) % len(self.cnl)
                self.update()
            elif 150 <= x < 175:
                self.copy_color('mc')
            elif 175 <= x < 200:
                self.copy_color('ac')
            elif 200 <= x < 260:
                self.toggle_help()

        # 检查色板区域
        start_x, start_y = 10, 85
        block_w = block_h = self.step * 4
        if self.step == 5:
            block_w = block_h = 10
            start_x, start_y = 30, 105
        elif self.step == 10:
            block_w = block_h = 20
            start_x, start_y = 30, 105
        else:
            block_w = block_h = 40
            start_x, start_y = 10, 85

        if x >= start_x and y >= start_y:
            j = (x - start_x) // block_w
            i = (y - start_y) // block_h
            s = j * self.step
            v = 100 - i * self.step
            if 0 <= s <= 100 and 0 <= v <= 100:
                self.sat = s
                self.bri = v
                self.update_colors()

    def update_colors(self):
        self.update()

    def hsv_to_rgb(self, h, s, v):
        h = h % 360
        s /= 100
        v /= 100
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        r, g, b = (r + m), (g + m), (b + m)
        return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        else:
            h = (60 * ((r - g) / df) + 240) % 360
        s = 0 if mx == 0 else (df / mx)
        v = mx
        return {'h': round(h), 's': round(s * 100), 'v': round(v * 100)}

    def copy_color(self, mode):
        clipboard = QApplication.clipboard()
        if mode == 'mc':
            color = self.mc
        else:
            color = self.ac

        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        hsv = self.rgb_to_hsv(r, g, b)
        h, s, v = hsv['h'], hsv['s'], hsv['v']

        c = 1 - r / 255
        m = 1 - g / 255
        y = 1 - b / 255
        k = min(c, m, y)
        if k == 1:
            c = m = y = 0
        else:
            c = (c - k) / (1 - k)
            m = (m - k) / (1 - k)
            y = (y - k) / (1 - k)
        cmyk = f"CMYK: {int(c*100)} {int(m*100)} {int(y*100)} {int(k*100)}"

        hex_val = color[1:].upper()
        hash_hex = color.upper()

        formats = [
            f"{hash_hex}\nrgb({r}, {g}, {b})\nrgba({r}, {g}, {b}, 1)\nhsv({h}, {s}, {v})\n{cmyk}\nPANTONE 185 C",
            hex_val,
            hash_hex,
            f"rgb({r}, {g}, {b})",
            f"rgba({r}, {g}, {b}, 1)",
            f"hsv({h}, {s}, {v})",
            f"HSB: {h} {s} {v}",
            cmyk,
            "PANTONE 185 C"
        ]

        text = formats[self.cn]
        clipboard.setText(text)
        self.cpv = text
        self.cps = 1
        if hasattr(self, 'copy_timer'):
            self.killTimer(self.copy_timer)
        self.copy_timer = self.new_timer()
        self.update()

    def toggle_help(self):
        if self.help_dialog.isVisible():
            self.help_dialog.hide()
        else:
            self.help_dialog.show()


def run_win(run):
    '''
    启动图形窗口。
    '''
    if run:
        app = QApplication(sys.argv)
        picker = RyCyColorPicker()
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

    # 全局选项
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-H', '--help', action='store_true')
    parser.add_argument('-I', '--info', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument('-m', '--module', action='store_true')
    parser.add_argument('-r', '--run', action='store_true')
    parser.add_argument('--win', action='store_true')

    # 获取当前目录的所有子模块
    smod = comm.get_modules(__package__)

    # 创建子模块解析器
    subp = parser.add_subparsers(dest='smod', required=False)

    # 定义子模块
    for name, _, _ in smod:
        subp.add_parser(name, add_help=False)

    # 只解析到子模块名称，剩下的参数作为未知参数留给子模块处理
    args, args2 = parser.parse_known_args(args)
    #print(f'args: {args}, args2: {args2}')

    if args.version:
        print(VER)
    elif args.info:
        print(INFO)
    elif args.help:
        print(HELP)
    elif args.run:
        run_win(args.win)

    # 显示子模块
    elif args.module:
        print(f'\n可以在模块名称后加参数(-H)查看该模块的帮助信息。')
        print(f'\n名称前面带横线(-)的是命令模块（目录），否则是辅助模块（脚本 .py 文件）。')
        print(f'\nmodule list:')
        for name, desc, ispkg in smod:
            sub = '-' if ispkg else ' '
            print(f'\n  {sub} {name}: {desc}')

    # 调用子模块
    elif args.smod:
        for name, desc, ispkg in smod:
            if name == args.smod:
                #print(f'name: {name}, args: {args2}')
                comm.run_mod(__package__, name, ispkg, args2)

    # 显示帮助
    else:
        print(HELP)

if __name__ == '__main__':
    main()