import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QComboBox,
    QLineEdit, QCheckBox, QTextEdit, QProgressBar,
    QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont


class PackWorker(QObject):
    """打包线程类（独立于GUI线程，避免界面卡死）"""
    finished = pyqtSignal(bool)  # 打包完成信号（True=成功，False=失败）
    log_signal = pyqtSignal(str)  # 日志输出信号（实时传递打包日志）
    progress_signal = pyqtSignal(int)  # 进度更新信号

    def __init__(self, pack_params):
        super().__init__()
        self.pack_params = pack_params  # 打包参数
        self.is_canceled = False  # 取消标记

    def run(self):
        """执行打包逻辑（线程核心方法）"""
        # 解析打包参数
        tool = self.pack_params["tool"]
        script_path = self.pack_params["script_path"]
        output_dir = self.pack_params["output_dir"]
        exe_name = self.pack_params["exe_name"]
        icon_path = self.pack_params["icon_path"]
        single_file = self.pack_params["single_file"]
        no_console = self.pack_params["no_console"]

        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            self.log_signal.emit(f"✅ 输出目录已准备：{output_dir}")
            self.progress_signal.emit(10)

            # 构建打包命令（根据工具选择）
            if tool == "PyInstaller":
                cmd = [
                    sys.executable, "-m", "pyinstaller",
                    script_path,
                    "-n", exe_name,
                    "--distpath", os.path.join(output_dir, "dist"),
                    "--workpath", os.path.join(output_dir, "build"),
                    "--specpath", output_dir
                ]
                if icon_path and os.path.exists(icon_path):
                    cmd.extend(["-i", icon_path])
                if single_file:
                    cmd.append("-F")
                if no_console:
                    cmd.append("-w")

            elif tool == "Nuitka":
                cmd = [
                    sys.executable, "-m", "nuitka",
                    script_path,
                    "--output-dir", output_dir,
                    "--exe",
                    "--output-filename", exe_name
                ]
                if icon_path and os.path.exists(icon_path):
                    cmd.append(f"--windows-icon-from-ico={icon_path}")
                if no_console:
                    cmd.append("--windows-disable-console")
                if single_file:
                    cmd.append("--standalone")

            # 过滤空参数
            cmd = [arg for arg in cmd if arg]
            self.log_signal.emit(f"📦 打包命令：{' '.join(cmd)}")
            self.progress_signal.emit(20)

            # 执行打包命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                shell=False
            )

            # 实时输出日志
            while not self.is_canceled and process.poll() is None:
                output = process.stdout.readline()
                if output:
                    self.log_signal.emit(output.strip())
                
            if self.is_canceled:
                process.terminate()
                self.log_signal.emit("❌ 打包已取消")
                self.finished.emit(False)
                return

            # 检查执行结果
            if process.returncode == 0:
                self.log_signal.emit("✅ 打包成功！")
                self.progress_signal.emit(100)
                self.finished.emit(True)
            else:
                self.log_signal.emit(f"❌ 打包失败，返回码：{process.returncode}")
                self.finished.emit(False)

        except Exception as e:
            self.log_signal.emit(f"❌ 打包出错：{str(e)}")
            self.finished.emit(False)

    def cancel(self):
        """取消打包"""
        self.is_canceled = True


