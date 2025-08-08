import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (email, password) => {
  const response = await apiClient.post('/auth/login', { email, password });
  if (response.data.token) {
    localStorage.setItem('token', response.data.token);
  }
  return response;
};

export const logout = () => {
  localStorage.removeItem('token');
};

export const getWorkouts = () => apiClient.get('/workouts');
export const addWorkout = (workout) => apiClient.post('/workouts', workout);
export const deleteWorkout = (workoutId) => apiClient.delete(`/workouts/${workoutId}`);
export const getLastWorkoutForExercise = (exercise) => apiClient.get(`/workouts/last?exercise=${exercise}`);

export const getRoutines = () => apiClient.get('/routines');
export const addRoutine = (routine) => apiClient.post('/routines', routine);
export const deleteRoutine = (routineId) => apiClient.delete(`/routines/${routineId}`);

export const getConfig = () => apiClient.get('/config');

export const getCoachRecommendations = (days) => apiClient.get(`/coach/recommendations?days=${days}`);

export const getFeed = () => apiClient.get('/feed');
export const followUser = (userId) => apiClient.post(`/users/${userId}/follow`);
export const unfollowUser = (userId) => apiClient.post(`/users/${userId}/unfollow`);

export const getWeeklyVolume = () => apiClient.get('/analytics/weekly-volume');
export const getMonthlyVolume = () => apiClient.get('/analytics/monthly-volume');

export { apiClient };

