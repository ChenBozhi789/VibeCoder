import React from 'react';
import TaskList from '../components/organisms/TaskList';
import { Task } from '../components/molecules/TaskItem';
import { Button } from '../components/atoms/Button';

const sampleTasks: Task[] = [
  { id: '1', title: 'Buy milk' },
  { id: '2', title: 'Walk the dog' },
  { id: '3', title: 'Write a short note' },
];

const Home: React.FC = () => {
  // Presentational only: handlers are placeholders
  const handleEdit = (task: Task) => {
    console.log('edit', task);
  };
  const handleDelete = (id: string) => {
    console.log('delete', id);
  };

  return (
    <div className="max-w-xl w-full mx-auto p-4">
      <header className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-white">DailyTasks2</h1>
        <Button ariaLabel="Open settings" variant="ghost">Settings</Button>
      </header>

      <section aria-label="Task list" className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="flex-1">
            <p className="text-sm text-gray-300">A minimal list focused on speed. Add tasks quickly.</p>
          </div>
          <Button ariaLabel="Add task">Add</Button>
        </div>

        <TaskList tasks={sampleTasks} onEdit={handleEdit} onDelete={handleDelete} />
      </section>
    </div>
  );
};

export default Home;
