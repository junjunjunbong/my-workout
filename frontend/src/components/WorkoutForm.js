import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Box,
  Card,
  CardContent,
  IconButton,
  Alert,
  Grid,
  FormControlLabel,
  Switch,
  Paper,
  Chip
} from '@mui/material';
import { Add, Remove } from '@mui/icons-material';
import { format } from 'date-fns';
import { addWorkout, getConfig, getLastWorkoutForExercise } from '../services/api';
import AIAssistant from './AIAssistant';

const WorkoutForm = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [config, setConfig] = useState(null);
  
  // Extract date from URL parameters
  const urlParams = new URLSearchParams(location.search);
  const initialDate = urlParams.get('date') || format(new Date(), 'yyyy-MM-dd');
  
  // Check if a routine was passed in the location state
  const routineFromState = location.state?.routine;
  
  const [formData, setFormData] = useState({
    date: initialDate,
    category: routineFromState?.items?.[0]?.category || '',
    exercise: routineFromState?.items?.[0]?.exercise || '',
    type: 'strength',
    sets: [{ weight_kg: '', reps: '' }],
    cardio: { minutes: '', distance_km: '' },
    notes: routineFromState?.name ? `루틴: ${routineFromState.name}` : ''
  });
  
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [useLastValues, setUseLastValues] = useState(false);
  const [appliedRoutine, setAppliedRoutine] = useState(routineFromState || null);
  const [currentRoutineItemIndex, setCurrentRoutineItemIndex] = useState(0);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await getConfig();
        setConfig(res.data);
        setExercises(res.data.exercises);
        
        // If a routine was applied, set the first exercise
        if (routineFromState && routineFromState.items.length > 0) {
          const firstItem = routineFromState.items[0];
          setFormData(prev => ({
            ...prev,
            category: firstItem.category,
            exercise: firstItem.exercise
          }));
        }
      } catch (err) {
        setError('Failed to load configuration');
      }
    };

    fetchConfig();
  }, [routineFromState]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleCategoryChange = (e) => {
    const category = e.target.value;
    setFormData({
      ...formData,
      category,
      exercise: ''
    });
  };

  const handleExerciseChange = (e) => {
    const exercise = e.target.value;
    setFormData({
      ...formData,
      exercise
    });
    
    // If useLastValues is enabled, fetch last workout for this exercise
    if (useLastValues && exercise) {
      fetchLastWorkout(exercise);
    }
  };
  
  const handleNextRoutineItem = () => {
    if (!appliedRoutine || currentRoutineItemIndex >= appliedRoutine.items.length - 1) {
      return;
    }
    
    const nextIndex = currentRoutineItemIndex + 1;
    const nextItem = appliedRoutine.items[nextIndex];
    
    setFormData({
      ...formData,
      category: nextItem.category,
      exercise: nextItem.exercise
    });
    
    setCurrentRoutineItemIndex(nextIndex);
  };
  
  const handlePreviousRoutineItem = () => {
    if (!appliedRoutine || currentRoutineItemIndex <= 0) {
      return;
    }
    
    const prevIndex = currentRoutineItemIndex - 1;
    const prevItem = appliedRoutine.items[prevIndex];
    
    setFormData({
      ...formData,
      category: prevItem.category,
      exercise: prevItem.exercise
    });
    
    setCurrentRoutineItemIndex(prevIndex);
  };

  const fetchLastWorkout = async (exercise) => {
    try {
      const res = await getLastWorkoutForExercise(exercise);
      const lastWorkout = res.data;
      
      if (lastWorkout && lastWorkout.type === 'strength' && lastWorkout.sets.length > 0) {
        setFormData({
          ...formData,
          exercise,
          sets: lastWorkout.sets.map(set => ({
            weight_kg: set.weight_kg,
            reps: set.reps
          }))
        });
      }
    } catch (err) {
      console.error('Failed to fetch last workout', err);
    }
  };

  const handleSetChange = (index, field, value) => {
    const newSets = [...formData.sets];
    newSets[index][field] = value;
    setFormData({
      ...formData,
      sets: newSets
    });
  };

  const addSet = () => {
    setFormData({
      ...formData,
      sets: [...formData.sets, { weight_kg: '', reps: '' }]
    });
  };

  const removeSet = (index) => {
    if (formData.sets.length > 1) {
      const newSets = [...formData.sets];
      newSets.splice(index, 1);
      setFormData({
        ...formData,
        sets: newSets
      });
    }
  };

  const handleCardioChange = (field, value) => {
    setFormData({
      ...formData,
      cardio: {
        ...formData.cardio,
        [field]: value
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Prepare data for submission
      const workoutData = {
        ...formData,
        sets: formData.type === 'strength' 
          ? formData.sets.map(set => ({
              weight_kg: parseFloat(set.weight_kg) || 0,
              reps: parseInt(set.reps) || 0
            }))
          : [],
        cardio: formData.type === 'cardio' 
          ? {
              minutes: parseFloat(formData.cardio.minutes) || 0,
              distance_km: formData.cardio.distance_km 
                ? parseFloat(formData.cardio.distance_km) 
                : null
            }
          : null
      };

      await addWorkout(workoutData);
      setSuccess(true);
      
      // Reset form
      setFormData({
        date: format(new Date(), 'yyyy-MM-dd'),
        category: '',
        exercise: '',
        type: 'strength',
        sets: [{ weight_kg: '', reps: '' }],
        cardio: { minutes: '', distance_km: '' },
        notes: ''
      });
    } catch (err) {
      setError('Failed to add workout');
    } finally {
      setLoading(false);
    }
  };

  if (!config) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="md">
      <Box mb={3}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 800 }}>
          운동 기록 추가
        </Typography>
      </Box>
      
      {appliedRoutine && (
        <Paper elevation={1} sx={{ p: 2, mb: 3, borderRadius: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              적용된 루틴: {appliedRoutine.name}
            </Typography>
            <Chip 
              label={`${currentRoutineItemIndex + 1} / ${appliedRoutine.items.length}`} 
              color="primary" 
            />
          </Box>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
            {appliedRoutine.items.map((item, index) => (
              <Chip
                key={index}
                label={`${item.exercise} (${item.sets}×${item.reps})`}
                color={index === currentRoutineItemIndex ? "primary" : "default"}
                variant={index === currentRoutineItemIndex ? "filled" : "outlined"}
              />
            ))}
          </Box>

          {/* AI Assistant */}
          <AIAssistant 
            routine={appliedRoutine}
            workouts={[]}
            onRoutineUpdate={(updated) => {
              if (!updated || !updated.items || updated.items.length === 0) {
                return;
              }
              const first = updated.items[0];
              const repsStr = typeof first.reps === 'string' ? first.reps : String(first.reps ?? '');
              const isCardio = /분|km|킬로|시간|초/i.test(repsStr) || (first.category && /유산소/i.test(first.category));
              const repNumber = (repsStr.match(/\d+/) || [""])[0];
              const setsCount = Number(first.sets) || 3;

              setAppliedRoutine(updated);
              setCurrentRoutineItemIndex(0);
              setFormData((prev) => ({
                ...prev,
                category: first.category || '',
                exercise: first.exercise || '',
                type: isCardio ? 'cardio' : 'strength',
                sets: isCardio ? [{ weight_kg: '', reps: '' }] : Array.from({ length: setsCount }, () => ({ weight_kg: '', reps: repNumber })),
                cardio: isCardio ? { minutes: Number(repsStr.replace(/[^0-9.]/g, '')) || 30, distance_km: null } : { minutes: '', distance_km: '' },
                notes: `루틴: ${updated.name} (AI 수정)`
              }));
            }}
          />
          
          <Box display="flex" justifyContent="space-between" mt={2}>
            <Button
              variant="outlined"
              onClick={handlePreviousRoutineItem}
              disabled={currentRoutineItemIndex === 0}
            >
              이전 운동
            </Button>
            <Button
              variant="outlined"
              onClick={handleNextRoutineItem}
              disabled={currentRoutineItemIndex === appliedRoutine.items.length - 1}
            >
              다음 운동
            </Button>
          </Box>
        </Paper>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          운동 기록이 성공적으로 추가되었습니다!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card elevation={0} sx={{ borderRadius: 3, border: '1px solid #eef2f7' }}>
        <CardContent>
          <Box component="form" onSubmit={handleSubmit}>
            <Grid container columnSpacing={2} rowSpacing={2} columns={12}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  label="Date"
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  fullWidth
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    name="category"
                    value={formData.category}
                    onChange={handleCategoryChange}
                  >
                    {config.categories.map(category => (
                      <MenuItem key={category} value={category}>{category}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth>
                  <InputLabel>Exercise</InputLabel>
                  <Select
                    name="exercise"
                    value={formData.exercise}
                    onChange={handleExerciseChange}
                    disabled={!formData.category}
                  >
                    {formData.category && exercises[formData.category] ? (
                      exercises[formData.category].map(exercise => (
                        <MenuItem key={exercise} value={exercise}>{exercise}</MenuItem>
                      ))
                    ) : (
                      <MenuItem disabled>Select a category first</MenuItem>
                    )}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    name="type"
                    value={formData.type}
                    onChange={handleChange}
                  >
                    <MenuItem value="strength">Strength</MenuItem>
                    <MenuItem value="cardio">Cardio</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              {formData.exercise && (
                <Grid xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useLastValues}
                        onChange={(e) => setUseLastValues(e.target.checked)}
                      />
                    }
                    label="Use values from last workout"
                  />
                </Grid>
              )}
              
              {formData.type === 'strength' && (
                <Grid xs={12}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 700 }}>
                    Sets
                  </Typography>
                  
                  {formData.sets.map((set, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                      <Typography sx={{ mr: 2, color: 'text.secondary', minWidth: 56 }}>Set {index + 1}</Typography>
                      <TextField
                        label="Weight (kg)"
                        type="number"
                        value={set.weight_kg}
                        onChange={(e) => handleSetChange(index, 'weight_kg', e.target.value)}
                        sx={{ mr: 2, width: 140 }}
                      />
                      <TextField
                        label="Reps"
                        type="number"
                        value={set.reps}
                        onChange={(e) => handleSetChange(index, 'reps', e.target.value)}
                        sx={{ mr: 2, width: 120 }}
                      />
                      <IconButton onClick={() => removeSet(index)} disabled={formData.sets.length <= 1}>
                        <Remove />
                      </IconButton>
                    </Box>
                  ))}
                  
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={addSet}
                    sx={{ mt: 1, borderRadius: 8 }}
                  >
                    Add Set
                  </Button>
                </Grid>
              )}
              
              {formData.type === 'cardio' && (
                <Grid xs={12} md={6}>
                  <TextField
                    label="Minutes"
                    type="number"
                    value={formData.cardio.minutes}
                    onChange={(e) => handleCardioChange('minutes', e.target.value)}
                    fullWidth
                  />
                </Grid>
              )}
              
              {formData.type === 'cardio' && (
                <Grid xs={12} md={6}>
                  <TextField
                    label="Distance (km)"
                    type="number"
                    value={formData.cardio.distance_km}
                    onChange={(e) => handleCardioChange('distance_km', e.target.value)}
                    fullWidth
                  />
                </Grid>
              )}
              
              <Grid xs={12}>
                <TextField
                  label="Notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  multiline
                  rows={3}
                  fullWidth
                />
              </Grid>
              
              <Grid xs={12}>
                <Box display="flex" gap={2}>
                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading || !formData.category || !formData.exercise}
                    fullWidth
                    sx={{ borderRadius: 8 }}
                  >
                    {loading ? 'Adding...' : 'Add Workout'}
                  </Button>
                  
                  {appliedRoutine && currentRoutineItemIndex === appliedRoutine.items.length - 1 && (
                    <Button
                      variant="contained"
                      color="secondary"
                      onClick={() => navigate('/routines')}
                      fullWidth
                      sx={{ borderRadius: 8 }}
                    >
                      루틴 완료
                    </Button>
                  )}
                </Box>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default WorkoutForm;