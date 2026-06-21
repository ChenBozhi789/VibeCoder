import { useState, useEffect } from 'react'
import ChatPanel from './ChatPanel'
import PreviewPanel from './PreviewPanel'
import { fetchSessions } from '../api/client'
import type { Session } from '../api/client'
import './Layout.css'

function Layout() {
  const [currentAppId, setCurrentAppId] = useState<string | undefined>()
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>()
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [showHistorySidebar, setShowHistorySidebar] = useState(false)
  const [sessions, setSessions] = useState<Session[]>([])

  useEffect(() => {
    if (showHistorySidebar) {
      loadSessions();
    }
  }, [showHistorySidebar]);

  const loadSessions = async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    }
  };

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setShowHistorySidebar(false);
  };

  const handleNewChat = () => {
    setCurrentSessionId(undefined);
    setCurrentAppId(undefined);
    setShowHistorySidebar(false);
  };

  return (
    <div className="layout">
      {/* Gemini-style slim sidebar */}
      <div className="layout-gemini-sidebar">
        <button 
          className="gemini-icon-btn top-btn" 
          onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          title={isSidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>

        <button 
          className={`gemini-icon-btn history-btn ${showHistorySidebar ? 'active' : ''}`}
          onClick={() => setShowHistorySidebar(!showHistorySidebar)}
          title="Chat History"
          style={{ marginTop: '1rem' }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </button>
      </div>

      {/* History Drawer */}
      {showHistorySidebar && (
        <div className="history-drawer">
          <div className="history-drawer-header">
            <h3>Chat History</h3>
            <button className="new-chat-btn-small" onClick={handleNewChat}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
          </div>
          <div className="history-drawer-content">
            {sessions.length === 0 ? (
              <div className="history-empty-text">No previous chats.</div>
            ) : (
              sessions.map(s => (
                <div 
                  key={s.session_id} 
                  className={`history-drawer-item ${currentSessionId === s.session_id ? 'selected' : ''}`}
                  onClick={() => handleSelectSession(s.session_id)}
                >
                  <div className="history-drawer-title">{s.title || 'New Chat'}</div>
                  <div className="history-drawer-date">
                    {new Date(s.updated_at).toLocaleDateString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      <div className={`layout-left ${isSidebarCollapsed ? 'collapsed' : ''}`}>
        <ChatPanel 
          onAppGenerated={setCurrentAppId} 
          currentSessionId={currentSessionId}
          onSessionChanged={setCurrentSessionId}
          currentAppId={currentAppId}
        />
      </div>
      
      <div className="layout-right">
        <PreviewPanel 
          appId={currentAppId} 
          onAppSelected={setCurrentAppId}
          isSidebarCollapsed={isSidebarCollapsed}
          onToggleSidebar={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />
      </div>
    </div>
  )
}

export default Layout

