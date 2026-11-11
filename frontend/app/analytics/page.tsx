"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { 
  BarChart3, 
  TrendingUp, 
  Zap, 
  ScanLine, 
  BookOpenCheck,
  Calendar,
  Layers,
  DollarSign
} from "lucide-react";

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>({
    total_questions_scanned: 0,
    practice_sessions_completed: 0,
    average_accuracy_percentage: 0,
    total_tokens_used: 0,
    estimated_api_cost_usd: 0,
    activity_last_7_days: []
  });
  const [subjectData, setSubjectData] = useState<any[]>([]);
  const [usageData, setUsageData] = useState<{ providers: any[]; recent_logs: any[] }>({
    providers: [],
    recent_logs: []
  });

  useEffect(() => {
    loadAllAnalytics();
  }, []);

  const loadAllAnalytics = async () => {
    try {
      const ov = await api.getAnalyticsOverview();
      setOverview(ov);
      const sub = await api.getSubjectAnalytics();
      setSubjectData(sub.subjects || []);
      const usg = await api.getUsageAnalytics();
      setUsageData(usg);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-primary" />
          Analytics & API Usage Dashboard
        </h1>
        <p className="text-sm text-muted">
          Transparent metrics on learning accuracy, subject performance, and external AI provider token spending.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-sm">
          <div className="flex items-center justify-between text-muted text-xs font-medium">
            <span>Questions Scanned</span>
            <ScanLine className="w-4 h-4 text-primary" />
          </div>
          <div className="mt-3 text-2xl font-bold text-foreground">
            {overview.total_questions_scanned}
          </div>
          <p className="mt-1 text-[11px] text-muted">Across all practice sets</p>
        </div>

        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-sm">
          <div className="flex items-center justify-between text-muted text-xs font-medium">
            <span>Practice Accuracy</span>
            <TrendingUp className="w-4 h-4 text-success" />
          </div>
          <div className="mt-3 text-2xl font-bold text-foreground">
            {overview.average_accuracy_percentage}%
          </div>
          <p className="mt-1 text-[11px] text-muted">Mean test score</p>
        </div>

        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-sm">
          <div className="flex items-center justify-between text-muted text-xs font-medium">
            <span>Total AI Tokens</span>
            <Zap className="w-4 h-4 text-secondary" />
          </div>
          <div className="mt-3 text-2xl font-bold text-foreground">
            {overview.total_tokens_used.toLocaleString()}
          </div>
          <p className="mt-1 text-[11px] text-muted">Input & output tokens consumed</p>
        </div>

        <div className="p-5 rounded-xl bg-card border border-cardBorder shadow-sm">
          <div className="flex items-center justify-between text-muted text-xs font-medium">
            <span>Estimated API Cost</span>
            <DollarSign className="w-4 h-4 text-warning" />
          </div>
          <div className="mt-3 text-2xl font-bold text-foreground">
            ${overview.estimated_api_cost_usd}
          </div>
          <p className="mt-1 text-[11px] text-muted">Direct provider pricing rate</p>
        </div>
      </div>

      {/* Subject Performance & Provider Spending Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Subject Mastery */}
        <div className="lg:col-span-6 bg-card border border-cardBorder rounded-xl p-6 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-muted flex items-center gap-2">
            <BookOpenCheck className="w-4 h-4 text-primary" />
            Subject Performance & Question Breakdown
          </h2>

          {subjectData.length === 0 ? (
            <div className="text-center py-8 text-xs text-muted">No subject data recorded yet.</div>
          ) : (
            <div className="space-y-3">
              {subjectData.map((s) => (
                <div key={s.subject} className="p-3.5 rounded-lg bg-[#101726] border border-cardBorder flex items-center justify-between text-xs">
                  <div>
                    <p className="font-semibold text-foreground">{s.subject}</p>
                    <p className="text-[11px] text-muted">{s.question_count} questions recorded</p>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-primary/20 text-primary-light font-bold">
                    {s.practice_accuracy}% Accuracy
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Provider Usage Summary */}
        <div className="lg:col-span-6 bg-card border border-cardBorder rounded-xl p-6 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-muted flex items-center gap-2">
            <Layers className="w-4 h-4 text-secondary" />
            Provider Token & Cost Breakdown
          </h2>

          {usageData.providers.length === 0 ? (
            <div className="text-center py-8 text-xs text-muted">No provider usage recorded yet.</div>
          ) : (
            <div className="space-y-3">
              {usageData.providers.map((p) => (
                <div key={p.provider} className="p-3.5 rounded-lg bg-[#101726] border border-cardBorder flex items-center justify-between text-xs">
                  <div>
                    <p className="font-bold text-foreground capitalize">{p.provider}</p>
                    <p className="text-[11px] text-muted">{p.requests} requests &bull; {(p.input_tokens + p.output_tokens).toLocaleString()} tokens</p>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-warning/20 text-warning font-mono font-bold">
                    ${p.estimated_cost}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Usage Audit Logs */}
      <div className="bg-card border border-cardBorder rounded-xl p-6 space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-wider text-muted flex items-center gap-2">
          <Calendar className="w-4 h-4 text-primary" />
          Recent API Request Logs
        </h2>

        {usageData.recent_logs.length === 0 ? (
          <div className="text-center py-10 text-xs text-muted border border-dashed border-cardBorder rounded-lg">
            No API requests logged yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-muted">
              <thead className="border-b border-cardBorder text-[11px] uppercase tracking-wider text-foreground">
                <tr>
                  <th className="py-2.5 px-3">Provider</th>
                  <th className="py-2.5 px-3">Model</th>
                  <th className="py-2.5 px-3">Feature</th>
                  <th className="py-2.5 px-3">Tokens (In / Out)</th>
                  <th className="py-2.5 px-3">Estimated Cost</th>
                  <th className="py-2.5 px-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cardBorder/50 font-mono">
                {usageData.recent_logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[#101726]">
                    <td className="py-2.5 px-3 capitalize font-sans font-medium text-foreground">{log.provider}</td>
                    <td className="py-2.5 px-3">{log.model}</td>
                    <td className="py-2.5 px-3 font-sans text-muted">{log.feature}</td>
                    <td className="py-2.5 px-3">{log.input_tokens} / {log.output_tokens}</td>
                    <td className="py-2.5 px-3 text-warning">${log.estimated_cost}</td>
                    <td className="py-2.5 px-3 text-muted">{new Date(log.created_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

