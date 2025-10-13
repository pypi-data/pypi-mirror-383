#!/usr/bin/env python

"""
Utility functions for sedlib
"""

__all__ = [
    'tqdm', 'tqdm_joblib', 'ParallelPbar',
    'InMemoryHandler', 'get_local_ip', 'get_system_ram',
    'generate_unique_worker_name', 'MacDaemon', 'Daemon'
]

# System and OS
import os
import platform
import socket
import subprocess
import sys
import uuid

# Python utilities
import contextlib
import logging
from typing import List, Optional

# Progress and parallel processing
import joblib
import psutil
from tqdm import tqdm as terminal_tqdm
from tqdm.auto import tqdm as notebook_tqdm

# Time and process management
import time
import signal
import atexit

# Automatically choose the correct tqdm implementation
if "ipykernel" in sys.modules:
    tqdm = notebook_tqdm
else:
    tqdm = terminal_tqdm


@contextlib.contextmanager
def tqdm_joblib(*args, **kwargs):
    """Context manager to patch joblib to report into tqdm progress bar
    given as argument"""

    tqdm_object = tqdm(*args, **kwargs)

    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()


def ParallelPbar(desc=None, **tqdm_kwargs):

    class Parallel(joblib.Parallel):
        def __call__(self, it):
            it = list(it)
            with tqdm_joblib(total=len(it), desc=desc, **tqdm_kwargs):
                return super().__call__(it)

    return Parallel


class InMemoryHandler(logging.Handler):
    """A logging handler that stores log records in memory."""
    
    def __init__(self, capacity: Optional[int] = None):
        """Initialize the handler with optional capacity limit.
        
        Parameters
        ----------
        capacity : Optional[int]
            Maximum number of log records to store. If None, no limit is applied.
        """
        super().__init__()
        self.capacity = capacity
        self.logs: List[str] = []
        
    def emit(self, record: logging.LogRecord) -> None:
        """Store the log record in memory.
        
        Parameters
        ----------
        record : logging.LogRecord
            The log record to store
        """
        log_entry = self.format(record)
        self.logs.append(log_entry)
        if self.capacity and len(self.logs) > self.capacity:
            self.logs.pop(0)
            
    def get_logs(self, log_type: str = 'all') -> List[str]:
        """Get all stored log records.

        Parameters
        ----------
        log_type : str
            log type to get
            possible values are 'all', 'info', 'debug', 'warning', 'error'
            (default: 'all')

        Returns
        -------
        List[str]
            List of formatted log records
        """
        if log_type == 'all':
            return self.logs.copy()
        elif log_type == 'info':
            return [log for log in self.logs if log[22:].startswith('INFO')]
        elif log_type == 'debug':
            return [log for log in self.logs if log[22:].startswith('DEBUG')]
        elif log_type == 'warning':
            return [log for log in self.logs if log[22:].startswith('WARNING')]
        elif log_type == 'error':
            return [log for log in self.logs if log[22:].startswith('ERROR')]
        else:
            raise ValueError(f"Invalid log type: {log_type}")
    
    def clear(self) -> None:
        """Clear all stored log records."""
        self.logs.clear()


def old_get_local_ip():
    """Get the local network IP address.

    Attempts to find a private network IP address (192.168.x.x, 172.16-31.x.x, 
    or 10.x.x.x) by checking network interfaces and socket connections.

    Returns:
        str: Local network IP address, or "127.0.0.1" if none found.
    """
    def is_local_network_ip(ip):
        """Check if IP is in private network ranges."""
        parts = [int(part) for part in ip.split('.')]
        return ((parts[0] == 192 and parts[1] == 168) or  # 192.168.x.x
                (parts[0] == 172 and 16 <= parts[1] <= 31) or  # 172.16-31.x.x
                (parts[0] == 10))  # 10.x.x.x

    try:
        # Try network interfaces first
        for interface in socket.getaddrinfo(socket.gethostname(), None):
            ip = interface[4][0]
            if '.' in ip and is_local_network_ip(ip):
                return ip

        # Try socket connection method
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.bind(('', 0))
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
            if is_local_network_ip(ip):
                return ip
        finally:
            s.close()
    except Exception:
        pass

    return "127.0.0.1"


