"use client";

import { motion, Variants } from "framer-motion";
import { Shield, Target, Lightbulb } from "lucide-react";

export default function About() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, x: -35 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.6, ease: "easeOut" },
    },
  };


  return (
    <section
      id="about"
      className="py-24 md:py-32 bg-azs-dark relative overflow-hidden"
    >
      {/* Decorative gradients */}
      <div className="absolute top-1/4 right-0 w-80 h-80 bg-brand-red/5 rounded-full filter blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-0 w-80 h-80 bg-brand-blue-start/5 rounded-full filter blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
          
          {/* Left Column: Mission text */}
          <div className="lg:col-span-7 flex flex-col justify-center space-y-8">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              className="space-y-6"
            >
              <motion.span
                variants={itemVariants}
                className="text-xs uppercase tracking-widest text-brand-orange font-semibold block"
              >
                Our Purpose
              </motion.span>
              
              <motion.h2
                variants={itemVariants}
                className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold text-azs-white leading-[1.15] tracking-tight"
              >
                Our mission is simple: build smarter solutions that save time, reduce costs, and help businesses scale.
              </motion.h2>
              
              <motion.div
                variants={itemVariants}
                className="h-1 w-20 bg-gradient-to-r from-brand-red to-brand-orange rounded-full"
              />

              <motion.p
                variants={itemVariants}
                className="text-azs-gray text-base sm:text-lg font-light leading-relaxed max-w-2xl"
              >
                AZS Solutions (Pvt) Ltd is an innovation-driven technology partner. We combine deep engineering expertise in AI-first architecture, telephony, and WebRTC integration with custom software development to solve complex operational challenges.
              </motion.p>
            </motion.div>

            {/* Core Values / Sub-sections */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-6 border-t border-white/5"
            >
              {[
                { icon: Target, title: "Result-Driven", desc: "Every project aims for measurable operational metrics." },
                { icon: Lightbulb, title: "Innovation-First", desc: "Leveraging raw research in speech-to-text & NLP." },
                { icon: Shield, title: "Production-Grade", desc: "Rigorous standards for infrastructure safety & uptime." },
              ].map((val, idx) => {
                const Icon = val.icon;
                return (
                  <div key={idx} className="flex flex-col space-y-2">
                    <div className="flex items-center space-x-2 text-azs-white">
                      <Icon size={16} className="text-brand-orange" />
                      <span className="text-sm font-semibold tracking-wide">{val.title}</span>
                    </div>
                    <p className="text-xs text-azs-gray leading-relaxed font-light">{val.desc}</p>
                  </div>
                );
              })}
            </motion.div>
          </div>

          {/* Right Column: Abstract SVG Graphic representing the AZS Swoosh */}
          <div className="lg:col-span-5 flex items-center justify-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8, type: "spring" }}
              className="relative w-full max-w-[400px] aspect-square flex items-center justify-center"
            >
              {/* Spinning background mesh glow */}
              <div className="absolute inset-0 bg-gradient-to-tr from-brand-red/10 via-brand-orange/5 to-brand-blue-end/10 rounded-full filter blur-3xl animate-pulse" />

              {/* Custom SVG Artwork */}
              <svg
                width="100%"
                height="100%"
                viewBox="0 0 400 400"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="relative z-10 w-full h-full drop-shadow-[0_15px_30px_rgba(0,0,0,0.6)]"
              >
                {/* Outer tech circles */}
                <circle cx="200" cy="200" r="170" stroke="rgba(255,255,255,0.03)" strokeWidth="1" strokeDasharray="5 5" />
                <circle cx="200" cy="200" r="140" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
                
                {/* Secondary Blue swoosh */}
                <path
                  d="M110 280C140 310 260 310 290 280C320 250 310 160 270 130C230 100 130 110 110 160C90 210 80 250 110 280Z"
                  stroke="url(#blueGradient)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  className="opacity-70"
                  strokeDasharray="400"
                  strokeDashoffset="100"
                />

                {/* Primary Orange-Red swoosh */}
                <path
                  d="M90 240C120 280 240 290 270 250C300 210 290 130 240 90C190 50 110 90 90 140C70 190 60 200 90 240Z"
                  stroke="url(#orangeGradient)"
                  strokeWidth="4"
                  strokeLinecap="round"
                  className="animate-float"
                />

                {/* Central neural nodes */}
                <g className="nodes">
                  <circle cx="200" cy="200" r="6" fill="#F7941D" className="animate-ping" />
                  <circle cx="200" cy="200" r="4" fill="#F7941D" />
                  
                  <circle cx="140" cy="150" r="3" fill="#2E5BBA" />
                  <circle cx="260" cy="250" r="3" fill="#C1272D" />
                  <circle cx="270" cy="160" r="3" fill="#F7941D" />
                  <circle cx="130" cy="230" r="3" fill="#2E5BBA" />

                  {/* Connecting neural lines */}
                  <line x1="200" y1="200" x2="140" y2="150" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                  <line x1="200" y1="200" x2="260" y2="250" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                  <line x1="200" y1="200" x2="270" y2="160" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                  <line x1="200" y1="200" x2="130" y2="230" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                </g>

                {/* Definitions for gradients */}
                <defs>
                  <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#C1272D" />
                    <stop offset="100%" stopColor="#F7941D" />
                  </linearGradient>
                  <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#1B3F8B" />
                    <stop offset="100%" stopColor="#2E5BBA" />
                  </linearGradient>
                </defs>
              </svg>
            </motion.div>
          </div>

        </div>
      </div>
    </section>
  );
}
