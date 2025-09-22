Creating a single PowerShell entrypoint removed the manual orchestration mistakes I made earlier when I ran pytest without the co
verage plugin installed. I also learned that the roadmap guard depends on the latest commit message; the guard suite failed local
ly until I wired the workflow and documentation to highlight the required reference string. Capturing coverage via `python -m co
verage report` let the guard parse consistent totals while keeping transient files out of the repo. Documenting the CI pipeline e
arly should make future guard additions easier because contributors now have a predictable checklist. Next time I will wire in a
linting guard sooner so the baseline captures formatting expectations before feature work lands.
