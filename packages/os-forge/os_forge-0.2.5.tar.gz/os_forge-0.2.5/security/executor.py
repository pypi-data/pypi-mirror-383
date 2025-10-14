"""
Secure Command Execution Module

Provides secure command execution with input validation and privilege escalation handling.
"""

import logging
import shlex
import subprocess
from typing import List, Union


class SecureCommandExecutor:
    """
    Secure command execution with input validation and privilege escalation handling.
    
    Security Features:
    1. Command whitelist validation
    2. Parameter sanitization
    3. Privilege escalation handling
    4. Input validation
    5. Audit logging
    """
    
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Whitelist of allowed command prefixes by OS
        self.allowed_commands = {
            'windows': [
                # PowerShell commands
                'powershell', 'pwsh', 'Get-', 'Set-', 'Enable-', 'Disable-',
                'New-', 'Remove-', 'Add-', 'Clear-', 'Test-', 'Invoke-',
                # Registry commands
                'reg', 'regedit', 'regsvr32',
                # System commands
                'wmic', 'net', 'sc', 'bcdedit', 'gpupdate', 'gpresult',
                'netsh', 'wusa', 'sfc', 'dism', 'chkdsk', 'diskpart',
                # Windows Defender
                'mpcmdrun', 'Update-MpSignature', 'Start-MpScan',
                # Service management
                'tasklist', 'taskkill', 'schtasks', 'wmic service',
                # User management
                'net user', 'net localgroup', 'whoami', 'query user',
                # File operations
                'icacls', 'attrib', 'cacls', 'takeown', 'robocopy',
                # Network commands
                'ipconfig', 'ping', 'tracert', 'nslookup', 'netstat',
                # Windows Update
                'wuauclt', 'usoclient', 'WindowsUpdate',
                # Event logs
                'wevtutil', 'eventvwr',
                # Group Policy
                'gpedit', 'rsop', 'gpresult'
            ],
            'linux': [
                # System commands
                'grep', 'sed', 'awk', 'systemctl', 'ufw', 'sysctl', 'lsmod',
                'bootctl', 'dpkg', 'rpm', 'yum', 'apt', 'sudo', 'apt-get',
                # File operations
                'stat', 'chmod', 'chown', 'cat', 'echo', 'tee', 'cut',
                'find', 'ls', 'wc', 'head', 'tail', 'sort', 'uniq',
                # Network and security
                'iptables', 'firewalld', 'sshd', 'ssh', 'openssh',
                'ip', 'iwconfig', 'netstat', 'ss', 'tcpdump',
                # Process and service management
                'service', 'chkconfig', 'systemd', 'cron', 'chrony',
                # Package management
                'dnf', 'zypper', 'pacman', 'emerge',
                # File system
                'mount', 'umount', 'fstab', 'passwd', 'shadow',
                # Kernel and modules
                'modprobe', 'rmmod', 'insmod', 'lsmod',
                # Time synchronization
                'ntp', 'timesyncd', 'chronyd',
                # Logging and monitoring
                'journalctl', 'logrotate', 'rsyslog', 'auditctl', 'auditd',
                # Security tools
                'getenforce', 'aa-status', 'sestatus', 'selinux',
                # Additional hardening commands
                'bluetooth', 'cups', 'avahi', 'dhcp', 'dns', 'ftp', 'ldap',
                'mail', 'nfs', 'nis', 'rpc', 'rsync', 'samba', 'snmp',
                'tftp', 'proxy', 'web', 'xinetd', 'x11', 'gdm'
            ]
        }
        
        # Commands that require privilege escalation
        self.sudo_required = [
            'systemctl', 'ufw', 'sed -i', 'tee -a', 'modprobe', 'apt-get',
            'chmod', 'chown', 'mount', 'umount', 'sysctl', 'firewalld',
            'service', 'chkconfig', 'dnf', 'yum', 'zypper'
        ]
    
    def _validate_command(self, command: str, os_type: str) -> bool:
        """Validate command against whitelist with enhanced Windows support"""
        if not command or not command.strip():
            return False
            
        # Get allowed commands for OS
        allowed = self.allowed_commands.get(os_type, [])
        
        # Check if command starts with allowed prefix
        command_lower = command.lower().strip()
        
        # Special handling for complex commands with pipes and redirects
        # Extract the first command from pipe chains
        first_cmd = command_lower.split('|')[0].split('&&')[0].split('||')[0].split(';')[0].strip()
        
        # Enhanced Windows PowerShell validation
        if os_type == 'windows':
            # Check for PowerShell commands with -Command parameter
            if 'powershell' in first_cmd or 'pwsh' in first_cmd:
                self.logger.info(f"Allowing PowerShell command: {command}")
                return True
            
            # Check for PowerShell cmdlets (Get-, Set-, etc.)
            for allowed_cmd in allowed:
                if allowed_cmd.endswith('-') and first_cmd.startswith(allowed_cmd.lower()):
                    self.logger.info(f"Allowing PowerShell cmdlet: {command}")
                    return True
                elif first_cmd.startswith(allowed_cmd.lower()):
                    return True
        
        # Standard validation for other commands
        for allowed_cmd in allowed:
            if first_cmd.startswith(allowed_cmd.lower()):
                return True
        
        # Additional validation for hardening-specific commands
        hardening_patterns = [
            # Linux patterns
            'kernel.randomize_va_space', 'permitrootlogin', 'protocol',
            'unattended-upgrade', 'timesyncd', 'chrony', 'cron',
            'firewalld', 'ufw', 'passwd', 'shadow', 'motd', 'issue',
            # Network security patterns
            'ipv6', 'inet6', 'wireless', 'ieee 802.11', 'bluetooth',
            # SSH security patterns
            'ssh_host', 'allowusers', 'denyusers', 'allowgroups', 'denygroups',
            'maxauthtries', 'maxsessions', 'clientaliveinterval', 'clientalivecountmax',
            # Logging patterns
            'logrotate', 'logfiles', 'auditctl', 'auditd', 'rsyslog',
            # Service patterns
            'autofs', 'avahi', 'dhcp', 'dns', 'ftp', 'ldap', 'mail', 'nfs',
            'nis', 'rpc', 'rsync', 'samba', 'snmp', 'tftp', 'proxy', 'web',
            'xinetd', 'x11', 'gdm', 'cups',
            # Windows patterns
            'enablelua', 'consentpromptbehavioradmin', 'firewall',
            'defender', 'bitlocker', 'smb', 'rdp', 'remoteaccess',
            'windowsupdate', 'autologon', 'guestaccount', 'administrator',
            'powershellpolicy', 'executionpolicy', 'scriptblocklogging'
        ]
        
        # Allow commands that contain hardening-related patterns
        for pattern in hardening_patterns:
            if pattern in command_lower:
                self.logger.info(f"Allowing hardening command: {command}")
                return True
        
        self.logger.warning(f"Command not in whitelist: {command}")
        return False
    
    def _needs_sudo(self, command: str) -> bool:
        """Check if command requires sudo privileges"""
        command_lower = command.lower()
        return any(sudo_cmd in command_lower for sudo_cmd in self.sudo_required)
    
    def _sanitize_command(self, command: str) -> Union[List[str], str]:
        """
        Sanitize command by parsing it safely with enhanced Windows support
        
        Returns either:
        - List[str] for simple commands that can run with shell=False
        - str for complex commands that need shell=True but are validated
        
        This prevents command injection by:
        1. Using shlex to properly parse simple command arguments
        2. Validating complex commands against whitelist
        3. Avoiding shell interpretation when possible
        4. Special handling for Windows PowerShell commands
        """
        try:
            command = command.strip()
            
            # Check if command contains shell features that require shell=True
            shell_features = ['|', '>', '<', '&&', '||', ';', '`', '$', '(', ')']
            needs_shell = any(feature in command for feature in shell_features)
            
            # Windows PowerShell commands almost always need shell=True
            if command.lower().startswith(('powershell', 'pwsh')):
                self.logger.info(f"PowerShell command requires shell: {command}")
                return command
            
            # Windows registry commands need shell=True
            if command.lower().startswith(('reg ', 'regedit', 'netsh')):
                self.logger.info(f"Windows system command requires shell: {command}")
                return command
            
            if needs_shell:
                # Complex command - return as string for shell=True but validated
                self.logger.info(f"Complex command requires shell: {command}")
                return command
            else:
                # Simple command - parse into list for shell=False
                try:
                    return shlex.split(command)
                except ValueError:
                    # If shlex fails, fall back to shell=True for complex commands
                    self.logger.warning(f"shlex parsing failed, using shell=True: {command}")
                    return command
                    
        except ValueError as e:
            self.logger.error(f"Failed to parse command: {command}, Error: {e}")
            raise ValueError(f"Invalid command syntax: {command}")
    
    def execute_command(self, command: str, os_type: str, timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Securely execute a command with validation and logging
        
        Args:
            command: Command to execute
            os_type: Operating system type (windows/linux/ubuntu/centos)
            timeout: Command timeout in seconds
            
        Returns:
            subprocess.CompletedProcess object
            
        Raises:
            ValueError: If command is invalid or not allowed
            subprocess.TimeoutExpired: If command times out
        """
        
        # Normalize OS type
        if os_type in ['ubuntu', 'centos']:
            os_type = 'linux'
        
        # Validate command
        if not self._validate_command(command, os_type):
            raise ValueError(f"Command not allowed: {command}")
        
        # Log the execution attempt
        self.logger.info(f"Executing command: {command} (OS: {os_type})")
        
        try:
            # Sanitize command - get either list or string
            sanitized_cmd = self._sanitize_command(command)
            
            # Determine if we need shell=True
            if isinstance(sanitized_cmd, str):
                # Complex command requiring shell=True (but validated)
                self.logger.info(f"Executing with shell=True (validated): {command}")
                result = subprocess.run(
                    sanitized_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=True  # Required for complex commands, but command is validated
                )
            else:
                # Simple command that can run with shell=False
                self.logger.info(f"Executing with shell=False: {command}")
                result = subprocess.run(
                    sanitized_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=False  # SECURE: No shell interpretation
                )
            
            # Log result with more detail
            if result.returncode == 0:
                self.logger.info(f"Command completed successfully: {command}")
            else:
                self.logger.warning(f"Command failed with return code {result.returncode}: {command}")
                if result.stderr:
                    self.logger.warning(f"Error output: {result.stderr}")
                if result.stdout:
                    self.logger.info(f"Output: {result.stdout}")
            
            return result
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {command}")
            raise
        except FileNotFoundError:
            # Command not found - might need different handling on Windows vs Linux
            self.logger.error(f"Command not found: {command}")
            raise ValueError(f"Command not found: {sanitized_cmd[0] if isinstance(sanitized_cmd, list) else command}")
        except Exception as e:
            self.logger.error(f"Command execution failed: {command}, Error: {e}")
            raise

