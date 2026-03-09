import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Автоматически добавляем токен к каждому запросу
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const login = (email, password) =>
  api.post('/auth/login', { email, password });

// Competitions
export const getCompetitions = () => api.get('/competitions/');

// Divisions
export const getDivisions = (competitionId) =>
  api.get(`/competitions/${competitionId}/divisions`);

export const getDivision = (divisionId) =>
  api.get(`/divisions/${divisionId}`);

// Disciplines
export const getDisciplines = (divisionId) =>
  api.get(`/disciplines/division/${divisionId}`);

// Participants
export const getParticipants = (divisionId) =>
  api.get(`/participants/division/${divisionId}`);

// Results
export const getResults = (disciplineId) =>
  api.get(`/results/discipline/${disciplineId}`);

export const upsertResult = (disciplineId, data) =>
  api.post(`/results/discipline/${disciplineId}`, data);

export const calculateStandings = (disciplineId) =>
  api.post(`/disciplines/${disciplineId}/calculate-standings`);

export const calculateOverall = (divisionId) =>
  api.post(`/divisions/${divisionId}/calculate-overall`);

export default api;