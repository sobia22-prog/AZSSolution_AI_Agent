"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { Terminal, Cpu, Radio, Sparkles } from "lucide-react";

const mockLogs = [
  { time: "10:14:02.12", msg: "SYS: Initializing Voice-Agent pipeline..." },
  { time: "10:14:02.50", msg: "SYS: Telephony WebRTC session bound." },
  { time: "10:14:03.01", msg: "AI: 'Hello! Thanks for calling AZS Solutions. How can I help you today?'" },
  { time: "10:14:05.42", msg: "USER: 'Hi, I'm looking to automate our lead follow-up. Can your AI do that?'" },
  { time: "10:14:06.10", msg: "SYS: Processing speech-to-text (STT)..." },
  { time: "10:14:06.35", msg: "SYS: NLP Confidence Score: 98.7% - Intent: Lead_Automation" },
  { time: "10:14:06.85", msg: "AI: 'Absolutely. We design voice agents that connect to your CRM, qualify leads, and schedule calls automatically.'" },
  { time: "10:14:10.22", msg: "USER: 'That sounds perfect. How fast can we deploy?'" },
  { time: "10:14:10.90", msg: "SYS: Generating agent response..." },
  { time: "10:14:11.45", msg: "AI: 'Typically, we can configure, train, and deploy a custom agent within 7 business days.'" },
];

