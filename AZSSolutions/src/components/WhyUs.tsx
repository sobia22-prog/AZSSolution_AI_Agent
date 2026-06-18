"use client";

import { motion, Variants } from "framer-motion";
import { Zap, Coins, Layers, HeartHandshake } from "lucide-react";

const differentiators = [
  {
    icon: Zap,
    title: "Faster Time-to-Deploy",
    description: "Our pre-built frameworks and automated pipelines allow us to deploy voice agents and customs software in weeks, not months.",
    color: "text-brand-orange",
    bgGradient: "from-brand-red/10 to-brand-orange/10 border-brand-orange/10",
  },
  {
    icon: Coins,
    title: "Reduced Operational Costs",
    description: "By automating customer contact pipelines and administrative tasks, we slash operations costs by up to 70% from day one.",
    color: "text-brand-orange",
    bgGradient: "from-brand-red/10 to-brand-orange/10 border-brand-orange/10",
  },
  {
    icon: Layers,
    title: "Scalable AI Architecture",
    description: "Built for enterprise capacity, our systems handle thousands of simultaneous active audio streams and webhook requests.",
    color: "text-brand-blue-end",
    bgGradient: "from-brand-blue-start/10 to-brand-blue-end/10 border-brand-blue-end/10",
  },
  {
    icon: HeartHandshake,
    title: "Dedicated Technical Support",
    description: "We work as your long-term innovation partner, offering 24/7 infrastructure monitoring and regular model fine-tuning.",
    color: "text-brand-blue-end",
    bgGradient: "from-brand-blue-start/10 to-brand-blue-end/10 border-brand-blue-end/10",
  },
];

export default function WhyUs() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.12,
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
        stiffness: 80,
        damping: 18,
      },
    },
  };

  return (
    <section
      id="why-us"
      className="py-24 md:py-32 bg-azs-charcoal relative overflow-hidden"
    >
      {/* Decorative gradient accents */}
      <div className="absolute top-0 right-10 w-96 h-96 bg-brand-red/5 rounded-full filter blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 left-10 w-96 h-96 bg-brand-blue-start/5 rounded-full filter blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
          >
            <span className="text-xs uppercase tracking-widest text-brand-orange font-semibold mb-3 block">
              Why Partner With Us
            </span>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold text-azs-white mb-6">
              Engineering Value at Every Layer
            </h2>
            <div className="h-1 w-20 bg-gradient-to-r from-brand-red to-brand-orange mx-auto mb-6 rounded-full" />
            <p className="text-azs-gray text-base sm:text-lg font-light leading-relaxed">
              We design production-grade systems built around concrete business metrics: cost reduction, scale, and deployment velocity.
            </p>
          </motion.div>
        </div>

        {/* Highlight Columns Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8"
        >
          {differentiators.map((diff, index) => {
            const IconComponent = diff.icon;
            return (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                className={`glass-panel p-6 sm:p-8 rounded-2xl border flex flex-col items-start bg-gradient-to-b ${diff.bgGradient} transition-all duration-300 relative group overflow-hidden`}
              >
                {/* Icon wrapper */}
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center bg-white/[0.02] border border-white/10 mb-6 group-hover:scale-110 group-hover:bg-white/[0.04] transition-all duration-300 ${diff.color}`}
                >
                  <IconComponent size={22} className="transition-transform duration-500 group-hover:rotate-[360deg]" />
                </div>

                {/* Content */}
                <h3 className="text-lg font-heading font-semibold text-azs-white mb-3 group-hover:text-azs-white transition-colors">
                  {diff.title}
                </h3>
                
                <p className="text-sm text-azs-gray leading-relaxed font-light">
                  {diff.description}
                </p>

                {/* Subtle border bottom hover glow */}
                <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-white/10 to-transparent group-hover:via-white/30 transition-all duration-500" />
              </motion.div>
            );
          })}
        </motion.div>

      </div>
    </section>
  );
}
