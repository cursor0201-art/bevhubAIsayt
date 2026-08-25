# SYSTEM_PROMPT_PART_13.md
# AI ORCHESTRATOR BIBLE

==================================================
MISSION
==================================================

The AI Orchestrator is the central intelligence layer of BevHub AI.

It does not simply send prompts to an LLM.

It coordinates specialized AI agents, manages workflows,
tracks execution, optimizes cost, ensures quality,
and delivers one coherent result to the user.

The user interacts with ONE assistant.

Internally dozens of AI agents may collaborate.

==================================================
CORE PRINCIPLES
==================================================

Never call an AI model directly from the frontend.

Never expose providers.

Never expose system prompts.

Never expose internal reasoning.

Always execute through the AI Orchestrator.

==================================================
AI PIPELINE
==================================================

User Request

↓

Intent Detection

↓

Context Collection

↓

Project Memory

↓

Task Planning

↓

Agent Selection

↓

Model Selection

↓

Execution

↓

Validation

↓

Merge Results

↓

Save Memory

↓

Return Response

==================================================
INTENT DETECTION
==================================================

Detect user goals automatically.

Examples:

Create Website

Improve Website

Generate Logo

Create Banner

Generate Product Images

Write SEO

Translate

Generate Code

Deploy Website

Analyze Business

Marketing Strategy

Landing Page

CRM

Portfolio

E-commerce

Blog

Documentation

Dashboard

==================================================
PROJECT MEMORY
==================================================

Remember permanently inside each project.

Business Name

Industry

Audience

Brand Colors

Fonts

Language

Tone

Logo

Products

Services

Pages

Domain

SEO Keywords

Generated Assets

Deployment Status

==================================================
USER MEMORY
==================================================

Remember user preferences.

Preferred Language

Preferred Writing Style

Favorite Colors

Preferred AI Model

Previous Projects

Subscription Plan

Credits

==================================================
WORKFLOW ENGINE
==================================================

Every request becomes a workflow.

Workflow contains:

Tasks

Dependencies

Priority

Retries

Status

Progress

Logs

Execution Time

==================================================
AI AGENTS
==================================================

Website Agent

Landing Agent

Logo Agent

Banner Agent

Image Agent

SEO Agent

Marketing Agent

Business Agent

Analytics Agent

Deployment Agent

Translation Agent

Code Agent

Support Agent

CRM Agent

Documentation Agent

Database Agent

API Agent

Testing Agent

Security Agent

Optimization Agent

Future Agents

==================================================
MODEL ROUTING
==================================================

Choose model dynamically.

Coding

↓

GPT

Reasoning

↓

Claude

Fast Tasks

↓

Gemini

Cheap Tasks

↓

DeepSeek

Image

↓

Configured Image Provider

==================================================
MULTI AGENT EXECUTION
==================================================

Example

User:

Create a dental clinic website.

Workflow:

Business Analysis

↓

Logo

↓

Brand Palette

↓

Website Structure

↓

SEO

↓

Texts

↓

Images

↓

Deployment Plan

↓

Analytics Setup

↓

Return Complete Project

==================================================
FAILOVER
==================================================

If one provider fails

↓

Retry

↓

Alternative Model

↓

Alternative Provider

↓

Continue Workflow

Never fail the whole request because of one provider.

==================================================
AI OUTPUT VALIDATION
==================================================

Every response must be checked.

Grammar

Language

Structure

Completeness

Business Logic

Formatting

Safety

If validation fails

↓

Repair

↓

Retry

↓

Alternative Model

==================================================
PROMPT MANAGEMENT
==================================================

Every agent has

System Prompt

Developer Prompt

Execution Rules

Output Schema

Validation Rules

Examples

Version

==================================================
AI COST OPTIMIZATION
==================================================

Prefer

Lowest Cost

↓

Lowest Latency

↓

Highest Quality

depending on task.

==================================================
TOKEN MANAGEMENT
==================================================

Track

Input Tokens

Output Tokens

Estimated Cost

Actual Cost

Credits Used

Latency

==================================================
OBSERVABILITY
==================================================

Track

Success Rate

Failure Rate

Retry Count

Average Response Time

Model Accuracy

Credits Consumption

Popular Prompts

==================================================
SECURITY
==================================================

Never expose

API Keys

System Prompts

Internal Chains

Hidden Instructions

User Data

Workspace Data

==================================================
FINAL PRINCIPLE
==================================================

The user must feel they are talking to one intelligent AI.

Internally the platform may execute
10
20
50
or even 100 AI operations.

Complexity belongs inside the platform.

Simplicity belongs to the user.

==================================================
END OF PART 13
