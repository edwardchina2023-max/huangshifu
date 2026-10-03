#!/usr/bin/env node
/**
 * md2docx.js — 把实验室雷达早报 / 诺奖资料包的 Markdown 转成 Word（.docx）
 *
 * 用法：node scripts/md2docx.js <输入.md> [输出.docx]
 *   未给输出路径时，写到 assets/files/word/<同名>.docx
 *
 * 支持的 Markdown 子集（覆盖本仓库日报格式）：
 *   # / ## / ### 标题、> 引用、| 表格 |、- 无序列表、1. 有序列表、
 *   --- 分隔线、**粗体**、*斜体*、`代码`、[文字](链接)
 * 依赖：docx（npm，全局预装；缺失时 npm install -g docx）
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ExternalHyperlink, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, AlignmentType, Footer, PageNumber,
} = require("docx");

const FONT = "Microsoft YaHei";
const ACCENT = "0F3460";
const PAGE_W = 11906, MARGIN = 1134;            // A4，左右边距 2cm
const CONTENT_W = PAGE_W - MARGIN * 2;

// ---------- 行内格式：**粗体** *斜体* `代码` [文字](链接) ----------
function inline(text, base = {}) {
  const out = [];
  const re = /(\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)\s]+)\)|`([^`]+)`|\*([^*]+)\*)/g;
  let last = 0, m;
  const push = (t, extra = {}) => t && out.push(new TextRun({ text: t, font: FONT, ...base, ...extra }));
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index));
    if (m[2] !== undefined) {
      // 粗体内部可能嵌套链接，递归处理
      out.push(...inline(m[2], { ...base, bold: true }));
    } else if (m[3] !== undefined) {
      out.push(new ExternalHyperlink({
        link: m[4],
        children: [new TextRun({ text: m[3], font: FONT, ...base, style: "Hyperlink", color: "1F5FBF", underline: {} })],
      }));
    } else if (m[5] !== undefined) {
      push(m[5], { font: "Consolas", color: "7A2E0E" });
    } else if (m[6] !== undefined) {
      // 斜体内部也可能嵌套链接，递归处理
      out.push(...inline(m[6], { ...base, italics: true }));
    }
    last = re.lastIndex;
  }
  push(text.slice(last));
  return out;
}

// ---------- 表格 ----------
function buildTable(lines) {
  const rows = lines
    .filter((l) => !/^\|\s*:?-{2,}/.test(l))           // 去掉 |---|---| 分隔行
    .map((l) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
  const cols = Math.max(...rows.map((r) => r.length));
  // 按各列文字长度分配列宽（每列最少 8%）
  const lens = Array.from({ length: cols }, (_, i) =>
    Math.max(...rows.map((r) => (r[i] || "").replace(/\]\([^)]*\)/g, "]").length), 2));
  const total = lens.reduce((a, b) => a + b, 0);
  let widths = lens.map((n) => Math.max(Math.round((n / total) * CONTENT_W), Math.round(CONTENT_W * 0.08)));
  const scale = CONTENT_W / widths.reduce((a, b) => a + b, 0);
  widths = widths.map((w) => Math.floor(w * scale));
  widths[cols - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);

  const border = { style: BorderStyle.SINGLE, size: 4, color: "C9D1DE" };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: widths,
    borders: { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border },
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: ri === 0,
      children: Array.from({ length: cols }, (_, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA },
        shading: ri === 0 ? { type: ShadingType.CLEAR, fill: ACCENT, color: "auto" } : undefined,
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({
          spacing: { after: 0, line: 300 },
          children: inline(r[ci] || "", ri === 0 ? { bold: true, color: "FFFFFF", size: 19 } : { size: 19 }),
        })],
      })),
    })),
  });
}

// ---------- 主转换 ----------
function convert(md) {
  const lines = md.replace(/\r/g, "").split("\n");
  const blocks = [];
  let title = "实验室雷达";
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const t = line.trim();
    if (!t) continue;

    if (t.startsWith("|")) {                             // 表格
      const tbl = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) tbl.push(lines[i++].trim());
      i--;
      blocks.push(buildTable(tbl));
      blocks.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      continue;
    }
    if (/^-{3,}$/.test(t)) {                              // 分隔线：段落下边框
      blocks.push(new Paragraph({
        spacing: { before: 120, after: 120 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "D7DCE5", space: 1 } },
        children: [],
      }));
      continue;
    }
    let m;
    if ((m = t.match(/^(#{1,4})\s+(.*)$/))) {           // 标题
      const lvl = m[1].length;
      if (lvl === 1) title = m[2];
      const heading = [HeadingLevel.TITLE, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl - 1];
      blocks.push(new Paragraph({ heading, children: inline(m[2]) }));
      continue;
    }
    if (t.startsWith(">")) {                              // 引用
      blocks.push(new Paragraph({
        indent: { left: 240 },
        spacing: { after: 60 },
        border: { left: { style: BorderStyle.SINGLE, size: 18, color: "C0392B", space: 8 } },
        children: inline(t.replace(/^>\s?/, ""), { color: "555555", size: 19 }),
      }));
      continue;
    }
    if ((m = line.match(/^(\s*)[-*]\s+(.*)$/))) {        // 无序列表
      const level = Math.min(Math.floor(m[1].length / 2), 1);
      blocks.push(new Paragraph({ numbering: { reference: "bullets", level }, children: inline(m[2]) }));
      continue;
    }
    if ((m = t.match(/^(\d+)\.\s+(.*)$/))) {             // 有序列表：保留原编号，避免跨段续号
      blocks.push(new Paragraph({ indent: { left: 420, hanging: 300 }, children: inline(`${m[1]}. ${m[2]}`) }));
      continue;
    }
    blocks.push(new Paragraph({ children: inline(t) })); // 普通段落
  }
  return { title, blocks };
}

function main() {
  const [input, outputArg] = process.argv.slice(2);
  if (!input) {
    console.error("用法：node scripts/md2docx.js <输入.md> [输出.docx]");
    process.exit(1);
  }
  const md = fs.readFileSync(input, "utf8");
  const { title, blocks } = convert(md);
  const repoRoot = path.resolve(__dirname, "..");
  const output = outputArg || path.join(repoRoot, "assets/files/word", path.basename(input).replace(/\.md$/i, ".docx"));
  fs.mkdirSync(path.dirname(output), { recursive: true });

  const doc = new Document({
    creator: "实验室雷达 · Claude 云端",
    title,
    styles: {
      default: { document: { run: { font: FONT, size: 21 }, paragraph: { spacing: { after: 100, line: 340 } } } },
      paragraphStyles: [
        { id: "Title", name: "Title", basedOn: "Normal", run: { font: FONT, size: 36, bold: true, color: ACCENT }, paragraph: { spacing: { after: 200 } } },
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 28, bold: true, color: ACCENT }, paragraph: { spacing: { before: 300, after: 140 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: "16213E" }, paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 22, bold: true }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } },
      ],
    },
    numbering: {
      config: [{
        reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 420, hanging: 260 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 840, hanging: 260 } } } },
        ],
      }],
    },
    sections: [{
      properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 1134, bottom: 1134, left: MARGIN, right: MARGIN } } },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: `${title}　·　第 `, size: 16, color: "888888", font: FONT }),
              new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "888888" }),
              new TextRun({ text: " 页", size: 16, color: "888888", font: FONT })],
          })],
        }),
      },
      children: blocks,
    }],
  });

  Packer.toBuffer(doc).then((buf) => {
    fs.writeFileSync(output, buf);
    console.log(`已生成：${output}`);
  }).catch((err) => {
    console.error(`生成失败：${err.message}`);
    process.exit(1);
  });
}

main();
