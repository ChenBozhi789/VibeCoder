import React from "react";
import TaskCard, { Task } from "./task-card";

export interface TaskListProps {
  tasks: Task[];
  onView?: (id: string) => void;
  onToggleComplete?: (id: string) => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onView, onToggleComplete }) => {
  if (!tasks || tasks.length === 0) {
    return (
      <div className="empty-state" role="status" aria-live="polite">
        <h2>No tasks yet</h2>
        <p>Click “Add” to create your first task with a title, description, and due date.</p>
      </div>
    );
  }

  return (
    <ul style={{listStyle:"none", padding:0, margin:0}}>
      {tasks.map((t) => (
        <li key={t.id} style={{marginBottom:8}}>
          <TaskCard task={t} onView={onView} onToggleComplete={onToggleComplete} />
        </li>
      ))}
    </ul>
  );
};

export default TaskList;
