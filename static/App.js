import React, { useState } from 'react';

function App() {
  const [githubUrl, setGithubUrl] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (event) => {
    setGithubUrl(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      const res = await fetch('/get_response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: 'session_1',  // or dynamically generate it
          question: githubUrl,
        }),
      });

      const data = await res.json();
      setResponse(data.answer);
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error fetching response');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>GitHub Query Form</h1>
      <form onSubmit={handleSubmit}>
        <label>
          GitHub URL:
          <input
            type="text"
            value={githubUrl}
            onChange={handleChange}
            placeholder="Enter GitHub URL"
            required
          />
        </label>
        <button type="submit">Submit</button>
      </form>

      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <div>
          <h2>Answer:</h2>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}

export default App;
