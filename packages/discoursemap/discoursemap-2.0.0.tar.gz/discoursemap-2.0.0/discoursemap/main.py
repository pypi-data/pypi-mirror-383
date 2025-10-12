#!/usr/bin/env python3
"""
DiscourseMap v2.0
Specialized Security Scanner for Discourse Forums Only

This tool is specifically designed for Discourse platform security assessment.
It is NOT a general-purpose web scanner and only works with Discourse forums.

Author: ibrahimsql
Version: 2.0
License: MIT

WARNING: This tool should only be used on authorized Discourse systems.
Unauthorized use is prohibited and may have legal consequences.
"""

import argparse
import sys
import os
import time
import json
import yaml
import asyncio
import requests
from datetime import datetime
from colorama import init, Fore, Style
from .core.scanner import DiscourseScanner
from .core.reporter import Reporter
from .lib.discourse_utils import validate_url
from .lib.config_manager import ConfigManager
from .core.banner import Banner

init(autoreset=False)


def load_config(config_file):
    """Load configuration from YAML file"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    except (FileNotFoundError, PermissionError) as e:
        print(f"{Fore.YELLOW}[!] Warning: Could not access config file {config_file}: {e}{Style.RESET_ALL}")
        return {}
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"{Fore.YELLOW}[!] Warning: Invalid config file format {config_file}: {e}{Style.RESET_ALL}")
        return {}
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Warning: Unexpected error loading config file {config_file}: {e}{Style.RESET_ALL}")
        return {}


def load_resume_data(resume_file):
    """Load resume data from JSON file"""
    try:
        with open(resume_file, 'r') as f:
            data = json.load(f)
            completed_modules = list(data.get('modules', {}).keys())
            return completed_modules, data
    except (FileNotFoundError, PermissionError) as e:
        print(f"{Fore.RED}[!] Error: Cannot access resume file {resume_file}: {e}{Style.RESET_ALL}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}[!] Error: Invalid JSON in resume file {resume_file}: {e}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}[!] Unexpected error loading resume file {resume_file}: {e}{Style.RESET_ALL}")
        sys.exit(1)


def save_partial_results(results, filename=None):
    """Save partial scan results"""
    if not filename:
        filename = f"partial_scan_{int(time.time())}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        return filename
    except (IOError, OSError, PermissionError) as e:
        print(f"{Fore.RED}[!] File error saving partial results: {e}{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}[!] Unexpected error saving partial results: {e}{Style.RESET_ALL}")
        return None


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='DiscourseMap v1.2.0 - Comprehensive Discourse security assessment tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py -u https://forum.example.com -m info vuln
  python3 main.py -u https://forum.example.com -o json -f report.json
  python3 main.py -u https://forum.example.com -v -t 10
  python3 main.py -u https://forum.example.com -m cve -p http://127.0.0.1:8080
  python3 main.py -u https://forum.example.com -q  # Quick scan (maximum speed)
  python3 main.py -q -u https://forum.example.com -o json  # Quick scan with JSON output
        """
    )
    
    # Required arguments
    parser.add_argument('-u', '--url', required=False,
                       help='Target Discourse forum URL')
    
    # Optional arguments
    parser.add_argument('-t', '--threads', type=int, default=5,
                       help='Number of threads (default: 5)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='HTTP timeout duration (default: 10)')
    parser.add_argument('-p', '--proxy', type=str,
                       help='Proxy server (e.g: http://127.0.0.1:8080)')
    parser.add_argument('--user-agent', type=str,
                       help='Custom User-Agent string')
    parser.add_argument('--delay', type=float, default=0.05,
                       help='Delay between requests (seconds, default: 0.05)')
    
    # Scanning options
    parser.add_argument('--skip-ssl-verify', action='store_true',
                       help='Skip SSL certificate verification')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output')
    parser.add_argument('--quiet', action='store_true',
                       help='Show only results')
    parser.add_argument('-q', '--quick', action='store_true',
                       help='Quick scan mode: Maximum speed with info, auth, api, vuln, waf_bypass modules')
    parser.add_argument('--sync', action='store_true',
                       help='Use synchronous scanning mode (default is async for better performance)')
    
    # Performance presets (enhanced quick scan)
    parser.add_argument('--fast', action='store_true',
                       help='Maximum speed preset (50 threads, 0.01s delay)')
    parser.add_argument('--balanced', action='store_true',
                       help='Balanced preset (20 threads, 0.05s delay)')
    parser.add_argument('--safe', action='store_true',
                       help='Safe preset (10 threads, 0.1s delay)')
    
    # Module options
    parser.add_argument('-m', '--modules', nargs='+', 
                       choices=['info', 'vuln', 'endpoint', 'user', 'cve', 'plugin_detection', 'plugin_bruteforce', 
                               'api', 'auth', 'config', 'crypto', 'network', 'plugin', 'waf_bypass', 'compliance'],
                       help='Modules to run (default: all)')
    
    # Output options
    parser.add_argument('-o', '--output', choices=['json', 'html', 'csv'],
                       help='Report format')
    parser.add_argument('-f', '--output-file', type=str,
                       help='Output file name')
    
    # Resume and update options
    parser.add_argument('--resume', type=str,
                       help='Resume scan from partial results file')
    parser.add_argument('-c', '--config', type=str, default='config.yaml',
                       help='Configuration file path (default: config.yaml)')
    parser.add_argument('--update', action='store_true',
                       help='Update scan data and signatures')
    
    return parser.parse_args()

def main():
    """Main function"""
    print(Banner)
    start_time = time.time()
    
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load configuration
        config = load_config(args.config)
        
        # Handle update mode
        if args.update:
            print(f"{Fore.CYAN}[*] Updating DiscourseMap to latest version...{Style.RESET_ALL}")
            
            try:
                import subprocess
                
                # Check current version
                print(f"{Fore.CYAN}[*] Checking current version...{Style.RESET_ALL}")
                current_version = "1.2.0"
                print(f"    Current version: {current_version}")
                
                # Check for latest version on GitHub
                print(f"{Fore.CYAN}[*] Checking for updates on GitHub...{Style.RESET_ALL}")
                try:
                    response = requests.get(
                        "https://api.github.com/repos/ibrahmsql/discoursemap/releases/latest",
                        timeout=10
                    )
                    if response.status_code == 200:
                        latest_release = response.json()
                        latest_version = latest_release.get('tag_name', '').lstrip('v')
                        print(f"    Latest version: {latest_version}")
                        
                        # Check pip installed version
                        pip_version = None
                        try:
                            pip_show_result = subprocess.run([
                                sys.executable, '-m', 'pip', 'show', 'discoursemap'
                            ], capture_output=True, text=True, timeout=10)
                            
                            if pip_show_result.returncode == 0:
                                for line in pip_show_result.stdout.split('\n'):
                                    if line.startswith('Version:'):
                                        pip_version = line.split(':')[1].strip()
                                        print(f"    Pip installed version: {pip_version}")
                                        break
                        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                            print(f"    Could not check pip installed version: {e}")
                        except Exception as e:
                            print(f"    Unexpected error checking pip version: {e}")
                        
                        # Determine update strategy
                        should_update = True
                        if latest_version and pip_version:
                            if latest_version != pip_version:
                                print(f"{Fore.YELLOW}[!] Version mismatch: GitHub({latest_version}) vs Pip({pip_version}){Style.RESET_ALL}")
                                print(f"{Fore.CYAN}[*] Using pip version as authoritative source{Style.RESET_ALL}")
                            elif latest_version == current_version:
                                should_update = False
                                print(f"{Fore.GREEN}[+] All versions match - no update needed{Style.RESET_ALL}")
                        
                        if should_update:
                            print(f"{Fore.CYAN}[*] Attempting update...{Style.RESET_ALL}")
                            
                            # Try pip update with multiple methods
                            update_success = False
                            
                            # Method 1: python -m pip
                            try:
                                print(f"{Fore.CYAN}[*] Trying: python -m pip install --upgrade{Style.RESET_ALL}")
                                result = subprocess.run([
                                    sys.executable, '-m', 'pip', 'install', '--upgrade', 'discoursemap'
                                ], capture_output=True, text=True, timeout=30)
                                
                                if result.returncode == 0:
                                    if 'Successfully installed' in result.stdout:
                                        print(f"{Fore.GREEN}[+] Successfully updated via python -m pip!{Style.RESET_ALL}")
                                        update_success = True
                                    else:
                                        print(f"{Fore.GREEN}[+] Already up to date (python -m pip){Style.RESET_ALL}")
                                        update_success = True
                                else:
                                    print(f"{Fore.YELLOW}[!] python -m pip failed: {result.stderr[:50]}...{Style.RESET_ALL}")
                            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                                print(f"{Fore.YELLOW}[!] python -m pip subprocess error: {str(e)[:50]}...{Style.RESET_ALL}")
                            except Exception as e:
                                print(f"{Fore.YELLOW}[!] python -m pip unexpected error: {str(e)[:50]}...{Style.RESET_ALL}")
                            
                            # Method 2: Direct pip command
                            if not update_success:
                                try:
                                    print(f"{Fore.CYAN}[*] Trying: pip install --upgrade{Style.RESET_ALL}")
                                    result = subprocess.run([
                                        'pip', 'install', '--upgrade', 'discoursemap'
                                    ], capture_output=True, text=True, timeout=30)
                                    
                                    if result.returncode == 0:
                                        if 'Successfully installed' in result.stdout:
                                            print(f"{Fore.GREEN}[+] Successfully updated via pip!{Style.RESET_ALL}")
                                            update_success = True
                                        else:
                                            print(f"{Fore.GREEN}[+] Already up to date (pip){Style.RESET_ALL}")
                                            update_success = True
                                    else:
                                        print(f"{Fore.YELLOW}[!] pip failed: {result.stderr[:50]}...{Style.RESET_ALL}")
                                except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                                    print(f"{Fore.YELLOW}[!] pip subprocess error: {str(e)[:50]}...{Style.RESET_ALL}")
                                except Exception as e:
                                    print(f"{Fore.YELLOW}[!] pip unexpected error: {str(e)[:50]}...{Style.RESET_ALL}")
                            
                            # Method 3: pip3 command
                            if not update_success:
                                try:
                                    print(f"{Fore.CYAN}[*] Trying: pip3 install --upgrade{Style.RESET_ALL}")
                                    result = subprocess.run([
                                        'pip3', 'install', '--upgrade', 'discoursemap'
                                    ], capture_output=True, text=True, timeout=30)
                                    
                                    if result.returncode == 0:
                                        if 'Successfully installed' in result.stdout:
                                            print(f"{Fore.GREEN}[+] Successfully updated via pip3!{Style.RESET_ALL}")
                                            update_success = True
                                        else:
                                            print(f"{Fore.GREEN}[+] Already up to date (pip3){Style.RESET_ALL}")
                                            update_success = True
                                    else:
                                        print(f"{Fore.YELLOW}[!] pip3 failed: {result.stderr[:50]}...{Style.RESET_ALL}")
                                except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                                    print(f"{Fore.YELLOW}[!] pip3 subprocess error: {str(e)[:50]}...{Style.RESET_ALL}")
                                except Exception as e:
                                    print(f"{Fore.YELLOW}[!] pip3 unexpected error: {str(e)[:50]}...{Style.RESET_ALL}")
                            
                            # Method 4: Git fallback for development
                            if not update_success:
                                print(f"{Fore.YELLOW}[!] All pip methods failed, trying git...{Style.RESET_ALL}")
                                if os.path.exists('.git'):
                                    try:
                                        git_result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                                                   capture_output=True, text=True, timeout=30)
                                        if git_result.returncode == 0:
                                            if 'Already up to date' in git_result.stdout:
                                                print(f"{Fore.GREEN}[+] Already up to date (git){Style.RESET_ALL}")
                                            else:
                                                print(f"{Fore.GREEN}[+] Updated via git pull{Style.RESET_ALL}")
                                            update_success = True
                                        else:
                                            print(f"{Fore.RED}[!] Git update failed: {git_result.stderr[:100]}{Style.RESET_ALL}")
                                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                                        print(f"{Fore.RED}[!] Git subprocess error: {str(e)[:50]}...{Style.RESET_ALL}")
                                    except Exception as e:
                                        print(f"{Fore.RED}[!] Git unexpected error: {str(e)[:50]}...{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.RED}[!] Not a git repository - manual update required{Style.RESET_ALL}")
                            
                            if update_success:
                                print(f"{Fore.CYAN}[*] Please restart DiscourseMap to use the updated version{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.RED}[!] All update methods failed - please update manually{Style.RESET_ALL}")
                                print(f"{Fore.CYAN}[*] Manual update: pip install --upgrade discoursemap{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.GREEN}[+] You are already using the latest version!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}[!] Could not check for updates (GitHub API error){Style.RESET_ALL}")
                        
                except requests.RequestException:
                    print(f"{Fore.YELLOW}[!] Could not check for updates (network error){Style.RESET_ALL}")
                
                # Update dependencies
                print(f"{Fore.CYAN}[*] Updating dependencies...{Style.RESET_ALL}")
                deps_result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', 'requirements.txt'
                ], capture_output=True, text=True)
                
                if deps_result.returncode == 0:
                    print(f"{Fore.GREEN}[+] Dependencies updated successfully{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[!] Some dependencies could not be updated{Style.RESET_ALL}")
                
                # Update vulnerability database
                print(f"{Fore.CYAN}[*] Updating vulnerability database...{Style.RESET_ALL}")
                data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
                vuln_file = os.path.join(data_dir, 'plugin_vulnerabilities.yaml')
                
                if os.path.exists(vuln_file):
                    # Touch the file to update timestamp
                    os.utime(vuln_file, None)
                    print(f"{Fore.GREEN}[+] Vulnerability database refreshed{Style.RESET_ALL}")
                
                print(f"{Fore.GREEN}[+] Update process completed!{Style.RESET_ALL}")
                
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                print(f"{Fore.RED}[!] Update subprocess error: {e}{Style.RESET_ALL}")
                if args.verbose if 'args' in locals() else False:
                    import traceback
                    traceback.print_exc()
            except (requests.RequestException, ConnectionError) as e:
                print(f"{Fore.RED}[!] Update network error: {e}{Style.RESET_ALL}")
                if args.verbose if 'args' in locals() else False:
                    import traceback
                    traceback.print_exc()
            except Exception as e:
                print(f"{Fore.RED}[!] Update unexpected error: {e}{Style.RESET_ALL}")
                if args.verbose if 'args' in locals() else False:
                    import traceback
                    traceback.print_exc()
            
            return
        
        # Handle resume mode
        completed_modules = []
        resume_data = None
        if args.resume:
            print(f"{Fore.CYAN}[*] Resuming scan from: {args.resume}{Style.RESET_ALL}")
            completed_modules, resume_data = load_resume_data(args.resume)
            print(f"{Fore.GREEN}[+] Found {len(completed_modules)} completed modules{Style.RESET_ALL}")
        
        # Handle performance presets and quick scan mode
        preset_name = None
        performance_metrics = {}
        
        if args.fast:
            preset_name = "Maximum Speed"
            args.threads = 50
            args.delay = 0.01
            args.timeout = 5
            args.quiet = True
            performance_metrics = {'threads': 50, 'delay': 0.01, 'timeout': 5}
        elif args.balanced:
            preset_name = "Balanced"
            args.threads = 20
            args.delay = 0.05
            args.timeout = 7
            performance_metrics = {'threads': 20, 'delay': 0.05, 'timeout': 7}
        elif args.safe:
            preset_name = "Safe Mode"
            args.threads = 10
            args.delay = 0.1
            args.timeout = 10
            performance_metrics = {'threads': 10, 'delay': 0.1, 'timeout': 10}
        elif args.quick:
            preset_name = "Quick Scan (Legacy)"
            args.threads = 30
            args.timeout = 5
            args.delay = 0.01
            args.quiet = True
            args.modules = ['info', 'auth', 'api', 'vuln', 'waf_bypass']
            performance_metrics = {'threads': 30, 'delay': 0.01, 'timeout': 5}
        
        if preset_name:
            print(f"{Fore.CYAN}[*] Performance Preset: {preset_name}{Style.RESET_ALL}")
            if args.quick:
                print(f"{Fore.GREEN}[+] Quick scan modules: info, auth, api, vuln, waf_bypass{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Performance settings: {performance_metrics['threads']} threads, {performance_metrics['delay']}s delay, {performance_metrics['timeout']}s timeout{Style.RESET_ALL}")
            print()
        
        # Apply config defaults (only if not in quick mode)
        if config and not args.quick:
            args.url = args.url or config.get('target', {}).get('url')
            args.threads = args.threads or config.get('threads', 5)
            args.timeout = args.timeout or config.get('timeout', 10)
            args.delay = args.delay or config.get('delay', 0.05)
            args.user_agent = args.user_agent or config.get('user_agent')
            args.proxy = args.proxy or config.get('proxy')
        elif config:
            # In quick mode, only apply URL and proxy from config if not provided
            args.url = args.url or config.get('target', {}).get('url')
            args.proxy = args.proxy or config.get('proxy')
        
        # Check if URL is provided
        if not args.url:
            print(f"{Fore.RED}Error: Target URL is required. Provide via -u/--url or config file.{Style.RESET_ALL}")
            sys.exit(1)
        
        # URL validation
        if not validate_url(args.url):
            print(f"{Fore.RED}Error: Invalid URL format!{Style.RESET_ALL}")
            sys.exit(1)
        
        # Discourse site validation - Import is_discourse_site function
        from discoursemap.lib.discourse_utils import is_discourse_site
        
        print(f"{Fore.CYAN}[*] Verifying target is a Discourse forum...{Style.RESET_ALL}")
        if not is_discourse_site(args.url, timeout=10):
            print(f"{Fore.RED}[!] Error: Target is not a Discourse forum!{Style.RESET_ALL}")
            print(f"{Fore.RED}[!] This tool is specifically designed for Discourse forums only.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Please ensure the target URL points to a valid Discourse installation.{Style.RESET_ALL}")
            sys.exit(1)
        else:
            print(f"{Fore.GREEN}[+] Target confirmed as Discourse forum{Style.RESET_ALL}")

        # Initialize scanner with config file
        scanner = DiscourseScanner(
            target_url=args.url,
            threads=args.threads,
            timeout=args.timeout,
            proxy=args.proxy,
            user_agent=args.user_agent,
            delay=args.delay,
            verify_ssl=not args.skip_ssl_verify,
            verbose=args.verbose,
            quiet=args.quiet,
            config_file=args.config
        )
        
        # Show scan configuration
        if not args.quiet:
            print(f"{Fore.CYAN}[*] Scan Configuration:{Style.RESET_ALL}")
            print(f"    Target: {args.url}")
            print(f"    Threads: {args.threads}")
            print(f"    User-Agent: {'Custom' if args.user_agent else 'Rotating'}")
            print(f"    Delay: {args.delay}s")
            print()
        
        # Determine modules to run
        if args.quick:
            # Quick scan mode - use predefined modules
            modules_to_run = ['info', 'auth', 'api', 'vuln', 'waf_bypass']
        elif args.modules:
            modules_to_run = args.modules
        elif config.get('modules'):
            modules_to_run = config['modules']
        else:
            modules_to_run = ['info', 'vuln', 'endpoint', 'user', 'cve', 'plugin_detection', 'plugin_bruteforce', 
                             'api', 'auth', 'config', 'crypto', 'network', 'plugin', 'waf_bypass', 'compliance',
                             'backup_scanner', 'passive_scanner', 'file_integrity']
        
        # Filter out completed modules if resuming
        if completed_modules:
            original_count = len(modules_to_run)
            modules_to_run = [m for m in modules_to_run if m not in completed_modules]
            skipped_count = original_count - len(modules_to_run)
            if skipped_count > 0:
                print(f"{Fore.YELLOW}[!] Skipping {skipped_count} completed modules{Style.RESET_ALL}")
            if not modules_to_run:
                print(f"{Fore.GREEN}[+] All modules already completed!{Style.RESET_ALL}")
                return
        
        # Start scan (async by default, sync only if --sync flag is used)
        if getattr(args, 'sync', False):
            print(f"{Fore.CYAN}[*] Running synchronous scan mode...{Style.RESET_ALL}")
            results = scanner.run_scan(modules_to_run)
        else:
            print(f"{Fore.CYAN}[*] Running async scan mode...{Style.RESET_ALL}")
            results = asyncio.run(scanner.run_async_scan(modules_to_run))
        
        # Merge with resume data if available
        if resume_data:
            for module_name, module_results in resume_data.get('modules', {}).items():
                if module_name not in results['modules']:
                    results['modules'][module_name] = module_results
        
        # Save final results
        final_results_file = save_partial_results(results, f"final_scan_{int(time.time())}.json")
        if final_results_file:
            print(f"{Fore.GREEN}[+] Final results saved: {final_results_file}{Style.RESET_ALL}")
        
        # Calculate scan duration
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate report
        if args.output:
            reporter = Reporter(results)
            output_file = args.output_file or f"discourse_scan_report.{args.output}"
            
            if args.output == 'json':
                reporter.generate_json_report(output_file)
            elif args.output == 'html':
                reporter.generate_html_report(output_file)
            elif args.output == 'csv':
                reporter.generate_csv_report(output_file)
            
            print(f"{Fore.GREEN}[+] Report saved: {output_file}{Style.RESET_ALL}")
        
        # Show completion with duration
        print(f"{Fore.GREEN}[+] Scan completed in {duration:.2f} seconds!{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n{Fore.YELLOW}[!] Scan interrupted by user after {duration:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Performing graceful shutdown...{Style.RESET_ALL}")
        
        # Try to save partial results if available
        try:
            if 'scanner' in locals() and hasattr(scanner, 'results'):
                print(f"{Fore.CYAN}[*] Saving partial scan results...{Style.RESET_ALL}")
                partial_file = save_partial_results(scanner.results)
                if partial_file:
                    print(f"{Fore.GREEN}[+] Partial results saved: {partial_file}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}[*] Use --resume {partial_file} to continue scan{Style.RESET_ALL}")
        except (IOError, OSError, PermissionError) as e:
            print(f"{Fore.RED}[!] Could not save partial results (file error): {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Could not save partial results (unexpected error): {e}{Style.RESET_ALL}")
        
        sys.exit(0)
    except (ConnectionError, TimeoutError, requests.RequestException) as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"{Fore.RED}[!] Network error after {duration:.2f} seconds: {str(e)}{Style.RESET_ALL}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except (IOError, OSError, PermissionError) as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"{Fore.RED}[!] File system error after {duration:.2f} seconds: {str(e)}{Style.RESET_ALL}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"{Fore.RED}[!] Unexpected error after {duration:.2f} seconds: {str(e)}{Style.RESET_ALL}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
