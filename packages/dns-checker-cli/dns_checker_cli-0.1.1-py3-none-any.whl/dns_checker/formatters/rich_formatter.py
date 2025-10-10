"""Rich 라이브러리를 사용한 출력 포맷팅"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich import box
from typing import List, Dict, Any, Optional
from datetime import datetime


class RichFormatter:
    """터미널 출력을 위한 Rich 포맷터"""
    
    def __init__(self):
        """Console 객체 초기화"""
        self.console = Console()
    
    def print_error(self, message: str):
        """
        Print error message
        
        Args:
            message: Error message to print
        """
        self.console.print(f"[bold red]❌ Error:[/bold red] {message}")
    
    def print_success(self, message: str):
        """
        Print success message
        
        Args:
            message: Success message to print
        """
        self.console.print(f"[bold green]✓[/bold green] {message}")
    
    def print_warning(self, message: str):
        """
        Print warning message
        
        Args:
            message: Warning message to print
        """
        self.console.print(f"[bold yellow]⚠️  Warning:[/bold yellow] {message}")
    
    def print_info(self, message: str):
        """
        Print info message
        
        Args:
            message: Info message to print
        """
        self.console.print(f"[bold blue]ℹ️  Info:[/bold blue] {message}")
    
    def print_dns_records(self, domain: str, records: Dict[str, List[Dict[str, Any]]]):
        """
        DNS 레코드를 테이블 형식으로 출력
        
        Args:
            domain: 조회한 도메인 이름
            records: 레코드 타입별 결과 딕셔너리
        """
        # 타입별 색상 매핑
        type_colors = {
            'A': 'cyan',
            'AAAA': 'blue',
            'CNAME': 'green',
            'MX': 'magenta',
            'TXT': 'yellow',
            'NS': 'red'
        }
        
        table = Table(
            title=f"[bold white]DNS Records for {domain}[/bold white]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold"
        )
        
        table.add_column("Type", style="bold", width=10)
        table.add_column("Value", style="white")
        table.add_column("TTL", justify="right", style="dim", width=10)
        
        # No records found
        if not records or all(not v for v in records.values()):
            self.console.print(Panel(
                "[yellow]No DNS records found[/yellow]",
                title=f"[bold]{domain}[/bold]",
                border_style="yellow"
            ))
            return
        
        # 레코드 타입별로 정렬하여 출력
        for record_type in ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']:
            if record_type in records and records[record_type]:
                color = type_colors.get(record_type, 'white')
                for record in records[record_type]:
                    table.add_row(
                        f"[{color}]{record_type}[/{color}]",
                        record.get('value', ''),
                        str(record.get('ttl', 'N/A'))
                    )
        
        self.console.print(table)
    
    def print_ssl_info(self, domain: str, cert_info: Dict[str, Any]):
        """
        SSL 인증서 정보를 패널과 테이블로 출력
        
        Args:
            domain: 도메인 이름
            cert_info: 인증서 정보 딕셔너리
        """
        # 만료 경고 확인
        is_expiring = cert_info.get('is_expiring_soon', False)
        days_until_expiry = cert_info.get('days_until_expiry', 0)
        
        # 제목 스타일 설정
        if is_expiring:
            title_style = "bold red"
            border_style = "red"
        else:
            title_style = "bold green"
            border_style = "green"
        
        # Certificate information table
        table = Table(
            box=box.SIMPLE,
            show_header=False,
            padding=(0, 2)
        )
        table.add_column("Field", style="bold cyan", width=20)
        table.add_column("Value", style="white")
        
        # Issuer
        table.add_row("Issuer", cert_info.get('issuer', 'N/A'))
        
        # Subject
        table.add_row("Subject", cert_info.get('subject', 'N/A'))
        
        # Validity period
        valid_from = cert_info.get('valid_from', 'N/A')
        valid_to = cert_info.get('valid_to', 'N/A')
        table.add_row("Valid From", str(valid_from))
        
        # Expiration date - highlight if expiring
        if is_expiring:
            expiry_text = f"[bold red]{valid_to} (⚠️  {days_until_expiry} days left)[/bold red]"
        else:
            expiry_text = f"{valid_to} ({days_until_expiry} days left)"
        table.add_row("Expires", expiry_text)
        
        # Signature algorithm
        table.add_row("Signature Algorithm", cert_info.get('signature_algorithm', 'N/A'))
        
        # SAN (Subject Alternative Names)
        san_list = cert_info.get('san', [])
        if san_list:
            san_text = "\n".join(san_list[:5])  # Show max 5
            if len(san_list) > 5:
                san_text += f"\n... and {len(san_list) - 5} more"
            table.add_row("SAN", san_text)
        
        # 패널로 감싸서 출력
        panel = Panel(
            table,
            title=f"[{title_style}]SSL Certificate - {domain}[/{title_style}]",
            border_style=border_style,
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        # Expiration warning message
        if is_expiring:
            self.print_warning(f"Certificate expires in {days_until_expiry} days!")
    
    def print_httping_result(self, result: Dict[str, Any], previous_ip: Optional[str] = None):
        """
        HTTP ping 결과를 실시간으로 출력
        
        Args:
            result: ping 결과 딕셔너리
            previous_ip: 이전 요청의 서버 IP (변경 감지용)
        """
        timestamp = result.get('timestamp', datetime.now())
        status_code = result.get('status_code', 0)
        response_time = result.get('response_time', 0)
        server_ip = result.get('server_ip', 'N/A')
        success = result.get('success', False)
        error = result.get('error')
        content_length = result.get('content_length', 0)
        content_type = result.get('content_type', 'N/A')
        forced_ip = result.get('forced_ip')
        
        # 시간 포맷
        time_str = timestamp.strftime('%H:%M:%S')
        
        # 상태 코드 색상
        if success and 200 <= status_code < 300:
            status_style = "green"
        elif 300 <= status_code < 400:
            status_style = "yellow"
        else:
            status_style = "red"
        
        # 응답 시간 색상
        if response_time < 100:
            time_style = "green"
        elif response_time < 500:
            time_style = "yellow"
        else:
            time_style = "red"
        
        # IP change detection
        ip_changed = previous_ip and previous_ip != server_ip
        if ip_changed:
            ip_display = f"[bold magenta blink]{server_ip} (changed!)[/bold magenta blink]"
        elif forced_ip:
            ip_display = f"[bold yellow]{server_ip} (forced)[/bold yellow]"
        else:
            ip_display = f"[cyan]{server_ip}[/cyan]"
        
        # Content-Length 포맷팅
        if content_length >= 1024 * 1024:
            size_display = f"{content_length / (1024 * 1024):.2f}MB"
        elif content_length >= 1024:
            size_display = f"{content_length / 1024:.2f}KB"
        else:
            size_display = f"{content_length}B"
        
        # Content-Type 간략화
        if content_type != 'N/A':
            content_type_short = content_type.split(';')[0].strip()
        else:
            content_type_short = 'N/A'
        
        if success:
            self.console.print(
                f"[dim]{time_str}[/dim] "
                f"[{status_style}]{status_code}[/{status_style}] "
                f"[{time_style}]{response_time:.0f}ms[/{time_style}] "
                f"{ip_display} "
                f"[dim]{size_display}[/dim] "
                f"[dim italic]{content_type_short}[/dim italic]"
            )
        else:
            self.console.print(
                f"[dim]{time_str}[/dim] "
                f"[bold red]Failed[/bold red] "
                f"{error or 'Unknown error'}"
            )
    
    def print_statistics(self, stats: Dict[str, Any]):
        """
        HTTP ping 통계를 패널로 출력
        
        Args:
            stats: 통계 정보 딕셔너리
        """
        total = stats.get('total', 0)
        success = stats.get('success', 0)
        failed = stats.get('failed', 0)
        response_times = stats.get('response_times', [])
        
        if total == 0:
            return
        
        # 성공률 계산
        success_rate = (success / total * 100) if total > 0 else 0
        
        # 평균 응답 시간 계산
        avg_time = sum(response_times) / len(response_times) if response_times else 0
        min_time = min(response_times) if response_times else 0
        max_time = max(response_times) if response_times else 0
        
        # Statistics table
        table = Table(
            box=box.SIMPLE,
            show_header=False,
            padding=(0, 2)
        )
        table.add_column("Metric", style="bold cyan", width=15)
        table.add_column("Value", style="white")
        
        table.add_row("Total Requests", str(total))
        table.add_row("Success", f"[green]{success}[/green]")
        table.add_row("Failed", f"[red]{failed}[/red]")
        table.add_row("Success Rate", f"{success_rate:.1f}%")
        
        if response_times:
            table.add_row("Avg Response", f"{avg_time:.0f}ms")
            table.add_row("Min Response", f"{min_time:.0f}ms")
            table.add_row("Max Response", f"{max_time:.0f}ms")
        
        panel = Panel(
            table,
            title="[bold white]Statistics[/bold white]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print("\n")
        self.console.print(panel)
