import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Services from "@/components/Services";
import Innovation from "@/components/Innovation";
import WhyUs from "@/components/WhyUs";
import Stats from "@/components/Stats";
import About from "@/components/About";
import CTA from "@/components/CTA";
import Contact from "@/components/Contact";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen w-full overflow-x-hidden">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <Services />
        <Innovation />
        <WhyUs />
        <Stats />
        <About />
        <CTA />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}

