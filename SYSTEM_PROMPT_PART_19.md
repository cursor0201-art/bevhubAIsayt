# SYSTEM_PROMPT_PART_19.md
# TESTING • QA • RELIABILITY BIBLE

==================================================
MISSION
==================================================

Every feature must be tested before it is considered complete.

Testing is not optional.

Quality is built continuously,
not added at the end.

==================================================
QUALITY PHILOSOPHY
==================================================

Every bug has a cause.

Every cause must be eliminated.

Prevent bugs instead of fixing bugs.

==================================================
TEST PYRAMID
==================================================

Unit Tests

↓

Integration Tests

↓

API Tests

↓

End-to-End Tests

↓

Manual QA

==================================================
UNIT TESTS
==================================================

Every

Service

Utility

Validator

Business Logic

Permission

Parser

Formatter

Must have unit tests.

==================================================
INTEGRATION TESTS
==================================================

Verify

Database

Redis

Celery

Payments

Authentication

AI Router

Storage

==================================================
API TESTS
==================================================

Verify

Authentication

Authorization

Validation

Rate Limits

Pagination

Filtering

Sorting

Error Responses

==================================================
END TO END TESTS
==================================================

Critical User Flows

Register

Login

Create Project

Generate Website

Generate Logo

Upgrade Plan

Purchase Credits

Deploy Project

Delete Project

==================================================
PERFORMANCE TESTS
==================================================

Measure

API Response

Database Speed

AI Latency

Cache Hit Rate

Memory

CPU

Bandwidth

==================================================
LOAD TESTS
==================================================

Support

100 Users

1,000 Users

10,000 Users

100,000 Users

1,000,000 Users

==================================================
SECURITY TESTS
==================================================

SQL Injection

XSS

CSRF

Broken Authentication

Privilege Escalation

Rate Limit

JWT Validation

==================================================
VISUAL TESTS
==================================================

Verify

Layout

Spacing

Typography

Responsive Design

Dark Mode

Light Mode

Animations

==================================================
ACCESSIBILITY TESTS
==================================================

Keyboard Navigation

Focus Order

Contrast

ARIA Labels

Screen Readers

Reduced Motion

==================================================
AI TESTS
==================================================

Verify

Intent Detection

Routing

Prompt Quality

Fallback

Retry

Output Validation

Token Usage

Credit Usage

==================================================
FAILURE TESTS
==================================================

Database Down

Redis Down

Provider Down

Timeout

Slow Network

Disk Full

Payment Failure

==================================================
MONITORING
==================================================

Track

Errors

Latency

Memory

CPU

Queue

Workers

Payments

Deployments

AI Providers

==================================================
RELEASE CHECKLIST
==================================================

All Tests Pass

No Critical Bugs

No Console Errors

Performance OK

Security OK

Accessibility OK

SEO OK

==================================================
DEFINITION OF DONE
==================================================

A feature is complete only when

Business Logic Complete

Tests Complete

Documentation Complete

Security Verified

Performance Verified

Accessibility Verified

Deployment Verified

==================================================
FINAL RULE
==================================================

Never release software that has not been tested.

Every release must increase user trust.

==================================================
END OF PART 19
