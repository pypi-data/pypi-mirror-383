"""validators 모듈 유닛 테스트"""

import pytest
from dns_checker.utils.validators import validate_ip, validate_domain, parse_url


class TestValidateIP:
    """IP 주소 검증 테스트"""
    
    def test_valid_ipv4(self):
        """유효한 IPv4 주소 테스트"""
        assert validate_ip('192.168.1.1') is True
        assert validate_ip('8.8.8.8') is True
        assert validate_ip('127.0.0.1') is True
        assert validate_ip('255.255.255.255') is True
        assert validate_ip('0.0.0.0') is True
    
    def test_valid_ipv6(self):
        """유효한 IPv6 주소 테스트"""
        assert validate_ip('2001:0db8:85a3:0000:0000:8a2e:0370:7334') is True
        assert validate_ip('2001:db8::1') is True
        assert validate_ip('::1') is True
        assert validate_ip('fe80::1') is True
        assert validate_ip('::') is True
    
    def test_invalid_ipv4(self):
        """유효하지 않은 IPv4 주소 테스트"""
        assert validate_ip('256.1.1.1') is False
        assert validate_ip('192.168.1') is False
        assert validate_ip('192.168.1.1.1') is False
        assert validate_ip('192.168.-1.1') is False
        assert validate_ip('192.168.1.a') is False
    
    def test_invalid_ipv6(self):
        """유효하지 않은 IPv6 주소 테스트"""
        assert validate_ip('gggg::1') is False
        assert validate_ip('2001:db8::1::2') is False
        assert validate_ip('2001:db8:') is False
    
    def test_invalid_formats(self):
        """잘못된 형식 테스트"""
        assert validate_ip('') is False
        assert validate_ip('not-an-ip') is False
        assert validate_ip('example.com') is False
        assert validate_ip('192.168.1.1/24') is False


class TestValidateDomain:
    """도메인 이름 검증 테스트"""
    
    def test_valid_domains(self):
        """유효한 도메인 테스트"""
        assert validate_domain('example.com') is True
        assert validate_domain('sub.example.com') is True
        assert validate_domain('deep.sub.example.com') is True
        assert validate_domain('example-site.com') is True
        assert validate_domain('example123.com') is True
        assert validate_domain('123example.com') is True
    
    def test_valid_tld(self):
        """다양한 TLD 테스트"""
        assert validate_domain('example.co.kr') is True
        assert validate_domain('example.org') is True
        assert validate_domain('example.net') is True
        assert validate_domain('example.io') is True
    
    def test_invalid_domains(self):
        """유효하지 않은 도메인 테스트"""
        assert validate_domain('') is False
        assert validate_domain('example') is False  # TLD 없음
        assert validate_domain('.example.com') is False  # 시작이 점
        assert validate_domain('example.com.') is False  # 끝이 점
        assert validate_domain('example..com') is False  # 연속된 점
        assert validate_domain('-example.com') is False  # 시작이 하이픈
        assert validate_domain('example-.com') is False  # 끝이 하이픈
    
    def test_invalid_characters(self):
        """유효하지 않은 문자 테스트"""
        assert validate_domain('example_site.com') is False  # 언더스코어
        assert validate_domain('example site.com') is False  # 공백
        assert validate_domain('example@site.com') is False  # 특수문자
        assert validate_domain('example!.com') is False  # 특수문자
    
    def test_length_limits(self):
        """길이 제한 테스트"""
        # 253자 초과
        long_domain = 'a' * 250 + '.com'
        assert validate_domain(long_domain) is False
        
        # 빈 문자열
        assert validate_domain('') is False
    
    def test_ip_addresses_not_domains(self):
        """IP 주소는 도메인이 아님"""
        assert validate_domain('192.168.1.1') is False
        assert validate_domain('2001:db8::1') is False


class TestParseURL:
    """URL 파싱 테스트"""
    
    def test_parse_http_url(self):
        """HTTP URL 파싱 테스트"""
        scheme, hostname, port = parse_url('http://example.com')
        assert scheme == 'http'
        assert hostname == 'example.com'
        assert port == 80
    
    def test_parse_https_url(self):
        """HTTPS URL 파싱 테스트"""
        scheme, hostname, port = parse_url('https://example.com')
        assert scheme == 'https'
        assert hostname == 'example.com'
        assert port == 443
    
    def test_parse_url_with_port(self):
        """포트가 명시된 URL 파싱 테스트"""
        scheme, hostname, port = parse_url('http://example.com:8080')
        assert scheme == 'http'
        assert hostname == 'example.com'
        assert port == 8080
        
        scheme, hostname, port = parse_url('https://example.com:8443')
        assert scheme == 'https'
        assert hostname == 'example.com'
        assert port == 8443
    
    def test_parse_url_with_path(self):
        """경로가 포함된 URL 파싱 테스트"""
        scheme, hostname, port = parse_url('https://example.com/path/to/resource')
        assert scheme == 'https'
        assert hostname == 'example.com'
        assert port == 443
    
    def test_parse_url_without_scheme(self):
        """스킴이 없는 URL 파싱 테스트 (자동으로 http:// 추가)"""
        scheme, hostname, port = parse_url('example.com')
        assert scheme == 'http'
        assert hostname == 'example.com'
        assert port == 80
    
    def test_parse_url_with_subdomain(self):
        """서브도메인이 있는 URL 파싱 테스트"""
        scheme, hostname, port = parse_url('https://api.example.com')
        assert scheme == 'https'
        assert hostname == 'api.example.com'
        assert port == 443
    
    def test_parse_url_with_query_params(self):
        """쿼리 파라미터가 있는 URL 파싱 테스트"""
        scheme, hostname, port = parse_url('https://example.com?param=value')
        assert scheme == 'https'
        assert hostname == 'example.com'
        assert port == 443
    
    def test_parse_invalid_url(self):
        """유효하지 않은 URL 파싱 테스트"""
        with pytest.raises(ValueError, match="유효하지 않은 URL"):
            parse_url('http://')
        
        with pytest.raises(ValueError, match="유효하지 않은 URL"):
            parse_url('https://')
    
    def test_parse_empty_url(self):
        """빈 URL 파싱 테스트"""
        with pytest.raises(ValueError, match="URL이 비어있습니다"):
            parse_url('')
    
    def test_parse_url_with_username_password(self):
        """사용자명과 비밀번호가 포함된 URL 파싱 테스트"""
        scheme, hostname, port = parse_url('https://user:pass@example.com')
        assert scheme == 'https'
        assert hostname == 'example.com'
        assert port == 443
    
    def test_parse_localhost(self):
        """localhost URL 파싱 테스트"""
        scheme, hostname, port = parse_url('http://localhost:3000')
        assert scheme == 'http'
        assert hostname == 'localhost'
        assert port == 3000
    
    def test_parse_ip_address_url(self):
        """IP 주소 URL 파싱 테스트"""
        scheme, hostname, port = parse_url('http://192.168.1.1')
        assert scheme == 'http'
        assert hostname == '192.168.1.1'
        assert port == 80
        
        scheme, hostname, port = parse_url('https://[2001:db8::1]')
        assert scheme == 'https'
        assert hostname == '2001:db8::1'
        assert port == 443
