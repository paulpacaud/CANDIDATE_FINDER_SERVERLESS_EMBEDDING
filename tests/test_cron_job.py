import unittest
from unittest.mock import patch, MagicMock
import azure.functions as func
from function_app import cronjobembedding
from unittest.mock import Mock


class TestCronJobEmbedding(unittest.TestCase):
    @patch('function_app.os.getenv')
    @patch('function_app.helpers_functions.establish_connection_db')
    @patch('function_app.helpers_functions.query_db')
    @patch('function_app.helpers_functions.close_connection_db')
    @patch('function_app.OpenAI')
    @patch('function_app.Pinecone')
    @patch('function_app.helpers_functions.create_vector_embedding')
    def test_cron_job_executes_successfully_with_valid_data(self, mock_create_vector_embedding, mock_Pinecone, mock_OpenAI, 
                                                            mock_close_connection_db, mock_query_db, mock_establish_connection_db, mock_getenv):
        mock_getenv.side_effect = lambda x: {'OPENAI_API_KEY': 'fakekey', 'PINECONE_API_KEY': 'fakekey', 'DB_PASSWORD': 'fakekey'}.get(x, None)
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_establish_connection_db.return_value = (mock_cursor, mock_conn)
        mock_query_db.side_effect = [
            [('1', 'Paul Doe', "paul.doe@gmail.com", "0678980987", "fake cv")],  # Mocked candidates data
            [('1', 'Software Enginner', 'good job', 'Meta')]   # Mocked jobs data
        ]

        ## Mocking external APIs
        mock_openai_client = MagicMock()
        mock_openai_client.api_key = 'fakekey'
        mock_OpenAI.return_value = mock_openai_client
        mock_pinecone_index = MagicMock()
        mock_Pinecone.return_value.Index.return_value = mock_pinecone_index
        mock_create_vector_embedding.return_value = [0.1, 0.2, 0.3]

        # EXECUTION
        func_call = cronjobembedding.build().get_user_function()
        timer_request = Mock(past_due=False)
        func_call(timer_request)
        
        # ASSERTIONS
        mock_establish_connection_db.assert_called_once()
        assert mock_query_db.call_count == 2, "Database should be queried twice, once for candidates and once for jobs."
        mock_close_connection_db.assert_called_once_with(mock_cursor, mock_conn)
        mock_create_vector_embedding.assert_called()
        assert mock_pinecone_index.upsert.called, "Data must be upserted to Pinecone."

if __name__ == '__main__':
    unittest.main()



