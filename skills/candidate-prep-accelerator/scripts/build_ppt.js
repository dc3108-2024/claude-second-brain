#!/usr/bin/env node
/**
 * build_ppt.js — Generates domain briefing PPT from structured content JSON.
 * Usage: node build_ppt.js --content /tmp/prep_ppt_content.json [--output ~/Desktop/output.pptx]
 */
const PptxGenJS = require("pptxgenjs");
const fs = require("fs");
const os = require("os");
const path = require("path");

// ── Args ──────────────────────────────────────────────────────────────────────
const argv = {};
process.argv.slice(2).forEach((v, i, a) => {
  if (v.startsWith("--")) argv[v.slice(2)] = a[i + 1];
});
if (!argv.content) { console.error("--content required"); process.exit(1); }

const contentPath = argv.content.replace(/^~/, os.homedir());
const content = JSON.parse(fs.readFileSync(contentPath, "utf8"));
const meta = content.meta || {};
const W = 10, H = 5.625;

// ── Colors (brand from JSON with safe fallbacks) ───────────────────────────
const C = {
  primary: meta.brand_primary || "1A3A6B",
  dark:    meta.brand_dark    || "0D2247",
  accent:  meta.brand_accent  || "1A2B4A",
  white:   "FFFFFF",
  light:   "F7F8FA",
  slate:   "3A4F6A",
  muted:   "6B7FA3",
};

// ── PptxGenJS setup ───────────────────────────────────────────────────────
const pres = new PptxGenJS();
pres.defineLayout({ name: "CUSTOM_16x9", width: W, height: H });
pres.layout = "CUSTOM_16x9";
pres.author = "Candidate Prep Accelerator";
pres.subject = `${meta.company || "Client"} — ${meta.role || "Role"} Domain Primer`;

const mkShadow = () => ({ type: "outer", blur: 5, offset: 2, angle: 135, color: "000000", opacity: 0.09 });

// ── Header bar helper ─────────────────────────────────────────────────────
function header(sl, text) {
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: 0.85,
    fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.22, h: 0.85,
    fill: { color: C.primary }, line: { color: C.primary, width: 0 },
  });
  sl.addText(text, {
    x: 0.42, y: 0, w: 9.3, h: 0.85,
    fontSize: 20, bold: true, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0,
  });
}

// ── Section break slide (returns sl for addNotes chaining) ────────────────
function sectionSlide(num, title, subtitle) {
  const sl = pres.addSlide();
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: H, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
  });
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.35, h: H, fill: { color: C.dark }, line: { color: C.dark, width: 0 },
  });
  sl.addText(`0${num}`, {
    x: 0.5, y: 1.4, w: 1.2, h: 1.0, fontSize: 52, bold: true,
    color: C.white, fontFace: "Calibri", opacity: 0.35,
  });
  sl.addText(title, {
    x: 0.5, y: 2.1, w: 9.1, h: 1.0, fontSize: 36, bold: true,
    color: C.white, fontFace: "Calibri", valign: "middle",
  });
  if (subtitle) {
    sl.addText(subtitle, {
      x: 0.5, y: 3.0, w: 8.0, h: 0.6, fontSize: 16,
      color: C.white, fontFace: "Calibri", opacity: 0.8,
    });
  }
  return sl;
}

