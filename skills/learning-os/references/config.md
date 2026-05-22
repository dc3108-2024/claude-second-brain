# Learning OS — Configuration

Edit these values before first use. This file is read by the learning-os skill.

---

## Knowledge base

```
kb_folder:     ~/LearningOS/kb/        # where your KB markdown files live
review_folder: ~/LearningOS/reviews/   # where weekly review files are saved
quiz_state:    ~/LearningOS/quiz-state.md  # tracks recall intervals per concept
lattice_file:  ~/LearningOS/kb/_lattice.md # cross-domain connection log
```

## Your domains

Define your learning domains here. Each becomes a separate KB file.
Start broad — you can split later.

| Domain | File | What belongs here |
|---|---|---|
| Technology | technology.md | Software, AI, systems, tools |
| Finance | finance.md | Investing, economics, personal finance |
| Psychology | psychology.md | Mental models, behaviour, decision-making |
| Philosophy | philosophy.md | Ethics, epistemology, worldview |
| [Your domain] | [file.md] | [description] |

## Curriculum tracks (optional)

If you're learning toward a specific goal, define tracks here.
Concepts can be tagged to a track for progress reporting.

| Track | Goal | Target date |
|---|---|---|
| [e.g. Machine Learning] | [e.g. Build production ML pipeline] | [YYYY-MM-DD] |
| [Add your own] | | |

## Recall settings

```
default_new_interval:     1     # days until first recall after capture
correct_multiplier:       2.0   # multiply interval on correct recall
incorrect_reset:          1     # reset to this interval on missed recall
max_interval_days:        90    # cap the interval here
```

---

## Notes

- Keep domains broad enough that concepts have company — isolated domains get neglected
- The lattice file grows automatically — don't edit it manually
- Quiz state is maintained by the skill — don't delete it between sessions
