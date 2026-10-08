import React, { useState } from 'react';
import { 
  ShieldCheck, UserCheck, FileText, AlertTriangle, XCircle, CheckCircle2, 
  Clock, LogOut, Upload, Download, Search, PlusCircle, LayoutDashboard, 
  Database, Lock, Server, Cpu, ChevronRight
} from 'lucide-react';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('officer_admin');
  const [password, setPassword] = useState('verilens2026');
  const [activeTab, setActiveTab] = useState('dashboard');

  // Traveler creation state
  const [travelerForm, setTravelerForm] = useState({
    fullName: 'John Carter',
    dob: '1998-08-15',
    nationality: 'USA',
    passportNumber: 'DEMO-P-1001',
    expiry: '2031-08-15',
    visaRequired: true,
    visaType: 'TOURIST',
    visaNumber: 'DEMO-VISA-1001',
    visaValidUntil: '2027-01-15',
    securityProfile: 'CLEAR'
  });
  const [travelerCreated, setTravelerCreated] = useState(false);

  // Verification & Screening state
  const [selectedScenario, setSelectedScenario] = useState('scenario-1');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationProgress, setVerificationProgress] = useState([]);
  const [screeningResult, setScreeningResult] = useState(null);

  // Screening history
  const [history, setHistory] = useState([
    { id: 'VL-001', name: 'John Carter', nationality: 'USA', result: 'CLEAR', time: '10:42 AM' },
    { id: 'VL-002', name: 'Maria Chen', nationality: 'CAN', result: 'REVIEW', time: '11:15 AM' },
    { id: 'VL-003', name: 'Alex Smith', nationality: 'GBR', result: 'ALERT', time: '11:30 AM' }
  ]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (username && password) {
      setIsAuthenticated(true);
    }
  };

  const handleCreateTraveler = (e) => {
    e.preventDefault();
    setTravelerCreated(true);
    alert('Synthetic traveler & document pack generated successfully!');
  };

  const runVerification = (scenarioKey) => {
    setIsVerifying(true);
    setVerificationProgress([]);
    setScreeningResult(null);

    const steps = [
      "Document received & uploaded ✓",
      "Running OCR text extraction ✓",
      "Validating Machine Readable Zone (MRZ) ✓",
      "Querying Passport Database ✓",
      "Verifying Nationality & Immigration Status ✓",
      "Checking Visa Validity & Match ✓",
      "Running Synthetic Security Screening ✓",
      "Performing Live Face Biometric Verification ✓",
      "Synthesizing Structured Evidence ✓",
      "Cloud Gemma 4 Reasoning & Risk Scoring ✓"
    ];

    let currentStep = 0;
    const interval = setInterval(() => {
      if (currentStep < steps.length) {
        setVerificationProgress(prev => [...prev, steps[currentStep]]);
        currentStep++;
      } else {
        clearInterval(interval);
        setIsVerifying(false);
        generateResult(scenarioKey);
      }
    }, 300);
  };

  const generateResult = (key) => {
    if (key === 'scenario-1') {
      setScreeningResult({
        level: 'CLEAR',
        score: 0,
        recommendation: 'CLEAR',
        evidence: {
          passport: 'VALID',
          mrz: 'VALID',
          database: 'MATCH',
          nationality: 'IND (Citizen - No Visa Required)',
          visa: 'N/A',
          security: 'CLEAR',
          biometric: 'MATCH (96%)'
        },
        explanation: 'All verification signals are consistent. Genuine Indian citizen with valid credentials and biometric confirmation.'
      });
    } else if (key === 'scenario-2') {
      setScreeningResult({
        level: 'CLEAR',
        score: 5,
        recommendation: 'CLEAR',
        evidence: {
          passport: 'VALID',
          mrz: 'VALID',
          database: 'MATCH',
          nationality: 'USA',
          visa: 'VALID (TOURIST)',
          security: 'CLEAR',
          biometric: 'MATCH (91%)'
        },
        explanation: 'Foreign traveler with valid passport, active Indian visa, and clear security records. Biometrics match successfully.'
      });
    } else if (key === 'scenario-3') {
      setScreeningResult({
        level: 'REVIEW',
        score: 65,
        recommendation: 'SECONDARY_REVIEW',
        evidence: {
          passport: 'VALID',
          mrz: 'INVALID / TAMPERED',
          database: 'DISCREPANCY DETECTED',
          nationality: 'USA',
          visa: 'VALID',
          security: 'CLEAR',
          biometric: 'MATCH (88%)'
        },
        explanation: 'OCR / MRZ inconsistency detected. Uploaded document date of birth (1997) does not match secure database record (1998).'
      });
    } else {
      setScreeningResult({
        level: 'ALERT',
        score: 100,
        recommendation: 'SECONDARY IMMIGRATION REVIEW',
        evidence: {
          passport: 'VALID',
          mrz: 'VALID',
          database: 'MATCH',
          nationality: 'GBR',
          visa: 'VALID',
          security: 'CLEAR',
          biometric: 'MISMATCH (23% Similarity)'
        },
        explanation: 'Critical identity alert! Live face capture does not correspond with the verified passport photograph.'
      });
    }
  };

  if (!isAuthenticated) {
    return (
      <div style={styles.loginContainer}>
        <div style={styles.loginCard}>
          <div style={styles.logoHeader}>
            <ShieldCheck size={48} color="#3b82f6" />
            <h1 style={styles.title}>VeriLens AI</h1>
            <p style={styles.tagline}>"AI-assisted immigration pre-screening and identity verification."</p>
          </div>
          <form onSubmit={handleLogin} style={styles.form}>
            <div style={styles.inputGroup}>
              <label style={styles.label}>Officer Username</label>
              <input 
                type="text" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
                style={styles.input} 
                required 
              />
            </div>
            <div style={styles.inputGroup}>
              <label style={styles.label}>Password / PIN</label>
              <input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                style={styles.input} 
                required 
              />
            </div>
            <button type="submit" style={styles.loginButton}>LOGIN TO OFFICER CONSOLE</button>
          </form>
          <div style={styles.demoNotice}>
            <p>🔒 Demo Mode: Synthetic data only. Not connected to real government databases.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.dashboardContainer}>
      {/* Top Navbar */}
      <header style={styles.navbar}>
        <div style={styles.navBrand}>
          <ShieldCheck size={28} color="#3b82f6" />
          <span style={styles.brandText}>VeriLens AI <small style={styles.badge}>Officer Console</small></span>
        </div>
        <div style={styles.navUser}>
          <span style={styles.officerName}>👤 Officer: {username}</span>
          <button onClick={() => setIsAuthenticated(false)} style={styles.logoutBtn}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </header>

      <div style={styles.mainLayout}>
        {/* Sidebar Navigation */}
        <aside style={styles.sidebar}>
          <button 
            style={{...styles.navItem, ...(activeTab === 'dashboard' ? styles.activeNav : {})}}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={18} /> Dashboard Overview
          </button>
          <button 
            style={{...styles.navItem, ...(activeTab === 'create' ? styles.activeNav : {})}}
            onClick={() => setActiveTab('create')}
          >
            <PlusCircle size={18} /> Create Traveler
          </button>
          <button 
            style={{...styles.navItem, ...(activeTab === 'verify' ? styles.activeNav : {})}}
            onClick={() => setActiveTab('verify')}
          >
            <FileText size={18} /> Verify Document & Screen
          </button>
          <button 
            style={{...styles.navItem, ...(activeTab === 'history' ? styles.activeNav : {})}}
            onClick={() => setActiveTab('history')}
          >
            <Clock size={18} /> Screening History & Audit
          </button>
        </aside>

        {/* Content Area */}
        <main style={styles.content}>
          {activeTab === 'dashboard' && (
            <div>
              <h2>Immigration Control Command Center</h2>
              <p style={styles.subtext}>Welcome to VeriLens AI simulation workspace. Select a module below or start a live screening.</p>
              
              <div style={styles.statsGrid}>
                <div style={styles.statCard}>
                  <h3>Active Scans Today</h3>
                  <p style={styles.statNumber}>142</p>
                </div>
                <div style={styles.statCard}>
                  <h3>Clear Outcomes</h3>
                  <p style={{...styles.statNumber, color: '#10b981'}}>118</p>
                </div>
                <div style={styles.statCard}>
                  <h3>Secondary Reviews</h3>
                  <p style={{...styles.statNumber, color: '#f59e0b'}}>18</p>
                </div>
                <div style={styles.statCard}>
                  <h3>Security / ID Alerts</h3>
                  <p style={{...styles.statNumber, color: '#ef4444'}}>6</p>
                </div>
              </div>

              <div style={styles.bannerBox}>
                <h3>🚀 Quick Demo Scenarios</h3>
                <p>Jump straight into testing predefined immigration scenarios with Cloud Gemma 4 reasoning:</p>
                <div style={styles.scenarioButtonGroup}>
                  <button onClick={() => { setActiveTab('verify'); setSelectedScenario('scenario-1'); }} style={styles.scenarioBtn}>
                    Scenario 1: Genuine Indian Citizen (Clear)
                  </button>
                  <button onClick={() => { setActiveTab('verify'); setSelectedScenario('scenario-2'); }} style={styles.scenarioBtn}>
                    Scenario 2: Genuine Foreign Traveler (Clear)
                  </button>
                  <button onClick={() => { setActiveTab('verify'); setSelectedScenario('scenario-3'); }} style={styles.scenarioBtn}>
                    Scenario 3: Document Tampering / Mismatch (Review)
                  </button>
                  <button onClick={() => { setActiveTab('verify'); setSelectedScenario('scenario-4'); }} style={styles.scenarioBtn}>
                    Scenario 4: Identity Mismatch (Alert)
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'create' && (
            <div>
              <h2>Create Fictional Traveler & Document Pack</h2>
              <p style={styles.subtext}>Enter traveler details to generate synthetic database records and downloadable test documents.</p>
              
              <form onSubmit={handleCreateTraveler} style={styles.createForm}>
                <div style={styles.formRow}>
                  <div style={styles.inputGroup}>
                    <label style={styles.label}>Full Name</label>
                    <input type="text" value={travelerForm.fullName} onChange={e=>setTravelerForm({...travelerForm, fullName: e.target.value})} style={styles.input} />
                  </div>
                  <div style={styles.inputGroup}>
                    <label style={styles.label}>Date of Birth</label>
                    <input type="date" value={travelerForm.dob} onChange={e=>setTravelerForm({...travelerForm, dob: e.target.value})} style={styles.input} />
                  </div>
                </div>
                <div style={styles.formRow}>
                  <div style={styles.inputGroup}>
                    <label style={styles.label}>Nationality</label>
                    <input type="text" value={travelerForm.nationality} onChange={e=>setTravelerForm({...travelerForm, nationality: e.target.value})} style={styles.input} />
                  </div>
                  <div style={styles.inputGroup}>
                    <label style={styles.label}>Passport Number</label>
                    <input type="text" value={travelerForm.passportNumber} onChange={e=>setTravelerForm({...travelerForm, passportNumber: e.target.value})} style={styles.input} />
                  </div>
                </div>
                <button type="submit" style={styles.primaryBtn}>Generate Synthetic Database & Documents</button>
              </form>

              {travelerCreated && (
                <div style={styles.documentCenter}>
                  <h3>📥 Generated Test Document Pack</h3>
                  <p>Synthetic documents created for OCR, MRZ, and tamper testing:</p>
                  <div style={styles.docList}>
                    <div style={styles.docItem}><span>Original Passport.pdf</span> <button style={styles.dlBtn}><Download size={14}/> Download</button></div>
                    <div style={styles.docItem}><span>Tampered Passport.pdf</span> <button style={styles.dlBtn}><Download size={14}/> Download</button></div>
                    <div style={styles.docItem}><span>Original Visa.pdf</span> <button style={styles.dlBtn}><Download size={14}/> Download</button></div>
                    <div style={styles.docItem}><span>Expired Visa.pdf</span> <button style={styles.dlBtn}><Download size={14}/> Download</button></div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'verify' && (
            <div>
              <h2>Document Verification & AI Screening Console</h2>
              <p style={styles.subtext}>Select a test scenario and run the complete AI-assisted immigration screening pipeline.</p>
              
              <div style={styles.scenarioSelector}>
                <label style={styles.label}>Select Test Scenario:</label>
                <select 
                  value={selectedScenario} 
                  onChange={(e) => setSelectedScenario(e.target.value)}
                  style={styles.input}
                >
                  <option value="scenario-1">Scenario 1: Genuine Indian Citizen (CLEAR)</option>
                  <option value="scenario-2">Scenario 2: Genuine Foreign Traveler with Visa (CLEAR)</option>
                  <option value="scenario-3">Scenario 3: Document Mismatch / DOB Tampering (REVIEW)</option>
                  <option value="scenario-4">Scenario 4: Biometric Face Identity Mismatch (ALERT)</option>
                </select>
              </div>

              <button 
                onClick={() => runVerification(selectedScenario)} 
                style={styles.primaryBtn}
                disabled={isVerifying}
              >
                {isVerifying ? 'Running Screening Pipeline...' : 'Run Full Verification & Cloud Gemma 4 Analysis'}
              </button>

              {isVerifying && (
                <div style={styles.progressBox}>
                  <h3>Processing Verification Pipeline...</h3>
                  {verificationProgress.map((step, idx) => (
                    <div key={idx} style={styles.progressStep}>{step}</div>
                  ))}
                </div>
              )}

              {screeningResult && !isVerifying && (
                <div style={styles.resultContainer}>
                  <div style={{
                    ...styles.resultBanner, 
                    backgroundColor: screeningResult.level === 'CLEAR' ? '#d1fae5' : screeningResult.level === 'REVIEW' ? '#fef3c7' : '#fee2e2',
                    color: screeningResult.level === 'CLEAR' ? '#065f46' : screeningResult.level === 'REVIEW' ? '#92400e' : '#991b1b'
                  }}>
                    <h3>FINAL ASSESSMENT: {screeningResult.level}</h3>
                    <p><strong>Recommendation:</strong> {screeningResult.recommendation}</p>
                  </div>

                  <h4>Structured Evidence Matrix:</h4>
                  <ul style={styles.evidenceList}>
                    <li>Passport: <strong>{screeningResult.evidence.passport}</strong></li>
                    <li>MRZ Validation: <strong>{screeningResult.evidence.mrz}</strong></li>
                    <li>Database Record: <strong>{screeningResult.evidence.database}</strong></li>
                    <li>Nationality / Visa: <strong>{screeningResult.evidence.nationality} | {screeningResult.evidence.visa}</strong></li>
                    <li>Security Screening: <strong>{screeningResult.evidence.security}</strong></li>
                    <li>Biometric Verification: <strong>{screeningResult.evidence.biometric}</strong></li>
                  </ul>

                  <div style={styles.aiReasoningBox}>
                    <h4>🤖 Cloud Gemma 4 Reasoning Explanation:</h4>
                    <p>{screeningResult.explanation}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div>
              <h2>Screening History & Audit Logs</h2>
              <p style={styles.subtext}>Complete audit trail of past passenger screenings and officer decisions.</p>
              
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Case ID</th>
                    <th style={styles.th}>Traveler Name</th>
                    <th style={styles.th}>Nationality</th>
                    <th style={styles.th}>Result</th>
                    <th style={styles.th}>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item, idx) => (
                    <tr key={idx}>
                      <td style={styles.td}>{item.id}</td>
                      <td style={styles.td}>{item.name}</td>
                      <td style={styles.td}>{item.nationality}</td>
                      <td style={styles.td}>
                        <span style={{
                          padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold',
                          backgroundColor: item.result === 'CLEAR' ? '#d1fae5' : item.result === 'REVIEW' ? '#fef3c7' : '#fee2e2',
                          color: item.result === 'CLEAR' ? '#065f46' : item.result === 'REVIEW' ? '#92400e' : '#991b1b'
                        }}>
                          {item.result}
                        </span>
                      </td>
                      <td style={styles.td}>{item.time}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

const styles = {
  loginContainer: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#0f172a', fontFamily: 'Segoe UI, sans-serif' },
  loginCard: { background: '#1e293b', padding: '40px', borderRadius: '12px', width: '420px', boxShadow: '0 10px 25px rgba(0,0,0,0.3)', color: '#fff' },
  logoHeader: { textAlign: 'center', marginBottom: '24px' },
  title: { fontSize: '24px', fontWeight: 'bold', margin: '10px 0 5px' },
  tagline: { fontSize: '13px', color: '#94a3b8' },
  form: { display: 'flex', flexDirection: 'column', gap: '16px' },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: '6px' },
  label: { fontSize: '13px', color: '#cbd5e1', fontWeight: '600' },
  input: { padding: '10px 12px', borderRadius: '6px', border: '1px solid #475569', backgroundColor: '#0f172a', color: '#fff', fontSize: '14px' },
  loginButton: { backgroundColor: '#3b82f6', color: '#fff', padding: '12px', borderRadius: '6px', border: 'none', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' },
  demoNotice: { marginTop: '20px', fontSize: '11px', color: '#64748b', textAlign: 'center' },
  
  dashboardContainer: { display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'Segoe UI, sans-serif', backgroundColor: '#f8fafc' },
  navbar: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#0f172a', color: '#fff', padding: '12px 24px', borderBottom: '1px solid #334155' },
  navBrand: { display: 'flex', alignItems: 'center', gap: '10px', fontSize: '20px', fontWeight: 'bold' },
  brandText: { display: 'flex', alignItems: 'center', gap: '10px' },
  badge: { fontSize: '11px', backgroundColor: '#3b82f6', padding: '2px 6px', borderRadius: '4px', fontWeight: 'normal' },
  navUser: { display: 'flex', alignItems: 'center', gap: '15px' },
  officerName: { fontSize: '14px', color: '#cbd5e1' },
  logoutBtn: { display: 'flex', alignItems: 'center', gap: '5px', backgroundColor: '#ef4444', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' },
  
  mainLayout: { display: 'flex', flex: 1, overflow: 'hidden' },
  sidebar: { width: '260px', backgroundColor: '#1e293b', display: 'flex', flexDirection: 'column', gap: '5px', padding: '20px 10px', borderRight: '1px solid #cbd5e1' },
  navItem: { display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 16px', backgroundColor: 'transparent', border: 'none', color: '#cbd5e1', textAlign: 'left', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', fontWeight: '500' },
  activeNav: { backgroundColor: '#3b82f6', color: '#fff' },
  
  content: { flex: 1, padding: '30px', overflowY: 'auto' },
  subtext: { color: '#64748b', marginBottom: '24px' },
  
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '30px' },
  statCard: { background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0' },
  statNumber: { fontSize: '28px', fontWeight: 'bold', margin: '10px 0 0', color: '#0f172a' },
  
  bannerBox: { background: '#eff6ff', border: '1px solid #bfdbfe', padding: '20px', borderRadius: '8px' },
  scenarioButtonGroup: { display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '15px' },
  scenarioBtn: { backgroundColor: '#3b82f6', color: '#fff', border: 'none', padding: '10px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: '600', fontSize: '13px' },
  
  createForm: { background: '#fff', padding: '24px', borderRadius: '8px', border: '1px solid #e2e8f0', maxWidth: '700px' },
  formRow: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '15px' },
  primaryBtn: { backgroundColor: '#2563eb', color: '#fff', border: 'none', padding: '12px 20px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' },
  
  documentCenter: { marginTop: '30px', background: '#fff', padding: '24px', borderRadius: '8px', border: '1px solid #e2e8f0', maxWidth: '700px' },
  docList: { display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px' },
  docItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', backgroundColor: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0' },
  dlBtn: { display: 'flex', alignItems: 'center', gap: '5px', background: '#e2e8f0', border: 'none', padding: '6px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', fontWeight: '600' },
  
  scenarioSelector: { maxWidth: '500px', marginBottom: '20px' },
  progressBox: { marginTop: '20px', background: '#0f172a', color: '#38bdf8', padding: '20px', borderRadius: '8px', fontFamily: 'monospace' },
  progressStep: { margin: '6px 0', fontSize: '14px' },
  
  resultContainer: { marginTop: '25px', background: '#fff', padding: '24px', borderRadius: '8px', border: '1px solid #e2e8f0' },
  resultBanner: { padding: '16px', borderRadius: '6px', marginBottom: '20px' },
  evidenceList: { listStyle: 'none', padding: 0, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' },
  aiReasoningBox: { background: '#f8fafc', border: '1px solid #e2e8f0', padding: '15px', borderRadius: '6px' },
  
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', border: '1px solid #e2e8f0' },
  th: { background: '#f1f5f9', padding: '12px 16px', textAlign: 'left', fontSize: '13px', color: '#475569', borderBottom: '1px solid #e2e8f0' },
  td: { padding: '12px 16px', fontSize: '14px', borderBottom: '1px solid #e2e8f0', color: '#334155' }
};