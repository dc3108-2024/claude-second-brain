---
name: process-diagram
description: >
  Turn any process description, document, or system into a clean draw.io flow diagram.
  Use when the user says "diagram this", "sketch the flow for", "make a flowchart",
  "visualise this workflow", or drops a document and wants the process visualised.
  Works on any input: inline description, markdown file, PDF, or verbal explanation.
---

# Process Diagram Skill

Turn any described process into a clean, schematic draw.io diagram — saved and ready
to edit in the draw.io desktop app.

---

## Step 1 — Read the input

Accept any of:
- Inline description in the user's message
- A file path (read with the Read tool)
- A URL (fetch with WebFetch)

Extract the full text of what the process does before reasoning about structure.

---

## Step 2 — Reason about structure

Before writing any XML, answer these questions:

**Stages** — What are the 4–8 discrete phases? Name each in 1–2 words.
Too many stages = cluttered. Collapse adjacent minor steps into one.

**Node type per stage:**
| Shape | Use for |
|---|---|
| Rectangle | Standard process step |
| Diamond | Decision / branch point |
| Rounded rect | Start / end |
| Cylinder | Data store / database |
| Parallelogram | Input / output |

**Connections:**
- Main flow: solid arrows, left → right
- Branches: both paths connect, label the condition
- Feedback loop: dashed arc routed below the diagram, labeled with what flows back

**Does the process have a loop?** What triggers re-entry?

---

## Step 3 — Plan the layout

- Horizontal pipeline, ~1200 × 600 canvas
- Main pipeline y-centre = 230
- Space nodes evenly across the x-axis
- Max 8 main pipeline nodes

---

## Step 4 — Write the draw.io XML

Standard file skeleton:

```xml
<mxfile>
  <diagram name="Process Flow">
    <mxGraphModel width="1200" height="600" dx="0" dy="0" grid="0" tooltips="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- nodes and edges here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Node template:
```xml
<mxCell id="n1" value="Stage Name" style="rounded=1;whiteSpace=wrap;fillColor=#f9f9f9;strokeColor=#666666;" vertex="1" parent="1">
  <mxGeometry x="40" y="195" width="120" height="70" as="geometry"/>
</mxCell>
```

Edge template:
```xml
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;strokeColor=#999999;" edge="1" source="n1" target="n2" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

---

## Step 5 — Save and open

- Input was a file → save as `[filename]_flow.drawio` alongside the source
- Input was inline → save to `~/Desktop/[ProcessName]_flow.drawio`

```bash
open -a "draw.io" "[output-path]"
```

---

## Visual rules — do not break

1. Max 8 main pipeline nodes — merge minor steps
2. No colour fills — all nodes use `fillColor=#f9f9f9`
3. No emoji in node labels
4. Stage names are 1–2 words — verbs or nouns, not sentences
5. One feedback arc maximum
6. The diagram must be readable at a glance before the details are read
