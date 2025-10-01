import React from 'react';
import { Task } from '@/types';
import TaskItem from '@/components/task/TaskItem';

interface Props {
  tasks: Task[];
  onToggle?: (id: string) => void;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
}

export const TaskList: React.FC<Props> = ({ tasks, onToggle, onEdit, onDelete }) => {
  return (
    <ul className="w-full max-w-xl bg-card rounded-md overflow-hidden divide-y">
      {tasks.map((t) => (
        <TaskItem key={t.id} task={t} onToggle={onToggle} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </ul>
  );
};

export default TaskList;
