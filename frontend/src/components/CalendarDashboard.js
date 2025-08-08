import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Box,
  IconButton,
  Paper,
  Grid,
  Snackbar,
} from '@mui/material';
import {
  format,
  parseISO,
  isToday,
  isSameMonth,
  isSameDay,
  addMonths,
  subMonths,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  addDays,
  eachDayOfInterval
} from 'date-fns';
import { ko } from 'date-fns/locale';
import { getWorkouts, deleteWorkout } from '../services/api';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import AddIcon from '@mui/icons-material/Add';

const CalendarDashboard = () => {
  const navigate = useNavigate();
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const workoutsRes = await getWorkouts();
        setWorkouts(workoutsRes.data);
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

  const nextMonth = () => {
    setCurrentDate(addMonths(currentDate, 1));
  };

  const prevMonth = () => {
    setCurrentDate(subMonths(currentDate, 1));
  };

  const renderHeader = () => {
    return (
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <IconButton onClick={prevMonth}>
          <ChevronLeftIcon />
        </IconButton>
        <Typography variant="h5">
          {format(currentDate, 'yyyy년 M월', { locale: ko })}
        </Typography>
        <IconButton onClick={nextMonth}>
          <ChevronRightIcon />
        </IconButton>
      </Box>
    );
  };

  const renderDays = () => {
    const days = [];
    const dateFormat = 'E';
    const startDate = startOfWeek(new Date());

    for (let i = 0; i < 7; i++) {
      days.push(
        <Box 
          key={i} 
          textAlign="center" 
          p={1} 
          fontWeight="bold"
          sx={{ 
            backgroundColor: '#f5f5f5',
            borderBottom: '1px solid #e0e0e0'
          }}
        >
          {format(addDays(startDate, i), dateFormat, { locale: ko })}
        </Box>
      );
    }

    return (
      <Box display="grid" gridTemplateColumns="repeat(7, 1fr)">
        {days}
      </Box>
    );
  };

  const renderCells = () => {
    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(monthStart);
    const endDate = endOfWeek(monthEnd);

    const dateFormat = 'd';
    const rows = [];

    let days = eachDayOfInterval({ start: startDate, end: endDate });
    
    for (let i = 0; i < days.length; i += 7) {
      const weekDays = days.slice(i, i + 7);
      rows.push(
        <Box 
          key={i} 
          display="grid" 
          gridTemplateColumns="repeat(7, 1fr)" 
          borderBottom="1px solid #e0e0e0"
        >
          {weekDays.map((day) => {
            const isCurrentMonth = isSameMonth(day, monthStart);
            const isTodayDay = isToday(day);
            const dayWorkouts = workouts.filter(workout => isSameDay(parseISO(workout.date), day));
            const overflow = dayWorkouts.length > 3 ? dayWorkouts.length - 3 : 0;
            
            return (
              <Box
                key={day.toString()}
                minHeight={120}
                p={1}
                sx={{
                  backgroundColor: isCurrentMonth ? 'white' : '#f9fbff',
                  borderRight: '1px solid #e0e0e0',
                  '&:last-child': { borderRight: 'none' },
                  position: 'relative',
                  cursor: 'pointer',
                  '&:hover': { backgroundColor: isCurrentMonth ? '#f5f9ff' : '#f0f4ff' }
                }}
                onClick={() => {
                  const formattedDate = format(day, 'yyyy-MM-dd');
                  navigate(`/add-workout?date=${formattedDate}`);
                }}
              >
                <Box 
                  display="flex" justifyContent="space-between" alignItems="center"
                  p={0.5}
                >
                  <Box sx={{
                    px: 1,
                    py: 0.25,
                    borderRadius: 10,
                    fontSize: '0.7rem',
                    color: isCurrentMonth ? 'text.secondary' : 'text.disabled',
                    backgroundColor: isTodayDay ? 'primary.light' : 'transparent',
                    ...(isTodayDay && { color: 'primary.contrastText' })
                  }}>
                    {format(day, dateFormat)}
                  </Box>
                  {isTodayDay && (
                    <Box sx={{
                      px: 1,
                      py: 0.25,
                      borderRadius: 10,
                      fontSize: '0.65rem',
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText'
                    }}>
                      Today
                    </Box>
                  )}
                </Box>
                <Box mt={0.5}>
                  {dayWorkouts.slice(0,3).map(workout => (
                    <Box 
                      key={workout.id}
                      sx={{
                        backgroundColor: '#e9f2ff',
                        borderRadius: 1,
                        p: 0.5,
                        mb: 0.5,
                        fontSize: '0.75rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      {workout.exercise}
                    </Box>
                  ))}
                  {overflow > 0 && (
                    <Box sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>+{overflow} more</Box>
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      );
    }

    return <Box>{rows}</Box>;
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

  return (
    <Container>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" sx={{ fontWeight: 800 }}>
          Workout Calendar
        </Typography>
        <Box display="flex" gap={1}>
          <Button 
            variant="outlined"
            size="small"
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
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            component={Link}
            to="/add-workout"
            sx={{ borderRadius: 8 }}
          >
            Add Workout
          </Button>
        </Box>
      </Box>

      <Snackbar
        open={!!aiError}
        onClose={() => setAiError('')}
        message={aiError}
        autoHideDuration={4000}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      />
      
      <Paper elevation={0} sx={{ p: 1.5, borderRadius: 2, border: '1px solid #eef2f7' }}>
        {renderHeader()}
        {renderDays()}
        {renderCells()}
      </Paper>
      
      <Box mt={4}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
          Recent Workouts
        </Typography>
        {workouts.length === 0 ? (
          <Alert severity="info">No workouts recorded yet. Add your first workout!</Alert>
        ) : (
          <Grid container spacing={1.5} columns={{ xs: 12 }}>
            {(showAll ? workouts.slice(0, 8) : workouts.slice(0, 3)).map(workout => (
              <Grid size={{ xs: 12 }} key={workout.id}>
                <Card elevation={0} sx={{ borderRadius: 2, border: '1px solid #eef2f7' }}>
                  <CardContent sx={{ py: 1.25 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      {format(parseISO(workout.date), 'yyyy년 M월 d일 EEEE', { locale: ko })}
                      {isToday(parseISO(workout.date)) && ' (Today)'}
                    </Typography>
                    <List dense>
                      <ListItem secondaryAction={
                        <Button 
                          variant="outlined" 
                          color="error" 
                          size="small"
                          onClick={() => handleDeleteWorkout(workout.id)}
                        >
                          삭제
                        </Button>
                      }>
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
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
        {workouts.length > 3 && (
          <Box mt={1} display="flex" justifyContent="center">
            <Button size="small" onClick={() => setShowAll(!showAll)}>
              {showAll ? '접기' : '더보기'}
            </Button>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default CalendarDashboard;