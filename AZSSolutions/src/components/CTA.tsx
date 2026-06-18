"use client";

import { motion } from "framer-motion";

export default function CTA() {
  const handleScrollToContact = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const contactSection = document.getElementById("contact");
    if (contactSection) {
      const offset = 80;
      const bodyRect = document.body.getBoundingClientRect().top;
      const elementRect = contactSection.getBoundingClientRect().top;
      const elementPosition = elementRect - bodyRect;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  return (
    <section className="py-20 bg-azs-dark relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        
        {/* Banner Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, type: "spring" }}
          className="relative rounded-3xl overflow-hidden p-8 sm:p-12 md:p-16 text-center border border-white/10"
        >
          {/* Brand gradient background */}
          <div className="absolute inset-0 bg-gradient-to-r from-brand-red via-brand-orange to-brand-blue-start opacity-90" />
          {/* Subtle noise/grid pattern overlay */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:30px_30px] pointer-events-none" />
          {/* Ambient lighting blobs */}
          <div className="absolute -top-20 -left-20 w-60 h-60 bg-white/10 rounded-full filter blur-2xl animate-pulse" />
          <div className="absolute -bottom-20 -right-20 w-60 h-60 bg-brand-blue-end/30 rounded-full filter blur-2xl animate-pulse" />

          {/* Content */}
          <div className="relative z-10 max-w-2xl mx-auto flex flex-col items-center">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold text-white mb-6 tracking-tight leading-tight">
              Ready to Automate and Scale Your Business?
            </h2>
            <p className="text-white/80 text-sm sm:text-base font-light mb-10 max-w-lg leading-relaxed">
              Partner with AZS Solutions. Let's build the voice agents, support bots, and software architecture your business needs to grow.
            </p>

            <a
              href="#contact"
              onClick={handleScrollToContact}
              className="px-8 py-4 bg-white text-azs-dark font-semibold text-sm rounded-full hover:bg-azs-white shadow-xl shadow-black/20 hover:shadow-white/10 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-300"
            >
              Contact Us Today
            </a>
          </div>
        </motion.div>

      </div>
    </section>
  );
}
