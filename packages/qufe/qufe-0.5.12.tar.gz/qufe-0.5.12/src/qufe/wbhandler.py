"""
Web Browser Automation Handler

This module provides enhanced browser automation capabilities using pure Selenium
with custom timeout configurations, network monitoring, tab management, and interactive element discovery.

Required dependencies:
    pip install qufe[web]

This installs: selenium>=4.0.0

Classes:
    Browser: Base class for browser automation with common functionality and tab management
    Chrome: Chrome browser implementation with advanced configuration options
    Firefox: Firefox browser implementation with profile management
"""

import os
import sys
import json
import time
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional, Union


# Lazy imports for external dependencies
def _import_selenium_dependencies():
    """Lazy import selenium with helpful error message."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.common.exceptions import (
            WebDriverException, TimeoutException, NoSuchElementException,
            StaleElementReferenceException, ElementNotInteractableException
        )

        return {
            'webdriver': webdriver,
            'By': By,
            'WebDriverWait': WebDriverWait,
            'EC': EC,
            'ActionChains': ActionChains,
            'FirefoxOptions': FirefoxOptions,
            'FirefoxService': FirefoxService,
            'ChromeOptions': ChromeOptions,
            'ChromeService': ChromeService,
            'Select': Select,
            'WebDriverException': WebDriverException,
            'TimeoutException': TimeoutException,
            'NoSuchElementException': NoSuchElementException,
            'StaleElementReferenceException': StaleElementReferenceException,
            'ElementNotInteractableException': ElementNotInteractableException,
        }
    except ImportError as e:
        raise ImportError(
            "Web browser automation requires Selenium. "
            "Install with: pip install qufe[web]"
        ) from e


class TimeoutConfig:
    """Custom timeout configuration to replace SeleniumBase settings."""

    MINI_TIMEOUT = 5         # Default 2s → 5s
    SMALL_TIMEOUT = 20       # Default 7s → 20s
    LARGE_TIMEOUT = 40       # Default 10s → 40s
    EXTREME_TIMEOUT = 80     # Default 30s → 80s
    PAGE_LOAD_TIMEOUT = 180  # Default 120s → 180s
    SAFE_PAGE_LOAD_TIMEOUT = 30  # For timeout-based approach


def help():
    """
    Display help information for web browser automation.

    Shows installation instructions, available classes, and usage examples.
    """
    print("qufe.wbhandler - Web Browser Automation")
    print("=" * 45)
    print()

    try:
        _import_selenium_dependencies()
        print("✓ Dependencies: INSTALLED")
    except ImportError:
        print("✗ Dependencies: MISSING")
        print("  Install with: pip install qufe[web]")
        print("  This installs: selenium>=4.0.0")
        print()
        return

    print()
    print("AVAILABLE CLASSES:")
    print("  • Browser: Base class for browser automation with tab management")
    print("  • Firefox: Firefox browser with profile management")
    print("  • Chrome: Chrome browser with advanced configuration options")
    print()

    print("FEATURES:")
    print("  • Gradual element finding with automatic fallback")
    print("  • Network request monitoring via JavaScript injection")
    print("  • Interactive element discovery and automation")
    print("  • URL parameter extraction and parsing")
    print("  • Timeout-based page loading for compatibility")
    print()

    print("ELEMENT FINDING:")
    print("  • .find_element() - Fast direct find with gradual fallback")
    print("  • .wait_for_element() - Explicit wait for dynamic content")
    print("  • .select_option_by_text() - Dropdown selection with retry logic")
    print()

    print("SELECTOR SHORTCUTS:")
    print("  • XPath: '//button[text()=\"Submit\"]' (starts with //)")
    print("  • CSS: '$#my-id' or '$ .my-class' (starts with $)")
    print("  • Legacy: by='css' or by='xpath' (still supported)")
    print()

    print("TAB MANAGEMENT:")
    print("  • browser.open_new_tab('https://example.com')")
    print("  • browser.switch_to_tab(0)  # Switch to first tab")
    print("  • browser.get_tab_count()   # Get number of tabs")
    print("  • browser.close_current_tab()")
    print()

    print("PAGE LOADING OPTIONS:")
    print("  • browser.open(url)  # Default timeout handling")
    print("  • browser.open(url, safe_timeout=True)  # Shorter timeout")
    print("  • browser.open(url, timeout=15)  # Custom timeout")
    print("  • browser.wait_for_network_idle()  # Wait for network activity to settle")
    print()

    print("USAGE EXAMPLE:")
    print("  from qufe.wbhandler import Chrome")
    print("  ")
    print("  # Start browser with method chaining (secure by default)")
    print("  browser = Chrome()")
    print("  browser.configure_no_automation().configure_detach()")
    print("  ")
    print("  # Safe loading for protected environments")
    print("  browser.open('https://example.com', safe_timeout=True)")
    print("  browser.wait_for_network_idle(idle_time=2.0)")
    print("  ")
    print("  # Tab management")
    print("  browser.open_new_tab('https://github.com')")
    print("  browser.switch_to_tab(0)  # Back to first tab")
    print("  ")
    print("  # Auto-detect selectors")
    print("  browser.click('//button[text()=\"Login\"]')  # XPath")
    print("  browser.type_text('$#username', 'user')      # CSS ID")
    print("  browser.click('$ .submit-btn')               # CSS Class")
    print("  ")
    print("  # Element finding")
    print("  browser.select_option_by_text('#country', 'Korea')  # Dropdown")
    print("  ")
    print("  # Clean up")
    print("  browser.quit()")
    print()

    print("NOTE: Requires WebDriver (ChromeDriver/GeckoDriver) to be installed")


class Browser:
    """
    Base browser automation class with enhanced functionality including tab management.

    Provides network monitoring, element discovery, tab management, and automation utilities
    built on top of pure Selenium WebDriver with auto-detecting selectors.

    Attributes:
        driver: Selenium WebDriver instance for browser automation
        wait: WebDriverWait instance for explicit waits
        window_handles: List of window handles for tab management
    """

    def __init__(
            self,
            private_mode: bool = True,
            mobile_mode: bool = False,
            headless: bool = False,
            window_size: str = "1920,1080",
            window_position: str = "10,10"
    ):
        """
        Initialize browser instance.

        Args:
            private_mode: Enable private/incognito browsing mode
            mobile_mode: Enable mobile device emulation
            headless: Run browser in headless mode
            window_size: Browser window size as "width,height"
            window_position: Browser window position as "x,y"

        Raises:
            ImportError: If required dependencies are not installed
        """
        # Import required dependencies
        self.selenium = _import_selenium_dependencies()

        self._private_mode = private_mode
        self._mobile_mode = mobile_mode
        self._headless = headless
        self._window_size = window_size
        self._window_position = window_position

        # Initialize driver and tab management
        self.driver = None
        self.wait = None
        self.window_handles = []
        self._init_webdriver()

        # Configure timeouts
        self._configure_timeouts()

    def _init_webdriver(self) -> None:
        """Initialize webdriver with specified configuration."""
        raise NotImplementedError("Subclasses must implement _init_webdriver method")

    def _configure_timeouts(self) -> None:
        """Configure browser timeouts."""
        if self.driver:
            self.driver.implicitly_wait(TimeoutConfig.MINI_TIMEOUT)
            self.driver.set_page_load_timeout(TimeoutConfig.PAGE_LOAD_TIMEOUT)
            self.wait = self.selenium['WebDriverWait'](self.driver, TimeoutConfig.SMALL_TIMEOUT)

            # Initialize window handles list
            try:
                self.window_handles = [self.driver.current_window_handle]
            except self.selenium['WebDriverException']:
                self.window_handles = []

    def _parse_selector(self, selector: str, by: Optional[str] = None) -> tuple:
        """
        Parse selector and determine the appropriate By strategy.

        Auto-detects selector type based on SeleniumBase conventions:
        - Starts with '//' → XPath
        - Starts with '$' → CSS Selector
        - Otherwise → Use explicit 'by' parameter or default to CSS

        Args:
            selector: The selector string
            by: Explicit selector type ('css', 'xpath', or None for auto-detect)

        Returns:
            Tuple of (By strategy, cleaned selector)

        Raises:
            ValueError: If selector is empty or by parameter is invalid
        """
        if not selector:
            raise ValueError("Selector cannot be empty")

        # Auto-detect based on selector prefix
        if selector.startswith('//'):
            return (self.selenium['By'].XPATH, selector)
        elif selector.startswith('$'):
            # Remove $ prefix and handle space after $ for class selectors
            cleaned_selector = selector[1:].lstrip()
            return (self.selenium['By'].CSS_SELECTOR, cleaned_selector)

        # Fall back to explicit 'by' parameter
        if by is None:
            by = "css"  # Default to CSS

        if by.lower() == "css":
            return (self.selenium['By'].CSS_SELECTOR, selector)
        elif by.lower() == "xpath":
            return (self.selenium['By'].XPATH, selector)
        else:
            raise ValueError("by parameter must be 'css' or 'xpath'")

    def open(
            self,
            url: str,
            safe_timeout: bool = False,
            timeout: Optional[int] = None,
            wait_for_idle: bool = False,
            idle_time: float = 2.0
    ) -> None:
        """
        Navigate to the specified URL with enhanced timeout handling.

        Args:
            url: URL to navigate to
            safe_timeout: Use shorter timeout for protected environments
            timeout: Custom timeout in seconds (overrides safe_timeout)
            wait_for_idle: Wait for network activity to settle after loading
            idle_time: Time to wait for network idle (seconds)

        Raises:
            RuntimeError: If driver not initialized or page fails to load
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized")

        # Determine timeout to use
        if timeout is not None:
            load_timeout = timeout
        elif safe_timeout:
            load_timeout = TimeoutConfig.SAFE_PAGE_LOAD_TIMEOUT
        else:
            load_timeout = TimeoutConfig.PAGE_LOAD_TIMEOUT

        # Store original timeout to restore later
        original_timeout = self.driver.timeouts.page_load

        try:
            # Set temporary timeout
            self.driver.set_page_load_timeout(load_timeout)

            # Navigate to URL
            self.driver.get(url)

        except self.selenium['TimeoutException'] as e:
            # Check if page is partially loaded and usable
            try:
                ready_state = self.driver.execute_script("return document.readyState")
                current_url = self.driver.current_url

                if (ready_state in ['interactive', 'complete']) and (current_url != 'data:,'):
                    print(f"Page partially loaded but continuing (ready state: {ready_state})")
                else:
                    raise RuntimeError(f"Page failed to load properly: {e}")

            except Exception:
                raise RuntimeError(f"Page loading failed and unable to check status: {e}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error during page loading: {e}")

        finally:
            # Restore original timeout
            try:
                self.driver.set_page_load_timeout(original_timeout)
            except Exception:
                # If restoration fails, set back to default
                self.driver.set_page_load_timeout(TimeoutConfig.PAGE_LOAD_TIMEOUT)

        # Optional network idle wait
        if wait_for_idle:
            self.wait_for_network_idle(idle_time)

    def wait_for_network_idle(self, idle_time: float = 2.0, timeout: int = 30) -> bool:
        """
        Wait for network activity to settle by monitoring JavaScript activity.

        This method checks for jQuery activity and document ready state,
        then waits for a period of network inactivity.

        Args:
            idle_time: Time in seconds to wait for network to be idle
            timeout: Maximum time to wait for network to become idle

        Returns:
            True if network became idle within timeout, False otherwise
        """
        if not self.driver:
            return False

        end_time = time.time() + timeout

        try:
            # First wait for basic document ready state
            self.wait_for_ready_state_complete(timeout=min(10, timeout))

            # Then wait for jQuery if present
            if time.time() < end_time:
                remaining_timeout = int(end_time - time.time())
                self.wait_for_ajax(timeout=min(remaining_timeout, 10))

            # Finally wait for idle period
            last_activity_time = time.time()

            while time.time() < end_time:
                current_time = time.time()

                # Check if we've been idle long enough
                if (current_time - last_activity_time) >= idle_time:
                    return True

                # Check for ongoing network activity (simplified check)
                try:
                    # Check if any new script tags or resources are being added
                    script_count = self.driver.execute_script(
                        "return document.getElementsByTagName('script').length"
                    )

                    # Simple heuristic: if script count changes, reset idle timer
                    if not hasattr(self, '_last_script_count'):
                        self._last_script_count = script_count
                    elif script_count != self._last_script_count:
                        last_activity_time = current_time
                        self._last_script_count = script_count

                except Exception:
                    # If we can't check, assume activity has stopped
                    pass

                time.sleep(0.5)  # Check every 500ms

            return False  # Timeout reached

        except Exception:
            return False

    def wait_for_element(
            self,
            selector: str,
            by: Optional[str] = None,
            timeout: Optional[int] = None,
            condition: str = 'visibility'
    ):
        """
        Wait for element to be present and meet the specified condition.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            by: Explicit selection method ('css' or 'xpath', optional)
            timeout: Custom timeout in seconds
            condition: Wait condition ('visibility', 'presence', 'clickable')

        Returns:
            WebElement when found

        Raises:
            TimeoutException: If element not found within timeout
            ValueError: If invalid condition specified
        """
        wait_timeout = timeout or TimeoutConfig.SMALL_TIMEOUT
        wait = self.selenium['WebDriverWait'](self.driver, wait_timeout)

        (by_strategy, cleaned_selector) = self._parse_selector(selector, by)
        locator = (by_strategy, cleaned_selector)

        # Select appropriate expected condition
        if condition == 'visibility':
            wait_condition = self.selenium['EC'].visibility_of_element_located(locator)
        elif condition == 'presence':
            wait_condition = self.selenium['EC'].presence_of_element_located(locator)
        elif condition == 'clickable':
            wait_condition = self.selenium['EC'].element_to_be_clickable(locator)
        else:
            raise ValueError(f"Invalid condition: {condition}. Must be 'visibility', 'presence', or 'clickable'")

        return wait.until(wait_condition)

    def find_element(
            self,
            selector: str,
            by: Optional[str] = None,
            wait_if_needed: bool = True,
            timeout: int = 10
    ):
        """
        Find a single element with gradual approach.

        Implements fail-fast + gradual fallback pattern:
        1. Try immediate find (fast path for static content)
        2. If not found and wait_if_needed=True, wait for element (safe path for dynamic content)

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            by: Explicit selection method ('css' or 'xpath', optional)
            wait_if_needed: Enable gradual fallback with waiting
            timeout: Timeout for waiting phase

        Returns:
            WebElement if found

        Raises:
            NoSuchElementException: If element not found
            ValueError: If selector is invalid
        """
        (by_strategy, cleaned_selector) = self._parse_selector(selector, by)

        try:
            # Fast path: immediate find for static content
            return self.driver.find_element(by_strategy, cleaned_selector)
        except self.selenium['NoSuchElementException']:
            if wait_if_needed:
                # Fallback: use wait_for_element for dynamic content
                try:
                    return self.wait_for_element(selector, by, timeout, condition='presence')
                except self.selenium['TimeoutException']:
                    raise self.selenium['NoSuchElementException'](
                        f"Element not found after waiting {timeout}s: {selector}"
                    )
            else:
                raise

    def find_elements(self, selector: str, by: Optional[str] = None):
        """
        Find multiple elements using auto-detected or explicit selector type.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            by: Explicit selection method ('css' or 'xpath', optional)

        Returns:
            List of WebElements
        """
        (by_strategy, cleaned_selector) = self._parse_selector(selector, by)
        return self.driver.find_elements(by_strategy, cleaned_selector)

    def select_option_by_text(
            self,
            dropdown_selector: str,
            option_text: str,
            by: Optional[str] = None,
            max_retries: int = 2,
            retry_delay: float = 0.5
    ) -> None:
        """
        Select dropdown option by visible text with retry logic.

        Args:
            dropdown_selector: Selector for the <select> element
            option_text: Visible text of the option to select
            by: Explicit selection method ('css' or 'xpath', optional)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Raises:
            RuntimeError: If selection fails after all retries
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Find element (with or without waiting based on attempt)
                element = self.find_element(
                    dropdown_selector,
                    by,
                    wait_if_needed=(attempt > 0)  # Use waiting on retries
                )

                # Try to select option
                self.selenium['Select'](element).select_by_visible_text(option_text)
                return  # Success

            except (self.selenium['StaleElementReferenceException'],
                    self.selenium['ElementNotInteractableException']) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except Exception as e:
                # For other exceptions, fail immediately
                raise RuntimeError(
                    f"Failed to select option '{option_text}' from dropdown '{dropdown_selector}': {e}"
                )

        # If we get here, all retries failed
        raise RuntimeError(
            f"Failed to select option '{option_text}' after {max_retries} attempts. "
            f"Last error: {last_exception}"
        )

    def wait_for_ready_state_complete(self, timeout: Optional[int] = None) -> None:
        """
        Wait for page to reach ready state complete.

        Args:
            timeout: Maximum time to wait in seconds
        """
        wait_timeout = timeout or TimeoutConfig.SMALL_TIMEOUT
        wait = self.selenium['WebDriverWait'](self.driver, wait_timeout)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    def wait_for_ajax(self, timeout: int = 20) -> None:
        """
        Wait for AJAX requests to complete.

        Args:
            timeout: Maximum time to wait in seconds
        """
        wait = self.selenium['WebDriverWait'](self.driver, timeout)
        wait.until(
            lambda drv: drv.execute_script(
                "return window.jQuery ? jQuery.active == 0 : true"
            )
        )

    def click(self, selector: str, by: Optional[str] = None, timeout: int = 10) -> None:
        """
        Click on element identified by selector.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            by: Explicit selection method ('css' or 'xpath', optional)
            timeout: Timeout for element finding
        """
        element = self.wait_for_element(selector, by, timeout, condition='clickable')
        element.click()

    def type_text(self, selector: str, text: str, by: Optional[str] = None, timeout: int = 10) -> None:
        """
        Type text into element identified by selector.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            text: Text to type
            by: Explicit selection method ('css' or 'xpath', optional)
            timeout: Timeout for element finding
        """
        element = self.wait_for_element(selector, by, timeout, condition='visibility')
        element.clear()
        element.send_keys(text)

    def quit(self) -> None:
        """Clean up and quit the browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.window_handles.clear()

    # ==================== TAB MANAGEMENT ====================

    def get_current_handle(self) -> Optional[str]:
        """Get current window handle."""
        if not self.driver:
            return None
        try:
            return self.driver.current_window_handle
        except self.selenium['WebDriverException']:
            return None

    def get_all_handles(self) -> List[str]:
        """Get all window handles."""
        if not self.driver:
            return []
        try:
            return self.driver.window_handles
        except self.selenium['WebDriverException']:
            return []

    def switch_to_window(self, handle: str) -> bool:
        """
        Switch to window by handle.

        Args:
            handle: Window handle to switch to

        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            return False
        try:
            self.driver.switch_to.window(handle)
            return True
        except self.selenium['WebDriverException']:
            return False

    def open_new_tab(self, url: Optional[str] = None, safe_timeout: bool = False) -> bool:
        """
        Open new tab and optionally navigate to URL.

        Args:
            url: Optional URL to open in new tab
            safe_timeout: Use safe timeout for page loading

        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            return False
        try:
            self.driver.switch_to.new_window('tab')
            new_handle = self.driver.current_window_handle
            self.window_handles.append(new_handle)

            if url:
                self.open(url, safe_timeout=safe_timeout)
            return True

        except self.selenium['WebDriverException']:
            return False

    def switch_to_tab(self, index: int = -1) -> bool:
        """
        Switch to tab by index.

        Args:
            index: Tab index (-1 for last tab)

        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            return False
        try:
            # Refresh window handles list
            all_handles = self.get_all_handles()
            if all_handles:
                self.window_handles = all_handles

            if -len(self.window_handles) <= index < len(self.window_handles):
                target_handle = self.window_handles[index]
                return self.switch_to_window(target_handle)
            return False

        except (self.selenium['WebDriverException'], IndexError):
            return False

    def get_tab_count(self) -> int:
        """Get current number of tabs."""
        return len(self.get_all_handles())

    def close_current_tab(self) -> bool:
        """
        Close current tab and switch to previous tab.

        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            return False
        try:
            if self.get_tab_count() <= 1:
                return False  # Don't close last tab

            current_handle = self.get_current_handle()
            self.driver.close()

            # Remove closed handle from our list
            if current_handle in self.window_handles:
                self.window_handles.remove(current_handle)

            # Switch to remaining tab
            remaining_handles = self.get_all_handles()
            if remaining_handles:
                return self.switch_to_window(remaining_handles[-1])
            return False

        except self.selenium['WebDriverException']:
            return False

    # ==================== NETWORK MONITORING ====================

    def inject_network_capture(self) -> None:
        """
        Inject JavaScript to capture fetch/XHR network requests.

        Creates a global __selenium_logs array that stores network request details
        including URL, status, method, request body, and response.
        """
        inject_script = """
        window.__selenium_logs = [];
        (function() {
          const origFetch = window.fetch;
          window.fetch = function(...args) {
            return origFetch(...args).then(res => {
              const clone = res.clone();
              clone.text().then(body => {
                window.__selenium_logs.push({
                  type: 'fetch', url: clone.url,
                  status: clone.status,
                  method: args[1]?.method||'GET',
                  request: args[1]?.body||null,
                  response: body
                });
              });
              return res;
            });
          };

          const _open = XMLHttpRequest.prototype.open;
          XMLHttpRequest.prototype.open = function(m,u) {
            this._m=m; this._u=u; return _open.apply(this, arguments);
          };

          const _send = XMLHttpRequest.prototype.send;
          XMLHttpRequest.prototype.send = function(b) {
            this.addEventListener('load', () => {
              window.__selenium_logs.push({
                type: 'xhr', url: this._u,
                status: this.status, method: this._m,
                request: b||null, response: this.responseText
              });
            });
            return _send.apply(this, arguments);
          };
        })();
        """

        self.driver.execute_script(inject_script)
        print('Network capture script injected successfully.')

    def get_network_logs(self) -> List[Dict[str, Any]]:
        """
        Retrieve captured network requests.

        Returns:
            List of network request dictionaries containing type, URL, status,
            method, request body, and response data.
        """
        # Ensure page is fully loaded before retrieving logs
        self.wait_for_ready_state_complete()
        self.wait_for_ajax()
        time.sleep(1.0)

        logs = self.driver.execute_script("return window.__selenium_logs;")
        return logs or []

    # ==================== UTILITY METHODS ====================

    @staticmethod
    def extract_url_parameters(
            url: str,
            param: str,
            split_char: str = ''
    ) -> List[List[str]]:
        """
        Extract parameter values from URL query string.

        Args:
            url: URL to parse
            param: Parameter name to extract ('get_all' returns all parameters)
            split_char: Character to split parameter values on

        Returns:
            List of parameter value lists
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        if param == 'get_all':
            return query_params

        parsed_params = query_params.get(param, [''])
        param_count = len(parsed_params)

        if param_count > 1:
            if split_char:
                return [value.split(split_char) for value in parsed_params]
            else:
                return [[value] for value in parsed_params]
        elif param_count == 1:
            value = parsed_params[0]
            return [value.split(split_char)] if split_char else [[value]]
        else:
            return []

    def find_element_info(self, selector: str, concat_text: bool = False) -> None:
        """
        Find and display information about elements matching the selector.

        Args:
            selector: CSS, XPath selector, or auto-detected (XPath: //, CSS: $)
            concat_text: If True, concatenate element text; if False, show detailed info
        """
        elements = self.find_elements(selector)

        if not elements:
            print(f'No elements found with selector: {selector}')
            return

        for element in elements:
            try:
                if not concat_text:
                    print(f'outerHTML: {element.get_attribute("outerHTML")}')
                    print(f'class: {element.get_attribute("class")}')
                    print(f'value: {element.get_attribute("value")}')
                    print(f'text: {element.text.strip()}', end='\n\n')
                else:
                    print(f"'{element.text.strip()}'", end=', ')
            except Exception:
                if not concat_text:
                    print("Error getting element info")
                else:
                    print("'[error]'", end=', ')

    @staticmethod
    def generate_text_selectors(
            texts: List[str],
            element_type: str,
    ) -> List[str]:
        """
        Generate XPath selectors for elements containing specific text.

        Args:
            texts: List of text content to match
            element_type: HTML element type (e.g., 'a', 'span', 'button')

        Returns:
            List of XPath selectors

        Example:
            generate_text_selectors(['Home', 'About'], 'a')
            # Returns: ["//a[normalize-space(.)='Home']", "//a[normalize-space(.)='About']"]
        """
        return [f"//{element_type}[normalize-space(.)='{text}']" for text in texts]

    def find_common_attribute(
            self,
            selectors: List[str],
            attribute: str,
            verbose: bool = False
    ) -> str:
        """
        Find the most common attribute value among elements matched by selectors.

        This method helps discover common patterns in element attributes,
        useful for building robust selectors when class names might change.

        Args:
            selectors: List of CSS, XPath, or auto-detected selectors
            attribute: Attribute name to analyze (e.g., 'class', 'id')
            verbose: Print detailed information if True

        Returns:
            Most frequently occurring attribute value

        Example:
            names = ['RaspberryPi', 'BlackBerry', 'Apple']
            selectors = [f"//label[normalize-space(text())='{name}']" for name in names]
            common_class = browser.find_common_attribute(selectors, 'class')
        """
        attribute_counts = {}

        for selector in selectors:
            elements = self.find_elements(selector)
            for element in elements:
                try:
                    attr_value = element.get_attribute(attribute)
                    if attr_value:
                        attribute_counts[attr_value] = attribute_counts.get(attr_value, 0) + 1
                except Exception:
                    continue

        if not attribute_counts:
            return ''

        most_common = max(attribute_counts, key=attribute_counts.get)

        if verbose:
            print(f'Most common {attribute}: {most_common}')
            print(f'Attribute distribution: {attribute_counts}')

        return most_common


class Chrome(Browser):
    """Chrome browser implementation with enhanced configuration options and method chaining."""

    def __init__(
            self,
            private_mode: bool = True,
            mobile_mode: bool = False,
            headless: bool = False,
            window_size: str = "1920,1080",
            window_position: str = "10,10"
    ):
        """
        Initialize Chrome browser with enhanced configuration.

        Args:
            private_mode: Enable private/incognito browsing mode
            mobile_mode: Enable mobile device emulation
            headless: Run browser in headless mode
            window_size: Browser window size as "width,height"
            window_position: Browser window position as "x,y"
        """
        # Initialize options before calling parent
        self.options = None
        super().__init__(private_mode, mobile_mode, headless, window_size, window_position)

    def _init_webdriver(self) -> None:
        """Initialize Chrome webdriver with custom options."""
        self.options = self.selenium['ChromeOptions']()
        self._setup_default_options()

        # Initialize driver
        try:
            self.driver = self.selenium['webdriver'].Chrome(options=self.options)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Chrome driver: {e}\n"
                "Make sure ChromeDriver is installed and in PATH"
            )

    def _setup_default_options(self) -> None:
        """Setup safe default Chrome options."""
        # Basic options
        if self._headless:
            self.options.add_argument('--headless')

        if self._private_mode:
            self.options.add_argument('--incognito')

        # Safe performance and stability options
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-plugins')
        self.options.add_argument('--disable-images')

        # Mobile emulation
        if self._mobile_mode:
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }
            self.options.add_experimental_option("mobileEmulation", mobile_emulation)

        # Window size and position
        if not self._mobile_mode:
            width, height = self._window_size.split(',')
            self.options.add_argument(f'--window-size={width},{height}')

            x, y = self._window_position.split(',')
            self.options.add_argument(f'--window-position={x},{y}')

    # ==================== METHOD CHAINING CONFIGURATION ====================

    def add_argument(self, argument: str) -> 'Chrome':
        """
        Add Chrome argument with method chaining.

        Args:
            argument: Chrome command line argument

        Returns:
            Self for method chaining
        """
        if self.options:
            self.options.add_argument(argument)
        return self

    def add_experimental_option(self, name: str, value: Any) -> 'Chrome':
        """
        Add Chrome experimental option.

        Args:
            name: Option name
            value: Option value

        Returns:
            Self for method chaining
        """
        if self.options:
            self.options.add_experimental_option(name, value)
        return self

    def configure_new_window(self) -> 'Chrome':
        """Configure Chrome to start with new window."""
        return self.add_argument('--new-window')

    def configure_proxy_pac(self, pac_url: str) -> 'Chrome':
        """
        Configure PAC-based proxy.

        Args:
            pac_url: PAC file URL
        """
        return self.add_argument(f'--proxy-pac-url={pac_url}')

    def configure_detach(self) -> 'Chrome':
        """Configure Chrome to stay open after script ends."""
        return self.add_experimental_option('detach', True)

    def configure_no_automation(self) -> 'Chrome':
        """Disable automation indicators."""
        return (self.add_experimental_option('excludeSwitches', ['enable-automation'])
                .add_experimental_option('useAutomationExtension', False))


class Firefox(Browser):
    """Firefox browser implementation with profile management and private browsing."""

    def _init_webdriver(self) -> None:
        """
        Initialize Firefox webdriver with profile detection and private browsing.
        """
        options = self.selenium['FirefoxOptions']()

        # Basic options
        if self._headless:
            options.add_argument('--headless')

        # Profile configuration
        profile_path = self._find_firefox_profile()
        if profile_path:
            options.add_argument(f'-profile')
            options.add_argument(profile_path)

        # Private browsing
        if self._private_mode:
            options.add_argument('-private')
            options.set_preference('browser.privatebrowsing.autostart', True)

        # Safe performance preferences (keeping security features enabled)
        options.set_preference('network.proxy.type', 0)  # No proxy
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)

        # Mobile emulation for Firefox (basic user agent change)
        if self._mobile_mode:
            mobile_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            options.set_preference("general.useragent.override", mobile_user_agent)

        # Initialize driver
        try:
            self.driver = self.selenium['webdriver'].Firefox(options=options)

            # Set window size and position after initialization
            if not self._mobile_mode:
                width, height = map(int, self._window_size.split(','))
                x, y = map(int, self._window_position.split(','))

                self.driver.set_window_size(width, height)
                self.driver.set_window_position(x, y)

        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Firefox driver: {e}\n"
                "Make sure GeckoDriver is installed and in PATH"
            )

    @staticmethod
    def _find_firefox_profile() -> Optional[str]:
        """
        Find Firefox default profile path across different operating systems.

        Returns:
            Path to Firefox profile directory or None if not found
        """
        try:
            if sys.platform == "darwin":  # macOS
                profile_dir = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/")
            elif sys.platform == "win32":  # Windows
                profile_dir = os.path.expanduser("~/AppData/Roaming/Mozilla/Firefox/Profiles/")
            else:  # Linux and other Unix-like systems
                profile_dir = os.path.expanduser("~/.mozilla/firefox/")

            if os.path.exists(profile_dir):
                profiles = [
                    d for d in os.listdir(profile_dir)
                    if d.endswith('.default-release')
                ]
                if profiles:
                    return os.path.join(profile_dir, profiles[0])
        except Exception:
            # Silently fail if profile detection fails
            pass
        return None


# Example usage demonstrating the enhanced functionality
if __name__ == '__main__':
    print("qufe.wbhandler Example Usage with Improved Implementation")
    print("=" * 60)

    # Example with Chrome and method chaining
    chrome = Chrome()

    try:
        print("Configuring Chrome with secure defaults...")
        chrome.configure_new_window().configure_no_automation().configure_detach()

        print("\nOpening first page with safe timeout...")
        chrome.open("https://httpbin.org/get", safe_timeout=True)

        # Inject network capture
        chrome.inject_network_capture()
        print("✓ Network capture injected")

        # Wait for network to settle
        if chrome.wait_for_network_idle(idle_time=2.0):
            print("✓ Network activity settled")
        else:
            print("⚠ Network timeout, but continuing...")

        # Demonstrate improved element finding
        print("\nDemonstrating improved element finding...")

        # Example 1: Static content (fast path)
        try:
            element = chrome.find_element("body", wait_if_needed=False)
            print("✓ Static element found immediately (fast path)")
        except Exception as e:
            print(f"✗ Static element failed: {e}")

        # Example 2: Dynamic content with fallback
        try:
            # This will use fast path first, then fallback if needed
            element = chrome.find_element("//body", wait_if_needed=True, timeout=5)
            print("✓ Element found with fallback available")
        except Exception as e:
            print(f"✗ Element finding failed: {e}")

        # Demonstrate tab management
        print(f"\nCurrent tab count: {chrome.get_tab_count()}")

        print("Opening new tab with safe timeout...")
        if chrome.open_new_tab("https://httpbin.org/html", safe_timeout=True):
            print("✓ New tab opened")

        print(f"Updated tab count: {chrome.get_tab_count()}")

        # Switch between tabs
        print("Switching to first tab...")
        if chrome.switch_to_tab(0):
            print("✓ Switched to first tab")

        # Demonstrate improved dropdown selection
        try:
            # This would work if there was a select element on the page
            # chrome.select_option_by_text("#country", "Korea", max_retries=3)
            print("✓ Dropdown selection method available with retry logic")
        except Exception:
            print("⚠ No dropdown to test, but method is implemented")

        # Demonstrate URL parameter extraction
        test_url = "https://example.com?param1=value1&param2=value2,value3"
        params = Chrome.extract_url_parameters(test_url, 'param2', ',')
        print(f"Extracted params: {params}")

        print("\nSession completed successfully")

    except KeyboardInterrupt:
        print("\nSession interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up...")
        chrome.quit()
        print("Session ended")
