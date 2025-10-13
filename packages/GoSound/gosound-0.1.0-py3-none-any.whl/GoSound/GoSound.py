"""版权所有者：王子毅"""
import os
import platform
import threading
from typing import Dict, Any, Optional

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

class TurtleSound:
    """
    Turtle音效管理器
    支持多种音效播放方式，自动选择最佳可用方案
    """
    
    def __init__(self, enable_sound: bool = True):
        """
        初始化音效管理器
        
        Args:
            enable_sound: 是否启用音效
        """
        self.enable_sound = enable_sound
        self.system = platform.system()
        self.sound_method = None
        self.sounds: Dict[str, Any] = {}
        self.sound_configs: Dict[str, Dict] = {}
        
        # 检测可用的音效方案
        self._detect_sound_method()
        self._setup_default_sounds()
        
    
    def _detect_sound_method(self):
        """检测可用的音效播放方法"""
        if not self.enable_sound:
            self.sound_method = "none"
            return
            
        # 优先使用pygame
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.sound_method = "pygame"
                return
            except:
                pass
        
        # Windows系统使用winsound
        if self.system == "Windows" and WINSOUND_AVAILABLE:
            self.sound_method = "winsound"
            return
        
        # 最后尝试系统命令
        self.sound_method = "system"
    
    def _setup_default_sounds(self):
        """设置默认音效配置"""
        self.sound_configs = {
            # 游戏事件音效
            "click": {"type": "beep", "frequency": 800, "duration": 50, "volume": 0.3},
            "move": {"type": "beep", "frequency": 600, "duration": 30, "volume": 0.2},
            "select": {"type": "beep", "frequency": 1000, "duration": 80, "volume": 0.4},
            
            # 游戏动作音效
            "jump": {"type": "beep", "frequency": 700, "duration": 100, "volume": 0.5},
            "shoot": {"type": "beep", "frequency": 1200, "duration": 60, "volume": 0.6},
            "explosion": {"type": "beep", "frequency": 200, "duration": 300, "volume": 0.8},
            "coin": {"type": "beep", "frequency": 1500, "duration": 150, "volume": 0.5},
            "powerup": {"type": "beep", "frequency": 2000, "duration": 200, "volume": 0.6},
            
            # 游戏状态音效
            "game_start": {"type": "beep", "frequency": 1000, "duration": 200, "volume": 0.7},
            "game_over": {"type": "beep", "frequency": 300, "duration": 500, "volume": 0.8},
            "victory": {"type": "beep", "frequency": 1500, "duration": 1000, "volume": 0.7},
            "level_up": {"type": "beep", "frequency": 1200, "duration": 300, "volume": 0.6},
            
            # 界面音效
            "error": {"type": "beep", "frequency": 400, "duration": 200, "volume": 0.5},
            "notification": {"type": "beep", "frequency": 900, "duration": 100, "volume": 0.4}
        }
    
    def load_sound_file(self, sound_name: str, file_path: str):
        """
        加载音效文件（仅pygame模式支持）
        
        Args:
            sound_name: 音效名称
            file_path: 音效文件路径
        """
        if not self.enable_sound or self.sound_method != "pygame":
            return False
            
        try:
            if os.path.exists(file_path):
                self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                return True
            else:
                print(f"音效文件不存在: {file_path}")
                return False
        except Exception as e:
            print(f"加载音效文件失败 {file_path}: {e}")
            return False
    
    def add_sound(self, sound_name: str, config: Dict):
        """
        添加或修改音效配置
        
        Args:
            sound_name: 音效名称
            config: 音效配置字典
        """
        self.sound_configs[sound_name] = config
    
    def play(self, sound_name: str, volume: Optional[float] = None):
        """
        播放指定音效
        
        Args:
            sound_name: 音效名称
            volume: 音量(0.0-1.0)，None使用配置中的音量
        """
        if not self.enable_sound:
            return
            
        if sound_name not in self.sound_configs:
            print(f"未知音效: {sound_name}")
            return
        
        config = self.sound_configs[sound_name]
        
        # 使用指定音量或配置音量
        play_volume = volume if volume is not None else config.get('volume', 0.5)
        
        # 在新线程中播放音效，避免阻塞游戏
        thread = threading.Thread(
            target=self._play_sound_thread,
            args=(sound_name, config, play_volume),
            daemon=True
        )
        thread.start()
    
    def _play_sound_thread(self, sound_name: str, config: Dict, volume: float):
        """在新线程中播放音效"""
        try:
            if self.sound_method == "pygame":
                self._play_pygame(sound_name, config, volume)
            elif self.sound_method == "winsound":
                self._play_winsound(config, volume)
            elif self.sound_method == "system":
                self._play_system(config)
        except Exception as e:
            print(f"播放音效失败 {sound_name}: {e}")
    
    def _play_pygame(self, sound_name: str, config: Dict, volume: float):
        """使用pygame播放音效"""
        if sound_name in self.sounds:
            # 播放加载的音效文件
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
        else:
            # 生成并播放蜂鸣音效
            self._play_winsound(config, volume)
    
    def _play_winsound(self, config: Dict, volume: float):
        """使用winsound播放蜂鸣音效（仅Windows）"""
        if self.system == "Windows" and WINSOUND_AVAILABLE:
            frequency = config.get('frequency', 440)
            duration = config.get('duration', 100)
            # winsound不支持音量控制，但可以通过持续时间模拟
            adjusted_duration = int(duration * volume)
            winsound.Beep(frequency, adjusted_duration)
    
    def _play_system(self, config: Dict):
        """使用系统命令播放音效"""
        frequency = config.get('frequency', 440)
        duration = config.get('duration', 100) / 1000.0  # 转换为秒
        
        if self.system == "Darwin":  # macOS
            # 使用say命令模拟音效
            os.system(f"say -v Bells ' ' &")
        elif self.system == "Linux":
            # 使用beep命令或系统蜂鸣器
            os.system(f"beep -f {frequency} -l {duration*1000} 2>/dev/null || echo -e '\\a'")
        else:
            # 其他系统使用打印字符
            print(f"\a", end='', flush=True)
    
    def stop_all(self):
        """停止所有音效（仅pygame模式支持）"""
        if self.sound_method == "pygame":
            pygame.mixer.stop()
    
    def set_enabled(self, enabled: bool):
        """启用或禁用音效"""
        self.enable_sound = enabled
    
    def get_status(self) -> Dict[str, Any]:
        """获取音效系统状态"""
        return {
            "enabled": self.enable_sound,
            "system": self.system,
            "method": self.sound_method,
            "pygame_available": PYGAME_AVAILABLE,
            "sounds_loaded": len(self.sounds),
            "sound_configs": len(self.sound_configs)
        }


# 预配置的音效管理器实例
_sound_manager = None

def get_sound_manager(enable_sound: bool = True) -> TurtleSound:
    """
    获取全局音效管理器实例
    
    Args:
        enable_sound: 是否启用音效
        
    Returns:
        TurtleSound实例
    """
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = TurtleSound(enable_sound)
    return _sound_manager

def play(sound_name: str, volume: Optional[float] = None):
    """
    快速播放音效（使用全局管理器）
    
    Args:
        sound_name: 音效名称
        volume: 音量
    """
    manager = get_sound_manager()
    manager.play(sound_name, volume)

def load_sound(sound_name: str, file_path: str) -> bool:
    """
    快速加载音效文件（使用全局管理器）
    
    Args:
        sound_name: 音效名称
        file_path: 文件路径
        
    Returns:
        是否加载成功
    """
    manager = get_sound_manager()
    return manager.load_sound_file(sound_name, file_path)

def add_sound_config(sound_name: str, config: Dict):
    """
    快速添加音效配置（使用全局管理器）
    
    Args:
        sound_name: 音效名称
        config: 音效配置
    """
    manager = get_sound_manager()
    manager.add_sound(sound_name, config)
