# Overleaf-ready report and sync — MRAM p-bit low-order FP FYP

GitHub repo: https://github.com/Makise-okabe/MRAM_P-bit

The authoritative report source is **`main.tex` on GitHub default `main`**. It now contains the section **Proposed Coupling Array and Relationship to CIM**, retaining the 64–128-spin FP coupling tile and careful distinction between digital near-memory p-bit logic and a physically justified MRAM-CIM implementation. Additional architecture detail: `docs/ARCHITECTURE_CIM_SCOPE.md`.

**GitHub commit is NOT a push to an existing Overleaf project.** No Overleaf account/project write connection is installed in this chat. Overleaf's documented GitHub synchronization is a premium feature and requires you to choose **Integrations -> GitHub -> Pull GitHub changes** on a project already linked to this repo. Sync is manual, not automatic.

If your existing Overleaf project is **not linked to this GitHub repo**, Overleaf says linking an existing Overleaf project to an existing GitHub repository is not supported using GitHub Synchronization. Update that project's `main.tex` manually from GitHub, or create a NEW project from GitHub through the Overleaf GitHub import feature and use its pull control subsequently. Preserve existing Overleaf changes before copying.

Official docs: https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/github-synchronization

Alternative for an eligible project: Overleaf's separate premium Git integration can expose an authenticated Git remote that you can push to using a user-held token; do not share tokens in chat. See https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/git-integration

When editing technical findings in future, update and cite both the relevant GitHub research note and `main.tex`. Do not imply that Overleaf has synced until it actually has.