export default function Innovation() {
  const [visibleLogs, setVisibleLogs] = useState<typeof mockLogs>([]);
  const [logIndex, setLogIndex] = useState(0);

  // Feed logs line by line
  useEffect(() => {
    if (logIndex < mockLogs.length) {
      const timer = setTimeout(() => {
        setVisibleLogs((prev) => [...prev, mockLogs[logIndex]]);
        setLogIndex((prev) => prev + 1);
      }, logIndex === 0 ? 500 : 1500); // initial delay, then interval
      return () => clearTimeout(timer);
    } else {
      // Loop logs after completion
      const resetTimer = setTimeout(() => {
        setVisibleLogs([]);
        setLogIndex(0);
      }, 5000);
      return () => clearTimeout(resetTimer);
    }
  }, [logIndex]);

  return (
    <section
      id="innovation"
      className="py-24 md:py-32 bg-azs-dark relative overflow-hidden border-t border-b border-white/5"
    >
      {/* Background radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand-blue-start/5 rounded-full filter blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-blue-start/10 border border-brand-blue-end/20 mb-4">
              <Sparkles size={12} className="text-brand-blue-end animate-pulse" />
              <span className="text-[10px] uppercase tracking-wider font-semibold text-brand-blue-end">
                Innovation Lab
              </span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold text-azs-white mb-6">
              What We're Building
            </h2>
            <div className="h-1 w-20 bg-gradient-to-r from-brand-blue-start to-brand-blue-end mx-auto mb-6 rounded-full" />
            <p className="text-azs-gray text-base sm:text-lg font-light leading-relaxed">
              AZS Solutions is pushing boundaries in Voice AI. We are training custom LLMs and optimizing RTC protocols to build next-generation voice agents that feel entirely natural.
            </p>
          </motion.div>
        </div>

        {/* Core Layout: Description + Interactive Visual */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Column: Details */}
          <div className="lg:col-span-5 flex flex-col justify-center space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6 }}
              className="space-y-6"
            >
              <h3 className="text-2xl sm:text-3xl font-heading font-semibold text-azs-white tracking-tight">
                Conversational AI with Zero Latency
              </h3>
              <p className="text-azs-gray text-sm sm:text-base font-light leading-relaxed">
                Traditional support channels are slow and expensive. Our research centers on ultra-low-latency voice interfaces capable of carrying on nuanced business conversations.
              </p>
              
              <ul className="space-y-4 pt-2">
                {[
                  "Natural tone of voice and adaptive cadence matching",
                  "Sub-500ms response latency for realistic conversation flow",
                  "Direct CRM integration for instant appointment scheduling",
                  "High-capacity pipelines handling 10,000+ simultaneous calls",
                ].map((item, i) => (
                  <li key={i} className="flex items-start space-x-3">
                    <span className="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-brand-orange" />
                    <span className="text-sm text-azs-gray font-light">{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>

          {/* Right Column: Interactive Waveform & Console */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6 }}
              className="glass-panel rounded-2xl border border-white/5 overflow-hidden shadow-2xl shadow-black/40"
            >
              {/* Terminal header */}
              <div className="bg-[#0e0e14] px-4 py-3 flex items-center justify-between border-b border-white/5">
                <div className="flex items-center space-x-2">
                  <Terminal size={14} className="text-brand-blue-end" />
                  <span className="text-xs font-mono tracking-wider text-azs-white">azs-voice-terminal_v2.0.sh</span>
                </div>
                <div className="flex space-x-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                  <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                  <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                </div>
              </div>

              {/* Terminal Logs Area */}
              <div className="p-5 bg-[#0A0A0F]/90 h-[220px] overflow-y-auto font-mono text-[11px] leading-relaxed text-left flex flex-col space-y-2">
                {visibleLogs.map((log, i) => {
                  let colorClass = "text-azs-gray";
                  if (log.msg.startsWith("SYS:")) colorClass = "text-brand-blue-end";
                  if (log.msg.startsWith("AI:")) colorClass = "text-brand-orange font-semibold";
                  if (log.msg.startsWith("USER:")) colorClass = "text-azs-white font-medium";

                  return (
                    <div key={i} className={`flex items-start ${colorClass}`}>
                      <span className="opacity-40 mr-3 flex-shrink-0 select-none">[{log.time}]</span>
                      <span>{log.msg}</span>
                    </div>
                  );
                })}
                {visibleLogs.length < mockLogs.length && (
                  <div className="flex items-center text-brand-orange animate-pulse">
                    <span className="w-1.5 h-3 bg-brand-orange mr-1" />
                    <span className="text-[10px] tracking-widest uppercase font-semibold">LISTENING...</span>
                  </div>
                )}
              </div>

              {/* Glowing Waveform panel */}
              <div className="bg-[#0e0e14] p-6 flex flex-col items-center justify-center border-t border-white/5 relative">
                {/* Status elements */}
                <div className="absolute top-3 left-4 flex items-center space-x-2 text-[10px] uppercase font-mono tracking-widest text-azs-gray/50">
                  <Radio size={10} className="text-brand-red animate-pulse" />
                  <span>Live Stream</span>
                </div>

                {/* Animated Waveform Bars */}
                <div className="flex items-end justify-center h-20 space-x-1 w-full max-w-md mt-4">
                  {Array.from({ length: 42 }).map((_, i) => {
                    // Generate pseudo-random delay and duration
                    const duration = 0.5 + Math.random() * 0.8;
                    const delay = Math.random() * 0.5;
                    
                    // Render styling (gradient from blue to orange/red)
                    let bg = "bg-brand-blue-end";
                    if (i > 14 && i < 28) bg = "bg-gradient-to-t from-brand-blue-end to-brand-orange";
                    if (i >= 28) bg = "bg-brand-orange";

                    return (
                      <motion.div
                        key={i}
                        animate={{
                          height: ["10%", "90%", "20%", "70%", "10%"],
                        }}
                        transition={{
                          duration,
                          repeat: Infinity,
                          repeatType: "reverse",
                          ease: "easeInOut",
                          delay,
                        }}
                        className={`w-[4px] rounded-full opacity-80 ${bg}`}
                        style={{ height: "10%" }}
                      />
                    );
                  })}
                </div>

                {/* Performance stats banner */}
                <div className="mt-5 flex items-center justify-between w-full max-w-md border-t border-white/5 pt-4 text-[10px] font-mono text-azs-gray/40">
                  <div className="flex items-center space-x-1">
                    <Cpu size={10} />
                    <span>AUDIO_ENGINE: WebRTC/OPUS</span>
                  </div>
                  <span>LATENCY: 412ms</span>
                  <span>SAMPLING: 48kHz</span>
                </div>
              </div>
            </motion.div>
          </div>

        </div>

      </div>
    </section>
  );
}
