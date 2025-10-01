import React from 'react';
import Home from '@/pages/Home';
import { Task } from '@/types';
import '@/App.css';

const mockTasks: Task[] = [
  { id: '1', title: 'Buy milk', completed: false, created_at: new Date().toISOString() },
  { id: '2', title: 'Pick up laundry', completed: true, created_at: new Date().toISOString() },
];

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Home tasks={mockTasks} onAdd={(title) => { /* UI-only placeholder */ }} />
    </div>
  );
}

export default App;
