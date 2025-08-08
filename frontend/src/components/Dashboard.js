import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  Box,
  Snackbar,
} from '@mui/material';
import { format, parseISO, isToday } from 'date-fns';
import { ko } from 'date-fns/locale';
import { getWorkouts, deleteWorkout, getConfig } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const [workouts, setWorkouts] = useState([]);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [workoutsRes, configRes] = await Promise.all([
          getWorkouts(),
          getConfig()
        ]);
        setWorkouts(workoutsRes.data);
        setConfig(configRes.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        if (err.code === 'ERR_NETWORK') {
          setError('Network Error: Unable to connect to the backend server. Please make sure the backend server is running.');
        } else {
          setError('Failed to fetch data: ' + (err.response?.data?.detail || err.message));
        }
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleDeleteWorkout = async (id) => {
    try {
      await deleteWorkout(id);
      setWorkouts(workouts.filter(workout => workout.id !== id));
    } catch (err) {
      setError('Failed to delete workout');
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  // Group workouts by date
  const workoutsByDate = workouts.reduce((acc, workout) => {
    const date = workout.date;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(workout);
    return acc;
  }, {});

  // Sort dates in descending order
  const sortedDates = Object.keys(workoutsByDate).sort((a, b) => new Date(b) - new Date(a));

  return (
    <Container>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 800 }}>
          Workout Dashboard
        </Typography>
        <Button 
          variant="outlined"
          disabled={aiLoading}
          onClick={async () => {
            try {
              setAiError('');
              setAiLoading(true);
              const { getWorkouts } = await import('../services/api');
              const { createTodayAIRoutine } = await import('../services/todayAiService');
              const workoutsRes = await getWorkouts();
              const routine = await createTodayAIRoutine(workoutsRes.data || []);
              const { format } = await import('date-fns');
              const today = format(new Date(), 'yyyy-MM-dd');
              navigate(`/add-workout?date=${today}`, { state: { routine } });
            } catch (e) {
              console.error('AI today routine failed', e);
              setAiError('AI 루틴 생성에 실패했습니다. 서버 상태를 확인해주세요.');
            } finally {
              setAiLoading(false);
            }
          }}
          sx={{ borderRadius: 8, minWidth: 140 }}
        >
          {aiLoading ? <CircularProgress size={16} /> : 'AI 오늘 루틴'}
        </Button>
      </Box>

      <Snackbar
        open={!!aiError}
        onClose={() => setAiError('')}
        message={aiError}
        autoHideDuration={4000}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      />
      
      {sortedDates.length === 0 ? (
        <Alert severity="info" sx={{ borderRadius: 2 }}>No workouts recorded yet. Add your first workout!</Alert>
      ) : (
        <Grid container spacing={2} columns={12}>
          {sortedDates.map(date => (
            <Grid xs={12} key={date}>
              <Card elevation={0} sx={{ borderRadius: 3, border: '1px solid #eef2f7' }}>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    {format(parseISO(date), 'yyyy년 M월 d일 EEEE', { locale: ko })}
                    {isToday(parseISO(date)) && ' (Today)'}
                  </Typography>
                  <List dense>
                    {workoutsByDate[date].map(workout => (
                      <React.Fragment key={workout.id}>
                        <ListItem
                          secondaryAction={
                            <Button 
                              variant="outlined" 
                              color="error" 
                              size="small"
                              onClick={() => handleDeleteWorkout(workout.id)}
                            >
                              삭제
                            </Button>
                          }
                        >
                          <ListItemText
                            primaryTypographyProps={{ fontWeight: 700 }}
                            primary={`${workout.exercise} (${workout.category})`}
                            secondary={
                              <Box>
                                {workout.type === 'strength' ? (
                                  <Box>
                                    {workout.sets.map((set, index) => (
                                      <span key={index}>
                                        {set.weight_kg}kg × {set.reps}회{index < workout.sets.length - 1 ? ', ' : ''}
                                      </span>
                                    ))}
                                  </Box>
                                ) : (
                                  <Box>
                                    {workout.cardio.minutes}분
                                    {workout.cardio.distance_km && ` / ${workout.cardio.distance_km}km`}
                                  </Box>
                                )}
                                {workout.notes && (
                                  <Box sx={{ fontStyle: 'italic', mt: 1, color: 'text.secondary' }}>
                                    메모: {workout.notes}
                                  </Box>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                        <Divider component="li" />
                      </React.Fragment>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default Dashboard;