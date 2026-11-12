"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { 
  BookOpenCheck, 
  Play, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  ArrowRight, 
  ArrowLeft,
  RefreshCw,
  Trophy
} from "lucide-react";

interface QuestionItem {
  id: string;
  question_text: string;
  options: Record<string, string>;
  subject?: string;
}

interface TestResult {
  session_id: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  results: {
    question_id: string;
    question_text: string;
    options: Record<string, string>;
    selected_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
  }[];
}

export default function PracticePage() {
  const [testHistory, setTestHistory] = useState<any[]>([]);
  const [activeSession, setActiveSession] = useState<{
    session_id: string;
    title: string;
    questions: QuestionItem[];
    time_limit_minutes: number;
  } | null>(null);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [submitting, setSubmitting] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);

  // Form state to start test
  const [testTitle, setTestTitle] = useState("Architecture & CS Practice");
  const [selectedSubject, setSelectedSubject] = useState("Computer Science");
  const [questionCount, setQuestionCount] = useState(5);
  const [timeLimit, setTimeLimit] = useState(10);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  // Timer countdown
  useEffect(() => {
    if (!activeSession || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          handleSubmitTest();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [activeSession, timeLeft]);

  const loadHistory = async () => {
    try {
      const h = await api.listPracticeSessions();
      setTestHistory(h);
    } catch (err) {
      console.error(err);
    }
  };

  const handleStartTest = async () => {
    setStarting(true);
    setTestResult(null);
    try {
      const res = await api.createPracticeTest(testTitle, selectedSubject, questionCount, timeLimit);
      setActiveSession(res);
      setCurrentIndex(0);
      setSelectedAnswers({});
      setTimeLeft((res.time_limit_minutes || 10) * 60);
    } catch (err: any) {
      alert("Failed to start practice test: " + err.message);
    } finally {
      setStarting(false);
    }
  };

  const handleSelectOption = (optKey: string) => {
    if (!activeSession) return;
    const qId = activeSession.questions[currentIndex].id;
    setSelectedAnswers(prev => ({ ...prev, [qId]: optKey }));
  };

  const handleSubmitTest = async () => {
    if (!activeSession || submitting) return;
    setSubmitting(true);

    const answersPayload = activeSession.questions.map(q => ({
      question_id: q.id,
      selected_answer: selectedAnswers[q.id] || "unanswered"
    }));

    try {
      const res = await api.submitPracticeTest(activeSession.session_id, answersPayload);
      setTestResult(res);
      setActiveSession(null);
      await loadHistory();
    } catch (err: any) {
      alert("Failed to submit test: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <BookOpenCheck className="w-6 h-6 text-primary" />
          Interactive Practice Test Environment
        </h1>
        <p className="text-sm text-muted">
          Challenge yourself with timed quizzes generated from scanned questions and course curricula.
        </p>
      </div>

      {/* Test Active Runner */}
      {activeSession && (
        <div className="rounded-2xl bg-card border border-primary/40 p-8 shadow-2xl space-y-6">
          {/* Top Bar: Progress & Timer */}
          <div className="flex items-center justify-between pb-4 border-b border-cardBorder">
            <div>
              <p className="text-xs text-muted uppercase font-bold tracking-wider">
                {activeSession.title}
              </p>
              <p className="text-sm font-semibold text-foreground">
                Question {currentIndex + 1} of {activeSession.questions.length}
              </p>
            </div>

            <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-[#101726] border border-cardBorder text-warning font-mono font-bold text-sm">
              <Clock className="w-4 h-4" />
              {formatTimer(timeLeft)}
            </div>
          </div>

          {/* Current Question */}
          {activeSession.questions[currentIndex] && (
            <div className="space-y-6">
              <h2 className="text-base font-semibold text-foreground leading-relaxed">
                {activeSession.questions[currentIndex].question_text}
              </h2>

              {/* Options Radio List */}
              <div className="space-y-3">
                {Object.entries(activeSession.questions[currentIndex].options).map(([letter, text]) => {
                  const currentQId = activeSession.questions[currentIndex].id;
                  const isSelected = selectedAnswers[currentQId] === letter;
                  return (
                    <div
                      key={letter}
                      onClick={() => handleSelectOption(letter)}
                      className={`p-4 rounded-xl border flex items-center gap-3.5 cursor-pointer transition-all ${
                        isSelected
                          ? "bg-primary/10 border-primary text-foreground shadow-sm"
                          : "bg-[#101726] border-cardBorder text-muted hover:border-cardBorder/80 hover:text-foreground"
                      }`}
                    >
                      <div className={`w-7 h-7 rounded-lg font-bold text-xs flex items-center justify-center shrink-0 ${
                        isSelected ? "bg-primary text-white" : "bg-cardBorder text-muted"
                      }`}>
                        {letter}
                      </div>
                      <span className="text-sm leading-relaxed">{text}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Navigation Controls */}
          <div className="flex items-center justify-between pt-4 border-t border-cardBorder">
            <button
              onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="px-4 py-2 rounded-lg bg-[#101726] border border-cardBorder text-xs font-medium text-foreground hover:border-primary disabled:opacity-40 flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" /> Previous
            </button>

            {currentIndex < activeSession.questions.length - 1 ? (
              <button
                onClick={() => setCurrentIndex(prev => Math.min(activeSession.questions.length - 1, prev + 1))}
                className="px-5 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center gap-2"
              >
                Next <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSubmitTest}
                disabled={submitting}
                className="px-6 py-2 rounded-lg bg-success hover:bg-success/90 text-white text-xs font-bold shadow-md shadow-success/20 flex items-center gap-2"
              >
                {submitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                Submit & Grade Test
              </button>
            )}
          </div>
        </div>
      )}

      {/* Test Results Banner */}
      {testResult && (
        <div className="rounded-2xl bg-card border border-success/40 p-8 shadow-xl space-y-6 animate-in fade-in">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-cardBorder">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-success/20 text-success flex items-center justify-center">
                <Trophy className="w-7 h-7" />
              </div>
              <div>
                <h2 className="text-2xl font-extrabold text-foreground">
                  Score: {testResult.score_percentage}%
                </h2>
                <p className="text-xs text-muted">
                  {testResult.correct_answers} of {testResult.total_questions} questions answered correctly
                </p>
              </div>
            </div>

            <button
              onClick={() => setTestResult(null)}
              className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold"
            >
              Take Another Quiz
            </button>
          </div>

          {/* Breakdown List */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-muted">
              Question Review & Pedagogical Breakdown
            </h3>
            {testResult.results.map((r, i) => (
              <div
                key={r.question_id}
                className={`p-5 rounded-xl border space-y-3 ${
                  r.is_correct ? "bg-success/5 border-success/30" : "bg-danger/5 border-danger/30"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <p className="text-sm font-semibold text-foreground">
                    {i + 1}. {r.question_text}
                  </p>
                  <span className={`shrink-0 px-2.5 py-1 rounded-md text-xs font-bold flex items-center gap-1.5 ${
                    r.is_correct ? "bg-success/20 text-success" : "bg-danger/20 text-danger"
                  }`}>
                    {r.is_correct ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                    {r.is_correct ? "Correct" : "Incorrect"}
                  </span>
                </div>

                <div className="text-xs space-y-1">
                  <p className="text-muted">
                    Your Answer: <span className="font-bold text-foreground">Option {r.selected_answer}</span>
                  </p>
                  {!r.is_correct && (
                    <p className="text-success font-medium">
                      Correct Answer: <span className="font-bold">Option {r.correct_answer}</span>
                    </p>
                  )}
                </div>

                {r.explanation && (
                  <p className="p-3 rounded-lg bg-[#101726] border border-cardBorder text-xs text-muted leading-relaxed">
                    <span className="font-semibold text-foreground">Explanation: </span>
                    {r.explanation}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Start Quiz Form & History */}
      {!activeSession && !testResult && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Create Test Config */}
          <div className="lg:col-span-6 bg-card border border-cardBorder rounded-xl p-6 space-y-5">
            <h2 className="text-xs font-bold uppercase tracking-wider text-muted">
              Configure New Practice Session
            </h2>

            <div>
              <label className="text-xs text-muted block mb-1.5">Quiz Title</label>
              <input
                type="text"
                value={testTitle}
                onChange={(e) => setTestTitle(e.target.value)}
                className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-muted block mb-1.5">Subject</label>
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
                >
                  <option value="Computer Science">Computer Science</option>
                  <option value="Business & Finance">Business & Finance</option>
                  <option value="Mathematics">Mathematics</option>
                  <option value="All">All Subjects</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-muted block mb-1.5">Question Count</label>
                <input
                  type="number"
                  min={1}
                  max={25}
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                  className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-muted block mb-1.5">Time Limit (Minutes)</label>
              <input
                type="number"
                min={1}
                max={60}
                value={timeLimit}
                onChange={(e) => setTimeLimit(Number(e.target.value))}
                className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
              />
            </div>

            <button
              onClick={handleStartTest}
              disabled={starting}
              className="w-full py-3 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-bold shadow-lg shadow-primary/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {starting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Start Practice Session
            </button>
          </div>

          {/* Test History */}
          <div className="lg:col-span-6 bg-card border border-cardBorder rounded-xl p-6 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-muted">
              Past Practice Tests ({testHistory.length})
            </h2>

            {testHistory.length === 0 ? (
              <div className="text-center py-12 text-xs text-muted border border-dashed border-cardBorder rounded-lg">
                No past sessions recorded. Complete your first test above!
              </div>
            ) : (
              <div className="space-y-3 max-h-[360px] overflow-y-auto">
                {testHistory.map((h) => (
                  <div
                    key={h.id}
                    className="p-3.5 rounded-lg bg-[#101726] border border-cardBorder flex items-center justify-between"
                  >
                    <div>
                      <p className="text-xs font-semibold text-foreground">{h.title}</p>
                      <p className="text-[11px] text-muted">
                        {h.correct_answers} / {h.total_questions} correct &bull; {h.subject_name}
                      </p>
                    </div>
                    <span className="px-2.5 py-1 rounded bg-success/20 text-success text-xs font-bold font-mono">
                      {h.score_percentage}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

