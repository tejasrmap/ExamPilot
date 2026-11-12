"use client";

import { useEffect, useState } from "react";
import { api, ProviderItem } from "@/lib/api";
import { 
  KeyRound, 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  Trash2, 
  RefreshCw, 
  Lock, 
  Sparkles,
  ExternalLink,
  Star
} from "lucide-react";

interface ModelItem {
  id: string;
  name: string;
  provider: string;
  supports_vision: boolean;
  context_window: number;
}

const PROVIDERS_CONFIG = [
  {
    id: "openai",
    name: "OpenAI",
    description: "GPT-4o, GPT-4o Mini, o3-mini models",
    docsUrl: "https://platform.openai.com/api-keys",
    placeholder: "sk-proj-..."
  },
  {
    id: "gemini",
    name: "Google Gemini",
    description: "Gemini 2.0 Flash, Gemini 1.5 Pro multimodal models",
    docsUrl: "https://aistudio.google.com/app/apikey",
    placeholder: "AIzaSy..."
  },
  {
    id: "anthropic",
    name: "Anthropic Claude",
    description: "Claude 3.5 Sonnet, Claude 3.5 Haiku",
    docsUrl: "https://console.anthropic.com/settings/keys",
    placeholder: "sk-ant-api03-..."
  },
  {
    id: "openrouter",
    name: "OpenRouter",
    description: "DeepSeek V3, Llama 3.3 70B, multi-model router",
    docsUrl: "https://openrouter.ai/keys",
    placeholder: "sk-or-v1-..."
  }
];

