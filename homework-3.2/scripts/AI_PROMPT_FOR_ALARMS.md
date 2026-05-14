# Prompt for ChatGPT / AI tools (Homework 3.2 — item 1)

Use a variant of the following to generate **alarm** CSV data. The committed `data/alarms.csv` in this repo was produced with the **Python script** `scripts/generate_alarms_csv.py` (reproducible seed). You may replace the file by pasting AI output if your instructor prefers strictly “ChatGPT-generated” rows.

---

**Prompt template:**

> Generate a CSV file named `alarms.csv` with **at least 1,500 rows** and a header row.  
> Columns (exact names, numeric except `id`):
> - `id` — integer 1..N  
> - `duration_sec` — how long the alarm condition lasted (seconds), range roughly 1–300  
> - `peak_amplitude` — normalized signal strength 0.0–1.0  
> - `repetition_count` — how many times the same alarm repeated in a window, integer 0–50  
> - `hour_of_day` — hour 0–23 when the alarm fired  
> - `is_false_alarm` — **0** = real incident, **1** = false alarm (nuisance / noise)  
>
> Rules for realism:
> - False alarms (`is_false_alarm=1`) should tend to have **lower** `peak_amplitude`, **shorter** `duration_sec`, and **higher** `repetition_count` than true alarms, but **allow overlap** so a machine-learning model is non-trivial.  
> - Include **10–20%** false alarms.  
> - Do not include commas inside numeric fields; use plain CSV.  
> - Output **only** the CSV text, no markdown code fences.

---

After generation, save as `homework-3.2/data/alarms.csv` and run `python train.py` from the `homework-3.2` directory.
