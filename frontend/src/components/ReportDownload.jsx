import { jsPDF } from 'jspdf';

function getGradeLabel(grade) {
  const map = { A: 'Excellent', B: 'Good', C: 'Needs Improvement', F: 'Non-Compliant' };
  return map[grade] || grade;
}

function addWrappedText(doc, text, x, y, maxWidth, lineHeight) {
  const lines = doc.splitTextToSize(text, maxWidth);
  for (const line of lines) {
    if (y > 270) {
      doc.addPage();
      y = 20;
    }
    doc.text(line, x, y);
    y += lineHeight;
  }
  return y;
}

function generateReport(result) {
  const doc = new jsPDF();
  const { label_data, findings, risk_score, summary } = result;
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  const contentWidth = pageWidth - margin * 2;

  // ─── PAGE 1: Cover ───
  doc.setFontSize(10);
  doc.setTextColor(150);
  doc.text('FSSAI COMPLIANCE REPORT', margin, 20);

  doc.setDrawColor(59, 130, 246);
  doc.setLineWidth(0.8);
  doc.line(margin, 25, pageWidth - margin, 25);

  doc.setFontSize(28);
  doc.setTextColor(30, 41, 59);
  doc.text('Compliance Audit', margin, 50);

  doc.setFontSize(12);
  doc.setTextColor(100, 116, 139);
  doc.text(label_data.product_name || 'Food Product', margin, 62);
  if (label_data.brand) {
    doc.text(`Brand: ${label_data.brand}`, margin, 70);
  }
  if (label_data.food_category) {
    doc.text(`Category: ${label_data.food_category}`, margin, 78);
  }
  doc.text(`Date: ${new Date().toLocaleDateString('en-IN')}`, margin, 86);

  // Overall Score
  let y = 110;
  const scoreColor =
    risk_score.overall_score >= 85
      ? [34, 197, 94]
      : risk_score.overall_score >= 70
      ? [234, 179, 8]
      : risk_score.overall_score >= 50
      ? [249, 115, 22]
      : [239, 68, 68];

  doc.setFontSize(60);
  doc.setTextColor(...scoreColor);
  doc.text(`${risk_score.overall_score}`, margin, y);

  doc.setFontSize(16);
  doc.setTextColor(100, 116, 139);
  doc.text('/ 100', margin + 55, y);

  doc.setFontSize(14);
  doc.setTextColor(...scoreColor);
  doc.text(`Grade ${risk_score.grade} — ${getGradeLabel(risk_score.grade)}`, margin, y + 12);

  doc.setFontSize(10);
  doc.setTextColor(71, 85, 105);
  y = addWrappedText(doc, summary || '', margin, y + 28, contentWidth, 5);

  // ─── PAGE 2: Module Scores ───
  doc.addPage();
  y = 20;

  doc.setFontSize(16);
  doc.setTextColor(30, 41, 59);
  doc.text('Module Scores', margin, y);
  y += 12;

  // Table header
  doc.setFontSize(9);
  doc.setTextColor(255);
  doc.setFillColor(51, 65, 85);
  doc.rect(margin, y, contentWidth, 8, 'F');
  doc.text('Module', margin + 3, y + 5.5);
  doc.text('Score', margin + 60, y + 5.5);
  doc.text('Critical', margin + 90, y + 5.5);
  doc.text('Warnings', margin + 120, y + 5.5);
  y += 10;

  // Table rows
  for (const m of risk_score.modules) {
    if (y > 270) { doc.addPage(); y = 20; }
    const bg = y % 20 < 10 ? [248, 250, 252] : [255, 255, 255];
    doc.setFillColor(...bg);
    doc.rect(margin, y - 4, contentWidth, 8, 'F');

    doc.setTextColor(30, 41, 59);
    doc.text(m.module.charAt(0).toUpperCase() + m.module.slice(1), margin + 3, y + 1);

    const mColor =
      m.score >= 85 ? [34, 197, 94] : m.score >= 70 ? [234, 179, 8] : [239, 68, 68];
    doc.setTextColor(...mColor);
    doc.text(`${m.score}`, margin + 60, y + 1);

    doc.setTextColor(239, 68, 68);
    doc.text(`${m.critical_count}`, margin + 90, y + 1);

    doc.setTextColor(234, 179, 8);
    doc.text(`${m.warning_count}`, margin + 120, y + 1);

    y += 10;
  }

  // ─── PAGE 3+: Findings Detail ───
  y += 10;
  if (y > 240) { doc.addPage(); y = 20; }

  doc.setFontSize(16);
  doc.setTextColor(30, 41, 59);
  doc.text('Compliance Findings', margin, y);
  y += 12;

  const sortedFindings = [...findings].sort((a, b) => {
    const order = { CRITICAL: 0, WARNING: 1, INFO: 2 };
    return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
  });

  for (const f of sortedFindings) {
    if (y > 255) { doc.addPage(); y = 20; }

    // Severity badge
    const sColor =
      f.severity === 'CRITICAL' ? [239, 68, 68] : f.severity === 'WARNING' ? [234, 179, 8] : [59, 130, 246];
    doc.setFontSize(8);
    doc.setTextColor(...sColor);
    doc.text(`[${f.severity}]`, margin, y);

    doc.setTextColor(100, 116, 139);
    doc.text(`${f.module}`, margin + 25, y);
    y += 5;

    // Title
    doc.setFontSize(10);
    doc.setTextColor(30, 41, 59);
    y = addWrappedText(doc, f.title, margin, y, contentWidth, 4.5);
    y += 1;

    // Description
    doc.setFontSize(8);
    doc.setTextColor(71, 85, 105);
    y = addWrappedText(doc, f.description, margin, y, contentWidth, 3.8);

    if (f.regulation) {
      doc.setTextColor(148, 163, 184);
      y = addWrappedText(doc, `Ref: ${f.regulation}`, margin, y + 1, contentWidth, 3.5);
    }

    if (f.recommendation) {
      doc.setTextColor(100, 116, 139);
      doc.setFont(undefined, 'italic');
      y = addWrappedText(doc, `Fix: ${f.recommendation}`, margin, y + 1, contentWidth, 3.5);
      doc.setFont(undefined, 'normal');
    }

    y += 6;
  }

  // ─── Final page: Disclaimer ───
  if (y > 230) { doc.addPage(); y = 20; }
  y += 10;
  doc.setDrawColor(200);
  doc.line(margin, y, pageWidth - margin, y);
  y += 8;

  doc.setFontSize(8);
  doc.setTextColor(148, 163, 184);
  const disclaimer = [
    'DISCLAIMER: This report is generated automatically using AI-based label extraction and rule-based compliance checking.',
    'Results are indicative and should be verified by qualified food safety professionals.',
    'FSSAI compliance determinations are based on the Food Safety and Standards (Packaging and Labelling) Regulations, 2011',
    'and FSS (Advertising and Claims) Regulations, 2018. This tool does not replace formal regulatory audit.',
    '',
    'Generated by Food Label Analyzer — AI-Powered FSSAI Compliance Checker',
    `Report Date: ${new Date().toLocaleString('en-IN')}`,
  ];
  for (const line of disclaimer) {
    doc.text(line, margin, y);
    y += 4;
  }

  const fileName = `${(label_data.product_name || 'analysis').replace(/[^a-zA-Z0-9]/g, '_')}_compliance_report.pdf`;
  doc.save(fileName);
}

export default function ReportDownload({ result }) {
  return (
    <button
      onClick={() => generateReport(result)}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition cursor-pointer flex items-center gap-2"
    >
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      Download PDF Report
    </button>
  );
}
