import { useState, useEffect } from 'react'
import './PreviewPanel.css'

interface PreviewPanelProps {
  appId?: string
  onAppSelected?: (appId: string) => void
  isSidebarCollapsed?: boolean
  onToggleSidebar?: () => void
}

interface Task {
  task_id: string
  status: string
  created_at?: string
  updated_at?: string
  result?: any
}

function PreviewPanel({ appId, onAppSelected }: PreviewPanelProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const [prevAppId, setPrevAppId] = useState<string | undefined>(appId)
  
  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview')
  const [deviceType, setDeviceType] = useState<'desktop' | 'tablet' | 'mobile'>('desktop')
  const [isConsoleOpen, setIsConsoleOpen] = useState(false)
  const [consoleLogs, setConsoleLogs] = useState<{type: string, msg: string}[]>([
    { type: 'info', msg: 'VibeCoder Environment Initialized.' },
    { type: 'info', msg: 'Ready to preview applications.' }
  ])

  const [showHistoryModal, setShowHistoryModal] = useState(false)
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)

  // 当 appId 变化时，触发加载
  useEffect(() => {
    if (appId) {
      setIsLoading(true);
      setRefreshKey(prev => prev + 1);
      setConsoleLogs(prev => [...prev, { type: 'info', msg: `Loading Application (ID: ${appId.slice(0,8)})...` }]);
    }
  }, [appId]);

  // Fetch history
  useEffect(() => {
    if (showHistoryModal) {
      setIsLoadingHistory(true)
      
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
      
      fetch(`${API_BASE_URL}/api/all_tasks`)
        .then(res => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json();
        })
        .then(data => {
          if (data.status === 'success' && data.tasks) {
            const tasksArray = Object.keys(data.tasks).map(id => ({
              task_id: id,
              ...data.tasks[id]
            }))
            // Sort by created_at or updated_at descending if available
            tasksArray.sort((a, b) => {
              const dateA = a.created_at || a.updated_at || '';
              const dateB = b.created_at || b.updated_at || '';
              return dateB.localeCompare(dateA);
            })
            setTasks(tasksArray)
          }
        })
        .catch(err => console.error("Failed to fetch tasks", err))
        .finally(() => setIsLoadingHistory(false))
    }
  }, [showHistoryModal])

  // 构造预览 URL
  // 后端挂载在 /generated_app 路径下
  const BACKEND_URL = 'http://localhost:8000'
  const previewUrl = appId 
    ? `${BACKEND_URL}/generated_app/${appId}/ui/index.html?t=${refreshKey}` 
    : undefined

  const handleRefresh = () => {
    setIsLoading(true)
    setRefreshKey(prev => prev + 1)
    setConsoleLogs(prev => [...prev, { type: 'info', msg: `Refreshing application (ID: ${appId?.slice(0,8)})...` }])
  }

  // Listen for refresh events from other components (like ChatPanel after refinement)
  useEffect(() => {
    const handleRefreshEvent = () => handleRefresh()
    window.addEventListener('refresh-preview', handleRefreshEvent)
    return () => window.removeEventListener('refresh-preview', handleRefreshEvent)
  }, [])

  const getDeviceWidth = () => {
    switch(deviceType) {
      case 'mobile': return '375px';
      case 'tablet': return '768px';
      default: return '100%';
    }
  }

  return (
    <div className="preview-panel">
      <div className="preview-header">
        <div className="preview-header-left">
          <div className="preview-logo">VC</div>
          <div>
            <h1>App Preview</h1>
            <p className="preview-subtitle">
              {appId ? `Current App: ${appId.slice(0, 8)}...` : 'Real-time preview of generated applications'}
            </p>
          </div>
        </div>
        
        <div className="preview-header-actions">
          {appId && (
            <button className="header-button" onClick={handleRefresh}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M23 4v6h-6"></path>
                <path d="M1 20v-6h6"></path>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
              </svg>
              Refresh
            </button>
          )}
          <button className="header-button" onClick={() => setShowHistoryModal(true)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            History
          </button>
          <button className="header-button primary">
            Download Code
          </button>
        </div>
      </div>

      <div className="preview-toolbar">
        <div className="toolbar-tabs">
          <button 
            className={`tab-button ${viewMode === 'preview' ? 'active' : ''}`}
            onClick={() => setViewMode('preview')}
          >
            Preview
          </button>
          <button 
            className={`tab-button ${viewMode === 'code' ? 'active' : ''}`}
            onClick={() => setViewMode('code')}
          >
            Code
          </button>
        </div>

        {viewMode === 'preview' && appId && (
          <div className="device-selector">
            <button 
              className={`device-button ${deviceType === 'desktop' ? 'active' : ''}`}
              onClick={() => setDeviceType('desktop')}
              title="Desktop View"
            >
              Desktop
            </button>
            <button 
              className={`device-button ${deviceType === 'tablet' ? 'active' : ''}`}
              onClick={() => setDeviceType('tablet')}
              title="Tablet View"
            >
              Tablet
            </button>
            <button 
              className={`device-button ${deviceType === 'mobile' ? 'active' : ''}`}
              onClick={() => setDeviceType('mobile')}
              title="Mobile View"
            >
              Mobile
            </button>
          </div>
        )}
      </div>
      
      <div className="preview-content">
        {appId ? (
          viewMode === 'preview' ? (
            <div className="iframe-container" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', backgroundColor: '#f3f4f6' }}>
              <div className="iframe-wrapper" style={{ 
                width: getDeviceWidth(), 
                height: '100%', 
                position: 'relative', 
                transition: 'width 0.3s ease',
                boxShadow: deviceType !== 'desktop' ? '0 10px 25px rgba(0,0,0,0.1)' : 'none',
                backgroundColor: '#fff'
              }}>
                <iframe
                  key={`${appId}-${refreshKey}`}
                  src={previewUrl}
                  className="preview-iframe"
                  title="App Preview"
                  onLoad={() => {
                    setIsLoading(false);
                    setConsoleLogs(prev => [...prev, { type: 'success', msg: 'Application loaded successfully.' }]);
                  }}
                  sandbox="allow-scripts allow-forms allow-same-origin allow-popups"
                  style={{ width: '100%', height: '100%', border: 'none' }}
                />
                {isLoading && (
                  <div className="loading-overlay">
                    <div className="skeleton-loader">
                      <div className="skeleton-line header"></div>
                      <div className="skeleton-grid">
                        <div className="skeleton-box"></div>
                        <div className="skeleton-box"></div>
                      </div>
                      <div className="skeleton-line body"></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="code-view-container">
              <div className="code-placeholder">
                <div className="code-header">
                  <span>index.html</span>
                  <button className="copy-button">Copy</button>
                </div>
                <pre>
                  <code>
                    {`<!DOCTYPE html>
<html>
<head>
    <title>Generated App</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="root"></div>
    <script src="js/main.js"></script>
</body>
</html>`}
                  </code>
                </pre>
              </div>
            </div>
          )
        ) : (
          <div className="preview-placeholder">
            <div className="placeholder-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="9" y1="3" x2="9" y2="21"></line>
              </svg>
            </div>
            <h2>Project Workspace</h2>
            <p>Select or generate an application to see it here</p>
          </div>
        )}
      </div>

      <div className={`console-panel ${isConsoleOpen ? 'open' : ''}`}>
        <div className="console-header" onClick={() => setIsConsoleOpen(!isConsoleOpen)}>
          <div className="console-title">
            <span className="console-icon">Terminal</span>
            <span className="console-text">Console & Logs</span>
          </div>
          <div className="console-actions">
            <span className={`chevron ${isConsoleOpen ? 'up' : 'down'}`}>▼</span>
          </div>
        </div>
        {isConsoleOpen && (
          <div className="console-body">
            {consoleLogs.map((log, i) => (
              <div key={i} className={`log-line ${log.type}`}>
                <span className="log-time">[{new Date().toLocaleTimeString()}]</span>
                <span className="log-msg">{log.msg}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {showHistoryModal && (
        <div className="history-modal-overlay" onClick={() => setShowHistoryModal(false)}>
          <div className="history-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="history-modal-header">
              <h2>App History</h2>
              <button className="close-button" onClick={() => setShowHistoryModal(false)}>
                &times;
              </button>
            </div>
            <div className="history-modal-body">
              {isLoadingHistory ? (
                <div className="history-loading">
                  <div className="spinner"></div>
                  <span>Loading history...</span>
                </div>
              ) : tasks.length === 0 ? (
                <div className="history-empty">No generated apps found.</div>
              ) : (
                <ul className="history-list">
                  {tasks.map(task => (
                    <li 
                      key={task.task_id} 
                      className={`history-item ${task.status === 'completed' ? 'completed' : 'pending'}`}
                      onClick={() => {
                        if (task.status === 'completed' && onAppSelected) {
                          onAppSelected(task.task_id)
                          setShowHistoryModal(false)
                        }
                      }}
                    >
                      <div className="history-item-header">
                        <span className="history-item-id">{task.task_id.slice(0, 8)}...</span>
                        <span className={`history-item-status status-${task.status}`}>{task.status}</span>
                      </div>
                      <div className="history-item-date">
                        {new Date(task.created_at || task.updated_at || Date.now()).toLocaleString()}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PreviewPanel
