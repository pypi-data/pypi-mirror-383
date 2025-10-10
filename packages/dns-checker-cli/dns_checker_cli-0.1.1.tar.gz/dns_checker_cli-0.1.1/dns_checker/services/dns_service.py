"""DNS 조회 서비스"""

import dns.resolver
import dns.exception
from typing import List, Dict, Any, Optional


class DNSService:
    """DNS 레코드 조회를 담당하는 서비스 클래스"""
    
    def __init__(self, nameserver: Optional[str] = None):
        """
        DNSService 초기화
        
        Args:
            nameserver: 커스텀 nameserver IP (선택사항)
        """
        self.resolver = dns.resolver.Resolver()
        
        # 커스텀 nameserver 설정
        if nameserver:
            self.resolver.nameservers = [nameserver]
        
        # 타임아웃 설정 (초)
        self.resolver.timeout = 5
        self.resolver.lifetime = 10
    
    def query_single_record(self, domain: str, record_type: str) -> List[Dict[str, Any]]:
        """
        단일 DNS 레코드 타입 조회
        
        Args:
            domain: 조회할 도메인
            record_type: 레코드 타입 (A, AAAA, CNAME, MX, TXT 등)
            
        Returns:
            레코드 정보 리스트
            
        Raises:
            dns.resolver.NXDOMAIN: 도메인이 존재하지 않음
            dns.resolver.Timeout: DNS 조회 타임아웃
            dns.resolver.NoAnswer: 해당 레코드 타입에 대한 응답 없음
        """
        results = []
        
        try:
            answers = self.resolver.resolve(domain, record_type)
            
            for rdata in answers:
                record_value = str(rdata)
                
                # MX 레코드는 우선순위 포함
                if record_type == 'MX':
                    record_value = f"{rdata.preference} {rdata.exchange}"
                # TXT 레코드는 따옴표 제거
                elif record_type == 'TXT':
                    record_value = ' '.join([s.decode() if isinstance(s, bytes) else str(s) for s in rdata.strings])
                
                results.append({
                    'value': record_value,
                    'ttl': answers.rrset.ttl
                })
        
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            # 해당 레코드가 없는 경우 빈 리스트 반환
            pass
        
        return results
    
    def query_records(self, domain: str, record_types: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        여러 DNS 레코드 타입 조회
        
        Args:
            domain: 조회할 도메인
            record_types: 조회할 레코드 타입 리스트 (기본값: ['A', 'AAAA', 'CNAME', 'MX', 'TXT'])
            
        Returns:
            레코드 타입별 결과 딕셔너리
            
        Raises:
            dns.resolver.NXDOMAIN: 도메인이 존재하지 않음
            dns.resolver.Timeout: DNS 조회 타임아웃
        """
        if record_types is None:
            record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT']
        
        results = {}
        
        for record_type in record_types:
            try:
                records = self.query_single_record(domain, record_type)
                if records:
                    results[record_type] = records
            except dns.resolver.Timeout:
                raise
            except dns.resolver.NXDOMAIN:
                raise
            except Exception:
                # 다른 에러는 무시하고 계속 진행
                continue
        
        return results

    def resolve_to_ip(self, domain: str) -> Optional[str]:
        """
        도메인을 IP 주소로 변환
        
        Args:
            domain: 변환할 도메인
            
        Returns:
            IP 주소 문자열 (실패 시 None)
        """
        try:
            # A 레코드 조회 시도
            answers = self.resolver.resolve(domain, 'A')
            if answers:
                return str(answers[0])
        except Exception:
            pass
        
        try:
            # AAAA 레코드 조회 시도
            answers = self.resolver.resolve(domain, 'AAAA')
            if answers:
                return str(answers[0])
        except Exception:
            pass
        
        return None
