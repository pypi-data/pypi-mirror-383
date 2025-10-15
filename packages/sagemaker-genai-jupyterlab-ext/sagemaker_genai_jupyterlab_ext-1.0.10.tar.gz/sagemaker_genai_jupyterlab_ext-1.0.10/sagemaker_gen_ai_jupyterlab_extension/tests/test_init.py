from unittest.mock import Mock, patch
from pathlib import Path

# Mock watchdog before importing the module
with patch.dict('sys.modules', {
    'watchdog': Mock(),
    'watchdog.observers': Mock(),
    'watchdog.events': Mock()
}):
    # Import the module under test
    import sagemaker_gen_ai_jupyterlab_extension as init_module
    from sagemaker_gen_ai_jupyterlab_extension.extract_utils import AuthMode
    from sagemaker_gen_ai_jupyterlab_extension.constants import SMD_LSP_SERVER_PATH, SMD_CLIENTS_DIR, SMD_JSZIP_PATH


class TestInitModule:
    
    def test_version_exists(self):
        """Test that version is set"""
        assert hasattr(init_module, '__version__')
        assert init_module.__version__ is not None

    def test_constants(self):
        """Test module constants are properly set"""
        assert init_module.NODE_PATH == "/opt/conda/bin/node"
        assert init_module.WORKSPACE_FOLDER == "file:///home/sagemaker-user"
        assert isinstance(init_module.PACKAGE_DIR, Path)
        # LSP_EXECUTABLE_PATH may be set by other tests, just check it exists
        assert hasattr(init_module, 'LSP_EXECUTABLE_PATH')

    # Token and settings extraction tests moved to test_extract_utils.py

    def test_jupyter_labextension_paths(self):
        """Test JupyterLab extension paths configuration"""
        paths = init_module._jupyter_labextension_paths()
        
        expected = [{
            "src": "labextension",
            "dest": "sagemaker_gen_ai_jupyterlab_extension"
        }]
        assert paths == expected

    def test_get_lsp_connection(self):
        """Test getting LSP connection"""
        # Mock the global lsp_connection
        mock_connection = Mock()
        with patch.object(init_module, 'lsp_connection', mock_connection):
            result = init_module.get_lsp_connection()
            assert result == mock_connection
    
    def test_get_credential_manager(self):
        """Test getting credential manager"""
        # Mock the global credential_manager
        mock_manager = Mock()
        with patch.object(init_module, 'credential_manager', mock_manager):
            result = init_module.get_credential_manager()
            assert result == mock_manager

    def test_chat_with_prompt(self):
        """Test chat with prompt function"""
        mock_connection = Mock()
        mock_connection.get_chat_response.return_value = {"response": "test"}
        
        with patch.object(init_module, 'get_lsp_connection', return_value=mock_connection):
            result = init_module.chat_with_prompt("test prompt")
            
            assert result == {"response": "test"}
            mock_connection.get_chat_response.assert_called_once_with("test prompt")

    
    def test_load_jupyter_server_extension_success(self):
        """Test successful loading of Jupyter server extension"""
        # Setup mocks
        mock_server_app = Mock()
        mock_server_app.web_app = Mock()
        mock_server_app.log = Mock()
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:    
            # Call the function
            init_module._load_jupyter_server_extension(mock_server_app)
            # Verify calls
            mock_setup.assert_called_once_with(mock_server_app.web_app)
            

    def test_unload_jupyter_server_extension(self):
        """Test unloading Jupyter server extension"""
        # Create mocks
        mock_server_app = Mock()
        mock_cred_manager = Mock()
        mock_q_custom = Mock()
        
        with patch.object(init_module, 'credential_manager', mock_cred_manager):
            with patch.object(init_module, 'q_customization', mock_q_custom):
                # Call the function
                init_module._unload_jupyter_server_extension(mock_server_app)
                
                # Verify calls
                mock_cred_manager.cleanup.assert_called_once()
                mock_q_custom.stop_watcher_for_customization_file.assert_called_once()

    def test_unload_jupyter_server_extension_with_exception(self):
        """Test unloading Jupyter server extension with exception"""
        # Create mocks
        mock_server_app = Mock()
        mock_cred_manager = Mock()
        mock_cred_manager.cleanup.side_effect = Exception("Cleanup error")
        
        with patch.object(init_module, 'credential_manager', mock_cred_manager):
            with patch.object(init_module, 'logger') as mock_logger:
                # Call the function
                init_module._unload_jupyter_server_extension(mock_server_app)
                
                # Verify error was logged
                mock_logger.error.assert_called_with("Error cleaning up credential manager: Cleanup error")

    @patch('sagemaker_gen_ai_jupyterlab_extension.requests.get')
    def test_download_and_extract_lsp_server_success(self, mock_get):
        """Test successful LSP server download and extraction"""
        # Mock manifest response
        mock_manifest = {
            'versions': [{
                'serverVersion': init_module.FLARE_SERVER_VERSION,
                'targets': [{
                    'platform': 'linux',
                    'arch': 'x64',
                    'contents': [{
                        'filename': 'servers.zip',
                        'url': 'https://test.com/servers.zip'
                    }]
                }]
            }]
        }
        
        mock_response = Mock()
        mock_response.json.return_value = mock_manifest
        mock_response.content = b'fake zip content'
        mock_get.return_value = mock_response
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.tempfile.mkdtemp', return_value='/tmp/test'):
            with patch('sagemaker_gen_ai_jupyterlab_extension.zipfile.ZipFile'):
                with patch('sagemaker_gen_ai_jupyterlab_extension.os.walk', return_value=[('/tmp/test', [], ['aws-lsp-codewhisperer.js'])]):
                    with patch('builtins.open', create=True):
                        # Call the function
                        init_module.download_and_extract_lsp_server()
                        
                        # Verify LSP_EXECUTABLE_PATH was set
                        assert init_module.LSP_EXECUTABLE_PATH == '/tmp/test/aws-lsp-codewhisperer.js'

    def test_load_jupyter_server_extension_with_error_handling(self):
        """Test enhanced error handling in load_jupyter_server_extension"""
        mock_server_app = Mock()
        mock_server_app.web_app = Mock()
        mock_server_app.log = Mock()
        
        # Test RuntimeError handling
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:
            mock_setup.side_effect = RuntimeError("LSP server unavailable")
            init_module._load_jupyter_server_extension(mock_server_app)
            mock_server_app.log.error.assert_called_with("Failed to load Amazon Q extension: LSP server unavailable")
        
        # Reset mock
        mock_server_app.log.reset_mock()
        
        # Test general Exception handling
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:
            mock_setup.side_effect = Exception("Unexpected error")
            init_module._load_jupyter_server_extension(mock_server_app)
            mock_server_app.log.error.assert_called_with("Failed to load Amazon Q extension: Unexpected error")

    # Amazon Q Agentic Chat artifacts in SageMaker Distribution integration tests
    @patch('os.makedirs')
    @patch('shutil.copy')
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_copy_artifacts_to_static_success(self, mock_isfile, mock_listdir, 
                                            mock_exists, mock_copy, mock_makedirs):
        """Test successful copying of Amazon Q Agentic Chat artifacts from SageMaker Distribution"""
        mock_exists.side_effect = lambda path: path in [
            SMD_JSZIP_PATH,
            SMD_CLIENTS_DIR
        ]
        mock_listdir.return_value = ['amazonq-ui.js', 'other-file.js']
        mock_isfile.return_value = True
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger') as mock_logger:
            init_module.copy_artifacts_to_static('/tmp/test/static')
            
            mock_makedirs.assert_called_once_with('/tmp/test/static', exist_ok=True)
            mock_copy.assert_any_call(
                SMD_JSZIP_PATH,
                '/tmp/test/static/jszip.min.js'
            )
            mock_copy.assert_any_call(
                f'{SMD_CLIENTS_DIR}/amazonq-ui.js',
                '/tmp/test/static/amazonq-ui.js'
            )
            mock_logger.info.assert_any_call("Copied jszip.min.js to static folder")
            mock_logger.info.assert_any_call("Copied amazonq-ui.js to static folder")

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_copy_artifacts_to_static_missing_files(self, mock_exists, mock_makedirs):
        """Test copying artifacts when SageMaker Distribution files are missing"""
        mock_exists.return_value = False
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger') as mock_logger:
            init_module.copy_artifacts_to_static('/tmp/test/static')
            mock_logger.warning.assert_any_call(f"Amazon Q agentic chat artifact not found: {SMD_JSZIP_PATH}, will fallback to CDN download")
            mock_logger.warning.assert_any_call(f"Amazon Q agentic chat clients directory not found: {SMD_CLIENTS_DIR}, will fallback to CDN download")

    @patch('sagemaker_gen_ai_jupyterlab_extension.copy_artifacts_to_static')
    @patch('sagemaker_gen_ai_jupyterlab_extension.os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.download_and_extract_lsp_server')
    def test_initialize_lsp_server_with_sagemaker_distribution_artifacts(self, mock_download, mock_exists, mock_copy):
        """Test LSP server initialization with SageMaker Distribution artifacts available"""
        mock_exists.return_value = True
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.LspServerConnection') as mock_lsp_class:
            with patch('sagemaker_gen_ai_jupyterlab_extension.CredentialManager'):
                with patch('sagemaker_gen_ai_jupyterlab_extension.QCustomization'):
                    with patch('sagemaker_gen_ai_jupyterlab_extension.extract_auth_mode') as mock_auth:
                        with patch('sagemaker_gen_ai_jupyterlab_extension.logger') as mock_logger:
                            mock_auth.return_value = "test_auth"
                            mock_lsp = Mock()
                            mock_lsp_class.return_value = mock_lsp
                            
                            init_module.initialize_lsp_server()
                            
                            mock_copy.assert_called_once()
                            mock_download.assert_not_called()
                            mock_lsp.start_lsp_server.assert_called_once_with(
                                init_module.NODE_PATH,
                                SMD_LSP_SERVER_PATH,
                                "test_auth"
                            )
                            mock_logger.info.assert_any_call("Copying Amazon Q agentic chat artifacts to static folder")

    @patch('sagemaker_gen_ai_jupyterlab_extension.copy_artifacts_to_static')
    @patch('sagemaker_gen_ai_jupyterlab_extension.os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.download_and_extract_lsp_server')
    def test_initialize_lsp_server_fallback_to_download(self, mock_download, mock_exists, mock_copy):
        """Test LSP server initialization falling back to download when SageMaker Distribution artifacts unavailable"""
        mock_exists.return_value = False
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.LspServerConnection') as mock_lsp_class:
            with patch('sagemaker_gen_ai_jupyterlab_extension.CredentialManager'):
                with patch('sagemaker_gen_ai_jupyterlab_extension.QCustomization'):
                    with patch('sagemaker_gen_ai_jupyterlab_extension.extract_auth_mode') as mock_auth:
                        with patch('sagemaker_gen_ai_jupyterlab_extension.logger') as mock_logger:
                            mock_auth.return_value = "test_auth"
                            mock_lsp = Mock()
                            mock_lsp_class.return_value = mock_lsp
                            
                            init_module.initialize_lsp_server()
                            
                            mock_download.assert_called_once()
                            # LSP server won't be started if download fails and returns None
                            # The function returns None when LSP server is unavailable
                            mock_logger.info.assert_any_call("LSP server artifact not found, downloading LSP server")