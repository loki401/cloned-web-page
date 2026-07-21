import { createFileRoute } from "@tanstack/react-router";
import { ArrowUpRight, Mail, Github, Linkedin, Cpu, Cloud, Code2, GraduationCap, Briefcase } from "lucide-react";
const portrait = "/portrait.png";
export const Route = createFileRoute("/")({
  component: Index,
});

const projects = [
  {
    n: "01",
    title: "Mini ChatGPT Chatbot",
    tag: "NLP · Transformers",
    body: "Fine-tuned a pre-trained GPT-2 with Hugging Face Transformers and shipped it behind a Flask API for real-time conversational responses.",
    stack: ["GPT-2", "Hugging Face", "Flask", "Python"],
  },
  {
    n: "02",
    title: "AI-Based Automatic Car Parking",
    tag: "Computer Vision",
    body: "Real-time slot detection and path planning using OpenCV for image processing, with a BERT layer driving the decision logic.",
    stack: ["OpenCV", "BERT", "Python", "Path Planning"],
  },
  {
    n: "03",
    title: "Containerized Flipkart Clone",
    tag: "DevOps · AWS",
    body: "Production-style DevOps pipeline: Dockerized services, custom VPC on AWS, S3-backed assets, Docker Hub automation, and monitoring.",
    stack: ["Docker", "AWS EC2", "VPC", "S3", "IAM"],
  },
];

const skills = [
  {
    group: "AI & Machine Learning",
    icon: Cpu,
    items: ["GPT-2 Fine-Tuning", "Hugging Face Transformers", "BERT", "OpenCV", "NLP Pipelines"],
  },
  {
    group: "Cloud & DevOps",
    icon: Cloud,
    items: ["AWS EC2", "Amazon S3", "VPC & IAM", "Docker", "Docker Hub Automation"],
  },
  {
    group: "Software Engineering",
    icon: Code2,
    items: ["Java (OOP)", "SQL & Databases", "Data Structures & Algorithms", "React.js", "Flask"],
  },
];

const timeline = [
  {
    when: "2024",
    role: "AI Research Intern",
    org: "Evolve Robot Lab",
    body: "Built data preprocessing pipelines and applied NLP techniques to prototype intelligent systems for research.",
    icon: Briefcase,
  },
  {
    when: "2022 — 2026",
    role: "B.Tech, Artificial Intelligence & Data Science",
    org: "Panimalar Engineering College",
    body: "Coursework in DSA, OOP with Java, SQL, and applied ML — complemented by hands-on DevOps and cloud infrastructure.",
    icon: GraduationCap,
  },
];

function Index() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Nav />
      <main>
        <Hero />
        <Projects />
        <Skills />
        <Experience />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}

function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <a href="#top" className="flex items-center gap-2 text-sm font-semibold tracking-tight">
          <span className="grid h-8 w-8 place-items-center rounded-md bg-primary text-primary-foreground">LM</span>
          <span>Logesh M</span>
        </a>
        <nav className="hidden gap-8 text-sm text-muted-foreground md:flex">
          <a href="#work" className="transition hover:text-foreground">Work</a>
          <a href="#skills" className="transition hover:text-foreground">Skills</a>
          <a href="#experience" className="transition hover:text-foreground">Experience</a>
          <a href="#contact" className="transition hover:text-foreground">Contact</a>
        </nav>
        <a
          href="#contact"
          className="inline-flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm transition hover:opacity-90"
        >
          Get in touch
          <ArrowUpRight className="h-4 w-4" />
        </a>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section id="top" className="relative overflow-hidden border-b border-border/60">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_50%_at_50%_0%,color-mix(in_oklab,var(--accent)_14%,transparent),transparent_70%)]" />
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
        <div className="flex flex-col items-center text-center">
          <div className="relative mb-10">
            <div className="absolute -inset-3 -z-10 rounded-full bg-gradient-to-br from-accent/30 via-accent/10 to-transparent blur-2xl" />
            <div className="relative h-48 w-48 overflow-hidden rounded-full border border-border bg-card shadow-lg md:h-64 md:w-64">
              <img
                src={portrait.url}
                alt="Portrait of Logesh M"
                className="h-full w-full object-cover"
                loading="eager"
              />
            </div>
          </div>
          <div className="mx-auto max-w-3xl">
            <div className="flex items-center justify-center gap-2 text-xs font-medium text-muted-foreground">
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
              Open to Software Engineering, DevOps & Cloud Support roles · Batch of 2026
            </div>
            <h1 className="mt-6 text-4xl leading-[1.05] tracking-tight md:text-6xl">
              <span className="font-serif italic text-accent">Engineering</span> intelligent systems —
              <br className="hidden md:block" /> from model to <span className="font-serif italic">production cloud</span>.
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted-foreground md:text-lg">
              I'm Logesh M, a final-year B.Tech student in Artificial Intelligence & Data Science at Panimalar
              Engineering College. I build AI/ML systems, containerize them, deploy to AWS, and wire the full
              stack around them.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <a
                href="#work"
                className="inline-flex items-center gap-1.5 rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition hover:opacity-90"
              >
                View selected work
                <ArrowUpRight className="h-4 w-4" />
              </a>
              <a
                href="#contact"
                className="inline-flex items-center gap-1.5 rounded-md border border-border bg-card px-5 py-2.5 text-sm font-medium text-foreground transition hover:bg-secondary"
              >
                <Mail className="h-4 w-4" />
                Contact me
              </a>
            </div>
          </div>
        </div>

        <dl className="mt-16 grid grid-cols-2 gap-x-6 gap-y-8 border-t border-border/60 pt-10 md:grid-cols-4">
          <Stat k="3+" v="Shipped projects" />
          <Stat k="AWS" v="EC2 · S3 · VPC · IAM" />
          <Stat k="NLP" v="GPT-2 · BERT · Transformers" />
          <Stat k="Full-stack" v="React · Flask · SQL" />
        </dl>
      </div>
    </section>
  );
}

