"use client";

import { motion, Variants } from "framer-motion";
import { PhoneCall, Bot, Target, Code2, Server, Truck } from "lucide-react";

const services = [
  {
    icon: PhoneCall,
    title: "AI Calling Agents",
    description: "Automate customer support, lead qualification, and appointment scheduling with natural-sounding voice AI.",
    gradient: "from-brand-red to-brand-orange",
    isPrimary: true,
  },
  {
    icon: Bot,
    title: "AI Customer Support",
    description: "24/7 intelligent support solutions that resolve customer inquiries faster and drastically reduce operational costs.",
    gradient: "from-brand-blue-start to-brand-blue-end",
    isPrimary: false,
  },
  {
    icon: Target,
    title: "Automated Lead Generation",
    description: "Deploy smart, data-driven systems that search out, qualify, and nurture high-intent leads automatically.",
    gradient: "from-brand-red to-brand-orange",
    isPrimary: true,
  },
  {
    icon: Code2,
    title: "Custom Software Dev",
    description: "Tailored software applications and APIs engineered around your business's precise operational workflows.",
    gradient: "from-brand-blue-start to-brand-blue-end",
    isPrimary: false,
  },
  {
    icon: Server,
    title: "IT Infrastructure Management",
    description: "Reliable, secure, and scalable cloud-first infrastructure so you can focus entirely on scaling your product.",
    gradient: "from-brand-red to-brand-orange",
    isPrimary: true,
  },
  {
    icon: Truck,
    title: "Dispatch & Logistics",
    description: "Smarter routing, dispatching, and logistics automation systems built to cut down transit delays and shipping costs.",
    gradient: "from-brand-blue-start to-brand-blue-end",
    isPrimary: false,
  },
];

export default function Services() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const cardVariants: Variants = {
    hidden: { opacity: 0, y: 40 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 70,
        damping: 15,
      },
    },
  };

  return (
    <section
      id="services"
      className="py-24 md:py-32 bg-azs-charcoal relative overflow-hidden"
    >
      {/* Decorative gradient elements */}
      <div className="absolute top-1/2 left-0 w-80 h-80 bg-brand-orange/5 rounded-full filter blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-80 h-80 bg-brand-blue-start/5 rounded-full filter blur-[100px] pointer-events-none" />

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
              Core Capabilities
            </span>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold text-azs-white mb-6">
              Empowering Businesses with Next-Gen Infrastructure
            </h2>
            <div className="h-1 w-20 bg-gradient-to-r from-brand-red to-brand-orange mx-auto mb-6 rounded-full" />
            <p className="text-azs-gray text-base sm:text-lg font-light leading-relaxed">
              We design, build, and deploy intelligent automation systems and software architectures tailored to drive operational efficiency.
            </p>
          </motion.div>
        </div>

        {/* Services Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8"
        >
          {services.map((service, index) => {
            const IconComponent = service.icon;
            return (
              <motion.div
                key={index}
                variants={cardVariants}
                whileHover={{ y: -8, transition: { duration: 0.2 } }}
                className={`glass-panel p-8 rounded-2xl flex flex-col justify-between transition-all duration-300 relative group overflow-hidden ${
                  service.isPrimary ? "glass-panel-hover" : "glass-panel-hover-blue"
                }`}
              >
                {/* Accent lines at the top of cards */}
                <div
                  className={`absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r ${service.gradient} opacity-50 group-hover:opacity-100 transition-opacity`}
                />

                {/* Corner light blob on hover */}
                <div
                  className={`absolute -top-12 -right-12 w-24 h-24 rounded-full bg-gradient-to-br ${
                    service.isPrimary ? "from-brand-orange/10" : "from-brand-blue-end/20"
                  } to-transparent blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
                />

                <div>
                  {/* Icon Container */}
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-tr ${service.gradient} p-[1px] mb-8 shadow-lg shadow-black/30 group-hover:scale-110 transition-transform duration-300`}
                  >
                    <div className="w-full h-full bg-[#13131A] rounded-xl flex items-center justify-center">
                      <IconComponent
                        size={20}
                        className={`text-white transition-colors duration-300 ${
                          service.isPrimary ? "group-hover:text-brand-orange" : "group-hover:text-brand-blue-end"
                        }`}
                      />
                    </div>
                  </div>

                  {/* Title */}
                  <h3 className="text-xl font-heading font-semibold text-azs-white mb-4 group-hover:text-azs-white transition-colors">
                    {service.title}
                  </h3>

                  {/* Description */}
                  <p className="text-sm text-azs-gray leading-relaxed font-light mb-6">
                    {service.description}
                  </p>
                </div>

                {/* Interactive learn more indicator link */}
                <div className="flex items-center text-xs font-semibold tracking-wider uppercase mt-4">
                  <span
                    className={`transition-colors duration-300 ${
                      service.isPrimary
                        ? "text-brand-orange group-hover:text-white"
                        : "text-brand-blue-end group-hover:text-white"
                    }`}
                  >
                    Deploy Solution
                  </span>
                  <svg
                    className={`w-4 h-4 ml-1.5 transform group-hover:translate-x-1 transition-transform duration-300 ${
                      service.isPrimary ? "text-brand-orange" : "text-brand-blue-end"
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2.5}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </motion.div>
            );
          })}
        </motion.div>

      </div>
    </section>
  );
}
