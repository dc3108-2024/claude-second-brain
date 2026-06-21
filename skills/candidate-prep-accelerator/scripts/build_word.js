#!/usr/bin/env node
/**
 * build_word.js — Generates tech primer Word doc from structured content JSON.
 * Usage: node build_word.js --content /tmp/prep_word_content.json [--output ~/Desktop/output.docx]
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, LevelFormat, PageNumber, PageBreak, TableOfContents,
} = require("docx");
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

const brandHex = meta.brand_primary || "1A3A6B";
const company  = meta.company || "Client";
const role     = meta.role    || "Role";
const domain   = meta.domain  || "";
const depth    = meta.depth   || "101";

// ── Style helpers ──────────────────────────────────────────────────────────
const FONT = "Calibri";
const CONTENT_W_DXA = 8928; // A4 with 1" margins (11906 - 2 * 1440)
const borderCell = {
  top:    { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
  bottom: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
  left:   { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
  right:  { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
};

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: FONT, size: 32, bold: true, color: brandHex })],
    spacing: { before: 320, after: 160 },
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, font: FONT, size: 26, bold: true, color: "444444" })],
    spacing: { before: 240, after: 120 },
  });
}

function body(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: FONT, size: 22 })],
    spacing: { after: 100 },
  });
}

function spacer() {
  return new Paragraph({ children: [new TextRun("")], spacing: { after: 80 } });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function bulletPara(text, ref = "bullets") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    children: [new TextRun({ text, font: FONT, size: 21 })],
    spacing: { after: 60 },
  });
}

function tableRow(cells, isHeader = false) {
  return new TableRow({
    children: cells.map(({ text, w }) =>
      new TableCell({
        borders: borderCell,
        width: { size: w, type: WidthType.DXA },
        shading: isHeader ? { fill: brandHex, type: ShadingType.CLEAR } : { fill: "FFFFFF", type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({
            text,
            font: FONT,
            size: isHeader ? 20 : 19,
            bold: isHeader,
            color: isHeader ? "FFFFFF" : "333333",
          })],
        })],
      })
    ),
  });
}

// ── Build sections ────────────────────────────────────────────────────────
const children = [];

// Cover page
children.push(
  new Paragraph({ spacing: { before: 2880 } }),
  new Paragraph({
    children: [new TextRun({ text: company, font: FONT, size: 48, bold: true, color: brandHex })],
    alignment: AlignmentType.CENTER,
  }),
  new Paragraph({
    children: [new TextRun({ text: role, font: FONT, size: 36, color: "333333" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
  }),
  new Paragraph({
    children: [new TextRun({ text: domain ? `Domain: ${domain}` : "", font: FONT, size: 24, italics: true, color: "666666" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 480 },
  }),
  new Paragraph({
    children: [new TextRun({ text: `Technology Primer (${depth === "102" ? "Technical" : "Business"} Level)`, font: FONT, size: 22, italics: true, color: "888888" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
  }),
  new Paragraph({
    children: [new TextRun({ text: `Professional Services Practice`, font: FONT, size: 22, color: "888888" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
  }),
  new Paragraph({
    children: [new TextRun({ text: `Generated: ${new Date().toLocaleDateString("en-AU", { month: "long", year: "numeric" })}`, font: FONT, size: 20, color: "AAAAAA" })],
    alignment: AlignmentType.CENTER,
  }),
  pageBreak()
);

// Table of Contents
children.push(
  h1("Table of Contents"),
  new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }),
  pageBreak()
);

// 1. Role in Context
const rc = content.role_context || {};
children.push(h1("1. Role in Context"), spacer());
if (rc.overview) children.push(body(rc.overview), spacer());
if (rc.reporting_structure) {
  children.push(h2("Reporting Structure"), body(rc.reporting_structure), spacer());
}
if ((rc.success_looks_like || []).length) {
  children.push(h2("What Success Looks Like"));
  rc.success_looks_like.forEach(s => children.push(bulletPara(s)));
  children.push(spacer());
}
children.push(pageBreak());

// 2. Domain Primer
const dp = content.domain_primer || {};
children.push(h1("2. Business Domain Primer"), spacer());
if (dp.overview) children.push(body(dp.overview), spacer());
(dp.sub_domains || []).forEach(sd => {
  children.push(h2(sd.name));
  if (sd.summary) children.push(body(sd.summary), spacer());
  if ((sd.key_concepts || []).length) {
    children.push(new Paragraph({
      children: [new TextRun({ text: "Key Concepts: ", font: FONT, size: 21, bold: true })],
    }));
    sd.key_concepts.forEach(kc => children.push(bulletPara(kc)));
    children.push(spacer());
  }
});
children.push(pageBreak());

// 3. Systems Landscape
const systems = content.systems_landscape || [];
children.push(h1("3. Key Systems & Technology Platforms"), spacer());
if (systems.length) {
  const COLS = [3000, 2400, 3528];
  children.push(new Table({
    width: { size: CONTENT_W_DXA, type: WidthType.DXA },
    columnWidths: COLS,
    rows: [
      tableRow([{ text: "System / Platform", w: COLS[0] }, { text: "Vendor", w: COLS[1] }, { text: "Purpose", w: COLS[2] }], true),
      ...systems.map(s => tableRow([
        { text: s.system || "", w: COLS[0] },
        { text: s.vendor || "", w: COLS[1] },
        { text: `${s.purpose || ""}${s.category ? ` [${s.category}]` : ""}`, w: COLS[2] },
      ])),
    ],
  }));
  children.push(spacer());
}
children.push(pageBreak());

// 4. Process Flows
const flows = content.process_flows || [];
children.push(h1("4. Business Process Flows"), spacer());
flows.forEach(flow => {
  children.push(h2(flow.name));
  (flow.steps || []).forEach((step, i) =>
    children.push(bulletPara(`Step ${i + 1}: ${step}`, "numbers"))
  );
  children.push(spacer());
});
children.push(pageBreak());

// 5. Terminology Glossary
const glossary = (content.glossary || []).slice().sort((a, b) =>
  (a.term || "").localeCompare(b.term || "")
);
children.push(h1("5. Terminology Glossary"), spacer());
if (glossary.length) {
  const GCOLS = [2400, 5528, 1000];
  children.push(new Table({
    width: { size: CONTENT_W_DXA, type: WidthType.DXA },
    columnWidths: GCOLS,
    rows: [
      tableRow([{ text: "Term", w: GCOLS[0] }, { text: "Definition", w: GCOLS[1] }, { text: "Domain", w: GCOLS[2] }], true),
      ...glossary.map(g => tableRow([
        { text: g.term || "", w: GCOLS[0] },
        { text: g.definition || "", w: GCOLS[1] },
        { text: g.context || "", w: GCOLS[2] },
      ])),
    ],
  }));
  children.push(spacer());
}
children.push(pageBreak());

// 6. Regulatory Context
const regs = content.regulatory_context || [];
if (regs.length) {
  children.push(h1("6. Regulatory & Standards Context"), spacer());
  const RCOLS = [3000, 5928];
  children.push(new Table({
    width: { size: CONTENT_W_DXA, type: WidthType.DXA },
    columnWidths: RCOLS,
    rows: [
      tableRow([{ text: "Regulation / Standard", w: RCOLS[0] }, { text: "Relevance to Role", w: RCOLS[1] }], true),
      ...regs.map(r => tableRow([
        { text: r.regulation || "", w: RCOLS[0] },
        { text: r.relevance || "", w: RCOLS[1] },
      ])),
    ],
  }));
  children.push(spacer(), pageBreak());
}

// 7. Interview Preparation
const ip = content.interview_prep || {};
children.push(h1("7. Interview Preparation"), spacer());
if ((ip.likely_questions || []).length) {
  children.push(h2("Likely Questions"));
  ip.likely_questions.forEach(q => children.push(bulletPara(q)));
  children.push(spacer());
}
if ((ip.talking_points || []).length) {
  children.push(h2("Key Talking Points"));
  ip.talking_points.forEach(t => children.push(bulletPara(t)));
  children.push(spacer());
}
if ((ip.questions_to_ask || []).length) {
  children.push(h2("Questions to Ask Them"));
  ip.questions_to_ask.forEach(q => children.push(bulletPara(q)));
  children.push(spacer());
}

// ── Document ───────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT, color: brandHex },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONT, color: "444444" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [
            new TextRun({ text: `${company} — ${role} | `, font: FONT, size: 18, color: "888888" }),
            new TextRun({ text: "[Your Organisation]", font: FONT, size: 18, color: "888888", bold: true }),
          ],
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: brandHex, space: 1 } },
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [
            new TextRun({ text: "Page ", font: FONT, size: 18, color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "888888" }),
            new TextRun({ text: " | Candidate Prep Accelerator | Confidential", font: FONT, size: 18, color: "BBBBBB" }),
          ],
          alignment: AlignmentType.CENTER,
        })],
      }),
    },
    children,
  }],
});

// ── Save ───────────────────────────────────────────────────────────────────
const co2 = company.split(/\s+/).slice(0, 2).join("_").replace(/[^\w_]/g, "");
const rl = role.split(/[\s/,]+/).slice(0, 2).join("_").replace(/[^\w_]/g, "");
const defaultOut = path.join(os.homedir(), "Desktop", `${co2}_${rl}_Tech_Primer.docx`);
const outPath = (argv.output || defaultOut).replace(/^~/, os.homedir());

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log(`✅ Word doc saved: ${outPath}`);
}).catch(err => { console.error("❌ Word save failed:", err.message); process.exit(1); });
