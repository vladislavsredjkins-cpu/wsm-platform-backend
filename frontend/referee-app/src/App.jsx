import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// Referee
import RefereeCompetitions from './pages/referee/Competitions';
import RefereeDisciplines from './pages/referee/Disciplines';
import RefereeResults from './pages/referee/Results';

// Athlete
import AthleteProfile from './pages/athlete/Profile';
import AthleteCompetitions from './pages/athlete/Competitions';
import JudgeProfile from './pages/judge/Profile';
import CoachProfile from './pages/coach/Profile';
import TeamProfile from './pages/team/Profile';
import ASLDashboard from './pages/asl/ASLDashboard';
import ASLJudgeDashboard from './pages/asl/ASLJudgeDashboard';
import ASLDivision from './pages/asl/ASLDivision';
import ASLMatch from './pages/asl/ASLMatch';
// Organizer
import OrganizerCompetitions from './pages/organizer/Competitions';
import OrganizerCompetitionDetail from './pages/organizer/CompetitionDetail';
import OrganizerProfile from './pages/organizer/Profile';

function ProtectedRoute({ children, roles }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  return children;
}

export default function App() {
  const { user, loading } = useAuth();

  if (loading) return (
    <div style={{ color: '#fff', textAlign: 'center', marginTop: '40vh', background: '#0a0a0a', minHeight: '100vh' }}>
      Loading...
    </div>
  );

  return (
    <Routes>
      <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

      {/* Referee routes */}
      <Route path="/referee" element={<ProtectedRoute><RefereeCompetitions /></ProtectedRoute>} />
      <Route path="/referee/:divisionId/disciplines" element={<ProtectedRoute><RefereeDisciplines /></ProtectedRoute>} />
      <Route path="/referee/:disciplineId/results" element={<ProtectedRoute><RefereeResults /></ProtectedRoute>} />

      {/* Organizer routes */}
      <Route path="/athlete/profile" element={<ProtectedRoute><AthleteProfile /></ProtectedRoute>} />
      <Route path="/athlete/competitions" element={<ProtectedRoute><AthleteCompetitions /></ProtectedRoute>} />
      <Route path="/judge/profile" element={<ProtectedRoute><JudgeProfile /></ProtectedRoute>} />
      <Route path="/coach/profile" element={<ProtectedRoute><CoachProfile /></ProtectedRoute>} />
      <Route path="/team/profile" element={<ProtectedRoute><TeamProfile /></ProtectedRoute>} />
      <Route path="/asl/judge" element={<ProtectedRoute><ASLJudgeDashboard /></ProtectedRoute>} />
      <Route path="/asl/divisions/:divisionId" element={<ProtectedRoute><ASLDivision /></ProtectedRoute>} />
      <Route path="/asl/matches/:matchId" element={<ProtectedRoute><ASLMatch /></ProtectedRoute>} />
      <Route path="/asl" element={<ProtectedRoute><ASLDashboard /></ProtectedRoute>} />
      <Route path="/organizer/competitions" element={<ProtectedRoute><OrganizerCompetitions /></ProtectedRoute>} />
      <Route path="/organizer/competitions/:competitionId" element={<ProtectedRoute><OrganizerCompetitionDetail /></ProtectedRoute>} />
      <Route path="/organizer/profile" element={<ProtectedRoute><OrganizerProfile /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
    </Routes>
  );
}
