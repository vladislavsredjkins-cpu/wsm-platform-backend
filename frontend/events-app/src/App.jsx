import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import Login from './pages/Login';
import Landing from './pages/Landing';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import RefereeCompetitions from './pages/referee/Competitions';
import RefereeDisciplines from './pages/referee/Disciplines';
import RefereeResults from './pages/referee/Results';
import AthleteProfile from './pages/athlete/Profile';
import AthleteCompetitions from './pages/athlete/Competitions';
import TeamProfile from './pages/team/Profile';
import OrganizerCompetitions from './pages/organizer/Competitions';
import CreateCompetition from './pages/organizer/CreateCompetition';
import OrganizerCompetitionDetail from './pages/organizer/CompetitionDetail';
import EventsCompetitionDetail from './pages/organizer/EventsCompetitionDetail';
import FullCompetitionDetail from './pages/organizer/FullCompetitionDetail';
import OrganizerProfile from './pages/organizer/Profile';
import AthleteRegister from './pages/AthleteRegister';
import Tournaments from './pages/Tournaments';

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  return children;
}

export default function App() {
  const { user, loading } = useAuth();
  if (loading) return (
    <div style={{ color: '#1a1a1a', textAlign: 'center', marginTop: '40vh', background: '#f7f4ef', minHeight: '100vh' }}>
      Loading...
    </div>
  );
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
      <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" />} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/referee" element={<ProtectedRoute><RefereeCompetitions /></ProtectedRoute>} />
      <Route path="/referee/:divisionId/disciplines" element={<ProtectedRoute><RefereeDisciplines /></ProtectedRoute>} />
      <Route path="/referee/:disciplineId/results" element={<ProtectedRoute><RefereeResults /></ProtectedRoute>} />
      <Route path="/athlete/profile" element={<ProtectedRoute><AthleteProfile /></ProtectedRoute>} />
      <Route path="/athlete/competitions" element={<ProtectedRoute><AthleteCompetitions /></ProtectedRoute>} />
      <Route path="/team/profile" element={<ProtectedRoute><TeamProfile /></ProtectedRoute>} />
      <Route path="/organizer/competitions" element={<ProtectedRoute><OrganizerCompetitions /></ProtectedRoute>} />
      <Route path="/organizer/competitions/new" element={<ProtectedRoute><CreateCompetition /></ProtectedRoute>} />
      <Route path="/organizer/competitions/:competitionId" element={<ProtectedRoute><FullCompetitionDetail /></ProtectedRoute>} />
      <Route path="/organizer/profile" element={<ProtectedRoute><OrganizerProfile /></ProtectedRoute>} />
      <Route path="/tournaments" element={<Tournaments />} />
      <Route path="/tournament/:competitionId/register" element={<AthleteRegister />} />
      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/"} />} />
    </Routes>
  );
}