class PackPyGUI(QMainWindow):
    """主GUI窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python打包工具 - PackPy")
        self.setGeometry(100, 100, 850, 650)
        self.init_ui()
        self.pack_thread = None  # 打包线程
        self.pack_worker = None  # 打包工作对象

    def init_ui(self):
        """初始化UI界面"""
        # 中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 标题区域
        title_label = QLabel("Python 一键打包工具")
        title_label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 配置区域
        config_layout = QVBoxLayout()
        config_layout.setSpacing(12)

        # 1. 选择Python脚本
        script_layout = QHBoxLayout()
        script_label = QLabel("Python脚本：")
        script_label.setFixedWidth(100)
        self.script_edit = QLineEdit()
        self.script_edit.setPlaceholderText("请选择要打包的.py文件")
        script_btn = QPushButton("浏览...")
        script_btn.clicked.connect(self.select_script)
        script_layout.addWidget(script_label)
        script_layout.addWidget(self.script_edit)
        script_layout.addWidget(script_btn)
        config_layout.addLayout(script_layout)

        # 2. 输出目录
        output_layout = QHBoxLayout()
        output_label = QLabel("输出目录：")
        output_label.setFixedWidth(100)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("请选择输出目录")
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        config_layout.addLayout(output_layout)

        # 3. 可执行文件名
        name_layout = QHBoxLayout()
        name_label = QLabel("exe名称：")
        name_label.setFixedWidth(100)
        self.name_edit = QLineEdit("my_app")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        config_layout.addLayout(name_layout)

        # 4. 图标文件
        icon_layout = QHBoxLayout()
        icon_label = QLabel("图标文件：")
        icon_label.setFixedWidth(100)
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("(可选) 请选择.ico图标文件")
        icon_btn = QPushButton("浏览...")
        icon_btn.clicked.connect(self.select_icon)
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(icon_btn)
        config_layout.addLayout(icon_layout)

        # 5. 打包工具选择
        tool_layout = QHBoxLayout()
        tool_label = QLabel("打包工具：")
        tool_label.setFixedWidth(100)
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["PyInstaller", "Nuitka"])
        self.tool_combo.setCurrentIndex(0)
        tool_layout.addWidget(tool_label)
        tool_layout.addWidget(self.tool_combo)
        config_layout.addLayout(tool_layout)

        # 6. 打包选项
        option_layout = QHBoxLayout()
        self.single_file_box = QCheckBox("单文件模式")
        self.single_file_box.setChecked(True)
        self.no_console_box = QCheckBox("无控制台（GUI程序）")
        self.no_console_box.setChecked(True)
        option_layout.addWidget(self.single_file_box)
        option_layout.addWidget(self.no_console_box)
        config_layout.addLayout(option_layout)

        main_layout.addLayout(config_layout)

        # 分割线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        # 日志区域
        log_label = QLabel("打包日志：")
        main_layout.addWidget(log_label)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setStyleSheet("background-color: #f5f5f5; font-family: Consolas, monospace;")
        main_layout.addWidget(self.log_edit)

        # 进度条和按钮区域
        bottom_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(30)
        self.progress_bar.setVisible(False)

        self.start_btn = QPushButton("开始打包")
        self.start_btn.setFixedSize(120, 30)
        self.start_btn.setFont(QFont("微软雅黑", 9))
        self.start_btn.clicked.connect(self.start_pack)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedSize(120, 30)
        self.cancel_btn.setFont(QFont("微软雅黑", 9))
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_pack)

        bottom_layout.addWidget(self.progress_bar)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.start_btn)
        bottom_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(bottom_layout)

    def select_script(self):
        """选择Python脚本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Python脚本", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.script_edit.setText(file_path)
            # 自动填充输出目录（脚本所在目录）
            if not self.output_edit.text():
                self.output_edit.setText(os.path.dirname(file_path))
            # 自动填充exe名称（脚本文件名）
            if self.name_edit.text() == "my_app":
                self.name_edit.setText(os.path.splitext(os.path.basename(file_path))[0])

    def select_output_dir(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_edit.setText(dir_path)

    def select_icon(self):
        """选择图标文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图标文件", "", "ICO Files (*.ico);;All Files (*)"
        )
        if file_path:
            self.icon_edit.setText(file_path)

    def start_pack(self):
        """开始打包"""
        # 验证输入
        script_path = self.script_edit.text().strip()
        output_dir = self.output_edit.text().strip()
        exe_name = self.name_edit.text().strip()

        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(self, "输入错误", "请选择有效的Python脚本文件！")
            return

        if not output_dir:
            QMessageBox.warning(self, "输入错误", "请选择输出目录！")
            return

        if not exe_name:
            QMessageBox.warning(self, "输入错误", "请输入可执行文件名称！")
            return

        # 准备打包参数
        pack_params = {
            "tool": self.tool_combo.currentText(),
            "script_path": script_path,
            "output_dir": output_dir,
            "exe_name": exe_name,
            "icon_path": self.icon_edit.text().strip() if os.path.exists(self.icon_edit.text().strip()) else "",
            "single_file": self.single_file_box.isChecked(),
            "no_console": self.no_console_box.isChecked()
        }

        # 初始化线程和工作对象
        self.pack_thread = QThread()
        self.pack_worker = PackWorker(pack_params)
        self.pack_worker.moveToThread(self.pack_thread)

        # 连接信号槽
        self.pack_thread.started.connect(self.pack_worker.run)
        self.pack_worker.finished.connect(self.on_pack_finished)
        self.pack_worker.log_signal.connect(self.append_log)
        self.pack_worker.progress_signal.connect(self.update_progress)
        self.pack_worker.finished.connect(self.pack_thread.quit)
        self.pack_worker.finished.connect(self.pack_worker.deleteLater)
        self.pack_thread.finished.connect(self.pack_thread.deleteLater)

        # 更新UI状态
        self.start_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_edit.clear()
        self.append_log("🚀 准备开始打包...")

        # 启动线程
        self.pack_thread.start()

    def cancel_pack(self):
        """取消打包"""
        if self.pack_worker:
            self.pack_worker.cancel()
            self.append_log("⏳ 正在取消打包...")

    def on_pack_finished(self, success):
        """打包完成处理"""
        self.progress_bar.setValue(100 if success else 0)
        self.start_btn.setVisible(True)
        self.cancel_btn.setVisible(False)

        if success:
            QMessageBox.information(
                self, "成功", 
                f"打包成功！\n文件已保存到：\n{os.path.join(self.output_edit.text(), 'dist' if self.tool_combo.currentText() == 'PyInstaller' else '')}"
            )
            # 打开输出目录
            try:
                output_dir = os.path.join(self.output_edit.text(), 'dist') if self.tool_combo.currentText() == 'PyInstaller' else self.output_edit.text()
                os.startfile(output_dir)
            except:
                pass

    def append_log(self, text):
        """追加日志到界面"""
        self.log_edit.append(text)
        # 自动滚动到底部
        self.log_edit.moveCursor(self.log_edit.textCursor().End)

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self.pack_thread and self.pack_thread.isRunning():
            reply = QMessageBox.question(
                self, "确认关闭", 
                "正在打包中，确定要关闭吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.pack_worker:
                    self.pack_worker.cancel()
                self.pack_thread.wait(1000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
