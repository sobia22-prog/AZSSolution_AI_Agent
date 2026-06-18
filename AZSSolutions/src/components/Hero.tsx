"use client";

import { motion, Variants } from "framer-motion";
import GradientMeshCanvas from "./GradientMeshCanvas";

export default function Hero() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 20,
      },
    },
  };


  const handleScrollTo = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const element = document.getElementById(id);
    if (element) {
      const offset = 80;
      const bodyRect = document.body.getBoundingClientRect().top;
      const elementRect = element.getBoundingClientRect().top;
      const elementPosition = elementRect - bodyRect;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center pt-24 overflow-hidden bg-azs-dark"
    >
      {/* Dynamic Animated Particle/Mesh Background */}
      <GradientMeshCanvas />

      {/* Decorative Blur Spheres */}
      <div className="absolute top-1/4 left-10 w-96 h-96 bg-brand-red/5 rounded-full filter blur-[100px] pointer-events-none animate-pulse duration-[10000ms]" />
      <div className="absolute bottom-1/4 right-10 w-96 h-96 bg-brand-blue-start/5 rounded-full filter blur-[100px] pointer-events-none animate-pulse duration-[8000ms]" />

      <div className="relative z-10 max-w-5xl mx-auto px-6 md:px-12 text-center">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center"
        >
          {/* Animated Tech Badge */}
          <motion.div
            variants={itemVariants}
            className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-white/[0.03] border border-white/5 backdrop-blur-md mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-brand-orange animate-ping" />
            <span className="text-[11px] font-semibold text-azs-white uppercase tracking-widest">
              Next-Gen AI & Tech Infrastructure
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            variants={itemVariants}
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-heading font-bold text-azs-white tracking-tight leading-[1.1] mb-6 max-w-4xl"
          >
            Smarter Solutions for a{" "}
            <span className="relative inline-block text-gradient-primary">
              Faster-Moving
            </span>{" "}
            World
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            variants={itemVariants}
            className="text-base sm:text-lg md:text-xl text-azs-gray max-w-2xl mb-10 leading-relaxed font-light"
          >
            AZS Solutions helps businesses streamline operations, improve
            customer experiences, and accelerate growth through innovative
            technology.
          </motion.p>

          {/* CTAs */}
          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 w-full sm:w-auto"
          >
            {/* Primary CTA */}
            <a
              href="#services"
              onClick={(e) => handleScrollTo(e, "services")}
              className="w-full sm:w-auto px-8 py-4 text-sm font-semibold rounded-full bg-gradient-to-r from-brand-red to-brand-orange text-white hover:shadow-[0_0_25px_rgba(247,148,29,0.35)] transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 text-center relative overflow-hidden group"
            >
              <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-brand-blue-start to-brand-blue-end opacity-0 group-hover:opacity-100 transition-opacity duration-500 ease-out" />
              <span className="relative z-10">Explore Our Services</span>
            </a>

            {/* Secondary CTA */}
            <a
              href="#contact"
              onClick={(e) => handleScrollTo(e, "contact")}
              className="w-full sm:w-auto px-8 py-4 text-sm font-semibold rounded-full bg-[#0A0A0F]/60 text-azs-white border border-white/10 hover:border-brand-blue-end hover:bg-white/[0.02] transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 text-center backdrop-blur-sm shadow-inner shadow-white/5"
            >
              Book a Consultation
            </a>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            variants={itemVariants}
            className="mt-20 flex flex-col items-center space-y-2 text-azs-gray/40 text-xs tracking-widest uppercase"
          >
            <span className="animate-bounce">Scroll Down</span>
            <div className="w-5 h-8 rounded-full border-2 border-white/10 flex justify-center p-1">
              <motion.div
                animate={{
                  y: [0, 10, 0],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                className="w-1.5 h-1.5 rounded-full bg-brand-orange"
              />
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Grid Overlay for structure */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.005)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.005)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none opacity-40" />
    </section>
  );
}
