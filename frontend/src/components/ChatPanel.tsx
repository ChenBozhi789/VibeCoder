import { useState, useEffect } from 'react'
import './ChatPanel.css'
import { sendUserRequirements, sendChatMessage, createSession, addMessageToSession, fetchSession, sendRefineRequest, pollTaskStatus, getTaskPollIntervalMs } from '../api/client'
import type { Message } from '../api/client'

// Declare types for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface ChatPanelProps {
  onAppGenerated?: (appId: string | undefined) => void;
  currentSessionId?: string;
  onSessionChanged?: (sessionId: string | undefined) => void;
  currentAppId?: string;
}

function ChatPanel({ onAppGenerated, currentSessionId, onSessionChanged, currentAppId }: ChatPanelProps) {
  const [inputValue, setInputValue] = useState('')
  
  const defaultMessage: Message = {
    id: '1',
    text: 'Welcome to VibeCoder! I can help you generate and preview applications.',
    sender: 'assistant',
    timestamp: new Date().toISOString(),
  };

  const [messages, setMessages] = useState<Message[]>([defaultMessage])
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isDiscussMode, setIsDiscussMode] = useState(false)

  // Load session when currentSessionId changes
  useEffect(() => {
    if (currentSessionId) {
      loadSession(currentSessionId);
    } else {
      setMessages([defaultMessage]);
    }
  }, [currentSessionId]);

  const loadSession = async (sessionId: string) => {
    setIsLoading(true);
    try {
      const session = await fetchSession(sessionId);
      if (session && session.messages && session.messages.length > 0) {
        setMessages(session.messages);
        
        // If the last message has a task_id, load the app preview
        const lastMessage = session.messages[session.messages.length - 1];
        if (lastMessage.task_id) {
          onAppGenerated?.(lastMessage.task_id);
        } else {
          onAppGenerated?.(undefined);
        }
      }
    } catch (e) {
      console.error("Failed to load session", e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    onSessionChanged?.(undefined);
    onAppGenerated?.(undefined);
    setMessages([defaultMessage]);
    setInputValue('');
  }

  const handleSpeech = () => {
    if (isRecording) return; // Prevent multiple instances
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support Speech Recognition. Please try Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = navigator.language || 'en-US';
    recognition.interimResults = true;
    
    // Save current input to append speech to it
    let currentText = inputValue;
    if (currentText && !currentText.endsWith(' ')) {
        currentText += ' ';
    }

    recognition.onstart = () => {
      setIsRecording(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0])
        .map((result: any) => result.transcript)
        .join('');
      
      setInputValue(currentText + transcript);
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event.error);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.start();
  }

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) {
      return
    }

    // 1. Ensure we have a session
    let sessionId = currentSessionId;
    if (!sessionId) {
      const newSession = await createSession(inputValue);
      if (newSession) {
        sessionId = newSession.session_id;
        onSessionChanged?.(sessionId);
      }
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString(),
    }

    // 添加用户消息到聊天记录
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Save user message to backend
    if (sessionId) {
      await addMessageToSession(sessionId, userMessage);
    }

    try {
      if (isDiscussMode) {
        // 调用 Discuss API 纯聊天，不生成 App
        const response = await sendChatMessage(inputValue);
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.reply,
          sender: 'assistant',
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
        
        if (sessionId) {
          await addMessageToSession(sessionId, assistantMessage);
        }
      } else {
        if (currentAppId) {
          // 调用 Refine API 在现有 App 基础上修改
          const response = await sendRefineRequest(currentAppId, inputValue);
          
          let isCompleted = false;
          let finalStatus = 'running';
          let finalMessage = 'Refinement completed successfully.';

          // 轮询任务状态
          while (!isCompleted) {
            await new Promise((resolve) => setTimeout(resolve, getTaskPollIntervalMs()));
            try {
              const pollRes = await pollTaskStatus(response.task_id);
              if (pollRes.task && (pollRes.task.status === 'completed' || pollRes.task.status === 'failed')) {
                isCompleted = true;
                finalStatus = pollRes.task.status;
                if (finalStatus === 'failed') finalMessage = 'Refinement failed.';
              }
            } catch (pollErr) {
              console.error('Failed to poll status', pollErr);
              // Retry on next loop
            }
          }
          
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: finalStatus === 'completed' ? `✨ ${finalMessage}\nTask ID: ${response.task_id}` : `❌ ${finalMessage}\nTask ID: ${response.task_id}`,
            sender: 'assistant',
            task_id: response.task_id,
            timestamp: new Date().toISOString(),
          }
          setMessages((prev) => [...prev, assistantMessage])

          if (sessionId) {
            await addMessageToSession(sessionId, assistantMessage);
          }

          if (finalStatus === 'completed' && response.task_id) {
            onAppGenerated?.(response.task_id)
            window.dispatchEvent(new Event('refresh-preview'))
          }
        } else {
          // 调用后端 API，使用后端内置模型策略（生成全新 App）
          const response = await sendUserRequirements(inputValue)
          
          let isCompleted = false;
          let finalStatus = 'running';
          
          // 添加正在生成的提示消息
          const statusMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: `🏗️ Generating your app... (Task ID: ${response.task_id})`,
            sender: 'assistant',
            timestamp: new Date().toISOString(),
          }
          setMessages((prev) => [...prev, statusMessage])

          // 轮询任务状态
          while (!isCompleted) {
            await new Promise((resolve) => setTimeout(resolve, getTaskPollIntervalMs()));
            try {
              const pollRes = await pollTaskStatus(response.task_id);
              if (pollRes.task && (pollRes.task.status === 'completed' || pollRes.task.status === 'failed')) {
                isCompleted = true;
                finalStatus = pollRes.task.status;
              }
            } catch (pollErr) {
              console.error('Failed to poll status', pollErr);
            }
          }

          // 更新消息为完成状态
          const assistantMessage: Message = {
            id: (Date.now() + 2).toString(),
            text: finalStatus === 'completed' ? `✅ App generated successfully!\nTask ID: ${response.task_id}` : `❌ Generation failed.\nTask ID: ${response.task_id}`,
            sender: 'assistant',
            task_id: response.task_id,
            timestamp: new Date().toISOString(),
          }
          setMessages((prev) => [...prev, assistantMessage])

          if (sessionId) {
            await addMessageToSession(sessionId, assistantMessage);
          }

          // 只有成功后才通知预览
          if (finalStatus === 'completed' && response.task_id) {
            onAppGenerated?.(response.task_id)
          }
        }
      }
    } catch (error) {
      // 错误处理
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `❌ Send failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
      if (sessionId) {
        await addMessageToSession(sessionId, errorMessage);
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (prompt: string) => {
    setInputValue(prompt)
  }

  return (
    <div className="chat-panel">
      <div className="chat-panel-header">
        <div className="header-left">
          <h2>VibeCoder</h2>
        </div>
        
        <div className="header-center"></div>

        <div className="header-right">
          <button className="header-action-button" onClick={handleNewChat} title="New Chat">
            <span className="action-icon">+</span>
            <span>New Chat</span>
          </button>
        </div>
      </div>
      
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className="message-item">
            {message.sender === 'assistant' && <div className="message-avatar">VC</div>}
            <div className="message-content">
              <div className="message-text">{message.text}</div>
              <div className="message-time">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
            {message.sender === 'user' && <div className="message-avatar user">You</div>}
          </div>
        ))}
        
        {isLoading && (
          <div className="generation-flow">
            <div className="flow-item">
              <div className="flow-indicator"></div>
              <span>{isDiscussMode ? 'Thinking...' : (currentAppId ? 'Refining app...' : 'Generating app...')}</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="chat-input-area">
        {messages.length < 3 && (
          <div className="suggestions">
            <span className="suggestion-tag" onClick={() => handleSuggestionClick('Create a modern Todo App with drag and drop functionality')}>📋 Todo App</span>
            <span className="suggestion-tag" onClick={() => handleSuggestionClick('Generate a Minesweeper game with only the essential basic functions.')}>💣 MineSweeper</span>
            <span className="suggestion-tag" onClick={() => handleSuggestionClick('Design a Personal Blog with a dark mode toggle')}>✍️ Personal Blog</span>
          </div>
        )}
        
        <div className="input-box-wrapper">
          <textarea
            placeholder={isDiscussMode ? "Ask me anything..." : "What would you like to build or change?"}
            className="chat-input-textarea"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              // Auto-resize
              e.target.style.height = 'auto';
              e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={isLoading}
            rows={1}
          />
          
          <div className="input-actions-row">
            <div className="mode-actions">
              <button 
                className={`mode-button ${isDiscussMode ? 'active' : ''}`} 
                onClick={() => setIsDiscussMode(!isDiscussMode)} 
                title="Discuss Mode (Chat only)"
              >
                💬 Discuss
              </button>
              <button 
                className={`mode-button ${isRecording ? 'recording' : ''}`} 
                onClick={handleSpeech} 
                title="Voice Input"
              >
                {isRecording ? '🔴 Listening...' : '🎤 Voice'}
              </button>
            </div>
            
            <button 
              className="send-button-new"
              onClick={handleSend}
              disabled={isLoading || !inputValue.trim()}
              title="Send Message"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
        <div className="input-hint">
          Shift + Enter for new line
        </div>
      </div>
    </div>
  )
}

export default ChatPanel
