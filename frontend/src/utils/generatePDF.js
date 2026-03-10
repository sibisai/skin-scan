import { jsPDF } from 'jspdf';

// Brand color
const PRIMARY_BLUE = [21, 112, 239]; // #1570EF
const SUCCESS_GREEN = [22, 163, 74]; // Green for high confidence
const WARNING_ORANGE = [234, 88, 12]; // Orange for medium confidence

/**
 * Generate a clean, professional medical analysis report PDF
 */
export async function generateAnalysisReport({
  prediction,
  confidence,
  probabilities,
  conditionDescription,
  modelName,
  originalImageSrc,
  heatmapCanvas,
  formatClassName,
  formatConfidence,
}) {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  const contentWidth = pageWidth - (margin * 2);
  let yPos = margin;

  // Get confidence color based on value
  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return SUCCESS_GREEN;
    if (conf >= 0.5) return WARNING_ORANGE;
    return [220, 38, 38]; // Red for low
  };

  // === HEADER ===
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(22);
  doc.setTextColor(30, 30, 30);
  doc.text('Medical Image Analysis Report', margin, yPos);

  // Date and model
  yPos += 9;
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  doc.setTextColor(120, 120, 120);
  const dateStr = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  doc.text(`${dateStr}  •  ${modelName}`, margin, yPos);

  // Divider
  yPos += 8;
  doc.setDrawColor(220, 220, 220);
  doc.setLineWidth(0.3);
  doc.line(margin, yPos, pageWidth - margin, yPos);

  // === PREDICTION SECTION ===
  yPos += 15;

  // Row with Prediction and Confidence
  // Left side: Prediction
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  doc.setTextColor(120, 120, 120);
  doc.text('Prediction', margin, yPos);

  // Right side: Confidence label
  doc.text('Confidence', pageWidth - margin, yPos, { align: 'right' });

  // Main prediction text
  yPos += 10;
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(28);
  doc.setTextColor(...PRIMARY_BLUE);
  doc.text(formatClassName(prediction), margin, yPos);

  // Confidence value (aligned right, same row)
  const confidenceColor = getConfidenceColor(confidence);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(28);
  doc.setTextColor(...confidenceColor);
  doc.text(`${formatConfidence(confidence)}%`, pageWidth - margin, yPos, { align: 'right' });

  // Condition description
  if (conditionDescription) {
    yPos += 10;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(70, 70, 70);
    const lines = doc.splitTextToSize(conditionDescription, contentWidth);
    doc.text(lines, margin, yPos);
    yPos += (lines.length * 5);
  }

  // === IMAGES SECTION (centered) ===
  yPos += 10;
  const imageSize = 55;
  const imageGap = 15;
  const totalImagesWidth = (imageSize * 2) + imageGap;
  const imagesStartX = (pageWidth - totalImagesWidth) / 2;

  // Image labels
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.setTextColor(100, 100, 100);
  doc.text('Original', imagesStartX + (imageSize / 2), yPos, { align: 'center' });
  doc.text('Grad-CAM Visualization', imagesStartX + imageSize + imageGap + (imageSize / 2), yPos, { align: 'center' });

  yPos += 4;
  const imageY = yPos;

  // Add original image
  if (originalImageSrc) {
    try {
      const imgData = await loadImageAsBase64(originalImageSrc);
      doc.addImage(imgData, 'JPEG', imagesStartX, imageY, imageSize, imageSize);
    } catch (e) {
      console.error('Failed to add original image:', e);
    }
  }

  // Add heatmap image
  if (heatmapCanvas) {
    try {
      const heatmapData = heatmapCanvas.toDataURL('image/png');
      doc.addImage(heatmapData, 'PNG', imagesStartX + imageSize + imageGap, imageY, imageSize, imageSize);
    } catch (e) {
      console.error('Failed to add heatmap image:', e);
    }
  }

  yPos = imageY + imageSize + 8;

  // Legend (centered under images)
  const legendWidth = 60;
  const legendX = (pageWidth - legendWidth) / 2;

  doc.setFontSize(9);
  doc.setTextColor(100, 100, 100);
  doc.text('Low importance', legendX - 3, yPos + 2, { align: 'right' });

  // Draw smooth gradient
  const gradientSegments = 60;
  const segmentWidth = legendWidth / gradientSegments;
  for (let i = 0; i < gradientSegments; i++) {
    const ratio = i / (gradientSegments - 1);
    let r, g, b;
    if (ratio < 0.5) {
      const t = ratio * 2;
      r = Math.round(59 + (250 - 59) * t);
      g = Math.round(130 + (204 - 130) * t);
      b = Math.round(246 + (21 - 246) * t);
    } else {
      const t = (ratio - 0.5) * 2;
      r = Math.round(250 + (239 - 250) * t);
      g = Math.round(204 + (68 - 204) * t);
      b = Math.round(21 + (68 - 21) * t);
    }
    doc.setFillColor(r, g, b);
    doc.rect(legendX + (i * segmentWidth), yPos - 2, segmentWidth + 0.3, 5, 'F');
  }

  doc.text('High importance', legendX + legendWidth + 3, yPos + 2);

  // === CLASS PROBABILITIES (below images, full width) ===
  yPos += 18;

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(11);
  doc.setTextColor(60, 60, 60);
  doc.text('Class Probabilities', margin, yPos);

  yPos += 8;
  const sortedProbs = Object.entries(probabilities).sort(([, a], [, b]) => b - a);
  const barMaxWidth = contentWidth - 70; // Leave space for label and percentage

  for (const [className, prob] of sortedProbs) {
    const displayName = formatClassName(className);
    const percentage = formatConfidence(prob);
    const isPredicted = className.toLowerCase() === prediction.toLowerCase();

    // Class name (left)
    doc.setFontSize(10);
    if (isPredicted) {
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...PRIMARY_BLUE);
    } else {
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(80, 80, 80);
    }
    doc.text(displayName, margin, yPos);

    // Progress bar (middle)
    const barX = margin + 45;
    const barY = yPos - 3;
    const barHeight = 4;

    // Background
    doc.setFillColor(235, 235, 235);
    doc.roundedRect(barX, barY, barMaxWidth, barHeight, 2, 2, 'F');

    // Fill
    if (isPredicted) {
      doc.setFillColor(...PRIMARY_BLUE);
    } else {
      doc.setFillColor(180, 180, 180);
    }
    const fillWidth = Math.max((parseFloat(percentage) / 100) * barMaxWidth, 3);
    doc.roundedRect(barX, barY, fillWidth, barHeight, 2, 2, 'F');

    // Percentage (right)
    if (isPredicted) {
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...PRIMARY_BLUE);
    } else {
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(100, 100, 100);
    }
    doc.text(`${percentage}%`, pageWidth - margin, yPos, { align: 'right' });

    yPos += 12;
  }

  // === DISCLAIMER (fixed at bottom) ===
  const disclaimerY = pageHeight - 32;

  doc.setFillColor(254, 252, 232);
  doc.roundedRect(margin, disclaimerY, contentWidth, 22, 2, 2, 'F');

  doc.setDrawColor(253, 224, 71);
  doc.setLineWidth(0.4);
  doc.roundedRect(margin, disclaimerY, contentWidth, 22, 2, 2, 'S');

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(9);
  doc.setTextColor(161, 98, 7);
  doc.text('Disclaimer:', margin + 5, disclaimerY + 6);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.setTextColor(133, 77, 14);
  const disclaimer = 'This report is generated by an AI-powered educational tool and is NOT a substitute for professional medical diagnosis. Always consult a qualified healthcare provider for medical advice, diagnosis, or treatment.';
  doc.text(doc.splitTextToSize(disclaimer, contentWidth - 10), margin + 5, disclaimerY + 12);

  // Footer
  doc.setFontSize(8);
  doc.setTextColor(170, 170, 170);
  doc.text('Medical Image Analysis Platform', pageWidth / 2, pageHeight - 6, { align: 'center' });

  // Save
  const fileName = `analysis_report_${prediction.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}.pdf`;
  doc.save(fileName);
}

/**
 * Load an image and convert to base64
 */
function loadImageAsBase64(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      resolve(canvas.toDataURL('image/jpeg', 0.9));
    };
    img.onerror = reject;
    img.src = src;
  });
}