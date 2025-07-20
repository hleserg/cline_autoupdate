"""
Оптимизатор workflow для Cline
Создает и оптимизирует workflow файлы на основе анализа проекта
"""

from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime

class WorkflowOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Базовые шаблоны workflow
        self.base_workflows = {
            'development': {
                'name': 'Разработка нового функционала',
                'description': 'Стандартный процесс разработки новой функции',
                'steps': [
                    "1. Анализ требований и планирование архитектуры",
                    "2. Создание или обновление технического задания",
                    "3. Разработка основной логики функции",
                    "4. Написание unit-тестов для новой функциональности",
                    "5. Создание интеграционных тестов при необходимости",
                    "6. Обновление документации (README, docs, комментарии)",
                    "7. Проведение код-ревью и рефакторинг при необходимости",
                    "8. Тестирование в тестовой среде",
                    "9. Создание changelog записи",
                    "10. Подготовка к деплою"
                ]
            },
            'bugfix': {
                'name': 'Исправление багов',
                'description': 'Процесс исправления обнаруженных ошибок',
                'steps': [
                    "1. Воспроизведение и подтверждение бага",
                    "2. Анализ кода и выявление причины проблемы",
                    "3. Разработка тест-кейса для воспроизведения бага",
                    "4. Исправление проблемы в коде",
                    "5. Проверка, что тест теперь проходит успешно",
                    "6. Запуск полного набора тестов",
                    "7. Обновление документации при необходимости",
                    "8. Код-ревью изменений",
                    "9. Тестирование исправления в тестовой среде",
                    "10. Документирование исправления в changelog"
                ]
            },
            'refactoring': {
                'name': 'Рефакторинг кода',
                'description': 'Улучшение структуры и качества существующего кода',
                'steps': [
                    "1. Определение области для рефакторинга",
                    "2. Создание плана рефакторинга",
                    "3. Написание тестов для покрытия текущего поведения",
                    "4. Поэтапное проведение рефакторинга",
                    "5. Запуск тестов после каждого значимого изменения",
                    "6. Обновление документации и комментариев",
                    "7. Проверка производительности после рефакторинга",
                    "8. Код-ревью изменений",
                    "9. Интеграционное тестирование",
                    "10. Документирование изменений"
                ]
            },
            'testing': {
                'name': 'Тестирование',
                'description': 'Создание и поддержание тестового покрытия',
                'steps': [
                    "1. Анализ текущего тестового покрытия",
                    "2. Определение критических областей для тестирования",
                    "3. Написание unit-тестов для новых компонентов",
                    "4. Создание интеграционных тестов",
                    "5. Разработка end-to-end тестов при необходимости",
                    "6. Настройка автоматического запуска тестов",
                    "7. Создание моков для внешних зависимостей",
                    "8. Тестирование граничных случаев и ошибок",
                    "9. Анализ и улучшение покрытия тестами",
                    "10. Документирование тестовых сценариев"
                ]
            },
            'deployment': {
                'name': 'Деплоймент',
                'description': 'Процесс развертывания приложения',
                'steps': [
                    "1. Подготовка production окружения",
                    "2. Проверка всех тестов перед деплоем",
                    "3. Создание резервной копии текущей версии",
                    "4. Обновление переменных окружения при необходимости",
                    "5. Запуск деплоймента в production",
                    "6. Проверка работоспособности сервиса после деплоя",
                    "7. Мониторинг логов и метрик",
                    "8. Smoke тестирование основной функциональности",
                    "9. Уведомление команды об успешном деплое",
                    "10. Обновление документации по развертыванию"
                ]
            }
        }
        
        # Специфичные workflow для языков программирования
        self.language_workflows = {
            'python': {
                'python_setup': {
                    'name': 'Настройка Python проекта',
                    'description': 'Инициализация и настройка Python проекта',
                    'steps': [
                        "1. Создание виртуального окружения (python -m venv venv)",
                        "2. Активация виртуального окружения",
                        "3. Создание requirements.txt или pyproject.toml",
                        "4. Установка зависимостей разработки (pytest, black, flake8)",
                        "5. Настройка pre-commit hooks",
                        "6. Создание .gitignore для Python проекта",
                        "7. Настройка IDE/редактора (VS Code settings)",
                        "8. Создание базовой структуры проекта",
                        "9. Инициализация тестового фреймворка",
                        "10. Создание README.md с инструкциями по запуску"
                    ]
                },
                'python_package': {
                    'name': 'Создание Python пакета',
                    'description': 'Процесс создания переиспользуемого Python пакета',
                    'steps': [
                        "1. Создание setup.py или pyproject.toml",
                        "2. Определение структуры пакета (__init__.py файлы)",
                        "3. Написание основного функционала модулей",
                        "4. Создание comprehensive тестов",
                        "5. Написание документации (docstrings, README)",
                        "6. Настройка CI/CD для автоматического тестирования",
                        "7. Версионирование пакета (semantic versioning)",
                        "8. Создание CHANGELOG.md",
                        "9. Подготовка к публикации в PyPI",
                        "10. Создание документации на Read the Docs"
                    ]
                }
            },
            'javascript': {
                'node_setup': {
                    'name': 'Настройка Node.js проекта',
                    'description': 'Инициализация Node.js/npm проекта',
                    'steps': [
                        "1. Инициализация проекта (npm init)",
                        "2. Установка зависимостей разработки (eslint, prettier, jest)",
                        "3. Создание .eslintrc и .prettierrc конфигураций",
                        "4. Настройка npm scripts в package.json",
                        "5. Создание .gitignore для Node.js",
                        "6. Настройка Jest для тестирования",
                        "7. Создание базовой структуры проекта (src, tests)",
                        "8. Настройка Babel при необходимости",
                        "9. Инициализация Git репозитория",
                        "10. Создание README с инструкциями"
                    ]
                },
                'react_component': {
                    'name': 'Создание React компонента',
                    'description': 'Процесс разработки React компонента',
                    'steps': [
                        "1. Планирование интерфейса и props компонента",
                        "2. Создание базовой структуры компонента",
                        "3. Добавление PropTypes или TypeScript типов",
                        "4. Написание unit-тестов с Jest и React Testing Library",
                        "5. Создание Storybook истории для компонента",
                        "6. Добавление стилизации (CSS/styled-components)",
                        "7. Тестирование accessibility (a11y)",
                        "8. Оптимизация производительности (React.memo, useMemo)",
                        "9. Интеграция в основное приложение",
                        "10. Документирование компонента и его API"
                    ]
                }
            }
        }
        
        # Workflow для фреймворков
        self.framework_workflows = {
            'django': {
                'django_app': {
                    'name': 'Создание Django приложения',
                    'description': 'Разработка нового Django app',
                    'steps': [
                        "1. Создание Django app (python manage.py startapp)",
                        "2. Регистрация app в settings.py",
                        "3. Создание моделей в models.py",
                        "4. Создание и применение миграций",
                        "5. Создание views для обработки запросов",
                        "6. Настройка URLs в urls.py",
                        "7. Создание шаблонов в templates/",
                        "8. Написание тестов для models и views",
                        "9. Создание Django forms при необходимости",
                        "10. Настройка admin interface"
                    ]
                }
            },
            'flask': {
                'flask_api': {
                    'name': 'Создание Flask API',
                    'description': 'Разработка RESTful API на Flask',
                    'steps': [
                        "1. Настройка Flask приложения и blueprints",
                        "2. Создание моделей с SQLAlchemy",
                        "3. Настройка сериализации с Marshmallow",
                        "4. Создание endpoints для CRUD операций",
                        "5. Добавление валидации данных",
                        "6. Настройка аутентификации и авторизации",
                        "7. Написание unit и integration тестов",
                        "8. Создание API документации (Swagger/OpenAPI)",
                        "9. Добавление логирования и обработки ошибок",
                        "10. Настройка CORS и security headers"
                    ]
                }
            }
        }
        
    def optimize_workflows(self, config_data: Dict[str, Any], performance_data: Dict[str, Any]) -> Dict[str, str]:
        """Оптимизация workflow файлов на основе анализа"""
        
        self.logger.info("🔄 Оптимизация workflow файлов")
        
        workflows = {}
        
        # Добавление базовых workflow
        workflows.update(self._select_base_workflows(config_data, performance_data))
        
        # Добавление языко-специфичных workflow
        workflows.update(self._select_language_workflows(config_data))
        
        # Добавление фреймворк-специфичных workflow
        workflows.update(self._select_framework_workflows(config_data))
        
        # Сохранение существующих пользовательских workflow
        workflows.update(self._preserve_custom_workflows(config_data))
        
        # Адаптация workflow на основе производительности
        workflows = self._adapt_workflows_for_performance(workflows, performance_data)
        
        self.logger.info(f"✅ Создано/обновлено {len(workflows)} workflow файлов")
        
        return workflows
        
    def _select_base_workflows(self, config_data: Dict[str, Any], performance_data: Dict[str, Any]) -> Dict[str, str]:
        """Выбор базовых workflow"""
        selected = {}
        
        # Всегда добавляем основные workflow
        selected['development'] = self._format_workflow(self.base_workflows['development'])
        selected['bugfix'] = self._format_workflow(self.base_workflows['bugfix'])
        
        # Добавляем рефакторинг если есть признаки legacy кода
        if self._needs_refactoring(config_data):
            selected['refactoring'] = self._format_workflow(self.base_workflows['refactoring'])
            
        # Добавляем тестирование если недостаточно тестов
        if not self._has_adequate_tests(config_data):
            selected['testing'] = self._format_workflow(self.base_workflows['testing'])
            
        # Добавляем деплоймент для веб-проектов
        if self._is_deployable_project(config_data):
            selected['deployment'] = self._format_workflow(self.base_workflows['deployment'])
            
        return selected
        
    def _select_language_workflows(self, config_data: Dict[str, Any]) -> Dict[str, str]:
        """Выбор workflow для конкретных языков"""
        selected = {}
        
        languages = config_data.get('project_structure', {}).get('languages', [])
        
        for language in languages:
            if language in self.language_workflows:
                lang_workflows = self.language_workflows[language]
                
                for workflow_name, workflow_data in lang_workflows.items():
                    # Проверяем, нужен ли конкретный workflow
                    if self._is_workflow_needed(workflow_name, config_data):
                        selected[workflow_name] = self._format_workflow(workflow_data)
                        
        return selected
        
    def _select_framework_workflows(self, config_data: Dict[str, Any]) -> Dict[str, str]:
        """Выбор workflow для фреймворков"""
        selected = {}
        
        frameworks = config_data.get('project_structure', {}).get('frameworks', [])
        
        # Добавляем обнаруженные фреймворки
        detected_frameworks = self._detect_frameworks_from_files(config_data)
        frameworks.extend(detected_frameworks)
        
        for framework in frameworks:
            if framework in self.framework_workflows:
                fw_workflows = self.framework_workflows[framework]
                
                for workflow_name, workflow_data in fw_workflows.items():
                    if self._is_workflow_needed(workflow_name, config_data):
                        selected[workflow_name] = self._format_workflow(workflow_data)
                        
        return selected
        
    def _preserve_custom_workflows(self, config_data: Dict[str, Any]) -> Dict[str, str]:
        """Сохранение пользовательских workflow"""
        custom_workflows = {}
        
        current_workflows = config_data.get('current_workflows', {})
        if current_workflows.get('exists'):
            workflows_data = current_workflows.get('workflows', {})
            
            for workflow_name, workflow_info in workflows_data.items():
                # Сохраняем пользовательские workflow, которые не являются базовыми
                if self._is_custom_workflow(workflow_name, workflow_info):
                    custom_workflows[workflow_name] = workflow_info['content']
                    
        return custom_workflows
        
    def _adapt_workflows_for_performance(self, workflows: Dict[str, str], performance_data: Dict[str, Any]) -> Dict[str, str]:
        """Адаптация workflow на основе проблем производительности"""
        
        performance_issues = performance_data.get('performance_issues', [])
        
        if performance_issues:
            # Добавляем специальный workflow для оптимизации производительности
            perf_workflow = {
                'name': 'Оптимизация производительности',
                'description': 'Процесс выявления и устранения проблем производительности',
                'steps': [
                    "1. Профилирование приложения для выявления узких мест",
                    "2. Анализ использования памяти и CPU",
                    "3. Оптимизация алгоритмов и структур данных",
                    "4. Внедрение кеширования где это уместно",
                    "5. Оптимизация запросов к базе данных",
                    "6. Минификация и сжатие статических ресурсов",
                    "7. Настройка CDN и балансировки нагрузки",
                    "8. Мониторинг метрик производительности",
                    "9. A/B тестирование оптимизаций",
                    "10. Документирование изменений производительности"
                ]
            }
            
            # Добавляем специфичные шаги на основе типа проблем
            additional_steps = []
            for issue in performance_issues:
                if issue['type'] == 'memory':
                    additional_steps.append("- Анализ утечек памяти и оптимизация GC")
                elif issue['type'] == 'cpu':
                    additional_steps.append("- Распараллеливание CPU-интенсивных операций")
                    
            if additional_steps:
                perf_workflow['steps'].extend(additional_steps)
                
            workflows['performance_optimization'] = self._format_workflow(perf_workflow)
            
        return workflows
        
    def _format_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Форматирование workflow в markdown"""
        lines = []
        
        lines.append(f"# {workflow_data['name']}")
        lines.append("")
        lines.append(f"**Описание:** {workflow_data['description']}")
        lines.append("")
        lines.append("## Шаги выполнения:")
        lines.append("")
        
        for step in workflow_data['steps']:
            lines.append(f"{step}")
            
        lines.append("")
        lines.append("## Дополнительные заметки:")
        lines.append("")
        lines.append("- Всегда создавайте резервные копии перед критическими изменениями")
        lines.append("- Проводите код-ревью для всех значимых изменений")
        lines.append("- Документируйте все изменения в changelog")
        lines.append("- Тестируйте изменения в изолированной среде")
        lines.append("")
        lines.append(f"*Создано автоматически: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return '\n'.join(lines)
        
    def _needs_refactoring(self, config_data: Dict[str, Any]) -> bool:
        """Определение необходимости рефакторинга"""
        project_structure = config_data.get('project_structure', {})
        
        # Если проект большой, вероятно нужен рефакторинг
        total_files = project_structure.get('total_files', 0)
        if total_files > 50:
            return True
            
        # Если есть много разных языков, может потребоваться рефакторинг
        languages_count = len(project_structure.get('languages', []))
        if languages_count > 2:
            return True
            
        return False
        
    def _has_adequate_tests(self, config_data: Dict[str, Any]) -> bool:
        """Проверка достаточности тестового покрытия"""
        project_structure = config_data.get('project_structure', {})
        file_counts = project_structure.get('file_counts', {})
        
        # Простая эвристика: ищем тестовые файлы
        test_files = 0
        total_files = sum(file_counts.values())
        
        for ext, count in file_counts.items():
            if 'test' in ext or 'spec' in ext:
                test_files += count
                
        # Если тестовых файлов менее 20% от общего количества
        if total_files > 0:
            test_ratio = test_files / total_files
            return test_ratio >= 0.2
            
        return False
        
    def _is_deployable_project(self, config_data: Dict[str, Any]) -> bool:
        """Проверка, является ли проект развертываемым"""
        project_structure = config_data.get('project_structure', {})
        
        languages = project_structure.get('languages', [])
        frameworks = project_structure.get('frameworks', [])
        
        # Веб-проекты обычно развертываются
        web_indicators = ['javascript', 'typescript', 'python', 'nodejs']
        
        return any(indicator in languages + frameworks for indicator in web_indicators)
        
    def _is_workflow_needed(self, workflow_name: str, config_data: Dict[str, Any]) -> bool:
        """Определение необходимости конкретного workflow"""
        
        # Логика определения необходимости workflow
        if workflow_name == 'python_setup':
            languages = config_data.get('project_structure', {}).get('languages', [])
            return 'python' in languages
            
        elif workflow_name == 'node_setup':
            languages = config_data.get('project_structure', {}).get('languages', [])
            return 'javascript' in languages or 'typescript' in languages
            
        elif workflow_name == 'react_component':
            # Проверяем, есть ли признаки React проекта
            return self._has_react_indicators(config_data)
            
        elif workflow_name.endswith('_app') or workflow_name.endswith('_api'):
            # Фреймворк-специфичные workflow
            return True
            
        return True
        
    def _is_custom_workflow(self, workflow_name: str, workflow_info: Dict[str, Any]) -> bool:
        """Проверка, является ли workflow пользовательским"""
        
        # Проверяем, что workflow не является одним из базовых
        base_workflow_names = set(self.base_workflows.keys())
        
        if workflow_name in base_workflow_names:
            return False
            
        # Проверяем языко-специфичные workflow
        for lang_workflows in self.language_workflows.values():
            if workflow_name in lang_workflows:
                return False
                
        # Проверяем фреймворк-специфичные workflow
        for fw_workflows in self.framework_workflows.values():
            if workflow_name in fw_workflows:
                return False
                
        return True
        
    def _detect_frameworks_from_files(self, config_data: Dict[str, Any]) -> List[str]:
        """Обнаружение фреймворков на основе файловой структуры"""
        detected = []
        
        # Можно расширить логику обнаружения
        # на основе анализа содержимого файлов конфигурации
        
        return detected
        
    def _has_react_indicators(self, config_data: Dict[str, Any]) -> bool:
        """Проверка наличия признаков React проекта"""
        project_structure = config_data.get('project_structure', {})
        
        # Простая проверка наличия .jsx файлов
        file_counts = project_structure.get('file_counts', {})
        
        return '.jsx' in file_counts or '.tsx' in file_counts
