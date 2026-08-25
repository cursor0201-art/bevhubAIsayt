# BEVHUB AI
# CODE REVIEW CONTRACT
# Version 1.0

==================================================
MISSION
==================================================

Every line of code must pass engineering review before being considered complete.

Working code is not sufficient.

The implementation must satisfy

Architecture
Maintainability
Security
Performance
Readability
Scalability

==================================================
INPUT
==================================================

Changed Files
Git Diff
Feature Specification
Architecture
Task Contract

==================================================
REVIEW PROCESS
==================================================

Read Entire Change
↓
Understand Purpose
↓
Compare Against Architecture
↓
Find Bugs
↓
Find Edge Cases
↓
Find Security Problems
↓
Find Performance Problems
↓
Find Maintainability Problems
↓
Approve or Reject

==================================================
ARCHITECTURE REVIEW
==================================================

Verify

No duplicated logic
No architecture violations
Correct layer responsibilities
Proper abstractions
Correct dependencies

==================================================
BACKEND REVIEW
==================================================

Verify

Transactions
Validation
Permissions
Authentication
Authorization
Logging
Error Handling
Rate Limiting

==================================================
FRONTEND REVIEW
==================================================

Verify

Accessibility
Responsive Design
Reusable Components
Hooks
Performance
Error States
Loading States

==================================================
DATABASE REVIEW
==================================================

Verify

Indexes
Constraints
Relations
Migration Safety
Rollback

==================================================
SECURITY REVIEW
==================================================

Verify

SQL Injection
XSS
CSRF
Secrets
Environment Variables
Sensitive Data

==================================================
PERFORMANCE REVIEW
==================================================

Verify

Slow Queries
Bundle Size
React Rendering
Caching
Lazy Loading
Network Requests

==================================================
QUALITY SCORE
==================================================

Architecture
Security
Performance
Readability
Maintainability
Testing
Documentation

==================================================
OUTPUT
==================================================

Approve
Reject
Required Changes
Optional Improvements
Risk Analysis

==================================================
FINAL RULE
==================================================

Never approve code that you would not deploy to production.
