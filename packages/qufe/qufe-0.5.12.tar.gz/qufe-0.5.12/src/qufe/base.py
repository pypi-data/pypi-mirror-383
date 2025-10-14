import difflib
import importlib.util as ut
import os
import re
import socket
import time
from datetime import datetime
from typing import Optional, Dict, Any
from zoneinfo import ZoneInfo


class TS:
    """Timestamp handling utility class with timezone support."""

    def __init__(self, time_zone: str = 'Asia/Seoul'):
        """
        Initialize timestamp handler.

        Args:
            time_zone: Timezone string (default: 'Asia/Seoul')
        """
        self.time_zone = time_zone
        self.tz_info = ZoneInfo(time_zone)
        self.time_format = '%Y-%m-%d %H:%M:%S'

    def timestamp_to_datetime(self, timestamp) -> datetime:
        """
        Convert timestamp to datetime object with timezone.

        Args:
            timestamp: Unix timestamp (int/float) or datetime object

        Returns:
            datetime object with timezone or None if invalid input

        Example:
            >>> ts = TS()
            >>> dt = ts.timestamp_to_datetime(1640995200)  # 2022-01-01 00:00:00 UTC
        """
        match timestamp:
            case int() | float():
                return datetime.fromtimestamp(timestamp, tz=self.tz_info)
            case datetime():
                return timestamp
            case _:
                return None

    def get_ts_formatted(self, timestamp) -> str:
        """
        Get formatted timestamp string.

        Args:
            timestamp: Unix timestamp or datetime object

        Returns:
            Formatted timestamp string or None if invalid

        Example:
            >>> ts = TS()
            >>> formatted = ts.get_ts_formatted(1640995200)
            >>> print(formatted)  # '2022-01-01 09:00:00'
        """
        if isinstance(timestamp, int | float):
            timestamp = self.timestamp_to_datetime(timestamp)

        if isinstance(timestamp, datetime):
            return timestamp.strftime(self.time_format)
        else:
            return None


# ============================================================================
# Progress Bar Utilities
# ============================================================================

