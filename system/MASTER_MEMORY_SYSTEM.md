# MASTER_MEMORY_SYSTEM.md
# BevHub AI Memory System
# Version 1.0

==================================================
MISSION
==================================================

The Memory System provides a human-like, multi-tiered
retrieval mechanism.

It solves context window limitations by organizing
information into specialized storage layers,
ensuring the AI never forgets business goals,
user preferences, or code relationships.

==================================================
MEMORY HIERARCHY
==================================================

1. Conversation Memory
   - Stores transient chat history, immediate turns, and user corrections.
   - Provides context for the current active task.

2. Project Memory
   - Captures metadata of the generated project (name, domain, scope).
   - Tracks general MVP requirements and target user personas.

3. Workspace Memory
   - Maps the project directory structure, active file list, and environmental variables.
   - Tracks active edit sessions.

4. Knowledge Memory
   - Reference store of platform bibles, libraries, framework standards, and third-party APIs.
   - Integrates curated Knowledge Items (KIs).

5. Business Memory
   - Contains business model, target competitors, pricing tiers, and marketing channels.
   - Tracks ROI targets and conversion funnel definitions.

6. Developer Memory
   - Stores styling tokens, architectural patterns, naming conventions, and linting rules.
   - Captures previous build failure causes and automated repair histories.

7. Code Memory
   - Pre-computed AST (Abstract Syntax Tree) representations of codebase.
   - Tracks dependency relationships between files, database entities, and endpoints.

8. Long-Term Memory
   - Vector database storing semantic embeddings of previous conversations and user decisions.
   - Enables multi-session learning and personalized assistance.

==================================================
MEMORY PIPELINE
==================================================

Conversation Memory

↓

Project Memory

↓

Workspace Memory

↓

Knowledge Memory

↓

Business Memory

↓

Developer Memory

↓

Code Memory

↓

Long-term Memory

↓

Compression

↓

Semantic Search

↓

Timeline

==================================================
MEMORY OPERATIONS
==================================================

1. Compression: Automatically summarizes conversation logs when context length exceeds limits, extracting core decisions into Project Memory.
2. Semantic Search: Uses vector embeddings to query long-term memory for relevant code patterns or business rules.
3. Timeline & Versioning: Maintains snapshots of workspace states, enabling seamless rollback/restore operations.

==================================================
END OF MASTER MEMORY SYSTEM
