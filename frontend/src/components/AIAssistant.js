import React, { useState } from 'react';
import { Box, Paper, Typography, TextField, IconButton, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { chatWithAI } from '../services/todayAiService';

export default function AIAssistant({ routine, workouts, onRoutineUpdate }) {
  const [msg, setMsg] = useState('루틴을 상체 위주로 바꿔줘. 볼륨은 적당히.');
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState('');

  const send = async () => {
    if (!msg.trim()) return;
    setLoading(true);
    try {
      const res = await chatWithAI({ message: msg, routine, workouts });
      setReply(res.reply || '');
      if (res.updatedRoutine && onRoutineUpdate) onRoutineUpdate(res.updatedRoutine);
    } catch (e) {
      setReply('AI 대화에 실패했습니다. 잠시 후 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={0} sx={{ p: 2, border: '1px solid #eef2f7', borderRadius: 2 }}>
      <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>AI 어시스턴트</Typography>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          value={msg}
          onChange={(e) => setMsg(e.target.value)}
          placeholder="AI에게 질문하거나 루틴 수정을 요청해보세요"
        />
        <IconButton color="primary" onClick={send} disabled={loading}>
          {loading ? <CircularProgress size={20} /> : <SendIcon />}
        </IconButton>
      </Box>
      {reply && (
        <Box sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
          <Typography variant="body2">{reply}</Typography>
        </Box>
      )}
    </Paper>
  );
}
