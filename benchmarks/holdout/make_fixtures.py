"""Non-sensitive fictional resumes and externally sourced job requirements.
No purported Upplai reference scores: provider blocked further calls.
"""
import json
from pathlib import Path
ROOT=Path(__file__).parent
RESUMES={
"rails_specialist":'''BENCHMARK ONLY — SYNTHETIC RESUME; DOES NOT REPRESENT A REAL PERSON
Role: Senior Ruby on Rails Product Engineer
Email: synthetic-rails@example.test
SUMMARY
Seven years delivering Rails SaaS applications with payment, subscription, and customer management systems. Focus on database correctness, background workers, test automation, secure API integration, and production debugging. Collaborates remotely with distributed product teams and reviews pull requests.
TECHNICAL SKILLS
Ruby, Ruby on Rails, ActiveRecord, PostgreSQL, MySQL, Redis, Sidekiq, Rails 7, Hotwire, Turbo, Stimulus, CSS, JavaScript, Stripe Connect, Stripe Billing, REST APIs, RSpec, Capybara, Minitest, GitHub Actions, Docker, AWS, Heroku, Git, CI/CD, monitoring, caching, authentication, OAuth, OWASP, accessibility.
EXPERIENCE
Lead Ruby Engineer — Invented Storage Software, 2022–2026
Designed Rails and ActiveRecord data models for storage facilities, inventory, customer billing and online reservations. Owned PostgreSQL indexing and zero-downtime migrations to improve reporting performance. Integrated Stripe subscription billing with retry-safe webhook handlers and Sidekiq background workers. Implemented Redis caching for high-traffic product pages. Delivered Hotwire/Turbo interface workflows, fixed production incidents, and wrote RSpec integration tests. Reviewed code and coached three junior engineers on Rails architecture.
Software Developer — Sample Online Commerce, 2019–2022
Developed Rails API endpoints and admin screens with JavaScript and CSS. Maintained database transactions, login permissions and OAuth integrations; improved Ruby service-object coverage with RSpec and Capybara tests. Deployed Dockerized applications to AWS and Heroku through GitHub Actions and documented releases for support engineers.
SELECTED PROJECT
An internal product demo for multi-tenant subscription plans with Rails, PostgreSQL, Redis, Stripe sandbox events and monitoring.
EDUCATION
Bachelor of Science in Computer Science, Fictional Institute, 2019.''',
"react_specialist":'''BENCHMARK ONLY — SYNTHETIC RESUME; DOES NOT REPRESENT A REAL PERSON
Role: Frontend Engineer — React and TypeScript
Email: synthetic-react@example.test
SUMMARY
Six years building accessible, responsive, data-rich consumer web applications. Specialized in design-system components, large React projects, modern TypeScript and frontend performance. Strong accessibility standards and cross-functional collaboration with UX and backend teams.
TECHNICAL SKILLS
React, React 19, TypeScript, Next.js, App Router, server components, Tailwind CSS, Redux Toolkit, Zustand, TanStack Query, JavaScript, HTML5, CSS, REST APIs, GraphQL, Apollo Client, Figma, WCAG, Core Web Vitals, SEO, Vite, Vitest, Testing Library, Playwright, Jest, Cypress, Storybook, GitHub Actions, Docker, AWS, CI/CD.
EXPERIENCE
Senior Frontend Engineer — Fictional Consumer Marketplace, 2021–2026
Developed customer-facing listing and filtering pages using React and Next.js App Router. Designed reusable accessible UI components from Figma specifications with Tailwind CSS and TypeScript. Integrated REST and GraphQL API endpoints with loading, error and empty states. Led performance improvements in bundle size, lazy loading and image delivery; reported improvement in Largest Contentful Paint on internal benchmarks. Implemented role-based administration screens with Redux Toolkit and authentication hooks. Wrote Vitest, React Testing Library and Playwright suites and reviewed production changes with other developers.
Frontend Developer — Example Travel Product, 2019–2021
Built JavaScript and React bookings pages, forms and a responsive checkout UI. Collaborated with product designers and backend engineers on API contracts. Added keyboard navigation and high-contrast improvements in accordance with WCAG guidance. Deployed through CI/CD and supported incident troubleshooting.
PROJECTS
Interactive Next.js dashboard demonstration, with API data loading, pagination, theme switching and test automation.
EDUCATION
BSc Software Engineering, Example Institute, 2019.''',
"python_data":'''BENCHMARK ONLY — SYNTHETIC RESUME; DOES NOT REPRESENT A REAL PERSON
Role: Senior Data Engineer
Email: synthetic-data@example.test
SUMMARY
Over seven years developing production batch and streaming data pipelines for analytics and machine learning. Strong Python, advanced SQL, cloud data warehouses and orchestrated ETL/ELT. Focused on data quality, monitoring, reliability and cost-performance optimization.
TECHNICAL SKILLS
Python, PySpark, Apache Spark, Apache Airflow, Snowflake, dbt, Kafka, Parquet, Apache Iceberg, AWS, S3, AWS Glue, EMR, Lambda, Snowpark, Snowpipe, Terraform, Docker, CI/CD, GitHub Actions, SQL, window functions, CTEs, Spark tuning, dimensional modeling, lakehouse, data lineage, Great Expectations, Azure, GCP, Pandas.
EXPERIENCE
Senior Data Engineer — Invented Cloud Analytics Firm, 2021–2026
Developed AWS data lake and Spark/PySpark processing pipelines that transform business transactions into Snowflake data marts. Wrote dbt models for slowly changing dimensions and business metrics. Orchestrated daily datasets and backfills with Apache Airflow, optimizing execution and failure retries. Maintained data-quality validation, monitoring and lineage for critical downstream dashboards. Migrated Parquet datasets to Iceberg tables in a lakehouse and partnered with machine-learning engineers on feature-ready extracts. Added CI/CD tests, infrastructure deployment with Terraform and cloud cost-monitoring alerts.
Data Platform Engineer — Example Retail Analytics, 2018–2021
Built high-volume SQL data models with complex joins, CTEs and window functions. Migrated stored procedures to Python and created automated warehouse loading jobs. Operated Kafka streams and AWS S3 staging, with alerting for late records and duplicate events. Contributed to code review and operational runbooks.
PROJECTS
Open-source benchmark example: Airflow DAGs orchestrating data quality checks in PySpark and Snowflake.
EDUCATION
BSc Computer Science, Fictional Institute, 2018.''',
"security_specialist":'''BENCHMARK ONLY — SYNTHETIC RESUME; DOES NOT REPRESENT A REAL PERSON
Role: Application Security Engineer and Software Developer
Email: synthetic-appsec@example.test
SUMMARY
Seven years developing applications and reviewing production web services for security vulnerabilities. Focus on software assurance, threat modeling, penetration testing, security code review, authentication, authorization and safer deployment practices.
TECHNICAL SKILLS
Python, JavaScript, TypeScript, Java, C#, Ruby, Go, OWASP ASVS, OWASP API Top 10, secure code review, SAST, DAST, Semgrep, Bandit, CodeQL, Burp Suite, GitHub Actions, Docker, AWS, Terraform, threat modeling, vulnerability assessment, penetration testing, incident response, API security, dependency scanning, SBOM, Trivy, secrets scanning, SSRF, SQL injection, CSRF, OIDC, OAuth2, JWT, Cloudflare.
EXPERIENCE
Senior Application Security Engineer — Fictional SaaS Provider, 2022–2026
Performed structured reviews of Node.js, React and Python applications for input validation, IDOR, authorization bypass, unsafe deserialization, SSRF and injection paths. Triaged automated Semgrep, CodeQL, Bandit and DAST alerts; reproduced findings and provided developers with remediation patches and unit-test proof. Built threat models and implemented GitHub Actions checks for dependency vulnerabilities, leaked secrets and container image scanning using Trivy. Improved incident response playbooks and coached software teams on secure authentication and access control. Reviewed an internal AI-powered feature for prompt injection and excessive tool permissions.
Security Engineer — Invented Financial Platform, 2019–2022
Conducted authenticated penetration tests using Burp Suite and developed Python-based scanning helpers. Helped application teams fix CSRF, OAuth and API access-control issues. Supported cloud access-control reviews and AWS infrastructure-as-code security checks using Terraform.
SELECTED WORK
Redacted sample security finding format, proof-of-concept scripts and verified remediation tests.
EDUCATION
BSc Computer Security, Example University, 2019.'''
}
JOBS={
"garirhat_frontend":{"title":"GarirHat Senior Frontend Engineer","family":"frontend","url":"https://www.garirhat.com/careers/senior-frontend-engineer","jd":'''Senior Frontend Engineer — GarirHat, Dhaka, Bangladesh, hybrid, full time. Own the buyer-facing marketplace experience: vehicle listings, search and filtering, vehicle comparisons, dealer showroom and detail views. Build and maintain customer-facing features in React and TypeScript, including search, sorting, filtering and listing pages. Maintain Core Web Vitals and page-performance budgets for bundle size, image delivery, lazy loading and performance profiling. Partner with design to implement accessible responsive components from Figma specifications. Own engineering quality across the frontend with pull request reviews, automated tests and strict typing. Collaborate with backend API engineers on REST API contracts. Requirements: five or more years production React and TypeScript experience, strong CSS layout and responsive design, accessibility according to WCAG 2.1 AA, Next.js App Router and server components with caching semantics. Experience measuring and fixing real performance problems and working knowledge of PostgreSQL and REST API design. Bonus: SEO, state management, CI/CD automation and architecture for large frontend applications.'''},
"virtualfusion_backend":{"title":"VirtualFusion Backend Developer","family":"backend","url":"https://virtualfusion.ai/careers/backend-developer","jd":'''Backend Developer — VirtualFusion, full-time remote, AI enterprise products. Develop scalable high-performance Python backend infrastructure and reliable APIs used by enterprise clients. Build REST APIs with Python, Django and FastAPI, implement distributed systems, use async task processing with Celery, message queues with RabbitMQ, and Redis caching and real-time features. Design service integrations, data-processing workflows and robust cloud-facing backend applications. Skills: hands-on Django, FastAPI, Python, Celery, RabbitMQ, Redis, PostgreSQL, distributed systems, microservices, database performance and query optimization. Bonus: AWS, GCP or Azure cloud platforms, Docker containerization, monitoring and observability, application security, integration testing and production debugging. Collaborate with product teams on architecture, release quality and incident resolution.'''},
"invadel_appsec":{"title":"Invadel Application Security Engineer","family":"security","url":"https://invadel.com/careers/application-security-engineer/","jd":'''Application Security Engineer (Source Code Review) — Invadel, remote United States only. Conduct source code security reviews that combine static analysis and manual penetration testing. Find authentication vulnerabilities, authorization flaws, injection paths, business logic defects, cryptographic misuse, insecure third-party dependencies, and secrets-management failures in production web, mobile and backend software. Triage false-positive SAST results, trace data flows across services, and demonstrate practical exploitability in safely scoped proof-of-concepts. Write security findings with file and line references, technical impact, step-by-step reproduction and remediation code; retest fixes and update reports for engineers and auditors. Required: four or more years software engineering plus application security, strong source-code reading fluency in three languages among JavaScript, TypeScript, Python, Java, Kotlin, C#, Go, PHP, Ruby or Swift; web and API security, security testing, secure code review, pentesting and OWASP fundamentals. Nice to have reviewing AI-generated code, security tooling at scale, mobile code reviews or infrastructure-as-code risk analysis. Requires US location and legal work authorization.'''},
"pavago_rails":{"title":"Pavago Ruby on Rails Developer","family":"rails","url":"https://jobs.workable.com/view/dmN2ocrwTcnrNgPPis9AmP/remote-ruby-on-rails-developer-in-pakistan-at-pavago","jd":'''Ruby on Rails Developer — Pavago, fully remote Pakistan, U.S. client business hours. Build, maintain, optimize and scale production Rails web applications, APIs and background workers. Implement Rails MVC business logic with Ruby, ActiveRecord models, controllers, views and REST API integrations. Design PostgreSQL or MySQL schemas, write production-safe migrations, tune SQL queries and improve performance. Develop background processing using Sidekiq or Resque and Redis caching, focusing on reliable retries and asynchronous workflows. Write automated unit tests, integration tests and system tests with RSpec, Minitest and Capybara. Use Git, CI/CD and Heroku, AWS or GCP deployments. Secure the application through Devise/OmniAuth authentication, OWASP practices, CSRF protection and input validation; use monitoring systems such as Datadog and Rollbar. Collaborate with product managers, designers, and frontend engineers using React, Vue or Stimulus. Requires more than 3 years professional Rails experience, strong problem solving, debugging and code review, reliable remote collaboration and clear communication.'''},
"gain_data":{"title":"Gain America Data Engineer","family":"data","url":"https://gainam.com/data-engineer-remote-us","jd":'''Data Engineer — Gain America, remote United States, contract/contract-to-hire. Design and operate batch and streaming data pipelines, data warehouses and ELT/ETL platforms for analytics. Build reliable Python and SQL pipelines using Apache Spark / PySpark, Snowflake, dbt and Apache Airflow. Create data warehouse layers, dimensional models and quality tests; orchestrate Airflow DAGs, monitor reliability, late arrivals, and lineage. Use AWS or Azure cloud data platforms with secure data access and robust orchestration. Build integrations from APIs, databases and event streams and work with business intelligence and machine learning teams to deliver trusted data. Requirements: four or more years data engineering, strong Python and SQL, hands-on Spark, Snowflake, dbt, Airflow, AWS or Azure, workflow orchestration, cloud data architecture, data modeling, performance optimization and communication with analysts. Nice to have Kafka, ETL/ELT optimization, CI/CD, Docker and production monitoring. US based applicants only.'''}
}
ROOT.joinpath("synthetic_resumes.json").write_text(json.dumps(RESUMES,indent=2))
ROOT.joinpath("new_public_jobs.json").write_text(json.dumps(JOBS,indent=2))
print("Created",len(RESUMES),"synthetic resumes and",len(JOBS),"source-derived job briefs")
