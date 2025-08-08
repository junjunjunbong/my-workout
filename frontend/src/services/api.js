import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Workout endpoints
export const getWorkouts = () => api.get('/workouts');
export const addWorkout = (workout) => api.post('/workouts', workout);
export const deleteWorkout = (id) => api.delete(`/workouts/${id}`);
export const getWorkoutsByDate = (date) => api.get(`/workouts/${date}`);
export const getLastWorkoutForExercise = (exercise) => api.get(`/workouts/exercise/${exercise}/last`);

// Routine endpoints
export const getRoutines = () => api.get('/routines');
export const addRoutine = (routine) => api.post('/routines', routine);
export const deleteRoutine = (id) => api.delete(`/routines/${id}`);

// Config endpoint
export const getConfig = () => api.get('/config');

// Analytics endpoints
export const getWeeklyVolume = () => api.get('/analytics/weekly-volume');
export const getMonthlyVolume = () => api.get('/analytics/monthly-volume');
export const getCalendarSummary = (date) => api.get(`/calendar-summary/${date}`);

// Auth endpoints
export const login = (email, password) => api.post('/auth/login', { email, password });

// Social endpoints
export const followUser = (token, userId) =>
  api.post('/social/follow', { user_id: userId }, { headers: { Authorization: `Bearer ${token}` } });

export const unfollowUser = (token, userId) =>
  api.delete('/social/follow', { data: { user_id: userId }, headers: { Authorization: `Bearer ${token}` } });

export const getFeed = (token, { limit = 20, cursor } = {}) =>
  api.get('/social/feed', {
    params: { limit, cursor },
    headers: { Authorization: `Bearer ${token}` },
  });

// Likes & Comments endpoints
export const likeItem = (token, refId) =>
  api.post('/social/like', { ref_id: refId }, { headers: { Authorization: `Bearer ${token}` } });

export const unlikeItem = (token, refId) =>
  api.delete('/social/like', { data: { ref_id: refId }, headers: { Authorization: `Bearer ${token}` } });

export const createComment = (token, refId, content) =>
  api.post('/social/comment', { ref_id: refId, content }, { headers: { Authorization: `Bearer ${token}` } });

export const listComments = (token, refId) =>
  api.get('/social/comments', { params: { ref_id: refId }, headers: { Authorization: `Bearer ${token}` } });

export const deleteComment = (token, commentId) =>
  api.delete(`/social/comment/${commentId}`, { headers: { Authorization: `Bearer ${token}` } });

// Advanced analytics endpoints (for Task 6)
export const getPrTrend = (exercise, start, end) =>
  api.get('/analytics/pr-trend', { params: { exercise, start, end } });

export const getMuscleVolumeRange = (start, end) =>
  api.get('/analytics/muscle-volume-range', { params: { start, end } });

// AI Coach
export const getCoachRecommendations = (days = 30) =>
  api.get('/coach/recommendations', { params: { days } });

// Exercise detail
export const getExerciseDetail = (exercise, start, end) =>
  api.get('/analytics/exercise-detail', { params: { exercise, start, end } });

export default api;