class ProgressBar:
    """
    Progress bar utility for visual feedback during long operations.

    Supports both console and Jupyter notebook environments.
    """

    @staticmethod
    def show_bar(current: int, total: int, prefix: str = "Progress",
                 suffix: str = "", bar_length: int = 30,
                 filled_char: str = "█", empty_char: str = "░") -> str:
        """
        Generate a text-based progress bar.

        Args:
            current: Current progress value
            total: Total value for completion
            prefix: Text to display before the bar
            suffix: Text to display after the bar
            bar_length: Length of the progress bar in characters
            filled_char: Character for filled portion
            empty_char: Character for empty portion

        Returns:
            Formatted progress bar string

        Example:
            >>> bar = ProgressBar.show_bar(30, 100, prefix="Processing")
            >>> print(bar)
            Processing: [█████████░░░░░░░░░░░░░░░░░░░░░] 30.0% (30/100)
        """
        if total == 0:
            return f"{prefix}: [{empty_char * bar_length}] 0.0% (0/0) {suffix}"

        percent = (current / total) * 100
        filled = int(bar_length * current / total)
        bar = filled_char * filled + empty_char * (bar_length - filled)

        result = f"{prefix}: [{bar}] {percent:.1f}% ({current}/{total})"
        if suffix:
            result += f" {suffix}"

        return result

    @staticmethod
    def show_spinner(current: int, prefix: str = "Processing",
                     suffix: str = "") -> str:
        """
        Generate a simple spinner animation.

        Args:
            current: Current iteration count
            prefix: Text before spinner
            suffix: Text after spinner

        Returns:
            Formatted spinner string

        Example:
            >>> for i in range(10):
            ...     spinner = ProgressBar.show_spinner(i, "Loading")
            ...     print(f"\r{spinner}", end="")
        """
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spinner = spinners[current % len(spinners)]

        result = f"{prefix} {spinner}"
        if suffix:
            result += f" {suffix}"

        return result

    @staticmethod
    def update_display(content: str, jupyter_mode: bool = False,
                       clear: bool = True) -> None:
        """
        Update display with content, supporting both console and Jupyter.

        Args:
            content: Content to display
            jupyter_mode: Whether running in Jupyter environment
            clear: Whether to clear previous output

        Example:
            >>> for i in range(100):
            ...     bar = ProgressBar.show_bar(i, 100)
            ...     ProgressBar.update_display(bar, jupyter_mode=True)
        """
        if jupyter_mode:
            try:
                from IPython.display import clear_output, display
                if clear:
                    clear_output(wait=True)
                print(content)
            except ImportError:
                # Fallback to console mode if IPython not available
                if clear:
                    print(f"\r{content}", end="", flush=True)
                else:
                    print(content)
        else:
            if clear:
                # Console mode with carriage return
                print(f"\r{content}", end="", flush=True)
            else:
                print(content)

    @staticmethod
    def format_time(seconds: float) -> str:
        """
        Format seconds into human-readable time string.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string

        Example:
            >>> ProgressBar.format_time(125.5)
            '2m 5s'
            >>> ProgressBar.format_time(3665)
            '1h 1m 5s'
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}h {minutes}m {secs}s"

    @staticmethod
    def estimate_remaining(current: int, total: int,
                           elapsed_seconds: float) -> Optional[float]:
        """
        Estimate remaining time based on current progress.

        Args:
            current: Current progress value
            total: Total value for completion
            elapsed_seconds: Elapsed time in seconds

        Returns:
            Estimated remaining time in seconds or None

        Example:
            >>> remaining = ProgressBar.estimate_remaining(30, 100, 15.0)
            >>> print(f"Remaining: {ProgressBar.format_time(remaining)}")
        """
        if current == 0 or total == 0:
            return None

        rate = current / elapsed_seconds
        remaining_items = total - current

        if rate > 0:
            return remaining_items / rate
        else:
            return None


class ProgressTracker:
    """
    Advanced progress tracking with statistics and time estimation.

    Supports status messages for richer feedback during processing.
    """

    def __init__(self, total: int, prefix: str = "Progress",
                 jupyter_mode: bool = False, bar_length: int = 30,
                 show_status: bool = True):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items to process
            prefix: Prefix text for progress bar
            jupyter_mode: Whether in Jupyter environment
            bar_length: Length of progress bar
            show_status: Whether to display status messages
        """
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.jupyter_mode = jupyter_mode
        self.bar_length = bar_length
        self.show_status = show_status
        self.start_time = time.time()
        self.errors = []
        self.completed_items = []
        self.statuses = []  # Track status messages
        self.current_status = None  # Current status to display

    def update(self, increment: int = 1, item: Any = None,
               error: Optional[str] = None, status: Optional[str] = None) -> None:
        """
        Update progress with optional item tracking and status message.

        Args:
            increment: Amount to increment progress
            item: Item that was processed (optional)
            error: Error message if processing failed (optional)
            status: Status message to display (optional)
        """
        self.current += increment

        if error:
            self.errors.append({'item': item, 'error': error})
        elif item is not None:
            self.completed_items.append(item)

        if status is not None:
            self.statuses.append({'item': item, 'status': status})
            self.current_status = status

        self._display_progress()

    def _display_progress(self) -> None:
        """Display current progress with statistics and status."""
        elapsed = time.time() - self.start_time

        # Generate progress bar
        bar = ProgressBar.show_bar(
            self.current, self.total,
            prefix=self.prefix,
            bar_length=self.bar_length
        )

        # Build content lines
        content = [bar]

        # Add current status if available
        if self.show_status and self.current_status:
            content.append(f"Status: {self.current_status}")

        # Add time information
        elapsed_str = ProgressBar.format_time(elapsed)
        content.append(f"Elapsed: {elapsed_str}")

        # Add remaining time estimate
        remaining = ProgressBar.estimate_remaining(
            self.current, self.total, elapsed
        )
        if remaining:
            remaining_str = ProgressBar.format_time(remaining)
            content.append(f"Remaining: {remaining_str}")

        # Add error count if any
        if self.errors:
            content.append(f"Errors: {len(self.errors)}")

        # Update display
        display_content = "\n".join(content)
        ProgressBar.update_display(
            display_content,
            jupyter_mode=self.jupyter_mode
        )

    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of all status messages.

        Returns:
            Dictionary with status statistics
        """
        if not self.statuses:
            return {}

        # Count status types
        status_counts = {}
        for status_entry in self.statuses:
            status_msg = status_entry['status']
            status_counts[status_msg] = status_counts.get(status_msg, 0) + 1

        return {
            'total_statuses': len(self.statuses),
            'unique_statuses': len(status_counts),
            'status_counts': status_counts,
            'recent_statuses': self.statuses[-5:]  # Last 5 statuses
        }

    def finish(self, show_summary: bool = True) -> Dict[str, Any]:
        """
        Finish tracking and return summary.

        Args:
            show_summary: Whether to display summary

        Returns:
            Dictionary with tracking statistics including status summary
        """
        elapsed = time.time() - self.start_time

        summary = {
            'total': self.total,
            'completed': self.current,
            'errors': len(self.errors),
            'elapsed_time': elapsed,
            'elapsed_formatted': ProgressBar.format_time(elapsed),
            'items_per_second': self.current / elapsed if elapsed > 0 else 0,
            'error_details': self.errors,
            'completed_items': self.completed_items,
            'status_summary': self.get_status_summary()  # Add status summary
        }

        if show_summary:
            print()  # New line after progress bar
            print("=" * 50)
            print("Completion Summary")
            print("=" * 50)
            print(f"Processed: {summary['completed']}/{summary['total']}")
            print(f"Time taken: {summary['elapsed_formatted']}")
            print(f"Processing rate: {summary['items_per_second']:.2f} items/sec")

            # Show status summary if available
            if summary['status_summary'] and summary['status_summary'].get('status_counts'):
                print("\nResults by status:")
                for status, count in summary['status_summary']['status_counts'].items():
                    print(f"  • {status}: {count}")

            if summary['errors']:
                print(f"\nErrors: {summary['errors']}")
                # Show first few errors
                for i, error_entry in enumerate(summary['error_details'][:3]):
                    print(f"  - {error_entry['item']}: {error_entry['error']}")
                if len(summary['error_details']) > 3:
                    print(f"  ... and {len(summary['error_details']) - 3} more")

        return summary


def diff_codes(left: str, right: str, mode: int = 0):
    """
    Compare two code strings with different diff formats.

    Args:
        left: Left code string to compare
        right: Right code string to compare
        mode: Comparison mode (0=simple, 1=unified, 2=ndiff)

    Example:
        >>> diff_codes("line1\nline2", "line1\nmodified", mode=1)
    """
    left_lines = left.splitlines()
    right_lines = right.splitlines()

    match mode:
        case 0:
            print("\n=== simple mode ===\n")
            # Simple line-by-line comparison
            for i, (l, r) in enumerate(zip(left_lines, right_lines), start=1):
                if l != r:
                    print(f"Difference found at line {i}:")
                    print(f"Left: {l}")
                    print(f"Right: {r}")
                    print()
            # Handle different line counts
            if len(left_lines) > len(right_lines):
                print("Additional lines in left code:")
                for i, l in enumerate(left_lines[len(right_lines):], start=len(right_lines) + 1):
                    print(f"Line {i}: {l}")
            elif len(right_lines) > len(left_lines):
                print("Additional lines in right code:")
                for i, r in enumerate(right_lines[len(left_lines):], start=len(left_lines) + 1):
                    print(f"Line {i}: {r}")
        case 1:
            print("\n=== unified mode ===\n")
            # Unified diff format
            diff = difflib.unified_diff(
                left_lines, right_lines,
                fromfile='left', tofile='right',
                lineterm=''
            )
            print("\n".join(diff))
        case 2:
            print("\n=== ndiff mode ===")
            # Detailed ndiff format
            diff = difflib.ndiff(left_lines, right_lines)
            print("\n".join(diff))
        case _:
            print("Unsupported mode. Please choose 0 (simple), 1 (unified), or 2 (ndiff).")


def import_script(script_name: str, script_path: str):
    """
    Dynamically import a Python module from file path.

    Args:
        script_name: Name for the imported module
        script_path: Path to the Python file to import

    Returns:
        Imported module object

    Example:
        >>> module = import_script("my_module", "/path/to/script.py")
        >>> module.some_function()
    """
    module_spec = ut.spec_from_file_location(script_name, script_path)
    module = ut.module_from_spec(module_spec)

    module_dir = os.path.dirname(script_path)
    prev_cwd = os.getcwd()
    os.chdir(module_dir)

    try:
        module_spec.loader.exec_module(module)
    finally:
        os.chdir(prev_cwd)

    return module


def flatten(lst, max_depth=1, current_depth=0):
    """
    Flatten nested lists up to a specified depth.

    Args:
        lst: The list to flatten
        max_depth: Maximum depth to flatten (default: 1)
        current_depth: Current recursion depth (internal use)

    Returns:
        Flattened list

    Example:
        >>> flatten([1, [2, [3, 4], 5], [6, 7], 8])
        [1, 2, 3, 4, 5, 6, 7, 8]
    """
    result = []
    for item in lst:
        if isinstance(item, list) and current_depth < max_depth:
            result.extend(flatten(item, max_depth, current_depth + 1))
        else:
            result.append(item)
    return result


def flatten_gen(lst, max_depth=1, current_depth=0):
    """
    Flatten nested lists using generator (memory efficient).

    Args:
        lst: The list to flatten
        max_depth: Maximum depth to flatten (default: 1)
        current_depth: Current recursion depth (internal use)

    Yields:
        Flattened items one by one

    Example:
        >>> list(flatten_gen([1, [2, [3, [4]], 5]]))
        [1, 2, 3, 4, 5]
    """
    for item in lst:
        if isinstance(item, list) and current_depth < max_depth:
            yield from flatten_gen(item, max_depth, current_depth + 1)
        else:
            yield item


def flatten_any(nested, max_depth=1, current_depth=0):
    """
    Flatten nested collections (list, tuple, set) up to specified depth.

    Args:
        nested: The nested collection to flatten
        max_depth: Maximum depth to flatten (default: 1)
        current_depth: Current recursion depth (internal use)

    Yields:
        Flattened items one by one

    Example:
        >>> list(flatten_any([1, (2, [3, {4, 5}])]))
        [1, 2, 3, 4, 5]  # Order may vary for set items
    """
    for item in nested:
        if isinstance(item, (list, tuple, set)) and current_depth < max_depth:
            yield from flatten_any(item, max_depth, current_depth + 1)
        else:
            yield item


def flatten_three_levels_with_suffix(nested_dict: dict) -> dict:
    """
    Flatten 3-level nested dictionary by merging level2 into level1
    with suffix notation for original parent keys.

    Args:
        nested_dict: 3-level nested dictionary

    Returns:
        Flattened dictionary with suffix notation

    Example:
        >>> data = {'A': {'x': 1, 'y': {'p': 10, 'q': 20}, 'z': 3}}
        >>> flatten_three_levels_with_suffix(data)
        {'A': {'x': 1, 'p (y)': 10, 'q (y)': 20, 'z': 3}}
    """
    result = {}
    for (top_key, level1) in nested_dict.items():
        if not isinstance(level1, dict):
            result[top_key] = level1
            continue

        merged = {}
        for (k1, v1) in level1.items():
            if isinstance(v1, dict):
                # Level2 dict: extract items with suffix
                for (k2, v2) in v1.items():
                    new_key = f"{k2} ({k1})"
                    merged[new_key] = v2
            else:
                merged[k1] = v1

        result[top_key] = merged

    return result


# ============================================================================
# Network Utilities (WOL)
# ============================================================================


class WOL:
    """Wake-on-LAN utility for network device control."""

    def __init__(self, verbose: bool = True):
        """
        Initialize Wake-on-LAN handler.

        Args:
            verbose: Enable detailed output messages (default: True)
        """
        self.verbose = verbose

    def validate_mac(self, mac: str) -> bool:
        """
        Validate MAC address format.

        Args:
            mac: MAC address string

        Returns:
            True if valid MAC address format

        Example:
            >>> wol = WOL()
            >>> wol.validate_mac("AA:BB:CC:DD:EE:FF")
            True
            >>> wol.validate_mac("AA-BB-CC-DD-EE-FF")
            True
        """
        # Support various MAC formats: XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXXXXXXXXXX
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]?){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac.replace(' ', '')))

    def format_mac(self, mac: str) -> str:
        """
        Format MAC address to standard colon notation.

        Args:
            mac: MAC address string in any supported format

        Returns:
            MAC address in XX:XX:XX:XX:XX:XX format

        Raises:
            ValueError: If MAC address format is invalid

        Example:
            >>> wol = WOL()
            >>> wol.format_mac("aabbccddeeff")
            'AA:BB:CC:DD:EE:FF'
        """
        # Remove all separators
        mac_clean = re.sub(r'[:\-\s]', '', mac).upper()

        # Validate length
        if len(mac_clean) != 12:
            raise ValueError(f"Invalid MAC address length: {len(mac_clean)} (expected 12)")

        # Format as XX:XX:XX:XX:XX:XX
        return ':'.join(mac_clean[i:i + 2] for i in range(0, 12, 2))

    def create_magic_packet(self, mac: str) -> bytes:
        """
        Create WOL magic packet.

        Magic packet structure:
        - 6 bytes of 0xFF (synchronization stream)
        - Target MAC address repeated 16 times

        Args:
            mac: Target device MAC address

        Returns:
            Magic packet as bytes

        Example:
            >>> wol = WOL()
            >>> packet = wol.create_magic_packet("AA:BB:CC:DD:EE:FF")
            >>> len(packet)
            102
        """
        mac_formatted = self.format_mac(mac)
        mac_bytes = bytes.fromhex(mac_formatted.replace(':', ''))

        # Magic packet: 0xFF * 6 + MAC * 16
        return b'\xff' * 6 + mac_bytes * 16

    def send_packet(self,
                    mac: str,
                    broadcast_ip: str = '255.255.255.255',
                    port: int = 9,
                    attempts: int = 3,
                    delay: float = 0.5) -> bool:
        """
        Send WOL magic packet to network.

        Args:
            mac: Target device MAC address
            broadcast_ip: Broadcast IP address (default: 255.255.255.255)
            port: WOL port (default: 9, alternative: 7)
            attempts: Number of send attempts (default: 3)
            delay: Delay between attempts in seconds (default: 0.5)

        Returns:
            True if packet sent successfully

        Example:
            >>> wol = WOL()
            >>> success = wol.send_packet("AA:BB:CC:DD:EE:FF")
        """
        if not self.validate_mac(mac):
            raise ValueError(f"Invalid MAC address format: {mac}")

        packet = self.create_magic_packet(mac)

        # Create UDP socket with broadcast enabled
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            for attempt in range(attempts):
                try:
                    sock.sendto(packet, (broadcast_ip, port))
                    if self.verbose:
                        print(f"  [{attempt + 1}/{attempts}] Magic packet sent to {broadcast_ip}:{port}")

                    if attempt < attempts - 1:
                        time.sleep(delay)

                except Exception as e:
                    if self.verbose:
                        print(f"  [{attempt + 1}/{attempts}] Send failed: {e}")
                    return False

            return True

    def wake(self,
             mac: str,
             device_name: Optional[str] = None,
             subnet_broadcast: Optional[str] = None) -> bool:
        """
        Wake network device using Wake-on-LAN.

        Args:
            mac: Target device MAC address
            device_name: Device name for display (optional)
            subnet_broadcast: Subnet broadcast address (e.g., 192.168.1.255)

        Returns:
            True if wake signals sent successfully

        Example:
            >>> wol = WOL()
            >>> wol.wake("AA:BB:CC:DD:EE:FF", device_name="Development Server")

            >>> # With subnet broadcast
            >>> wol.wake("AA:BB:CC:DD:EE:FF",
            ...          device_name="Office PC",
            ...          subnet_broadcast="192.168.1.255")
        """
        success = True

        if self.verbose:
            print("=" * 50)
            print("Wake-on-LAN")
            print("=" * 50)
            if device_name:
                print(f"Target device: {device_name}")

            try:
                mac_formatted = self.format_mac(mac)
                print(f"MAC address: {mac_formatted}")
            except ValueError as e:
                print(f"Error: {e}")
                return False

            print("-" * 50)

        # Send via global broadcast
        if self.verbose:
            print("Sending via global broadcast (255.255.255.255)...")

        if not self.send_packet(mac):
            success = False
            if self.verbose:
                print("Global broadcast failed")
        elif self.verbose:
            print("Global broadcast sent successfully")

        # Send via subnet broadcast if provided
        if subnet_broadcast:
            if self.verbose:
                print(f"\nSending via subnet broadcast ({subnet_broadcast})...")

            if not self.send_packet(mac, broadcast_ip=subnet_broadcast):
                success = False
                if self.verbose:
                    print("Subnet broadcast failed")
            elif self.verbose:
                print("Subnet broadcast sent successfully")

        if self.verbose:
            print("-" * 50)
            if success:
                print("Wake signal sent. Device should power on within 10-30 seconds.")
            else:
                print("Failed to send wake signal.")
            print("=" * 50)

        return success


def wake_device(mac: str,
                device_name: Optional[str] = None,
                subnet_broadcast: Optional[str] = None,
                verbose: bool = True) -> bool:
    """
    Wake network device using Wake-on-LAN (convenience function).

    Args:
        mac: Target device MAC address
        device_name: Device name for display (optional)
        subnet_broadcast: Subnet broadcast address (optional)
        verbose: Enable detailed output (default: True)

    Returns:
        True if wake signals sent successfully

    Example:
        >>> # Simple usage
        >>> wake_device("AA:BB:CC:DD:EE:FF")

        >>> # With device name and subnet
        >>> wake_device("AA:BB:CC:DD:EE:FF",
        ...            device_name="Development Server",
        ...            subnet_broadcast="192.168.1.255")

        >>> # Silent mode
        >>> success = wake_device("AA:BB:CC:DD:EE:FF", verbose=False)
    """
    wol = WOL(verbose=verbose)
    return wol.wake(mac, device_name, subnet_broadcast)


def wake_multiple_devices(devices: Dict[str, str],
                          subnet_broadcast: Optional[str] = None,
                          verbose: bool = True,
                          delay: float = 1.0) -> Dict[str, bool]:
    """
    Wake multiple network devices sequentially.

    Args:
        devices: Dictionary of {device_name: mac_address}
        subnet_broadcast: Subnet broadcast address (optional)
        verbose: Enable detailed output (default: True)
        delay: Delay between devices in seconds (default: 1.0)

    Returns:
        Dictionary of {device_name: success_status}

    Example:
        >>> devices = {
        ...     "Development Server": "AA:BB:CC:DD:EE:FF",
        ...     "Testing Machine": "11:22:33:44:55:66",
        ...     "Database Server": "99:88:77:66:55:44"
        ... }
        >>> results = wake_multiple_devices(devices, subnet_broadcast="192.168.1.255")
        >>> for device, success in results.items():
        ...     status = "OK" if success else "FAILED"
        ...     print(f"{device}: {status}")
    """
    wol = WOL(verbose=verbose)
    results = {}

    for i, (name, mac) in enumerate(devices.items()):
        if i > 0:
            time.sleep(delay)
            if verbose:
                print("\n")

        results[name] = wol.wake(mac, device_name=name, subnet_broadcast=subnet_broadcast)

    return results
