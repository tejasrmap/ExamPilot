"use client";

import { useState, useRef } from "react";
import { api } from "@/lib/api";
import { 
  FileText, 
  UploadCloud, 
  RefreshCw, 
  CheckCircle2, 
  Layers, 
  Sparkles,
  ArrowRight
} from "lucide-react";
import Link from "next/link";

interface ExtractedMCQ {
  page_number: number;
  question: string;
  options: Record<string, string>;
  subject: string;
  confidence: number;
}

export default function PdfPapersPage() {
  const [loading, setLoading] = useState(false);
  const [pdfData, setPdfData] = useState<{
    filename: string;
    total_pages: number;
    processed_pages: number;
    questions: ExtractedMCQ[];
  } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMsg("Please upload a valid PDF document.");
      return;
    }
    setErrorMsg(null);
    setLoading(true);

    try {
      const res = await api.scanPdfFile(file, 15);
      setPdfData(res);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to process PDF question paper.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <FileText className="w-6 h-6 text-primary" />
          PDF Question Paper Processor
        </h1>
        <p className="text-sm text-muted">
          Upload PDF exam papers and problem sets. RapidOCR and PyMuPDF segment and extract questions page-by-page.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm">
          {errorMsg}
        </div>
      )}

      {/* Upload Box */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-cardBorder hover:border-primary/60 rounded-2xl p-10 bg-card flex flex-col items-center justify-center text-center cursor-pointer transition-colors"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFileUpload(f);
          }}
        />

        <div className="w-14 h-14 rounded-2xl bg-secondary/20 text-secondary mx-auto flex items-center justify-center mb-4">
          <UploadCloud className="w-7 h-7" />
        </div>
        <h2 className="text-base font-bold text-foreground">Upload Exam Question Paper PDF</h2>
        <p className="text-xs text-muted mt-1 max-w-sm">
          Upload midterms, finals, or practice test booklets. Both digital and scanned PDFs are supported.
        </p>
        <span className="mt-3 px-3 py-1 rounded bg-cardBorder text-[11px] text-muted font-mono">
          PDF up to 25MB (First 15 pages)
        </span>
      </div>

      {loading && (
        <div className="p-6 rounded-xl bg-card border border-cardBorder flex items-center justify-center gap-3 text-sm text-muted">
          <RefreshCw className="w-5 h-5 animate-spin text-primary" />
          <span>Rendering PDF pages and executing OCR segmentation pipeline...</span>
        </div>
      )}

      {/* Extracted Questions View */}
      {pdfData && (
        <div className="space-y-6 animate-in fade-in">
          {/* Summary Strip */}
          <div className="p-4 rounded-xl bg-[#101726] border border-cardBorder flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Layers className="w-5 h-5 text-primary" />
              <div>
                <p className="text-xs font-bold text-foreground">{pdfData.filename}</p>
                <p className="text-[11px] text-muted">
                  {pdfData.processed_pages} pages processed &bull; {pdfData.questions.length} multiple-choice questions detected
                </p>
              </div>
            </div>
            <span className="px-3 py-1 rounded bg-success/20 text-success text-xs font-bold">
              Extraction Complete
            </span>
          </div>

          {/* Questions Grid */}
          <div className="space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-muted">
              Detected Questions ({pdfData.questions.length})
            </h2>

            {pdfData.questions.length === 0 ? (
              <div className="p-8 text-center text-xs text-muted border border-dashed border-cardBorder rounded-xl">
                No multiple choice structures detected in this PDF.
              </div>
            ) : (
              pdfData.questions.map((q, idx) => (
                <div
                  key={idx}
                  className="p-5 rounded-xl bg-card border border-cardBorder hover:border-cardBorder/80 space-y-3 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-primary/20 text-primary-light mr-2">
                        Page {q.page_number}
                      </span>
                      <span className="text-xs font-semibold text-foreground">
                        {q.question}
                      </span>
                    </div>
                    <Link
                      href="/scanner"
                      className="shrink-0 px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-medium flex items-center gap-1.5 transition-colors"
                    >
                      Solve <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  {/* Options */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-muted pt-2 border-t border-cardBorder/50">
                    {Object.entries(q.options).map(([key, val]) => (
                      <div key={key} className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded bg-[#101726] border border-cardBorder font-bold text-[10px] flex items-center justify-center shrink-0 text-foreground">
                          {key}
                        </span>
                        <span className="truncate">{val}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

