import platform
import sys


class SystemInfo:
    @staticmethod
    def check_python_version():
        return {
            "version": platform.python_version(),
            "full_version": sys.version,
            "is_python3": sys.version_info.major >= 3
        }

    @staticmethod
    def check_os_info():
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "processor": platform.processor()
        }