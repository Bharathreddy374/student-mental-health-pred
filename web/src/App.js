import React, { useState } from 'react';

function App() {
  // Form state
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Male');
  const [phq9, setPhq9] = useState(Array(9).fill(''));
  const [sleepQuality, setSleepQuality] = useState('Good');
  const [studyPressure, setStudyPressure] = useState('Average');
  const [financialPressure, setFinancialPressure] = useState('Average');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const phq9Questions = [
    'Little interest or pleasure in doing things',
    'Feeling down, depressed, or hopeless',
    'Trouble falling or staying asleep, or sleeping too much',
    'Feeling tired or having little energy',
    'Poor appetite or overeating',
    'Feeling bad about yourself—or that you are a failure or have let yourself or your family down',
    'Trouble concentrating on things, such as reading the newspaper or watching television',
    'Moving or speaking so slowly that other people could have noticed? Or the opposite—being so fidgety or restless that you have been moving around a lot more than usual',
    'Thoughts that you would be better off dead or of hurting yourself in some way'
  ];
  const phq9Options = [
    { value: 0, label: 'Not at all' },
    { value: 1, label: 'Several days' },
    { value: 2, label: 'More than half the days' },
    { value: 3, label: 'Nearly every day' }
  ];
  const genderOptions = ['Male', 'Female', 'Other'];
  const sleepOptions = ['Good', 'Average', 'Bad'];
  const pressureOptions = ['Low', 'Average', 'High'];

  // Handlers
  const handlePhq9Change = (idx, value) => {
    const newPhq9 = [...phq9];
    newPhq9[idx] = value;
    setPhq9(newPhq9);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          age: Number(age),
          gender,
          phq9: phq9.map(Number),
          sleep_quality: sleepQuality,
          study_pressure: studyPressure,
          financial_pressure: financialPressure
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setResult({ error: 'Prediction failed. Backend may be down.' });
    }
    setLoading(false);
  };

  // Severity mapping
  const severityOrder = ['Minimal', 'Mild', 'Moderate', 'Moderately severe', 'Severe'];
  const severityEmojis = ['😊', '🙂', '😐', '😟', '😢'];

  // Helper to get severity label and emoji
  const getSeverityLabel = (sev) => {
    let idx = -1;
    if (typeof sev === 'number' && sev >= 0 && sev < severityOrder.length) idx = sev;
    else if (!isNaN(Number(sev)) && Number(sev) >= 0 && Number(sev) < severityOrder.length) idx = Number(sev);
    else if (typeof sev === 'string') idx = severityOrder.indexOf(sev);
    if (idx >= 0) {
      return `${severityEmojis[idx]} ${severityOrder[idx]}`;
    }
    return sev;
  };

  // Info section toggle
  const [showInfo, setShowInfo] = useState(false);

  return (
    <div className="App" style={{ maxWidth: 650, margin: '2rem auto', padding: 24, border: '1px solid #e0e0e0', borderRadius: 12, background: '#f8fafc', boxShadow: '0 2px 8px #f0f0f0' }}>
      <h1 style={{ textAlign: 'center', marginBottom: 18, color: '#1976d2', letterSpacing: 1 }}>Student Mental Health PHQ-9</h1>
      <div style={{ textAlign: 'center', marginBottom: 18 }}>
        <button type="button" onClick={() => setShowInfo(v => !v)} style={{ background: '#e3eafc', color: '#1976d2', border: 'none', borderRadius: 6, padding: '6px 18px', fontWeight: 500, cursor: 'pointer', fontSize: 15 }}>
          {showInfo ? 'Hide' : 'How does this work?'}
        </button>
      </div>
      {showInfo && (
        <div style={{ background: '#fff', border: '1px solid #dbeafe', borderRadius: 8, padding: 18, marginBottom: 24, fontSize: 15, color: '#333', boxShadow: '0 1px 3px #f3f3f3' }}>
          <b>How it works:</b>
          <ul style={{ margin: '10px 0 10px 18px' }}>
            <li>Fill in your age, gender, and answer the 9 PHQ-9 questions about your mood and feelings over the past 2 weeks.</li>
            <li>Provide your sleep quality, study pressure, and financial pressure.</li>
            <li>Click <b>Predict Severity</b> to get your depression severity level, as predicted by a machine learning model trained on real student data.</li>
          </ul>
          <b>Severity Levels:</b>
          <ul style={{ margin: '10px 0 0 18px' }}>
            <li>😊 <b>Minimal</b>: No or very mild symptoms</li>
            <li>🙂 <b>Mild</b>: Mild symptoms, monitor and self-care</li>
            <li>😐 <b>Moderate</b>: Noticeable symptoms, consider talking to someone</li>
            <li>😟 <b>Moderately severe</b>: Significant symptoms, professional help recommended</li>
            <li>😢 <b>Severe</b>: Severe symptoms, seek professional help</li>
          </ul>
          <div style={{ marginTop: 10, fontSize: 13, color: '#666' }}>
            <b>Note:</b> This tool is for educational purposes and not a substitute for professional diagnosis.
          </div>
        </div>
      )}
      <form onSubmit={handleSubmit}>
        {/* Demographics */}
        <div style={{ display: 'flex', gap: 24, marginBottom: 24 }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontWeight: 500 }}>Age</label>
            <input type="number" min="10" max="100" required value={age} onChange={e => setAge(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ccc', marginTop: 4 }} />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ fontWeight: 500 }}>Gender</label>
            <select value={gender} onChange={e => setGender(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ccc', marginTop: 4 }}>
              {genderOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
        </div>

        {/* PHQ-9 Section */}
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 20, color: '#333', marginBottom: 12 }}>PHQ-9 Questions</h2>
          {phq9Questions.map((q, idx) => (
            <div key={idx} style={{ marginBottom: 20, padding: 14, background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px #f3f3f3' }}>
              <div style={{ fontWeight: 500, marginBottom: 8 }}>{q}</div>
              <div style={{ display: 'flex', gap: 24 }}>
                {phq9Options.map(opt => (
                  <label key={opt.value} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 15 }}>
                    <input
                      type="radio"
                      name={`phq9-q${idx}`}
                      value={opt.value}
                      checked={String(phq9[idx]) === String(opt.value)}
                      onChange={e => handlePhq9Change(idx, e.target.value)}
                      required
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Other Features */}
        <div style={{ display: 'flex', gap: 24, marginBottom: 32 }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontWeight: 500 }}>Sleep Quality</label>
            <select value={sleepQuality} onChange={e => setSleepQuality(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ccc', marginTop: 4 }}>
              {sleepOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ fontWeight: 500 }}>Study Pressure</label>
            <select value={studyPressure} onChange={e => setStudyPressure(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ccc', marginTop: 4 }}>
              {pressureOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ fontWeight: 500 }}>Financial Pressure</label>
            <select value={financialPressure} onChange={e => setFinancialPressure(e.target.value)} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ccc', marginTop: 4 }}>
              {pressureOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
        </div>

        <button type="submit" disabled={loading} style={{ marginTop: 10, width: '100%', padding: 14, fontSize: 18, background: '#1976d2', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600, letterSpacing: 1 }}>
          {loading ? 'Predicting...' : 'Predict Severity'}
        </button>
      </form>
      {result && (
        <div style={{ marginTop: 36 }}>
          {result.error ? (
            <span style={{ color: 'red' }}>{result.error}</span>
          ) : (
            <>
              <h3 style={{ color: '#1976d2' }}>Prediction Result</h3>
              <div style={{ fontSize: 18, marginBottom: 8 }}><b>Severity:</b> {getSeverityLabel(result.severity_label)}</div>
              <div style={{ fontSize: 15, color: '#555', marginBottom: 8 }}>
                {/* <b>Score:</b> {result.severity} */}
                
              </div>
              {/* <div style={{ marginTop: 12 }}>
                <b>Full Model Response:</b>
                <pre style={{ background: '#f6f6f6', padding: 12, borderRadius: 6, fontSize: 14, marginTop: 6 }}>{JSON.stringify(result, null, 2)}</pre>
              </div> */}
             
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
