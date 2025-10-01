import React from 'react';
import { TaskItem } from '../molecules/TaskItem';
import { Card } from '../molecules/Card';
import { Button } from '../atoms/Button';
import { Loader2, AlertCircle } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { Task } from '../../types';

interface TaskListProps {
  tasks: Task[];
  onToggle: (id: string) => void;
  onEdit: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  loading?: boolean;
  error?: string | null;
  editingTaskId?: string | null;
  onStartEdit?: (id: string) => void;
}

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onToggle,
  onEdit,
  onDelete,
  loading = false,
  error = null,
  editingTaskId = null,
  onStartEdit
}) => {
  if (loading) {
    return (
      <Card className="text-center py-8">
        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
        <p className="text-muted-foreground">Loading tasks...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="text-center py-8">
        <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        <Button 
          variant="outline"
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </Card>
    );
  }

  if (tasks.length === 0) {
    return (
      <Card className="text-center py-8">
        <h3 className="text-lg font-semibold mb-2">No tasks yet</h3>
        <p className="text-muted-foreground mb-4">
          Add your first task above to get started!
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-2">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onEdit={onEdit}
          onDelete={onDelete}
          isEditing={editingTaskId === task.id}
          onStartEdit={onStartEdit}
        />
      ))}
    </div>
  );
};
