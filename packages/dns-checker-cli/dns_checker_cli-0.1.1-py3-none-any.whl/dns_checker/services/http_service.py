"""HTTP 핑 서비스"""

import socket
import time
from datetime import datetime
from typing import Dict, Any, Optional
import requests
import urllib3
from dns_checker.services.dns_service import DNSService

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HTTPService:
    """HTTP 핑 및 마이그레이션 모니터링을 담당하는 서비스 클래스"""
    
    def __init__(self, nameserver: Optional[str] = None):
        """
        HTTPService 초기화
        
        Args:
            nameserver: 커스텀 nameserver IP (선택사항)
        """
        self.nameserver = nameserver
        self.dns_service = DNSService(nameserver) if nameserver else None
        
        # 통계 데이터
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'response_times': [],
            'server_ips': []
        }
        
        # 타임아웃 설정
        self.timeout = 10

    def ping(self, url: str, force_ip: Optional[str] = None) -> Dict[str, Any]:
        """
        HTTP/HTTPS 요청을 보내고 응답 시간 측정
        
        Args:
            url: 요청할 URL
            force_ip: 강제로 연결할 IP 주소 (선택사항)
            
        Returns:
            ping 결과 딕셔너리
        """
        result = {
            'timestamp': datetime.now(),
            'status_code': 0,
            'response_time': 0,
            'server_ip': 'N/A',
            'success': False,
            'error': None,
            'content_length': 0,
            'content_type': 'N/A',
            'forced_ip': force_ip
        }
        
        try:
            # URL에 scheme이 없으면 http:// 추가
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            # URL에서 호스트명 추출
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            
            # IP 강제 연결 설정
            session = requests.Session()
            if force_ip:
                # Host 헤더를 원래 도메인으로 설정하고 URL의 호스트를 IP로 변경
                original_url = url
                url = url.replace(hostname, force_ip)
                session.headers.update({'Host': hostname})
                server_ip = force_ip
            else:
                # 서버 IP 조회
                try:
                    if self.nameserver and self.dns_service:
                        # 커스텀 nameserver 사용
                        server_ip = self.dns_service.resolve_to_ip(hostname)
                    else:
                        # 시스템 기본 DNS 사용
                        server_ip = socket.gethostbyname(hostname)
                    
                    if not server_ip:
                        server_ip = 'N/A'
                except Exception:
                    server_ip = 'N/A'
            
            # 시작 시간 기록
            start_time = time.time()
            
            # HTTP 요청
            response = session.get(url, timeout=self.timeout, allow_redirects=True, verify=False)
            
            # 응답 시간 계산 (밀리초)
            response_time = (time.time() - start_time) * 1000
            
            # Content-Length 추출
            content_length = len(response.content)
            
            # Content-Type 추출
            content_type = response.headers.get('Content-Type', 'N/A')
            
            # 결과 업데이트
            result.update({
                'status_code': response.status_code,
                'response_time': response_time,
                'server_ip': server_ip,
                'content_length': content_length,
                'content_type': content_type,
                'success': True
            })
            
            # 통계 업데이트
            self.stats['total'] += 1
            self.stats['success'] += 1
            self.stats['response_times'].append(response_time)
            self.stats['server_ips'].append(server_ip)
            
        except requests.Timeout:
            result['error'] = 'Timeout'
            self.stats['total'] += 1
            self.stats['failed'] += 1
            
        except requests.ConnectionError as e:
            result['error'] = f'Connection failed: {str(e)}'
            self.stats['total'] += 1
            self.stats['failed'] += 1
            
        except Exception as e:
            result['error'] = f'Error: {str(e)}'
            self.stats['total'] += 1
            self.stats['failed'] += 1
        
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """
        통계 정보 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        return {
            'total': self.stats['total'],
            'success': self.stats['success'],
            'failed': self.stats['failed'],
            'response_times': self.stats['response_times'].copy(),
            'server_ips': self.stats['server_ips'].copy()
        }
    
    def reset_statistics(self):
        """통계 데이터 초기화"""
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'response_times': [],
            'server_ips': []
        }
