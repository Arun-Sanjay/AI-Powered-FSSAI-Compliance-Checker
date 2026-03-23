import { useState } from 'react';
import UploadPage from './components/UploadPage';
import Dashboard from './components/Dashboard';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  if (result) {
    return (
      <Dashboard
        result={result}
        onReset={() => setResult(null)}
      />
    );
  }

  return (
    <UploadPage
      onResult={setResult}
      loading={loading}
      setLoading={setLoading}
    />
  );
}

export default App;