// ── Mental model slide (2–4 pillars) ─────────────────────────────────────
function mentalModelSlide(domainName, modelTitle, pillars) {
  const sl = pres.addSlide();
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: H, fill: { color: C.light }, line: { color: C.light, width: 0 },
  });
  header(sl, `${domainName} — Mental Model`);

  // Subtitle
  sl.addText(modelTitle || `The ${domainName} Framework`, {
    x: 0.42, y: 0.95, w: 9.2, h: 0.35, fontSize: 11,
    italic: true, color: C.muted, fontFace: "Calibri",
  });

  const n = Math.min(pillars.length, 4);
  const GAP = 0.18;
  const TOTAL_W = 9.2;
  const BOX_W = (TOTAL_W - (n - 1) * GAP) / n;
  const BOX_Y = 1.35, HDR_H = 0.5, BOX_H = 3.9;
  const X0 = 0.4;

  const pillarColors = [C.primary, C.accent, C.dark, C.muted];

  for (let i = 0; i < n; i++) {
    const p = pillars[i];
    const x = X0 + i * (BOX_W + GAP);

    // Pillar header
    sl.addShape(pres.shapes.RECTANGLE, {
      x, y: BOX_Y, w: BOX_W, h: HDR_H,
      fill: { color: pillarColors[i % pillarColors.length] },
      line: { color: pillarColors[i % pillarColors.length], width: 0 },
    });
    sl.addText(p.title, {
      x: x + 0.05, y: BOX_Y, w: BOX_W - 0.1, h: HDR_H,
      fontSize: 10.5, bold: true, color: C.white, fontFace: "Calibri",
      valign: "middle", align: "center",
    });

    // Pillar body
    sl.addShape(pres.shapes.RECTANGLE, {
      x, y: BOX_Y + HDR_H, w: BOX_W, h: BOX_H - HDR_H,
      fill: { color: C.white }, line: { color: "D8DDED", width: 1 },
      shadow: mkShadow(),
    });

    const bullets = (p.bullets || []).slice(0, 6);
    const items = bullets.map((b, j) => ({
      text: b,
      options: { bullet: true, breakLine: j < bullets.length - 1 },
    }));
    sl.addText(items, {
      x: x + 0.1, y: BOX_Y + HDR_H + 0.1,
      w: BOX_W - 0.2, h: BOX_H - HDR_H - 0.2,
      fontSize: 9, color: C.slate, fontFace: "Calibri", valign: "top",
      lineSpacingMultiple: 1.25,
    });
  }
  return sl;
}

// ── Process lifecycle slide ────────────────────────────────────────────────
function processSlide(domainName, flowTitle, steps, footerNote) {
  const sl = pres.addSlide();
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: H, fill: { color: C.white }, line: { color: C.white, width: 0 },
  });
  header(sl, `${domainName} — Process Lifecycle`);

  sl.addText(flowTitle || `${domainName} End-to-End Flow`, {
    x: 0.42, y: 0.95, w: 9.2, h: 0.3, fontSize: 10,
    italic: true, color: C.muted, fontFace: "Calibri",
  });

  const n = Math.min(steps.length, 6);
  const GAP = n <= 4 ? 0.28 : n === 5 ? 0.22 : 0.18;
  const BOX_W = (9.1 - (n - 1) * GAP) / n;
  const X0 = 0.42, BOX_Y = 1.35, BOX_H = 3.2;
  const TRACK_Y = BOX_Y + 0.48, TRACK_H = 0.18;

  // Connector track
  sl.addShape(pres.shapes.RECTANGLE, {
    x: X0 + BOX_W, y: TRACK_Y, w: (n - 1) * (BOX_W + GAP), h: TRACK_H,
    fill: { color: C.primary }, line: { color: C.primary, width: 0 }, opacity: 0.35,
  });

  for (let i = 0; i < n; i++) {
    const step = steps[i];
    const x = X0 + i * (BOX_W + GAP);
    const hdrColor = i === 0 ? C.primary : i === n - 1 ? C.dark : C.accent;

    // Numbered header pill
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y: BOX_Y, w: BOX_W, h: 0.5,
      fill: { color: hdrColor }, line: { color: hdrColor, width: 0 },
      rectRadius: 0.05,
    });
    sl.addText(`${i + 1}. ${step.label}`, {
      x: x + 0.05, y: BOX_Y, w: BOX_W - 0.1, h: 0.5,
      fontSize: 9, bold: true, color: C.white, fontFace: "Calibri",
      valign: "middle", align: "center",
    });

    // Step body card
    sl.addShape(pres.shapes.RECTANGLE, {
      x, y: BOX_Y + 0.5, w: BOX_W, h: BOX_H - 0.5,
      fill: { color: C.light }, line: { color: "D8DDED", width: 1 },
      shadow: mkShadow(),
    });
    sl.addText(step.description || "", {
      x: x + 0.08, y: BOX_Y + 0.6, w: BOX_W - 0.16, h: BOX_H - 1.2,
      fontSize: 8.5, color: C.slate, fontFace: "Calibri", valign: "top",
      lineSpacingMultiple: 1.2, wrap: true,
    });

    // System tag pill (bottom of card)
    if (step.system) {
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: x + 0.08, y: BOX_Y + BOX_H - 0.55, w: BOX_W - 0.16, h: 0.3,
        fill: { color: "E8EBF5" }, line: { color: "C8CCE0", width: 1 },
        rectRadius: 0.04,
      });
      sl.addText(step.system, {
        x: x + 0.08, y: BOX_Y + BOX_H - 0.55, w: BOX_W - 0.16, h: 0.3,
        fontSize: 7.5, bold: true, color: C.accent, fontFace: "Calibri",
        valign: "middle", align: "center",
      });
    }
  }

  if (footerNote) {
    sl.addText(footerNote, {
      x: 0.42, y: 4.75, w: 9.2, h: 0.35,
      fontSize: 8, italic: true, color: C.muted, fontFace: "Calibri",
    });
  }
  return sl;
}

