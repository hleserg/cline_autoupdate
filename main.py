#!/usr/bin/env python3
"""
Система автоматического улучшения настроек Cline
Запускается при каждом старте Cline и адаптивно улучшает конфигурацию
"""

import os
import json
import sys
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import platform

from src.config_analyzer import ConfigAnalyzer
from src.rules_generator import RulesGenerator
from src.workflow_optimizer import WorkflowOptimizer
from src.performance_tracker import PerformanceTracker
from src.adaptive_settings import AdaptiveSettings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cline_autoupdate.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ClineAutoUpdater:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_analyzer = ConfigAnalyzer()
        self.rules_generator = RulesGenerator()
        self.workflow_optimizer = WorkflowOptimizer()
        self.performance_tracker = PerformanceTracker()
        self.adaptive_settings = AdaptiveSettings()
        
        # Пути к конфигурационным файлам Cline
        self.setup_paths()
        
    def setup_paths(self):
        """Настройка путей к файлам конфигурации Cline"""
        system = platform.system()
        if system == "Windows":
            self.vscode_config_path = Path.home() / "AppData/Roaming/Code/User"
        elif system == "Darwin":  # macOS
            self.vscode_config_path = Path.home() / "Library/Application Support/Code/User"
        else:  # Linux
            self.vscode_config_path = Path.home() / ".config/Code/User"
            
        self.cline_config_path = self.vscode_config_path / "globalStorage/saoudrizwan.claude-dev"
        self.workspace_path = Path.cwd()
        
    def run(self):
        """Основная функция запуска автообновления"""
        self.logger.info("🚀 Запуск системы автообновления Cline")
        
        try:
            # 1. Анализ текущей конфигурации
            current_config = self.config_analyzer.analyze_current_setup(
                self.cline_config_path, self.workspace_path
            )
            
            # 2. Отслеживание производительности
            performance_data = self.performance_tracker.collect_metrics()
            
            # 3. Генерация улучшенных правил
            improved_rules = self.rules_generator.generate_improved_rules(
                current_config, performance_data
            )
            
            # 4. Оптимизация workflow
            optimized_workflows = self.workflow_optimizer.optimize_workflows(
                current_config, performance_data
            )
            
            # 5. Адаптивная настройка параметров
            adaptive_config = self.adaptive_settings.generate_adaptive_config(
                current_config, performance_data
            )
            
            # 6. Применение улучшений
            self.apply_improvements(improved_rules, optimized_workflows, adaptive_config)
            
            # 7. Сохранение метрик
            self.performance_tracker.save_session_data(performance_data)
            
            self.logger.info("✅ Автообновление завершено успешно")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при автообновлении: {e}")
            sys.exit(1)
            
    def apply_improvements(self, rules, workflows, config):
        """Применение улучшений к конфигурации Cline"""
        
        # Обновление .clinerules
        self.update_clinerules(rules)
        
        # Обновление workflow файлов
        self.update_workflows(workflows)
        
        # Обновление настроек VS Code для Cline
        self.update_vscode_settings(config)
        
        self.logger.info("🔄 Конфигурация обновлена")
        
    def update_clinerules(self, rules):
        """Обновление файла .clinerules"""
        clinerules_path = self.workspace_path / ".clinerules"
        
        with open(clinerules_path, 'w', encoding='utf-8') as f:
            f.write(rules)
            
        self.logger.info(f"📝 Обновлен файл .clinerules")
        
    def update_workflows(self, workflows):
        """Обновление workflow файлов"""
        workflows_dir = self.workspace_path / ".cline" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        for workflow_name, workflow_content in workflows.items():
            workflow_path = workflows_dir / f"{workflow_name}.md"
            with open(workflow_path, 'w', encoding='utf-8') as f:
                f.write(workflow_content)
                
        self.logger.info(f"📋 Обновлены workflow файлы: {list(workflows.keys())}")
        
    def update_vscode_settings(self, config):
        """Обновление настроек VS Code для Cline"""
        settings_path = self.vscode_config_path / "settings.json"
        
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            settings = {}
            
        # Обновление настроек Cline
        cline_settings = config.get('cline_settings', {})
        for key, value in cline_settings.items():
            settings[f"cline.{key}"] = value
            
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
            
        self.logger.info("⚙️ Обновлены настройки VS Code")

def main():
    """Точка входа"""
    # Создание необходимых директорий
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    updater = ClineAutoUpdater()
    updater.run()

if __name__ == "__main__":
    main()
