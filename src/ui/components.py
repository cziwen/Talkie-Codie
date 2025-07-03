from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QFrame, QStackedLayout, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
import sounddevice as sd
import numpy as np
import threading
import tempfile
import scipy.io.wavfile as wavfile
from src.audio.whisper_transcriber import transcribe_audio
from src.llm.manager import LLMManager
from src.ui.settings_dialog import SettingsDialog
import json
import re
import datetime
import os

RECORD_DURATION_MS = 60000  # 60秒
SAMPLE_RATE = 44100  # 提高采样率到44.1kHz
CHANNELS = 1
DTYPE = 'float32'  # 使用float32提高精度

def get_selected_device():
    try:
        with open('config/whisper_config.json', 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        device_str = cfg.get('input_device', None)
        if device_str:
            m = re.search(r'\(id=(\d+)\)', device_str)
            if m:
                return int(m.group(1))
        return None
    except Exception:
        return None

def clean_rephrase_tags(text):
    """清理REPHRASE标签，提取标签内的内容，忽略标签外的说明文字"""
    import re
    
    # 首先尝试提取<REPHRASE>和</REPHRASE>之间的内容
    rephrase_pattern = r'<REPHRASE[^>]*>(.*?)</REPHRASE>'
    match = re.search(rephrase_pattern, text, flags=re.IGNORECASE | re.DOTALL)
    
    if match:
        # 找到完整的REPHRASE标签，提取其中的内容
        content = match.group(1).strip()
        return content
    
    # 如果没有找到完整的标签，尝试提取不完整的标签内容
    # 移除所有REPHRASE相关标签
    text = re.sub(r'</?REPHRASE>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?REP[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?REPHRASE?[^>]*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^</?REPHRASE?[^>]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?REP[^>]*', '', text, flags=re.IGNORECASE)
    
    # 移除行首行尾的空白字符
    text = text.strip()
    
    # 如果文本为空或只包含空白字符，返回空字符串
    if not text or text.isspace():
        return ""
    
    return text

class VolumeWaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setFixedHeight(36)
        self.setMinimumWidth(120)
        self.amplitude = 0.0
        self._display_amplitude = 0.0
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._on_timer)
        self.setVisible(False)
        self._color = QColor(76, 175, 80)  # 初始绿色
        self._display_color = QColor(76, 175, 80)

    def start(self):
        self.setVisible(True)
        self.timer.start()

    def stop(self):
        self.setVisible(False)
        self.timer.stop()

    def set_amplitude(self, amp):
        self.amplitude = max(0.01, min(amp, 1.0))

    def _on_timer(self):
        # 平滑过渡振幅
        alpha = 0.18  # 越小越平滑
        self._display_amplitude += (self.amplitude - self._display_amplitude) * alpha
        # 平滑过渡颜色
        r = int(76 + (244 - 76) * self._display_amplitude)
        g = int(175 + (67 - 175) * self._display_amplitude)
        b = int(80 + (54 - 80) * self._display_amplitude)
        self._display_color = QColor(r, g, b)
        self.phase += 0.18
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        mid = h // 2
        pen = QPen(self._display_color, 2)
        painter.setPen(pen)
        # 绘制一条跳舞的正弦波
        points = []
        for x in range(w):
            y = mid + int(self._display_amplitude * (h/2-4) * \
                np.sin(2 * np.pi * (x / w) * 2 + self.phase))
            points.append((x, y))
        for i in range(1, len(points)):
            painter.drawLine(points[i-1][0], points[i-1][1], points[i][0], points[i][1])

class PromptTextEdit(QTextEdit):
    waveform: 'VolumeWaveformWidget|None' = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.waveform = None
    def resizeEvent(self, event):
        if self.waveform:
            margin = getattr(self.parent(), 'waveform_margin', 2) if self.parent() else 2
            height = getattr(self.parent(), 'waveform_height', 48) if self.parent() else 48
            self.waveform.move(margin, self.height() - height - 6)
            self.waveform.resize(self.width() - 2 * margin, height)
        super().resizeEvent(event)

