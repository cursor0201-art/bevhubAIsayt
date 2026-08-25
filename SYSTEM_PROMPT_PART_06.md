# SYSTEM_PROMPT_PART_06.md
# DATABASE & PLATFORM CORE

==================================================
MISSION
==================================================

The database is the single source of truth.

Every piece of information must have one owner.

Never duplicate data.

Design for millions of users.

==================================================
DATABASE ENGINE
==================================================

Primary Database

PostgreSQL

Redis

Cache

Queue

Session

Rate Limiter

Search

PostgreSQL Full Text

Future Ready

ElasticSearch

OpenSearch

==================================================
PRIMARY ENTITIES
==================================================

Users

Organizations

Workspaces

Projects

Folders

Templates

Conversations

Messages

AI Executions

AI Providers

AI Credits

Subscriptions

Invoices

Payments

Files

Media

Notifications

Logs

Audit Logs

Domains

Deployments

API Keys

Sessions

Devices

Roles

Permissions

Feature Flags

Analytics

Reports

==================================================
USER
==================================================

Every user contains

UUID

Email

Username

Display Name

Avatar

Password Hash

Language

Timezone

Country

Theme

Role

Subscription

Credits

Created At

Updated At

Deleted At

==================================================
WORKSPACE
==================================================

A workspace is an isolated environment.

Contains

Projects

Members

Files

Billing

Credits

Deployments

Settings

No data leaks between workspaces.

==================================================
PROJECT
==================================================

Every project contains

UUID

Owner

Workspace

Type

Name

Description

Prompt

Current Status

Current Version

AI History

Deployment

Domain

SEO

Analytics

Media

Created

Updated

==================================================
AI EXECUTION
==================================================

Every AI request stores

Prompt

Provider

Model

Execution Time

Input Tokens

Output Tokens

Credits Used

Latency

Success

Error

Retry Count

==================================================
SUBSCRIPTIONS
==================================================

Plans

Free

Starter

Pro

Business

Enterprise

Store

Renewal

Expiration

Status

Usage

Limits

==================================================
FILES
==================================================

Every uploaded file

UUID

Owner

Workspace

Project

Storage Provider

Mime Type

Size

Hash

URL

Security Level

==================================================
MEDIA LIBRARY
==================================================

Images

Videos

Documents

Generated Images

Generated Logos

Generated Banners

Generated PDFs

==================================================
VERSIONING
==================================================

Every project has versions.

User can

Restore

Duplicate

Compare

History

Undo

Redo

==================================================
SOFT DELETE
==================================================

Never permanently remove data immediately.

Support

Restore

Recovery

Audit

==================================================
BACKUPS
==================================================

Automatic Daily

Weekly

Monthly

Point In Time Recovery

Encrypted

Verified

==================================================
AUDIT LOGS
==================================================

Track everything.

Login

Logout

Password Change

Payment

Subscription

Deployment

Admin Action

Role Change

Deletion

Permission Changes

==================================================
ANALYTICS
==================================================

Store

Daily Active Users

Monthly Active Users

Retention

Credits Used

Popular Features

Generation Time

Average Session

Conversion Rate

Revenue

==================================================
DATABASE RULES
==================================================

Use UUID.

Never expose IDs.

Always index foreign keys.

Always validate relationships.

Always use transactions.

Always optimize queries.

Never use SELECT *.

Never allow orphan records.

==================================================
SCALABILITY
==================================================

Support

10 Users

↓

100 Users

↓

1,000 Users

↓

10,000 Users

↓

100,000 Users

↓

1 Million Users

↓

10 Million Users

without redesigning schema.

==================================================
FINAL PRINCIPLE
==================================================

The database is forever.

Poor database decisions become expensive.

Design carefully.

==================================================
END OF PART 06
