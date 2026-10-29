import axios from 'axios';

// Automatically use relative '/api' in production (Vercel), and localhost for local dev
const baseURL = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api';

const api = axios.create({
  baseURL: baseURL,
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getJanuaryAnalysis = async () => {
  const response = await api.get('/analysis/january-2026');
  return response.data;
};