def old_get_system_ram():
    """Get total system RAM in GB.
    
    Raises:
        ValueError: If the OS type is not supported

    Returns:
        float: Total RAM in GB
    """

    os_type = sys.platform
    if os_type in ['linux', 'darwin']:
        ram_gb = round(
            os.sysconf('SC_PAGE_SIZE') * 
            os.sysconf('SC_PHYS_PAGES') / (1024.**3)
        )
    elif os_type == 'windows':
        ram_gb = psutil.virtual_memory().total / (1024.**3)
    else:
        raise ValueError(f"Unsupported OS type: {os_type}")
    
    return ram_gb


def get_local_ip() -> str:
    """Return the local IP address by scanning local network interfaces (no external queries)."""
    try:
        # Examine all network interfaces
        addrs = psutil.net_if_addrs()
        for iface, snics in addrs.items():
            for snic in snics:
                if snic.family == socket.AF_INET:
                    ip = snic.address
                    # Skip loopback and link-local addresses
                    if ip.startswith("127.") or ip.startswith("169.254."):
                        continue
                    return ip
    except Exception:
        pass

    # Fallback: hostname lookup
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass

    # Final fallback to loopback
    return "127.0.0.1"


def get_system_ram() -> float:
    """Return total physical RAM in gigabytes across all platforms."""
    total_bytes = psutil.virtual_memory().total
    return round(total_bytes / (1024 ** 3), 0)


def generate_unique_worker_name():
    """
    Generate a unique, memorable name for a worker process on this machine.

    This function always returns the same name when run on the same host,
    regardless of network configuration, yet yields different names on
    different machines. The format is:

        {OS}_{hostname}_{Constellation}{NN}

    - OS         : Single-letter code for the operating system
                   ('L' = Linux, 'W' = Windows, 'M' = macOS, 'U' = Unknown)
    - hostname   : The full machine hostname, lowercased (dots removed)
    - Constellation : A full constellation name chosen deterministically
                      from a fixed list, never truncated
    - NN         : A two-digit number (00–99) to avoid collisions

    By using intact constellation names, nothing is ever cut off, making
    the result easier to remember. Example output:

        "L_my-laptop_Orion07"
    """
    # Determine OS code
    os_name = platform.system()
    os_code = {'Linux': 'L', 'Windows': 'W', 'Darwin': 'M'}.get(os_name, 'U')

    # Get the hostname (remove domain parts, lowercase)
    raw_host = platform.node().split('.')[0]
    hostname = raw_host.lower() if raw_host else 'unknown'

    # Try to read a stable machine identifier
    machine_id = None
    if os_name == 'Linux':
        try:
            with open('/etc/machine-id', 'r') as f:
                machine_id = f.read().strip()
        except Exception:
            pass
    elif os_name == 'Windows':
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            )
            machine_id, _ = winreg.QueryValueEx(key, "MachineGuid")
        except Exception:
            pass
    elif os_name == 'Darwin':
        try:
            out = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                text=True
            )
            for line in out.splitlines():
                if "IOPlatformUUID" in line:
                    machine_id = line.split('=')[1].strip().strip('"')
                    break
        except Exception:
            pass

    # Fallback to MAC address if no platform-specific ID found
    if not machine_id:
        machine_id = f"{uuid.getnode():x}"

    # Build a deterministic UUID5 hash from OS, hostname, and machine_id
    name_input = f"{os_name}-{platform.node()}-{machine_id}"
    hash_hex = uuid.uuid5(uuid.NAMESPACE_OID, name_input).hex

    # Full list of constellations (names never truncated)
    CONSTELLATIONS = [
        "Andromeda", "Antlia", "Apus", "Aquarius", "Aquila", "Ara", "Aries",
        "Auriga", "Bootes", "Caelum", "Camelopardalis", "Cancer", "CanesVenatici",
        "CanisMajor", "CanisMinor", "Capricornus", "Carina", "Cassiopeia",
        "Centaurus", "Cepheus", "Cetus", "Chamaeleon", "Circinus", "Columba",
        "ComaBerenices", "CoronaAustralis", "CoronaBorealis", "Corvus",
        "Crater", "Crux", "Cygnus", "Delphinus", "Dorado", "Draco", "Equuleus",
        "Eridanus", "Fornax", "Gemini", "Grus", "Hercules", "Horologium",
        "Hydra", "Hydrus", "Indus", "Lacerta", "Leo", "LeoMinor", "Lepus",
        "Libra", "Lupus", "Lynx", "Lyra", "Mensa", "Microscopium", "Monoceros",
        "Musca", "Norma", "Octans", "Ophiuchus", "Orion", "Pavo", "Pegasus",
        "Perseus", "Phoenix", "Pictor", "Pisces", "Puppis", "Pyxis", "Reticulum",
        "Sagitta", "Sagittarius", "Scorpius", "Sculptor", "Scutum", "Serpens",
        "Sextans", "Taurus", "Telescopium", "Triangulum", "Tucana", "UrsaMajor",
        "UrsaMinor", "Vela", "Virgo", "Volans", "Vulpecula"
    ]

    # Pick one constellation and a two-digit suffix deterministically
    idx = int(hash_hex[:4], 16) % len(CONSTELLATIONS)
    num = int(hash_hex[4:6], 16) % 100
    constellation = CONSTELLATIONS[idx]

    # Assemble the final name
    return f"{os_code}_{hostname}_{constellation}{num:02d}"


