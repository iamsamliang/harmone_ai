import React from 'react';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';

// Page 1 Component
const WelcomePage = () => (
  <div>
    <div>Welcome</div>
    <Link to="/next" style={{ position: 'fixed', bottom: '20px', right: '20px' }}>→</Link>
  </div>
);

// Page 2 Component
const NextPage = () => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
    <div>Meet Harmone AI and watch YouTube with it</div>
    <Link to="/session"><button style={{ marginTop: '20px' }}>Start Session</button></Link>
  </div>
);

// Session Page Component
const SessionPage = () => (
  <div>
    {/* Your session page content here */}
  </div>
);

// App Component with Routing
const App = () => (
  <Router>
    <Route exact path="/" component={WelcomePage} />
    <Route path="/next" component={NextPage} />
    <Route path="/session" component={SessionPage} />
  </Router>
);

export default App;
