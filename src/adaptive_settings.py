"""
Система адаптивных настроек Cline
Генерирует оптимальные настройки на основе анализа системы и проекта
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

class AdaptiveSettings:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Базовые настройки по умолчанию
        self.default_settings = {
            'cline_settings': {
                'autoApprove': False,
                'alwaysAllowReadOnly': True,
                'alwaysAllowWriteOnly': False,
                'requestLimit': 25,
                'contextWindow': 200000,
                'maxResponseTokens': 8192,
                'temperature': 0.1,
                'debugMode': False,
                'experimentalFeatures': False,
                'customInstructions': "",
                'preferredLanguage': "ru",
                'codeStyle': {
                    'indentation': 4,
                    'quotes': "double",
                    'semicolons': True,
                    'trailingCommas': True
                },
                'performance': {
                    'enableCaching': True,
                    'maxCacheSize': 100,
                    'parallelProcessing': False,
                    'memoryOptimization': False
                },
                'security': {
                    'restrictFileAccess': True,
                    'sanitizeInputs': True,
                    'logSecurityEvents': True
                }
            }
        }
        
        # Настройки для разных типов проектов
        self.project_specific_settings = {
            'python': {
                'codeStyle': {
                    'indentation': 4,
                    'quotes': "double",
                    'lineLength': 88
                },
                'linting': {
                    'enableFlake8': True,
                    'enableBlack': True,
                    'enableMypy': True
                },
                'testing': {
                    'framework': 'pytest',
                    'coverage': True,
                    'autoDiscovery': True
                }
            },
            'javascript': {
                'codeStyle': {
                    'indentation': 2,
                    'quotes': "single",
                    'semicolons': False,
                    'trailingCommas': True
                },
                'linting': {
                    'enableESLint': True,
                    'enablePrettier': True
                },
                'build': {
                    'enableSourceMaps': True,
                    'minification': True
                }
            },
            'typescript': {
                'codeStyle': {
                    'indentation': 2,
                    'quotes': "single",
                    'semicolons': False,
                    'strictMode': True
                },
                'typeChecking': {
                    'strict': True,
                    'noImplicitAny': True,
                    'strictNullChecks': True
                }
            },
            'web': {
                'features': {
                    'autoReload': True,
                    'livePreview': True,
                    'responsiveDesign': True
                },
                'optimization': {
                    'imageOptimization': True,
                    'cssMinification': True,
                    'jsMinification': True
                }
            }
        }
        
        # Настройки для производительности системы
        self.performance_settings = {
            'high_memory': {
                'contextWindow': 300000,
                'maxResponseTokens': 12288,
                'enableCaching': True,
                'maxCacheSize': 200,
                'parallelProcessing': True
            },
            'low_memory': {
                'contextWindow': 100000,
                'maxResponseTokens': 4096,
                'enableCaching': False,
                'maxCacheSize': 50,
                'parallelProcessing': False,
                'memoryOptimization': True
            },
            'high_cpu': {
                'parallelProcessing': True,
                'backgroundProcessing': True,
                'optimizeAlgorithms': True
            },
            'low_cpu': {
                'parallelProcessing': False,
                'backgroundProcessing': False,
                'simpleAlgorithms': True
            }
        }
        
    def generate_adaptive_config(self, config_data: Dict[str, Any], performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация адаптивной конфигурации"""
        
        self.logger.info("⚙️ Генерация адаптивных настроек")
        
        # Начинаем с базовых настроек
        adaptive_config = self._deep_copy(self.default_settings)
        
        # Адаптация на основе типа проекта
        project_settings = self._adapt_for_project_type(config_data)
        adaptive_config = self._merge_settings(adaptive_config, project_settings)
        
        # Адаптация на основе производительности системы
        performance_settings = self._adapt_for_performance(performance_data)
        adaptive_config = self._merge_settings(adaptive_config, performance_settings)
        
        # Адаптация на основе размера проекта
        scale_settings = self._adapt_for_project_scale(config_data)
        adaptive_config = self._merge_settings(adaptive_config, scale_settings)
        
        # Адаптация на основе паттернов использования
        usage_settings = self._adapt_for_usage_patterns(config_data, performance_data)
        adaptive_config = self._merge_settings(adaptive_config, usage_settings)
        
        # Сохранение пользовательских настроек
        user_settings = self._preserve_user_settings(config_data)
        adaptive_config = self._merge_settings(adaptive_config, user_settings)
        
        # Добавление дополнительных настроек VS Code
        vscode_config = self._generate_vscode_config(adaptive_config, config_data)
        adaptive_config.update(vscode_config)
        
        self.logger.info("✅ Адаптивные настройки сгенерированы")
        
        return adaptive_config
        
    def _adapt_for_project_type(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Адаптация настроек для типа проекта"""
        settings = {'cline_settings': {}}
        
        project_structure = config_data.get('project_structure', {})
        project_type = project_structure.get('project_type', 'unknown')
        languages = project_structure.get('languages', [])
        
        # Применяем настройки для основного языка
        if languages:
            primary_language = languages[0]  # Берем первый язык как основной
            
            if primary_language in self.project_specific_settings:
                lang_settings = self.project_specific_settings[primary_language]
                settings['cline_settings'].update(lang_settings)
                
        # Применяем настройки для типа проекта
        if project_type in self.project_specific_settings:
            type_settings = self.project_specific_settings[project_type]
            settings['cline_settings'].update(type_settings)
            
        # Специальная логика для веб-проектов
        if self._is_web_project(project_structure):
            web_settings = self.project_specific_settings.get('web', {})
            settings['cline_settings'].update(web_settings)
            
        return settings
        
    def _adapt_for_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Адаптация настроек для производительности системы"""
        settings = {'cline_settings': {}}
        
        system_metrics = performance_data.get('system_metrics', {})
        performance_issues = performance_data.get('performance_issues', [])
        
        if not system_metrics:
            return settings
            
        memory_info = system_metrics.get('memory', {})
        cpu_info = system_metrics.get('cpu', {})
        
        # Адаптация для памяти
        memory_percent = memory_info.get('percent', 0)
        memory_total_gb = memory_info.get('total', 0) / (1024**3)
        
        if memory_percent > 80 or memory_total_gb < 4:
            # Низкая память - консервативные настройки
            low_mem_settings = self.performance_settings['low_memory']
            settings['cline_settings'].update(low_mem_settings)
        elif memory_total_gb > 16:
            # Высокая память - агрессивные настройки
            high_mem_settings = self.performance_settings['high_memory']
            settings['cline_settings'].update(high_mem_settings)
            
        # Адаптация для CPU
        cpu_percent = cpu_info.get('percent', 0)
        cpu_count = cpu_info.get('count', 1)
        
        if cpu_percent > 80 or cpu_count < 4:
            # Низкая производительность CPU
            low_cpu_settings = self.performance_settings['low_cpu']
            settings['cline_settings'].update(low_cpu_settings)
        elif cpu_count > 8:
            # Высокая производительность CPU
            high_cpu_settings = self.performance_settings['high_cpu']
            settings['cline_settings'].update(high_cpu_settings)
            
        # Специальные настройки для проблем производительности
        for issue in performance_issues:
            if issue['type'] == 'memory' and issue['severity'] == 'high':
                settings['cline_settings']['memoryOptimization'] = True
                settings['cline_settings']['enableCaching'] = False
            elif issue['type'] == 'cpu' and issue['severity'] == 'high':
                settings['cline_settings']['parallelProcessing'] = False
                settings['cline_settings']['maxResponseTokens'] = 4096
                
        return settings
        
    def _adapt_for_project_scale(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Адаптация настроек для масштаба проекта"""
        settings = {'cline_settings': {}}
        
        project_structure = config_data.get('project_structure', {})
        total_files = project_structure.get('total_files', 0)
        languages_count = len(project_structure.get('languages', []))
        
        # Настройки для больших проектов
        if total_files > 100:
            settings['cline_settings'].update({
                'requestLimit': 50,
                'contextWindow': 250000,
                'enableCaching': True,
                'maxCacheSize': 150
            })
        elif total_files > 50:
            settings['cline_settings'].update({
                'requestLimit': 35,
                'contextWindow': 200000,
                'enableCaching': True
            })
        else:
            # Небольшие проекты
            settings['cline_settings'].update({
                'requestLimit': 20,
                'contextWindow': 150000
            })
            
        # Настройки для многоязычных проектов
        if languages_count > 2:
            settings['cline_settings'].update({
                'contextWindow': settings['cline_settings'].get('contextWindow', 200000) + 50000,
                'maxResponseTokens': 10240
            })
            
        return settings
        
    def _adapt_for_usage_patterns(self, config_data: Dict[str, Any], performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Адаптация на основе паттернов использования"""
        settings = {'cline_settings': {}}
        
        usage_patterns = config_data.get('usage_patterns', {})
        
        # Если пользователь часто использует Cline
        sessions_count = usage_patterns.get('sessions_count', 0)
        if sessions_count > 100:
            settings['cline_settings'].update({
                'autoApprove': True,  # Для опытных пользователей
                'experimentalFeatures': True,
                'debugMode': False  # Отключаем отладку для скорости
            })
        elif sessions_count < 10:
            # Новые пользователи - консервативные настройки
            settings['cline_settings'].update({
                'autoApprove': False,
                'experimentalFeatures': False,
                'debugMode': True  # Включаем отладку для обучения
            })
            
        # Анализ частых ошибок
        error_patterns = usage_patterns.get('error_patterns', [])
        if len(error_patterns) > 10:
            settings['cline_settings'].update({
                'temperature': 0.05,  # Более детерминированные ответы
                'security': {
                    'restrictFileAccess': True,
                    'sanitizeInputs': True
                }
            })
            
        return settings
        
    def _preserve_user_settings(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Сохранение пользовательских настроек"""
        user_settings = {'cline_settings': {}}
        
        vscode_settings = config_data.get('vscode_settings', {})
        current_cline_settings = vscode_settings.get('cline_settings', {})
        
        # Список настроек, которые должны сохраняться
        preserve_keys = [
            'customInstructions',
            'preferredLanguage',
            'autoApprove'  # Только если явно установлено пользователем
        ]
        
        for key in preserve_keys:
            if key in current_cline_settings:
                user_settings['cline_settings'][key] = current_cline_settings[key]
                
        return user_settings
        
    def _generate_vscode_config(self, adaptive_config: Dict[str, Any], config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация дополнительных настроек VS Code"""
        vscode_config = {}
        
        project_structure = config_data.get('project_structure', {})
        languages = project_structure.get('languages', [])
        
        # Настройки редактора на основе проекта
        if 'python' in languages:
            vscode_config.update({
                'python.defaultInterpreterPath': './venv/bin/python',
                'python.linting.enabled': True,
                'python.linting.pylintEnabled': True,
                'python.formatting.provider': 'black',
                'python.testing.pytestEnabled': True
            })
            
        if 'javascript' in languages or 'typescript' in languages:
            vscode_config.update({
                'eslint.enable': True,
                'prettier.enable': True,
                'javascript.preferences.includePackageJsonAutoImports': 'auto',
                'typescript.preferences.includePackageJsonAutoImports': 'auto'
            })
            
        # Общие настройки редактора
        cline_settings = adaptive_config.get('cline_settings', {})
        code_style = cline_settings.get('codeStyle', {})
        
        if code_style:
            vscode_config.update({
                'editor.tabSize': code_style.get('indentation', 4),
                'editor.insertSpaces': True,
                'editor.detectIndentation': False
            })
            
        # Настройки производительности
        performance = cline_settings.get('performance', {})
        if performance.get('memoryOptimization'):
            vscode_config.update({
                'typescript.disableAutomaticTypeAcquisition': True,
                'search.followSymlinks': False,
                'files.watcherExclude': {
                    '**/.git/objects/**': True,
                    '**/.git/subtree-cache/**': True,
                    '**/node_modules/**': True,
                    '**/.hg/store/**': True
                }
            })
            
        return vscode_config
        
    def _is_web_project(self, project_structure: Dict[str, Any]) -> bool:
        """Проверка, является ли проект веб-проектом"""
        languages = project_structure.get('languages', [])
        frameworks = project_structure.get('frameworks', [])
        
        web_indicators = ['javascript', 'typescript', 'html', 'css']
        web_frameworks = ['nodejs', 'react', 'vue', 'angular']
        
        return (any(lang in web_indicators for lang in languages) or 
                any(fw in web_frameworks for fw in frameworks))
                
    def _deep_copy(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Глубокое копирование словаря"""
        if isinstance(obj, dict):
            return {key: self._deep_copy(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
            
    def _merge_settings(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Слияние настроек с приоритетом для update"""
        result = self._deep_copy(base)
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = self._deep_copy(value)
                
        return result
        
    def export_settings_summary(self, config: Dict[str, Any]) -> str:
        """Экспорт сводки настроек в читаемом формате"""
        lines = []
        
        lines.append("# Сводка адаптивных настроек Cline")
        lines.append(f"# Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        cline_settings = config.get('cline_settings', {})
        
        # Основные настройки
        lines.append("## Основные настройки")
        lines.append("")
        lines.append(f"- Лимит запросов: {cline_settings.get('requestLimit', 25)}")
        lines.append(f"- Размер контекстного окна: {cline_settings.get('contextWindow', 200000)}")
        lines.append(f"- Максимальные токены ответа: {cline_settings.get('maxResponseTokens', 8192)}")
        lines.append(f"- Температура: {cline_settings.get('temperature', 0.1)}")
        lines.append(f"- Автоподтверждение: {'Да' if cline_settings.get('autoApprove') else 'Нет'}")
        lines.append("")
        
        # Настройки производительности
        performance = cline_settings.get('performance', {})
        if performance:
            lines.append("## Производительность")
            lines.append("")
            lines.append(f"- Кеширование: {'Включено' if performance.get('enableCaching') else 'Выключено'}")
            lines.append(f"- Размер кеша: {performance.get('maxCacheSize', 100)}")
            lines.append(f"- Параллельная обработка: {'Да' if performance.get('parallelProcessing') else 'Нет'}")
            lines.append(f"- Оптимизация памяти: {'Да' if performance.get('memoryOptimization') else 'Нет'}")
            lines.append("")
            
        # Стиль кода
        code_style = cline_settings.get('codeStyle', {})
        if code_style:
            lines.append("## Стиль кода")
            lines.append("")
            lines.append(f"- Отступы: {code_style.get('indentation', 4)} пробелов")
            lines.append(f"- Кавычки: {code_style.get('quotes', 'double')}")
            lines.append(f"- Точки с запятой: {'Да' if code_style.get('semicolons') else 'Нет'}")
            lines.append("")
            
        # Безопасность
        security = cline_settings.get('security', {})
        if security:
            lines.append("## Безопасность")
            lines.append("")
            lines.append(f"- Ограничение доступа к файлам: {'Да' if security.get('restrictFileAccess') else 'Нет'}")
            lines.append(f"- Санитизация ввода: {'Да' if security.get('sanitizeInputs') else 'Нет'}")
            lines.append(f"- Логирование событий безопасности: {'Да' if security.get('logSecurityEvents') else 'Нет'}")
            lines.append("")
            
        lines.append("---")
        lines.append("*Настройки адаптированы автоматически на основе анализа проекта и системы*")
        
        return '\n'.join(lines)
