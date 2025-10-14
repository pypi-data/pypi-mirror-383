"""
GoSound - 音效播放库
版权所有者：王子毅
"""

from .core import (
    TurtleSound,
    get_sound_manager,
    play,
    load_sound,
    add_sound_config,
     get_sound_manager,
    
)

# 导出到模块级别的公共API
__all__ = [
    'TurtleSound',
    'get_sound_manager', 
    'play',
    'load_sound',
    'add_sound_config'
]

__version__ = "0.1.2"
__author__ = "王子毅"