// ── SLIDE 1: Title ────────────────────────────────────────────────────────
const title = pres.addSlide();
title.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: W, h: H, fill: { color: C.dark }, line: { color: C.dark, width: 0 },
});
title.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 0.5, h: H, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
});
title.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 2.85, w: 9.1, h: 0.06,
  fill: { color: C.primary }, line: { color: C.primary, width: 0 }, opacity: 0.5,
});
title.addText(meta.company || "Client", {
  x: 0.7, y: 1.0, w: 8.8, h: 0.65, fontSize: 16, color: C.white,
  fontFace: "Calibri", opacity: 0.7,
});
title.addText(`Domain Primer — ${meta.role || "Role"}`, {
  x: 0.7, y: 1.55, w: 8.8, h: 1.1, fontSize: 34, bold: true,
  color: C.white, fontFace: "Calibri",
});
title.addText("Professional Services Practice", {
  x: 0.7, y: 3.0, w: 8.8, h: 0.5, fontSize: 13,
  color: C.white, fontFace: "Calibri", opacity: 0.8,
});
title.addText(`Candidate Prep Accelerator  |  ${new Date().toLocaleDateString(undefined, { month: "long", year: "numeric" })}`, {
  x: 0.7, y: 3.5, w: 8.8, h: 0.4, fontSize: 10,
  color: C.white, fontFace: "Calibri", opacity: 0.55,
});
title.addNotes(`DOMAIN PRIMER\nCompany: ${meta.company || "—"} | Role: ${meta.role || "—"}\nGenerated by Candidate Prep Accelerator — [Your Organisation]\n\nUSAGE\nThis deck provides enterprise context and business domain fluency for candidates preparing for client interviews or internal briefings. Use it to understand how the business works before discussing technology.`);

// ── SLIDE 2: Company Overview ──────────────────────────────────────────────
const co = content.company_overview || {};
const ovSl = pres.addSlide();
ovSl.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: W, h: H, fill: { color: C.light }, line: { color: C.light, width: 0 },
});
header(ovSl, `${meta.company || "Company"} — Enterprise Overview`);

// Tagline
if (co.tagline) {
  ovSl.addText(`"${co.tagline}"`, {
    x: 0.42, y: 0.95, w: 6.0, h: 0.45, fontSize: 11.5,
    italic: true, bold: true, color: C.primary, fontFace: "Calibri",
  });
}

// Stat boxes (up to 4)
const stats = (co.stats || []).slice(0, 4);
const SB_W = 2.05, SB_H = 0.85, SB_Y = 1.5, SB_X0 = 5.9;
stats.forEach((s, i) => {
  const x = SB_X0 + i % 2 * (SB_W + 0.1);
  const y = SB_Y + Math.floor(i / 2) * (SB_H + 0.1);
  ovSl.addShape(pres.shapes.RECTANGLE, {
    x, y, w: SB_W, h: SB_H,
    fill: { color: i % 2 === 0 ? C.primary : C.accent },
    line: { color: i % 2 === 0 ? C.primary : C.accent, width: 0 },
    shadow: mkShadow(),
  });
  ovSl.addText(s.value || "", {
    x: x + 0.08, y: y + 0.04, w: SB_W - 0.16, h: 0.42,
    fontSize: 18, bold: true, color: C.white, fontFace: "Calibri", valign: "bottom", align: "center",
  });
  ovSl.addText(s.label || "", {
    x: x + 0.08, y: y + 0.46, w: SB_W - 0.16, h: 0.3,
    fontSize: 8.5, color: C.white, fontFace: "Calibri", valign: "top", align: "center", opacity: 0.85,
  });
});

