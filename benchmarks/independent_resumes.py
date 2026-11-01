"""Fictional evaluation resumes, explicitly not real people.
Never use as application materials or assert achievements as real.
"""
RESUMES = {
'rails': '''SYNTHETIC BENCHMARK RESUME — fictional candidate, not a real applicant
Software Engineer — Ruby on Rails and payments
Contact: benchmark-rails@example.test
PROFILE
Product engineer with seven years of experience building and maintaining Ruby on Rails applications for small and medium SaaS teams. Focused on high-reliability subscription billing and customer-service workflows, background tasks, and production debugging. Comfortable translating product requirements into code, reviewing merge requests, and collaborating remotely.
SKILLS
Ruby, Ruby on Rails, ActiveRecord, PostgreSQL, Redis, Sidekiq, RSpec, Capybara, Hotwire, Turbo, Stimulus, JavaScript, CSS, HTML, GitHub Actions, Docker, Heroku, REST APIs, OAuth2, Stripe Billing, Stripe Connect, performance profiling, automated tests, Agile.
EXPERIENCE
Senior Rails Engineer — Fictional Storage Products, 2022–2026
Designed booking, inventory, facility and subscription workflows in a Rails monolith serving storage operators. Built Rails backend APIs, ActiveRecord models and PostgreSQL schema migrations for customers and payments. Implemented Stripe billing events with idempotency guards and reconciliation. Optimized slow PostgreSQL queries with indexes. Integrated Redis/Sidekiq background jobs for payment retries and email notifications. Built Hotwire/Turbo views and accessible UI components. Wrote request specs and integration tests using RSpec and Capybara. Reviewed code and diagnosed production incidents through logs.
Software Engineer — Sample Commerce Platform, 2019–2022
Built Rails commerce features and JavaScript admin screens. Added OAuth integrations with third-party services, maintained REST endpoints, and automated deployment tests in GitHub Actions. Refactored fragile payment logic and validated fixes before production release.
EDUCATION
Bachelor of Science in Computer Science, Example University, 2019.
PROJECT
Open-source example: Rails subscription management demo with Stripe test mode, PostgreSQL and automated RSpec suite.''',
'frontend': '''SYNTHETIC BENCHMARK RESUME — fictional candidate, not a real applicant
Senior Frontend Engineer — React / Next.js / TypeScript
Contact: benchmark-frontend@example.test
PROFILE
Frontend-focused engineer with six years of production experience delivering secure, responsive business dashboards and administration tools. Experienced in translating designs into accessible interfaces, integrating backend APIs and managing deployments, with rigorous regression testing.
SKILLS
React, TypeScript, Next.js, App Router, server components, middleware, API routes, Vitest, React Testing Library, Playwright, RBAC, role-based access control, authentication, JavaScript, AWS, Docker, GitHub Actions, CI/CD, WCAG accessibility, state management, UI performance, API gateways, Git.
EXPERIENCE
Senior Frontend Engineer — Example Portal Company, 2022–2026
Developed React and Next.js App Router portals using TypeScript. Built server components and server-side authentication, implemented role-based access control (RBAC), and integrated internal backend APIs through server-side API gateways. Wrote automated unit tests with Vitest and React Testing Library and end-to-end browser tests with Playwright. Improved frontend rendering speed by 38% through code splitting, caching and profiling. Automated deployments on AWS using Docker and GitHub Actions CI/CD; investigated production failures. Conducted code reviews and verified AI-assisted code against user acceptance criteria.
Frontend Developer — Example Commerce Studio, 2020–2022
Delivered React dashboards for business users, fixed integration bugs, developed WCAG-accessible forms, and built component libraries with TypeScript. Collaborated across product and engineering and mentored junior developers. Maintained a production deployment checklist.
EDUCATION
BSc Computer Science, Fictional University, 2020.
PROJECTS
Open-source admin dashboard demo with Next.js, secure authentication, automated frontend tests and accessible navigation.''',
'backend': '''SYNTHETIC BENCHMARK RESUME — fictional candidate, not a real applicant
Senior Backend Engineer — Python / Django / Distributed Systems
Contact: benchmark-backend@example.test
PROFILE
Backend engineer with eight years of commercial Python experience building secure enterprise SaaS services and data-intensive applications. Owns distributed services from design and testing to production monitoring and incident response. Familiar with Agile cross-functional delivery and responsible AI-assisted programming.
SKILLS
Python 3, Django, Django REST Framework, FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, AWS, Kubernetes, Docker, CI/CD, SQL, complex schemas, query optimization, data migrations, microservices, REST APIs, event-driven task processing, observability, monitoring, security, distributed systems, documentation.
EXPERIENCE
Senior Python Engineer — Example Housing SaaS, 2021–2026
Designed and implemented Python/Django REST Framework and FastAPI microservices for housing repairs, invoices and notifications deployed on AWS and Kubernetes. Created technical designs and ERD diagrams for complex PostgreSQL relational models. Optimized SQL queries, indexes and transactional migrations to improve throughput by 40%. Implemented Redis caching and Celery asynchronous task processing for notifications and reconciliation. Maintained CI/CD, Docker containers and automatic tests. Added observability, logging, metrics and incident alerts; resolved production errors. Performed code reviews and inspected AI-generated changes for correctness and security. Mentored engineers and coordinated technical specifications with the product team.
Backend Developer — Example Workflow Systems, 2018–2021
Built scalable Django APIs and backend integrations. Diagnosed database deadlocks, added rollback plans, documented architecture trade-offs and improved service performance. Managed PostgreSQL backups, security reviews and operational runbooks.
EDUCATION
Bachelor of Science in Software Engineering, Fictional University, 2018.
PROJECT
Documented Django/Redis/Celery demo with automated tests and deployment guide.''',
'security': '''SYNTHETIC BENCHMARK RESUME — fictional candidate, not a real applicant
Senior Application Security Engineer — Python / Product Security
Contact: benchmark-security@example.test
PROFILE
Security engineer with seven years of experience protecting production web applications, cloud infrastructure and developer pipelines. Conducts code reviews, threat modeling, penetration tests, vulnerability research and disclosure handling; works directly with engineers to deliver verified remediations.
SKILLS
Python, application security, API security, OWASP, vulnerabilities, vulnerability management, CVE intake, vulnerability disclosure, threat models, security reviews, cloud security, AWS, Docker, GitHub Actions, CI/CD, SAST, DAST, Semgrep, Bandit, CodeQL, Burp Suite, Snyk, Trivy, Grype, SBOM, Sigstore, Cosign, SSRF, SQL injection, command injection, secrets exposure, unsafe deserialization, secure pipelines, incident triage, tenant isolation, access control, authentication, LLM security.
EXPERIENCE
Senior Product Security Engineer — Example AI Gateway, 2022–2026
Led a security program for a multi-tenant Python API gateway, triaging vulnerability reports, verifying CVEs and establishing coordinated disclosure workflows. Identified SSRF and authorization failures in production APIs and delivered code changes with automated regression tests. Reviewed Python code with Semgrep, Bandit, CodeQL and Burp Suite; documented threats and remediations. Integrated SAST/DAST checks into GitHub Actions CI/CD and secured Docker build artifacts using SBOM, Sigstore, Cosign, Trivy and dependency scanning. Reviewed cloud security, secrets handling and tenant isolation. Resolved security incidents with engineering teams and documented risk decisions. Reviewed AI-generated security fixes manually before shipping.
Application Security Engineer — Example Cloud Service, 2019–2022
Performed source-code audits and penetration testing, maintained Snyk vulnerability alerts, participated in incident response and improved secure development guidelines.
EDUCATION
BSc Computer Science, Fictional University, 2019.
PROJECT
Open-source Python API threat-modeling and Semgrep rules package.''',
}
