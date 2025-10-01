import React from 'react';
import { Task } from '@/types';
import Input from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import TaskList from '@/components/task/TaskList';
import EmptyState from '@/components/empty/EmptyState';

interface Props {
  tasks: Task[];
  onAdd?: (title: string) => void;
}

export const Home: React.FC<Props> = ({ tasks, onAdd }) => {
  const [value, setValue] = React.useState('');
  const showEmpty = tasks.length === 0;

  return (
    <main className="p-4 w-full max-w-3xl mx-auto">
      <header className="mb-4">
        <h1 className="text-2xl font-bold">BlueToDo</h1>
        <p className="text-sm text-muted-foreground">A minimal, fast todo list</p>
      </header>

      <section className="mb-4">
        <div className="flex gap-2">
          <Input
            value={value}
            onChange={setValue}
            placeholder="Add a task title..."
            ariaLabel="Quick add task title"
            className="flex-1"
          />
          <Button onClick={() => { onAdd?.(value); setValue(''); }}>Add</Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">Title is required. (UI validation hint)</p>
      </section>

      <section>
        {showEmpty ? (
          <EmptyState onPrimary={() => onAdd?.('My first task')} />
        ) : (
          <TaskList tasks={tasks} />
        )}
      </section>
    </main>
  );
};

export default Home;
