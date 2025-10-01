import React from 'react';

export type Task = { id: string; title: string };

export type TaskItemProps = {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (id: string) => void;
};

export const TaskItem: React.FC<TaskItemProps> = ({ task, onEdit, onDelete }) => {
  return (
    <li className="flex items-center justify-between px-3 py-2 hover:bg-gray-800 rounded-md">
      <span className="text-white">{task.title}</span>
      <div className="flex items-center gap-2">
        <button
          aria-label={"Edit " + task.title}
          className="p-1 rounded hover:bg-gray-700"
          onClick={() => onEdit?.(task)}
        >
          {/* simple pencil icon */}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-gray-200">
            <path d="M3 21v-3.75L17.81 2.44a2 2 0 012.83 0l.92.92a2 2 0 010 2.83L6.75 21H3z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <button
          aria-label={"Delete " + task.title}
          className="p-1 rounded hover:bg-gray-700"
          onClick={() => onDelete?.(task.id)}
        >
          {/* simple trash icon */}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-red-400">
            <path d="M3 6h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M8 6v14a2 2 0 002 2h4a2 2 0 002-2V6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M10 11v6M14 11v6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </li>
  );
};

export default TaskItem;
