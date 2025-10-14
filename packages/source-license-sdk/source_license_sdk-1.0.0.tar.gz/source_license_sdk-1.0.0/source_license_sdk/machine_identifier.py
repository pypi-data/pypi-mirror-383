"""Machine identifier generation for license activation"""

import hashlib
import socket
import platform
import subprocess
import os
import re
from typing import List, Optional

class MachineIdentifier:
    """Generates unique machine identifiers for license activation"""
    
    @classmethod
    def generate(cls) -> str:
        """Generate a unique machine identifier
        
        Returns:
            str: A unique 32-character machine identifier
        """
        components = []
        
        # Get hostname
        components.append(cls._get_hostname())
        
        # Get MAC addresses
        components.extend(cls._get_mac_addresses())
        
        # Get CPU info if available
        cpu_info = cls._get_cpu_info()
        if cpu_info:
            components.append(cpu_info)
        
        # Get motherboard info if available
        motherboard_info = cls._get_motherboard_info()
        if motherboard_info:
            components.append(motherboard_info)
        
        # Get disk serial if available
        disk_serial = cls._get_disk_serial()
        if disk_serial:
            components.append(disk_serial)
        
        # Create hash from all components
        raw_id = '|'.join(filter(None, components))
        return hashlib.sha256(raw_id.encode()).hexdigest()[:32]
    
    @classmethod
    def generate_fingerprint(cls) -> str:
        """Generate machine fingerprint (more detailed than machine ID)
        
        Returns:
            str: A detailed machine fingerprint hash
        """
        components = []
        
        # Basic system info
        components.append(cls._get_hostname())
        components.append(platform.python_version())
        components.append(platform.platform())
        
        # Network info
        components.extend(cls._get_mac_addresses())
        components.append(cls._get_local_ip())
        
        # Hardware info
        cpu_info = cls._get_cpu_info()
        if cpu_info:
            components.append(cpu_info)
        
        memory_info = cls._get_memory_info()
        if memory_info:
            components.append(memory_info)
        
        disk_info = cls._get_disk_info()
        if disk_info:
            components.append(disk_info)
        
        # Environment info
        components.append(cls._get_environment_hash())
        
        raw_fingerprint = '|'.join(filter(None, components))
        return hashlib.sha256(raw_fingerprint.encode()).hexdigest()
    
    @staticmethod
    def _get_hostname() -> str:
        """Get system hostname"""
        try:
            return socket.gethostname()
        except Exception:
            return 'unknown-host'
    
    @classmethod
    def _get_mac_addresses(cls) -> List[str]:
        """Get MAC addresses from network interfaces"""
        try:
            import uuid
            import psutil
            
            addresses = []
            
            # Try psutil first (more reliable)
            try:
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == psutil.AF_LINK and addr.address:
                            mac = addr.address.lower()
                            if cls._is_valid_mac_address(mac):
                                addresses.append(mac)
            except (ImportError, Exception):
                # Fallback to uuid.getnode()
                try:
                    mac = ':'.join(f'{(uuid.getnode() >> i) & 0xff:02x}' for i in range(0, 48, 8)[::-1])
                    if cls._is_valid_mac_address(mac):
                        addresses.append(mac)
                except Exception:
                    pass
            
            # Platform-specific fallback methods
            if not addresses:
                addresses = cls._get_mac_addresses_fallback()
            
            return list(set(addresses))  # Remove duplicates
        except Exception:
            return []
    
    @staticmethod
    def _is_valid_mac_address(mac: str) -> bool:
        """Check if MAC address is valid (not virtual/invalid)"""
        if not mac or len(mac) != 17:
            return False
        
        # Filter out common virtual/invalid addresses
        invalid_prefixes = ['00:00:00', '02:00:00']
        return not any(mac.startswith(prefix) for prefix in invalid_prefixes)
    
    @classmethod
    def _get_mac_addresses_fallback(cls) -> List[str]:
        """Platform-specific fallback methods for getting MAC addresses"""
        addresses = []
        system = platform.system().lower()
        
        try:
            if system == 'darwin':
                # macOS
                output = cls._run_command(['ifconfig'])
                addresses = re.findall(r'ether ([a-f0-9:]{17})', output, re.IGNORECASE)
            
            elif system == 'linux':
                # Linux
                output = cls._run_command(['ip', 'link', 'show']) or cls._run_command(['ifconfig'])
                addresses = re.findall(r'(?:ether|HWaddr)\s+([a-f0-9:]{17})', output, re.IGNORECASE)
            
            elif system == 'windows':
                # Windows
                output = cls._run_command(['getmac', '/fo', 'csv', '/nh'])
                matches = re.findall(r'"([A-F0-9-]{17})"', output, re.IGNORECASE)
                addresses = [addr.replace('-', ':').lower() for addr in matches]
        
        except Exception:
            pass
        
        return [addr for addr in addresses if cls._is_valid_mac_address(addr)]
    
    @classmethod
    def _get_cpu_info(cls) -> Optional[str]:
        """Get CPU information"""
        system = platform.system().lower()
        
        try:
            if system == 'darwin':
                return cls._run_command(['sysctl', '-n', 'machdep.cpu.brand_string']).strip()
            
            elif system == 'linux':
                output = cls._run_command(['cat', '/proc/cpuinfo'])
                match = re.search(r'model name\s*:\s*(.+)', output)
                return match.group(1).strip() if match else None
            
            elif system == 'windows':
                output = cls._run_command(['wmic', 'cpu', 'get', 'name', '/value'])
                match = re.search(r'Name=(.+)', output)
                return match.group(1).strip() if match else None
        
        except Exception:
            pass
        
        return None
    
    @classmethod
    def _get_motherboard_info(cls) -> Optional[str]:
        """Get motherboard information"""
        system = platform.system().lower()
        
        try:
            if system == 'darwin':
                output = cls._run_command(['system_profiler', 'SPHardwareDataType'])
                match = re.search(r'Serial Number.*?:\s*(.+)', output)
                return match.group(1).strip() if match else None
            
            elif system == 'linux':
                return cls._run_command(['sudo', 'dmidecode', '-s', 'baseboard-serial-number']).strip()
            
            elif system == 'windows':
                output = cls._run_command(['wmic', 'baseboard', 'get', 'serialnumber', '/value'])
                match = re.search(r'SerialNumber=(.+)', output)
                return match.group(1).strip() if match else None
        
        except Exception:
            pass
        
        return None
    
    @classmethod
    def _get_disk_serial(cls) -> Optional[str]:
        """Get disk serial number"""
        system = platform.system().lower()
        
        try:
            if system == 'darwin':
                output = cls._run_command(['diskutil', 'info', '/'])
                match = re.search(r'Volume UUID:\s*(.+)', output)
                return match.group(1).strip() if match else None
            
            elif system == 'linux':
                return cls._run_command(['lsblk', '-dno', 'SERIAL']).strip().split('\n')[0]
            
            elif system == 'windows':
                output = cls._run_command(['wmic', 'diskdrive', 'get', 'serialnumber', '/value'])
                match = re.search(r'SerialNumber=(.+)', output)
                return match.group(1).strip() if match else None
        
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _get_local_ip() -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to get local IP (doesn't actually send data)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'
    
    @classmethod
    def _get_memory_info(cls) -> Optional[str]:
        """Get memory information"""
        system = platform.system().lower()
        
        try:
            if system == 'darwin':
                return cls._run_command(['sysctl', '-n', 'hw.memsize']).strip()
            
            elif system == 'linux':
                output = cls._run_command(['cat', '/proc/meminfo'])
                match = re.search(r'MemTotal:\s*(\d+)', output)
                return match.group(1) if match else None
            
            elif system == 'windows':
                output = cls._run_command(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory', '/value'])
                match = re.search(r'TotalPhysicalMemory=(.+)', output)
                return match.group(1).strip() if match else None
        
        except Exception:
            pass
        
        return None
    
    @classmethod
    def _get_disk_info(cls) -> Optional[str]:
        """Get disk information"""
        system = platform.system().lower()
        
        try:
            if system in ['darwin', 'linux']:
                output = cls._run_command(['df', '-h', '/'])
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].split()[0]
            
            elif system == 'windows':
                output = cls._run_command(['wmic', 'logicaldisk', 'get', 'size,caption', '/value'])
                match = re.search(r'Size=(.+)', output)
                return match.group(1).strip() if match else None
        
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _get_environment_hash() -> str:
        """Get hash of relevant environment variables"""
        try:
            env_vars = ['HOME', 'USER', 'USERNAME', 'PATH', 'SHELL']
            env_data = '|'.join(f"{var}={os.environ.get(var, '')}" for var in env_vars)
            return hashlib.sha256(env_data.encode()).hexdigest()[:16]
        except Exception:
            return 'unknown-env'
    
    @staticmethod
    def _run_command(cmd: List[str], timeout: int = 5) -> str:
        """Run a system command and return its output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return result.stdout or ''
        except Exception:
            return ''
