import React from 'react';
import { Task } from '@/types';
import { Button } from '@/components/ui/button';

interface Props {
  task: Task;
  onToggle?: (id: string) => void;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
}

export const TaskItem: React.FC<Props> = ({ task, onToggle, onEdit, onDelete }) => {
  return (
    <li className="flex items-center justify-between p-3 border-b last:border-b-0">
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          checked={!!task.completed}
          onChange={() => onToggle?.(task.id)}
          aria-label={`Mark ${task.title} as complete`}
          className="w-4 h-4"
        />
        <div>
          <div className={`text-sm ${task.completed ? 'line-through text-gray-400' : 'text-gray-900'}`}>
            {task.title}
          </div>
          {task.notes ? <div className="text-xs text-muted-foreground">{task.notes}</div> : null}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" aria-label={`Edit ${task.title}`} onClick={() => onEdit?.(task.id)}>Edit</Button>
        <Button variant="ghost" aria-label={`Delete ${task.title}`} onClick={() => onDelete?.(task.id)}>Delete</Button>
      </div>
    </li>
  );
};

export default TaskItem;