export default function ProvidersPage() {
  const [savedProviders, setSavedProviders] = useState<ProviderItem[]>([]);
  const [selectedProvider, setSelectedProvider] = useState("openai");
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [availableModels, setAvailableModels] = useState<ModelItem[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [isDefault, setIsDefault] = useState(false);

  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadProviders();
  }, []);

  useEffect(() => {
    loadModels(selectedProvider);
    setTestResult(null);
    setApiKeyInput("");
  }, [selectedProvider]);

  const loadProviders = async () => {
    try {
      const list = await api.getProviders();
      setSavedProviders(list);
    } catch (err: any) {
      console.error("Failed to load providers:", err);
    }
  };

  const loadModels = async (prov: string) => {
    try {
      const models = await api.getModels(prov);
      setAvailableModels(models);
      if (models.length > 0) {
        setSelectedModel(models[0].id);
      }
    } catch {
      setAvailableModels([]);
    }
  };

  const handleTestConnection = async () => {
    if (!apiKeyInput.trim()) {
      setErrorMsg("Please enter an API key to test.");
      return;
    }
    setErrorMsg(null);
    setTesting(true);
    setTestResult(null);

    try {
      const res = await api.testProvider(selectedProvider, apiKeyInput.trim());
      setTestResult({
        success: res.success,
        message: res.message
      });
    } catch (err: any) {
      setTestResult({
        success: false,
        message: err.message || "Failed to reach provider endpoint."
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSaveProvider = async () => {
    if (!apiKeyInput.trim()) {
      setErrorMsg("API key cannot be empty.");
      return;
    }
    setErrorMsg(null);
    setSaving(true);

    try {
      await api.saveProvider(selectedProvider, apiKeyInput.trim(), selectedModel, isDefault);
      setApiKeyInput("");
      setTestResult(null);
      await loadProviders();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to save API key.");
    } finally {
      setSaving(false);
    }
  };

  const handleSetDefault = async (prov: string) => {
    try {
      await api.setDefaultProvider(prov);
      await loadProviders();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to set default provider.");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to remove this provider key?")) return;
    try {
      await api.deleteProvider(id);
      await loadProviders();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to delete provider.");
    }
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <KeyRound className="w-6 h-6 text-primary" />
          API Provider Management (BYOK)
        </h1>
        <p className="text-sm text-muted">
          Connect your own API credentials for OpenAI, Google Gemini, Anthropic Claude, and OpenRouter.
        </p>
      </div>

      {/* Security Banner */}
      <div className="p-4 rounded-xl bg-[#101726] border border-cardBorder flex items-start gap-3.5">
        <ShieldCheck className="w-5 h-5 text-success shrink-0 mt-0.5" />
        <div className="text-xs text-muted leading-relaxed">
          <p className="font-semibold text-foreground mb-0.5">Enterprise AES-256-GCM Hardware-Grade Encryption</p>
          API keys are securely encrypted at rest using server-side AES-256-GCM. Your plain keys are never logged, never returned to the frontend, and never exposed in JavaScript bundles.
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm">
          {errorMsg}
        </div>
      )}

      {/* Provider Configurator */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Select Provider & Inputs */}
        <div className="lg:col-span-7 bg-card border border-cardBorder rounded-xl p-6 space-y-6">
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-muted mb-3 block">
              1. Select AI Provider
            </label>
            <div className="grid grid-cols-2 gap-3">
              {PROVIDERS_CONFIG.map((p) => {
                const isSelected = selectedProvider === p.id;
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setSelectedProvider(p.id)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      isSelected
                        ? "bg-primary/10 border-primary text-foreground"
                        : "bg-[#101726] border-cardBorder text-muted hover:border-cardBorder/80"
                    }`}
                  >
                    <p className="text-xs font-bold text-foreground">{p.name}</p>
                    <p className="text-[10px] text-muted truncate mt-0.5">{p.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Key Input */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold uppercase tracking-wider text-muted">
                2. Enter API Key
              </label>
              <a
                href={PROVIDERS_CONFIG.find(p => p.id === selectedProvider)?.docsUrl}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-primary hover:underline flex items-center gap-1 font-medium"
              >
                Get API Key <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <div className="relative">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder={PROVIDERS_CONFIG.find(p => p.id === selectedProvider)?.placeholder}
                className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3.5 py-2.5 text-xs text-foreground focus:outline-none focus:border-primary font-mono placeholder:text-muted/40"
              />
              <Lock className="w-3.5 h-3.5 text-muted absolute right-3.5 top-3" />
            </div>
          </div>

          {/* Model Selector */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-muted mb-2 block">
              3. Default Model Selection
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary"
            >
              {availableModels.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.id})
                </option>
              ))}
            </select>
          </div>

          {/* Make Default checkbox */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="isDefaultCheck"
              checked={isDefault}
              onChange={(e) => setIsDefault(e.target.checked)}
              className="rounded bg-[#101726] border-cardBorder text-primary focus:ring-0"
            />
            <label htmlFor="isDefaultCheck" className="text-xs text-muted cursor-pointer">
              Set as primary default provider for question analysis
            </label>
          </div>

          {/* Test Status feedback */}
          {testResult && (
            <div className={`p-3.5 rounded-lg border text-xs flex items-center gap-2.5 ${
              testResult.success
                ? "bg-success/10 border-success/30 text-success"
                : "bg-danger/10 border-danger/30 text-danger"
            }`}>
              {testResult.success ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <XCircle className="w-4 h-4 shrink-0" />}
              <span>{testResult.message}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={handleTestConnection}
              disabled={testing || !apiKeyInput.trim()}
              className="px-4 py-2.5 rounded-lg bg-[#101726] border border-cardBorder hover:border-primary text-foreground text-xs font-medium flex items-center gap-2 transition-colors disabled:opacity-40"
            >
              {testing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-primary" />}
              Test Connection
            </button>

            <button
              type="button"
              onClick={handleSaveProvider}
              disabled={saving || !apiKeyInput.trim()}
              className="flex-1 py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-md shadow-primary/20 flex items-center justify-center gap-2 transition-all disabled:opacity-40"
            >
              {saving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
              Save & Encrypt Key
            </button>
          </div>
        </div>

        {/* Right Column: Connected Providers List */}
        <div className="lg:col-span-5 bg-card border border-cardBorder rounded-xl p-6 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-muted">
            Configured Providers ({savedProviders.length})
          </h2>

          {savedProviders.length === 0 ? (
            <div className="text-center py-10 border border-dashed border-cardBorder rounded-lg text-xs text-muted">
              No API providers configured yet.
              <p className="mt-1 text-[11px] text-muted/80">Add your first key to start solving questions.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {savedProviders.map((p) => (
                <div
                  key={p.id}
                  className="p-4 rounded-lg bg-[#101726] border border-cardBorder hover:border-cardBorder/80 space-y-2 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-foreground uppercase tracking-wider flex items-center gap-1.5">
                      {p.provider}
                      {p.is_default && (
                        <span className="px-1.5 py-0.5 rounded bg-primary/20 text-primary-light text-[10px] font-mono font-normal flex items-center gap-1">
                          <Star className="w-2.5 h-2.5 fill-primary" /> Default
                        </span>
                      )}
                    </span>
                    <span className={`text-[10px] px-2 py-0.5 rounded font-semibold capitalize ${
                      p.status === "connected" ? "bg-success/20 text-success" : "bg-danger/20 text-danger"
                    }`}>
                      {p.status}
                    </span>
                  </div>

                  <p className="text-xs font-mono text-muted">{p.masked_key}</p>
                  
                  <div className="flex items-center justify-between text-[11px] text-muted pt-1 border-t border-cardBorder/50">
                    <span>Model: {p.default_model || "auto"}</span>
                    <div className="flex items-center gap-2">
                      {!p.is_default && (
                        <button
                          type="button"
                          onClick={() => handleSetDefault(p.provider)}
                          className="text-primary hover:underline"
                        >
                          Set Default
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => handleDelete(p.id)}
                        className="text-muted hover:text-danger p-1"
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
      </div>
    </div>
  );
}

