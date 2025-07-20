"""
Трекер производительности для анализа метрик системы и Cline
Собирает данные о производительности для оптимизации настроек
"""

import json
import psutil
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

class PerformanceTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
    def collect_metrics(self) -> Dict[str, Any]:
        """Сбор метрик производительности"""
        
        self.logger.info("📈 Сбор метрик производительности")
        
        metrics = {
            'timestamp': time.time(),
            'system_metrics': self._collect_system_metrics(),
            'process_metrics': self._collect_process_metrics(),
            'disk_metrics': self._collect_disk_metrics(),
            'memory_patterns': self._analyze_memory_patterns(),
            'performance_issues': self._identify_performance_issues(),
            'historical_data': self._load_historical_data(),
            'session_info': self._get_session_info()
        }
        
        # Анализ тенденций
        metrics['trends'] = self._analyze_trends(metrics)
        
        self.logger.info("✅ Метрики производительности собраны")
        
        return metrics
        
    def save_session_data(self, performance_data: Dict[str, Any]) -> None:
        """Сохранение данных сессии"""
        
        session_file = self.data_dir / f"session_{int(time.time())}.json"
        
        # Подготовка данных для сохранения
        session_data = {
            'timestamp': performance_data['timestamp'],
            'system_metrics': performance_data['system_metrics'],
            'process_metrics': performance_data['process_metrics'],
            'performance_issues': performance_data['performance_issues'],
            'session_info': performance_data['session_info']
        }
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"💾 Данные сессии сохранены: {session_file}")
            
            # Очистка старых данных (старше 30 дней)
            self._cleanup_old_data()
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения данных сессии: {e}")
            
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Сбор системных метрик"""
        try:
            # Метрики CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Метрики памяти
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Метрики диска
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Сетевые метрики
            network_io = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': {
                        'current': cpu_freq.current if cpu_freq else None,
                        'min': cpu_freq.min if cpu_freq else None,
                        'max': cpu_freq.max if cpu_freq else None
                    }
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': (disk_usage.used / disk_usage.total) * 100
                },
                'disk_io': {
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0,
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                }
            }
            
        except Exception as e:
            self.logger.warning(f"Ошибка сбора системных метрик: {e}")
            return {}
            
    def _collect_process_metrics(self) -> Dict[str, Any]:
        """Сбор метрик процессов"""
        try:
            current_process = psutil.Process()
            
            # Метрики текущего процесса
            process_info = {
                'pid': current_process.pid,
                'name': current_process.name(),
                'cpu_percent': current_process.cpu_percent(),
                'memory_info': current_process.memory_info()._asdict(),
                'memory_percent': current_process.memory_percent(),
                'num_threads': current_process.num_threads(),
                'create_time': current_process.create_time()
            }
            
            # Поиск процессов VS Code
            vscode_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'code' in proc.info['name'].lower():
                        vscode_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return {
                'current_process': process_info,
                'vscode_processes': vscode_processes,
                'total_processes': len(list(psutil.process_iter())),
                'system_load': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
        except Exception as e:
            self.logger.warning(f"Ошибка сбора метрик процессов: {e}")
            return {}
            
    def _collect_disk_metrics(self) -> Dict[str, Any]:
        """Сбор метрик дискового пространства"""
        try:
            # Анализ рабочей директории
            workspace_path = Path.cwd()
            workspace_size = self._get_directory_size(workspace_path)
            
            # Анализ временных файлов
            temp_dirs = [Path.home() / 'AppData/Local/Temp', Path('/tmp')]
            temp_usage = 0
            
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    temp_usage += self._get_directory_size(temp_dir)
                    
            return {
                'workspace_size': workspace_size,
                'temp_usage': temp_usage,
                'large_files': self._find_large_files(workspace_path),
                'cache_usage': self._estimate_cache_usage()
            }
            
        except Exception as e:
            self.logger.warning(f"Ошибка сбора метрик диска: {e}")
            return {}
            
    def _analyze_memory_patterns(self) -> Dict[str, Any]:
        """Анализ паттернов использования памяти"""
        try:
            memory_samples = []
            
            # Собираем несколько образцов с интервалом
            for _ in range(5):
                memory = psutil.virtual_memory()
                memory_samples.append({
                    'timestamp': time.time(),
                    'percent': memory.percent,
                    'available': memory.available,
                    'used': memory.used
                })
                time.sleep(0.5)
                
            # Анализ тенденций
            if len(memory_samples) > 1:
                start_usage = memory_samples[0]['percent']
                end_usage = memory_samples[-1]['percent']
                trend = 'increasing' if end_usage > start_usage else 'decreasing'
            else:
                trend = 'stable'
                
            avg_usage = sum(sample['percent'] for sample in memory_samples) / len(memory_samples)
            
            return {
                'samples': memory_samples,
                'trend': trend,
                'average_usage': avg_usage,
                'peak_usage': max(sample['percent'] for sample in memory_samples),
                'min_usage': min(sample['percent'] for sample in memory_samples)
            }
            
        except Exception as e:
            self.logger.warning(f"Ошибка анализа памяти: {e}")
            return {}
            
    def _identify_performance_issues(self) -> List[Dict[str, Any]]:
        """Выявление проблем производительности"""
        issues = []
        
        try:
            # Проверка использования CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                issues.append({
                    'type': 'cpu',
                    'severity': 'high' if cpu_percent > 90 else 'medium',
                    'value': cpu_percent,
                    'description': f'Высокая загрузка CPU: {cpu_percent:.1f}%',
                    'recommendation': 'Рассмотрите оптимизацию алгоритмов и распараллеливание задач'
                })
                
            # Проверка использования памяти
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                issues.append({
                    'type': 'memory',
                    'severity': 'high' if memory.percent > 90 else 'medium',
                    'value': memory.percent,
                    'description': f'Высокое использование памяти: {memory.percent:.1f}%',
                    'recommendation': 'Освободите неиспользуемые ресурсы и оптимизируйте структуры данных'
                })
                
            # Проверка дискового пространства
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 85:
                issues.append({
                    'type': 'disk',
                    'severity': 'high' if disk_percent > 95 else 'medium',
                    'value': disk_percent,
                    'description': f'Низкое свободное место на диске: {disk_percent:.1f}% занято',
                    'recommendation': 'Очистите временные файлы и кеши'
                })
                
            # Проверка swap использования
            swap = psutil.swap_memory()
            if swap.percent > 50:
                issues.append({
                    'type': 'swap',
                    'severity': 'medium',
                    'value': swap.percent,
                    'description': f'Активное использование swap: {swap.percent:.1f}%',
                    'recommendation': 'Рассмотрите увеличение объема RAM'
                })
                
        except Exception as e:
            self.logger.warning(f"Ошибка выявления проблем производительности: {e}")
            
        return issues
        
    def _load_historical_data(self) -> List[Dict[str, Any]]:
        """Загрузка исторических данных"""
        historical_data = []
        
        try:
            # Загрузка данных за последние 7 дней
            cutoff_time = time.time() - (7 * 24 * 3600)
            
            for session_file in self.data_dir.glob('session_*.json'):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    if data.get('timestamp', 0) > cutoff_time:
                        historical_data.append(data)
                        
                except Exception as e:
                    self.logger.warning(f"Ошибка загрузки файла {session_file}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"Ошибка загрузки исторических данных: {e}")
            
        return historical_data
        
    def _get_session_info(self) -> Dict[str, Any]:
        """Получение информации о сессии"""
        return {
            'start_time': time.time(),
            'working_directory': str(Path.cwd()),
            'python_version': f"{psutil.version_info}",
            'platform': psutil.LINUX or psutil.WINDOWS or psutil.MACOS,
            'boot_time': psutil.boot_time()
        }
        
    def _analyze_trends(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ трендов на основе исторических данных"""
        trends = {}
        
        try:
            historical_data = metrics.get('historical_data', [])
            
            if len(historical_data) < 2:
                return trends
                
            # Анализ тренда использования CPU
            cpu_values = [data['system_metrics']['cpu']['percent'] 
                         for data in historical_data 
                         if 'system_metrics' in data and 'cpu' in data['system_metrics']]
                         
            if len(cpu_values) > 1:
                trends['cpu_trend'] = 'increasing' if cpu_values[-1] > cpu_values[0] else 'decreasing'
                trends['avg_cpu'] = sum(cpu_values) / len(cpu_values)
                
            # Анализ тренда использования памяти
            memory_values = [data['system_metrics']['memory']['percent'] 
                           for data in historical_data 
                           if 'system_metrics' in data and 'memory' in data['system_metrics']]
                           
            if len(memory_values) > 1:
                trends['memory_trend'] = 'increasing' if memory_values[-1] > memory_values[0] else 'decreasing'
                trends['avg_memory'] = sum(memory_values) / len(memory_values)
                
        except Exception as e:
            self.logger.warning(f"Ошибка анализа трендов: {e}")
            
        return trends
        
    def _get_directory_size(self, path: Path) -> int:
        """Вычисление размера директории"""
        try:
            total_size = 0
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0
            
    def _find_large_files(self, path: Path, size_limit: int = 100 * 1024 * 1024) -> List[Dict[str, Any]]:
        """Поиск больших файлов"""
        large_files = []
        
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    if size > size_limit:
                        large_files.append({
                            'path': str(file_path),
                            'size': size,
                            'size_mb': round(size / (1024 * 1024), 2)
                        })
                        
        except Exception as e:
            self.logger.warning(f"Ошибка поиска больших файлов: {e}")
            
        return large_files
        
    def _estimate_cache_usage(self) -> Dict[str, Any]:
        """Оценка использования кеша"""
        cache_info = {}
        
        try:
            # VS Code cache
            vscode_cache_paths = [
                Path.home() / 'AppData/Roaming/Code/User/workspaceStorage',
                Path.home() / '.config/Code/User/workspaceStorage',
                Path.home() / 'Library/Application Support/Code/User/workspaceStorage'
            ]
            
            total_cache = 0
            for cache_path in vscode_cache_paths:
                if cache_path.exists():
                    size = self._get_directory_size(cache_path)
                    total_cache += size
                    cache_info[str(cache_path)] = size
                    
            cache_info['total_vscode_cache'] = total_cache
            
        except Exception as e:
            self.logger.warning(f"Ошибка оценки кеша: {e}")
            
        return cache_info
        
    def _cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Очистка старых данных"""
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)
            
            for session_file in self.data_dir.glob('session_*.json'):
                try:
                    # Извлекаем timestamp из имени файла
                    timestamp = int(session_file.stem.split('_')[1])
                    
                    if timestamp < cutoff_time:
                        session_file.unlink()
                        self.logger.info(f"Удален старый файл данных: {session_file}")
                        
                except (ValueError, IndexError):
                    # Если не удается извлечь timestamp, проверяем время модификации
                    if session_file.stat().st_mtime < cutoff_time:
                        session_file.unlink()
                        self.logger.info(f"Удален старый файл данных: {session_file}")
                        
        except Exception as e:
            self.logger.warning(f"Ошибка очистки старых данных: {e}")
