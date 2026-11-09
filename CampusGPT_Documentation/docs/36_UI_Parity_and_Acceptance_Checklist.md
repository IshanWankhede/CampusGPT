# 36 — UI Parity and Acceptance Checklist

Run per screen at P24 and after each UI phase. Record evidence (screenshot, route, viewport).

## A. Fidelity to the prototype and references
- [ ] Layout, hierarchy and spacing match the mapped prototype screen
- [ ] Colours come from tokens; no ad-hoc hex values
- [ ] Typography scale and weights consistent
- [ ] Icons are Lucide, consistent size and stroke
- [ ] Cards, tables, forms, dialogs, dropdowns, charts share the same styling
- [ ] Animations match intent and respect reduced motion

## B. Dark-mode-only
- [ ] No white or light surfaces anywhere (including dialogs, dropdowns, date pickers, charts, tooltips, scrollbars, print views excluded)
- [ ] `color-scheme: dark` set; no light media-query branches
- [ ] No theme toggle

## C. Behaviour (no dead UI)
- [ ] Every button, link, menu item and filter does something real
- [ ] Loading, empty, error and permission-denied states exist
- [ ] Forms validate with clear messages; server errors shown
- [ ] No prototype mock data; data comes from the API

## D. Role correctness
- [ ] Navigation shows only the role's items
- [ ] Direct URL to another role's route is blocked in UI **and** by the API (tested)

## E. Responsive
- [ ] 360, 768, 1024, 1280, 1536 px verified; no horizontal scroll; touch targets ≥ 44 px

## F. Accessibility
- [ ] Keyboard-only path through each screen; visible focus
- [ ] Labels, ARIA for dialogs/menus; screen-reader check on chat and tables
- [ ] Contrast ≥ 4.5:1 for text (doc 33 table re-measured on rendered pages)
- [ ] `prefers-reduced-motion` honoured

## G. Preservation
- [ ] Landing, sign-in, sign-up pages visually unchanged
- [ ] Auth flows still pass the Foundation regression checklist

## Result
Screen: ______ Reviewer: ______ Date: ______ Parity: PASS / FAIL (list defects)
