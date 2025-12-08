from abc import ABC, abstractmethod
import datetime
from Src.settings_manager import settings_manager

class LoggerSubject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, level, message):
        timestamp = datetime.datetime.now().isoformat()
        full_message = f"[{timestamp}] [{level}] {message}"
        for observer in self._observers:
            observer.update(full_message)

class LogObserver(ABC):
    @abstractmethod
    def update(self, message):
        pass

class ConsoleObserver(LogObserver):
    def update(self, message):
        print(message)

class FileObserver(LogObserver):
    def __init__(self, filename):
        self.filename = filename
    
    def update(self, message):
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(message + '\n')

class log_service:
    __instance = None
    
    @staticmethod
    def get_instance():
        if log_service.__instance is None:
            log_service.__instance = log_service()
            log_service.__instance._configure()
        return log_service.__instance
    
    def __init__(self):
        self.logger = LoggerSubject()
        self.levels = {'DEBUG': 0, 'INFO': 1, 'ERROR': 2}
        self.min_level = 1  # default INFO

    def _configure(self):
        sm = settings_manager()
        sm.file_name = "settings.json"
        sm.load()
        self.min_level = self.levels.get(sm.settings.log_level, 1)
        log_output = sm.settings.log_output
        if log_output in ["console", "both"]:
            self.logger.attach(ConsoleObserver())
        if log_output in ["file", "both"]:
            self.logger.attach(FileObserver(sm.settings.log_file))

    def _should_log(self, level):
        return self.levels.get(level, 3) >= self.min_level

    def log(self, level, message):
        if self._should_log(level):
            self.logger.notify(level, message)

    def debug(self, message):
        self.log('DEBUG', message)

    def info(self, message):
        self.log('INFO', message)

    def error(self, message):
        self.log('ERROR', message)