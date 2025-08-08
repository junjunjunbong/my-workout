import React, { useState } from 'react';
import { Box, Paper, TextField, Button, Typography, Alert, Stack } from '@mui/material';
import { login } from '../services/api';
import axios from 'axios';

export default function AuthPage() {
  const [email, setEmail] = useState('demo1@example.com');
  const [password, setPassword] = useState('Demo1234!');
  const [token, setToken] = useState('');
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');

  const register = async () => {
    setError('');
    try {
      await axios.post((process.env.REACT_APP_API_BASE || 'http://localhost:8000/api') + '/auth/register', { email, password });
      alert('Registered. Now login.');
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };

  const doLogin = async () => {
    setError('');
    try {
      const res = await login(email, password);
      setToken(res.data.token);
      setUserId(res.data.user_id);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>Auth Demo</Typography>
      <Stack spacing={1}>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField label="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
        <TextField label="Password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} />
        <Box display="flex" gap={1}>
          <Button variant="outlined" onClick={register}>Register</Button>
          <Button variant="contained" onClick={doLogin}>Login</Button>
        </Box>
        {token && (
          <Alert severity="success">Logged in. user_id={userId}. Token stored in memory (copy for Swagger):<br/>{token}</Alert>
        )}
      </Stack>
    </Paper>
  );
}


