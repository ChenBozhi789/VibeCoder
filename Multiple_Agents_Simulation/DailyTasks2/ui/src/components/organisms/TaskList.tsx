import React from 'react';
import { Task, TaskItem } from '../molecules/TaskItem';

export type TaskListProps = {
  tasks?: Task[];
  isLoading?: boolean;
  error?: string | null;
  onEdit?: (task: Task) => void;
  onDelete?: (id: string) => void;
};

export const TaskList: React.FC<TaskListProps> = ({ tasks = [], isLoading = false, error = null, onEdit, onDelete }) => {
  if (isLoading) {
    // simple skeleton
    return (
      <div className="space-y-2">
        <div className="h-10 bg-gray-800 rounded animate-pulse" />
        <div className="h-10 bg-gray-800 rounded animate-pulse" />
        <div className="h-10 bg-gray-800 rounded animate-pulse" />
      </div>
    );
  }

  if (error) {
    return <div role="alert" className="text-red-400">{error}</div>;
  }

  if (tasks.length === 0) {
    return (
      <div className="rounded-md p-6 bg-gray-900 text-center text-gray-300">
        <div className="text-lg font-semibold text-white mb-2">No tasks yet</div>
        <div className="text-sm">Add your first task using the Add button.</div>
      </div>
    );
  }

  return (
    <ul className="space-y-2">
      {tasks.map((t) => (
        <TaskItem key={t.id} task={t} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </ul>
  );
};

export default TaskList;
