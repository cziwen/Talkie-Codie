from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QMessageBox)
import json
import os
import sounddevice as sd

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setMinimumWidth(400)
        self.llm_config_path = os.path.join('config', 'llm_config.json')
        self.whisper_config_path = os.path.join('config', 'whisper_config.json')
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

    def save_config(self):
        # Save LLM config
        llm_cfg = {}
        if os.path.exists(self.llm_config_path):
            with open(self.llm_config_path, 'r', encoding='utf-8') as f:
                llm_cfg = json.load(f)
        provider = self.model_combo.currentText()
        api_key = self.api_key_edit.text().strip()
        llm_cfg['default_provider'] = provider
        if 'providers' not in llm_cfg:
            llm_cfg['providers'] = {}
        if provider not in llm_cfg['providers']:
            llm_cfg['providers'][provider] = {}
        llm_cfg['providers'][provider]['api_key'] = api_key
        with open(self.llm_config_path, 'w', encoding='utf-8') as f:
            json.dump(llm_cfg, f, indent=2, ensure_ascii=False)
        # Save Whisper config
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