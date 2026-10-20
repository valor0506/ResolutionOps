import { useState, useRef, useEffect } from 'react'
import { X, Send, Sparkles, Bot, User } from 'lucide-react'
import { apiFetch } from '../../lib/api'
import type { AskResponse, AssistantMessage } from '../../types/domain'

interface InvestigationAssistantProps {
  caseId: string
  caseName: string
  open: boolean
  onClose: () => void
}

const SUGGESTED_QUESTIONS = [
  'What happened in this case?',
  'What is the most likely root cause?',
  'What evidence do we have?',
  'Who is the customer and what is their SLA?',
  'What should I do next?',
]

export function InvestigationAssistant({ caseId, caseName, open, onClose }: InvestigationAssistantProps) {
  const [messages, setMessages] = useState<AssistantMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async (question?: string) => {
    const q = (question ?? input).trim()
    if (!q || loading) return

    const userMsg: AssistantMessage = { role: 'user', content: q }
    const updatedMessages = [...messages, userMsg]
    setMessages(updatedMessages)
    setInput('')
    setLoading(true)

    try {
      const res = await apiFetch<AskResponse>(`/assistant/cases/${caseId}/ask`, {
        method: 'POST',
        body: JSON.stringify({
          question: q,
          conversation_history: updatedMessages.slice(-6),
        }),
      })

      const assistantMsg: AssistantMessage = { role: 'assistant', content: res.answer }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg: AssistantMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${(err as Error).message}. Please try again.`,
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-y-0 right-0 w-[420px] bg-white border-l border-slate-200 shadow-2xl z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Bot className="h-4 w-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Investigation Assistant</h3>
            <p className="text-[11px] text-slate-500 truncate max-w-[260px]">{caseName}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-slate-200/60 text-slate-400 hover:text-slate-600 transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="space-y-4">
            <div className="bg-blue-50/60 border border-blue-200/60 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="h-4 w-4 text-blue-600" />
                <span className="text-xs font-semibold text-blue-900">AI-Powered Case Q&A</span>
              </div>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Ask me anything about this case. I answer using only verified evidence, diagnostic results, and knowledge articles — never guessing.
              </p>
            </div>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Suggested Questions
              </p>
              <div className="space-y-1.5">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => handleSend(q)}
                    className="w-full text-left px-3 py-2 rounded-lg border border-slate-200 text-xs text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="h-3.5 w-3.5 text-blue-600" />
              </div>
            )}
            <div
              className={`max-w-[85%] rounded-xl px-3.5 py-2.5 text-xs leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-800 border border-slate-200'
              }`}
            >
              <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
            </div>
            {msg.role === 'user' && (
              <div className="h-6 w-6 rounded-full bg-slate-200 flex items-center justify-center shrink-0 mt-0.5">
                <User className="h-3.5 w-3.5 text-slate-600" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-2.5">
            <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
              <Bot className="h-3.5 w-3.5 text-blue-600" />
            </div>
            <div className="bg-slate-100 border border-slate-200 rounded-xl px-4 py-3">
              <div className="flex gap-1.5">
                <div className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="px-5 py-4 border-t border-slate-200 bg-slate-50/50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about evidence, root cause, next steps..."
            disabled={loading}
            className="flex-1 rounded-lg border border-slate-200 bg-white py-2.5 px-3.5 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-3.5 py-2.5 text-white hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        </div>
        <p className="text-[10px] text-slate-400 mt-1.5 text-center">
          Responses are grounded in case evidence. AI does not fabricate information.
        </p>
      </div>
    </div>
  )
}

