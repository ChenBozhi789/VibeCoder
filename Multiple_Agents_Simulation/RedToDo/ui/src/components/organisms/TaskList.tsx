import React from 'react';
import { Task } from '../types';
import TaskRow from '../molecules/TaskRow';
interface TaskListProps {
  tasks: Task[];
  onToggle?: (id:string)=>void;
  onEdit?: (task:Task)=>void;
}
export const TaskList: React.FC<TaskListProps> = ({ tasks, onToggle, onEdit }) => {
  if (!tasks || tasks.length === 0) {
    return (
      <div style={{padding:24,textAlign:'center'}}>
        <h3>No tasks yet</h3>
        <p>Add your first task using the + button.</p>
      </div>
    );
  }
  return (
    <div>
      {tasks.map(t => <TaskRow key={t.id} task={t} onToggle={onToggle} onEdit={onEdit} />)}
    </div>
  );
};
export default TaskList;
