"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";

interface StatItemProps {
  value: number;
  suffix?: string;
  decimals?: number;
  label: string;
  gradient: string;
}

function StatItem({ value, suffix = "", decimals = 0, label, gradient }: StatItemProps) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (!isInView) return;

    let startTime: number | null = null;
    const duration = 2000; // 2 seconds animation

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      // Easing function (easeOutQuad)
      const easeProgress = progress * (2 - progress);
      const currentVal = easeProgress * value;

      setCount(currentVal);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [isInView, value]);

  const formattedCount = count.toFixed(decimals);

  return (
    <div ref={ref} className="text-center p-6 flex flex-col items-center">
      <div className={`text-4xl sm:text-5xl md:text-6xl font-heading font-bold bg-gradient-to-r ${gradient} bg-clip-text text-transparent mb-2 tracking-tight`}>
        {formattedCount}
        {suffix}
      </div>
      <div className="text-xs sm:text-sm uppercase tracking-widest text-azs-gray/80 font-medium">
        {label}
      </div>
    </div>
  );
}

export default function Stats() {
  const stats = [
    {
      value: 250,
      suffix: "K+",
      decimals: 0,
      label: "Hours Automated",
      gradient: "from-brand-red to-brand-orange",
    },
    {
      value: 150,
      suffix: "+",
      decimals: 0,
      label: "Businesses Scaled",
      gradient: "from-brand-blue-start to-brand-blue-end",
    },
    {
      value: 94.2,
      suffix: "%",
      decimals: 1,
      label: "Resolution Rate",
      gradient: "from-brand-red to-brand-orange",
    },
    {
      value: 1.2,
      suffix: "M+",
      decimals: 1,
      label: "Calls Handled",
      gradient: "from-brand-blue-start to-brand-blue-end",
    },
  ];

  return (
    <section className="bg-azs-dark py-16 border-t border-b border-white/5 relative overflow-hidden">
      {/* Mesh lines */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.002)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none opacity-40" />

      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 md:gap-12">
          {stats.map((stat, index) => (
            <StatItem
              key={index}
              value={stat.value}
              suffix={stat.suffix}
              decimals={stat.decimals}
              label={stat.label}
              gradient={stat.gradient}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
