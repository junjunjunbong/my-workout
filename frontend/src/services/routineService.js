import { apiClient } from './api';

export const getRoutines = () => apiClient.get('/routines');
export const addRoutine = (routine) => apiClient.post('/routines', routine);
export const deleteRoutine = (id) => apiClient.delete(`/routines/${id}`);