// Description
if (co.tech_strategy) {
  ovSl.addText("Technology Strategy", {
    x: 0.42, y: 1.5, w: 5.3, h: 0.3, fontSize: 10, bold: true, color: C.accent, fontFace: "Calibri",
  });
  ovSl.addText(co.tech_strategy, {
    x: 0.42, y: 1.8, w: 5.3, h: 1.0, fontSize: 9.5, color: C.slate,
    fontFace: "Calibri", lineSpacingMultiple: 1.25, wrap: true,
  });
}

// Key segments
const segs = co.key_segments || [];
if (segs.length) {
  ovSl.addText("Key Business Segments", {
    x: 0.42, y: 3.0, w: 9.0, h: 0.28, fontSize: 9.5, bold: true, color: C.accent, fontFace: "Calibri",
  });
  const SEG_H = 0.32;
  segs.slice(0, 5).forEach((seg, i) => {
    const x = 0.42 + (i % 3) * 3.0;
    const y = 3.3 + Math.floor(i / 3) * (SEG_H + 0.08);
    ovSl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y, w: 2.8, h: SEG_H,
      fill: { color: "E8EBF5" }, line: { color: C.primary, width: 1 },
      rectRadius: 0.04,
    });
    ovSl.addText(seg, {
      x: x + 0.05, y, w: 2.7, h: SEG_H,
      fontSize: 9, color: C.accent, fontFace: "Calibri", valign: "middle", align: "center", bold: true,
    });
  });
}

ovSl.addNotes(`COMPANY OVERVIEW NOTES\nUse this slide to establish commercial credibility before diving into domain specifics.\n\nKey talking points:\n- Understand the organisational structure before discussing systems\n- Know which business lines this role serves\n- Tech strategy signals where investment is going — align your skills accordingly`);

// ── Domain slides ─────────────────────────────────────────────────────────
const domains = content.domains || [];
domains.forEach((domain, idx) => {
  // Section slide
  const sec = sectionSlide(idx + 1, domain.name, domain.subtitle || "");
  sec.addNotes(`SECTION: ${domain.name.toUpperCase()}\n${domain.subtitle || ""}\n\nThis section covers the business context, mental models, and process lifecycle for ${domain.name}.`);

  // Mental model slide
  if (domain.mental_model) {
    const mm = domain.mental_model;
    const mmSl = mentalModelSlide(domain.name, mm.title, mm.pillars || []);
    mmSl.addNotes(`MENTAL MODEL: ${domain.name}\n${mm.title || ""}\n\nPILLARS:\n${(mm.pillars || []).map(p => `${p.title}: ${(p.bullets || []).join("; ")}`).join("\n")}`);
  }

  // Process flow slide
  if (domain.process_flow) {
    const pf = domain.process_flow;
    const pfSl = processSlide(domain.name, pf.title, pf.steps || [], pf.footer || "");
    pfSl.addNotes(`PROCESS FLOW: ${domain.name}\n${pf.title || ""}\n\nSTEPS:\n${(pf.steps || []).map((s, i) => `${i + 1}. ${s.label}: ${s.description} [${s.system || "—"}]`).join("\n")}`);
  }
});

