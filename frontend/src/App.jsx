import React from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Dashboard from './components/Dashboard';
import RiskSimulator from './components/RiskSimulator';

function App() {
  return (
    <div className="bg-slate-50 pb-20">
      <Dashboard />
      
      {/* Decorative separator */}
      <div className="max-w-7xl mx-auto px-6 md:px-10 py-6">
        <hr className="border-slate-200" />
      </div>

      <RiskSimulator />
      <ToastContainer position="top-right" autoClose={4000} hideProgressBar theme="colored" />
    </div>
  );
}

export default App;
