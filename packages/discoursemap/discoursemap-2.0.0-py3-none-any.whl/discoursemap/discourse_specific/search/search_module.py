#!/usr/bin/env python3
"""
Discourse Search Security Module

Tests search functionality for information disclosure, injection, and DoS vulnerabilities.
"""

import requests
from typing import Dict, List, Optional, Any
from colorama import Fore, Style
from urllib.parse import urljoin, quote


class SearchSecurityModule:
    """Search security testing for Discourse"""
    
    def __init__(self, target_url: str, session: Optional[requests.Session] = None,
                 verbose: bool = False):
        """Initialize search security module"""
        self.target_url = target_url.rstrip('/')
        self.session = session or requests.Session()
        self.verbose = verbose
        self.results = {
            'search_endpoints': [],
            'information_disclosure': [],
            'injection_vulnerabilities': [],
            'dos_potential': [],
            'recommendations': []
        }
    
    def scan(self) -> Dict[str, Any]:
        """Perform search security scan"""
        if self.verbose:
            print(f"{Fore.CYAN}[*] Starting search security scan...{Style.RESET_ALL}")
        
        self._test_search_endpoints()
        self._test_search_injection()
        self._test_information_disclosure()
        self._test_dos_vectors()
        self._test_search_filters()
        
        self._generate_recommendations()
        return self.results
    
    def _test_search_endpoints(self):
        """Test search endpoints"""
        if self.verbose:
            print(f"{Fore.YELLOW}[*] Testing search endpoints...{Style.RESET_ALL}")
        
        endpoints = [
            '/search',
            '/search.json',
            '/search/query',
            '/tags/search',
            '/u/search/users'
        ]
        
        for endpoint in endpoints:
            try:
                url = urljoin(self.target_url, endpoint)
                response = self.session.get(url, params={'q': 'test'}, timeout=5)
                
                self.results['search_endpoints'].append({
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200,
                    'response_size': len(response.content)
                })
                
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}[!] Error testing {endpoint}: {e}{Style.RESET_ALL}")
    
    def _test_search_injection(self):
        """Test search injection vulnerabilities"""
        if self.verbose:
            print(f"{Fore.YELLOW}[*] Testing search injection...{Style.RESET_ALL}")
        
        injection_payloads = [
            "' OR '1'='1",
            '" OR "1"="1',
            '<script>alert(1)</script>',
            '${7*7}',
            '{{7*7}}',
            '%27%20OR%20%271%27%3D%271',
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32'
        ]
        
        search_url = urljoin(self.target_url, '/search.json')
        
        for payload in injection_payloads:
            try:
                response = self.session.get(
                    search_url,
                    params={'q': payload},
                    timeout=5
                )
                
                if response.status_code == 500:
                    self.results['injection_vulnerabilities'].append({
                        'payload': payload,
                        'type': 'Server Error',
                        'severity': 'MEDIUM',
                        'status_code': 500
                    })
                elif payload in response.text:
                    self.results['injection_vulnerabilities'].append({
                        'payload': payload,
                        'type': 'Reflected Input',
                        'severity': 'LOW'
                    })
                    
            except Exception:
                pass
    
    def _test_information_disclosure(self):
        """Test for information disclosure via search"""
        if self.verbose:
            print(f"{Fore.YELLOW}[*] Testing information disclosure...{Style.RESET_ALL}")
        
        # Test searching for sensitive information
        sensitive_queries = [
            'password',
            'api_key',
            'secret',
            'token',
            'admin',
            'private',
            'confidential'
        ]
        
        search_url = urljoin(self.target_url, '/search.json')
        
        for query in sensitive_queries:
            try:
                response = self.session.get(
                    search_url,
                    params={'q': query},
                    timeout=5
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        results_count = len(data.get('posts', [])) + len(data.get('topics', []))
                        
                        if results_count > 0:
                            self.results['information_disclosure'].append({
                                'query': query,
                                'results_found': results_count,
                                'severity': 'MEDIUM',
                                'note': 'Sensitive terms found in search results'
                            })
                    except:
                        pass
                        
            except Exception:
                pass
    
    def _test_dos_vectors(self):
        """Test for DoS vectors in search"""
        if self.verbose:
            print(f"{Fore.YELLOW}[*] Testing DoS vectors...{Style.RESET_ALL}")
        
        dos_payloads = [
            '*' * 1000,  # Large wildcard
            'a' * 10000,  # Very long query
            ' OR '.join(['a'] * 100),  # Complex query
            '%' * 100  # Many wildcards
        ]
        
        search_url = urljoin(self.target_url, '/search.json')
        
        for payload in dos_payloads:
            try:
                import time
                start_time = time.time()
                
                response = self.session.get(
                    search_url,
                    params={'q': payload},
                    timeout=10
                )
                
                elapsed_time = time.time() - start_time
                
                if elapsed_time > 5:
                    self.results['dos_potential'].append({
                        'payload_type': 'Slow query',
                        'time_taken': elapsed_time,
                        'severity': 'MEDIUM',
                        'description': 'Search query causes significant delay'
                    })
                    
            except requests.exceptions.Timeout:
                self.results['dos_potential'].append({
                    'payload_type': 'Timeout',
                    'severity': 'HIGH',
                    'description': 'Search query causes timeout'
                })
            except Exception:
                pass
    
    def _test_search_filters(self):
        """Test search filter bypass"""
        if self.verbose:
            print(f"{Fore.YELLOW}[*] Testing search filters...{Style.RESET_ALL}")
        
        # Test various search parameters
        search_params = [
            {'q': 'test', 'in': 'private'},
            {'q': 'test', 'status': 'deleted'},
            {'q': 'test', 'min_posts': '0'},
            {'q': 'test', 'category': '*'}
        ]
        
        search_url = urljoin(self.target_url, '/search.json')
        
        for params in search_params:
            try:
                response = self.session.get(search_url, params=params, timeout=5)
                
                if response.status_code == 200:
                    self.results['search_endpoints'].append({
                        'params': params,
                        'accessible': True,
                        'note': 'Filter parameters accepted'
                    })
                    
            except Exception:
                pass
    
    def _generate_recommendations(self):
        """Generate security recommendations"""
        recommendations = []
        
        if self.results['injection_vulnerabilities']:
            recommendations.append({
                'severity': 'HIGH',
                'issue': 'Search injection vulnerabilities detected',
                'recommendation': 'Implement proper input validation and sanitization'
            })
        
        if self.results['information_disclosure']:
            recommendations.append({
                'severity': 'MEDIUM',
                'issue': 'Sensitive information accessible via search',
                'recommendation': 'Review search indexing and implement proper access controls'
            })
        
        if self.results['dos_potential']:
            recommendations.append({
                'severity': 'HIGH',
                'issue': 'DoS potential via search queries',
                'recommendation': 'Implement query complexity limits and rate limiting'
            })
        
        if not any([self.results['injection_vulnerabilities'],
                   self.results['dos_potential']]):
            recommendations.append({
                'severity': 'INFO',
                'issue': 'Search functionality appears secure',
                'recommendation': 'Continue monitoring and implement rate limiting'
            })
        
        self.results['recommendations'] = recommendations
    
    def print_results(self):
        """Print formatted results"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"Discourse Search Security Scan Results")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}[*] Search Endpoints Tested: {len(self.results['search_endpoints'])}{Style.RESET_ALL}")
        
        if self.results['injection_vulnerabilities']:
            print(f"\n{Fore.RED}[!] Injection Vulnerabilities: {len(self.results['injection_vulnerabilities'])}{Style.RESET_ALL}")
            for vuln in self.results['injection_vulnerabilities']:
                print(f"  [{vuln['severity']}] {vuln['type']} - {vuln.get('payload', '')[:50]}")
        
        if self.results['information_disclosure']:
            print(f"\n{Fore.YELLOW}[!] Information Disclosure: {len(self.results['information_disclosure'])}{Style.RESET_ALL}")
            for info in self.results['information_disclosure']:
                print(f"  • Query '{info['query']}': {info['results_found']} results")
        
        if self.results['dos_potential']:
            print(f"\n{Fore.RED}[!] DoS Potential: {len(self.results['dos_potential'])}{Style.RESET_ALL}")
            for dos in self.results['dos_potential']:
                print(f"  [{dos['severity']}] {dos['description']}")
        
        if self.results['recommendations']:
            print(f"\n{Fore.YELLOW}[*] Recommendations:{Style.RESET_ALL}")
            for rec in self.results['recommendations']:
                print(f"  [{rec['severity']}] {rec['issue']}")
                print(f"      → {rec['recommendation']}")
