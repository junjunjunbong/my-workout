import { getWeeklyVolume, getMonthlyVolume, apiClient } from './api';

export { getWeeklyVolume, getMonthlyVolume };

export const getExerciseStats = async (exerciseName) => {
  const response = await apiClient.get(`/analytics/exercise-stats/${exerciseName}`);
  return response.data;
};

export const getWorkoutDistribution = async () => {
  const response = await apiClient.get('/analytics/workout-distribution');
  return response.data;
};

export const getProgressOverTime = async (metric) => {
  const response = await apiClient.get(`/analytics/progress-over-time?metric=${metric}`);
  return response.data;
};
