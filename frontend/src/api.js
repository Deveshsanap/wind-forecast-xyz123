import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getJanuaryAnalysis = async () => {
  const response = await api.get('/analysis/january-2026');
  return response.data;
};