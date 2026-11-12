"use client";

import { useState, useRef } from "react";
import { api, QuestionAnalysis } from "@/lib/api";
import { 
  ScanLine, 
  UploadCloud, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Copy, 
  Check, 
  RefreshCw, 
  HelpCircle,
  Plus,
  Trash2
} from "lucide-react";

export default function ScannerPage() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loadingOcr, setLoadingOcr] = useState(false);
  const [loadingAi, setLoadingAi] = useState(false);
  
  // Question & Options form state
  const [questionText, setQuestionText] = useState("");
  const [options, setOptions] = useState<Record<string, string>>({
    A: "",
    B: "",
    C: "",
    D: ""
  });
  const [detectedDomain, setDetectedDomain] = useState("Computer Science");
  const [analysisResult, setAnalysisResult] = useState<QuestionAnalysis | null>(null);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    if (!file) return;
    setErrorMsg(null);
    setLoadingOcr(true);
    setAnalysisResult(null);

    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    try {
      const data = await api.scanImageFile(file);
      if (data.parsed_question) {
        setQuestionText(data.parsed_question);
      } else if (data.raw_text) {
        setQuestionText(data.raw_text);
      }

      if (data.options && Object.keys(data.options).length > 0) {
        setOptions(data.options);
      }
      if (data.detected_domain) {
        setDetectedDomain(data.detected_domain);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to extract text from image.");
    } finally {
      setLoadingOcr(false);
    }
  };

  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          handleFileUpload(file);
          break;
        }
      }
    }
  };

  const handleOptionChange = (key: string, value: string) => {
    setOptions(prev => ({ ...prev, [key]: value }));
  };

  const addOption = () => {
    const keys = ["A", "B", "C", "D", "E", "F"];
    const existing = Object.keys(options);
    const nextKey = keys.find(k => !existing.includes(k));
    if (nextKey) {
      setOptions(prev => ({ ...prev, [nextKey]: "" }));
    }
  };

  const removeOption = (key: string) => {
    const updated = { ...options };
    delete updated[key];
    setOptions(updated);
  };

  const handleAnalyze = async () => {
    if (!questionText.trim()) {
      setErrorMsg("Please enter or scan a question first.");
      return;
    }
    const cleanOpts: Record<string, string> = {};
    for (const [k, v] of Object.entries(options)) {
      if (v.trim()) cleanOpts[k] = v.trim();
    }
    if (Object.keys(cleanOpts).length < 2) {
      setErrorMsg("At least two options are required to analyze an MCQ.");
      return;
    }

    setErrorMsg(null);
    setLoadingAi(true);

    try {
      const res = await api.analyseQuestion({
        question_text: questionText,
        options: cleanOpts,
        subject: detectedDomain
      });
      setAnalysisResult(res);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to analyze question with AI provider.");
    } finally {
      setLoadingAi(false);
    }
  };

  const copyExplanation = () => {
    if (!analysisResult) return;
    const txt = `Correct Answer: Option ${analysisResult.suggested_answer} (${analysisResult.answer_text})\n\nExplanation:\n${analysisResult.explanation}`;
    navigator.clipboard.writeText(txt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6" onPaste={handlePaste}>
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <ScanLine className="w-6 h-6 text-primary" />
          Question Scanner & AI Solver
        </h1>
        <p className="text-sm text-muted">
          Upload or paste a practice-question screenshot (Ctrl+V). RapidOCR extracts text and AI decomposes each option.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Grid: Upload & Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Image Dropzone & Preview */}
        <div className="lg:col-span-5 space-y-4">
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-cardBorder hover:border-primary/60 rounded-xl p-6 bg-card flex flex-col items-center justify-center text-center cursor-pointer transition-colors min-h-[220px]"
          >
            <input 
              ref={fileInputRef}
              type="file" 
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileUpload(file);
              }}
            />
            {imagePreview ? (
              <div className="w-full">
                <img 
                  src={imagePreview} 
                  alt="Scanned question preview" 
                  className="max-h-56 mx-auto rounded-lg object-contain shadow-md"
                />
                <p className="mt-3 text-xs text-muted">Click or paste again to replace image</p>
              </div>
            ) : (
              <div>
                <div className="w-12 h-12 rounded-xl bg-primary/20 text-primary mx-auto flex items-center justify-center mb-3">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <p className="text-sm font-semibold text-foreground">Click to upload screenshot</p>
                <p className="text-xs text-muted mt-1">or paste screenshot directly (Ctrl + V)</p>
                <span className="inline-block mt-3 px-2.5 py-1 rounded-md bg-cardBorder text-[11px] text-muted font-mono">
                  PNG, JPG, WebP up to 25MB
                </span>
              </div>
            )}
          </div>

          {loadingOcr && (
            <div className="p-3.5 rounded-lg bg-primary/10 border border-primary/20 flex items-center gap-3 text-xs text-primary-light">
              <RefreshCw className="w-4 h-4 animate-spin text-primary" />
              <span>Running RapidOCR spatial sorting and question boundary parsing...</span>
            </div>
          )}
        </div>

        {/* Right Column: Question & Options Editor */}
        <div className="lg:col-span-7 bg-card border border-cardBorder rounded-xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold uppercase tracking-wider text-muted">
              Question Statement
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted">Subject:</span>
              <select
                value={detectedDomain}
                onChange={(e) => setDetectedDomain(e.target.value)}
                className="text-xs bg-[#101625] border border-cardBorder rounded-md px-2.5 py-1 text-foreground focus:outline-none focus:border-primary"
              >
                <option value="Computer Science">Computer Science</option>
                <option value="Business & Finance">Business & Finance</option>
                <option value="Electrical Engineering">Electrical Engineering</option>
                <option value="Mathematics">Mathematics</option>
                <option value="Data Science">Data Science</option>
                <option value="General">General</option>
              </select>
            </div>
          </div>

          <textarea
            value={questionText}
            onChange={(e) => setQuestionText(e.target.value)}
            rows={3}
            placeholder="Question statement extracted via OCR or entered manually..."
            className="w-full bg-[#101726] border border-cardBorder rounded-lg p-3 text-sm text-foreground focus:outline-none focus:border-primary placeholder:text-muted/60"
          />

          {/* Options List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-muted">
                Multiple Choice Options
              </label>
              <button
                type="button"
                onClick={addOption}
                className="text-xs text-primary hover:underline flex items-center gap-1 font-medium"
              >
                <Plus className="w-3.5 h-3.5" /> Add Option
              </button>
            </div>

            <div className="space-y-2.5">
              {Object.entries(options).map(([key, val]) => (
                <div key={key} className="flex items-center gap-2.5">
                  <span className="w-7 h-7 rounded-md bg-[#101625] border border-cardBorder text-primary font-bold text-xs flex items-center justify-center shrink-0">
                    {key}
                  </span>
                  <input
                    type="text"
                    value={val}
                    onChange={(e) => handleOptionChange(key, e.target.value)}
                    placeholder={`Option ${key} text...`}
                    className="flex-1 bg-[#101726] border border-cardBorder rounded-lg px-3 py-1.5 text-xs text-foreground focus:outline-none focus:border-primary placeholder:text-muted/50"
                  />
                  {Object.keys(options).length > 2 && (
                    <button
                      type="button"
                      onClick={() => removeOption(key)}
                      className="text-muted hover:text-danger p-1 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Action Button */}
          <button
            onClick={handleAnalyze}
            disabled={loadingAi}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-primary to-primary-hover text-white text-sm font-semibold shadow-lg shadow-primary/25 hover:shadow-primary/40 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            {loadingAi ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Analyzing with AI Provider...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Analyse Question with AI
              </>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Results View */}
      {analysisResult && (
        <div className="rounded-2xl bg-card border border-cardBorder p-6 sm:p-8 space-y-6 shadow-xl animate-in fade-in duration-300">
          {/* Header Badge */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-cardBorder">
            <div className="flex items-center gap-3">
              <span className="px-3.5 py-1.5 rounded-lg bg-success/20 text-success font-extrabold text-sm border border-success/30 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                Suggested Answer: Option {analysisResult.suggested_answer}
              </span>
              <span className="text-xs px-2.5 py-1 rounded bg-[#101625] text-muted border border-cardBorder">
                Subject: {analysisResult.subject}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-xs text-muted">Confidence: </span>
                <span className={`text-xs font-bold capitalize ${
                  analysisResult.confidence.level === "high" ? "text-success" : "text-warning"
                }`}>
                  {analysisResult.confidence.level}
                </span>
              </div>
              <button
                onClick={copyExplanation}
                className="px-3 py-1.5 rounded-lg bg-[#101625] border border-cardBorder hover:border-primary text-xs font-medium text-foreground flex items-center gap-1.5 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5 text-muted" />}
                {copied ? "Copied!" : "Copy Explanation"}
              </button>
            </div>
          </div>

          {/* Correct Option Banner */}
          <div className="p-4 rounded-xl bg-success/10 border border-success/20">
            <p className="text-xs font-bold text-success uppercase tracking-wider mb-1">
              Correct Answer Text
            </p>
            <p className="text-sm font-semibold text-foreground">
              {analysisResult.answer_text}
            </p>
          </div>

          {/* Confidence Reason */}
          <div className="p-4 rounded-xl bg-[#101726] border border-cardBorder">
            <p className="text-xs font-bold text-muted uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-primary" />
              Calibrated Confidence Assessment
            </p>
            <p className="text-xs text-muted leading-relaxed">
              {analysisResult.confidence.reason}
            </p>
          </div>

          {/* Explanation */}
          <div>
            <h3 className="text-sm font-bold text-foreground uppercase tracking-wider mb-2">
              Comprehensive Pedagogical Explanation
            </h3>
            <div className="p-5 rounded-xl bg-[#101726] border border-cardBorder text-sm text-foreground leading-relaxed whitespace-pre-wrap">
              {analysisResult.explanation}
            </div>
          </div>

          {/* Option-by-Option Breakdown */}
          {analysisResult.option_analysis && (
            <div>
              <h3 className="text-sm font-bold text-foreground uppercase tracking-wider mb-3">
                Option-by-Option Breakdown
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(analysisResult.option_analysis).map(([opt, reason]) => {
                  const isCorrect = opt.toUpperCase() === analysisResult.suggested_answer.toUpperCase();
                  return (
                    <div 
                      key={opt}
                      className={`p-4 rounded-xl border ${
                        isCorrect 
                          ? "bg-success/5 border-success/30" 
                          : "bg-[#101726] border-cardBorder"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className={`w-6 h-6 rounded-md font-bold text-xs flex items-center justify-center ${
                          isCorrect ? "bg-success text-white" : "bg-cardBorder text-muted"
                        }`}>
                          {opt}
                        </span>
                        <span className={`text-xs font-semibold ${isCorrect ? "text-success" : "text-muted"}`}>
                          {isCorrect ? "Correct Option" : "Distractor"}
                        </span>
                      </div>
                      <p className="text-xs text-muted leading-relaxed">
                        {reason}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