class MacDaemon:
    """macOS daemon implementation that avoids fork() to prevent deadlocks.
    
    Uses subprocess.Popen similar to Windows implementation instead of fork()
    to create a detached process on macOS.
    """
    
    def __init__(self, pidfile, worker, working_dir=None):
        """Initialize the macOS daemon.
        
        Args:
            pidfile (str): Path to file for storing process ID
            worker (Worker): Worker instance to run as daemon
            working_dir (str, optional): Working directory for daemon process
        """
        self.pidfile = os.path.abspath(pidfile)
        self.worker = worker
        self.working_dir = working_dir or os.getcwd()
        self.logger = logging.getLogger("worker.macdaemon")
        
    def is_running(self):
        """Check if the daemon process is currently running.
        
        Returns:
            bool: True if daemon is running, False otherwise
        """
        if not os.path.exists(self.pidfile):
            return False
        
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
            
            if not psutil.pid_exists(pid):
                return False
            
            # Check if process is a Python process
            try:
                process = psutil.Process(pid)
                cmdline = " ".join(process.cmdline()).lower()
                
                # Check if it's our worker script
                if "python" in process.name().lower() and "worker.py" in cmdline:
                    self.logger.debug(f"Found worker process with PID {pid}")
                    return True
                
                self.logger.warning(
                    f"Found process with PID {pid} but not our worker."
                )
                return False
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.logger.error(f"Error checking process: {e}")
                return False
        except (IOError, ValueError) as e:
            self.logger.error(f"Error reading PID file: {e}")
            return False
    
    def _write_pid(self, pid):
        """Write PID to the PID file.
        
        Args:
            pid (int): Process ID to write
        """
        # Create parent directories for pidfile if needed
        pidfile_dir = os.path.dirname(self.pidfile)
        if pidfile_dir and not os.path.exists(pidfile_dir):
            os.makedirs(pidfile_dir)
            
        with open(self.pidfile, 'w') as pf:
            pf.write(f"{pid}\n")
        
        self.logger.info(f"macOS daemon started with PID: {pid}")
    
    def delpid(self):
        """Remove the PID file when daemon exits."""
        if os.path.exists(self.pidfile):
            try:
                os.remove(self.pidfile)
                self.logger.info("PID file removed")
            except Exception as e:
                self.logger.error(f"Error removing PID file: {e}")
    
    def start(self):
        """Start the daemon process."""
        self.logger.info("Starting macOS daemon...")
        
        if self.is_running():
            self.logger.error("Daemon already running according to PID file")
            sys.exit(1)
        
        try:
            # Get script path
            script_path = os.path.abspath(sys.argv[0])
            
            # Build command with daemon flag
            cmd = [
                sys.executable, 
                script_path, 
                "run",
                "--daemon",
                "--config", getattr(self.worker, "_config_file", "config.json"),
                "--logfile", getattr(self.worker, "_logfile", "worker.log"),
                "--loglevel", getattr(self.worker, "_loglevel", "INFO"),
                "--pidfile", self.pidfile
            ]
            
            # Create a detached process
            self.logger.info(f"Starting worker as detached process: {' '.join(cmd)}")
            
            # On macOS, we need to use subprocess but handle differently than Windows
            with open(os.devnull, 'w') as devnull_fh:
                process = subprocess.Popen(
                    cmd,
                    cwd=self.working_dir,
                    stdout=devnull_fh,
                    stderr=devnull_fh,
                    stdin=subprocess.PIPE,
                    # No creationflags parameter on macOS
                )
            
            # Wait briefly to see if process exits immediately (indicating error)
            time.sleep(2)
            
            # process.poll() returns None if running, or exit code if terminated
            exit_code = process.poll()
            if exit_code is not None:
                # If process exited, its stdout/stderr went to devnull.
                # Guide user to the daemon's own log file.
                self.logger.error(
                    f"Process exited immediately with code {exit_code}. "
                    f"Check daemon's log file (e.g., worker.log) for details."
                )
                raise RuntimeError(
                    f"Failed to start daemon (exited with code {exit_code}). "
                    f"Check daemon's log file."
                )
            
            # Process is still running, so it should be our daemon process
            pid = process.pid
            self._write_pid(pid)
            
            self.logger.info(f"macOS daemon started with PID {pid}")
            
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}", exc_info=True)
            self.delpid()
            sys.exit(1)
    
    def stop(self):
        """Stop the daemon process."""
        self.logger.info("Stopping macOS daemon...")
        
        if not os.path.exists(self.pidfile):
            self.logger.warning("PID file not found. Daemon not running?")
            return
        
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
            
            if not psutil.pid_exists(pid):
                self.logger.warning(
                    f"Process {pid} not found. Removing stale PID file."
                )
                self.delpid()
                return
            
            # Try graceful termination first
            try:
                process = psutil.Process(pid)
                self.logger.info(f"Sending termination signal to process {pid}")
                process.terminate()
                
                # Wait for process to terminate
                gone, alive = psutil.wait_procs([process], timeout=10)
                
                # Force kill if still running
                if alive:
                    self.logger.warning(f"Process {pid} did not terminate gracefully. Forcing termination.")
                    for p in alive:
                        p.kill()
            except psutil.NoSuchProcess:
                self.logger.warning(f"Process {pid} not found")
            
            self.delpid()
            self.logger.info("macOS daemon stopped")
            
        except (IOError, ValueError) as err:
            self.logger.error(f"Error reading PID file: {err}")
            self.delpid()
        except Exception as err:
            self.logger.error(f"Error stopping daemon: {err}")
            sys.exit(1)
    
    def restart(self):
        """Restart the daemon process."""
        self.logger.info("Restarting macOS daemon...")
        self.stop()
        time.sleep(2)  # Give it time to fully stop
        self.start()
    
    def run(self):
        """Run the worker daemon loop.
        
        This method is called in the child process when started with the --daemon flag.
        """
        # Create and register cleanup handler
        def cleanup_handler(signum=None, frame=None):
            self.logger.info("Received shutdown signal. Cleaning up...")
            if hasattr(self.worker, 'send_heartbeat'):
                try:
                    self.worker.send_heartbeat(status="offline", message="shutting down")
                except Exception as e:
                    self.logger.error(f"Error sending final heartbeat: {e}")
            
            self.delpid()
            sys.exit(0)
        
        # Register cleanup for normal exit
        atexit.register(cleanup_handler)
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, cleanup_handler)
        signal.signal(signal.SIGINT, cleanup_handler)
        
        # If args supplied by main() calling this directly, write PID
        if os.path.exists(self.pidfile):
            self.logger.debug("PID file already exists")
        else:
            self._write_pid(os.getpid())
        
        try:
            self.logger.info("Starting macOS worker's main processing loop...")
            self.worker.loop()  # Worker's infinite loop
        except Exception as e:
            self.logger.critical(f"Critical error in worker loop: {e}", exc_info=True)
            self.delpid()
            sys.exit(1)


