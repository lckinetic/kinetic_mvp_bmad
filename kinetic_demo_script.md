# Kinetic MVP — Demo Script (CTO Audience)

## Objective
Demonstrate Kinetic as a workflow orchestration layer combining:
- Prebuilt workflows
- AI-generated workflows
- Unified execution engine

---

## 1. Problem
Building crypto workflows requires stitching multiple providers (onramp, custody, trading, payouts), leading to complexity and slow delivery.

---

## 2. Solution
Kinetic abstracts integrations into reusable workflow components and allows execution via UI or AI.

---

## 3. Demo Part 1 — Prebuilt Workflow
Go to /ui and run:
Treasury Rebalance (Demo)

Show:
- Step execution
- Metrics
- Logs

Message:
Deterministic execution and reliability.

---

## 4. Demo Part 2 — AI Workflow
Go to /ui/ai

Input:
Buy BTC and withdraw to wallet

Click Generate

Show:
- Workflow card
- Steps

Message:
AI creates structured executable workflows.

---

## 5. User Control
Edit JSON:
Change amount from 100 → 250

Message:
AI suggests, user controls.

---

## 6. Execute Workflow
Click Run

Show:
- Step execution
- Output

Message:
Same engine powers both AI and templates.

---

## 7. Architecture
Highlight:
- Modular monolith
- Adapter pattern
- Graph runner + template runner

---

## 8. Closing
Kinetic turns integrations into programmable workflows.

---

## Demo Tips
Use safe prompts:
- Buy BTC and withdraw to wallet
- Create a wallet
- Fund wallet with USDC