class MainWidget(QWidget):
    prompt_ready = pyqtSignal(str)  # 新增信号

    def __init__(self):
        super().__init__()
        self.init_ui()
        # 录音相关
        self.is_recording = False
        self.stream = None
        self.volume_level = 0
        self.timer = QTimer()
        self.timer.setInterval(50)  # 20fps 刷新音量
        self.timer.timeout.connect(self.update_volume_bar)
        self.record_btn.clicked.connect(self.start_recording)
        # 新增：高质量录音相关
        self.rec_thread = None
        self.rec_stop_flag = threading.Event()
        self.high_quality_audio = None
        self.silence_duration_ms = 0
        self.silence_threshold = 0.01  # 音量阈值
        self.silence_max_ms = self._load_silence_max_ms()  # 静音超过N毫秒自动停止
        self.last_callback_time = None
        # LLM 管理器
        self.llm_manager = LLMManager()
        # 信号连接
        self.prompt_ready.connect(self.prompt_box.setPlainText)
        self.settings_btn.clicked.connect(self.open_settings)
        self._auto_stop_timer = None  # 记录自动停止的 QTimer

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)


        # ---- 新增：包裹 prompt_box 和复制按钮 ----
        prompt_frame = QFrame()
        prompt_frame.setStyleSheet('border: none; background: transparent;')
        prompt_layout = QVBoxLayout()
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        prompt_layout.setSpacing(0)
        prompt_frame.setLayout(prompt_layout)

        # 只读文本框
        self.prompt_box = PromptTextEdit()
        self.prompt_box.setReadOnly(True)
        self.prompt_box.setPlaceholderText('"Write a Python function for bubble sort"')
        self.prompt_box.setStyleSheet('''
            font-size: 15px;
            color: #222;
            background: #f5f7fa;
            border: 1.5px solid #b0b8c1;
            border-radius: 12px;
            padding: 18px 16px 36px 16px; /* 底部留空间给波形 */
            font-family: "Menlo", "Consolas", "monospace", "PingFang SC", "Microsoft YaHei";
            line-height: 1.7;
            letter-spacing: 0.5px;
        ''')
        self.prompt_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 波形控件
        self.waveform = VolumeWaveformWidget(self.prompt_box)
        self.prompt_box.waveform = self.waveform
        self.waveform_height = 48
        self.waveform_margin = 1
        self.waveform.move(self.waveform_margin, self.prompt_box.height() - self.waveform_height - 6)
        self.waveform.resize(self.prompt_box.width() - 2 * self.waveform_margin, self.waveform_height)
        self.waveform.raise_()

        # 复制按钮
        self.copy_btn = QPushButton('Copy')
        self.copy_btn.setToolTip('复制到剪贴板')
        self.copy_btn.setMinimumWidth(40)
        self.copy_btn.setMinimumHeight(22)
        self.copy_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setStyleSheet('''
            QPushButton {
                background: transparent;
                border: none;
                font-size: 13px;
                color: #666;
                padding: 0 4px;
            }
            QPushButton:hover {
                color: #1976d2;
            }
        ''')
        self.copy_btn.clicked.connect(self.copy_prompt_text)
        self._copy_reset_timer = QTimer(self)
        self._copy_reset_timer.setSingleShot(True)
        self._copy_reset_timer.timeout.connect(self._reset_copy_btn)

        # 右上角布局
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 8, 0)  # 右上角留点空隙
        btn_row.addStretch(1)
        btn_row.addWidget(self.copy_btn, alignment=Qt.AlignmentFlag.AlignRight)
        # 用一个小竖直布局包裹按钮和文本框
        prompt_layout.addLayout(btn_row)
        prompt_layout.addWidget(self.prompt_box)
        # ---- end ----

        # 下方按钮区
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setContentsMargins(0, 10, 0, 0)

        # 左侧：开始说话按钮
        self.record_btn = QPushButton('🎤 Start Recording')
        self.record_btn.setFixedHeight(40)
        self.record_btn.setStyleSheet('font-size: 16px;')
        btn_layout.addWidget(self.record_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        btn_layout.addStretch(1)

        # 右侧：设置按钮
        self.settings_btn = QPushButton('⚙ Settings')
        self.settings_btn.setFixedHeight(40)
        self.settings_btn.setStyleSheet('font-size: 16px;')
        btn_layout.addWidget(self.settings_btn, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addWidget(prompt_frame)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def start_recording(self):
        if self.is_recording:
            return
        self.is_recording = True
        self.record_btn.setText('■ Stop Recording')
        self.record_btn.setEnabled(True)
        self.record_btn.clicked.disconnect()
        self.record_btn.clicked.connect(self.stop_recording)
        self.volume_level = 0
        self.timer.start()
        self.waveform.start()  # 显示波形
        self.silence_duration_ms = 0
        self.last_callback_time = None
        self.rec_stop_flag.clear()
        self.high_quality_audio = None
        self.recording_start_time = datetime.datetime.now()  # 记录录音开始时间
        self.recording_stop_time = None  # 录音终止时间
        # 启动 InputStream 线程（只做音量/静音检测）
        threading.Thread(target=self._monitor_stream, daemon=True).start()
        # 启动高质量录音线程
        self.rec_thread = threading.Thread(target=self._record_high_quality, daemon=True)
        self.rec_thread.start()
        # 60秒后自动停止
        self._auto_stop_timer = QTimer(self)
        self._auto_stop_timer.setSingleShot(True)
        self._auto_stop_timer.timeout.connect(self.stop_recording)
        self._auto_stop_timer.start(RECORD_DURATION_MS)

    def _monitor_stream(self):
        device_id = get_selected_device()
        def callback(indata, frames, time, status):
            # 只做音量和静音检测
            vol = float(np.sqrt(np.mean(indata**2)))
            self.volume_level = vol
            now = datetime.datetime.now()
            if self.last_callback_time is None:
                self.last_callback_time = now
            # 静音检测
            if vol < self.silence_threshold:
                delta = (now - self.last_callback_time).total_seconds() * 1000
                self.silence_duration_ms += delta
            else:
                self.silence_duration_ms = 0
            self.last_callback_time = now
            # 静音超时自动停止
            if self.silence_max_ms <= 0:
                # 不要grace period，首次静音立即停止
                if vol < self.silence_threshold:
                    QTimer.singleShot(0, self.stop_recording)
            else:
                if self.silence_duration_ms >= self.silence_max_ms:
                    QTimer.singleShot(0, self.stop_recording)
        self.stream = sd.InputStream(
            channels=CHANNELS, samplerate=SAMPLE_RATE, dtype=DTYPE, callback=callback,
            device=device_id
        )
        with self.stream:
            while self.is_recording and not self.rec_stop_flag.is_set():
                sd.sleep(50)  # 50ms 检查一次

    def _record_high_quality(self):
        device_id = get_selected_device()
        duration_sec = RECORD_DURATION_MS / 1000
        self.high_quality_audio = sd.rec(int(duration_sec * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, device=device_id)
        # 等待录音结束或被 stop_recording 提前终止
        elapsed = 0
        interval = 0.05
        while self.is_recording and not self.rec_stop_flag.is_set() and elapsed < duration_sec:
            sd.sleep(int(interval * 1000))
            elapsed += interval
        sd.stop()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.rec_stop_flag.set()
        self.recording_stop_time = datetime.datetime.now()  # 记录录音终止时间
        if self._auto_stop_timer:
            self._auto_stop_timer.stop()
            self._auto_stop_timer = None
        self.record_btn.setText('🎤 Start Recording')
        self.record_btn.setEnabled(True)
        self.record_btn.clicked.disconnect()
        self.record_btn.clicked.connect(self.start_recording)
        self.timer.stop()
        self.volume_level = 0
        self.waveform.stop()  # 隐藏波形
        self.update_volume_bar()
        # 等待高质量录音线程结束
        if self.rec_thread is not None:
            self.rec_thread.join(timeout=1)
        threading.Thread(target=self.process_audio_to_prompt, daemon=True).start()

    def process_audio_to_prompt(self):
        # 用高质量录音数据
        if self.high_quality_audio is None:
            self.update_prompt_box('No audio data detected.')
            return
        audio = self.high_quality_audio
        # 裁剪音频到实际录音时长
        if self.recording_start_time and self.recording_stop_time:
            duration_sec = (self.recording_stop_time - self.recording_start_time).total_seconds()
            max_samples = int(duration_sec * SAMPLE_RATE)
            if max_samples < len(audio):
                audio = audio[:max_samples]
        # 音频质量检查
        if len(audio) == 0:
            self.update_prompt_box('No audio data detected.')
            return
        # 检查音频是否全为静音
        audio_rms = np.sqrt(np.mean(audio**2))
        if audio_rms < 0.001:  # 阈值可调整
            self.update_prompt_box('Audio too quiet, please speak louder.')
            return
        # 生成时间戳
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        audio_dir = os.path.join('cache', 'audio')
        transcript_dir = os.path.join('cache', 'transcript')
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(transcript_dir, exist_ok=True)
        audio_path = os.path.join(audio_dir, f'audio_{ts}.wav')
        # 转换为int16格式保存（Whisper兼容）
        audio_int16 = (audio * 32767).astype(np.int16)
        wavfile.write(audio_path, SAMPLE_RATE, audio_int16)
        # Whisper 语音转文本
        try:
            self.update_prompt_box('Transcribing audio...')
            transcript, detected_language = transcribe_audio(audio_path)
            # 保存转录文本
            transcript_path = os.path.join(transcript_dir, f'transcript_{ts}.txt')
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
        except Exception as e:
            self.update_prompt_box(f'Transcription failed: {e}')
            return
        
        # LLM 改写 prompt
        try:
            self.update_prompt_box('Rephrasing prompt...')
            result = self.llm_manager.optimize_prompt(transcript, language=detected_language)
            if isinstance(result, tuple):
                prompt = result[0]
            else:
                prompt = result
            self.update_prompt_box(prompt)
        except Exception as e:
            self.update_prompt_box(f'AI rephrase failed: {e}')

    def update_prompt_box(self, text):
        text = clean_rephrase_tags(text)
        self._reset_copy_btn()  # 新文本时重置按钮
        self.prompt_ready.emit(text)

    def _reset_copy_btn(self):
        self.copy_btn.setText('Copy')
        self.copy_btn.setEnabled(True)
        self.copy_btn.setStyleSheet('''
            QPushButton {
                background: transparent;
                border: none;
                font-size: 13px;
                color: #666;
                padding: 0 4px;
            }
            QPushButton:hover {
                color: #1976d2;
            }
        ''')

    def update_volume_bar(self):
        # 控制波形显示/隐藏和动画
        if self.is_recording:
            self.waveform.set_amplitude(min(self.volume_level * 8, 1.0))
            if not self.waveform.isVisible():
                self.waveform.start()
        else:
            self.waveform.stop()
        # 保留原有音量条逻辑（可移除）

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            # 设置保存后，重新初始化LLM管理器
            self.reload_configurations()
    
    def reload_configurations(self):
        """重新加载所有配置"""
        # 重新加载LLM管理器配置
        self.llm_manager.reload_config()
        print("所有配置已重新加载")

    def copy_prompt_text(self):
        from PyQt6.QtWidgets import QApplication
        text = self.prompt_box.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(text)
            self.copy_btn.setText('Copied!')
            self.copy_btn.setEnabled(False)
            self.copy_btn.setStyleSheet('''
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 13px;
                    color: #43a047;
                    padding: 0 4px;
                }
            ''')
            self._copy_reset_timer.start(1500) 

    def _load_silence_max_ms(self):
        try:
            with open('config/whisper_config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            vad_params = cfg.get('vad_parameters', {})
            return int(vad_params.get('min_silence_duration_ms', 2000))
        except Exception:
            return 2000 