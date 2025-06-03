"""
Unit Tests for Log Parser Module

This module contains unit tests for the log parsing functionality.
Will be implemented during Phase 5: Testing & Validation.
"""

import pytest
from backend.log_parser.parser import LogParser, parse_log_line, parse_log_batch


class TestLogParser:
    """Test cases for LogParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = LogParser()
        
    def test_parse_syslog(self):
        """Test parsing of Linux syslog format."""
        # TODO: Phase 5 implementation
        log_line = "Jan 12 14:30:15 web01 sshd[1234]: Failed password for user from 192.168.1.100"
        
        result = self.parser.parse_syslog(log_line)
        
        # TODO: Add actual assertions
        assert result is not None
        assert 'timestamp' in result
        assert 'host' in result
        assert 'process' in result
        assert 'message' in result
        
    def test_parse_hadoop(self):
        """Test parsing of Hadoop log format."""
        # TODO: Phase 5 implementation
        log_line = "2023-01-12 14:30:15,123 INFO [main] org.apache.hadoop.hdfs.DataNode: Starting DataNode"
        
        result = self.parser.parse_hadoop(log_line)
        
        # TODO: Add actual assertions
        assert result is not None
        assert result['log_type'] == 'hadoop'
        
    def test_parse_windows_event(self):
        """Test parsing of Windows Event Log format."""
        # TODO: Phase 5 implementation
        log_line = "EventID: 4624 Source: Microsoft-Windows-Security User: SYSTEM"
        
        result = self.parser.parse_windows_event(log_line)
        
        # TODO: Add actual assertions
        assert result is not None
        assert result['log_type'] == 'windows'
        
    def test_auto_parse_detection(self):
        """Test automatic log format detection."""
        # TODO: Phase 5 implementation
        test_cases = [
            ("Jan 12 14:30:15 web01 sshd[1234]: Login attempt", "syslog"),
            ("2023-01-12 14:30:15 INFO hadoop.DataNode: Starting", "hadoop"),
            ("EventID: 4624 User login successful", "windows"),
            ("Unknown format log line", "generic")
        ]
        
        for log_line, expected_type in test_cases:
            result = self.parser.auto_parse(log_line)
            # TODO: Assert actual log type detection
            assert 'log_type' in result
            
    def test_parse_generic(self):
        """Test generic parser for unknown formats."""
        log_line = "Some unknown log format with timestamp and message"
        
        result = self.parser.parse_generic(log_line)
        
        assert result['log_type'] == 'generic'
        assert result['message'] == log_line
        assert 'timestamp' in result


class TestBatchParsing:
    """Test cases for batch parsing functions."""
    
    def test_parse_log_batch(self):
        """Test parsing multiple log lines."""
        # TODO: Phase 5 implementation
        log_lines = [
            "Jan 12 14:30:15 web01 sshd[1234]: Failed password",
            "2023-01-12 14:30:16 INFO hadoop.DataNode: Starting",
            "",  # Empty line should be skipped
            "EventID: 4624 User login successful"
        ]
        
        results = parse_log_batch(log_lines)
        
        # Should parse 3 lines (skip empty line)
        assert len(results) == 3
        
        for result in results:
            assert 'timestamp' in result
            assert 'message' in result
            assert 'log_type' in result
            
    def test_parse_single_log_line(self):
        """Test parsing a single log line."""
        log_line = "Jan 12 14:30:15 web01 nginx[5678]: GET /api/health 200"
        
        result = parse_log_line(log_line)
        
        assert result is not None
        assert 'timestamp' in result
        assert result['message'] == log_line
        
    def test_empty_log_handling(self):
        """Test handling of empty or whitespace-only logs."""
        empty_lines = ["", "   ", "\t", "\n"]
        
        results = parse_log_batch(empty_lines)
        
        # All empty lines should be filtered out
        assert len(results) == 0


class TestErrorHandling:
    """Test cases for error handling and edge cases."""
    
    def test_malformed_log_parsing(self):
        """Test parsing of malformed log entries."""
        # TODO: Phase 5 implementation
        malformed_logs = [
            "Invalid timestamp format",
            "Missing fields in log",
            "Special characters: áéíóú 中文 🚨",
            "Very long log line " + "x" * 1000
        ]
        
        parser = LogParser()
        
        for log_line in malformed_logs:
            result = parser.auto_parse(log_line)
            
            # Should not crash and return a valid result
            assert result is not None
            assert 'message' in result
            assert 'timestamp' in result
            
    def test_none_input_handling(self):
        """Test handling of None or invalid inputs."""
        parser = LogParser()
        
        # TODO: Decide on behavior for None inputs
        # For now, expect graceful handling
        try:
            result = parser.auto_parse("")
            assert result is not None
        except Exception as e:
            pytest.fail(f"Parser should handle empty string gracefully: {e}")


# Integration tests
class TestIntegrationParsing:
    """Integration tests with realistic log samples."""
    
    def test_real_syslog_samples(self):
        """Test with real syslog samples."""
        # TODO: Phase 5 - Add real syslog examples from datasets
        real_logs = [
            "Dec 10 07:07:38 server1 sshd[25455]: Accepted publickey for user1 from 192.168.1.100 port 52743 ssh2",
            "Dec 10 07:08:15 server1 sudo: user1 : TTY=pts/0 ; PWD=/home/user1 ; USER=root ; COMMAND=/bin/ls",
            "Dec 10 07:10:22 server1 kernel: [12345.678] TCP: eth0: link up"
        ]
        
        results = parse_log_batch(real_logs)
        
        assert len(results) == 3
        
        # Check that all results have required fields
        for result in results:
            assert all(key in result for key in ['timestamp', 'host', 'process', 'message'])
            
    def test_mixed_log_formats(self):
        """Test parsing mixed log formats in one batch."""
        # TODO: Phase 5 implementation
        mixed_logs = [
            "Jan 12 14:30:15 web01 apache[1234]: GET /index.html",  # syslog
            "2023-01-12 14:30:16,123 INFO [main] DataNode: Starting",  # hadoop
            "EventID: 4624 Source: Security User: Administrator",  # windows
            "Custom application log with no standard format"  # generic
        ]
        
        results = parse_log_batch(mixed_logs)
        
        assert len(results) == 4
        
        # Verify different log types were detected
        log_types = [result['log_type'] for result in results]
        assert len(set(log_types)) > 1  # Should have multiple types


if __name__ == "__main__":
    pytest.main([__file__]) 