function Stat({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-2xl font-semibold tracking-tight md:text-3xl">{k}</dt>
      <dd className="mt-1 text-sm text-muted-foreground">{v}</dd>
    </div>
  );
}

function SectionHeader({ kicker, title, lede }: { kicker: string; title: string; lede?: string }) {
  return (
    <div className="max-w-2xl">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-accent">{kicker}</p>
      <h2 className="mt-3 text-3xl tracking-tight md:text-4xl">
        <span className="font-serif italic">{title}</span>
      </h2>
      {lede ? <p className="mt-4 text-base leading-relaxed text-muted-foreground">{lede}</p> : null}
    </div>
  );
}

function Projects() {
  return (
    <section id="work" className="border-b border-border/60">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-24">
        <SectionHeader
          kicker="Selected work"
          title="Projects that move ideas to production."
          lede="A cross-section of AI research, computer vision, and cloud-native engineering."
        />
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {projects.map((p) => (
            <article
              key={p.n}
              className="group flex h-full flex-col rounded-xl border border-border bg-card p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-accent/60 hover:shadow-md"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium tracking-widest text-muted-foreground">{p.n}</span>
                <span className="rounded-full border border-border bg-secondary px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-secondary-foreground">
                  {p.tag}
                </span>
              </div>
              <h3 className="mt-6 text-lg font-semibold tracking-tight">{p.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{p.body}</p>
              <ul className="mt-6 flex flex-wrap gap-1.5">
                {p.stack.map((s) => (
                  <li key={s} className="rounded-md bg-secondary px-2 py-1 text-[11px] font-medium text-secondary-foreground">
                    {s}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function Skills() {
  return (
    <section id="skills" className="border-b border-border/60 bg-secondary/40">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-24">
        <SectionHeader
          kicker="Technical stack"
          title="A stack tuned for AI, cloud, and shipping fast."
        />
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {skills.map((s) => {
            const Icon = s.icon;
            return (
              <div key={s.group} className="rounded-xl border border-border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <span className="grid h-9 w-9 place-items-center rounded-md bg-accent/10 text-accent">
                    <Icon className="h-4 w-4" />
                  </span>
                  <h3 className="text-sm font-semibold tracking-tight">{s.group}</h3>
                </div>
                <ul className="mt-6 space-y-2.5">
                  {s.items.map((i) => (
                    <li key={i} className="flex items-center gap-2.5 text-sm text-foreground/90">
                      <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent" />
                      {i}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function Experience() {
  return (
    <section id="experience" className="border-b border-border/60">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-24">
        <SectionHeader kicker="Experience & education" title="Where I've been learning to build." />
        <ol className="mt-12 space-y-4">
          {timeline.map((it) => {
            const Icon = it.icon;
            return (
              <li
                key={it.role}
                className="grid gap-4 rounded-xl border border-border bg-card p-6 shadow-sm md:grid-cols-[160px_1fr] md:gap-8"
              >
                <div className="flex items-center gap-3 md:flex-col md:items-start md:gap-4">
                  <span className="grid h-9 w-9 place-items-center rounded-md bg-primary text-primary-foreground">
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
                    {it.when}
                  </div>
                </div>
                <div>
                  <h3 className="text-base font-semibold tracking-tight">{it.role}</h3>
                  <div className="text-sm text-accent">{it.org}</div>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{it.body}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}

function Contact() {
  return (
    <section id="contact" className="border-b border-border/60">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
        <div className="rounded-2xl border border-border bg-card p-10 shadow-sm md:p-14">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-accent">Contact</p>
          <h2 className="mt-3 max-w-2xl text-3xl tracking-tight md:text-5xl">
            Let's build something <span className="font-serif italic">meaningful</span>.
          </h2>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-muted-foreground">
            I'm actively exploring Software Engineering Associate, DevOps, and Cloud Support opportunities.
            Happy to talk about roles, collaborations, or a specific project.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a
              href="mailto:muruganlogesh409@gmail.com"
              className="inline-flex items-center gap-2 rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition hover:opacity-90"
            >
              <Mail className="h-4 w-4" />
              muruganlogesh409@gmail.com
            </a>
            <a
              href="https://www.linkedin.com/in/logesh-m-72b801258"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-md border border-border bg-background px-5 py-2.5 text-sm font-medium transition hover:bg-secondary"
            >
              <Linkedin className="h-4 w-4" />
              LinkedIn
            </a>
            <a
              href="https://github.com/loki401"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-md border border-border bg-background px-5 py-2.5 text-sm font-medium transition hover:bg-secondary"
            >
              <Github className="h-4 w-4" />
              GitHub
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer>
      <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-2 px-6 py-8 text-xs text-muted-foreground md:flex-row md:items-center">
        <span>© 2026 Logesh M. All rights reserved.</span>
        <span>Chennai, India</span>
      </div>
    </footer>
  );
}
