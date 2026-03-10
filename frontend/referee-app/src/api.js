import axios from 'axios';

const api = axios.create({
  baseURL: 'https://ranking.worldstrongman.org',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const login = (email, password) =>
  api.post('/auth/login', { email, password });

export const getCompetitions = () => api.get('/competitions/');
export const getResults = (disciplineId) => api.get(`/results/discipline/${disciplineId}`);
export const upsertResult = (disciplineId, data) => api.post(`/results/discipline/${disciplineId}`, data);
export const calculateStandings = (disciplineId) => api.post(`/disciplines/${disciplineId}/calculate-standings`);

export default api;
