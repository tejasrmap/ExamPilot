"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import { 
  BotMessageSquare, 
  Send, 
  Sparkles, 
  User, 
  RefreshCw, 
  Plus, 
  BookOpen, 
  HelpCircle,
  Code
} from "lucide-react";

interface MessageItem {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

interface ConversationItem {
  id: string;
  title: string;
  messages: MessageItem[];
}

export default function AssistantPage() {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputContent, setInputContent] = useState("");
  const [loadingReply, setLoadingReply] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (activeConvId) {
      loadMessages(activeConvId);
    }
  }, [activeConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loadingReply]);

  const loadConversations = async () => {
    try {
      const list = await api.getConversations();
      setConversations(list);
      if (list.length > 0 && !activeConvId) {
        setActiveConvId(list[0].id);
      } else if (list.length === 0) {
        // Create initial conversation
        const initial = await api.createConversation("Exam Preparation Tutoring");
        setConversations([initial]);
        setActiveConvId(initial.id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadMessages = async (convId: string) => {
    try {
      const conv = await api.getConversation(convId);
      setMessages(conv.messages || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleNewConversation = async () => {
    try {
      const conv = await api.createConversation("New Study Session");
      setConversations(prev => [conv, ...prev]);
      setActiveConvId(conv.id);
      setMessages(conv.messages || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputContent;
    if (!text.trim() || !activeConvId || loadingReply) return;

    setInputContent("");
    const tempUserMsg: MessageItem = {
      id: "temp-" + Date.now(),
      role: "user",
      content: text.trim(),
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);
    setLoadingReply(true);

    try {
      const replyMsg = await api.sendChatMessage(activeConvId, text.trim());
      setMessages(prev => [...prev, replyMsg]);
    } catch (err: any) {
      const errMsg: MessageItem = {
        id: "err-" + Date.now(),
        role: "assistant",
        content: `Sorry, an error occurred while connecting to the AI provider: ${err.message}`,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoadingReply(false);
    }
  };

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-cardBorder">
        <div>
          <h1 className="text-xl font-bold text-foreground flex items-center gap-2">
            <BotMessageSquare className="w-5 h-5 text-primary" />
            AI Conceptual Study Assistant
          </h1>
          <p className="text-xs text-muted">
            Ask questions, clarify tricky distractors, or request on-demand practice questions.
          </p>
        </div>
        <button
          onClick={handleNewConversation}
          className="px-3 py-1.5 rounded-lg bg-card border border-cardBorder hover:border-primary text-xs font-medium text-foreground flex items-center gap-1.5 transition-colors"
        >
          <Plus className="w-3.5 h-3.5 text-primary" /> New Chat
        </button>
      </div>

      {/* Main Chat Interface */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-4 overflow-hidden">
        {/* Sidebar: Conversation Sessions */}
        <div className="hidden md:flex flex-col bg-card border border-cardBorder rounded-xl p-3 space-y-2 overflow-y-auto">
          <p className="text-[11px] font-bold uppercase tracking-wider text-muted px-2 py-1">
            Recent Sessions
          </p>
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => setActiveConvId(c.id)}
              className={`w-full text-left p-2.5 rounded-lg text-xs font-medium transition-colors truncate ${
                activeConvId === c.id
                  ? "bg-primary text-white"
                  : "text-muted hover:text-foreground hover:bg-[#101726]"
              }`}
            >
              {c.title}
            </button>
          ))}
        </div>

        {/* Chat Thread */}
        <div className="md:col-span-3 flex flex-col bg-card border border-cardBorder rounded-xl overflow-hidden">
          {/* Messages Scroll Area */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4">
            {messages.map((m) => {
              const isAssistant = m.role === "assistant";
              return (
                <div
                  key={m.id}
                  className={`flex items-start gap-3 ${isAssistant ? "" : "flex-row-reverse"}`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    isAssistant ? "bg-primary/20 text-primary" : "bg-secondary/20 text-secondary"
                  }`}>
                    {isAssistant ? <Sparkles className="w-4 h-4" /> : <User className="w-4 h-4" />}
                  </div>
                  <div className={`p-4 rounded-xl text-xs leading-relaxed max-w-2xl whitespace-pre-wrap ${
                    isAssistant
                      ? "bg-[#101726] border border-cardBorder text-foreground shadow-sm"
                      : "bg-primary text-white shadow-md shadow-primary/20"
                  }`}>
                    {m.content}
                  </div>
                </div>
              );
            })}

            {loadingReply && (
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-primary/20 text-primary flex items-center justify-center shrink-0">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                </div>
                <div className="p-3.5 rounded-xl bg-[#101726] border border-cardBorder text-xs text-muted flex items-center gap-2">
                  <span>Generating pedagogical tutor response...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Study Prompts */}
          <div className="px-6 py-2 border-t border-cardBorder bg-[#101625]/40 flex gap-2 overflow-x-auto text-xs">
            <button
              onClick={() => handleSendMessage("Can you generate 3 similar practice questions on this topic with answer keys?")}
              className="px-2.5 py-1 rounded-md bg-[#101726] hover:bg-cardBorder border border-cardBorder text-[11px] text-muted whitespace-nowrap flex items-center gap-1.5"
            >
              <BookOpen className="w-3 h-3 text-primary" /> Generate Similar MCQs
            </button>
            <button
              onClick={() => handleSendMessage("Please summarize the foundational principle behind this topic in simple terms.")}
              className="px-2.5 py-1 rounded-md bg-[#101726] hover:bg-cardBorder border border-cardBorder text-[11px] text-muted whitespace-nowrap flex items-center gap-1.5"
            >
              <HelpCircle className="w-3 h-3 text-secondary" /> Simplify Concept
            </button>
            <button
              onClick={() => handleSendMessage("How do I avoid common trick traps and distractors for these types of questions?")}
              className="px-2.5 py-1 rounded-md bg-[#101726] hover:bg-cardBorder border border-cardBorder text-[11px] text-muted whitespace-nowrap flex items-center gap-1.5"
            >
              <Code className="w-3 h-3 text-success" /> Identify Traps
            </button>
          </div>

          {/* Input Box */}
          <div className="p-4 border-t border-cardBorder bg-[#101726]/60">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={inputContent}
                onChange={(e) => setInputContent(e.target.value)}
                placeholder="Ask your tutor anything or paste a concept..."
                className="flex-1 bg-[#090D18] border border-cardBorder rounded-xl px-4 py-2.5 text-xs text-foreground focus:outline-none focus:border-primary placeholder:text-muted/50"
              />
              <button
                type="submit"
                disabled={!inputContent.trim() || loadingReply}
                className="px-4 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-md shadow-primary/25 disabled:opacity-40 flex items-center gap-1.5 transition-all"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

