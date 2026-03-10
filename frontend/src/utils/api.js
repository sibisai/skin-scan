const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function analyzeImage(modelName, imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await fetch(
    `${API_URL}/predict/${modelName}/gradcam`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Analysis failed');
  }

  return response.json();
}

export async function generateExplanation(modelName, prediction, confidence, comparisonImageB64) {
  // Convert base64 to blob
  const byteString = atob(comparisonImageB64);
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  const blob = new Blob([ab], { type: 'image/png' });
  const file = new File([blob], 'comparison.png', { type: 'image/png' });

  const formData = new FormData();
  formData.append('file', file);

  const params = new URLSearchParams({
    prediction,
    confidence: confidence.toString(),
  });

  const response = await fetch(
    `${API_URL}/explain/${modelName}?${params}`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Explanation failed');
  }

  return response.json();
}