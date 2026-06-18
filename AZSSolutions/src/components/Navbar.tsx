"use client";

import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const navLinks = [
  { name: "Home", href: "#home" },
  { name: "Services", href: "#services" },
  { name: "Innovation", href: "#innovation" },
  { name: "Why Us", href: "#why-us" },
  { name: "About", href: "#about" },
  { name: "Contact", href: "#contact" },
];

export default function Navbar() {
  const [activeSection, setActiveSection] = useState("home");
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Scroll handler for background change
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Intersection Observer to update active nav link
  useEffect(() => {
    const observerOptions = {
      root: null,
      rootMargin: "-40% 0px -50% 0px", // triggers when section is in middle of viewport
      threshold: 0,
    };

    const observerCallback = (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setActiveSection(entry.target.id);
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);
    
    navLinks.forEach((link) => {
      const el = document.getElementById(link.href.substring(1));
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    const id = href.substring(1);
    const element = document.getElementById(id);
    if (element) {
      setIsMobileMenuOpen(false);
      const offset = 80; // height of navbar
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
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? "py-3 bg-[#0A0A0F]/80 backdrop-blur-md border-b border-white/5 shadow-lg shadow-black/20"
            : "py-6 bg-transparent"
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between">
          {/* Logo */}
          <a
            href="#home"
            onClick={(e) => scrollToSection(e, "#home")}
            className="flex items-center space-x-3 group"
          >
            <div className="relative w-8 h-8 flex items-center justify-center rounded-lg bg-gradient-to-tr from-brand-red to-brand-orange shadow-md shadow-brand-red/10">
              <span className="text-white font-bold text-base select-none">A</span>
              {/* Swoosh dot indicator */}
              <span className="absolute -bottom-1 -right-1 w-2.5 h-2.5 rounded-full bg-brand-blue-end border border-[#0A0A0F] animate-pulse" />
            </div>
            <div className="flex flex-col">
              <span className="text-azs-white font-heading font-semibold text-lg tracking-wide group-hover:text-brand-orange transition-colors">
                AZS Solutions
              </span>
              <span className="text-[9px] uppercase tracking-widest text-azs-gray leading-none">
                (Pvt) Ltd
              </span>
            </div>
          </a>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => scrollToSection(e, link.href)}
                className={`relative py-1.5 text-sm font-medium transition-colors duration-200 ${
                  activeSection === link.href.substring(1)
                    ? "text-azs-white"
                    : "text-azs-gray hover:text-azs-white"
                }`}
              >
                {link.name}
                {activeSection === link.href.substring(1) && (
                  <motion.span
                    layoutId="activeNavIndicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-brand-red to-brand-orange rounded-full"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
              </a>
            ))}
          </nav>

          {/* Desktop CTA Button */}
          <div className="hidden md:block">
            <a
              href="#contact"
              onClick={(e) => scrollToSection(e, "#contact")}
              className="relative inline-flex items-center justify-center px-6 py-2.5 text-xs uppercase tracking-widest font-semibold text-white rounded-full bg-gradient-to-r from-brand-red to-brand-orange hover:shadow-[0_0_20px_rgba(247,148,29,0.3)] transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 overflow-hidden group"
            >
              <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-brand-blue-start to-brand-blue-end opacity-0 group-hover:opacity-100 transition-opacity duration-500 ease-out" />
              <span className="relative z-10">Get in Touch</span>
            </a>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 text-azs-gray hover:text-azs-white transition-colors"
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 md:hidden pt-24 pb-8 px-6 bg-[#0A0A0F]/95 backdrop-blur-xl border-b border-white/5 flex flex-col justify-between"
          >
            <div className="flex flex-col space-y-6">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  onClick={(e) => scrollToSection(e, link.href)}
                  className={`text-lg font-medium py-2 border-b border-white/5 transition-colors ${
                    activeSection === link.href.substring(1)
                      ? "text-brand-orange font-semibold"
                      : "text-azs-gray"
                  }`}
                >
                  {link.name}
                </a>
              ))}
            </div>

            <div className="flex flex-col space-y-4 pt-6">
              <a
                href="#contact"
                onClick={(e) => scrollToSection(e, "#contact")}
                className="w-full py-3 text-center text-sm font-semibold rounded-full bg-gradient-to-r from-brand-red to-brand-orange text-white"
              >
                Get in Touch
              </a>
              <p className="text-[10px] text-center text-azs-gray/50 uppercase tracking-widest">
                AZS Solutions (Pvt) Ltd
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
