import api from './api';

export const createTodayAIRoutine = async (workouts) => {
  const res = await api.post('/ai/today-routine', { workouts });
  return res.data;
};

export const chatWithAI = async ({ message, routine, workouts }) => {
  const res = await api.post('/ai/chat', { message, routine, workouts });
  return res.data; // { reply, suggestions?, updatedRoutine? }
};
