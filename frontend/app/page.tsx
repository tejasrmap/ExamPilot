"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, QuestionRecord } from "@/lib/api";
import { 
  ScanLine, 
  BookOpenCheck, 
  BarChart3, 
  KeyRound, 
  ArrowRight, 
  CheckCircle2, 
  Sparkles,
  Zap,
  TrendingUp,
  Clock
} from "lucide-react";

export default function OverviewPage() {
  const [stats, setStats] = useState<any>({
    total_questions_scanned: 0,
    practice_sessions_completed: 0,
    average_accuracy_percentage: 0,
    total_tokens_used: 0,
    estimated_api_cost_usd: 0
  });
  const [recentQuestions, setRecentQuestions] = useState<QuestionRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const ov = await api.getAnalyticsOverview();
        setStats(ov);
        const qs = await api.getQuestions();
        setRecentQuestions(qs.slice(0, 5));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Welcome Hero */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-card via-[#182338] to-card border border-cardBorder p-8 shadow-xl">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 text-primary-light text-xs font-semibold mb-4 border border-primary/30">
            <Sparkles className="w-3.5 h-3.5" />
            ExamPilot 2.0 Online SaaS
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
            Understand Questions. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
              Learn the Answers.
            </span>
          </h1>
          <p className="mt-3 text-muted text-sm leading-relaxed">
            Extract, parse, and master multiple-choice questions with enterprise-grade cloud AI inference, calibrated confidence metrics, and deep pedagogical option analysis.
          </p>

          <div className="mt-6 flex flex-wrap gap-4">
            <Link
              href="/scanner"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-semibold shadow-lg shadow-primary/30 transition-all hover:translate-y-[-1px]"
            >
              <ScanLine className="w-4 h-4" />
              Open Question Scanner
            </Link>
            <Link
              href="/providers"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-card border border-cardBorder hover:border-primary text-foreground text-sm font-medium transition-colors"
            >
              <KeyRound className="w-4 h-4 text-primary" />
              Manage API Providers
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-sm">
          <div className="flex items-center justify-between text-muted text-xs font-medium">
            <span>Questions Analysed</span>
            <ScanLine className="w-4 h-4 text-primary" />
          </div>
          <div className="mt-3 text-2xl font-bold text-foreground">
            {stats.total_questions_scanned}
          </div>
          <p className="mt-1 text-[11px] text-muted">Across all subjects</p>
        </div>

        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-sm">
          <div className="flex items-center justify-between text-muted text-xs font-medium">
            <span>Practice Accuracy</span>
            <TrendingUp className="w-4 h-4 text-success" />
          </div>
          <div className="mt-3 text-2xl font-bold text-foreground">
            {stats.average_accuracy_percentage}%
          </div>
          <p className="mt-1 text-[11px] text-muted">From completed test sessions</p>
        </div>

        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-sm">
          <div className="flex items-center justify-between text-muted text-xs font-medium">
            <span>Practice Tests</span>
            <BookOpenCheck className="w-4 h-4 text-secondary" />
          </div>
          <div className="mt-3 text-2xl font-bold text-foreground">
            {stats.practice_sessions_completed}
          </div>
          <p className="mt-1 text-[11px] text-muted">Timed practice tests completed</p>
        </div>

        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-sm">
          <div className="flex items-center justify-between text-muted text-xs font-medium">
            <span>API Spending</span>
            <Zap className="w-4 h-4 text-warning" />
          </div>
          <div className="mt-3 text-2xl font-bold text-foreground">
            ${stats.estimated_api_cost_usd}
          </div>
          <p className="mt-1 text-[11px] text-muted">{stats.total_tokens_used.toLocaleString()} tokens tracked</p>
        </div>
      </div>

      {/* Recent Activity & Quick Navigation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Questions List */}
        <div className="lg:col-span-2 rounded-xl bg-card border border-cardBorder p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-foreground flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" />
              Recent Question Analysis
            </h2>
            <Link href="/history" className="text-xs text-primary hover:underline flex items-center gap-1 font-medium">
              View all <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {recentQuestions.length === 0 ? (
            <div className="text-center py-12 border border-dashed border-cardBorder rounded-lg">
              <p className="text-sm text-muted">No questions analysed yet.</p>
              <Link href="/scanner" className="inline-block mt-3 text-xs text-primary font-medium hover:underline">
                Start by scanning an MCQ &rarr;
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentQuestions.map((q) => (
                <div key={q.id} className="p-4 rounded-lg bg-[#101726] border border-cardBorder hover:border-primary/40 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <p className="text-xs font-medium text-foreground line-clamp-2">
                      {q.question_text}
                    </p>
                    <span className="shrink-0 px-2.5 py-1 rounded-md bg-primary/20 text-primary-light font-bold text-xs">
                      Option {q.suggested_answer}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center gap-3 text-[11px] text-muted">
                    <span className="px-2 py-0.5 rounded bg-cardBorder text-foreground font-medium">
                      {q.subject || "General"}
                    </span>
                    <span>Confidence: {q.confidence_level}</span>
                    <span>&bull;</span>
                    <span>{new Date(q.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Tools */}
        <div className="rounded-xl bg-card border border-cardBorder p-6 shadow-sm space-y-4">
          <h2 className="text-base font-bold text-foreground">Quick Actions</h2>
          
          <Link
            href="/scanner"
            className="flex items-center justify-between p-3.5 rounded-lg bg-[#101726] border border-cardBorder hover:border-primary transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/20 text-primary flex items-center justify-center">
                <ScanLine className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-semibold text-foreground">Scan Screenshot</p>
                <p className="text-[11px] text-muted">Extract and solve question</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-muted group-hover:text-primary transition-colors" />
          </Link>

          <Link
            href="/pdf-papers"
            className="flex items-center justify-between p-3.5 rounded-lg bg-[#101726] border border-cardBorder hover:border-primary transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-secondary/20 text-secondary flex items-center justify-center">
                <BookOpenCheck className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-semibold text-foreground">PDF Exam Papers</p>
                <p className="text-[11px] text-muted">Batch extract full test papers</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-muted group-hover:text-primary transition-colors" />
          </Link>

          <Link
            href="/assistant"
            className="flex items-center justify-between p-3.5 rounded-lg bg-[#101726] border border-cardBorder hover:border-primary transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-success/20 text-success flex items-center justify-center">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-semibold text-foreground">AI Study Assistant</p>
                <p className="text-[11px] text-muted">Ask questions & clarify concepts</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-muted group-hover:text-primary transition-colors" />
          </Link>
        </div>
      </div>
    </div>
  );
}

