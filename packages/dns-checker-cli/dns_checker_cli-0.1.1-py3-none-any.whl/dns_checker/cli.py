"""DNS Checker CLI Command Interface"""

import click
import sys
from dns_checker.formatters.rich_formatter import RichFormatter
from dns_checker.utils.validators import validate_ip


# Global formatter
formatter = RichFormatter()


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    DNS Checker CLI - DNS lookup, SSL inspection, and HTTP ping tool
    
    Query DNS records, inspect SSL certificates, and monitor
    migration status through HTTP pinging.
    """
    pass


def handle_error(func):
    """Error handling decorator"""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            formatter.print_info("\nOperation cancelled.")
            sys.exit(0)
        except Exception as e:
            formatter.print_error(f"Unexpected error: {str(e)}")
            sys.exit(1)
    return wrapper



@cli.command()
@click.argument('domain')
@click.option('--nameserver', '-n', help='Custom nameserver IP address')
@handle_error
def dns(domain, nameserver):
    """
    Query DNS records for a domain
    
    DOMAIN: Domain name to query (e.g., example.com)
    
    Examples:
        dns-checker dns example.com
        dns-checker dns example.com --nameserver 8.8.8.8
    """
    from dns_checker.services.dns_service import DNSService
    import dns.resolver
    
    # Validate nameserver
    if nameserver and not validate_ip(nameserver):
        formatter.print_error(f"Invalid nameserver IP: {nameserver}")
        sys.exit(1)
    
    try:
        # Initialize DNS service
        dns_service = DNSService(nameserver)
        
        # Query DNS records
        formatter.print_info(f"Querying DNS records: {domain}")
        records = dns_service.query_records(domain)
        
        # Print results
        formatter.print_dns_records(domain, records)
        
    except dns.resolver.NXDOMAIN:
        formatter.print_error(f"Domain not found: {domain}")
        sys.exit(1)
    except dns.resolver.Timeout:
        formatter.print_error("DNS query timeout")
        sys.exit(1)
    except Exception as e:
        formatter.print_error(f"DNS query failed: {str(e)}")
        sys.exit(1)



@cli.command()
@click.argument('domain')
@click.option('--nameserver', '-n', help='Custom nameserver IP address')
@handle_error
def inspect(domain, nameserver):
    """
    Detailed inspection of DNS and SSL certificate information
    
    DOMAIN: Domain name to inspect (e.g., example.com)
    
    Examples:
        dns-checker inspect example.com
        dns-checker inspect example.com --nameserver 8.8.8.8
    """
    from dns_checker.services.dns_service import DNSService
    from dns_checker.services.ssl_service import SSLService
    import dns.resolver
    import ssl
    import socket
    
    # Validate nameserver
    if nameserver and not validate_ip(nameserver):
        formatter.print_error(f"Invalid nameserver IP: {nameserver}")
        sys.exit(1)
    
    # Query DNS information
    try:
        dns_service = DNSService(nameserver)
        formatter.print_info(f"Querying DNS records: {domain}")
        records = dns_service.query_records(domain)
        formatter.print_dns_records(domain, records)
        
    except dns.resolver.NXDOMAIN:
        formatter.print_error(f"Domain not found: {domain}")
        sys.exit(1)
    except dns.resolver.Timeout:
        formatter.print_error("DNS query timeout")
        sys.exit(1)
    except Exception as e:
        formatter.print_error(f"DNS query failed: {str(e)}")
    
    # Query SSL certificate information
    formatter.print_info(f"\nQuerying SSL certificate: {domain}")
    
    try:
        ssl_service = SSLService()
        cert_info = ssl_service.get_full_certificate_info(domain)
        formatter.print_ssl_info(domain, cert_info)
        
    except socket.gaierror:
        formatter.print_error(f"Cannot resolve domain: {domain}")
    except socket.timeout:
        formatter.print_error("SSL connection timeout")
    except ssl.SSLError as e:
        formatter.print_error(f"SSL error: {str(e)}")
    except ConnectionRefusedError:
        formatter.print_error(f"Connection refused (port 443 may not be open)")
    except Exception as e:
        formatter.print_error(f"SSL certificate query failed: {str(e)}")



@cli.command()
@click.argument('url')
@click.option('--interval', '-i', default=1, type=float, help='Request interval in seconds (default: 1)')
@click.option('--count', '-c', type=int, help='Number of requests (infinite if not specified)')
@click.option('--nameserver', '-n', help='Custom nameserver IP address')
@click.option('--server', '-s', help='Force connection to specific server IP')
@handle_error
def httping(url, interval, count, nameserver, server):
    """
    HTTP/HTTPS ping for migration monitoring
    
    URL: URL to request (e.g., https://example.com)
    
    Examples:
        dns-checker httping https://example.com
        dns-checker httping https://example.com --interval 2 --count 10
        dns-checker httping https://example.com --nameserver 8.8.8.8
        dns-checker httping https://naver.com --server 211.11.11.11
    """
    from dns_checker.services.http_service import HTTPService
    from dns_checker.utils.validators import parse_url
    import time
    
    # Validate nameserver
    if nameserver and not validate_ip(nameserver):
        formatter.print_error(f"Invalid nameserver IP: {nameserver}")
        sys.exit(1)
    
    # Validate server IP
    if server and not validate_ip(server):
        formatter.print_error(f"Invalid server IP: {server}")
        sys.exit(1)
    
    # Parse URL
    try:
        scheme, hostname, port = parse_url(url)
    except ValueError as e:
        formatter.print_error(str(e))
        sys.exit(1)
    
    # Initialize HTTP service
    http_service = HTTPService(nameserver)
    
    # Start message
    formatter.print_info(f"Starting HTTP ping: {url}")
    if server:
        formatter.print_info(f"Forced connection IP: {server}")
    if count:
        formatter.print_info(f"Request count: {count}, interval: {interval}s")
    else:
        formatter.print_info(f"Interval: {interval}s (Press Ctrl+C to stop)")
    
    formatter.console.print()
    
    # Execute ping
    request_count = 0
    previous_ip = None
    
    try:
        while True:
            # Send request
            result = http_service.ping(url, force_ip=server)
            
            # Print result
            current_ip = result.get('server_ip')
            formatter.print_httping_result(result, previous_ip)
            previous_ip = current_ip
            
            # Increment count
            request_count += 1
            
            # Exit after specified count
            if count and request_count >= count:
                break
            
            # Wait
            time.sleep(interval)
    
    except KeyboardInterrupt:
        formatter.print_info("\n\nPing stopped.")
    
    finally:
        # Print statistics
        stats = http_service.get_statistics()
        if stats['total'] > 0:
            formatter.print_statistics(stats)


if __name__ == '__main__':
    cli()
