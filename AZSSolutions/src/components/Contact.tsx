"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Globe, Send, CheckCircle2 } from "lucide-react";

function Linkedin({ size = 20 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
      <rect width="4" height="12" x="2" y="9" />
      <circle cx="4" cy="4" r="2" />
    </svg>
  );
}



export default function Contact() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.message) return;

    setIsSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitSuccess(true);
      setFormData({ name: "", email: "", message: "" });
      
      // Reset success status after a delay
      setTimeout(() => setSubmitSuccess(false), 5000);
    }, 1500);
  };

  return (
    <section
      id="contact"
      className="py-24 md:py-32 bg-azs-charcoal relative overflow-hidden"
    >
      {/* Decorative gradient elements */}
      <div className="absolute top-1/4 right-0 w-80 h-80 bg-brand-orange/5 rounded-full filter blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-0 w-80 h-80 bg-brand-blue-start/5 rounded-full filter blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
          
          {/* Left Column: Direct Info & Socials */}
          <div className="lg:col-span-5 flex flex-col justify-between">
            <div className="space-y-6">
              <span className="text-xs uppercase tracking-widest text-brand-orange font-semibold block">
                Connect With Us
              </span>
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold text-azs-white tracking-tight leading-none">
                Let's Build Together
              </h2>
              <div className="h-1 w-20 bg-gradient-to-r from-brand-red to-brand-orange rounded-full mb-8" />
              <p className="text-azs-gray text-base font-light leading-relaxed max-w-sm">
                Have a question or looking to scope a project? Contact our engineering team directly or send us a message through the form.
              </p>

              {/* Contact list details */}
              <div className="space-y-4 pt-6">
                
                {/* Email link */}
                <a
                  href="mailto:azssolution01@gmail.com"
                  className="flex items-center space-x-4 p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-brand-orange/20 transition-all duration-300 group"
                >
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-brand-orange/10 border border-brand-orange/20 group-hover:scale-105 transition-transform text-brand-orange">
                    <Mail size={18} />
                  </div>
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-azs-gray/50">Direct Email</p>
                    <p className="text-sm font-medium text-azs-white group-hover:text-brand-orange transition-colors">
                      azssolution01@gmail.com
                    </p>
                  </div>
                </a>

                {/* Website link */}
                <a
                  href="https://azssolutions.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-4 p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-brand-blue-end/20 transition-all duration-300 group"
                >
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-brand-blue-start/10 border border-brand-blue-end/20 group-hover:scale-105 transition-transform text-brand-blue-end">
                    <Globe size={18} />
                  </div>
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-azs-gray/50">Corporate Site</p>
                    <p className="text-sm font-medium text-azs-white group-hover:text-brand-blue-end transition-colors">
                      azssolutions.com
                    </p>
                  </div>
                </a>

              </div>
            </div>

            {/* Socials & Legal details */}
            <div className="pt-12 lg:pt-0 space-y-6">
              <div>
                <p className="text-xs uppercase tracking-widest text-azs-gray/50 mb-3 font-semibold">Socials</p>
                <div className="flex space-x-4">
                  <a
                    href="https://www.linkedin.com/company/azs-solutions"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 rounded-lg bg-white/[0.02] border border-white/5 hover:border-brand-blue-end/30 flex items-center justify-center text-azs-gray hover:text-brand-blue-end hover:bg-brand-blue-start/5 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-300"
                    aria-label="LinkedIn Profile"
                  >
                    <Linkedin size={20} />
                  </a>
                </div>
              </div>
              <p className="text-xs font-mono text-azs-gray/35">
                AZS Solutions (Pvt) Ltd<br />
                Registered Corporate Entity.
              </p>
            </div>

          </div>

          {/* Right Column: Form */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, y: 35 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6 }}
              className="glass-panel p-8 sm:p-10 rounded-2xl border border-white/5 shadow-xl shadow-black/30 relative"
            >
              <AnimatePresence mode="wait">
                {!submitSuccess ? (
                  <motion.form
                    key="contact-form"
                    onSubmit={handleSubmit}
                    className="space-y-6"
                    initial={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                      {/* Name input */}
                      <div className="space-y-2 text-left">
                        <label htmlFor="name" className="text-xs font-semibold uppercase tracking-wider text-azs-white">
                          Full Name
                        </label>
                        <input
                          type="text"
                          id="name"
                          name="name"
                          required
                          value={formData.name}
                          onChange={handleChange}
                          className="w-full bg-[#0A0A0F]/70 border border-white/10 rounded-xl px-4 py-3 text-sm text-azs-white placeholder-azs-gray/30 focus:outline-none focus:border-brand-orange focus:ring-1 focus:ring-brand-orange transition-all duration-200"
                          placeholder="Jane Doe"
                        />
                      </div>

                      {/* Email input */}
                      <div className="space-y-2 text-left">
                        <label htmlFor="email" className="text-xs font-semibold uppercase tracking-wider text-azs-white">
                          Email Address
                        </label>
                        <input
                          type="email"
                          id="email"
                          name="email"
                          required
                          value={formData.email}
                          onChange={handleChange}
                          className="w-full bg-[#0A0A0F]/70 border border-white/10 rounded-xl px-4 py-3 text-sm text-azs-white placeholder-azs-gray/30 focus:outline-none focus:border-brand-orange focus:ring-1 focus:ring-brand-orange transition-all duration-200"
                          placeholder="jane@company.com"
                        />
                      </div>
                    </div>

                    {/* Message input */}
                    <div className="space-y-2 text-left">
                      <label htmlFor="message" className="text-xs font-semibold uppercase tracking-wider text-azs-white">
                        Your Message
                      </label>
                      <textarea
                        id="message"
                        name="message"
                        required
                        rows={5}
                        value={formData.message}
                        onChange={handleChange}
                        className="w-full bg-[#0A0A0F]/70 border border-white/10 rounded-xl px-4 py-3 text-sm text-azs-white placeholder-azs-gray/30 focus:outline-none focus:border-brand-orange focus:ring-1 focus:ring-brand-orange transition-all duration-200 resize-none"
                        placeholder="Tell us about your project or automated agent requirements..."
                      />
                    </div>

                    {/* Submit Button */}
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full py-4 rounded-xl bg-gradient-to-r from-brand-red to-brand-orange text-white font-semibold text-sm flex items-center justify-center space-x-2 hover:shadow-[0_0_20px_rgba(247,148,29,0.3)] disabled:opacity-50 transition-all duration-300 group"
                    >
                      {isSubmitting ? (
                        <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <>
                          <span>Send Message</span>
                          <Send size={16} className="transform group-hover:translate-x-1 group-hover:-translate-y-0.5 transition-transform" />
                        </>
                      )}
                    </button>
                  </motion.form>
                ) : (
                  <motion.div
                    key="success-message"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="py-12 flex flex-col items-center justify-center text-center space-y-4"
                  >
                    <CheckCircle2 size={56} className="text-brand-orange animate-bounce" />
                    <h3 className="text-xl font-heading font-semibold text-azs-white">
                      Message Sent Successfully!
                    </h3>
                    <p className="text-sm text-azs-gray max-w-sm">
                      Thank you for contacting AZS Solutions. Our engineering team will review your message and get back to you shortly.
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>

        </div>
      </div>
    </section>
  );
}