class Daemon:
    """Unix daemon supporting process management.
    
    Implements the Unix double-fork idiom for creating daemon processes
    that run detached from the controlling terminal.
    """
    
    def __init__(self, pidfile, worker, working_dir=None):
        """Initialize the daemon.
        
        Args:
            pidfile (str): Path to file for storing process ID
            worker (Worker): Worker instance to run as daemon
            working_dir (str, optional): Working directory for daemon process
        """
        self.pidfile = os.path.abspath(pidfile)
        self.worker = worker
        self.working_dir = working_dir or os.getcwd()
        self.logger = logging.getLogger("worker.daemon")

    def daemonize(self):
        """Create background process using double-fork method.
        
        Creates a detached process that runs independently from the
        terminal. Sets up proper file descriptors and process hierarchy.
        
        Raises:
            OSError: If fork operations fail
        """
        # First fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit first parent
        except OSError as err:
            self.logger.error(f"First fork failed: {err}")
            sys.exit(1)
        
        # Decouple from parent environment
        os.chdir(self.working_dir)
        os.setsid()
        os.umask(0)

        # Second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit second parent
        except OSError as err:
            self.logger.error(f"Second fork failed: {err}")
            sys.exit(1)
            
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Register cleanup function and record PID
        atexit.register(self.delpid)
        pid = str(os.getpid())

        # Create parent directories for pidfile if needed
        pidfile_dir = os.path.dirname(self.pidfile)
        if pidfile_dir and not os.path.exists(pidfile_dir):
            os.makedirs(pidfile_dir)

        with open(self.pidfile, 'w+') as pf:
            pf.write(f"{pid}\n")
            
        self.logger.info(f"Daemon started with PID: {pid}")

    def delpid(self):
        """Remove the PID file when daemon exits."""
        if os.path.exists(self.pidfile):
            try:
                os.remove(self.pidfile)
                self.logger.info("PID file removed")
            except Exception as e:
                self.logger.error(f"Error removing PID file: {e}")

    def is_running(self):
        """Check if the daemon process is currently running.
        
        Returns:
            bool: True if daemon is running, False otherwise
        """
        if not os.path.exists(self.pidfile):
            return False
        
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
            
            if not psutil.pid_exists(pid):
                return False
            
            # Check process command line to ensure it's our daemon
            process = psutil.Process(pid)
            cmdline = " ".join(process.cmdline()).lower()
            if "python" in process.name().lower() or "python" in cmdline:
                return True
            
            self.logger.warning(
                f"Found stale PID file. Process {pid} not our daemon."
            )
            return False
        except (IOError, ValueError, psutil.NoSuchProcess,
                psutil.AccessDenied) as e:
            self.logger.error(f"Error checking daemon status: {e}")
            return False

    def start(self):
        """Start the daemon process."""
        self.logger.info("Starting daemon...")
        
        if self.is_running():
            self.logger.error("Daemon already running according to PID file")
            sys.exit(1)
        
        try:
            self.daemonize()
            self.run()
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}")
            self.delpid()
            sys.exit(1)

    def stop(self):
        """Stop the daemon process."""
        self.logger.info("Stopping daemon...")
        
        if not os.path.exists(self.pidfile):
            self.logger.warning("PID file not found. Daemon not running?")
            return
        
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
            
            if not psutil.pid_exists(pid):
                self.logger.warning(
                    f"Process {pid} not found. Removing stale PID file."
                )
                self.delpid()
                return
            
            # Send termination signal
            self.logger.info(f"Sending termination signal to process {pid}")
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to terminate
            timeout = 10  # seconds
            start_time = time.time()
            while (psutil.pid_exists(pid) and 
                   time.time() - start_time < timeout):
                time.sleep(0.5)
            
            # Force kill if still running
            if psutil.pid_exists(pid):
                self.logger.warning(
                    f"Process {pid} did not terminate after {timeout}s. "
                    f"Forcing termination."
                )
                os.kill(pid, signal.SIGKILL)
            
            self.delpid()
            self.logger.info("Daemon stopped")
            
        except (IOError, ValueError) as err:
            self.logger.error(f"Error reading PID file: {err}")
            self.delpid()
        except Exception as err:
            self.logger.error(f"Error stopping daemon: {err}")
            sys.exit(1)

    def restart(self):
        """Restart the daemon process."""
        self.logger.info("Restarting daemon...")
        self.stop()
        time.sleep(2)  # Give it time to fully stop
        self.start()

    def run(self):
        """Run the worker daemon loop with signal handling."""
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGHUP, self._handle_signal)
        
        try:
            self.logger.info("Starting worker's main processing loop...")
            self.worker.loop() # This now contains the infinite loop
        except SystemExit:
             self.logger.info("Daemon run loop exited.") # Normal exit via sys.exit
        except Exception as e:
            self.logger.critical(f"Critical error in daemon run loop: {e}", exc_info=True)
            self.delpid()
            sys.exit(1) # Ensure daemon exits on critical failure

    def _handle_signal(self, signum, frame):
        """Handle termination signals for clean shutdown.
        
        Args:
            signum (int): Signal number received
            frame (frame): Current stack frame
        """
        signame = signal.Signals(signum).name
        self.logger.info(f"Received signal {signame}. Shutting down...")
        self.delpid()
        sys.exit(0)
