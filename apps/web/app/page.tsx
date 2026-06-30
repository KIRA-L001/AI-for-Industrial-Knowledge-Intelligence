"use client";

import { motion } from "framer-motion";
import {
  ArrowRight,
  BrainCircuit,
  FileSearch,
  Network,
  Quote,
  ScanLine,
  ShieldCheck,
  Sparkles,
  Workflow,
  Boxes,
  GitBranch,
  Gauge,
} from "lucide-react";
import Link from "next/link";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] as const },
  }),
};

const STANDARDS = ["OISD", "PESO", "Factory Act", "API 610", "API 617", "ASME", "ISO 10816", "TEMA"];

const FEATURES = [
  {
    icon: FileSearch,
    title: "Citation-backed Q&A",
    body: "Ask engineering questions and get answers grounded in your documents — every claim traceable to the exact page and passage.",
  },
  {
    icon: Network,
    title: "Industrial Knowledge Graph",
    body: "Explore equipment, incidents, standards and their relationships in a live, interactive graph built from your data.",
  },
  {
    icon: BrainCircuit,
    title: "Predictive Maintenance",
    body: "Surface failure patterns and recommended actions from maintenance and inspection history before things break.",
  },
  {
    icon: ShieldCheck,
    title: "Compliance Intelligence",
    body: "Map operations to Factory Act / OISD / PESO rules and identify compliance gaps automatically.",
  },
];

const PIPELINE = [
  { icon: ScanLine, label: "Ingest & OCR", note: "PDF · DOCX · XLSX · P&ID" },
  { icon: GitBranch, label: "Extract & Graph", note: "entities · relationships" },
  { icon: Boxes, label: "Embed & Index", note: "hybrid vector + keyword" },
  { icon: Sparkles, label: "Agents Answer", note: "cited · confidence-scored" },
];

