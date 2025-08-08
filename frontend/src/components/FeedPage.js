import React, { useState } from 'react';
import { Paper, TextField, Button, Typography, Alert, Stack, List, ListItem, ListItemText } from '@mui/material';
import { followUser, unfollowUser, getFeed } from '../services/api';

export default function FeedPage() {
  const [token, setToken] = useState('');
  const [targetId, setTargetId] = useState('2');
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');

  const follow = async () => {
    setError('');
    try {
      await followUser(token, Number(targetId));
      alert('Followed');
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };
  const unfollow = async () => {
    setError('');
    try {
      await unfollowUser(token, Number(targetId));
      alert('Unfollowed');
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };
  const load = async () => {
    setError('');
    try {
      const res = await getFeed(token);
      setItems(res.data.items || []);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>Feed Demo</Typography>
      <Stack spacing={1}>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField label="Bearer Token" value={token} onChange={(e)=>setToken(e.target.value)} fullWidth />
        <TextField label="Target User ID" value={targetId} onChange={(e)=>setTargetId(e.target.value)} />
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" onClick={follow}>Follow</Button>
          <Button variant="outlined" color="warning" onClick={unfollow}>Unfollow</Button>
          <Button variant="contained" onClick={load}>Load Feed</Button>
        </Stack>
        <List>
          {items.map((it)=> (
            <ListItem key={it.id}>
              <ListItemText primary={`${it.type} by user ${it.user_id}`} secondary={it.created_at} />
            </ListItem>
          ))}
        </List>
      </Stack>
    </Paper>
  );
}


