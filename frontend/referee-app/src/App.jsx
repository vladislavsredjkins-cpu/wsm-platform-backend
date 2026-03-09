import { AuthProvider, useAuth } from './AuthContext';
import { useState } from 'react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Divisions from './pages/Divisions';
import Disciplines from './pages/Disciplines';
import Results from './pages/Results';

function AppContent() {
  const { user, loading } = useAuth();
  const [competition, setCompetition] = useState(null);
  const [division, setDivision] = useState(null);
  const [discipline, setDiscipline] = useState(null);

  if (loading) return (
    <div style={{ color: '#fff', textAlign: 'center', marginTop: '40vh', background: '#0a0a0a', minHeight: '100vh' }}>
      Loading...
    </div>
  );

  if (!user) return <Login />;

  const handleBack = (to) => {
    if (to === 'competitions') { setCompetition(null); setDivision(null); setDiscipline(null); }
    if (to === 'divisions') { setDivision(null); setDiscipline(null); }
    if (to === 'disciplines') { setDiscipline(null); }
  };

  if (discipline) return (
    <Results
      competition={competition}
      division={division}
      discipline={discipline}
      onBack={handleBack}
    />
  );

  if (division) return (
    <Disciplines
      competition={competition}
      division={division}
      onBack={handleBack}
      onSelect={setDiscipline}
    />
  );

  if (competition) return (
    <Divisions
      competition={competition}
      onBack={() => setCompetition(null)}
      onSelect={setDivision}
    />
  );

  return <Dashboard onSelect={setCompetition} />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
