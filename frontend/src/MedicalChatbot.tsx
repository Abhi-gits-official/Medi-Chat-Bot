import React, { useState, useEffect, useRef } from 'react';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatResponse {
  response: string;
}

// Keyword emphasis helper
function emphasizeTerms(text: string): string {
  const replacements: Array<{ pattern: RegExp; cls: string } | { pattern: RegExp; wrap: (m: string) => string }> = [
    { pattern: /\b(emergency|urgent|immediately|now)\b/gi, cls: 'font-semibold text-red-600' },
    { pattern: /\b(call (?:911|112)|911|112)\b/gi, cls: 'font-semibold text-red-600' },
    { pattern: /\b(difficulty breathing|chest pain|severe bleeding|stroke|allergic reaction|unresponsive|suicidal)\b/gi, cls: 'font-semibold text-red-600' },
    { pattern: /\b(red flags|worsening|seek care|today|same day)\b/gi, cls: 'font-semibold' },
    { pattern: /\b(acetaminophen|paracetamol|ibuprofen|hydration|rest)\b/gi, cls: 'font-semibold' },
  ];
  let out = text;
  for (const r of replacements) {
    if ('cls' in r) {
      out = out.replace(r.pattern, (m) => `<span class="${r.cls}">${m}</span>`);
    }
  }
  return out;
}

// Minimal RTF -> HTML converter for our controlled subset
function rtfToHtml(rtf: string): string {
  try {
    let s = rtf;

    // Fast path: if the content already looks like HTML, just return as-is
    if (/<\w+[^>]*>/.test(s)) return s;

    // Remove font table groups to reduce noise
    s = s.replace(/\{\\fonttbl[\s\S]*?\}/g, '');

    // Convert bold/italic controls first (RTF)
    s = s.replace(/\\b0/g, '</strong>');
    s = s.replace(/\\b(?![a-zA-Z])/g, '<strong>');
    s = s.replace(/\\i0/g, '</em>');
    s = s.replace(/\\i(?![a-zA-Z])/g, '<em>');

    // Basic Markdown-to-HTML for common patterns in model output
    // Bold: **text**
    s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Italic: *text* (avoid bullets "* ")
    s = s.replace(/(^|[^*])\*(?!\s)([^*]+)\*(?!\*)/g, '$1<em>$2</em>');

    // Paragraphs -> line breaks for structuring
    s = s.replace(/\\par\b/g, '\n');

    // Remove other RTF control words (keep the ones already transformed)
    s = s.replace(/\\[a-zA-Z]+-?\d*/g, '');

    // Remove braces
    s = s.replace(/[{}]/g, '');

    // Decode simple escaped backslashes (best effort)
    s = s.replace(/\\\\/g, '\\');

    // Normalize whitespace
    s = s.replace(/\r/g, '');

    const stripTags = (t: string) => t.replace(/<[^>]+>/g, '').trim();
    const headingEmoji = (h: string) => {
      const t = h.toLowerCase();
      if (t.includes('immediate relief')) return '🆘 ';
      if (t.includes('possible causes')) return '🔎 ';
      if (t.includes('what you can do now') || t.includes('steps')) return '🧰 ';
      if (t.includes('when to get medical help') || t.includes('red flags')) return '⚠️ ';
      if (t.includes('brief empathy')) return '💙 ';
      if (t.includes('supportive reassurance')) return '🤝 ';
      if (t.includes('one follow-up question') || t.includes('follow-up')) return '❓ ';
      if (t.includes('disclaimer')) return 'ℹ️ ';
      if (t.includes('key details')) return '📝 ';
      if (t.includes('assumptions')) return '🧩 ';
      return '';
    };

    const lines = s.split(/\n+/).map(l => l.trim()).filter(Boolean);

    // Build HTML with lists and paragraphs
    const html: string[] = [];
    let inList = false;
    let listType: 'ul' | 'ol' | null = null;
    let currentSection: string | null = null;
    let titleHandled = false;
    let openWrapper: 'alert' | 'info' | null = null;

    const startList = (type: 'ul' | 'ol' = 'ul') => {
      if (!inList || listType !== type) {
        if (inList) { html.push(listType === 'ul' ? '</ul>' : '</ol>'); }
        if (type === 'ul') {
          html.push('<ul class="list-disc pl-5 space-y-1">');
        } else {
          html.push('<ol class="list-decimal pl-5 space-y-1">');
        }
        inList = true;
        listType = type;
      }
    };
    const endList = () => {
      if (inList) {
        html.push(listType === 'ul' ? '</ul>' : '</ol>');
        inList = false;
        listType = null;
      }
    };

    const closeWrapper = () => {
      if (openWrapper) {
        html.push('</div>');
        openWrapper = null;
      }
    };

    const openAlertWrapper = () => {
      if (openWrapper !== 'alert') {
        closeWrapper();
        html.push('<div class="rounded-md border border-red-200 bg-red-50 p-3">');
        openWrapper = 'alert';
      }
    };

    const openInfoWrapper = () => {
      if (openWrapper !== 'info') {
        closeWrapper();
        html.push('<div class="rounded-md border border-blue-200 bg-blue-50 p-3">');
        openWrapper = 'info';
      }
    };

    for (const raw of lines) {
      let line = raw;

      // Title line detection
      const plain = stripTags(line).toLowerCase();
      if (!titleHandled && /medical assistant response/.test(plain)) {
        titleHandled = true;
        closeWrapper();
        endList();
        html.push('<h2 class="text-lg font-semibold tracking-tight mb-2">Medical Assistant Response</h2>');
        continue;
      }

      // Handle inline keywords list e.g., "Keywords: fever, cough, rest"
      const kwMatch = line.match(/^\s*(Keywords|Important|Important words):\s*(.+)$/i);
      if (kwMatch) {
        const heading = kwMatch[1];
        const items = kwMatch[2].split(/[,;]\s*/).filter(Boolean);
        closeWrapper();
        endList();
        html.push(`<h3 class="mt-3 mb-1 font-semibold">${headingEmoji(heading)}${heading}</h3>`);
        if (items.length) {
          startList('ul');
          for (const it of items) {
            html.push(`<li>${emphasizeTerms(it)}</li>`);
          }
          endList();
        }
        currentSection = heading.toLowerCase();
        continue;
      }

      // Numbered bullet items (ordered list): 1. or 1)
      const numMatch = line.match(/^(\d+)[\.)]\s+(.*)$/);
      if (numMatch) {
        const itemRaw = emphasizeTerms(numMatch[2]);
        if (currentSection && /(what you can do now|direct answer|steps|immediate relief)/i.test(currentSection)) {
          openInfoWrapper();
        }
        startList('ol');
        html.push(`<li>${itemRaw}</li>`);
        continue;
      }

      // Unordered bullet items: -, •, *
      const bulletMatch = line.match(/^([-•*])\s+(.*)$/);
      if (bulletMatch) {
        const itemText = bulletMatch[2];
        const itemRaw = emphasizeTerms(itemText);
        if (currentSection && /(get medical help|red flags|when to get medical help)/i.test(currentSection)) {
          openAlertWrapper();
          startList('ul');
          html.push(`<li><span class="text-red-700">⚠️ ${itemRaw}</span></li>`);
        } else {
          if (currentSection && /(what you can do now|direct answer|steps|immediate relief)/i.test(currentSection)) {
            openInfoWrapper();
            startList('ul');
            html.push(`<li>✅ ${itemRaw}</li>`);
          } else {
            startList('ul');
            html.push(`<li>${itemRaw}</li>`);
          }
        }
        continue;
      }

      // Heading-like lines ending with ':'
      if (/.*:\s*$/.test(line) && !/^<strong>/.test(line)) {
        endList();
        const heading = stripTags(line.replace(/:$/, ''));
        currentSection = heading.toLowerCase();
        if (/(get medical help|red flags|when to get medical help)/i.test(currentSection)) {
          openAlertWrapper();
        } else if (/(what you can do now|direct answer|steps|immediate relief)/i.test(currentSection)) {
          openInfoWrapper();
        } else {
          closeWrapper();
        }
        html.push(`<h3 class="mt-3 mb-1 font-semibold">${headingEmoji(heading)}${heading}</h3>`);
        continue;
      }

      // Regular paragraph
      endList();
      const content = emphasizeTerms(line);
      if (currentSection && /disclaimer/i.test(currentSection)) {
        closeWrapper();
        html.push(`<p class="text-xs text-gray-600 italic">${content}</p>`);
      } else {
        html.push(`<p>${content}</p>`);
      }
    }
    endList();
    closeWrapper();

    return html.join('');
  } catch (e) {
    // Fallback to escaped plain text
    const escaped = rtf
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br/>');
    return `<p>${escaped}</p>`;
  }
}

const MedicalChatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initial greeting message
  useEffect(() => {
    const initialMessage: Message = {
      id: '1',
      content: "Hello! I'm your medical assistant. How can I help you today?",
      isUser: false,
      timestamp: new Date()
    };
    setMessages([initialMessage]);
  }, []);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (inputMessage.trim() === '' || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          conversation_history: messages.map(msg => ({
            content: msg.content,
            isUser: msg.isUser
          }))
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data: ChatResponse = await response.json();

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, I'm having trouble connecting right now. Please try again later.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Disclaimer Banner */}
      <div className="bg-red-50 border-l-4 border-red-400 p-4 shadow-sm">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-red-700">
              <strong>Disclaimer:</strong> This chatbot provides general medical information and is not a substitute for professional medical advice, diagnosis, or treatment. In case of a medical emergency, please call your local emergency services immediately.
            </p>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <svg className="h-8 w-8 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            Medical Assistant
          </h1>
          <p className="text-gray-600 mt-1">Get reliable medical information and first aid guidance</p>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-900 shadow-sm border border-gray-200'
                }`}
              >
                {message.isUser ? (
                  <>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className={`text-xs mt-1 ${message.isUser ? 'text-blue-100' : 'text-gray-500'}`}>
                      {formatTime(message.timestamp)}
                    </p>
                  </>
                ) : (
                  <>
                    <div
                      className="text-sm prose prose-sm lg:prose-base max-w-none prose-p:my-2 prose-li:my-1 prose-ol:my-1 prose-ul:my-1 prose-strong:font-semibold prose-h3:mt-3 prose-h3:mb-1"
                      dangerouslySetInnerHTML={{ __html: rtfToHtml(message.content) }}
                    />
                    <p className="text-xs mt-1 text-gray-500">{formatTime(message.timestamp)}</p>
                  </>
                )}
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 shadow-sm border border-gray-200 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-gray-500">Medical assistant is typing...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-4">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your symptoms or ask a medical question..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={2}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={isLoading || inputMessage.trim() === ''}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedicalChatbot;
