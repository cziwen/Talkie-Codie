from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QMessageBox, QProgressDialog)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtCore import Qt
import json
import os
import sounddevice as sd
from src.llm.manager import LLMManager

class APITestThread(QThread):
    """API连接测试线程"""
    test_completed = pyqtSignal(bool, str)  # 成功状态, 错误信息
    
    def __init__(self, provider_type, api_key):
        super().__init__()
        self.provider_type = provider_type
        self.api_key = api_key
    
    def run(self):
        try:
            # 创建临时配置进行测试
            temp_config = {
                "default_provider": self.provider_type,
                "providers": {
                    self.provider_type: {
                        "api_key": self.api_key
                    }
                }
            }
            
            # 创建临时LLM管理器进行测试
            llm_manager = LLMManager()
            llm_manager.config = temp_config
            llm_manager._initialize_provider()
            
            # 测试连接
            if llm_manager.test_connection():
                self.test_completed.emit(True, "")
            else:
                self.test_completed.emit(False, "连接测试失败，请检查API密钥和网络连接")
                
        except Exception as e:
            self.test_completed.emit(False, f"连接测试出错: {str(e)}")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setMinimumWidth(400)
        self.llm_config_path = os.path.join('config', 'llm_config.json')
        self.whisper_config_path = os.path.join('config', 'whisper_config.json')
        self.api_test_thread = None
        self.init_ui()
        self.load_config()

    def get_infer_devices(self):
        devices = ['cpu']
        try:
            import torch
            if torch.cuda.is_available():
                devices.append('cuda')
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                devices.append('mps')
        except Exception:
            pass
        return devices

    def init_ui(self):
        layout = QVBoxLayout()

        # API Key
        layout.addWidget(QLabel('API Key'))
        self.api_key_edit = QLineEdit()
        layout.addWidget(self.api_key_edit)

        # Model selection
        layout.addWidget(QLabel('Model'))
        self.model_combo = QComboBox()
        self.model_combo.addItems(['openai', 'deepseek'])
        layout.addWidget(self.model_combo)

        # Whisper inference device
        layout.addWidget(QLabel('Device'))
        self.infer_device_combo = QComboBox()
        self.infer_device_list = self.get_infer_devices()
        self.infer_device_combo.addItems(self.infer_device_list)
        layout.addWidget(self.infer_device_combo)

        # Whisper compute type
        layout.addWidget(QLabel('Compute Type'))
        self.compute_type_combo = QComboBox()
        self.compute_type_combo.addItems(['int8', 'int16', 'float16', 'float32'])
        layout.addWidget(self.compute_type_combo)

        # Whisper parameters
        layout.addWidget(QLabel('Model Size'))
        self.model_size_combo = QComboBox()
        self.model_size_combo.addItems(['tiny', 'base', 'small', 'medium', 'large'])
        layout.addWidget(self.model_size_combo)

        layout.addWidget(QLabel('Beam Size'))
        self.beam_size_spin = QSpinBox()
        self.beam_size_spin.setRange(1, 10)
        layout.addWidget(self.beam_size_spin)

        # Input device selection
        layout.addWidget(QLabel('Input Device'))
        self.device_combo = QComboBox()
        self.device_list = self.get_input_devices()
        self.device_combo.addItems(self.device_list)
        layout.addWidget(self.device_combo)

        # Save button
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_config)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_input_devices(self):
        devices = []
        for idx, dev in enumerate(sd.query_devices()):
            if isinstance(dev, dict):
                max_input = int(dev.get('max_input_channels', 0))
                name = dev.get('name', str(idx))
            else:
                max_input = int(getattr(dev, 'max_input_channels', 0))
                name = getattr(dev, 'name', str(idx))
            if max_input > 0:
                devices.append(f"{name} (id={idx})")
        return devices if devices else ['Default']

    def load_config(self):
        # LLM config
        if os.path.exists(self.llm_config_path):
            with open(self.llm_config_path, 'r', encoding='utf-8') as f:
                llm_cfg = json.load(f)
            provider = llm_cfg.get('default_provider', 'deepseek')
            self.model_combo.setCurrentText(provider)
            providers = llm_cfg.get('providers', {})
            if provider in providers:
                api_key = providers[provider].get('api_key', '')
                self.api_key_edit.setText(api_key)
        # Whisper config
        if os.path.exists(self.whisper_config_path):
            with open(self.whisper_config_path, 'r', encoding='utf-8') as f:
                whisper_cfg = json.load(f)
            # 推理设备
            device = whisper_cfg.get('device', 'cpu')
            if device in self.infer_device_list:
                self.infer_device_combo.setCurrentText(device)
            # 推理精度
            compute_type = whisper_cfg.get('compute_type', 'int8')
            self.compute_type_combo.setCurrentText(compute_type)
            self.model_size_combo.setCurrentText(whisper_cfg.get('model_size', 'base'))
            self.beam_size_spin.setValue(whisper_cfg.get('beam_size', 5))
            # Input device
            input_device = whisper_cfg.get('input_device', None)
            if input_device and input_device in self.device_list:
                self.device_combo.setCurrentText(input_device)

    def test_api_connection(self, provider_type, api_key):
        """测试API连接"""
        if not api_key.strip():
            return True, ""  # 空API密钥不进行测试
        
        # 显示进度对话框
        progress = QProgressDialog("正在测试API连接...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)  # 禁用取消按钮
        progress.show()
        
        # 创建并启动测试线程
        self.api_test_thread = APITestThread(provider_type, api_key)
        self.api_test_thread.test_completed.connect(self.on_api_test_completed)
        self.api_test_thread.test_completed.connect(progress.close)
        self.api_test_thread.start()
        
        return True, ""  # 返回True表示测试已启动

    def save_config(self):
        # 获取当前设置
        provider = self.model_combo.currentText()
        api_key = self.api_key_edit.text().strip()
        
        # 如果有API密钥，先测试连接
        if api_key:
            self.save_btn.setEnabled(False)
            self.api_test_pending_save = True  # 标记等待保存
            self.test_api_connection(provider, api_key)
            return  # 等待异步回调
        
        self._do_save_config()

    def _do_save_config(self):
        provider = self.model_combo.currentText()
        api_key = self.api_key_edit.text().strip()
        # 保存LLM配置
        llm_cfg = {}
        if os.path.exists(self.llm_config_path):
            with open(self.llm_config_path, 'r', encoding='utf-8') as f:
                llm_cfg = json.load(f)
        llm_cfg['default_provider'] = provider
        if 'providers' not in llm_cfg:
            llm_cfg['providers'] = {}
        if provider not in llm_cfg['providers']:
            llm_cfg['providers'][provider] = {}
        llm_cfg['providers'][provider]['api_key'] = api_key
        with open(self.llm_config_path, 'w', encoding='utf-8') as f:
            json.dump(llm_cfg, f, indent=2, ensure_ascii=False)
        # 保存Whisper配置
        whisper_cfg = {}
        if os.path.exists(self.whisper_config_path):
            with open(self.whisper_config_path, 'r', encoding='utf-8') as f:
                whisper_cfg = json.load(f)
        whisper_cfg['device'] = self.infer_device_combo.currentText()
        whisper_cfg['compute_type'] = self.compute_type_combo.currentText()
        whisper_cfg['model_size'] = self.model_size_combo.currentText()
        whisper_cfg['beam_size'] = self.beam_size_spin.value()
        whisper_cfg['input_device'] = self.device_combo.currentText()
        with open(self.whisper_config_path, 'w', encoding='utf-8') as f:
            json.dump(whisper_cfg, f, indent=2, ensure_ascii=False)
        QMessageBox.information(self, 'Info', 'Settings saved!')
        self.accept()

    def on_api_test_completed(self, success, error_message):
        self.save_btn.setEnabled(True)
        if not success:
            QMessageBox.critical(self, 'API连接测试失败', 
                               f'无法连接到{self.model_combo.currentText()} API:\n{error_message}\n\n请检查：\n1. API密钥是否正确\n2. 网络连接是否正常\n3. API服务是否可用')
            return False
        # 只有测试通过才保存
        if hasattr(self, 'api_test_pending_save') and self.api_test_pending_save:
            self.api_test_pending_save = False
            self._do_save_config()
        return True 