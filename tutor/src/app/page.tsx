"use client";

import { useRenderToolCall } from "@copilotkit/react-core";
import { CopilotChat, CopilotKitCSSProperties } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { useEffect, useRef, useState } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { oneDark } from "@codemirror/theme-one-dark";

const SUGGESTIONS = [
  { title: "Text Gen", message: "Show me how to call Claude Haiku using the Converse API." },
  { title: "Compare Models", message: "Run the same prompt through Claude Haiku, Nova Lite, and Llama 3.1 70B and compare responses." },
  { title: "RAG", message: "Show me the RetrieveAndGenerate API with a working example." },
  { title: "Image Gen", message: "Show me how to generate an image with Nova Canvas." },
  { title: "Streaming", message: "Show me how to stream a response token-by-token using converse_stream." },
  { title: "Tool Use", message: "Demonstrate function calling in Bedrock — define a tool spec and handle the response." },
];

const CHAT_MIN = 28;
const CHAT_MAX = 65;
const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL || "http://localhost:8000";

const STARTER_CODE = `import boto3

client = boto3.client('bedrock-runtime', region_name='us-west-2')

response = client.converse(
    modelId='us.anthropic.claude-haiku-4-5-20251001-v1:0',
    messages=[{'role': 'user', 'content': [{'text': 'Say hello!'}]}],
    inferenceConfig={'temperature': 0.0, 'maxTokens': 200}
)
print(response['output']['message']['content'][0]['text'])
`;

