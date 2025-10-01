import React from 'react';
import type { TaskCardProps } from '../../types';
import { Button } from '../atoms/Button';
import { cn } from '../../lib/utils';

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onView,
  onToggleComplete,
  className
}) => {
  const formatDueDate = (dueDate?: string) => {
    if (!dueDate) return null;
    try {
      return new Date(dueDate).toLocaleDateString();
    } catch {
      return dueDate; // Return as-is if not a valid date
    }
  };

  return (
    <div className={cn(
      'flex items-center justify-between p-4 border rounded-lg bg-card hover:bg-accent/50 transition-colors',
      task.completed && 'opacity-60',
      className
    )}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={task.completed || false}
            onChange={() => onToggleComplete?.(task.id)}
            className="h-4 w-4 rounded border-gray-300"
            aria-label={`Mark task "${task.title}" as ${task.completed ? 'incomplete' : 'complete'}`}
          />
          <h3 className={cn(
            'font-medium truncate',
            task.completed && 'line-through text-muted-foreground'
          )}>
            {task.title}
          </h3>
        </div>
        {task.description && (
          <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
            {task.description}
          </p>
        )}
        {task.dueDate && (
          <p className="text-xs text-muted-foreground mt-1">
            Due: {formatDueDate(task.dueDate)}
          </p>
        )}
      </div>
      <div className="flex items-center gap-2 ml-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onView?.(task.id)}
          ariaLabel={`View details for task "${task.title}"`}
        >
          View
        </Button>
      </div>
    </div>
  );
};
