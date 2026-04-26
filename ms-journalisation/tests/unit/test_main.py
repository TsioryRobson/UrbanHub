"""
Tests unitaires pour le module main
"""
import pytest
import json
from unittest.mock import patch, MagicMock, call
from src.main import main


class TestMain:
    """Tests pour la fonction main"""

    @patch('src.main.MockLogConsumer')
    @patch('src.main.LogApiAdapter')
    @patch('src.main.ProcessLogUseCase')
    @patch('src.main.LogValidator')
    @patch('src.main.InMemoryLogRepository')
    @patch('builtins.print')
    def test_main_execution(self, mock_print, mock_repo, mock_validator, 
                            mock_use_case, mock_api, mock_consumer_class):
        """Test la fonction main"""
        # Setup des mocks
        mock_consumer_instance = MagicMock()
        mock_consumer_class.return_value = mock_consumer_instance
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        mock_use_case_instance = MagicMock()
        mock_use_case.return_value = mock_use_case_instance
        mock_use_case_instance.execute.return_value = (True, "Success", "log-001")
        mock_api_instance.get_all_logs.return_value = {"data": []}
        mock_api_instance.get_logs_by_level.return_value = {"data": []}

        # Exécution
        main()

        # Vérifications
        assert mock_consumer_instance.start.called
        assert mock_consumer_instance.publish_message.called
        assert mock_api_instance.get_all_logs.called
        assert mock_api_instance.get_logs_by_level.called
        assert mock_consumer_instance.stop.called

    @patch('src.main.MockLogConsumer')
    @patch('src.main.LogApiAdapter')
    @patch('src.main.ProcessLogUseCase')
    @patch('src.main.LogValidator')
    @patch('src.main.InMemoryLogRepository')
    @patch('builtins.print')
    def test_main_with_sample_logs(self, mock_print, mock_repo, mock_validator, 
                                   mock_use_case, mock_api, mock_consumer_class):
        """Test la fonction main avec les logs d'exemple"""
        mock_consumer_instance = MagicMock()
        mock_consumer_class.return_value = mock_consumer_instance
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        mock_use_case_instance = MagicMock()
        mock_use_case.return_value = mock_use_case_instance
        mock_use_case_instance.execute.return_value = (True, "Success", "log-001")
        mock_api_instance.get_all_logs.return_value = {"status": "success", "data": []}
        mock_api_instance.get_logs_by_level.return_value = {"status": "success", "data": []}

        main()

        # Vérifier que start est appelé avec une fonction callback
        assert mock_consumer_instance.start.called
        start_call_args = mock_consumer_instance.start.call_args
        assert start_call_args is not None
        assert callable(start_call_args[0][0])

    @patch('src.main.MockLogConsumer')
    @patch('src.main.LogApiAdapter')
    @patch('src.main.ProcessLogUseCase')
    @patch('src.main.LogValidator')
    @patch('src.main.InMemoryLogRepository')
    @patch('builtins.print')
    def test_main_publishes_messages(self, mock_print, mock_repo, mock_validator, 
                                     mock_use_case, mock_api, mock_consumer_class):
        """Test que main publie les messages d'exemple"""
        mock_consumer_instance = MagicMock()
        mock_consumer_class.return_value = mock_consumer_instance
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        mock_use_case_instance = MagicMock()
        mock_use_case.return_value = mock_use_case_instance
        mock_use_case_instance.execute.return_value = (True, "Success", "log-001")
        mock_api_instance.get_all_logs.return_value = {"status": "success", "data": []}
        mock_api_instance.get_logs_by_level.return_value = {"status": "success", "data": []}

        main()

        # Vérifier que publish_message est appelé au moins 3 fois (pour les 3 logs d'exemple)
        assert mock_consumer_instance.publish_message.call_count >= 3

