"use client";

import { useEffect, useState } from "react";
import { api, QuestionRecord } from "@/lib/api";
import { 
  History, 
  Search, 
  Trash2, 
  CheckCircle2, 
  ThumbsUp, 
  ThumbsDown, 
  AlertTriangle,
  RotateCcw
} from "lucide-react";
import Link from "next/link";

export default function HistoryPage() {
  const [questions, setQuestions] = useState<QuestionRecord[]>([]);
  const [search, setSearch] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuestions();
  }, [selectedSubject]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const data = await api.getQuestions(search, selectedSubject);
      setQuestions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadQuestions();
  };

  const handleFeedback = async (qId: string, feedback: string) => {
    try {
      await api.submitFeedback(qId, feedback);
      setQuestions(prev => prev.map(q => q.id === qId ? { ...q, user_feedback: feedback } : q));
    } catch (err: any) {
      alert("Failed to record feedback: " + err.message);
    }
  };

  const handleDelete = async (qId: string) => {
    if (!confirm("Are you sure you want to remove this question from history?")) return;
    try {
      await api.deleteQuestion(qId);
      setQuestions(prev => prev.filter(q => q.id !== qId));
    } catch (err: any) {
      alert("Failed to delete question: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <History className="w-6 h-6 text-primary" />
          Question History & Feedback
        </h1>
        <p className="text-sm text-muted">
          Review previously scanned questions, verify pedagogical explanations, and record feedback.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center gap-4 bg-card border border-cardBorder p-4 rounded-xl">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex gap-2 min-w-[280px]">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search questions by keyword..."
            className="flex-1 bg-[#101726] border border-cardBorder rounded-lg px-3.5 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center gap-1.5"
          >
            <Search className="w-3.5 h-3.5" /> Search
          </button>
        </form>

        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">Subject:</span>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
          >
            <option value="All">All Subjects</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Business & Finance">Business & Finance</option>
            <option value="Mathematics">Mathematics</option>
            <option value="General">General</option>
          </select>
        </div>
      </div>

      {/* Questions List */}
      {loading ? (
        <div className="py-16 text-center text-xs text-muted">
          Loading question history...
        </div>
      ) : questions.length === 0 ? (
        <div className="py-16 text-center text-xs text-muted border border-dashed border-cardBorder rounded-xl bg-card">
          No questions found matching your criteria.
        </div>
      ) : (
        <div className="space-y-4">
          {questions.map((q) => (
            <div
              key={q.id}
              className="p-6 rounded-xl bg-card border border-cardBorder hover:border-cardBorder/80 space-y-4 shadow-sm transition-all"
            >
              {/* Question Statement & Answer Badge */}
              <div className="flex items-start justify-between gap-4">
                <p className="text-sm font-semibold text-foreground leading-relaxed">
                  {q.question_text}
                </p>
                <span className="shrink-0 px-3 py-1.5 rounded-lg bg-success/20 text-success font-extrabold text-xs border border-success/30 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {q.original_label
                    ? `Option ${q.original_label}`
                    : `${q.answer_text} (Item #${q.source_position || 1})`}
                </span>
              </div>

              {/* Options */}
              {q.options && Object.keys(q.options).length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  {Object.entries(q.options).map(([letter, text]) => {
                    const isSuggested = letter.toUpperCase() === (q.suggested_answer || "").toUpperCase();
                    return (
                      <div
                        key={letter}
                        className={`p-2.5 rounded-lg border flex items-center gap-2 ${
                          isSuggested
                            ? "bg-success/10 border-success/30 text-foreground font-medium"
                            : "bg-[#101726] border-cardBorder text-muted"
                        }`}
                      >
                        <span className={`w-5 h-5 rounded font-bold text-[10px] flex items-center justify-center shrink-0 ${
                          isSuggested ? "bg-success text-white" : "bg-cardBorder text-muted"
                        }`}>
                          {letter}
                        </span>
                        <span className="truncate">{text}</span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Explanation */}
              {q.explanation && (
                <div className="p-3.5 rounded-lg bg-[#101726] border border-cardBorder text-xs text-muted leading-relaxed">
                  <p className="font-semibold text-foreground mb-1">Explanation:</p>
                  {q.explanation}
                </div>
              )}

              {/* Footer: Metadata & Feedback Actions */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-cardBorder/60 text-xs text-muted">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-cardBorder text-foreground font-medium text-[11px]">
                    {q.subject || "General"}
                  </span>
                  <span>Provider: <span className="text-foreground capitalize">{q.provider}</span> ({q.model})</span>
                  <span>&bull;</span>
                  <span>{new Date(q.created_at).toLocaleDateString()}</span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-muted mr-1">Feedback:</span>
                  <button
                    onClick={() => handleFeedback(q.id, "correct")}
                    className={`p-1.5 rounded-lg border transition-colors ${
                      q.user_feedback === "correct"
                        ? "bg-success text-white border-success"
                        : "bg-[#101726] border-cardBorder hover:border-success text-muted"
                    }`}
                    title="Mark correct"
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => handleFeedback(q.id, "incorrect")}
                    className={`p-1.5 rounded-lg border transition-colors ${
                      q.user_feedback === "incorrect"
                        ? "bg-danger text-white border-danger"
                        : "bg-[#101726] border-cardBorder hover:border-danger text-muted"
                    }`}
                    title="Mark incorrect"
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => handleDelete(q.id)}
                    className="p-1.5 text-muted hover:text-danger rounded-lg transition-colors ml-2"
                    title="Delete question"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

