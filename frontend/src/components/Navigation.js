import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container, IconButton, Drawer, List, ListItemButton, ListItemText } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import { Link, useLocation } from 'react-router-dom';

const NavButton = ({ to, label, active }) => (
  <Button
    color="inherit"
    component={Link}
    to={to}
    variant={active ? 'outlined' : 'text'}
    sx={{
      mx: 0.25,
      minWidth: 0,
      borderColor: active ? 'rgba(255,255,255,0.7)' : 'transparent',
      '&:hover': { backgroundColor: 'rgba(255,255,255,0.08)' },
    }}
  >
    {label}
  </Button>
);

const Navigation = () => {
  const location = useLocation();
  const path = location.pathname;
  const theme = useTheme();
  const isXs = useMediaQuery(theme.breakpoints.down('sm'));
  const [open, setOpen] = React.useState(false);
  const toggle = (val) => () => setOpen(val);

  const links = [
    { to: '/', label: 'Dashboard', active: path === '/' },
    { to: '/add-workout', label: 'Add Workout', active: path === '/add-workout' },
    { to: '/routines', label: 'Routines', active: path === '/routines' },
    { to: '/ai-routines', label: 'AI Routines', active: path === '/ai-routines' },
    { to: '/analytics', label: 'Analytics', active: path === '/analytics' },
  ];

  return (
    <AppBar position="sticky" color="primary">
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ py: 0.5 }}>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 800 }}>
            My Workout Tracker
          </Typography>
          {isXs ? (
            <>
              <IconButton color="inherit" aria-label="menu" onClick={toggle(true)} edge="end">
                <MenuIcon />
              </IconButton>
              <Drawer anchor="right" open={open} onClose={toggle(false)}>
                <Box role="presentation" sx={{ width: 260 }} onClick={toggle(false)} onKeyDown={toggle(false)}>
                  <List>
                    {links.map((l) => (
                      <ListItemButton key={l.to} component={Link} to={l.to} selected={l.active}>
                        <ListItemText primary={l.label} />
                      </ListItemButton>
                    ))}
                  </List>
                </Box>
              </Drawer>
            </>
          ) : (
            <Box display="flex" alignItems="center">
              {links.map((l) => (
                <NavButton key={l.to} to={l.to} label={l.label} active={l.active} />
              ))}
            </Box>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navigation;