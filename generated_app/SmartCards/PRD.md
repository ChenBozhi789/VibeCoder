# Product Requirement Document

**App Name:** SmartCards  
**Goal/Purpose:** Help students and self-learners memorize and retain information efficiently using simple, offline-ready flashcards. Users can quickly add question/answer cards, review them one-by-one, and track what they know versus what needs more practice.

**Target Users:** Students, language learners, exam preppers, and professionals who need a lightweight, distraction-free tool to create and study flashcards on their own device.

## Core Features
- Flashcard CRUD: Create, view, edit, and delete cards with a question and answer. Optional tags help organization.
- Study Mode (One-by-One Review): Present cards sequentially or shuffled; reveal the answer, and mark each card as "Known" or "Unknown" with click or keyboard shortcuts.
- List & Preview: A central list of all cards showing the question, status (known/unknown), and last updated date, with quick delete.
- Search & Filter: Instant search by question/answer text and filters by tags and status (known/unknown).
- Data Portability: Export all cards to a JSON file and import them back (merge or replace).
- Basic Settings: Control import/export behavior and clear all local data with confirmation.

## Data Model
- **Main Entity:** Card
  - `id`: string (UUID, unique identifier)
  - `question`: string (required)
  - `answer`: string (required)
  - `status`: string enum ("unknown" | "known"), default "unknown"
  - `tags` (optional): array of strings
  - `createdAt`: ISO8601 timestamp
  - `updatedAt`: ISO8601 timestamp

(No secondary entities such as Decks are included by default. If needed later, a `deck` field or a separate Deck entity can be introduced.)

## User Interface (Views)
- **Home / List View:**
  - Displays a reverse-chronological list of cards (by updatedAt).
  - Key elements: Prominent "New Card" button, a search bar, and filter/sort controls (status, tags, A–Z/Recently Updated).
  - Each list item shows: question (truncated), status badge (Known/Unknown), updated date, and a quick delete action.
  - Multi-select delete is optional; start with single-item delete.

- **Detail / Form View:**
  - Clean form for creating or editing a card.
  - Fields: Question (textarea or large input), Answer (textarea), Tags (comma-separated chips).
  - Actions: Primary "Save" button; "Cancel" or back; "Delete" (with confirmation) for existing cards.

- **Study Mode View:**
  - Shows one card at a time. Initially displays the Question (front).
  - Controls: "Show Answer" (or flip). After reveal, display "Known" and "Unknown" actions.
  - Navigation: "Next" moves to the next card. Option to shuffle order before a session.
  - Progress: Simple progress indicator (e.g., 3/20 studied this session).
  - Keyboard shortcuts: Space to flip, 1 for Unknown, 2 for Known, Right Arrow for Next.
  - Filters for session: Study all, only Unknown, or by tag.

- **Settings View:**
  - **Import Data:** From a JSON file; user chooses merge or replace existing data.
  - **Export Data:** Download all cards as JSON.
  - **Clear All Data:** Wipes all local data with an explicit confirmation dialog.

## Assumptions
- **Platform:** Single-page web application running entirely in the browser.
- **Persistence:** Uses browser `localStorage` for data storage. No backend or cloud sync is required.
- **Offline First:** Fully functional without an internet connection.
- **Single-User:** No authentication, accounts, or collaboration.
- **UI/UX:** Clean, minimal, responsive design with basic accessibility (labels, keyboard navigation, sufficient contrast).

## Non-Functional Requirements
- **Performance:** UI remains responsive with 1,000+ cards; initial load under ~1 second on a modern browser.
- **Reliability:** Destructive actions require confirmation. Handle storage quota limits with user-friendly error messages.
- **Data Safety:** JSON import/export is the primary backup mechanism with a simple, documented schema.

## Implementation Notes / Developer Hints
- **Data Storage:**
  - Store all cards in one key: `SmartCards.cards` as an array of Card objects.
  - Optional settings in `SmartCards.settings` (e.g., last chosen study filter, shuffle preference).
- **State Management & UI:**
  - Prefer vanilla JS or a lightweight framework (Preact, Vue, or Svelte). Keep bundle size small.
  - Use semantic HTML for accessibility; ensure focus states and keyboard shortcuts.
- **Search/Filter Logic:**
  - Client-side filtering by status and tags; case-insensitive substring search on question and answer fields.
- **Study Mode Logic:**
  - Build the session queue from the current filter (e.g., Unknown-only); allow shuffle. Persist `status` changes immediately when the user marks Known/Unknown.
  - Keep session progress client-side in memory; no need to persist history initially.
- **Dependencies:**
  - Minimize external dependencies. Use native Web APIs where possible to ensure speed and maintainability.
