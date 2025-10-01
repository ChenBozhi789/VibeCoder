import React from 'react';
import TaskList from '../components/organisms/TaskList';
import { Task } from '../components/types';

const mock: Task[] = [
  { id: '1', title: 'Buy groceries', done: false, dueDate: '2025-01-01' },
  { id: '2', title: 'Morning run', done: true }
];

export const Home: React.FC = () => {
  return (
    <main style={{padding:16}}>
      <header style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:12}}>
        <h2>RedToDo</h2>
        <button aria-label="Settings" style={{border:'none',background:'transparent'}}>⚙️</button>
      </header>
      <TaskList tasks={mock} />
      <div style={{position:'fixed',right:16,bottom:16}}>
        <button aria-label="Add task" style={{padding:12,borderRadius:999,background:'#d33',color:'#fff',border:'none'}}>+</button>
      </div>
    </main>
  );
};
export default Home;
