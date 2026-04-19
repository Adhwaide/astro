import React, { useRef, useState } from 'react';
import html2pdf from 'html2pdf.js';
import ReactMarkdown from 'react-markdown';

export default function ReportPanel({ chartData }) {
  const contentRef = useRef(null);
  const [exporting, setExporting] = useState(false);

  if (!chartData) return null;

  const handleExportPDF = () => {
    setExporting(true);
    const element = contentRef.current;
    if (!element) return;

    // We create a clone so we can force styling suitable for PDF
    // Alternatively, we configure html2pdf to use dark mode or light mode
    const opt = {
      margin:       10,
      filename:     'jyotisha_report.pdf',
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true, logging: false },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    // Temporarily add a white background class or just export as is (which exports nicely on dark backgrounds too)
    html2pdf().set(opt).from(element).save().then(() => {
      setExporting(false);
    });
  };

  const { report, yogas } = chartData;

  return (
    <div className="glass-panel" style={{ position: 'relative' }}>
      <button 
        onClick={handleExportPDF} 
        disabled={exporting}
        style={{ position: 'absolute', top: '10px', right: '10px', padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
      >
        {exporting ? 'Generating PDF...' : 'Export to PDF'}
      </button>

      <div ref={contentRef} style={{ padding: '1rem', color: 'var(--color-text-main)' }} className="pdf-content">
        {/* We use inline styles heavily here so html2canvas captures them correctly */}
        <h2 style={{ color: 'var(--color-gold-light)', borderBottom: '1px solid var(--color-glass-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
          Astrological Blueprint
        </h2>

        {/* Written Report powered by ReactMarkdown */}
        <div style={{ lineHeight: '1.6', fontSize: '0.95rem', color: 'var(--color-text-main)' }}>
          <ReactMarkdown
            components={{
              h2: ({node, ...props}) => <h3 style={{ color: 'var(--color-gold-deep)', marginTop: '1.5rem', marginBottom: '0.5rem' }} {...props} />,
              h3: ({node, ...props}) => <h4 style={{ color: 'var(--color-gold-light)', marginTop: '1rem', marginBottom: '0.5rem' }} {...props} />,
              p: ({node, ...props}) => <p style={{ marginBottom: '1rem' }} {...props} />,
              ul: ({node, ...props}) => <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem' }} {...props} />,
              li: ({node, ...props}) => <li style={{ marginBottom: '0.5rem' }} {...props} />,
              strong: ({node, ...props}) => <strong style={{ color: 'var(--color-gold-light)' }} {...props} />
            }}
          >
            {report}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
