"""입력 유효성 검사 유틸리티"""

import ipaddress
import re
from urllib.parse import urlparse
from typing import Tuple, Optional


def validate_ip(ip_string: str) -> bool:
    """
    IP 주소 형식 검증 (IPv4/IPv6)
    
    Args:
        ip_string: 검증할 IP 주소 문자열
        
    Returns:
        유효한 IP 주소이면 True, 아니면 False
    """
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False


def validate_domain(domain: str) -> bool:
    """
    도메인 이름 형식 검증
    
    Args:
        domain: 검증할 도메인 이름
        
    Returns:
        유효한 도메인이면 True, 아니면 False
    """
    # 도메인 패턴: 알파벳, 숫자, 하이픈, 점으로 구성
    # 최소 하나의 점이 있어야 하고, 각 레이블은 63자 이하
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    
    if not domain or len(domain) > 253:
        return False
    
    return bool(re.match(pattern, domain))


def parse_url(url: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    URL 파싱 및 구성 요소 추출
    
    Args:
        url: 파싱할 URL
        
    Returns:
        (scheme, hostname, port) 튜플
        
    Raises:
        ValueError: URL이 유효하지 않은 경우
    """
    if not url:
        raise ValueError("URL이 비어있습니다")
    
    # scheme이 없으면 http:// 추가
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    parsed = urlparse(url)
    
    if not parsed.hostname:
        raise ValueError(f"유효하지 않은 URL: {url}")
    
    scheme = parsed.scheme
    hostname = parsed.hostname
    port = parsed.port
    
    # 기본 포트 설정
    if port is None:
        port = 443 if scheme == 'https' else 80
    
    return scheme, hostname, port