const METRICS = [
  { value: "6", label: "Specialized AI agents" },
  { value: "5", label: "Data engines unified" },
  { value: "100%", label: "Answers cited" },
  { value: "<1s", label: "To first token" },
];

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-x-clip bg-background">
      {/* ── Ambient background ── */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-grid bg-grid-fade opacity-[0.5]" />
        <div className="absolute -top-40 left-1/2 h-[36rem] w-[60rem] -translate-x-1/2 rounded-full bg-primary/25 blur-[120px] animate-aurora" />
        <div className="absolute top-[28rem] left-[8%] h-72 w-72 rounded-full bg-cyan-500/20 blur-[110px] animate-aurora [animation-delay:3s]" />
        <div className="absolute top-[20rem] right-[6%] h-80 w-80 rounded-full bg-indigo-500/20 blur-[120px] animate-aurora [animation-delay:6s]" />
      </div>

      {/* ── Nav ── */}
      <header className="sticky top-0 z-50">
        <nav className="mx-auto mt-4 flex max-w-6xl items-center justify-between rounded-full border border-border/70 glass px-4 py-2.5 sm:px-6">
          <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
            <span className="grid h-7 w-7 place-items-center rounded-lg bg-primary text-primary-foreground">
              <BrainCircuit className="h-4 w-4" />
            </span>
            KIRA
          </Link>
          <div className="hidden items-center gap-8 text-sm text-muted-foreground md:flex">
            <a href="#features" className="transition hover:text-foreground">Features</a>
            <a href="#pipeline" className="transition hover:text-foreground">How it works</a>
            <a href="#copilot" className="transition hover:text-foreground">Copilot</a>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/login"
              className="hidden rounded-full px-4 py-2 text-sm text-muted-foreground transition hover:text-foreground sm:block"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="group inline-flex items-center gap-1.5 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition hover:opacity-90"
            >
              Get started
              <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-0.5" />
            </Link>
          </div>
        </nav>
      </header>

      {/* ── Hero ── */}
      <section className="mx-auto max-w-6xl px-6 pb-10 pt-20 text-center sm:pt-28">
        <motion.div initial="hidden" animate="show" variants={fadeUp} custom={0}>
          <span className="inline-flex items-center gap-2 rounded-full border border-border/70 glass px-4 py-1.5 text-sm text-muted-foreground">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
            </span>
            Industrial AI Operating System
          </span>
        </motion.div>

        <motion.h1
          initial="hidden"
          animate="show"
          variants={fadeUp}
          custom={1}
          className="mx-auto mt-8 max-w-4xl text-balance text-5xl font-semibold leading-[1.05] tracking-tight sm:text-7xl"
        >
          <span className="text-gradient">Turn plant documents into</span>{" "}
          <span className="text-gradient-brand">decisions you can trust</span>
        </motion.h1>

        <motion.p
          initial="hidden"
          animate="show"
          variants={fadeUp}
          custom={2}
          className="mx-auto mt-6 max-w-2xl text-pretty text-lg text-muted-foreground"
        >
          KIRA unifies fragmented industrial documents into one knowledge intelligence hub —
          citation-backed answers, a live knowledge graph, predictive maintenance, and compliance
          monitoring. Not a chatbot. An operating system for engineering knowledge.
        </motion.p>

        <motion.div
          initial="hidden"
          animate="show"
          variants={fadeUp}
          custom={3}
          className="mt-10 flex flex-wrap items-center justify-center gap-3"
        >
          <Link
            href="/register"
            className="group inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3.5 font-medium text-primary-foreground shadow-lg shadow-primary/25 transition hover:opacity-90"
          >
            Start building <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 rounded-xl border border-border glass px-6 py-3.5 font-medium transition hover:bg-accent"
          >
            View dashboard
          </Link>
        </motion.div>

        <motion.p
          initial="hidden"
          animate="show"
          variants={fadeUp}
          custom={4}
          className="mt-4 text-xs text-muted-foreground"
        >
          No credit card · Self-hostable · Your data never leaves your stack
        </motion.p>

        {/* ── Product preview ── */}
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="relative mx-auto mt-16 max-w-5xl"
        >
          <div className="absolute -inset-x-10 -top-10 bottom-0 -z-10 rounded-[2rem] bg-gradient-to-b from-primary/20 to-transparent blur-2xl" />
          <ProductPreview />
        </motion.div>
      </section>

      {/* ── Logo cloud ── */}
      <section className="mx-auto mt-8 max-w-6xl px-6">
        <p className="text-center text-xs uppercase tracking-[0.2em] text-muted-foreground">
          Understands the standards your plant runs on
        </p>
        <div className="relative mt-6 overflow-hidden [mask-image:linear-gradient(to_right,transparent,#000_12%,#000_88%,transparent)]">
          <div className="flex w-max animate-marquee gap-4">
            {[...STANDARDS, ...STANDARDS].map((s, i) => (
              <span
                key={i}
                className="whitespace-nowrap rounded-lg border border-border/60 glass px-5 py-2 text-sm font-medium text-muted-foreground"
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="mx-auto max-w-6xl px-6 py-24">
        <SectionHeading
          eyebrow="Capabilities"
          title="Everything your engineers ask of their documents"
          subtitle="One platform that reads, structures, connects, and reasons over your industrial knowledge."
        />
        <div className="mt-14 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, body }, i) => (
            <motion.div
              key={title}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true, margin: "-80px" }}
              variants={fadeUp}
              custom={i}
              className="group relative overflow-hidden rounded-2xl border border-border/70 glass p-6 text-left transition hover:border-primary/40"
            >
              <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-primary/10 blur-2xl transition group-hover:bg-primary/20" />
              <div className="grid h-11 w-11 place-items-center rounded-xl border border-border bg-primary/10 text-primary">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="mt-5 font-semibold">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Pipeline ── */}
      <section id="pipeline" className="mx-auto max-w-6xl px-6 py-12">
        <SectionHeading
          eyebrow="The pipeline"
          title="From raw document to cited answer"
          subtitle="Every upload flows through an observable, idempotent pipeline — fully traceable end to end."
        />
        <div className="mt-14 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {PIPELINE.map(({ icon: Icon, label, note }, i) => (
            <motion.div
              key={label}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true, margin: "-60px" }}
              variants={fadeUp}
              custom={i}
              className="relative rounded-2xl border border-border/70 glass p-6"
            >
              <span className="text-xs font-mono text-primary">0{i + 1}</span>
              <Icon className="mt-3 h-6 w-6 text-foreground" />
              <h3 className="mt-3 font-medium">{label}</h3>
              <p className="mt-1 text-xs text-muted-foreground">{note}</p>
              {i < PIPELINE.length - 1 && (
                <ArrowRight className="absolute -right-2.5 top-1/2 hidden h-5 w-5 -translate-y-1/2 text-border lg:block" />
              )}
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Copilot spotlight ── */}
      <section id="copilot" className="mx-auto max-w-6xl px-6 py-24">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <motion.div
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: "-80px" }}
            variants={fadeUp}
          >
            <span className="text-sm font-medium text-primary">AI Copilot</span>
            <h2 className="mt-3 text-balance text-4xl font-semibold tracking-tight">
              Six specialized agents, one grounded answer
            </h2>
            <p className="mt-4 text-pretty text-muted-foreground">
              A planner routes each question to the right expert — Knowledge, Maintenance,
              Compliance, RCA, Document Intelligence, or Lessons Learned. Hybrid retrieval pulls the
              evidence; a cross-encoder reranks it; the answer ships with citations and a confidence
              score. No hallucinated facts. No answer without a source.
            </p>
            <ul className="mt-6 space-y-3 text-sm">
              {[
                ["Hybrid retrieval", "Semantic + keyword fused with Reciprocal Rank Fusion"],
                ["Confidence engine", "Every answer scored on the strength of its evidence"],
                ["Provider-agnostic", "Claude, OpenAI, or on-prem Ollama — swap by config"],
              ].map(([k, v]) => (
                <li key={k} className="flex items-start gap-3">
                  <span className="mt-0.5 grid h-5 w-5 place-items-center rounded-full bg-primary/15 text-primary">
                    <Gauge className="h-3 w-3" />
                  </span>
                  <span>
                    <span className="font-medium text-foreground">{k}</span>{" "}
                    <span className="text-muted-foreground">— {v}</span>
                  </span>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="rounded-2xl border border-border/70 glass p-5 ring-glow"
          >
            <ChatPreview />
          </motion.div>
        </div>
      </section>

      {/* ── Metrics ── */}
      <section className="mx-auto max-w-6xl px-6">
        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-border/70 bg-border/60 lg:grid-cols-4">
          {METRICS.map(({ value, label }) => (
            <div key={label} className="glass px-6 py-8 text-center">
              <div className="text-3xl font-semibold text-gradient-brand sm:text-4xl">{value}</div>
              <div className="mt-1 text-sm text-muted-foreground">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="mx-auto max-w-6xl px-6 py-28">
        <div className="relative overflow-hidden rounded-3xl border border-border/70 px-8 py-16 text-center">
          <div className="absolute inset-0 -z-10 bg-grid opacity-30" />
          <div className="absolute left-1/2 top-0 -z-10 h-64 w-[40rem] -translate-x-1/2 rounded-full bg-primary/25 blur-[100px]" />
          <h2 className="mx-auto max-w-2xl text-balance text-4xl font-semibold tracking-tight sm:text-5xl">
            Put your plant&apos;s knowledge to work
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
            Spin up a workspace, upload your first documents, and ask the Copilot a question in
            minutes.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/register"
              className="group inline-flex items-center gap-2 rounded-xl bg-primary px-7 py-3.5 font-medium text-primary-foreground shadow-lg shadow-primary/25 transition hover:opacity-90"
            >
              Create your workspace
              <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-xl border border-border glass px-7 py-3.5 font-medium transition hover:bg-accent"
            >
              Sign in
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-border/60">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 text-sm text-muted-foreground sm:flex-row">
          <div className="flex items-center gap-2 font-medium text-foreground">
            <span className="grid h-6 w-6 place-items-center rounded-md bg-primary text-primary-foreground">
              <BrainCircuit className="h-3.5 w-3.5" />
            </span>
            KIRA
          </div>
          <p>Knowledge Intelligence for Rapid Analysis</p>
          <p>© 2026 KIRA. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function SectionHeading({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
}) {
  return (
    <motion.div
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: "-80px" }}
      variants={fadeUp}
      className="mx-auto max-w-2xl text-center"
    >
      <span className="text-sm font-medium text-primary">{eyebrow}</span>
      <h2 className="mt-3 text-balance text-4xl font-semibold tracking-tight">{title}</h2>
      <p className="mt-3 text-pretty text-muted-foreground">{subtitle}</p>
    </motion.div>
  );
}

/** Stylized in-browser product window (built with divs, not an image). */
function ProductPreview() {
  return (
    <div className="overflow-hidden rounded-2xl border border-border/80 glass shadow-2xl shadow-primary/10 ring-glow">
      {/* Window chrome */}
      <div className="flex items-center gap-2 border-b border-border/70 px-4 py-3">
        <span className="h-3 w-3 rounded-full bg-red-400/70" />
        <span className="h-3 w-3 rounded-full bg-yellow-400/70" />
        <span className="h-3 w-3 rounded-full bg-green-400/70" />
        <div className="ml-3 flex-1 rounded-md border border-border/60 bg-background/40 px-3 py-1 text-left text-xs text-muted-foreground">
          app.kira.ai / copilot
        </div>
      </div>
      <div className="grid grid-cols-12">
        {/* Sidebar */}
        <div className="col-span-3 hidden border-r border-border/70 p-3 sm:block">
          {["Dashboard", "Copilot", "Documents", "Graph", "Compliance"].map((item, i) => (
            <div
              key={item}
              className={`mb-1 rounded-lg px-3 py-2 text-xs ${
                i === 1 ? "bg-primary/15 text-primary" : "text-muted-foreground"
              }`}
            >
              {item}
            </div>
          ))}
        </div>
        {/* Conversation */}
        <div className="col-span-12 space-y-4 p-5 text-left sm:col-span-9">
          <div className="ml-auto max-w-[80%] rounded-2xl rounded-tr-sm bg-primary px-4 py-2.5 text-sm text-primary-foreground">
            What is the root cause of the P-101 pump seal failure?
          </div>
          <div className="max-w-[92%] rounded-2xl rounded-tl-sm border border-border/70 bg-background/40 p-4 text-sm">
            <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
              <span className="rounded-md bg-primary/15 px-2 py-0.5 font-medium text-primary">
                RCA Agent
              </span>
              <span className="ml-auto inline-flex items-center gap-1 rounded-md border border-green-500/30 bg-green-500/10 px-2 py-0.5 text-green-400">
                <Gauge className="h-3 w-3" /> High confidence
              </span>
            </div>
            <p className="leading-relaxed text-foreground/90">
              Pump <span className="font-medium text-foreground">P-101</span> was started against a
              closed suction valve, causing{" "}
              <span className="font-medium text-foreground">dry running</span> that destroyed the
              mechanical seal faces during startup.
              <sup className="ml-0.5 text-primary">[1]</sup>
            </p>
            <div className="mt-3 flex items-start gap-2 rounded-lg border border-border/60 bg-background/40 p-2.5 text-xs text-muted-foreground">
              <Quote className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
              <span>
                <span className="font-medium text-foreground">[1] incident_reports.csv</span> · INC-2025-041
                · p.1 — &ldquo;started against a closed suction valve causing dry running&rdquo;
              </span>
            </div>
          </div>
          {/* mini graph chips */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            {["P-101", "OISD-STD-105", "API 682", "Mechanical Seal"].map((n) => (
              <span
                key={n}
                className="inline-flex items-center gap-1.5 rounded-full border border-border/60 px-3 py-1 text-xs text-muted-foreground"
              >
                <Workflow className="h-3 w-3 text-primary" /> {n}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/** Compact chat card used in the Copilot spotlight. */
function ChatPreview() {
  return (
    <div className="space-y-3 text-left text-sm">
      {[
        { agent: "Compliance", q: "Are we compliant with OISD and PESO?", a: "1 open gap: PSV-4501 testing overdue by 30 days vs API 526." },
        { agent: "Maintenance", q: "What's next for compressor C-200?", a: "Restore overhaul interval; add continuous thrust monitoring." },
      ].map((t) => (
        <div key={t.agent} className="rounded-xl border border-border/70 bg-background/40 p-4">
          <div className="text-xs text-muted-foreground">{t.q}</div>
          <div className="mt-2 flex items-center gap-2">
            <span className="rounded-md bg-primary/15 px-2 py-0.5 text-xs font-medium text-primary">
              {t.agent}
            </span>
            <span className="h-1 w-1 rounded-full bg-muted-foreground/50" />
            <span className="text-xs text-muted-foreground">cited · scored</span>
          </div>
          <p className="mt-2 text-foreground/90">{t.a}</p>
        </div>
      ))}
    </div>
  );
}
