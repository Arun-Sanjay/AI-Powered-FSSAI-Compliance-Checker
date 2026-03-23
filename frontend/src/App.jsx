import { useState } from 'react';
import UploadPage from './components/UploadPage';
import Dashboard from './components/Dashboard';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState(null);

  const handleReset = () => {
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    setResult(null);
    setImageUrl(null);
  };

  if (result) {
    return (
      <Dashboard
        result={result}
        imageUrl={imageUrl}
        onReset={handleReset}
      />
    );
  }

  return (
    <UploadPage
      onResult={setResult}
      onImageUrl={setImageUrl}
      loading={loading}
      setLoading={setLoading}
    />
  );
}

export default App;
