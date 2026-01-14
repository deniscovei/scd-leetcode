import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import AddProblem from './pages/AddProblem';
import ProblemPage from './pages/ProblemPage';

const App: React.FC = () => {
  return (
    <Router>
      <div>
        <Navbar />
        <Switch>
          <Route path="/" exact component={Home} />
          <Route path="/add-problem" component={AddProblem} />
          <Route path="/edit-problem/:id" component={AddProblem} />
          <Route path="/problems/:id" component={ProblemPage} />
        </Switch>
      </div>
    </Router>

  );
};

export default App;