export default function BedrockTutorPage() {
  const [code, setCode] = useState(STARTER_CODE);
  const [streamingCode, setStreamingCode] = useState<string | null>(null); // code being streamed in
  const [output, setOutput] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [chatWidth, setChatWidth] = useState(42);
  const containerRef = useRef<HTMLDivElement>(null);
  const dividerRef = useRef<HTMLDivElement>(null);

  // Draggable divider
  useEffect(() => {
    const divider = dividerRef.current;
    const container = containerRef.current;
    let dragging = false;
    const onMouseDown = () => { dragging = true; document.body.style.cursor = "col-resize"; document.body.style.userSelect = "none"; };
    const onMouseMove = (e: MouseEvent) => {
      if (!dragging || !container) return;
      const rect = container.getBoundingClientRect();
      const pct = ((e.clientX - rect.left) / rect.width) * 100;
      setChatWidth(Math.max(CHAT_MIN, Math.min(CHAT_MAX, pct)));
    };
    const onMouseUp = () => { dragging = false; document.body.style.cursor = ""; document.body.style.userSelect = ""; };
    divider?.addEventListener("mousedown", onMouseDown);
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
    return () => {
      divider?.removeEventListener("mousedown", onMouseDown);
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };
  }, []);

  // Agent writes code to scratchpad — streams in progressively
  useRenderToolCall({
    name: "update_scratchpad",
    parameters: [{ name: "code", description: "Python code to display", required: true }],
    render: (props) => {
      const incoming = props.args.code ?? "";

      useEffect(() => {
        if (props.status !== "complete") {
          setStreamingCode(incoming);
        }
        if (props.status === "complete") {
          setStreamingCode(null);
          setCode(incoming);
          setOutput(null);
        }
      }, [incoming, props.status]);

      if (props.status === "complete") {
        return (
          <span className="inline-flex items-center gap-1.5 text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 rounded px-2 py-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            code ready → edit &amp; run →
          </span>
        );
      }
      return (
        <span className="inline-flex items-center gap-1.5 text-xs font-mono text-orange-400 bg-orange-950/40 border border-orange-800/40 rounded px-2 py-0.5">
          <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
          writing code…
        </span>
      );
    },
  });

  // Inline indicator when agent runs code itself
  useRenderToolCall({
    name: "run_bedrock_code",
    parameters: [{ name: "code", description: "Python code to execute", required: true }],
    render: (props) => {
      if (props.status === "complete") {
        return (
          <span className="inline-flex items-center gap-1.5 text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 rounded px-2 py-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            done
          </span>
        );
      }
      return (
        <span className="inline-flex items-center gap-1.5 text-xs font-mono text-orange-400 bg-orange-950/40 border border-orange-800/40 rounded px-2 py-0.5">
          <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
          running…
        </span>
      );
    },
  });

  const runCode = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setOutput(null);
    try {
      const res = await fetch(`${AGENT_URL}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      const data = await res.json();
      setOutput(data.output ?? "(no output)");
    } catch (e) {
      setOutput(`Error: could not reach agent\n${e}`);
    } finally {
      setIsRunning(false);
    }
  };

  const displayCode = streamingCode ?? code;
  const isStreaming = streamingCode !== null;

  return (
    <div
      data-theme="dark"
      style={{
        "--copilot-kit-primary-color": "#FF9900",
        "--copilot-kit-contrast-color": "#000000",
        "--copilot-kit-background-color": "#0f1117",
        "--copilot-kit-secondary-color": "#1a1d27",
        "--copilot-kit-secondary-contrast-color": "#ffffff",
        "--copilot-kit-separator-color": "rgba(255,255,255,0.06)",
        "--copilot-kit-muted-color": "rgba(255,255,255,0.35)",
        "--copilot-kit-input-background-color": "#1a1d27",
      } as CopilotKitCSSProperties}
      className="h-screen flex flex-col bg-[#0b0d14] overflow-hidden"
    >
      {/* Top bar */}
      <header className="flex items-center justify-between px-4 border-b border-white/5 bg-[#0f1117] shrink-0" style={{ height: 36 }}>
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 rounded bg-orange-500 flex items-center justify-center text-[10px] font-bold text-black">B</div>
          <span className="text-sm font-semibold text-white/80 tracking-tight">Bedrock Workshop</span>
          <span className="text-xs text-white/25 font-mono">tutor</span>
        </div>
        <div className="flex items-center gap-3">
          {isRunning && (
            <div className="flex items-center gap-1.5 text-xs text-orange-400 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-ping" />
              running
            </div>
          )}
          <span className="text-xs text-white/20 font-mono">{process.env.NEXT_PUBLIC_MODEL_LABEL ?? "Claude Sonnet"} · us-west-2</span>
        </div>
      </header>

      {/* Main panels */}
      <div className="flex flex-1 overflow-hidden" ref={containerRef}>

        {/* Left: Chat */}
        <div className="flex flex-col overflow-hidden border-r border-white/5" style={{ width: `${chatWidth}%` }}>
          <div className="flex gap-1.5 px-3 py-2 border-b border-white/5 bg-[#0f1117] overflow-x-auto shrink-0 scrollbar-hide">
            {SUGGESTIONS.map((s) => (
              <button
                key={s.title}
                onClick={() => {
                  const input = document.querySelector<HTMLTextAreaElement>(".copilotKitInput textarea");
                  if (input) {
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")!.set;
                    setter?.call(input, s.message);
                    input.dispatchEvent(new Event("input", { bubbles: true }));
                    input.focus();
                  }
                }}
                className="shrink-0 text-[11px] font-mono text-white/40 bg-white/4 hover:bg-orange-500/10 hover:text-orange-400 hover:border-orange-500/25 border border-white/6 rounded-full px-3 py-0.5 transition-all duration-150 cursor-pointer whitespace-nowrap"
              >
                {s.title}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-hidden [&_.copilotKitHeader]:hidden [&_.copilotKitButton]:hidden [&_.copilotKitChat]:bg-[#0f1117] [&_.copilotKitChat]:h-full [&_.copilotKitMessages]:bg-[#0f1117] [&_.copilotKitInputControls]:bg-[#1a1d27] [&_.copilotKitInput]:border-t [&_.copilotKitInput]:border-white/5">
            <CopilotChat
              className="h-full"
              labels={{
                title: "Bedrock Tutor",
                initial: "👋 Welcome! I'm your Amazon Bedrock tutor.\n\nAsk me anything — I'll explain concepts and write runnable code directly into the editor on the right. Edit it, run it, break it, learn from it.\n\nNo labs, no steps. Just explore.",
              }}
            />
          </div>
        </div>

        {/* Divider */}
        <div
          ref={dividerRef}
          className="w-px shrink-0 bg-white/5 hover:bg-orange-500/30 cursor-col-resize transition-colors duration-150"
        />

        {/* Right: Scratchpad + Output */}
        <div className="flex-1 flex flex-col overflow-hidden bg-[#0b0d14] min-w-0">

          {/* Scratchpad */}
          <div className="flex flex-col border-b border-white/5" style={{ height: "55%" }}>
            {/* Scratchpad header — label + streaming indicator only */}
            <div className="flex items-center gap-2 px-4 shrink-0 border-b border-white/5" style={{ height: 34 }}>
              <span className="text-[10px] font-mono uppercase tracking-widest text-white/30">Scratchpad</span>
              {isStreaming && (
                <span className="flex items-center gap-1 text-[10px] font-mono text-orange-400">
                  <span className="w-1 h-1 rounded-full bg-orange-400 animate-pulse" />
                  writing…
                </span>
              )}
            </div>

            {/* CodeMirror editor */}
            <div
              className="flex-1 overflow-hidden"
              onKeyDown={(e) => {
                if ((e.metaKey || e.ctrlKey) && e.key === "Enter") { e.preventDefault(); runCode(); }
              }}
            >
              <CodeMirror
                value={displayCode}
                onChange={(val) => { if (!isStreaming) setCode(val); }}
                height="100%"
                theme={oneDark}
                extensions={[python()]}
                readOnly={isStreaming}
                basicSetup={{
                  lineNumbers: true,
                  highlightActiveLine: !isStreaming,
                  foldGutter: false,
                  dropCursor: false,
                  allowMultipleSelections: false,
                  indentOnInput: true,
                  bracketMatching: true,
                  closeBrackets: true,
                  autocompletion: true,
                  tabSize: 4,
                }}
                style={{ height: "100%", fontSize: 14 }}
              />
            </div>

            {/* Run button row — bottom of scratchpad */}
            <div className="flex items-center justify-between px-3 py-2 border-t border-white/5 shrink-0">
              <button
                onClick={runCode}
                disabled={isRunning || isStreaming}
                className="flex items-center gap-1.5 text-xs font-mono px-3 py-1.5 rounded bg-orange-500 hover:bg-orange-400 disabled:opacity-40 disabled:cursor-not-allowed text-black font-semibold transition-colors cursor-pointer"
              >
                {isRunning ? (
                  <><span className="w-1.5 h-1.5 rounded-full bg-black/50 animate-pulse" />running…</>
                ) : (
                  <><span className="text-[10px]">▶</span>Run</>
                )}
              </button>
              <span className="text-[10px] text-white/15 font-mono">⌘↵</span>
            </div>
          </div>

          {/* Output */}
          <div className="flex flex-col flex-1 overflow-hidden">
            <div className="flex items-center justify-between px-4 shrink-0 border-b border-white/5" style={{ height: 34 }}>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono uppercase tracking-widest text-white/30">Output</span>
                {isRunning && <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />}
                {output && !isRunning && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />}
              </div>
              {output && (
                <button
                  onClick={() => navigator.clipboard.writeText(output)}
                  className="text-[10px] font-mono text-white/20 hover:text-white/50 transition-colors cursor-pointer"
                >
                  copy
                </button>
              )}
            </div>
            <div className="flex-1 overflow-y-auto px-4 py-3">
              {isRunning ? (
                <div className="flex items-center gap-2 text-xs font-mono text-white/30">
                  <span className="animate-pulse">▋</span> executing…
                </div>
              ) : output ? (
                <pre
                  className="text-[14px] font-mono leading-relaxed whitespace-pre-wrap break-words"
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    color: (output.startsWith("Error") || output.includes("Traceback") || output.includes("Exception")) ? "#f87171" : "#86efac",
                  }}
                >
                  {output}
                </pre>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <p className="text-[11px] font-mono text-white/15">hit Run or press ⌘↵</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
