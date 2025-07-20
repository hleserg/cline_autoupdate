"""
Генератор правил для .clinerules
Создает и улучшает правила на основе анализа проекта и производительности
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set
import logging
from datetime import datetime

class RulesGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Базовые правила по категориям
        self.base_rules = {
            'general': [
                "Всегда используй понятные и описательные имена для переменных, функций и классов",
                "Добавляй комментарии для сложных алгоритмов и бизнес-логики",
                "Следуй принципам SOLID при разработке",
                "Избегай дублирования кода (DRY принцип)",
                "Используй константы вместо магических чисел"
            ],
            'security': [
                "Никогда не храни пароли и секретные ключи в коде",
                "Всегда валидируй пользовательский ввод",
                "Используй HTTPS для всех внешних запросов",
                "Логируй события безопасности",
                "Применяй принцип минимальных привилегий"
            ],
            'performance': [
                "Оптимизируй циклы и избегай излишней вложенности",
                "Используй кеширование для дорогостоящих операций",
                "Применяй ленивую загрузку где это возможно",
                "Минимизируй количество запросов к базе данных",
                "Профилируй код при подозрении на узкие места"
            ],
            'testing': [
                "Пиши unit-тесты для всех публичных методов",
                "Стремись к покрытию тестами не менее 80%",
                "Используй моки для внешних зависимостей",
                "Группируй тесты логически по модулям",
                "Тестируй граничные случаи и ошибки"
            ],
            'documentation': [
                "Пиши docstrings для всех публичных функций и классов",
                "Обновляй README.md при значимых изменениях",
                "Документируй API endpoints с примерами",
                "Веди changelog для релизов",
                "Добавляй инлайн-комментарии для неочевидного кода"
            ]
        }
        
        # Специфичные правила для языков программирования
        self.language_specific_rules = {
            'python': [
                "Следуй PEP 8 для стиля кода",
                "Используй type hints для всех функций",
                "Применяй list/dict comprehensions где уместно",
                "Обрабатывай исключения специфично, избегай голого except",
                "Используй f-strings для форматирования строк",
                "Применяй dataclasses для структур данных",
                "Используй pathlib вместо os.path для работы с путями"
            ],
            'javascript': [
                "Используй const/let вместо var",
                "Применяй строгий режим 'use strict'",
                "Используй async/await вместо промисов где возможно",
                "Применяй деструктуризацию объектов и массивов",
                "Используй модульную систему ES6",
                "Проверяй типы с помощью TypeScript или JSDoc"
            ],
            'typescript': [
                "Всегда указывай типы для параметров и возвращаемых значений",
                "Используй интерфейсы для описания структур данных",
                "Применяй generic типы для переиспользуемого кода",
                "Избегай any типа, используй unknown вместо него",
                "Используй enum для перечислений",
                "Применяй strict режим в tsconfig.json"
            ],
            'java': [
                "Следуй соглашениям по именованию Java",
                "Используй аннотации для метаданных",
                "Применяй Stream API для обработки коллекций",
                "Используй Optional для значений, которые могут быть null",
                "Следуй принципам объектно-ориентированного программирования",
                "Применяй паттерн Builder для сложных объектов"
            ],
            'rust': [
                "Используй Result<T, E> для обработки ошибок",
                "Применяй match для pattern matching",
                "Избегай паники (panic!) в библиотечном коде",
                "Используй References и Borrowing правильно",
                "Применяй трейты для полиморфизма",
                "Следуй принципам zero-cost abstractions"
            ]
        }
        
        # Правила для фреймворков
        self.framework_rules = {
            'react': [
                "Используй функциональные компоненты с хуками",
                "Применяй useCallback и useMemo для оптимизации",
                "Следуй принципу единственной ответственности для компонентов",
                "Используй prop-types или TypeScript для типизации",
                "Применяй условный рендеринг осознанно"
            ],
            'django': [
                "Используй Django ORM вместо сырого SQL",
                "Применяй миграции для изменения схемы БД",
                "Используй Django Forms для валидации",
                "Применяй middleware для кросс-функциональных задач",
                "Следуй MTV паттерну Django"
            ],
            'flask': [
                "Используй Blueprints для организации приложения",
                "Применяй декораторы для авторизации",
                "Используй Flask-SQLAlchemy для работы с БД",
                "Валидируй данные с помощью Marshmallow или WTForms",
                "Применяй application factory pattern"
            ]
        }
        
    def generate_improved_rules(self, config_data: Dict[str, Any], performance_data: Dict[str, Any]) -> str:
        """Генерация улучшенных правил на основе анализа"""
        
        self.logger.info("🔧 Генерация улучшенных правил .clinerules")
        
        selected_rules = []
        
        # Добавление базовых правил
        selected_rules.extend(self._select_base_rules(config_data, performance_data))
        
        # Добавление специфичных правил для языков
        selected_rules.extend(self._select_language_rules(config_data))
        
        # Добавление правил для фреймворков
        selected_rules.extend(self._select_framework_rules(config_data))
        
        # Добавление адаптивных правил на основе производительности
        selected_rules.extend(self._generate_adaptive_rules(performance_data))
        
        # Добавление пользовательских правил из существующей конфигурации
        selected_rules.extend(self._preserve_custom_rules(config_data))
        
        # Удаление дублирующихся правил
        selected_rules = self._remove_duplicates(selected_rules)
        
        # Сортировка правил по приоритету
        selected_rules = self._prioritize_rules(selected_rules, config_data)
        
        # Формирование итогового файла .clinerules
        rules_content = self._format_rules_file(selected_rules, config_data)
        
        self.logger.info(f"✅ Сгенерировано {len(selected_rules)} правил")
        
        return rules_content
        
    def _select_base_rules(self, config_data: Dict[str, Any], performance_data: Dict[str, Any]) -> List[str]:
        """Выбор базовых правил"""
        selected = []
        
        # Всегда добавляем основные правила
        selected.extend(self.base_rules['general'][:3])
        
        # Добавляем правила безопасности для веб-проектов
        if self._is_web_project(config_data):
            selected.extend(self.base_rules['security'][:3])
            
        # Добавляем правила производительности при наличии проблем
        performance_issues = performance_data.get('performance_issues', [])
        if performance_issues:
            selected.extend(self.base_rules['performance'][:2])
            
        # Добавляем правила тестирования если есть тестовые файлы
        if self._has_tests(config_data):
            selected.extend(self.base_rules['testing'][:3])
        else:
            selected.append("Создавай тесты для критически важного функционала")
            
        # Добавляем правила документации
        selected.extend(self.base_rules['documentation'][:2])
        
        return selected
        
    def _select_language_rules(self, config_data: Dict[str, Any]) -> List[str]:
        """Выбор правил для конкретных языков программирования"""
        selected = []
        
        languages = config_data.get('project_structure', {}).get('languages', [])
        
        for language in languages:
            if language in self.language_specific_rules:
                # Добавляем первые 4-5 правил для каждого языка
                lang_rules = self.language_specific_rules[language][:5]
                selected.extend(lang_rules)
                
        return selected
        
    def _select_framework_rules(self, config_data: Dict[str, Any]) -> List[str]:
        """Выбор правил для фреймворков"""
        selected = []
        
        frameworks = config_data.get('project_structure', {}).get('frameworks', [])
        
        # Определение фреймворков на основе структуры проекта
        detected_frameworks = self._detect_specific_frameworks(config_data)
        frameworks.extend(detected_frameworks)
        
        for framework in frameworks:
            if framework in self.framework_rules:
                framework_rules = self.framework_rules[framework][:3]
                selected.extend(framework_rules)
                
        return selected
        
    def _generate_adaptive_rules(self, performance_data: Dict[str, Any]) -> List[str]:
        """Генерация адаптивных правил на основе данных производительности"""
        adaptive_rules = []
        
        # Анализ ошибок производительности
        perf_issues = performance_data.get('performance_issues', [])
        
        for issue in perf_issues:
            if issue['type'] == 'memory':
                adaptive_rules.extend([
                    "Освобождай неиспользуемые ресурсы и закрывай соединения",
                    "Используй генераторы вместо списков для больших данных",
                    "Мониторь использование памяти в критических частях кода"
                ])
            elif issue['type'] == 'cpu':
                adaptive_rules.extend([
                    "Оптимизируй алгоритмы с высокой вычислительной сложностью",
                    "Используй многопоточность для CPU-интенсивных задач",
                    "Кеширyй результаты дорогостоящих вычислений"
                ])
                
        # Правила на основе частых ошибок
        error_patterns = performance_data.get('error_patterns', [])
        if error_patterns:
            adaptive_rules.append("Обрабатывай исключения на уровне приложения, не игнорируй их")
            
        return adaptive_rules
        
    def _preserve_custom_rules(self, config_data: Dict[str, Any]) -> List[str]:
        """Сохранение пользовательских правил из существующей конфигурации"""
        custom_rules = []
        
        current_rules = config_data.get('current_rules', {})
        if current_rules.get('exists') and current_rules.get('content'):
            # Извлекаем пользовательские правила (те, которые не совпадают с базовыми)
            existing_content = current_rules['content']
            
            for line in existing_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and self._is_custom_rule(line):
                    custom_rules.append(line)
                    
        return custom_rules
        
    def _remove_duplicates(self, rules: List[str]) -> List[str]:
        """Удаление дублирующихся правил"""
        seen = set()
        unique_rules = []
        
        for rule in rules:
            rule_lower = rule.lower().strip()
            if rule_lower not in seen:
                seen.add(rule_lower)
                unique_rules.append(rule)
                
        return unique_rules
        
    def _prioritize_rules(self, rules: List[str], config_data: Dict[str, Any]) -> List[str]:
        """Сортировка правил по приоритету"""
        
        def rule_priority(rule: str) -> int:
            rule_lower = rule.lower()
            
            # Высокий приоритет - безопасность
            if any(keyword in rule_lower for keyword in ['security', 'пароль', 'ключ', 'auth']):
                return 1
                
            # Средний приоритет - качество кода
            if any(keyword in rule_lower for keyword in ['test', 'тест', 'качество']):
                return 2
                
            # Производительность
            if any(keyword in rule_lower for keyword in ['performance', 'производительность', 'оптимиз']):
                return 3
                
            # Стиль и документация
            if any(keyword in rule_lower for keyword in ['style', 'стиль', 'комментар', 'документ']):
                return 4
                
            # Остальное
            return 5
            
        return sorted(rules, key=rule_priority)
        
    def _format_rules_file(self, rules: List[str], config_data: Dict[str, Any]) -> str:
        """Форматирование итогового файла .clinerules"""
        
        lines = []
        
        # Заголовок
        lines.append("# Правила Cline для проекта")
        lines.append(f"# Автогенерированно: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Информация о проекте
        project_info = config_data.get('project_structure', {})
        if project_info.get('project_type') != 'unknown':
            lines.append(f"# Тип проекта: {project_info['project_type']}")
            
        if project_info.get('languages'):
            lines.append(f"# Языки: {', '.join(project_info['languages'])}")
            
        if project_info.get('frameworks'):
            lines.append(f"# Фреймворки: {', '.join(project_info['frameworks'])}")
            
        lines.append("")
        
        # Правила по категориям
        categories = {
            'Безопасность': [],
            'Качество кода': [],
            'Производительность': [],
            'Тестирование': [],
            'Документация': [],
            'Общие правила': []
        }
        
        # Категоризация правил
        for rule in rules:
            rule_lower = rule.lower()
            
            if any(keyword in rule_lower for keyword in ['security', 'безопас', 'пароль', 'ключ']):
                categories['Безопасность'].append(rule)
            elif any(keyword in rule_lower for keyword in ['test', 'тест']):
                categories['Тестирование'].append(rule)
            elif any(keyword in rule_lower for keyword in ['performance', 'производительность', 'оптимиз']):
                categories['Производительность'].append(rule)
            elif any(keyword in rule_lower for keyword in ['doc', 'документ', 'комментар']):
                categories['Документация'].append(rule)
            elif any(keyword in rule_lower for keyword in ['style', 'стиль', 'format', 'качество']):
                categories['Качество кода'].append(rule)
            else:
                categories['Общие правила'].append(rule)
                
        # Добавление правил по категориям
        for category_name, category_rules in categories.items():
            if category_rules:
                lines.append(f"## {category_name}")
                lines.append("")
                for rule in category_rules:
                    lines.append(f"- {rule}")
                lines.append("")
                
        return '\n'.join(lines)
        
    def _is_web_project(self, config_data: Dict[str, Any]) -> bool:
        """Проверка, является ли проект веб-проектом"""
        project_structure = config_data.get('project_structure', {})
        
        languages = project_structure.get('languages', [])
        frameworks = project_structure.get('frameworks', [])
        
        web_indicators = ['javascript', 'typescript', 'nodejs', 'react', 'vue', 'angular']
        
        return any(indicator in languages + frameworks for indicator in web_indicators)
        
    def _has_tests(self, config_data: Dict[str, Any]) -> bool:
        """Проверка наличия тестов в проекте"""
        project_structure = config_data.get('project_structure', {})
        file_counts = project_structure.get('file_counts', {})
        
        # Поиск тестовых файлов по расширениям и именам
        test_indicators = ['.test.', '.spec.', '_test.', 'test_', 'tests/']
        
        for file_pattern in file_counts.keys():
            if any(indicator in file_pattern for indicator in test_indicators):
                return True
                
        return False
        
    def _detect_specific_frameworks(self, config_data: Dict[str, Any]) -> List[str]:
        """Обнаружение конкретных фреймворков"""
        detected = []
        
        # Можно расширить логику обнаружения фреймворков
        # на основе содержимого файлов конфигурации
        
        return detected
        
    def _is_custom_rule(self, rule: str) -> bool:
        """Проверка, является ли правило пользовательским"""
        # Проверяем, что правило не совпадает с базовыми
        all_base_rules = []
        
        for category_rules in self.base_rules.values():
            all_base_rules.extend(category_rules)
            
        for lang_rules in self.language_specific_rules.values():
            all_base_rules.extend(lang_rules)
            
        for framework_rules in self.framework_rules.values():
            all_base_rules.extend(framework_rules)
            
        rule_lower = rule.lower().strip()
        
        for base_rule in all_base_rules:
            if rule_lower == base_rule.lower().strip():
                return False
                
        return True
