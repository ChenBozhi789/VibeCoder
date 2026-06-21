import { useState } from 'react'
import { testConnection, testEcho } from '../api/client'
import './ConnectionTest.css'

function ConnectionTest() {
  const [status, setStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle')
  const [result, setResult] = useState<string>('')
  const [echoMessage, setEchoMessage] = useState<string>('Hello from frontend!')

  const handleTestConnection = async () => {
    setStatus('testing')
    setResult('正在测试连接...')
    
    try {
      const response = await testConnection()
      setResult(
        `✅ 连接成功！\n` +
        `消息: ${response.message}\n` +
        `时间戳: ${response.timestamp}\n` +
        `状态: ${response.status}\n` +
        `后端版本: ${response.backend_version}`
      )
      setStatus('success')
    } catch (error) {
      setResult(`❌ 连接失败: ${error instanceof Error ? error.message : '未知错误'}`)
      setStatus('error')
    }
  }

  const handleTestEcho = async () => {
    setStatus('testing')
    setResult('正在测试回显...')
    
    try {
      const response = await testEcho(echoMessage)
      setResult(
        `✅ 回显成功！\n` +
        `发送的消息: ${echoMessage}\n` +
        `收到的回显: ${response.echo}\n` +
        `接收时间: ${response.received_at}\n` +
        `状态: ${response.status}`
      )
      setStatus('success')
    } catch (error) {
      setResult(`❌ 回显失败: ${error instanceof Error ? error.message : '未知错误'}`)
      setStatus('error')
    }
  }

  return (
    <div className="connection-test">
      <h3>前后端连接测试</h3>
      
      <div className="test-buttons">
        <button 
          onClick={handleTestConnection}
          disabled={status === 'testing'}
          className="test-button"
        >
          {status === 'testing' ? '测试中...' : '测试连接'}
        </button>
        
        <div className="echo-test">
          <input
            type="text"
            value={echoMessage}
            onChange={(e) => setEchoMessage(e.target.value)}
            placeholder="输入要回显的消息"
            className="echo-input"
          />
          <button
            onClick={handleTestEcho}
            disabled={status === 'testing'}
            className="test-button"
          >
            {status === 'testing' ? '测试中...' : '测试回显'}
          </button>
        </div>
      </div>

      {result && (
        <div className={`test-result ${status}`}>
          <pre>{result}</pre>
        </div>
      )}

      <div className="test-info">
        <p>💡 提示：确保后端服务正在运行在 <code>http://localhost:8000</code></p>
        <p>后端 API 文档: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a></p>
      </div>
    </div>
  )
}

export default ConnectionTest

