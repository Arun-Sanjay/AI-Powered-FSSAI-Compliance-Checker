import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export async function analyzeLabel(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  const response = await api.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function getAdditives() {
  const response = await api.get('/additives');
  return response.data;
}

export async function getAllergens() {
  const response = await api.get('/allergens');
  return response.data;
}

export async function runSimulation(labelData, modifications) {
  const response = await api.post('/simulate', {
    label_data: labelData,
    modifications,
  });
  return response.data;
}
