import React from 'react';
import type { Task } from '../types';
import { Button } from '../components/atoms/Button';
import { Card } from '../components/molecules/Card';

// Mock task data for demonstration
const mockTask: Task = {
  id: '1',
  title: 'Buy groceries',
  description: 'Milk, bread, eggs, and vegetables for the week. Also need to check if we have enough coffee.',
  dueDate: '2024-01-15',
  completed: false
};

interface DetailPageProps {
  taskId?: string;
  onBack?: () => void;
}

const DetailPage: React.FC<DetailPageProps> = ({ taskId: _taskId, onBack }) => {
  // In a real app, this would fetch the task by ID using taskId
  const task = mockTask;

  const handleBack = () => {
    onBack?.();
  };

  const handleEdit = () => {
    // This would open edit form in a real app
    console.log('Edit task:', task.id);
  };

  const handleToggleComplete = () => {
    // This would toggle completion in a real app
    console.log('Toggle completion for task:', task.id);
  };

  const formatDueDate = (dueDate?: string) => {
    if (!dueDate) return 'No due date';
    try {
      return new Date(dueDate).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dueDate;
    }
  };

  if (!task) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card title="Task not found">
          <p className="text-muted-foreground">The requested task could not be found.</p>
          <Button onClick={handleBack} className="mt-4">
            Back to List
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={handleBack}>
              ← Back
            </Button>
            <h1 className="text-3xl font-bold">Task Details</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-6">
          <Card>
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h2 className="text-2xl font-semibold">{task.title}</h2>
                  <p className="text-muted-foreground mt-1">
                    Due: {formatDueDate(task.dueDate)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant={task.completed ? 'ghost' : 'primary'}
                    onClick={handleToggleComplete}
                  >
                    {task.completed ? 'Mark Incomplete' : 'Mark Complete'}
                  </Button>
                  <Button variant="outline" onClick={handleEdit}>
                    Edit
                  </Button>
                </div>
              </div>

              {task.description && (
                <div>
                  <h3 className="font-medium mb-2">Description</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">
                    {task.description}
                  </p>
                </div>
              )}

              <div className="pt-4 border-t">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Status:</span>
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                      task.completed 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {task.completed ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium">Created:</span>
                    <span className="ml-2 text-muted-foreground">
                      {new Date().toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default DetailPage;
