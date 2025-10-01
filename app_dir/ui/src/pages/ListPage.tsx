import React, { useState } from 'react';
import type { Task } from '../types';
import { TaskList } from '../components/organisms/TaskList';
import { Input } from '../components/atoms/Input';
import { Button } from '../components/atoms/Button';
import { Card } from '../components/molecules/Card';

// Mock data for demonstration
const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Buy groceries',
    description: 'Milk, bread, eggs, and vegetables',
    dueDate: '2024-01-15',
    completed: false
  },
  {
    id: '2',
    title: 'Call dentist',
    description: 'Schedule annual checkup',
    dueDate: '2024-01-20',
    completed: true
  },
  {
    id: '3',
    title: 'Finish project report',
    description: 'Complete the quarterly project report for the team',
    dueDate: '2024-01-18',
    completed: false
  }
];

interface ListPageProps {
  onViewTask?: (taskId: string) => void;
}

const ListPage: React.FC<ListPageProps> = ({ onViewTask }) => {
  const [tasks, setTasks] = useState<Task[]>(mockTasks);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCompleted, setShowCompleted] = useState(true);

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = showCompleted || !task.completed;
    return matchesSearch && matchesFilter;
  });

  const handleToggleComplete = (taskId: string) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === taskId
          ? { ...task, completed: !task.completed }
          : task
      )
    );
  };

  const handleViewTask = (taskId: string) => {
    onViewTask?.(taskId);
  };

  const handleAddTask = () => {
    // This would open add task modal/form in a real app
    console.log('Add new task');
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">DailyTasks</h1>
          <p className="text-muted-foreground mt-2">
            Simple list view to add and scan daily chores and reminders.
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        <div className="space-y-6">
          {/* Search and Filter Controls */}
          <Card>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  id="search"
                  placeholder="Search tasks..."
                  value={searchTerm}
                  onChange={setSearchTerm}
                />
              </div>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={showCompleted}
                    onChange={(e) => setShowCompleted(e.target.checked)}
                    className="h-4 w-4"
                  />
                  Show completed
                </label>
                <Button onClick={handleAddTask}>
                  Add Task
                </Button>
              </div>
            </div>
          </Card>

          {/* Task List */}
          <TaskList
            tasks={filteredTasks}
            onView={handleViewTask}
            onToggleComplete={handleToggleComplete}
          />
        </div>
      </main>
    </div>
  );
};

export default ListPage;
