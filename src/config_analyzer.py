"""
Анализатор конфигурации Cline
Анализирует текущие настройки и выявляет области для улучшения
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import time

class ConfigAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_current_setup(self, cline_config_path: Path, workspace_path: Path) -> Dict[str, Any]:
        """Анализ текущей настройки Cline"""
        config_data = {
            'timestamp': time.time(),
            'workspace_path': str(workspace_path),
            'cline_config_path': str(cline_config_path),
            'current_rules': self._analyze_clinerules(workspace_path),
            'current_workflows': self._analyze_workflows(workspace_path),
            'vscode_settings': self._analyze_vscode_settings(cline_config_path.parent.parent),
            'project_structure': self._analyze_project_structure(workspace_path),
            'usage_patterns': self._analyze_usage_patterns(cline_config_path),
            'performance_issues': self._identify_performance_issues(),
            'optimization_opportunities': []
        }
        
        # Выявление возможностей для оптимизации
        config_data['optimization_opportunities'] = self._identify_optimization_opportunities(config_data)
        
        self.logger.info(f"📊 Анализ конфигурации завершен. Найдено {len(config_data['optimization_opportunities'])} возможностей для улучшения")
        
        return config_data
        
    def _analyze_clinerules(self, workspace_path: Path) -> Dict[str, Any]:
        """Анализ файла .clinerules"""
        clinerules_path = workspace_path / ".clinerules"
        
        if not clinerules_path.exists():
            return {
                'exists': False,
                'content': '',
                'rules_count': 0,
                'categories': [],
                'issues': ['Файл .clinerules отсутствует']
            }
            
        try:
            content = clinerules_path.read_text(encoding='utf-8')
            rules = self._parse_rules(content)
            
            return {
                'exists': True,
                'content': content,
                'rules_count': len(rules),
                'categories': self._categorize_rules(rules),
                'issues': self._identify_rules_issues(rules),
                'last_modified': clinerules_path.stat().st_mtime
            }
        except Exception as e:
            return {
                'exists': True,
                'content': '',
                'error': str(e),
                'issues': [f'Ошибка чтения файла: {e}']
            }
            
    def _analyze_workflows(self, workspace_path: Path) -> Dict[str, Any]:
        """Анализ workflow файлов"""
        workflows_dir = workspace_path / ".cline" / "workflows"
        
        if not workflows_dir.exists():
            return {
                'exists': False,
                'workflows': {},
                'count': 0,
                'issues': ['Директория workflows отсутствует']
            }
            
        workflows = {}
        issues = []
        
        for workflow_file in workflows_dir.glob("*.md"):
            try:
                content = workflow_file.read_text(encoding='utf-8')
                workflows[workflow_file.stem] = {
                    'content': content,
                    'size': len(content),
                    'steps': self._count_workflow_steps(content),
                    'last_modified': workflow_file.stat().st_mtime
                }
            except Exception as e:
                issues.append(f"Ошибка чтения {workflow_file.name}: {e}")
                
        return {
            'exists': True,
            'workflows': workflows,
            'count': len(workflows),
            'issues': issues
        }
        
    def _analyze_vscode_settings(self, vscode_path: Path) -> Dict[str, Any]:
        """Анализ настроек VS Code для Cline"""
        settings_path = vscode_path / "settings.json"
        
        if not settings_path.exists():
            return {
                'exists': False,
                'cline_settings': {},
                'issues': ['Файл settings.json отсутствует']
            }
            
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # Извлечение настроек Cline
            cline_settings = {k: v for k, v in settings.items() if k.startswith('cline.')}
            
            return {
                'exists': True,
                'cline_settings': cline_settings,
                'total_settings': len(settings),
                'issues': self._identify_settings_issues(cline_settings)
            }
        except Exception as e:
            return {
                'exists': True,
                'error': str(e),
                'issues': [f'Ошибка чтения настроек: {e}']
            }
            
    def _analyze_project_structure(self, workspace_path: Path) -> Dict[str, Any]:
        """Анализ структуры проекта"""
        structure = {
            'languages': set(),
            'frameworks': set(),
            'file_counts': {},
            'total_files': 0,
            'project_type': 'unknown'
        }
        
        # Подсчет файлов по расширениям
        for file_path in workspace_path.rglob('*'):
            if file_path.is_file() and not self._is_ignored_path(file_path):
                structure['total_files'] += 1
                ext = file_path.suffix.lower()
                structure['file_counts'][ext] = structure['file_counts'].get(ext, 0) + 1
                
                # Определение языков программирования
                if ext in ['.py']:
                    structure['languages'].add('python')
                elif ext in ['.js', '.jsx']:
                    structure['languages'].add('javascript')
                elif ext in ['.ts', '.tsx']:
                    structure['languages'].add('typescript')
                elif ext in ['.java']:
                    structure['languages'].add('java')
                elif ext in ['.cpp', '.c', '.h']:
                    structure['languages'].add('cpp')
                elif ext in ['.rs']:
                    structure['languages'].add('rust')
                elif ext in ['.go']:
                    structure['languages'].add('go')
                    
        # Определение фреймворков и типа проекта
        structure['frameworks'] = self._detect_frameworks(workspace_path)
        structure['project_type'] = self._determine_project_type(structure)
        
        # Конвертация set в list для JSON сериализации
        structure['languages'] = list(structure['languages'])
        structure['frameworks'] = list(structure['frameworks'])
        
        return structure
        
    def _analyze_usage_patterns(self, cline_config_path: Path) -> Dict[str, Any]:
        """Анализ паттернов использования Cline"""
        # Попытка найти файлы с историей использования
        usage_data = {
            'sessions_count': 0,
            'average_session_length': 0,
            'most_used_commands': [],
            'error_patterns': [],
            'common_tasks': []
        }
        
        # Поиск логов и истории
        try:
            # Поиск в директории конфигурации Cline
            if cline_config_path.exists():
                for log_file in cline_config_path.rglob('*.log'):
                    if log_file.is_file():
                        usage_data = self._parse_usage_logs(log_file, usage_data)
        except Exception as e:
            self.logger.warning(f"Не удалось проанализировать паттерны использования: {e}")
            
        return usage_data
        
    def _identify_performance_issues(self) -> List[Dict[str, Any]]:
        """Выявление проблем с производительностью"""
        issues = []
        
        # Проверка системных ресурсов
        try:
            import psutil
            
            # Проверка использования памяти
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                issues.append({
                    'type': 'memory',
                    'severity': 'high',
                    'description': f'Высокое использование памяти: {memory.percent}%',
                    'recommendation': 'Рассмотрите оптимизацию настроек для экономии памяти'
                })
                
            # Проверка использования CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 70:
                issues.append({
                    'type': 'cpu',
                    'severity': 'medium',
                    'description': f'Высокая нагрузка на CPU: {cpu_percent}%',
                    'recommendation': 'Рассмотрите настройки для снижения нагрузки на процессор'
                })
                
        except ImportError:
            issues.append({
                'type': 'monitoring',
                'severity': 'low',
                'description': 'Модуль psutil недоступен для мониторинга производительности',
                'recommendation': 'pip install psutil для улучшенного мониторинга'
            })
            
        return issues
        
    def _identify_optimization_opportunities(self, config_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Выявление возможностей для оптимизации"""
        opportunities = []
        
        # Анализ правил
        if not config_data['current_rules']['exists']:
            opportunities.append({
                'type': 'rules',
                'priority': 'high',
                'description': 'Создать базовый набор правил .clinerules',
                'benefit': 'Улучшение качества кода и соблюдение стандартов'
            })
        elif config_data['current_rules']['rules_count'] < 10:
            opportunities.append({
                'type': 'rules',
                'priority': 'medium',
                'description': 'Расширить набор правил в .clinerules',
                'benefit': 'Более детальный контроль качества кода'
            })
            
        # Анализ workflow
        if not config_data['current_workflows']['exists']:
            opportunities.append({
                'type': 'workflows',
                'priority': 'high',
                'description': 'Создать базовые workflow для проекта',
                'benefit': 'Автоматизация рутинных задач разработки'
            })
            
        # Анализ настроек
        if len(config_data['vscode_settings']['cline_settings']) < 5:
            opportunities.append({
                'type': 'settings',
                'priority': 'medium',
                'description': 'Добавить дополнительные настройки Cline',
                'benefit': 'Более тонкая настройка поведения Cline'
            })
            
        # Анализ структуры проекта
        project_type = config_data['project_structure']['project_type']
        if project_type != 'unknown':
            opportunities.append({
                'type': 'project_specific',
                'priority': 'high',
                'description': f'Оптимизация для {project_type} проекта',
                'benefit': 'Специализированные правила и workflow для типа проекта'
            })
            
        return opportunities
        
    def _parse_rules(self, content: str) -> List[str]:
        """Парсинг правил из содержимого файла"""
        rules = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                rules.append(line)
        return rules
        
    def _categorize_rules(self, rules: List[str]) -> List[str]:
        """Категоризация правил"""
        categories = set()
        
        for rule in rules:
            rule_lower = rule.lower()
            if any(keyword in rule_lower for keyword in ['test', 'spec', 'unit']):
                categories.add('testing')
            elif any(keyword in rule_lower for keyword in ['security', 'auth', 'password']):
                categories.add('security')
            elif any(keyword in rule_lower for keyword in ['performance', 'optimize', 'cache']):
                categories.add('performance')
            elif any(keyword in rule_lower for keyword in ['format', 'style', 'lint']):
                categories.add('formatting')
            else:
                categories.add('general')
                
        return list(categories)
        
    def _identify_rules_issues(self, rules: List[str]) -> List[str]:
        """Выявление проблем в правилах"""
        issues = []
        
        if len(rules) == 0:
            issues.append("Файл правил пуст")
        elif len(rules) < 5:
            issues.append("Слишком мало правил для эффективной работы")
            
        # Проверка дублирования
        if len(rules) != len(set(rules)):
            issues.append("Обнаружены дублирующиеся правила")
            
        return issues
        
    def _count_workflow_steps(self, content: str) -> int:
        """Подсчет шагов в workflow"""
        steps = 0
        for line in content.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                steps += 1
        return steps
        
    def _identify_settings_issues(self, cline_settings: Dict[str, Any]) -> List[str]:
        """Выявление проблем в настройках"""
        issues = []
        
        if not cline_settings:
            issues.append("Настройки Cline отсутствуют")
            
        return issues
        
    def _is_ignored_path(self, path: Path) -> bool:
        """Проверка, нужно ли игнорировать путь"""
        ignored_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', 'build', 'dist'}
        return any(part.startswith('.') or part in ignored_dirs for part in path.parts)
        
    def _detect_frameworks(self, workspace_path: Path) -> set:
        """Определение используемых фреймворков"""
        frameworks = set()
        
        # Проверка файлов конфигурации
        if (workspace_path / "package.json").exists():
            frameworks.add("nodejs")
            
        if (workspace_path / "requirements.txt").exists() or (workspace_path / "pyproject.toml").exists():
            frameworks.add("python")
            
        if (workspace_path / "Cargo.toml").exists():
            frameworks.add("rust")
            
        if (workspace_path / "go.mod").exists():
            frameworks.add("go")
            
        return frameworks
        
    def _determine_project_type(self, structure: Dict[str, Any]) -> str:
        """Определение типа проекта"""
        languages = structure['languages']
        frameworks = structure['frameworks']
        
        if 'python' in languages:
            return 'python'
        elif 'javascript' in languages or 'typescript' in languages:
            return 'web'
        elif 'java' in languages:
            return 'java'
        elif 'rust' in languages:
            return 'rust'
        elif 'go' in languages:
            return 'go'
        elif 'cpp' in languages:
            return 'cpp'
        else:
            return 'unknown'
            
    def _parse_usage_logs(self, log_file: Path, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг логов использования"""
        try:
            content = log_file.read_text(encoding='utf-8')
            # Простой анализ логов (можно расширить)
            lines = content.split('\n')
            usage_data['sessions_count'] += content.count('session start')
            
        except Exception as e:
            self.logger.warning(f"Ошибка парсинга лога {log_file}: {e}")
            
        return usage_data
