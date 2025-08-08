import React, { useState } from 'react';
import { Paper, TextField, Button, Typography, Alert, Stack, Box } from '@mui/material';
import { getCoachRecommendations } from '../services/api';
import { createTodayAIRoutine, chatWithAI } from '../services/todayAiService';
import { getWorkouts } from '../services/api';

export default function CoachPage() {
  const [days, setDays] = useState(30);
  const [coach, setCoach] = useState(null);
  const [reply, setReply] = useState('');
  const [msg, setMsg] = useState('오늘 루틴 추천해줘');
  const [error, setError] = useState('');

  const loadCoach = async () => {
    setError('');
    try {
      const res = await getCoachRecommendations(days);
      setCoach(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };

  const todayRoutine = async () => {
    setError('');
    try {
      const ws = await getWorkouts();
      const r = await createTodayAIRoutine(ws.data || []);
      setReply(JSON.stringify(r, null, 2));
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };

  const chat = async () => {
    setError('');
    try {
      const ws = await getWorkouts();
      const res = await chatWithAI({ message: msg, workouts: ws.data || [], routine: null });
      setReply(res.reply || JSON.stringify(res.updatedRoutine || {}, null, 2));
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>AI Coach Demo</Typography>
      <Stack spacing={1}>
        {error && <Alert severity="error">{error}</Alert>}
        <Stack direction="row" spacing={1}>
          <TextField label="Days" type="number" value={days} onChange={(e)=>setDays(Number(e.target.value))} sx={{ width: 120 }} />
          <Button variant="contained" onClick={loadCoach}>Load Recommendations</Button>
          <Button variant="outlined" onClick={todayRoutine}>AI Today Routine</Button>
        </Stack>
        <Stack direction="row" spacing={1}>
          <TextField label="Message" fullWidth value={msg} onChange={(e)=>setMsg(e.target.value)} />
          <Button variant="outlined" onClick={chat}>Ask AI</Button>
        </Stack>
        {coach && (
          <Box component="pre" sx={{ p:1, bgcolor:'#f7f7f9', borderRadius:1 }}>{JSON.stringify(coach, null, 2)}</Box>
        )}
        {reply && (
          <Box component="pre" sx={{ p:1, bgcolor:'#f7f7f9', borderRadius:1 }}>{reply}</Box>
        )}
      </Stack>
    </Paper>
  );
}


