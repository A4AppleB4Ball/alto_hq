# Acceptance: checkout-guard-hardening (proposed, not approved)

1. **Two-hop link.** A test in `backend/config/tests/` builds, in a temp dir, a sandbox whose `data` links to a dir whose `alto_data` links into the live root; import raises CheckoutDeclarationError naming the path. Fails on base, passes after.
2. **Parent link.** Same for a link to a parent of the live root.
3. **Resolved paths, not a walk.** The guard checks the realpath of every PATH constant in `backend/config/paths.py` against the live root, instead of walking the sandbox tree. Import on a seeded ~450k-file sandbox root takes under 2 s (time shown).
4. **Live mode.** `mode: live` is accepted only in the main checkout, not any clone with a `.git` directory. Test fails on base, passes after.
5. **Repo checks.** `backend/config/tests` passes, boundary test, entry-point imports, full suite vs base with `comm -23`.
