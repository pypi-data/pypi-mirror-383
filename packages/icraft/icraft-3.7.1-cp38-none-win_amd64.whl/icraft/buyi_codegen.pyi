"""
icraft buyi codegen python interface
"""
from __future__ import annotations
import xir
__all__ = ['CodeGenOptions', 'MakeNetworkCodeGen']
class CodeGenOptions:
    def __init__(self, arg0: str, arg1: str) -> None:
        """
        				构造函数.
        
        				:param	str:			网络名
        				:param	log_path:		log路径
        """
    @property
    def cols(self) -> int:
        """
        MPE的列数.
        """
    @cols.setter
    def cols(self, arg0: int) -> None:
        ...
    @property
    def ddr_base(self) -> int:
        """
        地址的初始值.
        """
    @ddr_base.setter
    def ddr_base(self, arg0: int) -> None:
        ...
    @property
    def log_path(self) -> ...:
        """
        log路径.
        """
    @log_path.setter
    def log_path(self, arg0: ...) -> None:
        ...
    @property
    def net_log(self) -> ...:
        """
        log文件.
        """
    @net_log.setter
    def net_log(self, arg0: ...) -> None:
        ...
    @property
    def qbits(self) -> int:
        """
        硬算子的位数.
        """
    @qbits.setter
    def qbits(self, arg0: int) -> None:
        ...
    @property
    def rows(self) -> int:
        """
        MPE的行数.
        """
    @rows.setter
    def rows(self, arg0: int) -> None:
        ...
    @property
    def version(self) -> bool:
        """
        是否显示版本.
        """
    @version.setter
    def version(self, arg0: bool) -> None:
        ...
def MakeNetworkCodeGen(network: xir.Network, options: CodeGenOptions) -> None:
    """
    			为网络模型生成指令.
    
    			:param	network:	    网络
    			:param	options:	    配置信息
    """
