import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import { addRoutine, getWorkouts } from '../services/api';
import { createTodayAIRoutine } from '../services/todayAiService';

const AIRoutineGenerator = () => {
  const [goal, setGoal] = useState('근력 향상');
  const [experience, setExperience] = useState('초보자');
  const [availableEquipment, setAvailableEquipment] = useState(['덤벨', '바벨', '머신']);
  const [workoutFrequency, setWorkoutFrequency] = useState(3);
  const [generatedRoutine, setGeneratedRoutine] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // In a real app, we would fetch actual workout history
    // For now, we'll use mock data
  }, []);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);
      // Use real recent workouts to ask backend AI
      const workoutsRes = await getWorkouts();
      const routine = await createTodayAIRoutine(workoutsRes.data || []);
      setGeneratedRoutine(routine);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      // Convert routine items to the format expected by the API
      const routineToSave = {
        name: generatedRoutine.name,
        memo: generatedRoutine.memo,
        items: generatedRoutine.items.map(item => ({
          exercise: item.exercise,
          category: item.category,
          sets: item.sets,
          reps: item.reps
        }))
      };
      
      await addRoutine(routineToSave);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000); // Hide success message after 3 seconds
    } catch (err) {
      setError('루틴 저장에 실패했습니다: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const equipmentOptions = [
    '덤벨', '바벨', '머신', '케틀벨', '밴드', '체중', '로잉머신', '사이클머신'
  ];

  return (
    <Container maxWidth="md">
      <Box mb={3}>
        <Typography variant="h4" gutterBottom>
          AI 맞춤 루틴 생성기
        </Typography>
        <Typography variant="body1" color="textSecondary">
          당신의 목표와 경험에 맞는 운동 루틴을 AI가 생성해줍니다.
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          사용자 정보 입력
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControl fullWidth>
            <InputLabel>운동 목표</InputLabel>
            <Select
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
            >
              <MenuItem value="근력 향상">근력 향상</MenuItem>
              <MenuItem value="체중 감량">체중 감량</MenuItem>
              <MenuItem value="근육량 증가">근육량 증가</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth>
            <InputLabel>운동 경험</InputLabel>
            <Select
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
            >
              <MenuItem value="초보자">초보자</MenuItem>
              <MenuItem value="중급자">중급자</MenuItem>
              <MenuItem value="고급자">고급자</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            label="주 운동 빈도 (주당)"
            type="number"
            value={workoutFrequency}
            onChange={(e) => setWorkoutFrequency(parseInt(e.target.value) || 3)}
            InputProps={{ inputProps: { min: 1, max: 7 } }}
          />
          
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              사용 가능한 장비
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {equipmentOptions.map((equip) => (
                <Chip
                  key={equip}
                  label={equip}
                  onClick={() => {
                    if (availableEquipment.includes(equip)) {
                      setAvailableEquipment(availableEquipment.filter(e => e !== equip));
                    } else {
                      setAvailableEquipment([...availableEquipment, equip]);
                    }
                  }}
                  color={availableEquipment.includes(equip) ? "primary" : "default"}
                  variant={availableEquipment.includes(equip) ? "filled" : "outlined"}
                />
              ))}
            </Box>
          </Box>
        </Box>
        
        <Box mt={3}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerate}
            disabled={loading}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : 'AI 루틴 생성'}
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          루틴이 성공적으로 저장되었습니다!
        </Alert>
      )}

      {generatedRoutine && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              생성된 루틴: {generatedRoutine.name}
            </Typography>
            <Button
              variant="contained"
              color="secondary"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? <CircularProgress size={24} /> : '루틴 저장'}
            </Button>
          </Box>
          
          <Typography variant="body2" color="textSecondary" mb={2}>
            {generatedRoutine.memo}
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {generatedRoutine.items.map((item, index) => (
              <Paper key={index} sx={{ p: 2 }}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="subtitle1">
                    {item.exercise} ({item.category})
                  </Typography>
                  <Typography variant="body2">
                    {item.sets} 세트 × {item.reps}
                  </Typography>
                </Box>
              </Paper>
            ))}
          </Box>
        </Paper>
      )}
    </Container>
  );
};

export default AIRoutineGenerator;