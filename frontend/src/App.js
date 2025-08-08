import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme, Container, useMediaQuery } from '@mui/material';
import { responsiveFontSizes } from '@mui/material/styles';
import CalendarDashboard from './components/CalendarDashboard';
import WorkoutForm from './components/WorkoutForm';
import RoutineManager from './components/RoutineManager';
import AIRoutineGenerator from './components/AIRoutineGenerator';
import Analytics from './components/Analytics';
import Navigation from './components/Navigation';
import AuthPage from './components/AuthPage';
import FeedPage from './components/FeedPage';
import CoachPage from './components/CoachPage';

let theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1e88e5' },
    secondary: { main: '#ff7043' },
    background: { default: '#f7f9fc', paper: '#ffffff' },
    text: { primary: '#1c2630', secondary: '#6b7280' },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: ['Pretendard','Inter','-apple-system','BlinkMacSystemFont','Segoe UI','Roboto','Arial','sans-serif'].join(','),
    h4: { fontWeight: 700 },
    h5: { fontWeight: 700 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  components: {
    MuiPaper: { styleOverrides: { root: { borderRadius: 16 } } },
    MuiButton: { styleOverrides: { root: { borderRadius: 10 } } },
    MuiAppBar: { styleOverrides: { root: { boxShadow: 'none' } } },
  },
});
theme = responsiveFontSizes(theme);

function App() {
  const isXs = useMediaQuery(theme.breakpoints.down('sm'));
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navigation />
        <Container maxWidth={isXs ? 'sm' : 'lg'} sx={{ py: { xs: 2, sm: 3 }, px: { xs: 2, sm: 3 } }}>
          <Routes>
            <Route path="/" element={<CalendarDashboard />} />
            <Route path="/add-workout" element={<WorkoutForm />} />
            <Route path="/routines" element={<RoutineManager />} />
            <Route path="/ai-routines" element={<AIRoutineGenerator />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/feed" element={<FeedPage />} />
            <Route path="/coach" element={<CoachPage />} />
          </Routes>
        </Container>
      </Router>
    </ThemeProvider>
  );
}

export default App;