import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  Paper,
  Alert,
  Chip,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon, PlayArrow as ApplyIcon } from '@mui/icons-material';
import { getRoutines, addRoutine, deleteRoutine } from '../services/routineService';
import { useNavigate } from 'react-router-dom';
import RoutineEditor from './RoutineEditor';

const RoutineManager = () => {
  const navigate = useNavigate();
  const [routines, setRoutines] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRoutine, setEditingRoutine] = useState(null);
  const [routineName, setRoutineName] = useState('');
  const [routineMemo, setRoutineMemo] = useState('');
  const [error, setError] = useState(null);
  const [editingRoutineItems, setEditingRoutineItems] = useState(null);

  useEffect(() => {
    fetchRoutines();
  }, []);

  const fetchRoutines = async () => {
    try {
      setError(null);
      const response = await getRoutines();
      setRoutines(response.data);
    } catch (error) {
      console.error('Error fetching routines:', error);
      if (error.code === 'ERR_NETWORK') {
        setError('Network Error: Unable to connect to the backend server. Please make sure the backend server is running.');
      } else {
        setError('Error fetching routines: ' + (error.response?.data?.detail || error.message));
      }
    }
  };

  const handleOpenDialog = (routine = null) => {
    if (routine) {
      setEditingRoutine(routine);
      setRoutineName(routine.name);
      setRoutineMemo(routine.memo || '');
    } else {
      setEditingRoutine(null);
      setRoutineName('');
      setRoutineMemo('');
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingRoutine(null);
    setRoutineName('');
    setRoutineMemo('');
  };

  const handleSubmit = async () => {
    try {
      if (editingRoutine) {
        // For simplicity, we'll delete and recreate
        await deleteRoutine(editingRoutine.id);
      }
      await addRoutine({ name: routineName, memo: routineMemo, items: editingRoutine?.items || [] });
      fetchRoutines();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving routine:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteRoutine(id);
      fetchRoutines();
    } catch (error) {
      console.error('Error deleting routine:', error);
    }
  };

  const handleApplyRoutine = (routine) => {
    // Navigate to the workout form with the routine data
    navigate('/add-workout', { state: { routine } });
  };

  const handleEditRoutineItems = (routine) => {
    setEditingRoutineItems(routine);
  };

  const handleSaveRoutineItems = (updatedRoutine) => {
    // Update the routine in the list
    setRoutines(routines.map(r => r.id === updatedRoutine.id ? updatedRoutine : r));
    setEditingRoutineItems(null);
  };

  const handleCancelRoutineItems = () => {
    setEditingRoutineItems(null);
  };

  // If we're editing routine items, show the RoutineEditor component
  if (editingRoutineItems) {
    return (
      <RoutineEditor 
        routine={editingRoutineItems}
        onSave={handleSaveRoutineItems}
        onCancel={handleCancelRoutineItems}
      />
    );
  }

  return (
    <Container maxWidth="md">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>운동 루틴 관리</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 8 }}
        >
          루틴 추가
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={0} sx={{ borderRadius: 3, border: '1px solid #eef2f7' }}>
        <List>
          {routines.map((routine) => (
            <ListItem key={routine.id} divider>
              <ListItemText
                primaryTypographyProps={{ fontWeight: 700 }}
                primary={routine.name}
                secondary={
                  <Box>
                    <Typography component="span" variant="body2" color="textSecondary">
                      {routine.memo || '메모 없음'}
                    </Typography>
                    {routine.items && routine.items.length > 0 && (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                        {routine.items.slice(0, 3).map((item, index) => (
                          <Chip 
                            key={index} 
                            label={`${item.exercise} (${item.sets}×${item.reps})`} 
                            size="small" 
                            variant="outlined" 
                          />
                        ))}
                        {routine.items.length > 3 && (
                          <Chip 
                            label={`+${routine.items.length - 3} more`} 
                            size="small" 
                            variant="outlined" 
                          />
                        )}
                      </Box>
                    )}
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleApplyRoutine(routine)}>
                  <ApplyIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleEditRoutineItems(routine)}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDelete(routine.id)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>
          {editingRoutine ? '루틴 수정' : '새 루틴 추가'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="루틴 이름"
            fullWidth
            value={routineName}
            onChange={(e) => setRoutineName(e.target.value)}
          />
          <TextField
            margin="dense"
            label="메모"
            fullWidth
            multiline
            rows={3}
            value={routineMemo}
            onChange={(e) => setRoutineMemo(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>취소</Button>
          <Button onClick={handleSubmit} color="primary" variant="contained">
            저장
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default RoutineManager;