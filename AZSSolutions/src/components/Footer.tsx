"use client";

function Linkedin({ size = 16 }: { size?: number }) {
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



export default function Footer() {
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
    <footer className="bg-azs-dark border-t border-white/5 py-12 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
        
        {/* Left Side: Brand Logo & Legal */}
        <div className="flex flex-col items-center md:items-start text-center md:text-left space-y-3">
          <a
            href="#home"
            onClick={(e) => handleScrollTo(e, "home")}
            className="flex items-center space-x-3 group"
          >
            <div className="relative w-8 h-8 flex items-center justify-center rounded-lg bg-gradient-to-tr from-brand-red to-brand-orange shadow-md shadow-brand-red/10">
              <span className="text-white font-bold text-base select-none">A</span>
              <span className="absolute -bottom-1 -right-1 w-2.5 h-2.5 rounded-full bg-brand-blue-end border border-[#0A0A0F]" />
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
          <p className="text-xs text-azs-gray/50 max-w-xs leading-relaxed font-light">
            Smarter Solutions for a Faster-Moving World. Building production-grade AI & software infrastructure.
          </p>
        </div>

        {/* Center: Navigation Links */}
        <div className="flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs font-medium tracking-wide uppercase text-azs-gray">
          {[
            { name: "Home", id: "home" },
            { name: "Services", id: "services" },
            { name: "Innovation", id: "innovation" },
            { name: "Why Us", id: "why-us" },
            { name: "About", id: "about" },
            { name: "Contact", id: "contact" },
          ].map((link, idx) => (
            <a
              key={idx}
              href={`#${link.id}`}
              onClick={(e) => handleScrollTo(e, link.id)}
              className="hover:text-brand-orange transition-colors duration-200"
            >
              {link.name}
            </a>
          ))}
        </div>

        {/* Right Side: Social & Copyright */}
        <div className="flex flex-col items-center md:items-end space-y-3">
          <div className="flex space-x-3">
            <a
              href="https://www.linkedin.com/company/azs-solutions"
              target="_blank"
              rel="noopener noreferrer"
              className="w-8 h-8 rounded-lg bg-white/[0.02] border border-white/5 hover:border-brand-blue-end/30 flex items-center justify-center text-azs-gray hover:text-brand-blue-end hover:bg-brand-blue-start/5 transition-all duration-300"
              aria-label="LinkedIn"
            >
              <Linkedin size={16} />
            </a>
          </div>
          <p className="text-[10px] text-azs-gray/40 font-mono">
            © 2026 AZS Solutions (Pvt) Ltd. All rights reserved.
          </p>
        </div>

      </div>
    </footer>
  );
}
