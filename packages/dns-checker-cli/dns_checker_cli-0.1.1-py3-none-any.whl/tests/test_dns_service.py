"""DNSService 유닛 테스트"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import dns.resolver
import dns.exception

from dns_checker.services.dns_service import DNSService


class TestDNSService:
    """DNSService 클래스 테스트"""
    
    def test_init_without_nameserver(self):
        """기본 nameserver로 초기화 테스트"""
        service = DNSService()
        assert service.resolver is not None
        assert service.resolver.timeout == 5
        assert service.resolver.lifetime == 10
    
    def test_init_with_custom_nameserver(self):
        """커스텀 nameserver로 초기화 테스트"""
        custom_ns = "8.8.8.8"
        service = DNSService(nameserver=custom_ns)
        assert service.resolver.nameservers == [custom_ns]
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_single_record_a_type(self, mock_resolve):
        """A 레코드 조회 테스트"""
        # Mock 설정
        mock_rdata = Mock()
        mock_rdata.__str__ = Mock(return_value="93.184.216.34")
        
        mock_rrset = Mock()
        mock_rrset.ttl = 300
        
        mock_answer = Mock()
        mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
        mock_answer.rrset = mock_rrset
        
        mock_resolve.return_value = mock_answer
        
        # 테스트 실행
        service = DNSService()
        results = service.query_single_record("example.com", "A")
        
        # 검증
        assert len(results) == 1
        assert results[0]['value'] == "93.184.216.34"
        assert results[0]['ttl'] == 300
        mock_resolve.assert_called_once_with("example.com", "A")
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_single_record_mx_type(self, mock_resolve):
        """MX 레코드 조회 테스트"""
        # Mock 설정
        mock_rdata = Mock()
        mock_rdata.preference = 10
        mock_rdata.exchange = "mail.example.com."
        
        mock_rrset = Mock()
        mock_rrset.ttl = 3600
        
        mock_answer = Mock()
        mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
        mock_answer.rrset = mock_rrset
        
        mock_resolve.return_value = mock_answer
        
        # 테스트 실행
        service = DNSService()
        results = service.query_single_record("example.com", "MX")
        
        # 검증
        assert len(results) == 1
        assert results[0]['value'] == "10 mail.example.com."
        assert results[0]['ttl'] == 3600
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_single_record_txt_type(self, mock_resolve):
        """TXT 레코드 조회 테스트"""
        # Mock 설정
        mock_rdata = Mock()
        mock_rdata.strings = [b"v=spf1 include:_spf.example.com ~all"]
        
        mock_rrset = Mock()
        mock_rrset.ttl = 300
        
        mock_answer = Mock()
        mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
        mock_answer.rrset = mock_rrset
        
        mock_resolve.return_value = mock_answer
        
        # 테스트 실행
        service = DNSService()
        results = service.query_single_record("example.com", "TXT")
        
        # 검증
        assert len(results) == 1
        assert "v=spf1" in results[0]['value']
        assert results[0]['ttl'] == 300
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_single_record_no_answer(self, mock_resolve):
        """레코드가 없는 경우 테스트"""
        mock_resolve.side_effect = dns.resolver.NoAnswer()
        
        service = DNSService()
        results = service.query_single_record("example.com", "AAAA")
        
        # 빈 리스트 반환 확인
        assert results == []
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_single_record_nxdomain(self, mock_resolve):
        """존재하지 않는 도메인 테스트"""
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()
        
        service = DNSService()
        results = service.query_single_record("nonexistent.example.com", "A")
        
        # 빈 리스트 반환 확인
        assert results == []
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_single_record_timeout(self, mock_resolve):
        """DNS 조회 타임아웃 테스트"""
        mock_resolve.side_effect = dns.resolver.Timeout()
        
        service = DNSService()
        # Timeout 예외는 그대로 전파되어야 함
        with pytest.raises(dns.resolver.Timeout):
            service.query_single_record("example.com", "A")
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_records_multiple_types(self, mock_resolve):
        """여러 레코드 타입 조회 테스트"""
        def mock_resolve_side_effect(domain, record_type):
            mock_rrset = Mock()
            mock_rrset.ttl = 300
            
            mock_answer = Mock()
            mock_answer.rrset = mock_rrset
            
            if record_type == "A":
                mock_rdata = Mock()
                mock_rdata.__str__ = Mock(return_value="93.184.216.34")
                mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
                return mock_answer
            elif record_type == "AAAA":
                raise dns.resolver.NoAnswer()
            elif record_type == "CNAME":
                raise dns.resolver.NoAnswer()
            elif record_type == "MX":
                mock_rdata = Mock()
                mock_rdata.preference = 10
                mock_rdata.exchange = "mail.example.com."
                mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
                return mock_answer
            elif record_type == "TXT":
                mock_rdata = Mock()
                mock_rdata.strings = [b"v=spf1 ~all"]
                mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
                return mock_answer
            
            raise dns.resolver.NoAnswer()
        
        mock_resolve.side_effect = mock_resolve_side_effect
        
        # 테스트 실행
        service = DNSService()
        results = service.query_records("example.com")
        
        # 검증
        assert "A" in results
        assert "MX" in results
        assert "TXT" in results
        assert "AAAA" not in results  # NoAnswer이므로 결과에 없어야 함
        assert "CNAME" not in results
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_records_nxdomain(self, mock_resolve):
        """존재하지 않는 도메인 조회 시 빈 결과 반환 테스트"""
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()
        
        service = DNSService()
        # query_single_record가 NXDOMAIN을 catch하여 빈 리스트를 반환하므로
        # query_records는 빈 딕셔너리를 반환
        results = service.query_records("nonexistent.example.com")
        assert results == {}
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_records_timeout(self, mock_resolve):
        """DNS 조회 타임아웃 시 예외 발생 테스트"""
        mock_resolve.side_effect = dns.resolver.Timeout()
        
        service = DNSService()
        with pytest.raises(dns.resolver.Timeout):
            service.query_records("example.com")
    
    @patch('dns.resolver.Resolver.resolve')
    def test_query_records_custom_types(self, mock_resolve):
        """커스텀 레코드 타입 리스트로 조회 테스트"""
        mock_rdata = Mock()
        mock_rdata.__str__ = Mock(return_value="93.184.216.34")
        
        mock_rrset = Mock()
        mock_rrset.ttl = 300
        
        mock_answer = Mock()
        mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
        mock_answer.rrset = mock_rrset
        
        mock_resolve.return_value = mock_answer
        
        # 테스트 실행
        service = DNSService()
        results = service.query_records("example.com", record_types=["A"])
        
        # 검증
        assert "A" in results
        assert len(results) == 1
        mock_resolve.assert_called_once_with("example.com", "A")
    
    @patch('dns.resolver.Resolver.resolve')
    def test_resolve_to_ip_success_a_record(self, mock_resolve):
        """A 레코드로 IP 변환 성공 테스트"""
        mock_rdata = Mock()
        mock_rdata.__str__ = Mock(return_value="93.184.216.34")
        
        mock_answer = [mock_rdata]
        mock_resolve.return_value = mock_answer
        
        service = DNSService()
        ip = service.resolve_to_ip("example.com")
        
        assert ip == "93.184.216.34"
        mock_resolve.assert_called_once_with("example.com", "A")
    
    @patch('dns.resolver.Resolver.resolve')
    def test_resolve_to_ip_fallback_to_aaaa(self, mock_resolve):
        """A 레코드 실패 시 AAAA 레코드로 폴백 테스트"""
        def mock_resolve_side_effect(domain, record_type):
            if record_type == "A":
                raise dns.resolver.NoAnswer()
            elif record_type == "AAAA":
                mock_rdata = Mock()
                mock_rdata.__str__ = Mock(return_value="2606:2800:220:1:248:1893:25c8:1946")
                return [mock_rdata]
        
        mock_resolve.side_effect = mock_resolve_side_effect
        
        service = DNSService()
        ip = service.resolve_to_ip("example.com")
        
        assert ip == "2606:2800:220:1:248:1893:25c8:1946"
        assert mock_resolve.call_count == 2
    
    @patch('dns.resolver.Resolver.resolve')
    def test_resolve_to_ip_failure(self, mock_resolve):
        """IP 변환 실패 테스트"""
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()
        
        service = DNSService()
        ip = service.resolve_to_ip("nonexistent.example.com")
        
        assert ip is None
    
    @patch('dns.resolver.Resolver.resolve')
    def test_resolve_to_ip_both_records_fail(self, mock_resolve):
        """A와 AAAA 레코드 모두 실패 시 None 반환 테스트"""
        mock_resolve.side_effect = dns.resolver.NoAnswer()
        
        service = DNSService()
        ip = service.resolve_to_ip("example.com")
        
        assert ip is None
        assert mock_resolve.call_count == 2

