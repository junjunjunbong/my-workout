import api from './api';

export const getRoutines = () => api.get('/routines');
export const addRoutine = (routine) => api.post('/routines', routine);
export const deleteRoutine = (id) => api.delete(`/routines/${id}`);