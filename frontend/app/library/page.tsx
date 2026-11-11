"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import { 
  Library, 
  UploadCloud, 
  Search, 
  Trash2, 
  FileText, 
  RefreshCw,
  BookMarked
} from "lucide-react";

export default function LibraryPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [subjectInput, setSubjectInput] = useState("Computer Science");

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const list = await api.listDocuments();
      setDocuments(list);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async (file: File) => {
    if (!file) return;
    setUploading(true);
    try {
      await api.uploadDocument(file, subjectInput);
      await loadDocuments();
    } catch (err: any) {
      alert("Failed to upload document: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.searchDocuments(searchQuery.trim());
      setSearchResults(res.chunks || []);
    } catch (err: any) {
      alert("Search failed: " + err.message);
    } finally {
      setSearching(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this study document?")) return;
    try {
      await api.deleteDocument(id);
      await loadDocuments();
    } catch (err: any) {
      alert("Failed to delete document: " + err.message);
    }
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Library className="w-6 h-6 text-primary" />
          Knowledge Library & Study Materials
        </h1>
        <p className="text-sm text-muted">
          Upload reference textbooks, course slides, or revision notes. Use RAG to query and cite supporting evidence.
        </p>
      </div>

      {/* Upload and Search Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Upload Box */}
        <div className="lg:col-span-5 bg-card border border-cardBorder rounded-xl p-6 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-muted">
            Upload Study Material
          </h2>

          <div>
            <label className="text-xs text-muted block mb-1.5">Subject Category</label>
            <input
              type="text"
              value={subjectInput}
              onChange={(e) => setSubjectInput(e.target.value)}
              placeholder="e.g. Computer Science, Economics"
              className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
            />
          </div>

          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-cardBorder hover:border-primary rounded-xl p-6 text-center cursor-pointer transition-colors"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.md"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleUpload(f);
              }}
            />
            {uploading ? (
              <div className="flex flex-col items-center justify-center py-2">
                <RefreshCw className="w-6 h-6 animate-spin text-primary mb-2" />
                <p className="text-xs text-muted">Indexing chunks for RAG...</p>
              </div>
            ) : (
              <div>
                <UploadCloud className="w-8 h-8 text-primary mx-auto mb-2" />
                <p className="text-xs font-semibold text-foreground">Click to upload document</p>
                <p className="text-[11px] text-muted mt-0.5">PDF or plain text up to 25MB</p>
              </div>
            )}
          </div>
        </div>

        {/* Semantic Search Box */}
        <div className="lg:col-span-7 bg-card border border-cardBorder rounded-xl p-6 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-muted">
            Search Reference Context (RAG)
          </h2>

          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search across all uploaded textbook passages..."
              className="flex-1 bg-[#101726] border border-cardBorder rounded-lg px-3.5 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
            />
            <button
              type="submit"
              disabled={searching || !searchQuery.trim()}
              className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center gap-2 disabled:opacity-40"
            >
              {searching ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
              Search
            </button>
          </form>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="space-y-3 pt-2">
              <p className="text-[11px] text-muted font-medium">Found {searchResults.length} relevant reference passages:</p>
              {searchResults.map((c, i) => (
                <div key={i} className="p-3.5 rounded-lg bg-[#101726] border border-cardBorder text-xs text-muted leading-relaxed">
                  <div className="flex items-center gap-2 mb-1 text-primary text-[11px] font-semibold">
                    <BookMarked className="w-3.5 h-3.5" />
                    Reference Match (Relevance: {c.score})
                  </div>
                  {c.content}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-card border border-cardBorder rounded-xl p-6 space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-wider text-muted">
          Your Uploaded Library ({documents.length})
        </h2>

        {documents.length === 0 ? (
          <div className="text-center py-10 text-xs text-muted border border-dashed border-cardBorder rounded-lg">
            No study documents uploaded yet. Upload course materials above to enable contextual RAG search.
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((d) => (
              <div
                key={d.id}
                className="p-4 rounded-lg bg-[#101726] border border-cardBorder flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-secondary/20 text-secondary flex items-center justify-center shrink-0">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-foreground">{d.filename}</p>
                    <p className="text-[11px] text-muted">
                      {d.subject_name} &bull; {(d.file_size_bytes / 1024).toFixed(1)} KB &bull; {d.page_count} pages
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(d.id)}
                  className="p-1.5 text-muted hover:text-danger rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

