const STORAGE_KEY = 'fssai_analysis_history';
const MAX_ENTRIES = 20;

/**
 * Compress an image file to a small base64 data URL for storage.
 * Resizes to max 150px wide for thumbnail use.
 */
export function compressImage(file) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const maxW = 150;
        const scale = Math.min(maxW / img.width, 1);
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL('image/jpeg', 0.6));
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

/**
 * Save an analysis result to localStorage.
 */
export function saveAnalysis(result, imageDataUrl) {
  const history = getHistory();
  const entry = {
    id: Date.now().toString(),
    timestamp: new Date().toISOString(),
    productName: result.label_data.product_name || 'Unknown Product',
    brand: result.label_data.brand || '',
    category: result.label_data.food_category || '',
    score: result.risk_score.overall_score,
    grade: result.risk_score.grade,
    image: imageDataUrl || null,
    result,
  };

  history.unshift(entry);

  // Trim to max entries
  while (history.length > MAX_ENTRIES) {
    history.pop();
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch (e) {
    // If storage is full, remove oldest entries and retry
    while (history.length > 5) {
      history.pop();
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch {
      console.warn('Could not save to localStorage');
    }
  }

  return entry;
}

/**
 * Get all saved analyses.
 */
export function getHistory() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

/**
 * Delete a single analysis by ID.
 */
export function deleteAnalysis(id) {
  const history = getHistory().filter((e) => e.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  return history;
}

/**
 * Clear all saved analyses.
 */
export function clearHistory() {
  localStorage.removeItem(STORAGE_KEY);
}