// ── Tech Themes slide ─────────────────────────────────────────────────────
const themes = content.tech_themes || [];
if (themes.length) {
  const thSl = pres.addSlide();
  thSl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: H, fill: { color: C.light }, line: { color: C.light, width: 0 },
  });
  header(thSl, "Cross-Cutting Technology Themes");

  const COLS = 2, COL_W = 4.45, COL_GAP = 0.1, ROW_H = 0.75, ROW_GAP = 0.1;
  themes.slice(0, 6).forEach((t, i) => {
    const col = i % COLS, row = Math.floor(i / COLS);
    const x = 0.42 + col * (COL_W + COL_GAP);
    const y = 0.97 + row * (ROW_H + ROW_GAP);
    thSl.addShape(pres.shapes.RECTANGLE, {
      x, y, w: COL_W, h: ROW_H,
      fill: { color: C.white }, line: { color: "D0D5E8", width: 1 },
      shadow: mkShadow(),
    });
    thSl.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.18, h: ROW_H,
      fill: { color: i % 2 === 0 ? C.primary : C.accent },
      line: { color: i % 2 === 0 ? C.primary : C.accent, width: 0 },
    });
    thSl.addText(t.theme || "", {
      x: x + 0.26, y: y + 0.04, w: COL_W - 0.32, h: 0.26,
      fontSize: 10, bold: true, color: C.accent, fontFace: "Calibri",
    });
    thSl.addText(t.relevance || "", {
      x: x + 0.26, y: y + 0.3, w: COL_W - 0.32, h: 0.36,
      fontSize: 8.5, color: C.slate, fontFace: "Calibri", wrap: true,
    });
  });
  thSl.addNotes(`TECHNOLOGY THEMES\nThese cross-cutting themes apply across all domains covered in this primer.\n\nUse these as conversation bridges — they show systemic thinking, not siloed knowledge.`);
}

// ── Competency Profile slide ───────────────────────────────────────────────
const cp = content.competency_profile || {};
if (cp.quadrants && cp.quadrants.length) {
  const cpSl = pres.addSlide();
  cpSl.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: H, fill: { color: C.light }, line: { color: C.light, width: 0 },
  });
  header(cpSl, cp.title || "What Good Looks Like — Candidate Profile");

  const quads = cp.quadrants.slice(0, 4);
  const QW = 4.55, QH = 2.0, QX0 = 0.42, QY0 = 0.97, QGAP = 0.1;
  const quadColors = [C.primary, C.accent, C.dark, C.muted];

  quads.forEach((q, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = QX0 + col * (QW + QGAP);
    const y = QY0 + row * (QH + QGAP);
    cpSl.addShape(pres.shapes.RECTANGLE, {
      x, y, w: QW, h: QH,
      fill: { color: C.white }, line: { color: "D0D5E8", width: 1 },
      shadow: mkShadow(),
    });
    cpSl.addShape(pres.shapes.RECTANGLE, {
      x, y, w: QW, h: 0.38,
      fill: { color: quadColors[i % quadColors.length] },
      line: { color: quadColors[i % quadColors.length], width: 0 },
    });
    cpSl.addText(q.title || "", {
      x: x + 0.1, y: y, w: QW - 0.2, h: 0.38,
      fontSize: 10, bold: true, color: C.white, fontFace: "Calibri", valign: "middle",
    });
    const bullets = (q.bullets || []).slice(0, 5);
    const items = bullets.map((b, j) => ({
      text: b,
      options: { bullet: true, breakLine: j < bullets.length - 1 },
    }));
    cpSl.addText(items, {
      x: x + 0.1, y: y + 0.42, w: QW - 0.2, h: QH - 0.52,
      fontSize: 9, color: C.slate, fontFace: "Calibri", valign: "top",
      lineSpacingMultiple: 1.2,
    });
  });
  cpSl.addNotes(`CANDIDATE PROFILE\nUse this as a self-assessment checklist before the interview.\n\nFor each quadrant, prepare a concrete example (STAR format) that demonstrates the competency.\n\nThis is the examiner's lens — structure your answers to hit these dimensions.`);
}

// ── Save ──────────────────────────────────────────────────────────────────
const company = (meta.company || "Client").split(/\s+/).slice(0, 2).join("_").replace(/[^\w_]/g, "");
const role = (meta.role || "Role").split(/[\s/,]+/).slice(0, 2).join("_").replace(/[^\w_]/g, "");
const defaultOut = path.join(os.homedir(), "Desktop", `${company}_${role}_Domain_Primer.pptx`);
const outPath = (argv.output || defaultOut).replace(/^~/, os.homedir());

pres.writeFile({ fileName: outPath })
  .then(() => console.log(`✅ PPT saved: ${outPath}`))
  .catch(err => { console.error("❌ PPT save failed:", err.message); process.exit(1); });
