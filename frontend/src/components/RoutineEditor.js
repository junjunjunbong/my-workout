import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material';
import { addRoutine } from '../services/routineService';
import { getConfig } from '../services/api';

const RoutineEditor = ({ routine, onSave, onCancel }) => {
  const [config, setConfig] = useState(null);
  const [routineItems, setRoutineItems] = useState(routine.items || []);
  const [openItemDialog, setOpenItemDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [itemExercise, setItemExercise] = useState('');
  const [itemCategory, setItemCategory] = useState('');
  const [itemSets, setItemSets] = useState('');
  const [itemReps, setItemReps] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await getConfig();
        setConfig(res.data);
      } catch (err) {
        setError('Failed to load configuration');
      }
    };

    fetchConfig();
  }, []);

  const handleOpenItemDialog = (item = null) => {
    if (item) {
      setEditingItem(item);
      setItemExercise(item.exercise);
      setItemCategory(item.category);
      setItemSets(item.sets);
      setItemReps(item.reps);
    } else {
      setEditingItem(null);
      setItemExercise('');
      setItemCategory('');
      setItemSets('');
      setItemReps('');
    }
    setOpenItemDialog(true);
  };

  const handleCloseItemDialog = () => {
    setOpenItemDialog(false);
    setEditingItem(null);
    setItemExercise('');
    setItemCategory('');
    setItemSets('');
    setItemReps('');
  };

  const handleSaveItem = () => {
    if (!itemExercise || !itemCategory || !itemSets || !itemReps) {
      setError('모든 필드를 입력해주세요.');
      return;
    }

    const newItem = {
      exercise: itemExercise,
      category: itemCategory,
      sets: parseInt(itemSets),
      reps: itemReps
    };

    if (editingItem) {
      // Update existing item
      const updatedItems = routineItems.map(item => 
        item === editingItem ? newItem : item
      );
      setRoutineItems(updatedItems);
    } else {
      // Add new item
      setRoutineItems([...routineItems, newItem]);
    }

    handleCloseItemDialog();
  };

  const handleDeleteItem = (itemToDelete) => {
    setRoutineItems(routineItems.filter(item => item !== itemToDelete));
  };

  const handleSaveRoutine = async () => {
    try {
      // Update the routine with the new items
      const updatedRoutine = {
        ...routine,
        items: routineItems
      };
      
      await addRoutine(updatedRoutine);
      onSave(updatedRoutine);
    } catch (error) {
      setError('루틴 저장에 실패했습니다: ' + error.message);
    }
  };

  return (
    <Container maxWidth="md">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">루틴 편집: {routine.name}</Typography>
        <Box>
          <Button
            variant="outlined"
            onClick={onCancel}
            sx={{ mr: 1 }}
          >
            취소
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSaveRoutine}
          >
            저장
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">루틴 항목</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenItemDialog()}
          >
            항목 추가
          </Button>
        </Box>

        {routineItems.length === 0 ? (
          <Typography color="textSecondary" align="center" sx={{ py: 2 }}>
            아직 추가된 항목이 없습니다.
          </Typography>
        ) : (
          <List>
            {routineItems.map((item, index) => (
              <ListItem key={index} divider>
                <ListItemText
                  primary={`${item.exercise} (${item.category})`}
                  secondary={`세트: ${item.sets}, 반복: ${item.reps}`}
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={() => handleOpenItemDialog(item)}>
                    <EditIcon />
                  </IconButton>
                  <IconButton edge="end" onClick={() => handleDeleteItem(item)}>
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>

      <Dialog open={openItemDialog} onClose={handleCloseItemDialog}>
        <DialogTitle>
          {editingItem ? '항목 수정' : '새 항목 추가'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>카테고리</InputLabel>
              <Select
                value={itemCategory}
                onChange={(e) => setItemCategory(e.target.value)}
              >
                {config?.categories?.map(category => (
                  <MenuItem key={category} value={category}>{category}</MenuItem>
                ))}
              </Select>
            </FormControl>

            {itemCategory && (
              <FormControl fullWidth>
                <InputLabel>운동 종목</InputLabel>
                <Select
                  value={itemExercise}
                  onChange={(e) => setItemExercise(e.target.value)}
                >
                  {config?.exercises?.[itemCategory]?.map(exercise => (
                    <MenuItem key={exercise} value={exercise}>{exercise}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}

            <TextField
              label="세트 수"
              type="number"
              value={itemSets}
              onChange={(e) => setItemSets(e.target.value)}
              InputProps={{ inputProps: { min: 1 } }}
            />

            <TextField
              label="반복 횟수"
              value={itemReps}
              onChange={(e) => setItemReps(e.target.value)}
              helperText="예: 8-12, 10, 30초"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseItemDialog}>취소</Button>
          <Button onClick={handleSaveItem} color="primary" variant="contained">
            저장
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default RoutineEditor;