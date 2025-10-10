"""SSL 인증서 조회 서비스"""

import ssl
import socket
from datetime import datetime
from typing import Dict, Any, List
from cryptography import x509
from cryptography.hazmat.backends import default_backend


class SSLService:
    """SSL 인증서 정보 조회를 담당하는 서비스 클래스"""
    
    def __init__(self):
        """SSLService 초기화"""
        self.timeout = 10
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """
        SSL 컨텍스트 생성
        
        Returns:
            SSL 컨텍스트 객체
        """
        context = ssl.create_default_context()
        # 인증서 검증을 비활성화하여 자체 서명 인증서도 조회 가능
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    def parse_certificate(self, cert_binary: bytes) -> Dict[str, Any]:
        """
        인증서 파싱 및 정보 추출
        
        Args:
            cert_binary: DER 형식의 인증서 바이너리
            
        Returns:
            인증서 정보 딕셔너리
        """
        cert = x509.load_der_x509_certificate(cert_binary, default_backend())
        
        # 발급자 정보 추출
        issuer_attrs = cert.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        issuer = issuer_attrs[0].value if issuer_attrs else "Unknown"
        
        # 주체 정보 추출
        subject_attrs = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        subject = subject_attrs[0].value if subject_attrs else "Unknown"
        
        # 유효 기간
        try:
            # cryptography >= 42.0.0
            valid_from = cert.not_valid_before_utc
            valid_to = cert.not_valid_after_utc
        except AttributeError:
            # cryptography < 42.0.0
            valid_from = cert.not_valid_before
            valid_to = cert.not_valid_after
        
        # SAN (Subject Alternative Names) 추출
        san_list = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            san_list = [name.value for name in san_ext.value]
        except x509.ExtensionNotFound:
            pass
        
        # 서명 알고리즘
        signature_algorithm = cert.signature_algorithm_oid._name
        
        return {
            'issuer': issuer,
            'subject': subject,
            'valid_from': valid_from,
            'valid_to': valid_to,
            'san': san_list,
            'signature_algorithm': signature_algorithm
        }
    
    def get_certificate_info(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """
        SSL 인증서 정보 조회
        
        Args:
            domain: 조회할 도메인
            port: 포트 번호 (기본값: 443)
            
        Returns:
            인증서 정보 딕셔너리
            
        Raises:
            socket.error: 연결 실패
            ssl.SSLError: SSL 오류
        """
        context = self._create_ssl_context()
        
        with socket.create_connection((domain, port), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # DER 형식으로 인증서 가져오기
                cert_binary = ssock.getpeercert(binary_form=True)
                
                # 인증서 파싱
                cert_info = self.parse_certificate(cert_binary)
                
                return cert_info

    def check_expiry_warning(self, valid_to: datetime) -> tuple[int, bool]:
        """
        인증서 만료 경고 체크
        
        Args:
            valid_to: 인증서 만료일
            
        Returns:
            (남은 일수, 경고 여부) 튜플
        """
        now = datetime.now(valid_to.tzinfo)
        days_until_expiry = (valid_to - now).days
        is_expiring_soon = days_until_expiry <= 30
        
        return days_until_expiry, is_expiring_soon
    
    def get_full_certificate_info(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """
        만료 경고를 포함한 전체 인증서 정보 조회
        
        Args:
            domain: 조회할 도메인
            port: 포트 번호 (기본값: 443)
            
        Returns:
            만료 정보가 포함된 인증서 정보 딕셔너리
        """
        cert_info = self.get_certificate_info(domain, port)
        
        # 만료 경고 체크
        days_until_expiry, is_expiring_soon = self.check_expiry_warning(cert_info['valid_to'])
        
        cert_info['days_until_expiry'] = days_until_expiry
        cert_info['is_expiring_soon'] = is_expiring_soon
        
        return cert_info
